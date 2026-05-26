import streamlit as st
import numpy as np
import pandas as pd
from datetime import datetime

from src.ui.base_layout import *
from src.components.header import header_dashboard
from src.components.footer import footer_dashboard
from src.components.subject_card import subject_card
from src.components.dialog_create_subject import create_subject_dialog
from src.components.dialog_share_subject import share_subject_dialog
from src.components.dialog_add_photo import add_photos_dialog
from src.components.dialog_attendance_results import attendance_result_dialog
from src.components.dialog_voice_attendance import voice_attendance_dialog
from src.components.dialog_subject_analytics import subject_analytics_dialog

from src.pipelines.face_pipeline import predict_attendance
from src.database.db import (
    check_teacher_exists, create_teacher, teacher_login,
    get_teacher_subjects, get_attendance_for_teacher
)
from src.database.config import supabase


def teacher_screen():
    style_background_dashboard()
    style_base_layout()
    apply_dialog_styles()

    if 'teacher_data' in st.session_state:
        teacher_dashboard()
        return
    if 'teacher_login_type' not in st.session_state:
        st.session_state['teacher_login_type'] = "login"

    # show auth screen
    if st.session_state['teacher_login_type'] == "login":
        teacher_screen_login()
    else:
        teacher_screen_register()


# ── Dashboard ─────────────────────────────────────────────────────────────────

def teacher_dashboard():
    teacher_data = st.session_state.teacher_data

    c1, c2 = st.columns([1, 1], vertical_alignment='center', gap='large')
    with c1:
        header_dashboard()
    with c2:
        if st.button("Logout", type='secondary',icon=":material/logout:", key='teacher_logout_btn'):
            st.session_state['is_logged_in'] = False
            del st.session_state.teacher_data
            st.rerun()
    st.title(f"""Welcome Back, {teacher_data['name']} """)
    st.divider()

    if "current_teacher_tab" not in st.session_state:
        st.session_state.current_teacher_tab = 'take_attendance'

    tab1, tab2, tab3 = st.columns(3, gap='small')
    with tab1:
        t1 = "primary" if st.session_state.current_teacher_tab == 'take_attendance' else "tertiary"
        if st.button('Take Attendance', type=t1, width='stretch', icon=':material/ar_on_you:'):
            st.session_state.current_teacher_tab = 'take_attendance'
            st.rerun()
    with tab2:
        t2 = "primary" if st.session_state.current_teacher_tab == 'manage_subjects' else "tertiary"
        if st.button('Manage Subjects', type=t2, width='stretch', icon=':material/book_ribbon:'):
            st.session_state.current_teacher_tab = 'manage_subjects'
            st.rerun()
    with tab3:
        t3 = "primary" if st.session_state.current_teacher_tab == 'attendance_records' else "tertiary"
        if st.button('Attendance Records', type=t3, width='stretch', icon=':material/cards_stack:'):
            st.session_state.current_teacher_tab = 'attendance_records'
            st.rerun()

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    tab = st.session_state.current_teacher_tab
    if tab == "take_attendance":
        teacher_tab_take_attendance()
    elif tab == "manage_subjects":
        teacher_tab_manage_subjects()
    elif tab == "attendance_records":
        teacher_tab_attendance_records()

    footer_dashboard()


