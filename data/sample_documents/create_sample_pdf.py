"""
Generates PDF versions of the sample government documents for testing PDF upload.
"""
from pathlib import Path

SAMPLE_DIR = Path(__file__).parent

def create_sample_pdfs():
    try:
        import fitz  # PyMuPDF
        print("Using PyMuPDF to generate sample PDFs...")
        
        # 1. Pension Scheme PDF
        txt_path = SAMPLE_DIR / "TamilNadu_OldAge_Pension_Scheme.txt"
        if txt_path.exists():
            with open(txt_path, "r", encoding="utf-8") as f:
                content = f.read()
            doc = fitz.open()
            # Split into 2 pages for realistic multi-page testing
            parts = content.split("4. APPLICATION PROCEDURE & SUBMISSION:")
            p1_text = parts[0].strip()
            p2_text = "4. APPLICATION PROCEDURE & SUBMISSION:\n" + (parts[1].strip() if len(parts) > 1 else "")
            
            p1 = doc.new_page(width=595, height=842)
            p1.insert_textbox(fitz.Rect(50, 50, 545, 792), p1_text, fontsize=11)
            
            p2 = doc.new_page(width=595, height=842)
            p2.insert_textbox(fitz.Rect(50, 50, 545, 792), p2_text, fontsize=11)
            
            pdf_path = SAMPLE_DIR / "TamilNadu_OldAge_Pension_Scheme.pdf"
            doc.save(str(pdf_path))
            doc.close()
            print(f"Created {pdf_path}")

        # 2. Healthcare Directive PDF
        hc_path = SAMPLE_DIR / "Disability_Healthcare_Subsidy_Directive.txt"
        if hc_path.exists():
            with open(hc_path, "r", encoding="utf-8") as f:
                hc_content = f.read()
            doc2 = fitz.open()
            p = doc2.new_page(width=595, height=842)
            p.insert_textbox(fitz.Rect(50, 50, 545, 792), hc_content, fontsize=11)
            hc_pdf = SAMPLE_DIR / "Disability_Healthcare_Subsidy_Directive.pdf"
            doc2.save(str(hc_pdf))
            doc2.close()
            print(f"Created {hc_pdf}")

    except ImportError:
        print("PyMuPDF not yet installed; sample txt files are ready.")

if __name__ == "__main__":
    create_sample_pdfs()
