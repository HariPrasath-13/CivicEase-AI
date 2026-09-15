# CivicEase AI — Government Information Accessibility Analyzer

**Problem Statement GOV-29 — Public Service Accessibility Analyzer**  
> *"Understand Government. Improve Government."*

CivicEase AI is a full-stack, hybrid AI-powered platform that analyzes government service documents, policy notices, and welfare schemes. It identifies complex legal terminology, convoluted sentences, vague instructions, and missing essential service information—transforming obscure bureaucracy into clear, actionable citizen guidance and technical audit insights.

---

## 🏛 1. The Problem

Government service documents often contain archaic legalese, excessively long sentences, passive voice constructions, ambiguous deadlines, and missing critical information (such as fees, exact submission offices, and processing timelines). This creates severe barriers for ordinary citizens attempting to understand and claim their public rights and welfare entitlements.

---

## 💡 2. The Solution: Dual-Mode Accessibility Intelligence

CivicEase AI operates a single, centralized **Hybrid Document Intelligence Engine** powering two tailored user modes:

```
                    GOVERNMENT DOCUMENT
                             ↓
                 CENTRAL ACCESSIBILITY ENGINE
                             ↓
             ┌───────────────┴───────────────┐
             ▼                               ▼
       👤 CITIZEN MODE                🏛 AUDITOR MODE
  • Plain Language Explanation     • Page-Level Issue Traceability
  • Step-by-Step Procedure         • 5W1H Instruction Clarity Audit
  • Document Checklist             • 7-Field Completeness Matrix
  • Key Service Facts Grid         • Prioritized Drafter Recommendations
  • Simple English & Tamil         • PDF & Markdown Audit Reports
  • Before vs After Comparison     • Measured Improvement Stats
```

---

## 🔬 3. Hybrid AI Architecture

CivicEase AI adheres strictly to a **Hybrid AI Architecture**—deterministic tasks are handled by specialized rule-based NLP algorithms, while semantic and linguistic reasoning are performed via structured LLM pipelines with strict non-hallucination constraints:

```
                       UPLOADED DOCUMENT
                               ↓
             Text Extraction (PyMuPDF / docx / txt)
                               ↓
            Page-Preserving Sentence Preprocessing
                               ↓
          ┌────────────────────┴────────────────────┐
          ▼                                         ▼
   RULE-BASED NLP                                  LLM
  • Flesch Reading Ease                  • 5W1H Instruction Clarity
  • Flesch-Kincaid Grade Level           • Ambiguity Detection
  • Sentence Length Flags (>25, >40)     • Missing Info Auditor
  • Jargon & Legalese Dictionary         • Plain English Simplification
  • Passive Voice Regex                  • Accurate Tamil Translation
          └────────────────────┬────────────────────┘
                               ↓
                  ACCESSIBILITY ENGINE JSON
                               ↓
               COMPOSITE SCORING (6 DIMENSIONS)
                               ↓
                   DUAL-MODE DASHBOARDS
```

### Rule-Based Engine
- **Readability**: Computes Flesch Reading Ease, Flesch-Kincaid Grade Level, average sentence length, and complex word ratio using `textstat` and pure-Python fallbacks.
- **Sentence Length Analyzer**: Detects sentences $>25$ words (*Warning*) and $>40$ words (*High Severity*) with exact page numbers.
- **Jargon & Legalese Dictionary**: Curated database of 120+ Indian and global administrative/legal terms (*hereinafter, aforementioned, requisite, competent authority, furnish, mutatis mutandis, prescribed proforma, encumbrance, debarment, non-encumbrance*).
- **Passive Voice Detector**: Highlights bureaucratic passive phrasing that hides responsible actors.

### Semantic AI Engine
- **Instruction Clarity (5W1H)**: Verifies whether instructions clarify **WHO, WHAT, WHERE, WHEN, and HOW**.
- **Ambiguity Detection**: Flags phrases like *"within the prescribed period"*, *"concerned authority"*, *"as applicable"*.
- **Missing Information Auditor**: Analyzes 7 mandatory service fields (**Eligibility, Required Documents, Application Process, Fee, Deadline, Processing Time, Contact**).
- **Language Simplifier**: Rewrites complex text into Plain English and Tamil with **zero hallucination** of unmentioned fees, dates, or offices.

