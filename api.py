"""
CivicEase AI — Complete End-to-End REST API Service.
FastAPI implementation exposing document analysis, rule-based NLP, semantic AI,
citizen/auditor views, Tamil simplification, and PDF/Markdown report export.
"""
import io
import os
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import Depends, FastAPI, File, Form, HTTPException, Query, Response, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from pydantic import BaseModel, Field

from config.settings import (
    ALLOWED_EXTENSIONS,
    APP_SUBTITLE,
    APP_TAGLINE,
    APP_TITLE,
    APP_VERSION,
    MAX_FILE_SIZE_MB,
    SAMPLE_DOCS_DIR,
    UPLOADS_DIR,
)
from database.database import db
from database.models import AnalysisRecord, DocumentRecord, UserRecord
from document.docx_parser import extract_text_from_docx
from document.pdf_parser import extract_text_from_pdf
from document.preprocessing import preprocess_document
from document.txt_parser import extract_text_from_txt
from analysis.accessibility_engine import accessibility_engine
from ai.simplifier import simplifier
from reports.report_generator import report_generator
from utils.helpers import compute_file_hash, format_score_badge
from utils.logging import get_logger

logger = get_logger("civicease.api")

# Initialize FastAPI app
api_app = FastAPI(
    title=f"{APP_TITLE} API",
    description=f"**{APP_SUBTITLE}**\n\n{APP_TAGLINE}\n\n"
                "Comprehensive REST API providing hybrid AI and rule-based NLP analysis for government service documents, "
                "citizen-friendly plain language transformation, Tamil translation, page-level issue auditing, and report generation.",
    version=APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Enable CORS for external frontend or mobile clients
api_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==============================================================================
# Pydantic Request & Response Schemas
# ==============================================================================

class LoginRequest(BaseModel):
    username: str = Field(..., example="citizen")
    password: str = Field(..., example="citizen123")


class RegisterRequest(BaseModel):
    username: str = Field(..., example="priya_sharma")
    password: str = Field(..., example="password123")
    full_name: str = Field(..., example="Priya Sharma")
    role: str = Field(default="citizen", example="citizen", description="'citizen' or 'auditor'")


class TextAnalysisRequest(BaseModel):
    title: str = Field(default="Government Circular", example="Pension Scheme Guidelines")
    text_content: str = Field(
        ...,
        example="The applicant shall furnish the requisite documents to the competent authority within the prescribed period."
    )
    user_id: Optional[int] = Field(default=1)


class SimplifyRequest(BaseModel):
    text: str = Field(
        ...,
        example="The applicant shall furnish the requisite documents to the competent authority."
    )
    context_topic: Optional[str] = Field(default="Government Service")


# ==============================================================================
# Helper Functions
# ==============================================================================

def _process_file_data(filename: str, file_bytes: bytes, user_id: int = 1) -> Dict[str, Any]:
    """Extracts, preprocesses, and analyzes document bytes."""
    suffix = Path(filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file extension '{suffix}'. Allowed: {list(ALLOWED_EXTENSIONS)}"
        )

    if len(file_bytes) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty.")

    if len(file_bytes) > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File exceeds maximum allowed size of {MAX_FILE_SIZE_MB}MB."
        )

    file_hash = compute_file_hash(file_bytes)
    saved_path = UPLOADS_DIR / f"{file_hash[:12]}_{filename}"
    with open(saved_path, "wb") as f:
        f.write(file_bytes)

    # 1. Extraction
    if suffix == ".pdf":
        pages_data, meta = extract_text_from_pdf(str(saved_path))
    elif suffix == ".docx":
        pages_data, meta = extract_text_from_docx(str(saved_path))
    else:
        pages_data, meta = extract_text_from_txt(str(saved_path))

    # Validate extracted text
    total_text = "".join(p["text"] for p in pages_data).strip()
    if not total_text or len(total_text) < 15:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="The document does not contain sufficient readable text or appears to be a scanned image."
        )

    # 2. Preprocessing
    preprocessed = preprocess_document(pages_data)

    # 3. Database saving
    doc_record = DocumentRecord(
        user_id=user_id,
        filename=filename,
        file_type=suffix.replace(".", ""),
        file_hash=file_hash,
        file_size_bytes=len(file_bytes),
        page_count=len(pages_data),
        storage_path=str(saved_path)
    )
    doc_id = db.save_document(doc_record)
    doc_record.id = doc_id

    # 4. Accessibility Analysis
    analysis_record = accessibility_engine.analyze_document(doc_id, preprocessed)
    analysis_id = db.save_analysis(analysis_record)
    analysis_record.id = analysis_id

    return {
        "document_id": doc_id,
        "analysis_id": analysis_id,
        "filename": filename,
        "page_count": len(pages_data),
        "composite_score": analysis_record.composite_score,
        "score_tier": analysis_record.score_tier,
        "score_breakdown": analysis_record.score_breakdown,
        "rule_metrics": analysis_record.rule_metrics,
        "missing_information": analysis_record.missing_info,
        "citizen_explanation": analysis_record.citizen_explanation,
        "recommendations": analysis_record.recommendations,
        "detected_issues": analysis_record.detected_issues,
        "before_after_comparison": analysis_record.before_after_comparison,
        "total_issues_count": len(analysis_record.detected_issues),
    }


