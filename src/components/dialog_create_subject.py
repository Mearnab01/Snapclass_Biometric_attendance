import streamlit as st
from src.database.db import create_subject
from src.ui.base_layout import apply_dialog_styles


@st.dialog(title="Create Subject")
def create_subject_dialog(teacher_id):
    apply_dialog_styles()
    
    st.write("Enter the name of the subject you want to create.")
    
    sub_id = st.text_input("Subject ID", placeholder="TIU-PCA-101")
    sub_name = st.text_input("Subject Name", placeholder="Introduction to Computer Science")
    sub_section = st.selectbox(
    "Section",
    ["A", "B", "Both"],
    index=None,
    placeholder="Select Section"
)

    if st.button("Create Subject Now", icon=":material/check_circle:", type="primary"):
        if not sub_id or not sub_name or not sub_section:
            st.error("Please fill in all the fields.")
            return
        
        try:
            create_subject(sub_id, sub_name, sub_section, teacher_id)
            st.toast("Subject created successfully!", icon="✅")
            st.rerun()
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
