"""Module 2: Bidirectional Legal Language Transformation orchestration."""

import logging
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from config import settings
from nlp.entities import ExtractedFact, extract_all_facts
from nlp.preprocessing import preprocess_text
from nlp.retrieval import LegalTerm
from nlp.transformation import (
    PreservationReport,
    lookup_term,
    run_preservation_checks,
    transform_legal_to_normal,
    transform_normal_to_legal,
)

logger = logging.getLogger("lexilaw.legal_language")


class TransformRequest(BaseModel):
    """Input payload for legal language transformation."""

    text: str = Field(..., description="Source text to transform")
    mode: str = Field(
        ...,
        description="Transformation mode: strictly 'legal_to_normal' or 'normal_to_legal'",
        json_schema_extra={"example": "legal_to_normal"},
    )
    context: Optional[Dict[str, Any]] = Field(
        default=None, description="Optional drafting context or background parameters"
    )


class TransformResponse(BaseModel):
    """Result payload for bidirectional transformation with preservation report."""

    request_id: str
    mode: str
    original_text: str
    transformed_text: str
    extracted_facts: List[ExtractedFact]
    terminology_explanations: List[LegalTerm]
    missing_details: List[str]
    preservation_checks: PreservationReport
    warnings: List[str]
    review_status: str  # "passed_basic_checks", "warnings", "review_required"


def process_transformation(
    request: TransformRequest,
    request_id: str,
) -> TransformResponse:
    """Execute bidirectional language transformation."""
    text = request.text.strip()
    if not text:
        raise ValueError("Input text must not be empty.")

    if len(text) > settings.max_text_length:
        raise ValueError(
            f"Input text exceeds maximum allowed length of {settings.max_text_length} characters."
        )

    mode = request.mode.strip().lower()
    if mode not in ("legal_to_normal", "normal_to_legal"):
        raise ValueError(
            f"Unsupported mode '{request.mode}'. Allowed modes are 'legal_to_normal' and 'normal_to_legal'."
        )

    # Preprocess text to validate English language and normalize Unicode
    doc = preprocess_text(text)
    extraction = extract_all_facts(doc.normalized_text)

    if mode == "legal_to_normal":
        transformed_text, term_explanations, warnings = transform_legal_to_normal(doc.normalized_text)
        missing_details: List[str] = []
    else:  # normal_to_legal
        transformed_text, missing_details, warnings = transform_normal_to_legal(doc.normalized_text)
        term_explanations: List[LegalTerm] = []

    # Run deterministic fact and meaning preservation verification
    preservation_report = run_preservation_checks(doc.normalized_text, transformed_text)

    return TransformResponse(
        request_id=request_id,
        mode=mode,
        original_text=doc.normalized_text,
        transformed_text=transformed_text,
        extracted_facts=extraction.facts,
        terminology_explanations=term_explanations,
        missing_details=missing_details,
        preservation_checks=preservation_report,
        warnings=warnings,
        review_status=preservation_report.overall_status,
    )


def get_term_explanation(term: str) -> Optional[LegalTerm]:
    """Retrieve verified dictionary explanation for a legal term."""
    clean_term = term.strip()
    if not clean_term:
        return None
    return lookup_term(clean_term)
