"""
DOCX Document Parser using python-docx.
Extracts paragraphs, headings, and structure.
"""
from pathlib import Path
from typing import Any, Dict, List, Tuple
import docx

from utils.logging import get_logger

logger = get_logger(__name__)


def extract_text_from_docx(file_path: str) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Extracts structured text from a DOCX file.
    Maps paragraphs into logical page sections (~500 words per page representation).
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"DOCX file not found at: {file_path}")

    try:
        doc = docx.Document(file_path)
        paragraphs_text = []

        for p in doc.paragraphs:
            text = p.text.strip()
            if text:
                paragraphs_text.append(text)

        # Also extract table text
        for table in doc.tables:
            for row in table.rows:
                row_cells = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                if row_cells:
                    paragraphs_text.append(" | ".join(row_cells))

        full_text = "\n\n".join(paragraphs_text)
        words = full_text.split()
        
        # Approximate pages based on word chunks (~350 words per page)
        words_per_page = 350
        pages_data = []
        
        if not words:
            pages_data.append({"page": 1, "text": "", "char_count": 0, "word_count": 0})
        else:
            total_words = len(words)
            total_pages = max(1, (total_words + words_per_page - 1) // words_per_page)
            for p in range(total_pages):
                chunk_words = words[p * words_per_page : (p + 1) * words_per_page]
                chunk_text = " ".join(chunk_words)
                pages_data.append({
                    "page": p + 1,
                    "text": chunk_text,
                    "char_count": len(chunk_text),
                    "word_count": len(chunk_words)
                })

        metadata = {
            "page_count": len(pages_data),
            "is_scanned": False,
            "total_char_count": len(full_text),
            "title": path.stem,
            "author": doc.core_properties.author or "",
        }

        logger.info("Successfully extracted %d paragraphs from DOCX: %s", len(paragraphs_text), file_path)
        return pages_data, metadata

    except Exception as e:
        logger.error("Failed to parse DOCX document %s: %s", file_path, str(e))
        raise RuntimeError(f"Could not read DOCX: {str(e)}")