# ==============================================================================
# API Endpoints
# ==============================================================================

@api_app.get("/", tags=["System"])
def root_endpoint():
    """Root metadata endpoint."""
    return {
        "app": APP_TITLE,
        "subtitle": APP_SUBTITLE,
        "version": APP_VERSION,
        "status": "online",
        "documentation": "/docs",
        "supported_modes": ["citizen", "auditor"],
        "supported_formats": list(ALLOWED_EXTENSIONS),
    }


@api_app.get("/health", tags=["System"])
def health_check():
    """System health check endpoint."""
    return {"status": "healthy", "service": "CivicEase AI"}


# ------------------------------------------------------------------------------
# Authentication
# ------------------------------------------------------------------------------

@api_app.post("/api/auth/login", tags=["Authentication"])
def login(req: LoginRequest):
    """Authenticate user with username and password."""
    user = db.authenticate_user(req.username.strip(), req.password.strip())
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password. Use demo accounts: citizen/citizen123 or auditor/auditor123"
        )
    return {
        "status": "success",
        "user_id": user.id,
        "username": user.username,
        "full_name": user.full_name,
        "role": user.role,
        "message": f"Welcome {user.full_name}!"
    }


@api_app.post("/api/auth/register", tags=["Authentication"])
def register(req: RegisterRequest):
    """Register a new user account."""
    if req.role not in ["citizen", "auditor"]:
        raise HTTPException(status_code=400, detail="Role must be either 'citizen' or 'auditor'")
    user = db.register_user(req.username.strip(), req.password.strip(), req.full_name.strip(), req.role)
    if not user:
        raise HTTPException(status_code=409, detail="Username already exists.")
    return {
        "status": "created",
        "user_id": user.id,
        "username": user.username,
        "full_name": user.full_name,
        "role": user.role
    }


@api_app.get("/api/auth/demo-users", tags=["Authentication"])
def get_demo_users():
    """List available quick-access demo credentials."""
    return [
        {"username": "citizen", "password": "citizen123", "role": "citizen", "description": "Priya Sharma (Citizen Mode)"},
        {"username": "auditor", "password": "auditor123", "role": "auditor", "description": "Dr. Rajesh Kumar (Government Auditor Mode)"},
        {"username": "admin", "password": "admin123", "role": "admin", "description": "System Administrator"},
    ]


# ------------------------------------------------------------------------------
# Document Upload & Analysis
# ------------------------------------------------------------------------------

@api_app.post("/api/documents/upload-and-analyze", tags=["Document Analysis"])
async def upload_and_analyze_document(
    file: UploadFile = File(..., description="Government document file (PDF, DOCX, or TXT)"),
    user_id: int = Form(1, description="ID of the authenticated user")
):
    """
    Upload a government document (PDF, DOCX, TXT) and run the full end-to-end accessibility pipeline.
    Returns complete JSON with composite score, 5W1H ambiguities, missing information, citizen summary, and auditor issues.
    """
    file_bytes = await file.read()
    return _process_file_data(file.filename, file_bytes, user_id)


