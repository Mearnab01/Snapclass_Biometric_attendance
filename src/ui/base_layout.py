import streamlit as st


def style_background_home():
    st.markdown("""
        <style>
        .stApp {
            background: linear-gradient(135deg, #0f1123 0%, #1a1f3c 60%, #0f1123 100%) !important;
            min-height: 100vh;
        }
        .stApp div[data-testid="stColumn"] {
            background: rgba(255,255,255,0.04) !important;
            backdrop-filter: blur(12px) !important;
            -webkit-backdrop-filter: blur(12px) !important;
            padding: 2.5rem !important;
            border-radius: 1.5rem !important;
            border: 1px solid rgba(255,255,255,0.08) !important;
            box-shadow: 0 8px 32px rgba(0,0,0,0.3) !important;
        }
        </style>
    """, unsafe_allow_html=True)


def style_background_dashboard():
    st.markdown("""
        <style>
        .stApp {
            background: linear-gradient(135deg, #0f1123 0%, #1a1f3c 60%, #0f1123 100%) !important;
            min-height: 100vh;
        }
        .stApp div[data-testid="stColumn"] {
            background: transparent !important;
            padding: 0 !important;
            border-radius: 0 !important;
            border: none !important;
            box-shadow: none !important;
        }
        </style>
    """, unsafe_allow_html=True)


def style_base_layout():
    st.markdown("""
        <style>
        /* ── Layout ── */
        #MainMenu, footer, header { display: block !important; }
        .block-container {
            padding-top: 1.75rem !important;
            padding-bottom: 2rem !important;
            max-width: 960px;
        }

        /* ── Typography ── */
        h1 {
            font-family: sans-serif !important;
            font-weight: 800 !important;
            font-size: 3rem !important;
            line-height: 1.05 !important;
            letter-spacing: -0.02em !important;
            margin-bottom: 0.25rem !important;
        }
        h2 {
            font-family: 'Syne', sans-serif !important;
            font-weight: 700 !important;
            font-size: 1.75rem !important;
            line-height: 1.1 !important;
            letter-spacing: -0.015em !important;
            margin-bottom: 0.25rem !important;
        }
        h3 {
            font-family: 'Syne', sans-serif !important;
            font-weight: 600 !important;
            font-size: 1.2rem !important;
            letter-spacing: -0.01em !important;
        }
        h4, p, li, label { font-family: 'DM Sans', sans-serif !important; }
        p {
            font-size: 0.95rem !important;
            line-height: 1.65 !important;
            font-weight: 400 !important;
        }

        /* ── Inputs (global) ── */
        .stApp input,
        .stTextInput input,
        .stTextArea textarea {
            font-family: 'DM Sans', sans-serif !important;
            font-size: 0.9rem !important;
            border-radius: 0.6rem !important;
            border: 1.5px solid #e2e5f0 !important;
            background: #fafbff !important;
            color: #1a1f3c !important;
            padding: 10px 14px !important;
            transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
        }
        .stTextInput input:focus,
        .stTextArea textarea:focus {
            border-color: #4361EE !important;
            box-shadow: 0 0 0 3px rgba(67,97,238,0.12) !important;
            outline: none !important;
        }

        /* ── Buttons ── */
        .stButton > button {
            font-family: 'DM Sans', sans-serif !important;
            font-weight: 600 !important;
            font-size: 0.875rem !important;
            letter-spacing: 0.01em !important;
            border-radius: 0.6rem !important;
            border: none !important;
            padding: 0.55rem 1.4rem !important;
            transition: all 0.2s ease !important;
        }
        button[kind="primary"] {
            background: #4361EE !important;
            color: #fff !important;
            box-shadow: 0 2px 8px rgba(67,97,238,0.35) !important;
        }
        button[kind="primary"]:hover {
            background: #3451d1 !important;
            box-shadow: 0 4px 16px rgba(67,97,238,0.45) !important;
            transform: translateY(-1px) !important;
        }
        button[kind="secondary"] {
            background: #F72585 !important;
            color: #fff !important;
            box-shadow: 0 2px 8px rgba(247,37,133,0.3) !important;
        }
        button[kind="secondary"]:hover {
            background: #d91e72 !important;
            box-shadow: 0 4px 16px rgba(247,37,133,0.4) !important;
            transform: translateY(-1px) !important;
        }
        button[kind="tertiary"] {
            background: #1a1f3c !important;
            color: #fff !important;
            box-shadow: 0 2px 8px rgba(0,0,0,0.15) !important;
        }
        button[kind="tertiary"]:hover {
            background: #0f1123 !important;
            box-shadow: 0 4px 16px rgba(0,0,0,0.25) !important;
            transform: translateY(-1px) !important;
        }
        .stButton > button:active { transform: translateY(0) !important; }

        /* ── Misc ── */
        hr {
            border: none !important;
            border-top: 1px solid rgba(0,0,0,0.07) !important;
            margin: 1.5rem 0 !important;
        }
        ::-webkit-scrollbar { width: 5px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: #c7cbe8; border-radius: 999px; }
        </style>
    """, unsafe_allow_html=True)


