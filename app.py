"""
CivicEase AI — Government Information Accessibility Analyzer
Main Application Entrypoint and Orchestration Layer.
"""
import io
import os
import shutil
from pathlib import Path
import streamlit as st

# Configure Streamlit page before other imports
st.set_page_config(
    page_title="CivicEase AI — Government Accessibility Analyzer",
    page_icon="🏛",
    layout="wide",
    initial_sidebar_state="expanded"
)

from auth.authentication import (
    get_current_user,
    init_session_state,
    is_authenticated,
    logout_user,
    set_mode,
)
from config.settings import (
    ALLOWED_EXTENSIONS,
    APP_SUBTITLE,
    APP_TITLE,
    MAX_FILE_SIZE_MB,
    SAMPLE_DOCS_DIR,
    UPLOADS_DIR,
)
from database.database import db
from database.models import AnalysisRecord, DocumentRecord
from document.docx_parser import extract_text_from_docx
from document.pdf_parser import extract_text_from_pdf
from document.preprocessing import preprocess_document
from document.txt_parser import extract_text_from_txt
from analysis.accessibility_engine import accessibility_engine
from ui.citizen_dashboard import render_citizen_dashboard
from ui.components import inject_custom_css, render_header
from ui.government_dashboard import render_government_dashboard
from ui.login import render_login_view
from ui.mode_selection import render_mode_selection_view
from utils.helpers import compute_file_hash
from utils.logging import get_logger

logger = get_logger(__name__)


def process_uploaded_document(file_name: str, file_bytes: bytes, user_id: int):
    """Processes uploaded document bytes through extraction, preprocessing, and analysis."""
    suffix = Path(file_name).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        st.error(f"Unsupported file type: {suffix}. Please upload PDF, DOCX, or TXT.")
        return

    if len(file_bytes) == 0:
        st.error("The uploaded document is empty. Please upload a valid document.")
        return

    if len(file_bytes) > MAX_FILE_SIZE_MB * 1024 * 1024:
        st.error(f"File size exceeds the {MAX_FILE_SIZE_MB}MB limit.")
        return

    file_hash = compute_file_hash(file_bytes)
    saved_path = UPLOADS_DIR / f"{file_hash[:12]}_{file_name}"

    with open(saved_path, "wb") as f:
        f.write(file_bytes)

    progress_bar = st.progress(0)
    status_text = st.empty()

    def update_progress(msg: str, pct: int):
        status_text.markdown(f"⏳ **{msg}** ({pct}%)")
        progress_bar.progress(pct / 100.0)

    try:
        update_progress("Extracting document text & structure...", 10)
        if suffix == ".pdf":
            pages_data, meta = extract_text_from_pdf(str(saved_path))
            if meta.get("is_scanned"):
                st.warning("⚠ This appears to be a scanned document with sparse text. Results may be limited.")
        elif suffix == ".docx":
            pages_data, meta = extract_text_from_docx(str(saved_path))
        else:
            pages_data, meta = extract_text_from_txt(str(saved_path))

        # Validate extracted content
        total_text = "".join(p["text"] for p in pages_data).strip()
        if not total_text or len(total_text) < 15:
            st.error("The uploaded document does not contain readable text. Please upload a valid document.")
            progress_bar.empty()
            status_text.empty()
            return

        update_progress("Preprocessing text, sentences & paragraphs...", 20)
        preprocessed = preprocess_document(pages_data)

        # Save document metadata
        doc_record = DocumentRecord(
            user_id=user_id,
            filename=file_name,
            file_type=suffix.replace(".", ""),
            file_hash=file_hash,
            file_size_bytes=len(file_bytes),
            page_count=len(pages_data),
            storage_path=str(saved_path)
        )
        doc_id = db.save_document(doc_record)
        doc_record.id = doc_id

        # Run accessibility engine
        analysis_record = accessibility_engine.analyze_document(
            document_id=doc_id,
            preprocessed_data=preprocessed,
            progress_callback=update_progress
        )

        # Save analysis to database
        analysis_id = db.save_analysis(analysis_record)
        analysis_record.id = analysis_id

        # Store in session state
        st.session_state.current_document = doc_record
        st.session_state.current_analysis = analysis_record

        status_text.success("✓ Document analysis complete!")
        progress_bar.empty()
        status_text.empty()
        st.rerun()

    except Exception as err:
        logger.error("Error analyzing document %s: %s", file_name, str(err), exc_info=True)
        st.error(f"Analysis Error: {str(err)}")
        progress_bar.empty()
        status_text.empty()


