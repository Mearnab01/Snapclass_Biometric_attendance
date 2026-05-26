# SnapClass

**AI-Powered Attendance Management System**

> Automates classroom attendance using face recognition and voice verification — no roll calls, no sign-in sheets, no proxies.

---

## Table of Contents

1. [Overview](#overview)
2. [Demo](#demo)
3. [Features](#features)
4. [Tech Stack](#tech-stack)
5. [System Architecture](#system-architecture)
6. [ML Pipelines](#ml-pipelines)
7. [Database Schema](#database-schema)
8. [Screens](#screens)
9. [Folder Structure](#folder-structure)
10. [Setup Instructions](#setup-instructions)
11. [Environment Variables](#environment-variables)
12. [Security](#security)
13. [Known Issues and Fixes](#known-issues-and-fixes)
14. [Future Scope](#future-scope)
15. [Author](#author)

---

## Overview

Traditional classroom attendance is slow, prone to human error, and trivially gameable — a student can mark a proxy for an absent classmate in seconds. SnapClass eliminates this entirely.

Teachers upload a group photograph of their class. The system detects every face in the image, matches each against the enrolled student embeddings using a trained classifier, and logs attendance against the correct subject and session — all in one click. As an alternative modality, teachers can also run voice-based attendance where students speak a short phrase and the system identifies them by voice.

Students log into the platform using FaceID — a live camera scan replaces username and password entirely. New students register by taking a photo and optionally recording a voice sample, after which the classifier retrains automatically to include them.

---

## Demo

```
streamlit run app.py
```

Open `http://localhost:8501` in your browser.

On first run, `facenet-pytorch` downloads InceptionResnetV1 weights (~90MB) to `~/.cache/torch`. Subsequent runs are instant.

---

## Features

**For Teachers**

- Upload one or more classroom photos — system detects and marks all present students across all photos in a single session
- Voice attendance mode — students speak a phrase, system identifies them by voice embedding
- Subject management — create subjects with codes, share enrollment links with students
- Attendance records — full session-by-session log with present/total counts
- Subject analytics — per-student and per-session attendance breakdown in a modal dialog

**For Students**

- FaceID login — live camera scan, no password required
- Self-registration — take a photo, enter a name, optionally record a voice sample
- Voice enrollment — enables voice-based attendance as a second modality
- Enrolled subjects dashboard — view all subjects with total classes and attended count
- Enroll/unenroll — join subjects via code, leave at any time

**Technical**

- Dual-modal biometric identification — face (512-d) and voice (256-d) embeddings stored independently
- On-demand classifier retraining — SVC retrains automatically after each new student registers
- Session-level attendance deduplication — student detected in 3 photos is marked present once
- Centralized logging — all INFO, WARNING, ERROR events written to `logs/snapclass.log`
- Streamlit session state management — audio bytes persisted across reruns to survive widget resets
- Separation of concerns — UI, service, pipeline, and database layers are independently structured

---

## Tech Stack

| Layer            | Technology                      | Version  |
| ---------------- | ------------------------------- | -------- |
| Frontend         | Streamlit                       | 1.37.0+  |
| Face Detection   | facenet-pytorch MTCNN           | Latest   |
| Face Embedding   | InceptionResnetV1 (VGGFace2)    | Latest   |
| Voice Embedding  | Resemblyzer VoiceEncoder (GE2E) | Latest   |
| ML Classifier    | scikit-learn SVC (linear)       | Latest   |
| Audio Processing | librosa                         | Latest   |
| Database         | Supabase (PostgreSQL)           | Latest   |
| Auth             | bcrypt                          | Latest   |
| Config           | python-dotenv                   | Latest   |
| Logging          | Python logging (stdlib)         | Built-in |

---

## System Architecture

```
BROWSER / TEACHER
        |
        | uploads photo or audio
        v
STREAMLIT APP (app.py)
        |
        |── teacher_screen.py ──── Take Attendance
        |                              |
        |                         face_pipeline.py
        |                              |
        |                    MTCNN (detect faces)
        |                              |
        |                    InceptionResnetV1 (512-d embedding)
        |                              |
        |                    SVC.predict (match to student_id)
        |                              |
        |                    Euclidean distance check (<= 0.9)
        |                              |
        |                    attendance_logs INSERT
        |
        |── student_screen.py ─── FaceID Login
        |                              |
        |                         face_pipeline.py
        |                              |
        |                         predict_attendance()
        |                              |
        |                         session_state.student_data SET
        |
        |── voice pipeline ────── Voice Attendance
                                       |
                                   librosa (load + resample)
                                       |
                                   preprocess_wav (normalise)
                                       |
                                   VoiceEncoder.embed_utterance (256-d)
                                       |
                                   np.dot (cosine similarity)
                                       |
                                   threshold check (>= 0.65)
```

---

## ML Pipelines

### Face Pipeline

**Models:**

| Model               | Role                       | Architecture                                               | Output                  |
| ------------------- | -------------------------- | ---------------------------------------------------------- | ----------------------- |
| MTCNN               | Face detection + alignment | Multi-task CNN — 3 cascaded networks (P-Net, R-Net, O-Net) | Cropped 160x160 tensors |
| InceptionResnetV1   | Face embedding             | Inception-ResNet pretrained on VGGFace2 (3.3M images)      | 512-d float vector      |
| SVC (linear kernel) | Classification             | Linear hyperplane in 512-d embedding space                 | Predicted student_id    |

**Flow:**

```
get_face_embeddings(image_np)
  → MTCNN detects + aligns all faces in image
  → InceptionResnetV1 converts each to 512-d vector
  → returns list of numpy arrays

get_trained_model()
  → loads all students from Supabase
  → builds X (embeddings), y (student IDs)
  → handles clf=None when < 2 students enrolled
  → trains SVC, caches with @st.cache_resource

predict_attendance(image_np)
  → calls get_face_embeddings
  → SVC.predict → candidate student_id
  → Euclidean distance to stored embedding (second gate)
  → marks present only if distance <= 0.9
  → returns (detected_dict, all_students, num_faces)

train_classifier()
  → clears Streamlit cache
  → triggers get_trained_model() with latest DB data
  → called automatically after every new student registers
```

**Why SVC over a neural classifier:**

Most classrooms have 30–60 students with one enrollment photo each. SVC with a linear kernel works extremely well here because InceptionResnetV1 already produces high-quality 512-d embeddings — the classification problem is essentially linearly separable. A neural Sequential classifier would overfit immediately on N=1 sample per class.

---

### Voice Pipeline

**Model:** Resemblyzer VoiceEncoder (GE2E — Generalized End-to-End Loss)

| Property          | Detail                                                        |
| ----------------- | ------------------------------------------------------------- |
| Architecture      | LSTM — 3 layers, 768 hidden units, linear projection to 256-d |
| Training data     | LibriSpeech + VoxCeleb — thousands of speakers                |
| Output            | 256-d L2-normalised float vector                              |
| Similarity metric | Cosine similarity (dot product on unit vectors)               |
| Threshold         | 0.65                                                          |

**Flow:**

```
get_voice_embedding(audio_bytes)
  → librosa.load at 16kHz
  → preprocess_wav (normalise + trim silence)
  → embed_utterance → 256-d vector
  → returns as list for JSONB storage

identify_speaker(embedding, candidates_dict)
  → np.dot against every stored voice embedding
  → returns (best_sid, best_score) if score >= threshold

process_bulk_audio(audio_bytes, candidates_dict)
  → librosa.effects.split (top_db=30) → speech segments
  → skips segments < 0.5 seconds
  → embeds each segment independently
  → keeps best score per student across all segments
```

---

## Database Schema

```
teachers
  teacher_id  PK
  username    text UNIQUE
  password    text (bcrypt hashed)
  name        text

students
  student_id      PK
  name            text
  face_embeddings jsonb   ← 512-d float list
  voice_embeddings jsonb  ← 256-d float list, nullable

subjects
  subject_id    PK
  subject_code  text
  name          text
  section       text
  password      text
  teacher_id    FK → teachers.teacher_id

subject_students  (junction table — M:N enrollment)
  subject_id  FK + CPK → subjects.subject_id
  student_id  FK + CPK → students.student_id

attendance_logs
  id          PK
  timestamp   timestamptz
  subject_id  FK → subjects.subject_id
  student_id  FK → students.student_id
  is_present  boolean
```

**Relationships:**

- One teacher owns many subjects (1:N)
- Many students enroll in many subjects (M:N via `subject_students`)
- One student has many attendance logs (1:N)
- One subject has many attendance logs (1:N)
- Attendance logs from the same session share the same timestamp — grouping by timestamp gives session-level aggregation

---

## Screens

### Home Screen

- Landing page shown when no user is logged in
- Two role buttons: Teacher and Student
- Sets `login_type` in session state to route the app

### Teacher Login / Register

- Username + bcrypt password authentication
- Register flow inline — toggled via `teacher_login_type` session state
- Centered 1-3-1 column form layout
- Keyboard shortcut `Ctrl+Enter` triggers login

### Teacher Dashboard

**Take Attendance tab**

- Subject selector dropdown
- Add Photos dialog — supports multiple uploads
- 4-column photo gallery preview
- Run Face Analysis — iterates every photo through `predict_attendance()`, merges results across photos
- Voice Attendance — opens dialog for audio-based identification
- Results dialog shows per-student present/absent before committing to DB

**Manage Subjects tab**

- Lists all subjects with student count and class count
- Create New Subject dialog
- Share Code button — generates shareable enrollment link
- Analytics button — opens per-student and per-session attendance breakdown modal

**Attendance Records tab**

- Full session log grouped by timestamp
- Columns: Time, Subject, Subject Code, Present/Total

### Student Login (FaceID)

- `st.camera_input` captures live webcam frame
- `predict_attendance()` attempts recognition
- Recognised → session populated, dashboard loads
- Unrecognised → registration panel appears below camera

**Registration Panel**

- Name input + optional voice recording
- Audio bytes saved to session state before form submission (survives Streamlit rerun)
- Face embedding extracted with `.flatten().tolist()` to guarantee 1-D storage
- `train_classifier()` called after DB insert

### Student Dashboard

- Subject cards with name, code, section, total classes, attended count
- Enroll in Subject via code
- Unenroll button per subject

---

## Folder Structure

```
snapclass/
│
├── app.py                               ← entry point, session init, routing
├── requirements.txt                     ← all dependencies
├── requirements.lock                    ← pinned lockfile for reproducible installs
├── SETUP.md                             ← setup guide with install order notes
├── .env.example                         ← template for required environment variables
├── .gitignore
│
├── .streamlit/
│   └── secrets.toml                     ← deployment credentials (never committed)
│
├── logs/
│   └── snapclass.log                    ← runtime log (never committed)
│
├── src/
│   ├── pipelines/
│   │   ├── face_pipeline.py             ← MTCNN + InceptionResnetV1 + SVC
│   │   └── voice_pipeline.py            ← VoiceEncoder + identify_speaker
│   │
│   ├── screens/
│   │   ├── home_screen.py
│   │   ├── teacher_screen.py
│   │   └── student_screen.py
│   │
│   ├── components/
│   │   ├── header.py
│   │   ├── footer.py
│   │   ├── subject_card.py
│   │   ├── dialog_create_subject.py
│   │   ├── dialog_share_subject.py
│   │   ├── dialog_add_photo.py
│   │   ├── dialog_attendance_results.py
│   │   ├── dialog_voice_attendance.py
│   │   ├── dialog_enroll.py
│   │   ├── dialog_auto_enroll.py
│   │   └── dialog_subject_analytics.py
│   │
│   ├── database/
│   │   ├── config.py                    ← Supabase client init
│   │   └── db.py                        ← all query functions
│   │
│   └── ui/
│       └── base_layout.py               ← global CSS, fonts, backgrounds
│
├── utils/
│   └── logger.py                        ← setup_logger("name") factory
│
└── notebooks/
    └── voice_test.ipynb                 ← resemblyzer pipeline test notebook
```

---

## Setup Instructions

> **Windows note:** Do not run `pip install -r requirements.txt` directly without following the steps below. `resemblyzer` has a hard dependency on `webrtcvad` which requires Microsoft C++ Build Tools to compile from source. The steps below route around this.

**1. Clone the repository**

```bash
git clone https://github.com/your-username/snapclass.git
cd snapclass
```

**2. Create and activate a conda environment**

```bash
conda create -n snapclass python=3.10
conda activate snapclass
```

**3. Install prebuilt webrtcvad wheel first**

This must happen before anything else — installing it later does not prevent pip from pulling the source build.

```bash
pip install webrtcvad-wheels --no-cache-dir
```

**4. Install resemblyzer without its dependencies**

`resemblyzer` declares `webrtcvad` as a dependency. `--no-deps` prevents pip from overwriting the wheel you just installed.

```bash
pip install resemblyzer --no-deps
pip install typing
```

**5. Install the rest**

```bash
pip install -r requirements.txt
```

**6. Verify**

```bash
python -c "import resemblyzer; import webrtcvad; import supabase; from facenet_pytorch import MTCNN; print('all good')"
```

**7. Configure environment variables**

```bash
cp .env.example .env
```

Fill in your Supabase URL and anon key.

**8. Configure Streamlit secrets**

```bash
mkdir .streamlit
```

Create `.streamlit/secrets.toml`:

```toml
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_KEY = "your-anon-key"
```

**9. Run**

```bash
streamlit run app.py
```

---

## Environment Variables

```env
# .env.example

# Supabase project URL — found in project settings under API
SUPABASE_URL=https://your-project-ref.supabase.co

# Supabase anon/public key — used for client-side DB access
SUPABASE_KEY=your-supabase-anon-key
```

In local development these are loaded via `python-dotenv`. In Streamlit Cloud deployment the equivalent values are set in `.streamlit/secrets.toml` and accessed via `st.secrets`.

---

## Security

- Passwords hashed with bcrypt before storage — `gensalt()` per password, rainbow table attacks infeasible
- `check_pass()` uses `bcrypt.checkpw()` — plaintext is never compared directly
- `.env` and `.streamlit/secrets.toml` are in `.gitignore` — never committed
- Supabase anon key scoped to minimum required permissions — no service role key exposed
- Face and voice embeddings stored as JSONB numerical vectors — cannot be reconstructed into images or audio
- `logs/` directory is gitignored — runtime errors never exposed in version control
- Supabase Row Level Security policies can be enabled to restrict cross-user data access

---

## Known Issues and Fixes

| Issue                                | Root Cause                                                                            | Fix Applied                                                                 |
| ------------------------------------ | ------------------------------------------------------------------------------------- | --------------------------------------------------------------------------- |
| `webrtcvad` build failure on Windows | No prebuilt wheel — requires MSVC compiler                                            | `pip install webrtcvad-wheels` + `pip install resemblyzer --no-deps`        |
| `speechbrain` k2_fsa CUDA error      | Lazy import of k2_fsa requires CUDA even on CPU mode                                  | Reverted voice pipeline to resemblyzer                                      |
| Voice embedding always NULL          | `st.audio_input` resets on Streamlit rerun — `audio_data` is None when button clicked | Bytes saved to session state immediately when widget returns non-None       |
| SVC fit error: 1 class               | SVC requires minimum 2 classes                                                        | `clf=None` guard added — falls back to direct assignment for single student |
| Inhomogeneous embedding shape        | face_embedding stored as nested array                                                 | `.flatten().tolist()` applied before storage                                |
| Face not detected in low light       | MTCNN handles this natively                                                           | No fix needed — switching from dlib HOG to MTCNN resolved it                |

---

## Future Scope

**ML Improvements**

- Multi-photo enrollment — 5 to 10 photos per student per class for higher real-world accuracy
- Liveness detection — anti-spoofing to prevent photo-based bypass attacks
- Fine-tune InceptionResnetV1 backbone — outperforms SVC head when multi-photo data is available

**Feature Additions**

- Attendance analytics export — CSV and PDF reports per subject per month
- Automated low-attendance alerts — email/WhatsApp via Supabase Edge Functions
- Timetable integration — system knows active subject without manual selection
- Bulk student import — CSV roster upload instead of individual camera registration
- Manual override — teacher corrects AI mistakes with separate audit trail

**Infrastructure**

- FastAPI backend — decouple ML pipelines into REST API for LMS integration
- Background job queue — async attendance processing so teacher UI is non-blocking
- JWT session persistence — survive browser refresh via Supabase Auth tokens
- Progressive Web App — installable mobile experience with direct camera access

---

## Author

Built by **Arnab Nath**
MCA Final Year — Techno India University

---

_SnapClass is an independent academic project._