@api_app.post("/api/documents/analyze-text", tags=["Document Analysis"])
def analyze_raw_text(req: TextAnalysisRequest):
    """
    Directly analyze raw government circular or policy text without file upload.
    """
    text_bytes = req.text_content.encode("utf-8")
    filename = f"{req.title.replace(' ', '_')}.txt"
    return _process_file_data(filename, text_bytes, req.user_id or 1)


@api_app.get("/api/documents/samples", tags=["Sample Documents"])
def list_sample_documents():
    """List all preloaded sample government documents available for testing."""
    samples = []
    for f in SAMPLE_DOCS_DIR.glob("*.*"):
        if f.suffix.lower() in ALLOWED_EXTENSIONS:
            samples.append({
                "filename": f.name,
                "format": f.suffix.replace(".", "").upper(),
                "size_bytes": f.stat().st_size,
                "path": str(f)
            })
    return samples


@api_app.post("/api/documents/analyze-sample/{sample_filename}", tags=["Sample Documents"])
def analyze_sample_document(sample_filename: str, user_id: int = Query(1)):
    """
    Instantly analyze one of the preloaded sample government documents by filename.
    """
    sample_path = SAMPLE_DOCS_DIR / sample_filename
    if not sample_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Sample document '{sample_filename}' not found. Check /api/documents/samples for available files."
        )
    with open(sample_path, "rb") as f:
        file_bytes = f.read()
    return _process_file_data(sample_filename, file_bytes, user_id)


# ------------------------------------------------------------------------------
# Mode-Specific Tailored Views
# ------------------------------------------------------------------------------

@api_app.get("/api/analysis/{analysis_id}/citizen-view", tags=["Mode Views"])
def get_citizen_view(analysis_id: int):
    """
    Get citizen-tailored explanation, step-by-step application instructions,
    required documents checklist, and Tamil translation.
    """
    analysis = db.get_analysis_by_id(analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail=f"Analysis with ID {analysis_id} not found.")

    badge = format_score_badge(analysis.composite_score)
    citizen_out = analysis.citizen_explanation or {}
    missing_info = analysis.missing_info or {}
    before_after = analysis.before_after_comparison or {}

    return {
        "analysis_id": analysis.id,
        "document_id": analysis.document_id,
        "composite_score": analysis.composite_score,
        "accessibility_tier": analysis.score_tier,
        "tier_badge": badge,
        "service_name": citizen_out.get("service_name", "Public Service Scheme"),
        "what_you_need_to_know": [
            {
                "field": f.get("display_name"),
                "status": f.get("status"),
                "icon": f.get("badge_icon"),
                "details": f.get("details")
            }
            for f in missing_info.get("fields", [])[:4]
        ],
        "plain_explanation_english": citizen_out.get("brief_summary", citizen_out.get("simplified_english", "")),
        "plain_explanation_tamil": citizen_out.get("tamil_translation", ""),
        "how_to_apply_steps": citizen_out.get("how_to_apply_steps", []),
        "required_documents_checklist": citizen_out.get("documents_checklist", []),
        "key_service_facts": {
            "eligibility": citizen_out.get("who_can_apply", "See details"),
            "fee": citizen_out.get("fee_details", "Not specified"),
            "deadline": citizen_out.get("deadline_details", "Not specified"),
            "processing_time": citizen_out.get("processing_time_details", "Not specified"),
            "contact_helpdesk": citizen_out.get("contact_details", "Not specified"),
        },
        "critical_warnings": citizen_out.get("critical_warnings", []),
        "before_vs_after_sample": before_after
    }


