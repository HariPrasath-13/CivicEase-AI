"""
Pydantic Schemas for Structured AI Responses in CivicEase AI.
Guarantees strict schema adherence and reliable JSON parsing.
"""
from typing import Any, Dict, List, Literal, Optional

try:
    from pydantic import BaseModel, Field
    HAS_PYDANTIC = True
except ImportError:
    HAS_PYDANTIC = False
    class BaseModel:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)
        @classmethod
        def model_validate(cls, data):
            if isinstance(data, dict):
                return cls(**data)
            return data
        def model_dump(self):
            return self.__dict__
    def Field(*args, **kwargs):
        return kwargs.get("default", None)


class InstructionClarityIssue(BaseModel):
    issue: str = Field(description="Brief title of unclear instruction, e.g., 'Unclear Submission Authority'")
    category: str = Field(default="Instruction Clarity", description="Category name")
    severity: Literal["HIGH", "MEDIUM", "LOW"] = Field(description="Severity rating")
    page: int = Field(default=1, description="Source page number where issue occurs")
    original_text: str = Field(description="Original excerpt from the document")
    missing_aspect: str = Field(description="Which of 5W1H is missing or unclear (WHO, WHAT, WHERE, WHEN, HOW)")
    explanation: str = Field(description="Why this instruction is unclear or confusing to an applicant")
    suggestion: str = Field(description="Concrete recommendation to clarify the instruction without inventing facts")


class AmbiguityIssue(BaseModel):
    issue: str = Field(description="Brief title of ambiguous statement, e.g., 'Ambiguous Deadline'")
    category: str = Field(default="Ambiguity", description="Category name")
    severity: Literal["HIGH", "MEDIUM", "LOW"] = Field(description="Severity rating")
    page: int = Field(default=1, description="Source page number")
    original_text: str = Field(description="Vague phrase or sentence from document")
    explanation: str = Field(description="Why the wording is open to multiple interpretations or vague")
    suggestion: str = Field(description="Specific actionable improvement")


class MissingInfoField(BaseModel):
    field_key: str = Field(description="One of: eligibility, required_documents, application_process, fee, deadline, processing_time, contact_information")
    display_name: str = Field(description="Human readable name")
    status: Literal["FOUND", "PARTIAL", "MISSING", "AMBIGUOUS"] = Field(description="Completeness status")
    extracted_details: str = Field(description="Details found in document, or explicit statement of what is missing")
    confidence_reason: str = Field(description="Brief rationale for status assignment")


class CitizenSummarySchema(BaseModel):
    service_name: str = Field(description="Name or title of the government service/scheme")
    brief_summary: str = Field(description="2-3 sentence plain language overview of the scheme")
    who_can_apply: str = Field(description="Clear eligibility summary in simple terms")
    how_to_apply_steps: List[str] = Field(description="Numbered step-by-step application instructions (max 6 steps)")
    documents_checklist: List[str] = Field(description="List of specific required documents")
    fee_details: str = Field(description="Application fee details or explicitly 'Not specified in document'")
    deadline_details: str = Field(description="Deadline details or 'Not specified / Ongoing'")
    processing_time_details: str = Field(description="Estimated processing time or 'Not specified in document'")
    contact_details: str = Field(description="Helpdesk or contact info or 'Not specified in document'")
    critical_warnings: List[str] = Field(description="Important warnings regarding missing info or strict penalties")
    simplified_english: str = Field(description="Complete plain-English rewrite of the document")
    tamil_translation: str = Field(description="Accurate, natural Tamil translation of the citizen summary and steps")


class RecommendationItem(BaseModel):
    category: str = Field(description="Area of improvement")
    priority: Literal["HIGH", "MEDIUM", "LOW"] = Field(description="Implementation priority")
    recommendation: str = Field(description="Clear, actionable recommendation text")
    rationale: str = Field(description="Directly references detected problems in the document")


class CompleteSemanticAnalysis(BaseModel):
    unclear_instructions: List[InstructionClarityIssue] = Field(default_factory=list)
    ambiguities: List[AmbiguityIssue] = Field(default_factory=list)
    missing_information: List[MissingInfoField] = Field(default_factory=list)
    citizen_output: CitizenSummarySchema
    auditor_recommendations: List[RecommendationItem] = Field(default_factory=list)
    before_after_sample: Dict[str, Any] = Field(default_factory=dict)
