import numpy as np
import streamlit as st
from PIL import Image
from sklearn.svm import SVC
from facenet_pytorch import MTCNN, InceptionResnetV1

from src.database.db import get_all_students


# ── Model loader ──────────────────────────────────────────────────────────────

@st.cache_resource
def _load_models():
    mtcnn = MTCNN(keep_all=True, device='cpu', post_process=True)
    resnet = InceptionResnetV1(pretrained='vggface2').eval()

    return mtcnn, resnet


# ── Face embeddings ───────────────────────────────────────────────────────────

def get_face_embeddings(image_np: np.ndarray) -> list[np.ndarray]:
    mtcnn, resnet = _load_models()

    pil_img = Image.fromarray(image_np)

    # Returns list of aligned (3, 160, 160) face tensors or None if no face found
    faces = mtcnn(pil_img)

    if faces is None:
        return []

    embeddings = []
    for face in faces:
        embedding = resnet(face.unsqueeze(0))             # (1, 512)
        embeddings.append(embedding.detach().numpy()[0])  # (512,)

    return embeddings


# ── Classifier ────────────────────────────────────────────────────────────────

@st.cache_resource
def get_trained_model() -> dict | None:
    students = get_all_students()

    if not students:
        return None

    X, y = [], []
    for student in students:
        embedding = student.get('face_embeddings')
        if embedding:
            X.append(np.array(embedding))
            y.append(student.get('student_id'))

    if not X:
        return None
    
    clf = None
    if (len(set(y)) >= 2):
        clf = SVC(kernel='linear', probability=True, class_weight='balanced')

        try:
            clf.fit(X, y)
        except ValueError as e:
            print(f"[get_trained_model] fit error: {e}")
            return None

    return {'clf': clf, 'X': X, 'y': y}


def train_classifier() -> bool:
    st.cache_resource.clear()
    return bool(get_trained_model())


# ── Attendance prediction ─────────────────────────────────────────────────────

def predict_attendance(class_image_np: np.ndarray) -> tuple[dict, list, int]:
    encodings         = get_face_embeddings(class_image_np)
    detected_students = {}

    model_data = get_trained_model()

    if not model_data:
        return detected_students, [], len(encodings)

    clf     = model_data['clf']
    X_train = model_data['X']
    y_train = model_data['y']

    all_students = sorted(set(y_train))

    for encoding in encodings:
        predicted_id = (
            int(clf.predict([encoding])[0])
            if len(all_students) >= 2
            else int(all_students[0])
        )

        student_embedding = X_train[y_train.index(predicted_id)]
        distance          = np.linalg.norm(student_embedding - encoding)

        if distance <= 0.9:
            detected_students[predicted_id] = True

    return detected_students, all_students, len(encodings)
