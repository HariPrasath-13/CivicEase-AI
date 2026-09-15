"""
Passive Voice Detector for CivicEase AI.
Identifies bureaucratic passive voice constructions that obscure responsible actors.
"""
import re
from typing import Any, Dict, List

PASSIVE_PATTERNS = [
    (r"\b(?:is|are|was|were|be|been|being)\s+([a-z]+(?:ed|en|t))\b", "Standard passive construction"),
    (r"\bshall\s+be\s+([a-z]+(?:ed|en|t))\b", "Mandatory passive clause"),
    (r"\bmust\s+be\s+([a-z]+(?:ed|en|t))\b", "Obligatory passive clause"),
    (r"\bto\s+be\s+([a-z]+(?:ed|en|t))\b", "Infinitive passive construction"),
    (r"\bhereby\s+([a-z]+(?:ed|en|t))\b", "Bureaucratic passive notification"),
]

# Words that end with -ed/-en/-t but are adjectives or active forms to ignore
IRREGULAR_NON_PASSIVE = {
    "united", "limited", "interested", "related", "provided", "advanced",
    "competent", "different", "urgent", "current", "present", "frequent"
}


def detect_passive_voice(sentences: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Scans sentences for passive constructions that obscure who performs the action.
    """
    passive_instances: List[Dict[str, Any]] = []

    for item in sentences:
        text = item.get("text", "")
        page = item.get("page", 1)

        for pattern, pattern_desc in PASSIVE_PATTERNS:
            matches = re.finditer(pattern, text, flags=re.IGNORECASE)
            for m in matches:
                verb_part = m.group(1).lower()
                if verb_part in IRREGULAR_NON_PASSIVE:
                    continue

                full_match = m.group(0)
                passive_instances.append({
                    "id": f"passive_{len(passive_instances)}",
                    "category": "Passive Voice",
                    "issue": "Passive Voice Construction",
                    "matched_phrase": full_match,
                    "page": page,
                    "severity": "LOW",
                    "original_text": text,
                    "explanation": f"The phrase '{full_match}' uses passive voice, which obscures who is responsible for executing the step.",
                    "recommendation": "Rewrite in active voice (e.g. 'You must submit...' or 'The applicant must submit...' rather than 'The form shall be submitted')."
                })

    return {
        "passive_instances": passive_instances,
        "total_passive_count": len(passive_instances),
        "passive_percentage": round((len(passive_instances) / max(1, len(sentences))) * 100.0, 1)
    }
