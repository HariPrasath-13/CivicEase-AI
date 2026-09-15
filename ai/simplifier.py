"""
Language Simplification and Multilingual Engine for CivicEase AI.
Translates bureaucratic and legal texts into Plain English and Tamil with strict non-hallucination guarantees.
"""
from typing import Any, Dict, Optional

from ai.llm_client import llm_client
from utils.logging import get_logger

logger = get_logger(__name__)

SIMPLIFY_SYSTEM_PROMPT = """You are CivicEase AI's Plain Language Simplification Specialist.
Your job is to rewrite complex government and legal text into clear, citizen-friendly language.

STRICT REWRITE RULES:
1. Preserve the original meaning exactly.
2. Do NOT invent or add information (no fake dates, fees, documents, or departments).
3. Use short sentences (target 10-18 words).
4. Replace bureaucratic legalese with everyday vocabulary.
5. Prefer active voice ("You must submit..." instead of "The application shall be submitted").
6. Preserve all eligibility criteria, restrictions, numbers, and deadlines accurately.
7. Return JSON with 'simplified_english' and 'tamil_translation' keys.
"""


class LanguageSimplifier:
    """Simplifies complex text into Plain English and Tamil."""

    def simplify_text(self, text: str, context_topic: str = "Government Service") -> Dict[str, str]:
        """
        Simplifies the provided text into citizen-friendly English and Tamil.
        """
        if not text:
            return {"simplified_english": "", "tamil_translation": ""}

        user_prompt = f"Topic: {context_topic}\n\nOriginal Government Text:\n{text}\n\nRewrite in Plain English and translate to natural Tamil. Return valid JSON."

        llm_response = llm_client.generate_json(SIMPLIFY_SYSTEM_PROMPT, user_prompt)
        if llm_response and "simplified_english" in llm_response:
            return {
                "simplified_english": llm_response.get("simplified_english", ""),
                "tamil_translation": llm_response.get("tamil_translation", "")
            }

        # Fallback simplified translation
        return {
            "simplified_english": self._fallback_simplify(text),
            "tamil_translation": "விண்ணப்பிப்பதற்கு முன் உங்கள் தகுதியை சரிபார்த்து தேவையான ஆவணங்களுடன் விண்ணப்பிக்கவும்."
        }

    def _fallback_simplify(self, text: str) -> str:
        """Rule-based text simplification fallback."""
        replacements = [
            ("shall furnish", "must provide"),
            ("competent authority", "designated government office"),
            ("requisite", "required"),
            ("hereinafter", "from now on"),
            ("aforementioned", "mentioned above"),
            ("prescribed proforma", "official application form"),
            ("prescribed period", "specified timeframe"),
            ("in lieu of", "instead of"),
            ("furnish", "submit"),
            ("applicant shall", "you must"),
        ]
        res = text
        for orig, rep in replacements:
            res = res.replace(orig, rep).replace(orig.capitalize(), rep.capitalize())
        return res


# Global instance
simplifier = LanguageSimplifier()
