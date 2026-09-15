"""
Mode Selection View for CivicEase AI.
Enables citizens and auditors to choose their tailored analytical experience.
"""
import streamlit as st

from auth.authentication import set_mode
from ui.components import render_header


def render_mode_selection_view():
    """Renders dual mode selection screen."""
    user = st.session_state.get("user")
    render_header(user.full_name if user else None)

    st.markdown("""
    <div style="text-align: center; max-width: 700px; margin: 0 auto 32px auto;">
        <h2 style="color: #0F172A; font-weight: 700; margin-bottom: 8px;">Select Your Operating Mode</h2>
        <p style="color: #64748B; font-size: 15px;">
            CivicEase AI uses the same centralized document intelligence engine, tailored into distinct experiences for everyday citizens and government officials.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown("""
        <div class="mode-card">
            <div class="mode-icon">👤</div>
            <div class="mode-title">Citizen Mode</div>
            <div class="mode-desc">
                Understand government schemes, eligibility, and requirements in clear plain language with step-by-step checklists and Tamil translation.
            </div>
            <div style="font-size: 12px; color: #10B981; font-weight: 600; margin-bottom: 12px;">
                ✓ Plain English • ✓ Step-by-Step • ✓ Document Checklist • ✓ தமிழ் Support
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Continue as Citizen →", key="btn_select_citizen", use_container_width=True, type="primary"):
            set_mode("citizen")
            st.rerun()

    with col2:
        st.markdown("""
        <div class="mode-card">
            <div class="mode-icon">🏛</div>
            <div class="mode-title">Government Auditor Mode</div>
            <div class="mode-desc">
                Conduct deep accessibility audits on public service orders. Inspect page-level legalese, 5W1H ambiguities, completeness gaps, and export compliance reports.
            </div>
            <div style="font-size: 12px; color: #2563EB; font-weight: 600; margin-bottom: 12px;">
                ✓ Page-Level Traceability • ✓ 5W1H Clarity • ✓ Completeness Matrix • ✓ PDF Reports
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Continue as Auditor →", key="btn_select_auditor", use_container_width=True, type="secondary"):
            set_mode("auditor")
            st.rerun()

    # Information Footer
    st.markdown("""
    <div style="text-align: center; margin-top: 40px; color: #94A3B8; font-size: 13px;">
        💡 You can freely switch between Citizen and Auditor modes at any time from the top navigation bar without re-uploading your document.
    </div>
    """, unsafe_allow_html=True)
