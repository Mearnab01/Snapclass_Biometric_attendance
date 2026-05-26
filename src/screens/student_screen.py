import streamlit as st
from PIL import Image 
import numpy as np

from src.ui.base_layout import style_background_dashboard, style_base_layout
from src.components.header import header_dashboard
from src.components.footer import footer_dashboard
from src.components.student_compliance import render_student_compliance
from src.components.subject_card import subject_card
from src.components.dialog_enroll import enroll_dialog

from src.pipelines.face_pipeline import predict_attendance, get_face_embeddings, train_classifier
from src.pipelines.voice_pipeline import get_voice_embedding
from src.database.db import (
    get_all_students, create_student,
    get_student_subjects, get_student_attendance,
    unenroll_student_to_subject
)
from utils.logger import setup_logger

logger = setup_logger("student_screen")


def student_screen():
    style_background_dashboard()
    style_base_layout()

    if "student_data" in st.session_state:
        student_dashboard()
    else:
        student_login_screen()
        
    logger.info(f"Student screen rendered")


# ── Dashboard ─────────────────────────────────────────────────────────────────

def student_dashboard():
    student_data = st.session_state.student_data
    student_id   = student_data['student_id']
    
    logger.info(f"Rendering dashboard for student: {student_data['name']} (ID: {student_id})")

    c1, c2 = st.columns([3, 1], vertical_alignment='center', gap='large')
    with c1:
        header_dashboard()
    with c2:
        if st.button("Logout", icon=":material/exit_to_app:", type='secondary', key='student_logout_btn'):
            del st.session_state.student_data
            st.session_state['is_logged_in'] = False
            st.rerun()

    st.divider()
    render_student_compliance(student_data['student_id'])

    c1, c2 = st.columns([2, 1], vertical_alignment='center')
    with c1:
        st.header(f"Welcome, {student_data['name']}!")
        # if enrolled then show
    with c2:
        if st.button('Enroll in Subject', type='primary', width='stretch'):
            enroll_dialog()

    st.divider()

    with st.spinner('Loading your subjects...'):
        subjects = get_student_subjects(student_id)
        logs     = get_student_attendance(student_id)

    stats_map = _build_stats_map(logs)

    if not subjects:
        st.info("You are not enrolled in any subjects yet.")
    else:
        cols = st.columns(2, gap='medium')
        for i, sub_node in enumerate(subjects):
            sub   = sub_node['subjects']
            sid   = sub['subject_id']
            stats = stats_map.get(sid, {"total": 0, "attended": 0})

            def unenroll_btn(bound_sid=sid, bound_name=sub['name']):
                if st.button("Unenroll", type='secondary', width='stretch',
                             icon=':material/delete_forever:',
                             key=f"unenroll_{bound_sid}"):
                    unenroll_student_to_subject(student_id, bound_sid)
                    st.toast(f"Unenrolled from {bound_name}.")
                    st.rerun()

            with cols[i % 2]:
                subject_card(
                    name=sub['name'],
                    code=sub['subject_code'],
                    section=sub['section'],
                    stats=[
                        ('', 'Total Classes', stats['total']),
                        ('', 'Attended',      stats['attended']),
                    ],
                    footer_callback=unenroll_btn
                )

    footer_dashboard()


# ── Login screen ──────────────────────────────────────────────────────────────