def render_sidebar():
    """Renders application navigation sidebar with document upload and mode switcher."""
    user = get_current_user()
    if not user:
        return

    with st.sidebar:
        st.markdown(f"### 🏛 {APP_TITLE}")
        st.markdown(f"<span style='font-size:12px; color:#64748B;'>{APP_SUBTITLE}</span>", unsafe_allow_html=True)
        st.markdown(f"👤 **{user.full_name}** (`{user.username}`)")
        st.markdown("<hr style='margin: 8px 0 16px 0;'>", unsafe_allow_html=True)

        # Active Mode Selector
        st.markdown("#### 🎯 Active User Mode")
        current_mode = st.session_state.get("selected_mode", "citizen")
        mode_radio = st.radio(
            "Select Mode",
            ["Citizen Mode", "Government Auditor Mode"],
            index=0 if current_mode == "citizen" else 1,
            label_visibility="collapsed"
        )
        new_mode = "citizen" if mode_radio == "Citizen Mode" else "auditor"
        if new_mode != current_mode:
            set_mode(new_mode)
            st.rerun()

        st.markdown("<hr style='margin: 16px 0;'>", unsafe_allow_html=True)

        # Document Upload Section
        st.markdown("#### 📤 Upload Government Document")
        uploaded_file = st.file_uploader(
            "Choose a PDF, DOCX, or TXT file",
            type=["pdf", "docx", "txt"],
            label_visibility="collapsed"
        )

        if uploaded_file is not None:
            if st.button("🚀 Analyze Uploaded Document", use_container_width=True, type="primary"):
                process_uploaded_document(uploaded_file.name, uploaded_file.getvalue(), user.id or 1)

        # Sample Document Loader
        st.markdown("<hr style='margin: 14px 0;'>", unsafe_allow_html=True)
        st.markdown("#### 📚 Test with Sample Documents")
        
        sample_files = list(SAMPLE_DOCS_DIR.glob("*.*"))
        sample_options = {f.name: f for f in sample_files if f.suffix.lower() in ALLOWED_EXTENSIONS}

        if sample_options:
            selected_sample = st.selectbox(
                "Select Preloaded Sample",
                list(sample_options.keys()),
                label_visibility="collapsed"
            )
            if st.button("Load Sample Document", use_container_width=True):
                sample_path = sample_options[selected_sample]
                with open(sample_path, "rb") as sf:
                    process_uploaded_document(selected_sample, sf.read(), user.id or 1)
        else:
            st.info("Sample documents are being indexed...")

        st.markdown("<hr style='margin: 16px 0;'>", unsafe_allow_html=True)

        # Logout Button
        if st.button("🚪 Sign Out", use_container_width=True):
            logout_user()
            st.rerun()


def main():
    """Main routing and execution flow."""
    # Inject CSS styles
    inject_custom_css()

    # Initialize session state
    init_session_state()

    # Step 1: Authentication Guard
    if not is_authenticated():
        render_login_view()
        return

    # Step 2: Mode Selection Guard
    if not st.session_state.get("selected_mode"):
        render_mode_selection_view()
        return

    # Step 3: Render Sidebar Controls
    render_sidebar()

    current_doc = st.session_state.get("current_document")
    current_analysis = st.session_state.get("current_analysis")
    active_mode = st.session_state.get("selected_mode", "citizen")
    user = get_current_user()

    # Step 4: If no document is analyzed yet, show initial upload hero
    if not current_doc or not current_analysis:
        render_header(user.full_name if user else None, active_mode)

        st.markdown("""
        <div style="text-align: center; max-width: 650px; margin: 40px auto; background: #FFFFFF; border: 2px dashed #CBD5E1; border-radius: 14px; padding: 40px 24px;">
            <div style="font-size: 48px; margin-bottom: 12px;">📄</div>
            <h3 style="color: #0F172A; margin-bottom: 6px;">No Document Analyzed Yet</h3>
            <p style="color: #64748B; font-size: 14px; margin-bottom: 24px;">
                Upload a government service directive, policy notification, or scheme circular from the sidebar, or pick a sample document to begin instant evaluation.
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Quick sample loader buttons on main canvas
        sample_files = list(SAMPLE_DOCS_DIR.glob("*.*"))
        if sample_files:
            st.markdown("<div style='text-align: center; font-size: 13px; font-weight: 600; color: #64748B; margin-bottom: 12px;'>OR START WITH A SAMPLE GOVERNMENT DOCUMENT:</div>", unsafe_allow_html=True)
            scols = st.columns(len(sample_files[:3]))
            for idx, sfile in enumerate(sample_files[:3]):
                with scols[idx]:
                    if st.button(f"📑 {sfile.stem[:24]}", key=f"hero_sample_{idx}", use_container_width=True):
                        with open(sfile, "rb") as f:
                            process_uploaded_document(sfile.name, f.read(), user.id or 1)
        return

    # Step 5: Render Active Mode Dashboard
    render_header(user.full_name if user else None, active_mode)

    if active_mode == "citizen":
        render_citizen_dashboard(current_doc, current_analysis)
    else:
        render_government_dashboard(current_doc, current_analysis)


if __name__ == "__main__":
    main()
