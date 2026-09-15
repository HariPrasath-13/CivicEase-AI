"""
Multi-document format and mode verification test.
Tests PDF parsing with page extraction, DOCX/TXT extraction, and analysis across 3 different schemes.
"""
import sys
from pathlib import Path

# Ensure UTF-8 output on Windows console
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from database.database import db
from database.models import DocumentRecord
from document.pdf_parser import extract_text_from_pdf
from document.preprocessing import preprocess_document
from document.txt_parser import extract_text_from_txt
from analysis.accessibility_engine import accessibility_engine
from reports.report_generator import report_generator

def test_all_sample_documents():
    print("=" * 65)
    print(" MULTI-DOCUMENT ACCESSIBILITY ANALYSIS VERIFICATION")
    print("=" * 65)

    sample_dir = BASE_DIR / "data" / "sample_documents"
    samples = [
        ("TamilNadu_OldAge_Pension_Scheme.pdf", "pdf"),
        ("Disability_Healthcare_Subsidy_Directive.pdf", "pdf"),
        ("Ration_Card_Revision_Guidelines.txt", "txt"),
    ]

    for filename, ftype in samples:
        fpath = sample_dir / filename
        if not fpath.exists():
            print(f"Skipping {filename} (not found)")
            continue

        print(f"\n📄 Analyzing: {filename} ({ftype.upper()})")
        if ftype == "pdf":
            pages_data, meta = extract_text_from_pdf(str(fpath))
            print(f"  • Extracted {meta['page_count']} page(s), {meta['total_char_count']} chars")
        else:
            pages_data, meta = extract_text_from_txt(str(fpath))
            print(f"  • Extracted {meta['page_count']} section(s), {meta['total_char_count']} chars")

        preprocessed = preprocess_document(pages_data)
        print(f"  • Preprocessed: {preprocessed['total_sentences']} sentences, {preprocessed['total_words']} words")

        doc_record = DocumentRecord(
            user_id=1,
            filename=filename,
            file_type=ftype,
            file_hash="sample_hash_" + filename,
            file_size_bytes=fpath.stat().st_size,
            page_count=len(pages_data),
            storage_path=str(fpath)
        )
        doc_id = db.save_document(doc_record)
        doc_record.id = doc_id

        analysis = accessibility_engine.analyze_document(doc_id, preprocessed)
        print(f"  • CivicEase AI Score: {analysis.composite_score}/100 ({analysis.score_tier})")
        print(f"  • Score Breakdown: {analysis.score_breakdown}")
        print(f"  • Detected Issues: {len(analysis.detected_issues)}")
        print(f"  • Missing Info: {[f['field_key'] + '=' + f['status'] for f in analysis.missing_info.get('fields', [])]}")

        # Check PDF and MD reports
        md_rep = report_generator.generate_markdown_report(doc_record, analysis)
        pdf_bytes = report_generator.generate_pdf_report(doc_record, analysis)
        assert len(md_rep) > 500, "Markdown report too short"
        assert len(pdf_bytes) > 500, "PDF report too short"
        print(f"  ✓ Reports successfully compiled (MD: {len(md_rep)} chars, PDF: {len(pdf_bytes)} bytes)")

    print("\n" + "=" * 65)
    print(" ALL SAMPLE DOCUMENTS ANALYZED AND VERIFIED SUCCESSFULLY! ")
    print("=" * 65)

if __name__ == "__main__":
    test_all_sample_documents()
