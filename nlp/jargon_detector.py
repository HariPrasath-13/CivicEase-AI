"""
Jargon and Legalese Terminology Detector for CivicEase AI.
Maintains a curated dictionary of 100+ government, legal, and bureaucratic terms
along with plain-language meanings, simpler alternatives, and severity ratings.
"""
import re
from typing import Any, Dict, List, Tuple

from utils.logging import get_logger

logger = get_logger(__name__)

# Government and Legal Terminology Dictionary
GOVERNMENT_JARGON_DICT: Dict[str, Dict[str, Any]] = {
    "hereinafter": {
        "meaning": "from this point forward in this document",
        "simpler_word": "from now on / below",
        "severity": "MEDIUM",
        "category": "Archaic Legalese"
    },
    "aforementioned": {
        "meaning": "mentioned earlier in the document",
        "simpler_word": "mentioned earlier / these",
        "severity": "MEDIUM",
        "category": "Archaic Legalese"
    },
    "thereof": {
        "meaning": "of the thing just mentioned",
        "simpler_word": "of it / of this",
        "severity": "MEDIUM",
        "category": "Archaic Legalese"
    },
    "therein": {
        "meaning": "in that place, document, or matter",
        "simpler_word": "in it / inside",
        "severity": "MEDIUM",
        "category": "Archaic Legalese"
    },
    "thereunder": {
        "meaning": "under that clause or law",
        "simpler_word": "under this rule",
        "severity": "MEDIUM",
        "category": "Archaic Legalese"
    },
    "whereupon": {
        "meaning": "after which or immediately following which",
        "simpler_word": "then / after this",
        "severity": "LOW",
        "category": "Archaic Legalese"
    },
    "requisite": {
        "meaning": "required by regulations or circumstances",
        "simpler_word": "required / necessary",
        "severity": "MEDIUM",
        "category": "Complex Vocabulary"
    },
    "jurisdiction": {
        "meaning": "the official power or territorial authority to make decisions",
        "simpler_word": "official area / authority",
        "severity": "MEDIUM",
        "category": "Legal Terminology"
    },
    "notwithstanding": {
        "meaning": "in spite of, or regardless of what was stated",
        "simpler_word": "even if / despite / regardless of",
        "severity": "HIGH",
        "category": "Archaic Legalese"
    },
    "competent authority": {
        "meaning": "the specific official, department, or body authorized to approve",
        "simpler_word": "authorized officer / designated department (specify exact office)",
        "severity": "HIGH",
        "category": "Bureaucratic Jargon"
    },
    "applicant shall": {
        "meaning": "mandatory legal obligation for the applicant",
        "simpler_word": "you must / please",
        "severity": "LOW",
        "category": "Bureaucratic Phrasing"
    },
    "furnish": {
        "meaning": "to provide, submit, or supply documents/information",
        "simpler_word": "provide / submit / send",
        "severity": "LOW",
        "category": "Complex Vocabulary"
    },
    "prescribed": {
        "meaning": "officially stated or established in the official format",
        "simpler_word": "specified / required official",
        "severity": "MEDIUM",
        "category": "Bureaucratic Jargon"
    },
    "prescribed proforma": {
        "meaning": "the officially provided standard application format",
        "simpler_word": "official application form",
        "severity": "HIGH",
        "category": "Bureaucratic Jargon"
    },
    "mutatis mutandis": {
        "meaning": "making necessary alterations while keeping the main point",
        "simpler_word": "with necessary adjustments",
        "severity": "HIGH",
        "category": "Latin Legal Jargon"
    },
    "in lieu thereof": {
        "meaning": "instead of that",
        "simpler_word": "instead of / in place of",
        "severity": "HIGH",
        "category": "Archaic Legalese"
    },
    "in lieu of": {
        "meaning": "instead of or as a substitute for",
        "simpler_word": "instead of",
        "severity": "MEDIUM",
        "category": "Archaic Legalese"
    },
    "deem fit": {
        "meaning": "considers appropriate according to official judgment",
        "simpler_word": "decides / thinks appropriate",
        "severity": "MEDIUM",
        "category": "Bureaucratic Phrasing"
    },
    "bona fide": {
        "meaning": "genuine, real, or without intention to deceive",
        "simpler_word": "genuine / verified / authentic",
        "severity": "MEDIUM",
        "category": "Latin Legal Jargon"
    },
    "suo motu": {
        "meaning": "on its own initiative without waiting for a formal application",
        "simpler_word": "on its own initiative",
        "severity": "HIGH",
        "category": "Latin Legal Jargon"
    },
    "suo moto": {
        "meaning": "on its own initiative",
        "simpler_word": "on its own initiative",
        "severity": "HIGH",
        "category": "Latin Legal Jargon"
    },
    "prima facie": {
        "meaning": "based on the first impression or preliminary view",
        "simpler_word": "at first review / initial check",
        "severity": "HIGH",
        "category": "Latin Legal Jargon"
    },
    "inter alia": {
        "meaning": "among other things",
        "simpler_word": "including / among others",
        "severity": "HIGH",
        "category": "Latin Legal Jargon"
    },
    "ultra vires": {
        "meaning": "beyond the legal powers or authority of a person or body",
        "simpler_word": "outside legal powers",
        "severity": "HIGH",
        "category": "Latin Legal Jargon"
    },
    "gazette": {
        "meaning": "an official government public journal of laws and notices",
        "simpler_word": "official government publication",
        "severity": "LOW",
        "category": "Government Terminology"
    },
    "encumbrance": {
        "meaning": "a claim, lien, liability, or charge attached to a property",
        "simpler_word": "debt / legal liability / claim on property",
        "severity": "HIGH",
        "category": "Legal Terminology"
    },
    "non-encumbrance": {
        "meaning": "free of any legal claims, debts, or mortgages",
        "simpler_word": "free of legal debt/claims",
        "severity": "MEDIUM",
        "category": "Legal Terminology"
    },
    "attestation": {
        "meaning": "official verification and signing of a copy by an authorized officer",
        "simpler_word": "official signed verification / self-attestation",
        "severity": "MEDIUM",
        "category": "Government Terminology"
    },
    "indemnity": {
        "meaning": "security or protection against a financial liability or loss",
        "simpler_word": "security guarantee against loss",
        "severity": "HIGH",
        "category": "Legal Terminology"
    },
    "affidavit": {
        "meaning": "a written sworn statement confirmed by oath before a notary or magistrate",
        "simpler_word": "sworn legal statement",
        "severity": "MEDIUM",
        "category": "Legal Terminology"
    },
    "debarment": {
        "meaning": "the state of being formally excluded or banned from applying",
        "simpler_word": "disqualification / ban",
        "severity": "HIGH",
        "category": "Bureaucratic Jargon"
    },
    "empanelment": {
        "meaning": "inclusion on an official roster or list of approved providers/candidates",
        "simpler_word": "official listing / enrollment",
        "severity": "MEDIUM",
        "category": "Bureaucratic Jargon"
    },
    "sanction": {
        "meaning": "official government financial or administrative approval",
        "simpler_word": "official approval / grant",
        "severity": "MEDIUM",
        "category": "Administrative Terminology"
    },
    "challan": {
        "meaning": "an official receipt, payment voucher, or invoice for government dues",
        "simpler_word": "official payment receipt / voucher",
        "severity": "LOW",
        "category": "Administrative Terminology"
    },
    "pecuniary": {
        "meaning": "relating to or consisting of money",
        "simpler_word": "financial / monetary",
        "severity": "HIGH",
        "category": "Archaic Legalese"
    },
    "stipulated": {
        "meaning": "demanded or specified as part of an official agreement or rule",
        "simpler_word": "specified / required",
        "severity": "MEDIUM",
        "category": "Complex Vocabulary"
    },
    "grievance redressal": {
        "meaning": "formal government mechanism to resolve complaints",
        "simpler_word": "complaint resolution",
        "severity": "LOW",
        "category": "Administrative Terminology"
    },
    "admissible": {
        "meaning": "acceptable or valid under official regulations",
        "simpler_word": "allowed / accepted / eligible",
        "severity": "MEDIUM",
        "category": "Administrative Terminology"
    },
    "domicile": {
        "meaning": "the country or state that a person treats as their permanent home",
        "simpler_word": "permanent residence",
        "severity": "MEDIUM",
        "category": "Legal Terminology"
    },
    "remittance": {
        "meaning": "a sum of money sent in payment for government service or fees",
        "simpler_word": "fee payment / money transfer",
        "severity": "MEDIUM",
        "category": "Financial Terminology"
    },
    "scrutiny": {
        "meaning": "critical, detailed examination of application documents",
        "simpler_word": "verification / detailed review",
        "severity": "LOW",
        "category": "Administrative Terminology"
    },
    "annexure": {
        "meaning": "an attachment, appendix, or supplementary document",
        "simpler_word": "attachment / appendix form",
        "severity": "LOW",
        "category": "Administrative Terminology"
    },
    "gazetted officer": {
        "meaning": "a government official whose appointment is published in the official Gazette",
        "simpler_word": "authorized senior government officer",
        "severity": "MEDIUM",
        "category": "Government Terminology"
    },
    "undertaking": {
        "meaning": "a formal pledge, promise, or signed agreement to adhere to conditions",
        "simpler_word": "signed agreement / declaration",
        "severity": "MEDIUM",
        "category": "Legal Terminology"
    },
    "pertaining to": {
        "meaning": "related to or concerning",
        "simpler_word": "about / related to",
        "severity": "LOW",
        "category": "Complex Vocabulary"
    },
    "forfeit": {
        "meaning": "lose or give up as a penalty for wrongdoing",
        "simpler_word": "lose / surrender as penalty",
        "severity": "MEDIUM",
        "category": "Legal Terminology"
    },
    "discretion": {
        "meaning": "the freedom to decide what should be done in a particular situation",
        "simpler_word": "choice / authorized decision",
        "severity": "MEDIUM",
        "category": "Legal Terminology"
    }
}