@api_app.get("/api/analysis/{analysis_id}/auditor-view", tags=["Mode Views"])
def get_auditor_view(
    analysis_id: int,
    severity: Optional[str] = Query(None, description="Filter by severity: HIGH, MEDIUM, LOW"),
    category: Optional[str] = Query(None, description="Filter by category"),
    page: Optional[int] = Query(None, description="Filter by page number")
):
    """
    Get full technical auditor view with page-level issue traceability,
    severity breakdown, 6-pillar score calculation, 7-field completeness matrix, and recommendations.
    """
    analysis = db.get_analysis_by_id(analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail=f"Analysis with ID {analysis_id} not found.")

    rule_metrics = analysis.rule_metrics or {}
    all_issues = analysis.detected_issues or []

    # Apply filters
    filtered_issues = []
    for item in all_issues:
        if severity and item.get("severity", "").upper() != severity.upper():
            continue
        if category and item.get("category", "").lower() != category.lower():
            continue
        if page is not None and item.get("page") != page:
            continue
        filtered_issues.append(item)

    return {
        "analysis_id": analysis.id,
        "document_id": analysis.document_id,
        "composite_score": analysis.composite_score,
        "accessibility_tier": analysis.score_tier,
        "score_breakdown": analysis.score_breakdown,
        "severity_summary": rule_metrics.get("severity_counts", {}),
        "category_distribution": rule_metrics.get("category_counts", {}),
        "readability_metrics": rule_metrics.get("readability", {}),
        "information_completeness_matrix": analysis.missing_info,
        "total_issues_count": len(all_issues),
        "filtered_issues_count": len(filtered_issues),
        "detected_issues": filtered_issues,
        "prioritized_recommendations": analysis.recommendations,
        "before_after_comparison": analysis.before_after_comparison,
        "disclaimer": "CivicEase AI Composite Score (Project-defined multi-metric index)."
    }


# ------------------------------------------------------------------------------
# Simplification & Translation Endpoint
# ------------------------------------------------------------------------------

@api_app.post("/api/simplify", tags=["Language Simplification"])
def simplify_custom_text(req: SimplifyRequest):
    """
    Simplify arbitrary government/legal text into Plain English and natural Tamil.
    """
    result = simplifier.simplify_text(req.text, req.context_topic or "Government Service")
    return {
        "original_text": req.text,
        "simplified_english": result.get("simplified_english"),
        "tamil_translation": result.get("tamil_translation")
    }


# ------------------------------------------------------------------------------
# Report Generation & Download
# ------------------------------------------------------------------------------

@api_app.get("/api/reports/{analysis_id}/pdf", tags=["Reports"])
def download_pdf_report(analysis_id: int):
    """
    Download a formatted PDF audit report for a given analysis ID.
    """
    analysis = db.get_analysis_by_id(analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail=f"Analysis with ID {analysis_id} not found.")

    doc = DocumentRecord(id=analysis.document_id, filename=f"Document_{analysis.document_id}", page_count=1)
    pdf_bytes = report_generator.generate_pdf_report(doc, analysis)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=CivicEase_Audit_Report_{analysis_id}.pdf"}
    )


@api_app.get("/api/reports/{analysis_id}/markdown", tags=["Reports"])
def download_markdown_report(analysis_id: int):
    """
    Download Markdown audit report text for a given analysis ID.
    """
    analysis = db.get_analysis_by_id(analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail=f"Analysis with ID {analysis_id} not found.")

    doc = DocumentRecord(id=analysis.document_id, filename=f"Document_{analysis.document_id}", page_count=1)
    md_text = report_generator.generate_markdown_report(doc, analysis)

    return Response(
        content=md_text,
        media_type="text/markdown",
        headers={"Content-Disposition": f"attachment; filename=CivicEase_Audit_Report_{analysis_id}.md"}
    )


# ------------------------------------------------------------------------------
# History & Recent Documents
# ------------------------------------------------------------------------------

@api_app.get("/api/history", tags=["History"])
def get_analysis_history(limit: int = Query(10, ge=1, le=50)):
    """Retrieve recent document analysis records."""
    return db.get_recent_analyses(limit=limit)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:api_app", host="0.0.0.0", port=8000, reload=True)