def student_login_screen():
    c1, c2 = st.columns([1, 1], vertical_alignment='center', gap='large')
    with c1:
        header_dashboard()
    with c2:
        if st.button("Go back to Home", type='secondary', key='student_back_btn'):
            st.session_state['login_type'] = None
            st.rerun()

    st.markdown("""
        <div style="text-align:center; padding:1.5rem 0 1rem 0;">
            <h3 style="color:#1a1f3c; margin:0;">Student Face Login</h3>
            <p style="color:#8892b0; margin:0.35rem 0 0 0; font-size:0.875rem;">
                Position your face clearly in the camera to sign in.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    if 'open_camera' not in st.session_state:
        st.session_state['open_camera'] = False
        
    btn1, btn2 = st.columns([1, 1], gap='medium')
    # Open camera
    with btn1:
        if st.button('Open Camera', icon=":material/ar_on_you:", type="primary", width='stretch'):
            st.session_state["open_camera"] = True


    # Close camera
    with btn2:
        if st.button('Close Camera', icon=":material/cancel:", type="secondary", width='stretch'):
            st.session_state["open_camera"] = False
            st.rerun()
            
    if st.session_state["open_camera"]:
        photo_source = st.camera_input("Position your face in the center")
        show_registration = False

        if photo_source:
            show_registration = _handle_face_login(photo_source)

        if show_registration:
            _registration_panel(photo_source)

        footer_dashboard()


def _handle_face_login(photo_source) -> bool:
    img = np.array(Image.open(photo_source))

    with st.spinner('Scanning with AI...'):
        detected, _, num_faces = predict_attendance(img)

    if num_faces == 0:
        st.warning('No face detected. Please adjust your position and try again.')
        return False

    if num_faces > 1:
        st.warning('Multiple faces detected. Please ensure only one face is visible.')
        return False

    if not detected:
        st.info('Face not recognised. You may be a new student — register below.')
        return True

    student_id   = list(detected.keys())[0]
    all_students = get_all_students()
    student      = next((s for s in all_students if s['student_id'] == student_id), None)

    if not student:
        st.info('Face not recognised. You may be a new student — register below.')
        return True

    _set_student_session(student)
    logger.info(f"Student {student['name']} (ID: {student_id}) logged in successfully.")
    st.toast(f"Welcome back, {student['name']}!")
    st.rerun()
    return False


def _registration_panel(photo_source):
    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("""
            <div style="margin-bottom:0.75rem;">
                <h3 style="color:#1a1f3c; margin:0;">Create a New Profile</h3>
                <p style="color:#8892b0; margin:0.25rem 0 0 0; font-size:0.875rem;">
                    Your face will be enrolled from the photo above.
                </p>
            </div>
        """, unsafe_allow_html=True)

        new_name = st.text_input("Your Full Name", placeholder='e.g. Arnab Nath')

        st.markdown("""
            <p style="font-weight:600; color:#1a1f3c; font-size:0.875rem;
                       margin:0.75rem 0 0.25rem 0;">Voice Enrollment (Optional)</p>
            <p style="color:#8892b0; font-size:0.82rem; margin:0 0 0.5rem 0;">
                Record a short phrase to enable voice-based attendance.
            </p>
        """, unsafe_allow_html=True)

        audio_data = None
        try:
            audio_data = st.audio_input('Say something like "I am present" or state your name.')

            if audio_data is not None:
                audio_data.seek(0)
                st.session_state['reg_audio_bytes'] = audio_data.read()
                
        except Exception as e:
            logger.error(f"[_registration_panel] audio error: {e}")
            st.error('Audio recording failed.')

        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

        if st.button('Create Account', type='primary', width='stretch'):
            audio_data = st.session_state.get('reg_audio_bytes')
            _handle_registration(new_name, photo_source, audio_data)


def _handle_registration(new_name: str, photo_source, audio_data):
    if not new_name:
        st.warning('Please enter your name to continue.')
        return

    with st.spinner('Creating your profile...'):
        img       = np.array(Image.open(photo_source))
        encodings = get_face_embeddings(img)

        if not encodings:
            st.error('Could not capture facial features. Please retake the photo.')
            return


        face_emb  = encodings[0].flatten().tolist()
        if audio_data:
            # audio_bytes = audio_data.read()
            voice_emb   = get_voice_embedding(audio_data) if audio_data else None
            st.session_state.pop('reg_audio_bytes', None)
        else:
            voice_emb = None

        response_data = create_student(
            new_name,
            face_embeddings=face_emb,
            voice_embeddings=voice_emb
        )

        if not response_data:
            st.error('Account creation failed. Please try again.')
            return

        train_classifier()
        _set_student_session(response_data[0])
        st.toast(f"Profile created! Welcome, {new_name}!")
        st.rerun()


def _set_student_session(student: dict):
    st.session_state.is_logged_in = True
    st.session_state.user_role    = 'student'
    st.session_state.student_data = student


def _build_stats_map(logs: list) -> dict:
    stats_map = {}
    for log in logs:
        sid = log['subject_id']
        if sid not in stats_map:
            stats_map[sid] = {"total": 0, "attended": 0}
        stats_map[sid]['total'] += 1
        if log.get('is_present'):
            stats_map[sid]['attended'] += 1
    return stats_map