def apply_attendance_styles():
    st.markdown("""
        <style>
        .att-header { font-size: 1.6rem; font-weight: 700; color: #fff; margin-bottom: 0.25rem; }
        .att-sub { color: #8892b0; font-size: 0.875rem; margin-bottom: 1.5rem; }
        .gallery-caption { text-align: center; font-size: 0.75rem; color: #8892b0; margin-top: 4px; }
        </style>
    """, unsafe_allow_html=True)


def apply_dialog_styles():
    st.markdown("""
        <style>
        /* ── Dialog container ── */
        div[data-testid="stDialog"] div[role="dialog"] {
            background: linear-gradient(135deg, #0f1123 0%, #1a1f3c 60%, #0f1123 100%) !important;
            border: 1px solid rgba(88,101,242,0.3);
            border-radius: 16px;
            overflow: visible !important;
        }

        /* ── Dialog inputs ── */
        div[data-testid="stDialog"] .stTextInput input,
        div[data-testid="stDialog"] .stTextArea textarea {
            background: #15182b !important;
            border: 1px solid #2c3154 !important;
            color: #fff !important;
            border-radius: 8px;
        }

        /* ── Dialog buttons ── */
        div[data-testid="stDialog"] button[kind="primary"] {
            background: #5865F2 !important;
            box-shadow: none !important;
        }
        div[data-testid="stDialog"] button[kind="primary"]:hover {
            background: #4752C4 !important;
            box-shadow: 0 6px 20px rgba(88,101,242,0.4) !important;
        }
        div[data-testid="stDialog"] button[kind="tertiary"] {
            background: transparent !important;
            border: 1px solid rgba(255,255,255,0.1) !important;
            color: #8892b0 !important;
            box-shadow: none !important;
        }
        div[data-testid="stDialog"] button[kind="tertiary"]:hover {
            border-color: rgba(255,255,255,0.25) !important;
            color: #fff !important;
        }

        /* ── Selectbox trigger ── */
        
        div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
            background: #15182b !important;
            border: 1px solid rgba(88,101,242,0.4) !important;
            border-radius: 10px !important;
        }
        div[data-testid="stSelectbox"] div[data-baseweb="select"] > div:hover {
            border-color: #5865F2 !important;
            box-shadow: 0 0 0 3px rgba(88,101,242,0.15) !important;
        }

        /* ── Selectbox dropdown list ── */
        ul[data-testid="stSelectboxVirtualDropdown"] {
            background: #1a1f3c !important;
            border: 1px solid rgba(88,101,242,0.3) !important;
            border-radius: 10px !important;
            padding: 6px !important;
            box-shadow: 0 16px 48px rgba(0,0,0,0.6) !important;
            z-index: 99999 !important;
        }
        ul[data-testid="stSelectboxVirtualDropdown"] li {
            border-radius: 8px !important;
            color: #aab0d3 !important;
            padding: 10px 14px !important;
        }
        ul[data-testid="stSelectboxVirtualDropdown"] li:hover {
            background: rgba(88,101,242,0.15) !important;
            color: #fff !important;
        }
        ul[data-testid="stSelectboxVirtualDropdown"] li[aria-selected="true"] {
            background: rgba(88,101,242,0.25) !important;
            color: #fff !important;
            font-weight: 600;
        }

        /* ── Utility classes ── */
        .att-stat {
            background: rgba(88,101,242,0.08);
            border: 1px solid rgba(88,101,242,0.2);
            border-radius: 12px;
            padding: 14px 20px;
            text-align: center;
        }
        .att-stat-val { font-size: 1.8rem; font-weight: 700; color: #fff; display: block; line-height: 1; }
        .att-stat-label { font-size: 0.72rem; color: #8892b0; text-transform: uppercase; letter-spacing: 0.07em; margin-top: 4px; display: block; }

        .qr-card { background: #15182b; border: 1px solid rgba(88,101,242,0.2); border-radius: 12px; padding: 20px; }
        .qr-label { font-size: 0.75rem; font-weight: 700; color: #8892b0; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 8px; }

        .dialog-hint { color: #8892b0; font-size: 0.85rem; margin-bottom: 1rem; line-height: 1.6; }

        .badge-present { background: rgba(16,185,129,0.15); color: #10b981; padding: 3px 10px; border-radius: 100px; font-size: 0.75rem; font-weight: 600; }
        .badge-absent  { background: rgba(239,68,68,0.12);  color: #ef4444; padding: 3px 10px; border-radius: 100px; font-size: 0.75rem; font-weight: 600; }
        </style>
    """, unsafe_allow_html=True)