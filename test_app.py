"""
Comprehensive Test Suite for CivicEase AI.
Validates database, document parsers, rule-based NLP, semantic analysis, scoring, and report generation.
"""
import os
import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Ensure UTF-8 output on Windows console
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from database.database import db
from database.models import DocumentRecord, UserRecord
from document.preprocessing import preprocess_document
from document.txt_parser import extract_text_from_txt
from nlp.jargon_detector import detect_jargon_terms
from nlp.passive_voice import detect_passive_voice
from nlp.readability import compute_readability_metrics
from nlp.sentence_analysis import analyze_sentence_lengths
from analysis.accessibility_engine import accessibility_engine
from analysis.missing_information import summarize_missing_information
from analysis.recommendations import generate_prioritized_recommendations
from analysis.scoring import scorer
from reports.report_generator import report_generator


def run_all_tests():
    print("=" * 60)
    print(" CivicEase AI — End-to-End Backend & Analysis Verification")
    print("=" * 60)

    # 1. Test Database & Demo Users
    print("\n[1/7] Testing SQLite Database & User Authentication...")
    user = db.authenticate_user("citizen", "citizen123")
    assert user is not None, "Failed to authenticate default citizen user"
    assert user.role == "citizen", f"Expected citizen role, got {user.role}"

    auditor = db.authenticate_user("auditor", "auditor123")
    assert auditor is not None, "Failed to authenticate default auditor user"
    assert auditor.role == "auditor", f"Expected auditor role, got {auditor.role}"
    print(f"  ✓ Default accounts verified: Citizen ({user.full_name}), Auditor ({auditor.full_name})")

    # 2. Test Document Extraction
    print("\n[2/7] Testing Document Extraction & Preprocessing...")
    sample_path = BASE_DIR / "data" / "sample_documents" / "TamilNadu_OldAge_Pension_Scheme.txt"
    assert sample_path.exists(), f"Sample document not found at {sample_path}"

    pages_data, meta = extract_text_from_txt(str(sample_path))
    assert len(pages_data) > 0, "Failed to extract pages from sample text"
    assert meta["total_char_count"] > 100, "Extracted text is too short"

    preprocessed = preprocess_document(pages_data)
    assert len(preprocessed["sentences"]) > 0, "Failed to tokenize sentences"
    assert preprocessed["total_words"] > 50, "Word count is too low"
    print(f"  ✓ Preprocessing complete: {preprocessed['total_sentences']} sentences, {preprocessed['total_words']} words across {preprocessed['total_pages']} page(s).")

    # 3. Test Rule-Based NLP Pipeline
    print("\n[3/7] Testing Rule-Based NLP Analysis...")
    readability = compute_readability_metrics(
        preprocessed["full_text"],
        preprocessed["total_sentences"],
        preprocessed["total_words"]
    )
    assert "flesch_reading_ease" in readability, "Missing Flesch score"
    print(f"  ✓ Readability: Flesch Ease = {readability['flesch_reading_ease']} ({readability['interpretation']}), Avg Sent Len = {readability['avg_sentence_length']} words")

    sentence_analysis = analyze_sentence_lengths(preprocessed["sentences"])
    assert "flagged_sentences" in sentence_analysis, "Missing sentence length analysis"
    print(f"  ✓ Sentence Lengths: Flagged {sentence_analysis['total_flagged']} long sentences (High: {sentence_analysis['high_severity_count']}, Warning: {sentence_analysis['warning_severity_count']})")

    jargon_analysis = detect_jargon_terms(preprocessed["sentences"])
    assert jargon_analysis["total_jargon_count"] > 0, "Failed to detect known legal terms"
    print(f"  ✓ Jargon Detection: Found {jargon_analysis['total_jargon_count']} jargon occurrences across {jargon_analysis['unique_jargon_count']} unique terms")

    passive_analysis = detect_passive_voice(preprocessed["sentences"])
    print(f"  ✓ Passive Voice: Detected {passive_analysis['total_passive_count']} instances ({passive_analysis['passive_percentage']}%)")

    # 4. Test Master Accessibility Engine & Composite Scoring
    print("\n[4/7] Testing Master Accessibility Engine & Composite Scoring...")
    doc_record = DocumentRecord(
        user_id=user.id,
        filename=sample_path.name,
        file_type="txt",
        file_hash="test_hash_12345",
        file_size_bytes=sample_path.stat().st_size,
        page_count=len(pages_data),
        storage_path=str(sample_path)
    )
    doc_id = db.save_document(doc_record)
    doc_record.id = doc_id

    analysis = accessibility_engine.analyze_document(doc_id, preprocessed)
    assert analysis.composite_score >= 0.0 and analysis.composite_score <= 100.0, f"Invalid score: {analysis.composite_score}"
    assert len(analysis.detected_issues) > 0, "No issues detected"
    print(f"  ✓ CivicEase AI Composite Accessibility Score: {analysis.composite_score} / 100 ({analysis.score_tier})")
    print(f"    - Score Breakdown: {analysis.score_breakdown}")
    print(f"    - Total Detected Issues: {len(analysis.detected_issues)}")

    # 5. Test 7 Core Public Service Missing Information Fields
    print("\n[5/7] Testing 7-Field Information Completeness Matrix...")
    missing_fields = analysis.missing_info.get("fields", [])
    assert len(missing_fields) == 7, f"Expected 7 service fields, got {len(missing_fields)}"
    for f in missing_fields:
        print(f"    • {f['badge_icon']} {f['display_name']}: {f['status']} — {f['details'][:60]}...")

    # 6. Test Citizen Output & Tamil Translation
    print("\n[6/7] Testing Citizen Explanation & Tamil Translation...")
    citizen_out = analysis.citizen_explanation
    assert "how_to_apply_steps" in citizen_out and len(citizen_out["how_to_apply_steps"]) > 0, "Missing citizen steps"
    assert "documents_checklist" in citizen_out and len(citizen_out["documents_checklist"]) > 0, "Missing checklist"
    assert "tamil_translation" in citizen_out and len(citizen_out["tamil_translation"]) > 0, "Missing Tamil translation"
    print(f"  ✓ Citizen Summary: {citizen_out.get('service_name', 'Service')}")
    print(f"  ✓ Generated {len(citizen_out['how_to_apply_steps'])} Step-by-Step Instructions")
    print(f"  ✓ Generated {len(citizen_out['documents_checklist'])} Required Documents Checklist")
    print(f"  ✓ Tamil Translation Preview: {citizen_out['tamil_translation'][:90]}...")

    # 7. Test Report Generation (Markdown & PDF)
    print("\n[7/7] Testing Report Generation & Export...")
    md_report = report_generator.generate_markdown_report(doc_record, analysis)
    assert "# CivicEase AI" in md_report, "Markdown report header missing"
    assert "Composite Accessibility Score" in md_report, "Score missing from MD report"

    pdf_bytes = report_generator.generate_pdf_report(doc_record, analysis)
    assert len(pdf_bytes) > 100, "PDF generation produced empty output"
    print(f"  ✓ Markdown report generated ({len(md_report)} chars)")
    print(f"  ✓ PDF report compiled ({len(pdf_bytes)} bytes)")

    print("\n" + "=" * 60)
    print(" ALL 7 TEST PHASES PASSED WITH 100% SUCCESS! ")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()
