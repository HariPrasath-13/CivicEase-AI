"""
Data models and dataclasses for CivicEase AI storage.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class UserRecord:
    id: Optional[int] = None
    username: str = ""
    password_hash: str = ""
    full_name: str = ""
    role: str = "citizen"  # citizen, auditor, admin
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class DocumentRecord:
    id: Optional[int] = None
    user_id: Optional[int] = None
    filename: str = ""
    file_type: str = ""  # pdf, docx, txt
    file_hash: str = ""
    file_size_bytes: int = 0
    page_count: int = 1
    storage_path: str = ""
    uploaded_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class AnalysisRecord:
    id: Optional[int] = None
    document_id: int = 0
    composite_score: float = 0.0
    score_tier: str = "Moderate"
    score_breakdown: Dict[str, float] = field(default_factory=dict)
    rule_metrics: Dict[str, Any] = field(default_factory=dict)
    detected_issues: List[Dict[str, Any]] = field(default_factory=list)
    missing_info: Dict[str, Any] = field(default_factory=dict)
    citizen_explanation: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[Dict[str, Any]] = field(default_factory=list)
    before_after_comparison: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
