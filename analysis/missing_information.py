"""
Missing and Unclear Information Aggregator for CivicEase AI.
Classifies and analyzes information completeness across 7 core public service dimensions.
"""
from typing import Any, Dict, List

from config.settings import MANDATORY_SERVICE_FIELDS


def summarize_missing_information(missing_info_fields: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Summarizes the 7 core public service fields.
    Returns status counts, badge icons, and detailed item list.
    """
    field_map = {f["field_key"]: f for f in missing_info_fields}
    full_field_list = []

    status_counts = {"FOUND": 0, "PARTIAL": 0, "AMBIGUOUS": 0, "MISSING": 0}

    status_badges = {
        "FOUND": {"icon": "✅", "label": "Found", "color": "#10B981"},
        "PARTIAL": {"icon": "⚠", "label": "Partial", "color": "#F59E0B"},
        "AMBIGUOUS": {"icon": "❓", "label": "Ambiguous", "color": "#F97316"},
        "MISSING": {"icon": "❌", "label": "Missing", "color": "#EF4444"},
    }

    for key, display_name, desc in MANDATORY_SERVICE_FIELDS:
        existing = field_map.get(key)
        if existing:
            status = existing.get("status", "MISSING").upper()
            details = existing.get("extracted_details", "Not specified in document.")
            reason = existing.get("confidence_reason", "")
        else:
            status = "MISSING"
            details = "Not specified in document."
            reason = "Category was absent from document."

        status_counts[status] = status_counts.get(status, 0) + 1
        badge = status_badges.get(status, status_badges["MISSING"])

        full_field_list.append({
            "field_key": key,
            "display_name": display_name,
            "description": desc,
            "status": status,
            "badge_icon": badge["icon"],
            "badge_label": badge["label"],
            "badge_color": badge["color"],
            "details": details,
            "reason": reason
        })

    total_fields = len(MANDATORY_SERVICE_FIELDS)
    completeness_percentage = round(
        ((status_counts["FOUND"] * 1.0 + status_counts["PARTIAL"] * 0.6 + status_counts["AMBIGUOUS"] * 0.4) / total_fields) * 100.0,
        1
    )

    return {
        "fields": full_field_list,
        "status_counts": status_counts,
        "total_fields": total_fields,
        "completeness_percentage": completeness_percentage
    }
