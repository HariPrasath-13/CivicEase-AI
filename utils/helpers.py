"""
General helper functions for CivicEase AI.
"""
import hashlib
import re
from datetime import datetime
from typing import Any, Dict, List, Optional


def compute_file_hash(content: bytes) -> str:
    """Compute SHA-256 hash of file content."""
    return hashlib.sha256(content).hexdigest()


def truncate_text(text: str, max_chars: int = 140) -> str:
    """Safely truncate text for cards and previews."""
    if not text:
        return ""
    text = text.strip().replace("\n", " ")
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 3].rstrip() + "..."


def format_timestamp(dt: Optional[datetime] = None) -> str:
    """Format datetime into standard readable string."""
    if dt is None:
        dt = datetime.now()
    return dt.strftime("%B %d, %Y %I:%M %p")


def clean_whitespace(text: str) -> str:
    """Collapse redundant whitespace and tabs."""
    if not text:
        return ""
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n\n", text)
    return text.strip()


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safely divide numbers with zero-division guard."""
    if denominator == 0:
        return default
    return numerator / denominator


def format_score_badge(score: float) -> Dict[str, str]:
    """Return styling attributes based on composite score."""
    score = round(score, 1)
    if score >= 85:
        return {"label": "Very Easy", "color": "#10B981", "bg": "#ECFDF5", "icon": "🟢"}
    elif score >= 70:
        return {"label": "Easy", "color": "#3B82F6", "bg": "#EFF6FF", "icon": "🔵"}
    elif score >= 50:
        return {"label": "Moderate", "color": "#F59E0B", "bg": "#FEF3C7", "icon": "🟡"}
    elif score >= 30:
        return {"label": "Difficult", "color": "#F97316", "bg": "#FFEDD5", "icon": "🟠"}
    else:
        return {"label": "Very Difficult", "color": "#EF4444", "bg": "#FEE2E2", "icon": "🔴"}
