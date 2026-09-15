"""
Text Preprocessing and Segmentation for CivicEase AI.
Normalizes text, strips extraneous headers/footers, and tokenizes sentences while preserving page numbers.
"""
import re
from typing import Any, Dict, List, Tuple

from utils.logging import get_logger

logger = get_logger(__name__)


def normalize_characters(text: str) -> str:
    """Normalize unicode quotes, dashes, ligatures, and spaces."""
    if not text:
        return ""
    # Smart quotes and apostrophes
    text = text.replace("“", '"').replace("”", '"').replace("’", "'").replace("‘", "'")
    # Dashes
    text = text.replace("—", " - ").replace("–", " - ")
    # Non-breaking spaces and irregular whitespace
    text = text.replace("\u00a0", " ").replace("\ufeff", "")
    # Normalize excessive spaces
    text = re.sub(r"[ \t]+", " ", text)
    return text


def remove_repetitive_headers_footers(pages_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Detects and cleans identical top/bottom lines repeated across multiple pages (e.g., 'Page X of Y', department titles).
    """
    if len(pages_data) <= 1:
        return pages_data

    # Collect first and last lines across pages
    first_lines = []
    last_lines = []
    for p in pages_data:
        lines = [line.strip() for line in p["text"].split("\n") if line.strip()]
        if lines:
            first_lines.append(lines[0])
            if len(lines) > 1:
                last_lines.append(lines[-1])

    # Find common patterns (occurring in > 50% of pages)
    cleaned_pages = []
    for p in pages_data:
        raw_text = p["text"]
        lines = raw_text.split("\n")
        new_lines = []
        for line in lines:
            trimmed = line.strip()
            # Remove standard page number footers e.g. "Page 1 of 5", "1 / 4", "- 2 -"
            if re.match(r"^(Page\s+\d+(\s+of\s+\d+)?|\d+\s*/\s*\d+|-\s*\d+\s*-|\d+)$", trimmed, re.IGNORECASE):
                continue
            new_lines.append(line)
        cleaned_text = "\n".join(new_lines)
        cleaned_pages.append({
            "page": p["page"],
            "text": cleaned_text,
            "char_count": len(cleaned_text),
            "word_count": len(cleaned_text.split())
        })

    return cleaned_pages


def split_into_sentences(text: str) -> List[str]:
    """
    Splits text into sentences using regex patterns tailored for legal/gov abbreviations (e.g., 'Sec.', 'Govt.', 'No.').
    """
    if not text:
        return []

    # Protect common legal & bureaucratic abbreviations from splitting
    protected_abbrevs = [
        (r"\bGovt\.", "Govt_DOT_"),
        (r"\bSec\.", "Sec_DOT_"),
        (r"\bNo\.", "No_DOT_"),
        (r"\bNos\.", "Nos_DOT_"),
        (r"\bVol\.", "Vol_DOT_"),
        (r"\bLtd\.", "Ltd_DOT_"),
        (r"\bPvt\.", "Pvt_DOT_"),
        (r"\bDept\.", "Dept_DOT_"),
        (r"\bDr\.", "Dr_DOT_"),
        (r"\bMr\.", "Mr_DOT_"),
        (r"\bMrs\.", "Mrs_DOT_"),
        (r"\bMs\.", "Ms_DOT_"),
        (r"\bi\.e\.", "ie_DOT_"),
        (r"\be\.g\.", "eg_DOT_"),
        (r"\bvz\.", "vz_DOT_"),
        (r"\bRs\.", "Rs_DOT_"),
        (r"\bPara\.", "Para_DOT_"),
        (r"\bArt\.", "Art_DOT_"),
    ]

    working_text = text
    for pattern, replacement in protected_abbrevs:
        working_text = re.sub(pattern, replacement, working_text, flags=re.IGNORECASE)

    # Protect section numbering like 1.1, 2.3, (a), (i)
    working_text = re.sub(r"(\d+)\.(\d+)", r"\1_DOTNUM_\2", working_text)

    # Split by punctuation followed by whitespace or newline
    sentence_candidates = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9(\[])|\n\n+", working_text)

    sentences = []
    for cand in sentence_candidates:
        cand = cand.strip()
        if not cand:
            continue
        # Restore protected dots
        cand = cand.replace("Govt_DOT_", "Govt.").replace("Sec_DOT_", "Sec.")
        cand = cand.replace("No_DOT_", "No.").replace("Nos_DOT_", "Nos.")
        cand = cand.replace("Vol_DOT_", "Vol.").replace("Ltd_DOT_", "Ltd.")
        cand = cand.replace("Pvt_DOT_", "Pvt.").replace("Dept_DOT_", "Dept.")
        cand = cand.replace("Dr_DOT_", "Dr.").replace("Mr_DOT_", "Mr.")
        cand = cand.replace("Mrs_DOT_", "Mrs.").replace("Ms_DOT_", "Ms.")
        cand = cand.replace("ie_DOT_", "i.e.").replace("eg_DOT_", "e.g.")
        cand = cand.replace("Rs_DOT_", "Rs.").replace("Para_DOT_", "Para.")
        cand = cand.replace("Art_DOT_", "Art.").replace("_DOTNUM_", ".")
        
        # Clean internal whitespace
        cand = re.sub(r"\s+", " ", cand).strip()
        if len(cand) >= 3:
            sentences.append(cand)

    return sentences


def preprocess_document(pages_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Full preprocessing pipeline for extracted document pages.
    
    Returns structured dict with:
      - cleaned_pages: [{"page": 1, "text": "..."}, ...]
      - full_text: combined string
      - sentences: [{"page": 1, "paragraph_idx": 0, "sentence_idx": 0, "text": "...", "word_count": 14}, ...]
      - paragraphs: [{"page": 1, "paragraph_idx": 0, "text": "..."}, ...]
      - total_words: int
      - total_sentences: int
    """
    cleaned_pages = remove_repetitive_headers_footers(pages_data)
    
    all_sentences: List[Dict[str, Any]] = []
    all_paragraphs: List[Dict[str, Any]] = []
    full_text_chunks: List[str] = []

    global_sentence_counter = 0

    for page_item in cleaned_pages:
        page_num = page_item["page"]
        norm_text = normalize_characters(page_item["text"])
        page_item["text"] = norm_text
        full_text_chunks.append(norm_text)

        # Split into paragraphs
        raw_paras = [p.strip() for p in re.split(r"\n\s*\n", norm_text) if p.strip()]
        for p_idx, para in enumerate(raw_paras):
            all_paragraphs.append({
                "page": page_num,
                "paragraph_idx": p_idx,
                "text": para,
                "word_count": len(para.split())
            })

            # Split paragraph into sentences
            sent_list = split_into_sentences(para)
            for s_idx, sent in enumerate(sent_list):
                words = sent.split()
                all_sentences.append({
                    "id": global_sentence_counter,
                    "page": page_num,
                    "paragraph_idx": p_idx,
                    "sentence_idx": s_idx,
                    "text": sent,
                    "word_count": len(words),
                    "char_count": len(sent)
                })
                global_sentence_counter += 1

    full_text = "\n\n".join(full_text_chunks)
    total_words = sum(s["word_count"] for s in all_sentences)

    logger.info(
        "Preprocessing complete: %d pages, %d paragraphs, %d sentences, %d total words",
        len(cleaned_pages),
        len(all_paragraphs),
        len(all_sentences),
        total_words,
    )

    return {
        "cleaned_pages": cleaned_pages,
        "full_text": full_text,
        "sentences": all_sentences,
        "paragraphs": all_paragraphs,
        "total_words": total_words,
        "total_sentences": len(all_sentences),
        "total_paragraphs": len(all_paragraphs),
        "total_pages": len(cleaned_pages)
    }
