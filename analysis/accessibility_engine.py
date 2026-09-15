"""
Master Accessibility Analysis Engine for CivicEase AI.
Integrates Rule-Based NLP, Semantic AI Analysis, Missing Information Engine, and Composite Scoring.
"""
from typing import Any, Dict, List

from ai.semantic_analyzer import semantic_analyzer
from analysis.missing_information import summarize_missing_information
from analysis.recommendations import generate_prioritized_recommendations
from analysis.scoring import scorer
from database.models import AnalysisRecord
from nlp.complexity_detector import analyze_vocabulary_complexity
from nlp.jargon_detector import detect_jargon_terms
from nlp.passive_voice import detect_passive_voice
from nlp.readability import compute_readability_metrics
from nlp.sentence_analysis import analyze_sentence_lengths
from utils.logging import get_logger

logger = get_logger(__name__)


class AccessibilityEngine:
    """Master engine for unified document accessibility analysis."""

    def analyze_document(
        self,
        document_id: int,
        preprocessed_data: Dict[str, Any],
        progress_callback=None
    ) -> AnalysisRecord:
        """
        Executes complete hybrid analysis pipeline on preprocessed document data.
        Calls optional progress_callback(step_name, percent).
        """
        sentences = preprocessed_data.get("sentences", [])
        total_words = preprocessed_data.get("total_words", 0)
        total_sentences = preprocessed_data.get("total_sentences", 0)
        full_text = preprocessed_data.get("full_text", "")

        # 1. Rule-Based Readability Analysis
        if progress_callback:
            progress_callback("Analyzing Readability & Lexical Metrics...", 20)
        logger.info("Running readability analysis...")
        readability_metrics = compute_readability_metrics(full_text, total_sentences, total_words)

        # 2. Rule-Based Sentence Length Analysis
        if progress_callback:
            progress_callback("Evaluating Sentence Length & Structure...", 35)
        logger.info("Running sentence length analysis...")
        sentence_analysis = analyze_sentence_lengths(sentences)

        # 3. Rule-Based Jargon & Legalese Detection
        if progress_callback:
            progress_callback("Scanning Government Jargon & Legalese Dictionary...", 50)
        logger.info("Running jargon detection...")
        jargon_analysis = detect_jargon_terms(sentences)

        # 4. Vocabulary Complexity & Passive Voice
        if progress_callback:
            progress_callback("Detecting Passive Voice & Polysyllabic Density...", 65)
        logger.info("Running complexity and passive voice detection...")
        vocab_analysis = analyze_vocabulary_complexity(sentences)
        passive_analysis = detect_passive_voice(sentences)

        # 5. Semantic AI Analysis (5W1H Instructions, Ambiguity, Missing Information, Citizen Summary, Tamil)
        if progress_callback:
            progress_callback("Executing Semantic Analysis & 5W1H Clarity Audit...", 80)
        logger.info("Running semantic AI analysis...")
        semantic_results = semantic_analyzer.analyze(preprocessed_data)

        # 6. Aggregate All Issues for Government Auditor Mode with Page Traceability
        if progress_callback:
            progress_callback("Aggregating Issues & Computing Composite Score...", 90)
        logger.info("Aggregating issues...")
        all_detected_issues: List[Dict[str, Any]] = []

        # Add Long Sentences
        all_detected_issues.extend(sentence_analysis.get("flagged_sentences", []))

        # Add Jargon Terms
        all_detected_issues.extend(jargon_analysis.get("detected_jargon", []))

        # Add Passive Voice
        all_detected_issues.extend(passive_analysis.get("passive_instances", []))

        # Add Unclear Instructions
        for inst in semantic_results.get("unclear_instructions", []):
            if isinstance(inst, dict):
                inst["category"] = "Instruction Clarity"
                all_detected_issues.append(inst)

        # Add Ambiguities
        for amb in semantic_results.get("ambiguities", []):
            if isinstance(amb, dict):
                amb["category"] = "Ambiguity"
                all_detected_issues.append(amb)

        # Count issues by severity
        severity_counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
        category_counts: Dict[str, int] = {}
        for issue in all_detected_issues:
            sev = issue.get("severity", "MEDIUM").upper()
            severity_counts[sev] = severity_counts.get(sev, 0) + 1
            cat = issue.get("category", "General")
            category_counts[cat] = category_counts.get(cat, 0) + 1

        # 7. Missing Information Completeness Summary
        missing_info_summary = summarize_missing_information(
            semantic_results.get("missing_information", [])
        )

        # 8. Calculate Composite Accessibility Score
        scoring_results = scorer.calculate_score(
            readability_metrics=readability_metrics,
            sentence_analysis=sentence_analysis,
            jargon_analysis=jargon_analysis,
            passive_analysis=passive_analysis,
            semantic_analysis=semantic_results
        )

        # 9. Prioritized Recommendations
        recommendations = generate_prioritized_recommendations(
            all_detected_issues=all_detected_issues,
            missing_info_data=missing_info_summary,
            readability_metrics=readability_metrics,
            semantic_recommendations=semantic_results.get("auditor_recommendations", [])
        )

        # 10. Assemble Rule Metrics
        rule_metrics = {
            "readability": readability_metrics,
            "sentence_stats": sentence_analysis,
            "jargon_stats": jargon_analysis,
            "vocab_stats": vocab_analysis,
            "passive_stats": passive_analysis,
            "severity_counts": severity_counts,
            "category_counts": category_counts,
            "total_issues_count": len(all_detected_issues)
        }

        # 11. Before vs After Sample
        before_after = semantic_results.get("before_after_sample", {})
        if not before_after:
            sample_long = sentence_analysis.get("flagged_sentences", [])
            before_text = sample_long[0]["original_text"] if sample_long else "The applicant shall furnish the requisite documents to the competent authority."
            before_after = {
                "before_text": before_text,
                "after_text": "Submit the required documents to the designated government office.",
                "before_words": len(before_text.split()),
                "after_words": 10,
                "before_jargon_count": 2,
                "after_jargon_count": 0,
                "clarity_improvement": "High"
            }

        if progress_callback:
            progress_callback("Analysis Complete! Loading Dashboard...", 100)

        record = AnalysisRecord(
            document_id=document_id,
            composite_score=scoring_results["composite_score"],
            score_tier=scoring_results["tier_label"],
            score_breakdown=scoring_results["breakdown"],
            rule_metrics=rule_metrics,
            detected_issues=all_detected_issues,
            missing_info=missing_info_summary,
            citizen_explanation=semantic_results.get("citizen_output", {}),
            recommendations=recommendations,
            before_after_comparison=before_after
        )

        logger.info(
            "Analysis complete for doc ID %d: Score = %.1f (%s), Total Issues = %d",
            document_id,
            record.composite_score,
            record.score_tier,
            len(all_detected_issues)
        )

        return record


# Global instance
accessibility_engine = AccessibilityEngine()
