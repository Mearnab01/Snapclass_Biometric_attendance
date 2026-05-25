import streamlit as st


def header_home():
    logo_url = "https://i.ibb.co/YTYGn5qV/logo.png"
    st.markdown(f"""
        <div style="display:flex; flex-direction:column; align-items:center;
                    justify-content:center; padding:2.5rem 0 2rem 0; gap:0.75rem;">
            <div style="width:76px; height:76px; border-radius:20px;
                        background:rgba(255,255,255,0.06);
                        border:1px solid rgba(255,255,255,0.12);
                        display:flex; align-items:center; justify-content:center;
                        box-shadow:0 4px 24px rgba(0,0,0,0.2);">
                <img src='{logo_url}' style='height:52px; object-fit:contain;'/>
            </div>
            <div style="text-align:center;">
                <h1 style='color:#ffffff; margin:0; letter-spacing:-0.03em;
                            text-shadow:0 2px 20px rgba(67,97,238,0.4);'>SNAP CLASS</h1>
                <p style='color:rgba(255,255,255,0.45); margin:0.35rem 0 0 0;
                           font-size:0.875rem; letter-spacing:0.08em;
                           text-transform:uppercase; font-weight:500;'>
                    Smart Attendance Platform
                </p>
            </div>
        </div>
    """, unsafe_allow_html=True)


def header_dashboard():
    logo_url = "https://i.ibb.co/YTYGn5qV/logo.png"
    st.markdown(f"""
        <div style="display:flex; align-items:center; gap:14px;
                    padding:0.5rem 0 1.25rem 0;
                    border-bottom:1px solid rgba(0,0,0,0.07);
                    margin-bottom:0.5rem;">
            <div style="width:52px; height:52px; border-radius:14px;
                        background:#eef0fc; border:1px solid #dde1f0;
                        display:flex; align-items:center; justify-content:center;
                        flex-shrink:0;">
                <img src='{logo_url}' style='height:34px; object-fit:contain;'/>
            </div>
            <div>
                <h2 style='color:#1a1f3c; margin:0; letter-spacing:-0.02em;'>SNAP CLASS</h2>
                <p style='color:#8892b0; margin:0; font-size:0.78rem;
                           letter-spacing:0.06em; text-transform:uppercase;
                           font-weight:500;'>Dashboard</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
