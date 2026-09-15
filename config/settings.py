"""
Configuration settings for CivicEase AI - Public Service Accessibility Analyzer.
"""
import os
from pathlib import Path

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Base Directories
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
UPLOADS_DIR = DATA_DIR / "uploads"
REPORTS_DIR = DATA_DIR / "reports"
SAMPLE_DOCS_DIR = DATA_DIR / "sample_documents"
DATABASE_PATH = BASE_DIR / "civicease.db"

# Ensure runtime directories exist
for directory in [DATA_DIR, UPLOADS_DIR, REPORTS_DIR, SAMPLE_DOCS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Application Branding
APP_TITLE = "CivicEase AI"
APP_SUBTITLE = "Government Information Accessibility Analyzer"
APP_TAGLINE = "Empowering citizens with clarity. Equipping governments with actionable accessibility insights."
APP_VERSION = "1.0.0"

# LLM Configurations
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini").lower()  # gemini, openai, groq, ollama, fallback
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", os.getenv("GOOGLE_API_KEY", ""))
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
LLM_MODEL = os.getenv("LLM_MODEL", "gemini-1.5-flash" if LLM_PROVIDER == "gemini" else "gpt-4o-mini")

# Rule-Based NLP Thresholds
SENTENCE_LENGTH_WARNING = 25  # Words
SENTENCE_LENGTH_HIGH_SEVERITY = 40  # Words
PARAGRAPH_LENGTH_WARNING = 150  # Words

# CivicEase AI Composite Accessibility Score Weights (Sum = 1.00)
# Language Simplicity: 20%
# Instruction Clarity: 25%
# Information Completeness: 25%
# Readability: 15%
# Terminology: 10%
# Actionability: 5%
SCORE_WEIGHTS = {
    "language_simplicity": 0.20,
    "instruction_clarity": 0.25,
    "information_completeness": 0.25,
    "readability": 0.15,
    "terminology": 0.10,
    "actionability": 0.05,
}

# Score Interpretation Tiers
SCORE_TIERS = [
    (85, 100, "Very Easy", "#10B981", "Extremely accessible and plain language for general citizens."),
    (70, 84, "Easy", "#3B82F6", "Easily understandable with minimal complex terminology."),
    (50, 69, "Moderate", "#F59E0B", "Contains some bureaucratic jargon or moderate sentence lengths."),
    (30, 49, "Difficult", "#F97316", "Significant legalese, long sentences, or missing key information."),
    (0, 29, "Very Difficult", "#EF4444", "Severe accessibility barriers, heavy legalese, and major gaps."),
]

# Information Completeness Fields
MANDATORY_SERVICE_FIELDS = [
    ("eligibility", "Eligibility Criteria", "Who is eligible to apply for this government service"),
    ("required_documents", "Required Documents", "Specific checklist of supporting certificates/proofs"),
    ("application_process", "Application Process", "Clear step-by-step submission procedure & channel"),
    ("fee", "Application Fee", "Exact charges, payment methods, or explicit free waiver"),
    ("deadline", "Application Deadline", "Specific dates, duration, or recurring time window"),
    ("processing_time", "Processing Time", "Expected turnaround time for decision/dispatch"),
    ("contact_information", "Contact / Helpdesk", "Official phone, email, helpdesk, or physical office"),
]

# Supported File Extensions
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}
MAX_FILE_SIZE_MB = 20