def teacher_tab_take_attendance():
    teacher_id = st.session_state.teacher_data['teacher_id']

    st.markdown("""
        <div style="margin-bottom:1rem;">
            <h3 style="color:#1a1f3c; margin:0;">Take AI Attendance</h3>
            <p style="color:#8892b0; margin:0.25rem 0 0 0; font-size:0.875rem;">
                Upload classroom photos and let the model identify students automatically.
            </p>
        </div>
    """, unsafe_allow_html=True)

    if 'attendance_images' not in st.session_state:
        st.session_state.attendance_images = []

    subjects = get_teacher_subjects(teacher_id)
    if not subjects:
        st.warning('You have not created any subjects yet. Please create one to begin.')
        return

    subject_options = {f"{s['name']} - {s['subject_code']}": s['subject_id'] for s in subjects}

    col1, col2 = st.columns([3, 1], vertical_alignment='bottom')
    with col1:
        selected_subject_label = st.selectbox('Select Subject', options=list(subject_options.keys()))
    with col2:
        if st.button('Add Photos', type='primary', icon=':material/photo_prints:', width='stretch'):
            add_photos_dialog()

    selected_subject_id = subject_options[selected_subject_label]
    st.divider()

    if st.session_state.attendance_images:
        st.markdown("<p style='font-weight:600; color:#1a1f3c; font-size:0.9rem;'>Added Photos</p>",
                    unsafe_allow_html=True)
        gallery_cols = st.columns(4)
        for idx, img in enumerate(st.session_state.attendance_images):
            with gallery_cols[idx % 4]:
                st.image(img, width=400, caption=f'Photo {idx + 1}')
        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    has_photos = bool(st.session_state.attendance_images)
    c1, c2, c3 = st.columns(3, gap='small')

    with c1:
        if st.button('Clear Photos', width='stretch', type='tertiary',
                     icon=':material/delete:', disabled=not has_photos):
            st.session_state.attendance_images = []
            st.rerun()

    with c2:
        if st.button('Run Face Analysis', width='stretch', type='secondary',
                     icon=':material/analytics:', disabled=not has_photos):
            with st.spinner('Deep scanning classroom photos...'):
                all_detected_ids = {}
                for idx, img in enumerate(st.session_state.attendance_images):
                    img_np   = np.array(img.convert('RGB'))
                    detected, _, _ = predict_attendance(img_np)
                    if detected:
                        for sid in detected.keys():
                            all_detected_ids.setdefault(int(sid), []).append(f"Photo {idx + 1}")

                enrolled_res     = supabase.table('subject_students').select("*, students(*)").eq('subject_id', selected_subject_id).execute()
                enrolled_students = enrolled_res.data

                if not enrolled_students:
                    st.warning('No students enrolled in this course.')
                else:
                    results, attendance_to_log = [], []
                    current_timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

                    for node in enrolled_students:
                        student    = node['students']
                        sources    = all_detected_ids.get(int(student['student_id']), [])
                        is_present = len(sources) > 0

                        results.append({
                            "Name":   student['name'],
                            "ID":     student['student_id'],
                            "Source": ", ".join(sources) if is_present else "-",
                            "Status": "Present" if is_present else "Absent"
                        })
                        attendance_to_log.append({
                            'student_id': student['student_id'],
                            'subject_id': selected_subject_id,
                            'timestamp':  current_timestamp,
                            'is_present': bool(is_present)
                        })

                    attendance_result_dialog(pd.DataFrame(results), attendance_to_log)

    with c3:
        if st.button('Voice Attendance', type='primary', width='stretch', icon=':material/mic:'):
            voice_attendance_dialog(selected_subject_id)