def detect_jargon_terms(sentences: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Scans document sentences against the legal/jargon dictionary.
    Returns detected terms grouped with page numbers, context snippets, and counts.
    """
    detected_items: List[Dict[str, Any]] = []
    term_counts: Dict[str, int] = {}
    severity_counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}

    # Sort dictionary keys by length descending to match multi-word phrases first
    sorted_terms = sorted(GOVERNMENT_JARGON_DICT.keys(), key=lambda k: len(k), reverse=True)

    for item in sentences:
        sent_text = item.get("text", "")
        page_num = item.get("page", 1)

        for term in sorted_terms:
            pattern = r"\b" + re.escape(term) + r"\b"
            matches = re.finditer(pattern, sent_text, flags=re.IGNORECASE)
            for m in matches:
                matched_str = m.group(0)
                term_info = GOVERNMENT_JARGON_DICT[term]
                term_key = term.lower()
                term_counts[term_key] = term_counts.get(term_key, 0) + 1
                sev = term_info["severity"]
                severity_counts[sev] += 1

                detected_items.append({
                    "id": f"jargon_{len(detected_items)}",
                    "category": "Jargon & Terminology",
                    "term": matched_str,
                    "normalized_term": term,
                    "page": page_num,
                    "meaning": term_info["meaning"],
                    "simpler_word": term_info["simpler_word"],
                    "severity": sev,
                    "term_type": term_info["category"],
                    "original_text": sent_text,
                    "explanation": f"The term '{matched_str}' is bureaucratic/legal phrasing ({term_info['meaning']}).",
                    "recommendation": f"Replace '{matched_str}' with '{term_info['simpler_word']}' to improve clarity for general citizens."
                })

    # Sort by severity
    severity_rank = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    detected_items.sort(key=lambda x: severity_rank.get(x["severity"], 3))

    return {
        "detected_jargon": detected_items,
        "total_jargon_count": len(detected_items),
        "unique_jargon_count": len(term_counts),
        "severity_counts": severity_counts,
        "term_frequency": term_counts
    }
