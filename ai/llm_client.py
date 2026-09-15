"""
Unified LLM Client for CivicEase AI.
Supports Gemini, OpenAI, Groq, Ollama, and an advanced deterministic heuristic fallback engine.
"""
import json
import re
from typing import Any, Dict, List, Optional
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    import urllib.request
    import urllib.error

from config.settings import (
    GEMINI_API_KEY,
    LLM_MODEL,
    LLM_PROVIDER,
    OLLAMA_BASE_URL,
    OPENAI_API_KEY,
    OPENAI_BASE_URL,
)
from utils.logging import get_logger

logger = get_logger(__name__)


class LLMClient:
    """Dispatches semantic analysis requests across configured LLM providers with automatic fallback."""

    def __init__(self):
        self.provider = LLM_PROVIDER
        self.gemini_key = GEMINI_API_KEY
        self.openai_key = OPENAI_API_KEY
        self.openai_base_url = OPENAI_BASE_URL
        self.ollama_base_url = OLLAMA_BASE_URL
        self.model = LLM_MODEL

    def is_api_configured(self) -> bool:
        """Check whether at least one real LLM API backend is configured."""
        if self.gemini_key:
            return True
        if self.openai_key:
            return True
        return False

    def generate_json(self, system_prompt: str, user_prompt: str) -> Optional[Dict[str, Any]]:
        """
        Invokes LLM with JSON format instructions and parses the response.
        Falls back through available providers, and finally to deterministic heuristics if unavailable.
        """
        # Try Gemini if key is set
        if self.gemini_key:
            try:
                result = self._call_gemini_rest(system_prompt, user_prompt)
                if result:
                    return result
            except Exception as e:
                logger.warning("Gemini API call failed: %s. Trying fallback.", str(e))

        # Try OpenAI / Groq if key is set
        if self.openai_key:
            try:
                result = self._call_openai_rest(system_prompt, user_prompt)
                if result:
                    return result
            except Exception as e:
                logger.warning("OpenAI API call failed: %s. Trying fallback.", str(e))

        # Try Ollama if running
        try:
            result = self._call_ollama_rest(system_prompt, user_prompt)
            if result:
                return result
        except Exception:
            pass

        logger.info("No active LLM API response; using deterministic heuristic engine for semantic analysis.")
        return None

    def _call_gemini_rest(self, system_prompt: str, user_prompt: str) -> Optional[Dict[str, Any]]:
        """Call Gemini via Google Generative Language REST API."""
        models_to_try = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash"]
        for model_name in models_to_try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={self.gemini_key}"
            payload = {
                "contents": [
                    {
                        "role": "user",
                        "parts": [
                            {"text": f"{system_prompt}\n\n{user_prompt}\n\nIMPORTANT: Respond ONLY with valid JSON."}
                        ]
                    }
                ],
                "generationConfig": {
                    "responseMimeType": "application/json",
                    "temperature": 0.2
                }
            }
            resp = requests.post(url, json=payload, timeout=45)
            if resp.status_code == 200:
                data = resp.json()
                candidate_text = data["candidates"][0]["content"]["parts"][0]["text"]
                return self._parse_json_safely(candidate_text)
            else:
                logger.warning("Gemini %s returned status %d: %s", model_name, resp.status_code, resp.text[:200])
        return None

    def _call_openai_rest(self, system_prompt: str, user_prompt: str) -> Optional[Dict[str, Any]]:
        """Call OpenAI or compatible endpoint (Groq, OpenRouter, LocalAI)."""
        url = f"{self.openai_base_url.rstrip('/')}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.openai_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model if self.model else "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.2,
            "response_format": {"type": "json_object"}
        }
        resp = requests.post(url, headers=headers, json=payload, timeout=45)
        if resp.status_code == 200:
            data = resp.json()
            content = data["choices"][0]["message"]["content"]
            return self._parse_json_safely(content)
        return None

    def _call_ollama_rest(self, system_prompt: str, user_prompt: str) -> Optional[Dict[str, Any]]:
        """Call local Ollama instance if accessible."""
        url = f"{self.ollama_base_url.rstrip('/')}/api/generate"
        payload = {
            "model": "llama3.2" if "gemini" in self.model else self.model,
            "prompt": f"{system_prompt}\n\n{user_prompt}\n\nRespond in JSON only.",
            "format": "json",
            "stream": False,
            "options": {"temperature": 0.2}
        }
        resp = requests.post(url, json=payload, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            return self._parse_json_safely(data.get("response", ""))
        return None

    def _parse_json_safely(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract and parse JSON safely from potential markdown code fences."""
        if not text:
            return None
        text = text.strip()
        # Strip markdown ```json ... ```
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
            text = re.sub(r"\s*```$", "", text)
        text = text.strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Attempt to find the first '{' and last '}'
            match = re.search(r"(\{.*\})", text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(1))
                except Exception:
                    pass
        return None


# Global LLM instance
llm_client = LLMClient()
