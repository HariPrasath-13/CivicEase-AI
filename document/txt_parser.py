"""
TXT Document Parser with multi-encoding support.
"""
from pathlib import Path
from typing import Any, Dict, List, Tuple

from utils.logging import get_logger

logger = get_logger(__name__)


def extract_text_from_txt(file_path: str) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Extracts text from plain text files with encoding fallbacks.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"TXT file not found at: {file_path}")

    encodings_to_try = ["utf-8", "utf-8-sig", "latin-1", "cp1252"]
    raw_content = ""
    used_encoding = ""

    for enc in encodings_to_try:
        try:
            with open(file_path, "r", encoding=enc) as f:
                raw_content = f.read()
                used_encoding = enc
                break
        except UnicodeDecodeError:
            continue

    if not used_encoding:
        raise ValueError("Could not decode text file using supported encodings.")

    raw_content = raw_content.strip()
    words = raw_content.split()
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
        "total_char_count": len(raw_content),
        "title": path.stem,
        "author": "",
        "encoding": used_encoding
    }

    logger.info("Successfully extracted text from TXT using encoding %s", used_encoding)
    return pages_data, metadata
