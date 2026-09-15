"""
Word and Syntactic Complexity Detector for CivicEase AI.
"""
import re
from typing import Any, Dict, List

from nlp.readability import count_syllables_fallback
from utils.helpers import safe_divide


def analyze_vocabulary_complexity(sentences: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Identifies polysyllabic and unusually complex non-jargon vocabulary across the document.
    """
    difficult_words: List[Dict[str, Any]] = []
    total_words = 0
    complex_words_set = set()

    for item in sentences:
        text = item.get("text", "")
        page = item.get("page", 1)
        tokens = re.findall(r"\b[A-Za-z]{4,}\b", text)

        for token in tokens:
            total_words += 1
            low = token.lower()
            syllables = count_syllables_fallback(low)
            if syllables >= 4 and low not in complex_words_set:
                complex_words_set.add(low)
                difficult_words.append({
                    "word": token,
                    "syllables": syllables,
                    "page": page,
                    "sentence_snippet": text
                })

    difficult_word_ratio = safe_divide(len(complex_words_set), max(1, total_words)) * 100.0

    return {
        "complex_words": difficult_words[:30],  # Sample top complex words
        "unique_complex_count": len(complex_words_set),
        "complex_word_percentage": round(difficult_word_ratio, 1)
    }
