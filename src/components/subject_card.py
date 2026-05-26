import streamlit as st
def subject_card(name, code, section, stats=None, footer_callback=None):
    html = f"""
        <div style="background:#1e2238; border-left: 8px solid #5b7cff; padding:25px; border-radius: 20px; border: 1px solid #2c3154; margin-bottom:20px;">
        <h3 style="margin:0; color: #ffffff; font-size: 1.5rem ">{name}</h3>
        <p style="color:#aab0d3; margin:10px 0;">Code : <span style="background:rgba(91,124,255,0.15); color:#7f9cff; padding:2px 8px; border-radius:5px;">{code} </span> | Section : {section}</p>
        
        """
    
    if stats:
        html+= """
        <div style="display:flex; gap:8px; flex-wrap:wrap;">
        """
        for icon, label, value in stats:
            html+= f'<div style="background:#15182b; border:1px solid #2c3154; padding:5px 12px; border-radius:12px; font-size:0.9rem; color:#cfd6ff">{icon} <b>{value}</b> {label} </div>'
        
        html+= "</div>"

    st.markdown(html, unsafe_allow_html=True)

    if footer_callback:
        footer_callback()