"""
PDF Document Parser using PyMuPDF (fitz).
Extracts text page-by-page to guarantee page-level issue traceability.
"""
from pathlib import Path
from typing import Any, Dict, List, Tuple
import fitz  # PyMuPDF

from utils.logging import get_logger

logger = get_logger(__name__)


def extract_text_from_pdf(file_path: str) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Extracts text page-by-page from a PDF file.

    Returns:
        Tuple of (pages_data, metadata)
        where pages_data is a list of dicts: [{"page": 1, "text": "..."}, ...]
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF file not found at: {file_path}")

    pages_data: List[Dict[str, Any]] = []
    metadata: Dict[str, Any] = {
        "page_count": 0,
        "is_scanned": False,
        "total_char_count": 0,
        "title": "",
        "author": "",
    }

    try:
        doc = fitz.open(file_path)
        metadata["page_count"] = len(doc)
        metadata["title"] = doc.metadata.get("title", "") or path.stem
        metadata["author"] = doc.metadata.get("author", "")

        total_text_length = 0
        for page_idx in range(len(doc)):
            page = doc[page_idx]
            text = page.get_text("text")
            page_num = page_idx + 1

            cleaned_page_text = text.strip()
            total_text_length += len(cleaned_page_text)

            pages_data.append({
                "page": page_num,
                "text": cleaned_page_text,
                "char_count": len(cleaned_page_text),
                "word_count": len(cleaned_page_text.split())
            })

        metadata["total_char_count"] = total_text_length
        doc.close()

        # Heuristic for scanned/image-only PDFs
        if metadata["page_count"] > 0 and (total_text_length / metadata["page_count"]) < 30:
            metadata["is_scanned"] = True
            logger.warning("PDF appears to be scanned or contains very sparse text: %s", file_path)

        logger.info("Successfully extracted %d pages from PDF (%d chars)", len(pages_data), total_text_length)
        return pages_data, metadata

    except Exception as e:
        logger.error("Failed to parse PDF document %s: %s", file_path, str(e))
        raise RuntimeError(f"Could not read PDF: {str(e)}")
