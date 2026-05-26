import streamlit as st
import pandas as pd
from src.database.db import get_attendance_for_subject


@st.dialog("Attendance Analytics")
def subject_analytics_dialog(subject_id: int, subject_name: str):
    st.markdown(f"""
        <div style="margin-bottom:1rem;">
            <h3 style="color:#1a1f3c; margin:0;">{subject_name}</h3>
            <p style="color:#8892b0; margin:0.25rem 0 0 0; font-size:0.875rem;">
                Session-wise attendance breakdown
            </p>
        </div>
    """, unsafe_allow_html=True)

    records = get_attendance_for_subject(subject_id)

    if not records:
        st.info("No attendance records found for this subject yet.")
        return

    # ── Build dataframe ───────────────────────────────────────────────────────
    data = []
    for r in records:
        ts = r.get('timestamp', '')
        data.append({
            "ts_group"  : ts.split(".")[0] if ts else "",
            "Student"   : r['students']['name'],
            "is_present": bool(r.get('is_present', False)),
        })

    df = pd.DataFrame(data)

    # ── Overall stats ─────────────────────────────────────────────────────────
    total_logs   = len(df)
    total_present = df['is_present'].sum()
    attendance_pct = round((total_present / total_logs) * 100, 1) if total_logs > 0 else 0

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Records",   total_logs)
    c2.metric("Present",         int(total_present))
    c3.metric("Avg Attendance",  f"{attendance_pct}%")

    st.divider()

    # ── Per-student summary ───────────────────────────────────────────────────
    st.markdown("**Per Student**")
    student_summary = (
        df.groupby("Student")
        .agg(
            Total    = ("is_present", "count"),
            Attended = ("is_present", "sum"),
        )
        .reset_index()
    )
    student_summary["Attendance %"] = (
        (student_summary["Attended"] / student_summary["Total"] * 100)
        .round(1)
        .astype(str) + "%"
    )
    st.dataframe(student_summary, hide_index=True, width='stretch')

    st.divider()

    # ── Per-session summary ───────────────────────────────────────────────────
    st.markdown("**Per Session**")
    session_summary = (
        df.groupby("ts_group")
        .agg(
            Present = ("is_present", "sum"),
            Total   = ("is_present", "count"),
        )
        .reset_index()
        .sort_values("ts_group", ascending=False)
        .rename(columns={"ts_group": "Session"})
    )
    session_summary["Attendance"] = (
        session_summary["Present"].astype(str) + " / " +
        session_summary["Total"].astype(str)
    )
    st.dataframe(
        session_summary[["Session", "Attendance"]],
        hide_index=True,
        width='stretch'
    )