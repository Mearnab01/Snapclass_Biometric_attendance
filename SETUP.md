# SnapClass PyTorch — Setup Guide

## What changed from the original

| Original | Replacement | Benefit |
|---|---|---|
| `dlib` + `face_recognition_models` | `facenet-pytorch` | No C++ build tools needed |
| `resemblyzer` + `webrtcvad-wheels` | `speechbrain` | Pure pip install, no system deps |

All other files — database, screens, components, dialogs — are unchanged in logic.

---

## Install

```bash
conda create -n snapclass python=3.10
conda activate snapclass

pip install -r requirements.txt
```

No manual pre-installs needed. No `--no-deps` workarounds. No constraints files.

---

## First run — model downloads

On the first run, two models will be downloaded automatically:

- `facenet-pytorch` downloads InceptionResnetV1 weights (~90MB) to `~/.cache/torch`
- `speechbrain` downloads ECAPA-TDNN weights (~80MB) to `pretrained_models/`

Both are cached after the first download — subsequent runs are instant.

---

## Threshold note

The face distance threshold is set to `0.9` (was `0.6` with dlib).
This is because facenet produces 512-d embeddings vs dlib's 128-d — distances are naturally larger.
If you see false positives, lower it to `0.8`. If faces are not being recognised, raise it to `1.0`.

Voice similarity threshold is `0.75` (was `0.65` with resemblyzer).
ECAPA-TDNN embeddings are more discriminative — if legitimate students are rejected, lower to `0.70`.

---

## Run

```bash
streamlit run app.py
```
