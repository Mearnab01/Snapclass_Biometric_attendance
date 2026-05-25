from pathlib import Path

# Files to create
files = [
    # root
    "app.py",
    "requirements.txt",
    "requirements.lock",
    "README.md",
    "SETUP.md",
    "setup.py",
    "pyproject.toml",
    ".gitignore",

    # streamlit
    ".streamlit/secrets.toml",

    # notebooks
    "notebooks/research.ipynb",

    # pipelines
    "src/pipelines/face_pipeline.py",
    "src/pipelines/voice_pipeline.py",

    # screens
    "src/screens/home_screen.py",
    "src/screens/teacher_screen.py",
    "src/screens/student_screen.py",

    # components
    "src/components/header.py",
    "src/components/footer.py",
    "src/components/subject_card.py",
    "src/components/dialog_add_photo.py",
    "src/components/dialog_attendance_results.py",
    "src/components/dialog_auto_enroll.py",
    "src/components/dialog_create_subject.py",
    "src/components/dialog_enroll.py",
    "src/components/dialog_share_subject.py",
    "src/components/dialog_voice_attendance.py",

    # database
    "src/database/config.py",
    "src/database/db.py",

    # ui
    "src/ui/base_layout.py",

    # init files
    "src/__init__.py",
    "src/pipelines/__init__.py",
    "src/screens/__init__.py",
    "src/components/__init__.py",
    "src/database/__init__.py",
    "src/ui/__init__.py",
]

# Create all files + folders
for file in files:
    path = Path(file)

    # Create parent directories
    path.parent.mkdir(parents=True, exist_ok=True)

    # Create file if not exists
    if not path.exists():
        path.touch()
        print(f"✅ Created: {path}")

print("\n🚀 Full project structure created successfully!")