def teacher_tab_manage_subjects():
    teacher_id = st.session_state.teacher_data['teacher_id']

    col1, col2 = st.columns([2, 1], vertical_alignment='center')
    with col1:
        st.markdown("""
            <div style="margin-bottom:0.25rem;">
                <p style="color:#8892b0; margin:0.25rem 0 0 0; font-size:0.875rem;">
                    Create and share subjects with students.
                </p>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        if st.button('Create New Subject', width='stretch', type='primary'):
            create_subject_dialog(teacher_id)

    st.divider()

    subjects = get_teacher_subjects(teacher_id)
    if subjects:
        for sub in subjects:
            stats = [
                ("", "Students", sub['total_students']),
                ("", "Classes",  sub['total_classes']),
            ]

            def share_btn(bound_sub=sub):
                c1, c2 = st.columns(2, gap='small')
                with c1:
                    if st.button(
                        f"Share Code",
                        key=f"share_{bound_sub['subject_code']}",
                        icon=":material/share:",
                        width='stretch',
                        type='secondary'
                    ):
                        share_subject_dialog(bound_sub['name'], bound_sub['subject_code'])
                with c2:
                    if st.button(
                        "Analytics",
                        key=f"analytics_{bound_sub['subject_code']}",
                        icon=":material/bar_chart:",
                        width='stretch',
                        type='primary'
                    ):
                        subject_analytics_dialog(bound_sub['subject_id'], bound_sub['name'])

            subject_card(
                name=sub['name'],
                code=sub['subject_code'],
                section=sub['section'],
                stats=stats,
                footer_callback=share_btn
            )
    else:
        st.info("No subjects found. Create one using the button above.")


def teacher_tab_attendance_records():
    st.markdown("""
        <div style="margin-bottom:1rem;">
            <h3 style="color:#1a1f3c; margin:0;">Attendance Records</h3>
            <p style="color:#8892b0; margin:0.25rem 0 0 0; font-size:0.875rem;">
                Full log of all attendance sessions across your subjects.
            </p>
        </div>
    """, unsafe_allow_html=True)

    teacher_id = st.session_state.teacher_data['teacher_id']
    records    = get_attendance_for_teacher(teacher_id)

    if not records:
        st.info("No attendance records found yet.")
        return

    data = []
    for r in records:
        ts = r.get('timestamp')
        data.append({
            "ts_group":    ts.split(".")[0] if ts else None,
            "Time":        datetime.fromisoformat(ts).strftime("%Y-%m-%d %I:%M %p") if ts else "N/A",
            "Subject":     r['subjects']['name'],
            "Subject Code": r['subjects']['subject_code'],
            "is_present":  bool(r.get('is_present', False))
        })

    df = pd.DataFrame(data)
    summary = (
        df.groupby(['ts_group', 'Time', 'Subject', 'Subject Code'])
        .agg(Present_Count=('is_present', 'sum'), Total_Count=('is_present', 'count'))
        .reset_index()
    )
    summary['Attendance Stats'] = (
        summary['Present_Count'].astype(str) + " / "
        + summary['Total_Count'].astype(str) + " Students"
    )
    display_df = summary.sort_values(by='ts_group', ascending=False)[
        ['Time', 'Subject', 'Subject Code', 'Attendance Stats']
    ]
    st.dataframe(display_df, width="stretch", hide_index=True)


# ── Auth screens ──────────────────────────────────────────────────────────────

def _login_teacher(username, password) -> bool:
    if not username or not password:
        return False
    teacher = teacher_login(username, password)
    if teacher:
        st.session_state.user_role    = 'teacher'
        st.session_state.teacher_data = teacher
        st.session_state.is_logged_in = True
        return True
    return False


def teacher_screen_login():
    c1, c2 = st.columns([1, 1], vertical_alignment='center', gap='large')
    with c1:
        header_dashboard()
    with c2:
        if st.button("Go back to Home", type='secondary', key='login_back_btn'):
            st.session_state['login_type'] = None
            st.rerun()

    st.markdown("""
        <div style="text-align:center; padding:1.5rem 0 1rem 0;">
            <h3 style="color:#1a1f3c; margin:0;">Teacher Login</h3>
            <p style="color:#8892b0; margin:0.35rem 0 0 0; font-size:0.875rem;">
                Enter your credentials to access your dashboard.
            </p>
        </div>
    """, unsafe_allow_html=True)

    _, form_col, _ = st.columns([1, 3, 1])
    with form_col:
        username = st.text_input("Username", placeholder='e.g. ananyaroy',      key='login_u')
        password = st.text_input("Password", type='password',                    key='login_p',
                                 placeholder='Enter your password')
        st.divider()
        b1, b2 = st.columns(2, gap='small')
        with b1:
            if st.button("Login", key='loginBtn', shortcut='control+enter',
                         width='stretch', type='primary'):
                if _login_teacher(username, password):
                    st.toast("Welcome back!")
                    st.rerun()
                else:
                    st.error("Invalid username or password.")
        with b2:
            if st.button("Register instead", key='registerBtn',
                         type='secondary', width='stretch'):
                st.session_state.teacher_login_type = 'register'
                st.rerun()

    footer_dashboard()


def _register_teacher(username, name, password, confirm) -> tuple[bool, str]:
    if not all([username, name, password, confirm]):
        return False, "All fields are required."
    if check_teacher_exists(username):
        return False, "Username already taken."
    if password != confirm:
        return False, "Passwords do not match."
    try:
        create_teacher(username, password, name)
        return True, "Account created. Please log in."
    except Exception as e:
        print(f"[_register_teacher] error: {e}")
        return False, "Something went wrong. Please try again."


def teacher_screen_register():
    c1, c2 = st.columns([1, 1], vertical_alignment='center', gap='large')
    with c1:
        header_dashboard()
    with c2:
        if st.button("Go back to Home", type='secondary', key='register_back_btn'):
            st.session_state['login_type'] = None
            st.rerun()

    st.markdown("""
        <div style="text-align:center; padding:1.5rem 0 1rem 0;">
            <h3 style="color:#1a1f3c; margin:0;">Create a Teacher Profile</h3>
            <p style="color:#8892b0; margin:0.35rem 0 0 0; font-size:0.875rem;">
                Fill in your details to get started.
            </p>
        </div>
    """, unsafe_allow_html=True)

    _, form_col, _ = st.columns([1, 3, 1])
    with form_col:
        name    = st.text_input("Full Name",        placeholder='e.g. Ananya Roy',    key='reg_name')
        uname   = st.text_input("Username",         placeholder='e.g. ananyaroy',     key='reg_u')
        pwd     = st.text_input("Password",         type='password',                   key='reg_p',
                                placeholder='Create a password')
        pwd_c   = st.text_input("Confirm Password", type='password',                   key='reg_pc',
                                placeholder='Re-enter password')
        st.divider()
        b1, b2 = st.columns(2, gap='small')
        with b1:
            if st.button("Login instead", key='loginBtn',
                         type='secondary', width='stretch'):
                st.session_state.teacher_login_type = 'login'
                st.rerun()
        with b2:
            if st.button("Register", key='registerBtn',
                         type='primary', width='stretch'):
                success, message = _register_teacher(uname, name, pwd, pwd_c)
                if success:
                    st.success(message)
                    st.session_state.teacher_login_type = "login"
                    st.rerun()
                else:
                    st.error(message)

    footer_dashboard()
