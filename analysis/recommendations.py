"""
Actionable Recommendation Generator for CivicEase AI.
Produces prioritized, evidence-based recommendations strictly mapped to detected issues.
"""
from typing import Any, Dict, List


def generate_prioritized_recommendations(
    all_detected_issues: List[Dict[str, Any]],
    missing_info_data: Dict[str, Any],
    readability_metrics: Dict[str, Any],
    semantic_recommendations: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Consolidates and prioritizes recommendations based on detected problems.
    Avoids generic recommendations not connected to actual document findings.
    """
    recs: List[Dict[str, Any]] = []
    seen_recommendations = set()

    # Add recommendations from LLM / Semantic analyzer
    for item in semantic_recommendations:
        rec_text = item.get("recommendation", "").strip()
        if rec_text and rec_text not in seen_recommendations:
            seen_recommendations.add(rec_text)
            recs.append({
                "category": item.get("category", "General Accessibility"),
                "priority": item.get("priority", "MEDIUM"),
                "recommendation": rec_text,
                "rationale": item.get("rationale", "Directly addresses detected ambiguity.")
            })

    # Rule-driven recommendations based on missing info
    for field in missing_info_data.get("fields", []):
        status = field["status"]
        name = field["display_name"]
        key = field["field_key"]

        if status == "MISSING":
            if key == "fee":
                msg = "Explicitly specify the application fee structure (or explicitly declare 'Application is Free of Cost')."
            elif key == "deadline":
                msg = "Define clear calendar submission dates, seasonal cycles, or 'Applications accepted year-round'."
            elif key == "processing_time":
                msg = "Specify an expected service delivery timeline (e.g. 'Certificate issued within 15 working days')."
            elif key == "contact_information":
                msg = "Provide a public helpdesk number, official email, and physical office location for citizen support."
            elif key == "required_documents":
                msg = "Add a clear checklist of mandatory vs optional documents with acceptable alternatives."
            else:
                msg = f"Add explicit information regarding {name}."

            if msg not in seen_recommendations:
                seen_recommendations.add(msg)
                recs.append({
                    "category": "Information Completeness",
                    "priority": "HIGH" if key in ["fee", "deadline", "required_documents"] else "MEDIUM",
                    "recommendation": msg,
                    "rationale": f"{name} is currently missing from the document."
                })

    # Rule-driven recommendations for long sentences and readability
    avg_slen = readability_metrics.get("avg_sentence_length", 0)
    if avg_slen > 25:
        msg = f"Shorten average sentence length from {avg_slen} words to under 18 words per sentence."
        if msg not in seen_recommendations:
            seen_recommendations.add(msg)
            recs.append({
                "category": "Sentence Structure",
                "priority": "HIGH" if avg_slen > 35 else "MEDIUM",
                "recommendation": msg,
                "rationale": "High average sentence length creates substantial cognitive load for citizens."
            })

    # Sort recommendations by Priority: HIGH -> MEDIUM -> LOW
    priority_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    recs.sort(key=lambda x: priority_order.get(x["priority"], 3))

    return recs
