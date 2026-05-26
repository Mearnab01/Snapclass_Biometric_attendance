import streamlit as st


def footer_home():
    logo_url = "https://i.ibb.co/4r5X1FY/apnacollege.png"
    st.markdown(f"""
        <div style="margin-top:2.5rem; padding-top:1.25rem;
                    border-top:1px solid rgba(255,255,255,0.08);
                    display:flex; align-items:center; justify-content:center; gap:8px;">
            <p style="font-size:0.8rem; font-weight:500;
                       color:rgba(255,255,255,0.35); margin:0;">Built by Arnab_Nath</p>
        </div>
    """, unsafe_allow_html=True)


def footer_dashboard():
    logo_url = "https://i.ibb.co/4r5X1FY/apnacollege.png"
    st.markdown(f"""
        <div style="margin-top:2.5rem; padding-top:1.25rem;
                    border-top:1px solid rgba(0,0,0,0.07);
                    display:flex; align-items:center; justify-content:center; gap:8px;">
            <p style="font-size:0.8rem; font-weight:500; color:#a0aec0; margin:0;">Built by Arnab_Nath</p>

        </div>
    """, unsafe_allow_html=True)