---

## 📊 4. CivicEase Composite Accessibility Score

The project-defined composite accessibility score is computed deterministically across 6 weighted dimensions:

$$\text{Final Score} = 0.20 \times \text{Language} + 0.25 \times \text{Instruction} + 0.25 \times \text{Completeness} + 0.15 \times \text{Readability} + 0.10 \times \text{Terminology} + 0.05 \times \text{Actionability}$$

| Score Range | Tier | Color | Description |
| :---: | :---: | :---: | :--- |
| **85 – 100** | **Very Easy** | 🟢 Green | Extremely accessible; clear conversational plain English. |
| **70 – 84** | **Easy** | 🔵 Blue | Easily understandable with minimal specialized terminology. |
| **50 – 69** | **Moderate** | 🟡 Yellow | Contains moderate bureaucracy or longer sentences. |
| **30 – 49** | **Difficult** | 🟠 Orange | Significant legalese, long sentences, or missing key facts. |
| **0 – 29** | **Very Difficult** | 🔴 Red | Severe comprehension barriers, dense legalese, and major gaps. |

*Disclaimer: The CivicEase Composite Accessibility Score is a project-defined multi-metric index and does not represent an official statutory government standard.*

---

## 🛠 5. Technology Stack

- **Frontend**: Streamlit (with custom public-service CSS, responsive layout, Plotly charts)
- **Backend & NLP**: Python 3.10+, PyMuPDF (`fitz`), python-docx, textstat, Pydantic v2
- **AI & LLMs**: Google Gemini API, OpenAI / Groq / OpenRouter, Ollama, with an intelligent deterministic heuristic fallback
- **Database & Storage**: SQLite 3 with SHA-256 document hashing and relational audit tracking
- **Exporting**: ReportLab PDF generator and Markdown export

---

## 🚀 6. Installation & Quickstart

### Prerequisites
- Python 3.10, 3.11, 3.12, or 3.13 installed.

### 1. Clone Repository & Setup Virtual Environment
```bash
# Windows
py -m venv venv
.\venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment (Optional)
Copy the environment template:
```bash
cp .env.example .env
```
Edit `.env` to provide your API key (if using online LLMs):
```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key_here
```
> **Note**: CivicEase AI includes an advanced deterministic heuristic engine that functions **100% offline without any API keys required**!

### 4. Run the Application
You can run both the interactive Streamlit UI and the standalone REST API:

#### Option A: Streamlit Interactive UI
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

#### Option B: Standalone FastAPI REST API
```bash
uvicorn api:api_app --host 0.0.0.0 --port 8000 --reload
```
Interactive OpenAPI Swagger UI: `http://localhost:8000/docs`  
ReDoc Documentation: `http://localhost:8000/redoc`

---

## 🌐 7. Complete End-to-End REST API Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Root service metadata & supported configurations |
| `GET` | `/health` | Service healthcheck |
| `POST` | `/api/auth/login` | Authenticate user & get role permissions |
| `POST` | `/api/auth/register` | Register new citizen or auditor |
| `GET` | `/api/auth/demo-users` | List 1-click evaluation demo credentials |
| `POST` | `/api/documents/upload-and-analyze` | Upload file (PDF, DOCX, TXT) and run complete audit pipeline |
| `POST` | `/api/documents/analyze-text` | Directly analyze raw policy or circular text |
| `GET` | `/api/documents/samples` | List all preloaded sample government documents |
| `POST` | `/api/documents/analyze-sample/{filename}` | 1-Click instant analysis of a preloaded sample |
| `GET` | `/api/analysis/{id}/citizen-view` | Tailored citizen roadmap, checklist, warnings & Tamil translation |
| `GET` | `/api/analysis/{id}/auditor-view` | Technical audit breakdown, severity filters & page traceability |
| `POST` | `/api/simplify` | Plain English & Tamil simplification engine |
| `GET` | `/api/reports/{id}/pdf` | Download binary PDF audit report |
| `GET` | `/api/reports/{id}/markdown` | Download Markdown audit report |
| `GET` | `/api/history` | List recent document audit records |

