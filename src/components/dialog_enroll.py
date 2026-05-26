import streamlit as st
from src.database.db import enroll_student_to_subject
from src.database.config import supabase
from ui.base_layout import apply_dialog_styles

def get_available_subjects(student_id):
    all_subjects = supabase.table('subjects').select('subject_id, name, subject_code').execute()
    if not all_subjects.data:
        return []
    enrolled = supabase.table('subject_students').select('subject_id').eq('student_id', student_id).execute()
    enrolled_ids = {e['subject_id'] for e in (enrolled.data or [])}
    return [s for s in all_subjects.data if s['subject_id'] not in enrolled_ids]


@st.dialog("Enroll in Subject")
def enroll_dialog():
    apply_dialog_styles()
    st.markdown('<p class="enroll-hint">Select a subject from the list below to enroll.</p>', unsafe_allow_html=True)

    student_id = st.session_state.student_data['student_id']
    available  = get_available_subjects(student_id)

    if not available:
        st.info("No new subjects available to enroll in.")
        return

    options = {f"{s['name']} — {s['subject_code']}": s for s in available}
    choice  = st.selectbox("Available Subjects", list(options.keys()), index=0)

    if st.button("Enroll now", icon=":material/check_circle:", type="primary", width="stretch"):
        subject = options[choice]
        enroll_student_to_subject(student_id, subject['subject_id'])
        st.success(f"Successfully enrolled in {subject['name']}!")
        st.rerun()