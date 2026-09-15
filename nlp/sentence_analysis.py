"""
Deterministic sentence length analyzer for CivicEase AI.
Detects long and convoluted sentences with page-level traceability.
"""
from typing import Any, Dict, List

from config.settings import SENTENCE_LENGTH_HIGH_SEVERITY, SENTENCE_LENGTH_WARNING
from utils.logging import get_logger

logger = get_logger(__name__)


def analyze_sentence_lengths(sentences: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyzes all segmented sentences in the document for excessive length.

    Thresholds:
      - > 40 words -> High Severity
      - > 25 words -> Warning (Medium Severity)

    Returns:
      Dict with list of flagged issues and summary statistics.
    """
    flagged_sentences: List[Dict[str, Any]] = []
    total_analyzed = len(sentences)
    high_count = 0
    warning_count = 0
    word_counts = []

    for item in sentences:
        wc = item.get("word_count", 0)
        word_counts.append(wc)
        page_num = item.get("page", 1)
        sent_text = item.get("text", "").strip()

        if wc > SENTENCE_LENGTH_HIGH_SEVERITY:
            high_count += 1
            flagged_sentences.append({
                "id": f"sent_{item.get('id', len(flagged_sentences))}",
                "category": "Long Sentences",
                "issue": "Excessively Long Sentence",
                "severity": "HIGH",
                "page": page_num,
                "word_count": wc,
                "original_text": sent_text,
                "explanation": f"This sentence contains {wc} words (exceeds the 40-word limit). Long complex sentences severely degrade comprehension for general citizens.",
                "recommendation": "Break this complex sentence into 2 to 3 concise, focused sentences or a bulleted checklist."
            })
        elif wc > SENTENCE_LENGTH_WARNING:
            warning_count += 1
            flagged_sentences.append({
                "id": f"sent_{item.get('id', len(flagged_sentences))}",
                "category": "Long Sentences",
                "issue": "Long Sentence",
                "severity": "MEDIUM",
                "page": page_num,
                "word_count": wc,
                "original_text": sent_text,
                "explanation": f"This sentence contains {wc} words (exceeds the 25-word readability threshold).",
                "recommendation": "Consider splitting into two shorter sentences or separating clauses with bullet points."
            })

    # Sort flagged sentences: High severity first, then by word count descending
    flagged_sentences.sort(key=lambda x: (0 if x["severity"] == "HIGH" else 1, -x["word_count"]))

    max_len = max(word_counts) if word_counts else 0
    avg_len = sum(word_counts) / len(word_counts) if word_counts else 0

    return {
        "flagged_sentences": flagged_sentences,
        "total_analyzed": total_analyzed,
        "high_severity_count": high_count,
        "warning_severity_count": warning_count,
        "total_flagged": len(flagged_sentences),
        "max_sentence_length": max_len,
        "avg_sentence_length": round(avg_len, 1),
    }
