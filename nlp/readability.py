"""
Readability analysis module for CivicEase AI.
Calculates Flesch Reading Ease, Flesch-Kincaid Grade, average sentence/word length, and complex word ratios.
Provides fallback formulas if textstat is not yet loaded.
"""
import re
from typing import Any, Dict

from utils.helpers import safe_divide
from utils.logging import get_logger

logger = get_logger(__name__)

try:
    import textstat
    HAS_TEXTSTAT = True
except ImportError:
    HAS_TEXTSTAT = False


def count_syllables_fallback(word: str) -> int:
    """Pure-python fallback syllable counter."""
    word = word.lower().strip()
    if not word:
        return 0
    if len(word) <= 3:
        return 1
    # Remove common non-vocalic endings
    word = re.sub(r"(?:[^laeiouy]|ed|es|e)$", "", word)
    word = re.sub(r"^y", "", word)
    matches = re.findall(r"[aeiouy]{1,2}", word)
    return max(1, len(matches))


def compute_readability_metrics(text: str, total_sentences: int, total_words: int) -> Dict[str, Any]:
    """
    Computes deterministic readability scores and linguistic metrics.
    """
    if not text or total_words == 0:
        return {
            "flesch_reading_ease": 0.0,
            "flesch_kincaid_grade": 0.0,
            "gunning_fog": 0.0,
            "avg_sentence_length": 0.0,
            "avg_word_length": 0.0,
            "complex_word_ratio": 0.0,
            "complex_word_count": 0,
            "total_words": 0,
            "total_sentences": 0,
            "interpretation": "Empty Document",
            "tier_color": "#6B7280"
        }

    # Clean text
    clean_text = text.strip()
    words = re.findall(r"\b[A-Za-z0-9'-]+\b", clean_text)
    words_count = max(1, len(words))
    sentences_count = max(1, total_sentences)

    # Complex words (>= 3 syllables)
    complex_words = [w for w in words if count_syllables_fallback(w) >= 3]
    complex_count = len(complex_words)
    complex_ratio = safe_divide(complex_count, words_count) * 100.0

    avg_sentence_len = safe_divide(words_count, sentences_count)
    avg_word_len = safe_divide(sum(len(w) for w in words), words_count)

    if HAS_TEXTSTAT:
        try:
            flesch_score = float(textstat.flesch_reading_ease(clean_text))
            flesch_grade = float(textstat.flesch_kincaid_grade(clean_text))
            gunning_fog = float(textstat.gunning_fog(clean_text))
        except Exception:
            flesch_score = None
    else:
        flesch_score = None

    # Fallback formula: Flesch Reading Ease = 206.835 - (1.015 * ASL) - (84.6 * ASW)
    if flesch_score is None:
        total_syllables = sum(count_syllables_fallback(w) for w in words)
        avg_syllables_per_word = safe_divide(total_syllables, words_count, default=1.5)
        flesch_score = 206.835 - (1.015 * avg_sentence_len) - (84.6 * avg_syllables_per_word)
        flesch_grade = (0.39 * avg_sentence_len) + (11.8 * avg_syllables_per_word) - 15.59
        gunning_fog = 0.4 * (avg_sentence_len + complex_ratio)

    # Bound Flesch score to 0 - 100 range
    flesch_score = max(0.0, min(100.0, round(flesch_score, 1)))
    flesch_grade = max(0.0, round(flesch_grade, 1))
    gunning_fog = max(0.0, round(gunning_fog, 1))

    # Interpret Flesch Score
    if flesch_score >= 85:
        tier = "Very Easy"
        color = "#10B981"
        desc = "Very easy to read. Plain English conversational style suitable for all citizens."
    elif flesch_score >= 70:
        tier = "Easy"
        color = "#3B82F6"
        desc = "Fairly easy to read. Standard everyday communication style."
    elif flesch_score >= 50:
        tier = "Moderate"
        color = "#F59E0B"
        desc = "Moderately difficult. Requires high school reading level or basic civic familiarity."
    elif flesch_score >= 30:
        tier = "Difficult"
        color = "#F97316"
        desc = "Difficult to read. Heavy administrative structure and long sentences."
    else:
        tier = "Very Difficult"
        color = "#EF4444"
        desc = "Extremely difficult and obscure. Dense legal phrasing barrier for general citizens."

    return {
        "flesch_reading_ease": flesch_score,
        "flesch_kincaid_grade": flesch_grade,
        "gunning_fog": gunning_fog,
        "avg_sentence_length": round(avg_sentence_len, 1),
        "avg_word_length": round(avg_word_len, 1),
        "complex_word_ratio": round(complex_ratio, 1),
        "complex_word_count": complex_count,
        "total_words": words_count,
        "total_sentences": sentences_count,
        "interpretation": tier,
        "description": desc,
        "tier_color": color
    }
