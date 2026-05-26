import streamlit as st

from src.screens.home_screen import home_screen
from src.screens.teacher_screen import teacher_screen
from src.screens.student_screen import student_screen
from src.components.dialog_auto_enroll import auto_enroll_dialog

from utils.logger import setup_logger

logger = setup_logger("app")


def main():
    try:
        st.set_page_config(
            page_title='SnapClass - Making Attendance faster using AI',
            page_icon="https://i.ibb.co/YTYGn5qV/logo.png"
        )

        if 'login_type' not in st.session_state:
            st.session_state['login_type'] = None

        logger.info(f"app loaded — login_type={st.session_state['login_type']}")

        match st.session_state['login_type']:
            case 'teacher':
                logger.info("routing to teacher_screen")
                teacher_screen()

            case 'student':
                logger.info("routing to student_screen")
                student_screen()

            case None:
                logger.info("routing to home_screen")
                home_screen()

        join_code = st.query_params.get('join-code')
        if join_code:
            logger.info(f"join-code detected: {join_code}")
            if st.session_state.login_type != 'student':
                st.session_state.login_type = 'student'
                st.rerun()
            if st.session_state.get('is_logged_in') and st.session_state.get('user_role') == 'student':
                auto_enroll_dialog(join_code)

    except Exception:
        logger.critical("unhandled crash in main()", exc_info=True)
        st.error("Something went wrong. Please refresh the page.")


if __name__ == "__main__":
    main()