"""
Citizen Dashboard View for CivicEase AI.
Presents government service information in simple plain language, actionable steps, and Tamil translation.
"""
from typing import Any, Dict
import streamlit as st

from database.models import AnalysisRecord, DocumentRecord
from ui.components import render_score_card
from utils.helpers import format_score_badge


def render_citizen_dashboard(doc: DocumentRecord, analysis: AnalysisRecord):
    """Renders citizen-tailored accessibility explanation and checklist."""
    citizen_data = analysis.citizen_explanation or {}
    missing_info = analysis.missing_info or {}
    before_after = analysis.before_after_comparison or {}

    # Language Toggle in Sidebar/Header
    st.markdown("### 🗣 Select Language / மொழியைத் தேர்ந்தெடுக்கவும்")
    lang_col1, lang_col2 = st.columns([1, 3])
    with lang_col1:
        lang_choice = st.radio(
            "Language",
            ["Simple English", "தமிழ் (Tamil)"],
            horizontal=True,
            label_visibility="collapsed"
        )

    is_tamil = "தமிழ்" in lang_choice

    st.markdown("<hr style='margin: 12px 0 20px 0;'>", unsafe_allow_html=True)

    # 1. Top Score & Summary Banner
    col_score, col_quick = st.columns([1, 2], gap="medium")

    with col_score:
        badge = format_score_badge(analysis.composite_score)
        render_score_card(
            composite_score=analysis.composite_score,
            tier_label=analysis.score_tier,
            tier_color=badge["color"],
            tier_desc="Citizen Ease Rating: Indicates how simple this document is for general public understanding."
        )

    with col_quick:
        st.markdown("#### 📌 What You Need to Know at a Glance")
        fields = missing_info.get("fields", [])
        
        qcols = st.columns(2)
        for idx, f in enumerate(fields[:4]):
            target_col = qcols[idx % 2]
            with target_col:
                icon = f.get("badge_icon", "ℹ")
                name = f.get("display_name", "")
                status = f.get("status", "")
                color = f.get("badge_color", "#64748B")
                st.markdown(f"""
                <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-left: 3px solid {color}; border-radius: 6px; padding: 8px 12px; margin-bottom: 8px;">
                    <div style="font-size: 11px; color: #64748B; font-weight: 600;">{name}</div>
                    <div style="font-size: 13px; font-weight: 600; color: {color};">{icon} {status}</div>
                </div>
                """, unsafe_allow_html=True)

        # Critical Warnings Alert
        warnings = citizen_data.get("critical_warnings", [])
        if warnings:
            with st.expander("⚠ Important Warnings & Missing Items", expanded=True):
                for w in warnings:
                    st.markdown(f"<span style='color: #B91C1C; font-size: 13px;'>{w}</span>", unsafe_allow_html=True)

    st.markdown("<hr style='margin: 20px 0;'>", unsafe_allow_html=True)

    # 2. Simple Explanation Section (English vs Tamil)
    if is_tamil:
        st.markdown("### 📖 எளிய விளக்க உரை (Simple Explanation in Tamil)")
        tamil_text = citizen_data.get("tamil_translation", "")
        if tamil_text:
            st.info(tamil_text)
        else:
            st.info("இந்த ஆவணத்தின் எளிய தமிழ் விளக்கம் தயாராகிறது...")
    else:
        st.markdown("### 📖 Plain Language Explanation")
        summary_text = citizen_data.get("brief_summary", citizen_data.get("simplified_english", ""))
        st.markdown(f"""
        <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 10px; padding: 18px; font-size: 15px; line-height: 1.6; color: #1E293B;">
            {summary_text}
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 3. Two Columns: Step-by-Step Procedure & Required Documents Checklist
    c_left, c_right = st.columns([1.2, 1], gap="large")

    with c_left:
        st.markdown("### 📝 How to Apply (Step-by-Step)")
        steps = citizen_data.get("how_to_apply_steps", [])
        if not steps:
            steps = [
                "Check whether you satisfy all eligibility criteria.",
                "Gather the required supporting certificates listed on the right.",
                "Fill out the official application form accurately.",
                "Submit your application to the designated department or online portal."
            ]

        for s_idx, step in enumerate(steps, 1):
            st.markdown(f"""
            <div style="display: flex; align-items: flex-start; margin-bottom: 12px; background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; padding: 12px 16px;">
                <div style="background: #2563EB; color: #FFFFFF; font-weight: 700; width: 26px; height: 26px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 13px; margin-right: 12px; flex-shrink: 0;">
                    {s_idx}
                </div>
                <div style="font-size: 14px; color: #334155; line-height: 1.5; padding-top: 2px;">
                    {step}
                </div>
            </div>
            """, unsafe_allow_html=True)

    with c_right:
        st.markdown("### 📋 Required Documents Checklist")
        st.markdown("<p style='font-size: 12px; color: #64748B;'>Tick the items as you prepare your application:</p>", unsafe_allow_html=True)
        docs = citizen_data.get("documents_checklist", [])
        if not docs:
            docs = [
                "Government Photo ID Proof (Aadhaar / Voter ID / Passport)",
                "Address Proof (Ration Card / Utility Bill)",
                "Income Certificate (if applicable)",
                "Recent Passport-size Photographs"
            ]

        for d_idx, doc_item in enumerate(docs):
            st.checkbox(f" {doc_item}", key=f"chk_doc_{d_idx}", value=False)

    st.markdown("<hr style='margin: 28px 0;'>", unsafe_allow_html=True)

    # 4. Service Facts Grid
    st.markdown("### ℹ Key Service Information")
    info_cols = st.columns(4)
    with info_cols[0]:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-title">👤 Eligibility</div>
            <div style="font-size: 13px; color: #1E293B; font-weight: 500; min-height: 48px;">
        """ + citizen_data.get("who_can_apply", "See document details")[:100] + """
            </div>
        </div>
        """, unsafe_allow_html=True)

    with info_cols[1]:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-title">💳 Application Fee</div>
            <div style="font-size: 13px; color: #1E293B; font-weight: 500; min-height: 48px;">
        """ + citizen_data.get("fee_details", "Not specified")[:100] + """
            </div>
        </div>
        """, unsafe_allow_html=True)

    with info_cols[2]:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-title">📅 Deadline</div>
            <div style="font-size: 13px; color: #1E293B; font-weight: 500; min-height: 48px;">
        """ + citizen_data.get("deadline_details", "Not specified")[:100] + """
            </div>
        </div>
        """, unsafe_allow_html=True)

    with info_cols[3]:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-title">📞 Help & Contact</div>
            <div style="font-size: 13px; color: #1E293B; font-weight: 500; min-height: 48px;">
        """ + citizen_data.get("contact_details", "Not specified")[:100] + """
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr style='margin: 28px 0;'>", unsafe_allow_html=True)

    # 5. Before vs After Comparison Section
    st.markdown("### 🔄 Language Transformation: Before vs After")
    st.markdown("<p style='font-size: 13px; color: #64748B;'>See how bureaucratic legal phrasing is converted into plain, actionable language:</p>", unsafe_allow_html=True)

    bcol1, bcol2 = st.columns(2, gap="medium")
    with bcol1:
        st.markdown("""
        <div class="diff-before">
            <div style="font-size: 11px; font-weight: 700; text-transform: uppercase; margin-bottom: 4px; color: #9F1239;">Original Complex Text (Before)</div>
            <div style="font-size: 13px; line-height: 1.5;">
        """ + before_after.get("before_text", "The applicant shall furnish the requisite documents to the competent authority within the prescribed period.") + """
            </div>
        </div>
        """, unsafe_allow_html=True)

    with bcol2:
        st.markdown("""
        <div class="diff-after">
            <div style="font-size: 11px; font-weight: 700; text-transform: uppercase; margin-bottom: 4px; color: #166534;">Citizen-Friendly Simplified Text (After)</div>
            <div style="font-size: 13px; line-height: 1.5;">
        """ + before_after.get("after_text", "Submit the required documents to the specified government office within 30 days.") + """
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class="disclaimer-text">
        CivicEase AI • Built for Hackathon GOV-29 • Designed for public accessibility
    </div>
    """, unsafe_allow_html=True)
