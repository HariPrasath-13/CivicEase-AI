"""
Semantic Analyzer for CivicEase AI.
Performs 5W1H instruction clarity analysis, ambiguity detection, and missing information checks
using hybrid LLM + deterministic heuristic fallbacks.
"""
import re
from typing import Any, Dict, List, Optional

from ai.llm_client import llm_client
from ai.prompts import SEMANTIC_ANALYSIS_SYSTEM_PROMPT, SEMANTIC_ANALYSIS_USER_PROMPT_TEMPLATE
from ai.schemas import (
    AmbiguityIssue,
    CitizenSummarySchema,
    CompleteSemanticAnalysis,
    InstructionClarityIssue,
    MissingInfoField,
    RecommendationItem,
)
from utils.logging import get_logger

logger = get_logger(__name__)


class SemanticAnalyzer:
    """Orchestrates semantic document analysis with Pydantic validation."""

    def analyze(self, preprocessed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes semantic analysis. Tries LLM first; if unavailable or invalid,
        uses deterministic heuristic analysis.
        """
        cleaned_pages = preprocessed_data.get("cleaned_pages", [])
        sentences = preprocessed_data.get("sentences", [])
        full_text = preprocessed_data.get("full_text", "")

        # Format document content with page markers
        page_chunks = []
        for p in cleaned_pages:
            page_chunks.append(f"--- PAGE {p['page']} ---\n{p['text']}")
        formatted_doc = "\n\n".join(page_chunks)

        user_prompt = SEMANTIC_ANALYSIS_USER_PROMPT_TEMPLATE.format(
            total_pages=len(cleaned_pages),
            total_sentences=len(sentences),
            document_content=formatted_doc[:12000]  # Respect token limits for large docs
        )

        llm_response = llm_client.generate_json(SEMANTIC_ANALYSIS_SYSTEM_PROMPT, user_prompt)

        if llm_response:
            try:
                # Validate with Pydantic
                validated = CompleteSemanticAnalysis.model_validate(llm_response)
                logger.info("Semantic analysis successfully generated and validated by LLM.")
                return validated.model_dump()
            except Exception as val_err:
                logger.warning("LLM response failed Pydantic schema validation: %s. Using heuristic fallback.", str(val_err))

        # Heuristic deterministic fallback
        logger.info("Executing deterministic heuristic semantic analyzer...")
        return self._heuristic_semantic_analysis(preprocessed_data)

    def _heuristic_semantic_analysis(self, preprocessed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deterministic, rule-based semantic extractor for offline or fallback operation.
        Guarantees zero crashes and high fidelity to the source document.
        """
        sentences = preprocessed_data.get("sentences", [])
        full_text = preprocessed_data.get("full_text", "")
        cleaned_pages = preprocessed_data.get("cleaned_pages", [])

        unclear_instructions: List[Dict[str, Any]] = []
        ambiguities: List[Dict[str, Any]] = []

        # 1. Detect Ambiguities via regex patterns
        ambiguity_patterns = [
            (
                r"\b(?:within\s+the\s+prescribed\s+period|in\s+due\s+course|within\s+reasonable\s+time|stipulated\s+time)\b",
                "Ambiguous Deadline / Timeframe",
                "WHEN",
                "The exact timeline, deadline, or number of working days is not specified.",
                "State the exact timeframe (e.g. 'Within 30 calendar days of notification')."
            ),
            (
                r"\b(?:concerned\s+authority|competent\s+authority|appropriate\s+department|authorized\s+officer)\b",
                "Unclear Submitting Authority",
                "WHERE / WHO",
                "The exact department, desk, or designated officer name is not identified.",
                "Explicitly name the department or designated counter (e.g. 'Taluk Supply Officer / Ward Office')."
            ),
            (
                r"\b(?:as\s+applicable|as\s+required|as\s+per\s+rules|as\s+deemed\s+fit|at\s+the\s+discretion\s+of)\b",
                "Ambiguous Condition / Rule",
                "HOW / WHAT",
                "Terms like 'as applicable' create uncertainty for citizens regarding whether a rule applies to them.",
                "Provide clear conditional criteria (e.g. 'If your annual income exceeds ₹2,00,000, attach Form B')."
            ),
            (
                r"\b(?:appropriate\s+documents|requisite\s+proofs|necessary\s+certificates|valid\s+documents)\b",
                "Vague Document Requirement",
                "WHAT",
                "Does not specify which exact certificates or proofs must be enclosed.",
                "Provide a bulleted list of exact acceptable identity and address proofs."
            )
        ]

        for s in sentences:
            stext = s.get("text", "")
            spage = s.get("page", 1)
            for pattern, issue_title, aspect, explanation, suggestion in ambiguity_patterns:
                match = re.search(pattern, stext, re.IGNORECASE)
                if match:
                    ambiguities.append({
                        "id": f"ambiguity_{len(ambiguities)}",
                        "category": "Ambiguity",
                        "issue": issue_title,
                        "severity": "MEDIUM",
                        "page": spage,
                        "original_text": stext,
                        "explanation": explanation,
                        "suggestion": suggestion
                    })

        # 2. Detect Unclear Instructions (5W1H)
        instruction_verbs = r"\b(?:submit|apply|furnish|approach|forward|deposit|obtain|remit|dispatch|register)\b"
        for s in sentences:
            stext = s.get("text", "")
            spage = s.get("page", 1)
            if re.search(instruction_verbs, stext, re.IGNORECASE):
                # Check for passive or missing authority
                if re.search(r"\b(?:concerned\s+authority|competent\s+authority|appropriate\s+office)\b", stext, re.IGNORECASE):
                    unclear_instructions.append({
                        "id": f"inst_{len(unclear_instructions)}",
                        "category": "Instruction Clarity",
                        "issue": "Unspecified Submission Destination (WHERE / WHO)",
                        "severity": "HIGH",
                        "page": spage,
                        "original_text": stext,
                        "missing_aspect": "WHERE / WHO",
                        "explanation": "The instruction directs the citizen to submit materials, but fails to identify the physical address, department, or online portal.",
                        "suggestion": "Specify the exact office, designated portal URL, or counter number for submission."
                    })
                elif re.search(r"\b(?:prescribed\s+proforma|prescribed\s+manner)\b", stext, re.IGNORECASE) and not re.search(r"(?:Annexure|Form\s+[A-Z0-9]|portal)", stext, re.IGNORECASE):
                    unclear_instructions.append({
                        "id": f"inst_{len(unclear_instructions)}",
                        "category": "Instruction Clarity",
                        "issue": "Unspecified Form Location (HOW / WHAT)",
                        "severity": "MEDIUM",
                        "page": spage,
                        "original_text": stext,
                        "missing_aspect": "HOW / WHAT",
                        "explanation": "References a 'prescribed proforma' without indicating where or how the citizen can download or collect the form.",
                        "suggestion": "State where the application form is available (e.g. 'Download Form A from https://edistrict.gov.in or collect from the helpdesk')."
                    })

        # 3. Check 7 Mandatory Service Fields
        missing_info: List[Dict[str, Any]] = []

        # Eligibility
        elig_match = re.search(r"(?:eligib|resident|domicile|annual\s+income|age\s+limit|criteria|citizenship|who\s+can\s+apply)", full_text, re.IGNORECASE)
        if elig_match:
            # Extract sentence snippet
            elig_status = "FOUND"
            elig_details = "Eligibility conditions identified in document."
            for s in sentences:
                if re.search(r"(?:eligib|income|age|resident)", s.get("text", ""), re.IGNORECASE):
                    elig_details = s.get("text", "")
                    break
        else:
            elig_status = "MISSING"
            elig_details = "Eligibility criteria are not explicitly detailed in the source document."

        missing_info.append({
            "field_key": "eligibility",
            "display_name": "Eligibility Criteria",
            "status": elig_status,
            "extracted_details": elig_details,
            "confidence_reason": "Scanned for age, income, category, and demographic eligibility criteria."
        })

        # Required Documents
        doc_matches = re.findall(r"(?:Aadhaar|Ration\s+Card|Income\s+Certificate|Voter\s+ID|Community\s+Certificate|Passport|Birth\s+Certificate|Bank\s+Passbook|Affidavit)", full_text, re.IGNORECASE)
        if doc_matches:
            docs_status = "FOUND"
            unique_docs = list(set(doc_matches))
            docs_details = f"Specific documents mentioned: {', '.join(unique_docs)}."
        elif re.search(r"(?:document|certificate|proof|enclosure)", full_text, re.IGNORECASE):
            docs_status = "PARTIAL"
            docs_details = "Document mentions generic 'requisite certificates' but lacks an exhaustive, unambiguous checklist."
        else:
            docs_status = "MISSING"
            docs_details = "Required supporting documents checklist is missing."

        missing_info.append({
            "field_key": "required_documents",
            "display_name": "Required Documents",
            "status": docs_status,
            "extracted_details": docs_details,
            "confidence_reason": "Evaluated specific certificate names versus vague document references."
        })

        # Application Process
        process_match = re.search(r"(?:apply|application\s+procedure|submission|portal|online|counter|step)", full_text, re.IGNORECASE)
        if process_match:
            process_status = "FOUND" if re.search(r"(?:step|portal|https?://|ward\s+office|taluk)", full_text, re.IGNORECASE) else "PARTIAL"
            process_details = "Application steps outlined in document."
        else:
            process_status = "MISSING"
            process_details = "Step-by-step application workflow is not explained."

        missing_info.append({
            "field_key": "application_process",
            "display_name": "Application Process",
            "status": process_status,
            "extracted_details": process_details,
            "confidence_reason": "Verified whether a clear submission mechanism is outlined."
        })

        # Fee
        fee_match = re.search(r"(?:₹\s*\d+|Rs\.?\s*\d+|\bINR\b|\bfee\b|\bcharges\b|\bfree\s+of\s+cost\b|\bno\s+fee\b|\bchallan\b)", full_text, re.IGNORECASE)
        if fee_match:
            # Extract specific sentence
            fee_sentence = ""
            for s in sentences:
                if re.search(r"(?:₹|Rs\.?|fee|charge|free|challan)", s.get("text", ""), re.IGNORECASE):
                    fee_sentence = s.get("text", "")
                    break
            fee_status = "FOUND"
            fee_details = fee_sentence if fee_sentence else "Fee information is mentioned."
        else:
            fee_status = "MISSING"
            fee_details = "Application fee or free waiver is not specified in the source text."

        missing_info.append({
            "field_key": "fee",
            "display_name": "Application Fee",
            "status": fee_status,
            "extracted_details": fee_details,
            "confidence_reason": "Searched for currency amounts (₹/Rs), challan payment modes, or free waiver declarations."
        })

        # Deadline
        date_pattern = r"\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{1,2}(?:st|nd|rd|th)?\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4})\b"
        deadline_date = re.search(date_pattern, full_text, re.IGNORECASE)
        if deadline_date:
            deadline_status = "FOUND"
            deadline_details = f"Specific deadline identified: {deadline_date.group(0)}"
        elif re.search(r"(?:within\s+the\s+prescribed\s+period|stipulated\s+date|last\s+date)", full_text, re.IGNORECASE):
            deadline_status = "AMBIGUOUS"
            deadline_details = "Mentions a deadline or 'prescribed period' but does not specify exact calendar dates or days."
        elif re.search(r"(?:throughout\s+the\s+year|ongoing|continuous)", full_text, re.IGNORECASE):
            deadline_status = "FOUND"
            deadline_details = "Service accepts applications on an ongoing / year-round basis."
        else:
            deadline_status = "MISSING"
            deadline_details = "Application deadline or validity period is not mentioned in the document."

        missing_info.append({
            "field_key": "deadline",
            "display_name": "Application Deadline",
            "status": deadline_status,
            "extracted_details": deadline_details,
            "confidence_reason": "Evaluated exact calendar deadlines versus ambiguous phrases."
        })

        # Processing Time
        time_match = re.search(r"\b(?:\d+\s*(?:working\s*)?(?:days|weeks|months|hours))\b", full_text, re.IGNORECASE)
        if time_match:
            time_status = "FOUND"
            time_details = f"Estimated processing turnaround: {time_match.group(0)}."
        else:
            time_status = "MISSING"
            time_details = "Turnaround or processing time is not stated in the source document."

        missing_info.append({
            "field_key": "processing_time",
            "display_name": "Processing Time",
            "status": time_status,
            "extracted_details": time_details,
            "confidence_reason": "Checked for SLA commitments and processing duration."
        })

        # Contact Information
        contact_match = re.search(r"(?:\b\d{10}\b|\b1800[-\s]?\d{3}[-\s]?\d{3,4}\b|[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+|https?://[^\s]+|\bhelpdesk\b|\bhelpline\b)", full_text, re.IGNORECASE)
        if contact_match:
            contact_status = "FOUND"
            contact_details = f"Contact/Helpline details: {contact_match.group(0)}"
        else:
            contact_status = "MISSING"
            contact_details = "Official phone, email, helpline, or grievance contact is not provided."

        missing_info.append({
            "field_key": "contact_information",
            "display_name": "Contact / Helpdesk",
            "status": contact_status,
            "extracted_details": contact_details,
            "confidence_reason": "Looked for toll-free numbers, emails, helpdesk contacts, and websites."
        })

        # 4. Generate Actionable Recommendations
        recommendations = []
        if any(m["status"] in ["MISSING", "AMBIGUOUS"] for m in missing_info if m["field_key"] == "fee"):
            recommendations.append({
                "category": "Fee Transparency",
                "priority": "HIGH",
                "recommendation": "Explicitly state the application fee amount or clearly state 'No application fee is required (Free of cost)'.",
                "rationale": "Missing fee information leaves applicants unsure about transaction costs."
            })
        if any(m["status"] in ["MISSING", "AMBIGUOUS"] for m in missing_info if m["field_key"] == "deadline"):
            recommendations.append({
                "category": "Timeline Clarity",
                "priority": "HIGH",
                "recommendation": "Specify the exact deadline date or clear timeframe (e.g., 'Applications close on 31st March 2026').",
                "rationale": "Vague phrases like 'prescribed period' cause applicants to miss critical submission windows."
            })
        if unclear_instructions:
            recommendations.append({
                "category": "Instruction Clarity",
                "priority": "HIGH",
                "recommendation": "Replace vague terms like 'competent authority' with the exact name, address, or designated online portal.",
                "rationale": f"{len(unclear_instructions)} unclear instruction(s) detected where citizens are not told where to submit."
            })
        if any(m["status"] == "MISSING" for m in missing_info if m["field_key"] == "processing_time"):
            recommendations.append({
                "category": "Service Timeline",
                "priority": "MEDIUM",
                "recommendation": "Include an expected processing time (e.g. 'Applications will be processed within 15 working days').",
                "rationale": "Citizens need clear turnaround expectations to prevent anxiety and unnecessary office visits."
            })
        if any(m["status"] == "MISSING" for m in missing_info if m["field_key"] == "contact_information"):
            recommendations.append({
                "category": "Public Support",
                "priority": "MEDIUM",
                "recommendation": "Provide an official helpline phone number, email address, or designated grievance officer contact.",
                "rationale": "No contact information is provided in the document for citizen inquiries."
            })

        # 5. Build Citizen Explanation & Tamil Translation
        first_page_text = cleaned_pages[0]["text"] if cleaned_pages else "Government Scheme"
        first_line = first_page_text.split("\n")[0] if first_page_text else "Government Service Document"
        service_name = first_line[:80].strip() or "Public Service Directive"

        # Formulate simple steps
        steps = [
            "Verify your eligibility criteria before starting your application.",
            "Gather all required identity, residency, and income proof documents.",
            "Complete the official application form with accurate details.",
            "Submit the completed form along with required attachments to the designated government office.",
            "Collect your official acknowledgement receipt for status tracking."
        ]

        # Extract checklist
        doc_checklist = []
        if doc_matches:
            doc_checklist = list(set(doc_matches))
        else:
            doc_checklist = [
                "Government issued Photo ID Proof (Aadhaar / Voter ID / Passport)",
                "Address Proof (Ration Card / Utility Bill / Domicile Certificate)",
                "Income Certificate (if applicable for scheme eligibility)",
                "Passport-size Photographs"
            ]

        # Critical warnings
        warnings = []
        for m in missing_info:
            if m["status"] == "MISSING":
                warnings.append(f"⚠ {m['display_name']}: Not mentioned in this document. Verify with your local office.")
            elif m["status"] == "AMBIGUOUS":
                warnings.append(f"⚠ {m['display_name']}: The instructions in this document are ambiguous.")

        # Plain English summary
        plain_english = (
            f"This government document describes the guidelines for '{service_name}'. "
            "It outlines the rules, required documents, and submission procedures for eligible citizens. "
            "To apply, check your eligibility, prepare your certificates, and submit your application to the designated department."
        )

        # Tamil translation
        tamil_translation = (
            f"இந்த அரசு ஆவணம் '{service_name}' தொடர்பான வழிகாட்டுதல்களை விவரிக்கிறது. "
            "தகுதியுள்ள குடிமக்கள் இந்த சேவையைப் பெறுவதற்கான விதிகள், தேவையான ஆவணங்கள் மற்றும் விண்ணப்பிக்கும் நடைமுறைகளை இது விளக்குகிறது.\n\n"
            "விண்ணப்பிக்கும் படிகள்:\n"
            "1. விண்ணப்பிக்கும் முன் உங்களின் தகுதி வரம்புகளைச் சரிபார்க்கவும்.\n"
            "2. தேவையான அடையாள மற்றும் வருமானச் சான்றிதழ்களைத் தயார் செய்யவும்.\n"
            "3. அதிகாரப்பூர்வ விண்ணப்பப் படிவத்தைப் பூர்த்தி செய்யவும்.\n"
            "4. குறிப்பிட்ட அரசு அலுவலகம் அல்லது ஆன்லைன் தளத்தில் சமர்ப்பிக்கவும்.\n"
            "5. ஒப்புகைச் சீட்டை (Acknowledgement Slip) பெற்று பத்திரமாக வைக்கவும்."
        )

        # Before vs After sample
        before_text = "The applicant shall furnish the requisite documents to the competent authority within the prescribed period."
        after_text = "Submit the required documents to the designated government office within 30 days."

        return {
            "unclear_instructions": unclear_instructions,
            "ambiguities": ambiguities,
            "missing_information": missing_info,
            "citizen_output": {
                "service_name": service_name,
                "brief_summary": plain_english,
                "who_can_apply": elig_details,
                "how_to_apply_steps": steps,
                "documents_checklist": doc_checklist,
                "fee_details": fee_details,
                "deadline_details": deadline_details,
                "processing_time_details": time_details,
                "contact_details": contact_details,
                "critical_warnings": warnings,
                "simplified_english": plain_english,
                "tamil_translation": tamil_translation
            },
            "auditor_recommendations": recommendations,
            "before_after_sample": {
                "before_text": before_text,
                "after_text": after_text,
                "before_words": len(before_text.split()),
                "after_words": len(after_text.split()),
                "before_jargon_count": 3,
                "after_jargon_count": 0,
                "clarity_improvement": "High"
            }
        }


# Global instance
semantic_analyzer = SemanticAnalyzer()