---

## 🔑 7. Demo Credentials

Instant 1-click demo login buttons are provided on the login screen, or use:

| Role | Username | Password | Purpose |
| :--- | :--- | :--- | :--- |
| **Citizen** | `citizen` | `citizen123` | Plain language, checklist, procedure, Tamil |
| **Government Auditor** | `auditor` | `auditor123` | Technical audit, severity filters, PDF export |
| **Administrator** | `admin` | `admin123` | Full system access |

---

## 📂 8. Project Structure

```text
civicease-ai/
├── app.py                           # Main Streamlit orchestration & routing
├── requirements.txt                 # Project dependencies
├── README.md                        # Documentation
├── .env.example                     # Environment template
│
├── config/
│   └── settings.py                  # Paths, constants, weights, thresholds
│
├── data/
│   ├── uploads/                     # Uploaded files
│   ├── reports/                     # Generated reports
│   └── sample_documents/            # Preloaded demo government orders
│
├── database/
│   ├── database.py                  # SQLite schema, queries, user auth
│   └── models.py                    # Dataclass models
│
├── auth/
│   └── authentication.py            # Session management and guards
│
├── document/
│   ├── pdf_parser.py                # PyMuPDF page-preserving parser
│   ├── docx_parser.py               # python-docx parser
│   ├── txt_parser.py                # Multi-encoding text parser
│   └── preprocessing.py             # Sentence splitting & header cleanup
│
├── nlp/
│   ├── readability.py               # Flesch, Fog, Grade level formulas
│   ├── sentence_analysis.py         # Long sentence detector (>25, >40)
│   ├── jargon_detector.py           # 120+ legal term database & replacements
│   ├── complexity_detector.py       # Polysyllabic vocabulary analyzer
│   └── passive_voice.py             # Passive voice detector
│
├── ai/
│   ├── llm_client.py                # Unified LLM caller (Gemini/OpenAI/Ollama/Fallback)
│   ├── prompts.py                   # Strict anti-fabrication prompt templates
│   ├── semantic_analyzer.py         # 5W1H clarity, ambiguity, missing info
│   ├── simplifier.py                # Plain English & Tamil simplification
│   └── schemas.py                   # Pydantic schemas for JSON validation
│
├── analysis/
│   ├── accessibility_engine.py      # Master orchestrator combining NLP + AI
│   ├── missing_information.py       # 7-field completeness matrix
│   ├── scoring.py                   # 6-dimension composite score calculation
│   └── recommendations.py           # Prioritized actionable recommendations
│
├── reports/
│   └── report_generator.py          # PDF and Markdown audit generator
│
├── ui/
│   ├── login.py                     # Login & registration view
│   ├── mode_selection.py            # Citizen vs Auditor mode cards
│   ├── citizen_dashboard.py         # Plain language, checklist, Tamil view
│   ├── government_dashboard.py      # Technical audit, filters, PDF export
│   └── components.py                # Reusable CSS badges, score gauges
│
└── utils/
    ├── helpers.py                   # Hash, text truncation, formatting
    └── logging.py                   # Centralized logger
```

---

## 🔮 9. Limitations & Future Enhancements

- **OCR Fallback**: Optical Character Recognition for low-resolution scanned image PDFs via Tesseract / easyocr.
- **Expanded Indian Languages**: Extending translation and voice output to Hindi, Telugu, Kannada, Bengali, and Marathi.
- **Standard Harmonization**: Mapping composite scores to emerging official public communication standards (e.g. US Plain Writing Act, Indian NeSDA guidelines).
- **Interactive Document Editor**: Real-time drafting assistant with live score suggestions for government officials.

---

## 📜 10. License
Developed for Hackathon Problem **GOV-29**. Open for public service modernization.
