"""
Composite Accessibility Scoring Engine for CivicEase AI.
Implements the project-defined multi-dimensional accessibility score formula.
"""
from typing import Any, Dict, List, Tuple

from config.settings import SCORE_TIERS, SCORE_WEIGHTS
from utils.helpers import safe_divide
from utils.logging import get_logger

logger = get_logger(__name__)


class AccessibilityScorer:
    """Calculates CivicEase AI Composite Accessibility Score and sub-component breakdowns."""

    def calculate_score(
        self,
        readability_metrics: Dict[str, Any],
        sentence_analysis: Dict[str, Any],
        jargon_analysis: Dict[str, Any],
        passive_analysis: Dict[str, Any],
        semantic_analysis: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Calculates the 6 sub-scores and the composite score:
        Final Score =
          0.20 * Language Score
        + 0.25 * Instruction Score
        + 0.25 * Completeness Score
        + 0.15 * Readability Score
        + 0.10 * Terminology Score
        + 0.05 * Actionability Score
        """
        # 1. Readability Sub-Score (15%)
        # Flesch Reading Ease is already on 0-100 scale
        flesch = readability_metrics.get("flesch_reading_ease", 50.0)
        readability_score = max(0.0, min(100.0, flesch))

        # 2. Language Simplicity Sub-Score (20%)
        # Penalized by long sentences (>25 and >40 words) and complex word density
        total_sentences = max(1, sentence_analysis.get("total_analyzed", 1))
        high_long = sentence_analysis.get("high_severity_count", 0)
        warn_long = sentence_analysis.get("warning_severity_count", 0)
        passive_count = passive_analysis.get("total_passive_count", 0)

        # Long sentence penalty
        long_ratio = ((high_long * 2.5) + (warn_long * 1.0)) / total_sentences
        passive_penalty = min(20.0, (passive_count / total_sentences) * 15.0)
        lang_simplicity_score = max(10.0, min(100.0, 100.0 - (long_ratio * 40.0) - passive_penalty))

        # 3. Instruction Clarity Sub-Score (25%)
        # Evaluates 5W1H issues and ambiguities
        unclear_inst = semantic_analysis.get("unclear_instructions", [])
        ambiguities = semantic_analysis.get("ambiguities", [])
        total_instruction_issues = (len(unclear_inst) * 2.0) + (len(ambiguities) * 1.2)
        instruction_clarity_score = max(10.0, min(100.0, 100.0 - (total_instruction_issues * 7.5)))

        # 4. Information Completeness Sub-Score (25%)
        # 7 Mandatory fields: FOUND = 100, PARTIAL = 60, AMBIGUOUS = 40, MISSING = 0
        missing_fields = semantic_analysis.get("missing_information", [])
        field_scores = []
        status_weights = {
            "FOUND": 100.0,
            "PARTIAL": 60.0,
            "AMBIGUOUS": 40.0,
            "MISSING": 0.0,
        }
        for f in missing_fields:
            status = f.get("status", "MISSING").upper()
            field_scores.append(status_weights.get(status, 0.0))

        completeness_score = (
            sum(field_scores) / len(field_scores) if field_scores else 50.0
        )

        # 5. Terminology Sub-Score (10%)
        # Penalized by jargon frequency per 100 words
        total_words = max(1, readability_metrics.get("total_words", 100))
        total_jargon = jargon_analysis.get("total_jargon_count", 0)
        jargon_per_100 = (total_jargon / total_words) * 100.0
        terminology_score = max(10.0, min(100.0, 100.0 - (jargon_per_100 * 18.0)))

        # 6. Actionability Sub-Score (5%)
        # Presence of structured steps, clear checklist, and minimal ambiguities
        citizen_out = semantic_analysis.get("citizen_output", {})
        steps_count = len(citizen_out.get("how_to_apply_steps", []))
        docs_count = len(citizen_out.get("documents_checklist", []))
        actionability_score = 50.0
        if steps_count >= 3:
            actionability_score += 25.0
        if docs_count >= 1:
            actionability_score += 25.0
        if len(unclear_inst) > 2:
            actionability_score -= 15.0
        actionability_score = max(10.0, min(100.0, actionability_score))

        # Composite Calculation
        final_score = (
            (SCORE_WEIGHTS["language_simplicity"] * lang_simplicity_score)
            + (SCORE_WEIGHTS["instruction_clarity"] * instruction_clarity_score)
            + (SCORE_WEIGHTS["information_completeness"] * completeness_score)
            + (SCORE_WEIGHTS["readability"] * readability_score)
            + (SCORE_WEIGHTS["terminology"] * terminology_score)
            + (SCORE_WEIGHTS["actionability"] * actionability_score)
        )
        final_score = round(max(0.0, min(100.0, final_score)), 1)

        # Determine Tier
        tier_label = "Moderate"
        tier_color = "#F59E0B"
        tier_desc = ""
        for low, high, label, color, desc in SCORE_TIERS:
            if low <= final_score <= high:
                tier_label = label
                tier_color = color
                tier_desc = desc
                break

        breakdown = {
            "language_simplicity": round(lang_simplicity_score, 1),
            "instruction_clarity": round(instruction_clarity_score, 1),
            "information_completeness": round(completeness_score, 1),
            "readability": round(readability_score, 1),
            "terminology": round(terminology_score, 1),
            "actionability": round(actionability_score, 1),
        }

        return {
            "composite_score": final_score,
            "tier_label": tier_label,
            "tier_color": tier_color,
            "tier_description": tier_desc,
            "breakdown": breakdown,
            "disclaimer": "CivicEase AI Composite Accessibility Score (Project-defined multi-metric index, not an official government standard)."
        }


# Global instance
scorer = AccessibilityScorer()
