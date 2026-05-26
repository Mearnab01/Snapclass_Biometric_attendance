import streamlit as st
import pandas as pd
from src.database.config import supabase


def render_student_compliance(student_id: int):
    # ── 1. Fetch only subjects the student is currently enrolled in ───────────
    enroll_res = (
        supabase.table("subject_students")
        .select("subject_id")
        .eq("student_id", student_id)
        .execute()
    )
    enrolled_subject_ids = [r["subject_id"] for r in (enroll_res.data or [])]

    if not enrolled_subject_ids:
        st.info("No attendance records yet.")
        return

    # ── 2. Fetch attendance logs restricted to enrolled subjects only ─────────
    res = (
        supabase.table("attendance_logs")
        .select("*, subjects(name, subject_code)")
        .eq("student_id", student_id)
        .in_("subject_id", enrolled_subject_ids)   # ← key fix: ignore unenrolled
        .execute()
    )

    if not res.data:
        st.info("No attendance records yet.")
        return

    df = pd.DataFrame([
        {
            "Subject": r["subjects"]["name"],
            "Code":    r["subjects"]["subject_code"],
            "Present": r["is_present"],
            "Date":    r["timestamp"][:10],
        }
        for r in res.data
    ])

    summary = (
        df.groupby(["Subject", "Code"])["Present"]
        .agg(Total="count", Present="sum")
        .reset_index()
    )
    summary["Rate %"] = (summary["Present"] / summary["Total"] * 100).round(1)
    summary["Status"] = summary["Rate %"].apply(
        lambda r: "🟢 Cleared" if r >= 75 else ("🟡 Warning" if r >= 50 else "🔴 Detained")
    )

    for _, row in summary.iterrows():
        if row["Rate %"] >= 75:
            color, rgb = "#10b981", "16,185,129"
        elif row["Rate %"] >= 50:
            color, rgb = "#f59e0b", "245,158,11"
        else:
            color, rgb = "#ef4444", "239,68,68"

        bg = f"rgba({rgb},0.07)"

        st.markdown(
            f"""
            <div style="background:{bg};border:1px solid {color}30;
            border-radius:12px;padding:16px 20px;margin-bottom:10px;">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <div>
                        <span style="color:#fff;font-weight:600;font-size:0.95rem;">{row['Subject']}</span>
                        <span style="color:#8892b0;font-size:0.78rem;margin-left:10px;">{row['Code']}</span>
                    </div>
                    <span style="color:{color};font-weight:700;font-size:1.1rem;">{row['Rate %']}%</span>
                </div>
                <div style="margin-top:10px;background:rgba(255,255,255,0.06);
                border-radius:100px;height:5px;overflow:hidden;">
                    <div style="width:{row['Rate %']}%;height:100%;
                    background:{color};border-radius:100px;"></div>
                </div>
                <div style="display:flex;justify-content:space-between;margin-top:6px;">
                    <span style="font-size:0.72rem;color:#8892b0;">
                    {int(row['Present'])}/{int(row['Total'])} sessions</span>
                    <span style="font-size:0.72rem;color:{color};font-weight:600;">{row['Status']}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )