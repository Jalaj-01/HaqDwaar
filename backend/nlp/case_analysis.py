"""Legal case document analysis, segmentation, and field-level extraction."""

import os
import re
from typing import Any, Dict, List, Optional
import fitz  # PyMuPDF
from pydantic import BaseModel, Field

from config import settings
from nlp.entities import EvidenceSpan, extract_legal_references
from nlp.preprocessing import preprocess_text


class CaseItem(BaseModel):
    """An individual extracted item from a judgment or case text."""
    text: str
    evidence_span: Optional[EvidenceSpan] = None
    section: str = "general"


class PartyArguments(BaseModel):
    """Arguments attributed separately to petitioner and respondent."""
    petitioner_arguments: List[CaseItem] = Field(default_factory=list)
    respondent_arguments: List[CaseItem] = Field(default_factory=list)


class CaseMetadata(BaseModel):
    """Core identifiers and administrative metadata of a court judgment."""
    title: str = "not identified"
    citation: str = "not identified"
    court: str = "not identified"
    decision_date: str = "not identified"
    parties: List[str] = Field(default_factory=list)


class CaseAnalysisResult(BaseModel):
    """Comprehensive structured case understanding output."""
    request_id: Optional[str] = None
    case_metadata: CaseMetadata
    material_facts: List[CaseItem] = Field(default_factory=list)
    legal_issues: List[CaseItem] = Field(default_factory=list)
    cited_provisions: List[CaseItem] = Field(default_factory=list)
    party_arguments: PartyArguments = Field(default_factory=PartyArguments)
    court_reasoning: List[CaseItem] = Field(default_factory=list)
    outcome: CaseItem = Field(default_factory=lambda: CaseItem(text="not identified"))
    key_takeaways: List[str] = Field(default_factory=list)
    evidence_spans: List[EvidenceSpan] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


class PageExtraction(BaseModel):
    """Extracted text and character counts for a single page."""
    page_number: int
    text: str
    char_count: int


class DocumentExtractResponse(BaseModel):
    """Structured response for uploaded PDF document extraction."""
    request_id: str
    filename: str
    page_count: int
    total_characters: int
    pages: List[PageExtraction]
    extracted_text: str
    warnings: List[str]


# Regex patterns for judgment structure
COURT_PATTERNS = [
    re.compile(r"\b(?:IN THE\s+)?SUPREME COURT OF INDIA\b", re.IGNORECASE),
    re.compile(r"\b(?:IN THE\s+)?HIGH COURT OF (?:JUDICATURE AT\s+)?([A-Z\s]+)\b", re.IGNORECASE),
    re.compile(r"\b(?:NATIONAL|STATE)\s+CONSUMER\s+DISPUTES\s+REDRESSAL\s+COMMISSION\b", re.IGNORECASE),
    re.compile(r"\bDISTRICT\s+COURT\b", re.IGNORECASE),
]

CASE_TITLE_LINE_PATTERN = re.compile(
    r"^([A-Z][A-Za-z0-9.,'\s\-]+?)\s+(?:VERSUS|VS\.?|V\.)\s+([A-Z][A-Za-z0-9.,'\s\-]+?)$",
    re.IGNORECASE,
)

DATE_PATTERNS = [
    re.compile(
        r"\b(?:Date of Decision|Decided on|Judgment Date|Dated)\s*[:\-]?\s*([0-9]{1,2}(?:th|st|nd|rd)?\s+[A-Za-z]+,?\s+[0-9]{4}|[0-9]{1,2}[-/.][0-9]{1,2}[-/.][0-9]{2,4})\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b([0-9]{1,2}(?:th|st|nd|rd)?\s+(?:January|February|March|April|May|June|July|August|September|October|November|December),?\s+[0-9]{4})\b",
        re.IGNORECASE,
    ),
]

# Sentence-level marker patterns for party submissions vs findings
PETITIONER_SUBMISSION_PATTERNS = [
    re.compile(r"\b(?:counsel\s+for\s+(?:the\s+)?(?:appellant|petitioner)|petitioner\s+contended|appellant\s+argued|submitted\s+on\s+behalf\s+of\s+(?:the\s+)?(?:appellant|petitioner))\b", re.IGNORECASE),
    re.compile(r"\b(?:appellant|petitioner)\s+submits?\s+that\b", re.IGNORECASE),
]

RESPONDENT_SUBMISSION_PATTERNS = [
    re.compile(r"\b(?:counsel\s+for\s+(?:the\s+)?respondent|respondent\s+contended|respondent\s+argued|submitted\s+on\s+behalf\s+of\s+(?:the\s+)?respondent)\b", re.IGNORECASE),
    re.compile(r"\brespondent\s+submits?\s+that\b", re.IGNORECASE),
]

COURT_FINDING_PATTERNS = [
    re.compile(r"\b(?:we\s+have\s+considered|in\s+our\s+(?:considered\s+)?(?:view|opinion)|this\s+court\s+finds|we\s+are\s+of\s+the\s+view|the\s+court\s+held\s+that)\b", re.IGNORECASE),
    re.compile(r"\b(?:it\s+is\s+well[- ]settled\s+that|having\s+heard\s+the\s+parties|we\s+find\s+force\s+in)\b", re.IGNORECASE),
]

OUTCOME_PATTERNS = [
    re.compile(r"\b(?:appeal\s+is\s+(?:allowed|dismissed)|petition\s+is\s+(?:allowed|dismissed|disposed\s+of))\b", re.IGNORECASE),
    re.compile(r"\b(?:conviction\s+is\s+(?:upheld|set\s+aside)|impugned\s+order\s+is\s+(?:set\s+aside|quashed|confirmed))\b", re.IGNORECASE),
    re.compile(r"\b(?:ordered\s+accordingly|directions\s+are\s+issued\s+accordingly)\b", re.IGNORECASE),
]


def extract_case_metadata(text: str) -> CaseMetadata:
    """Extract court, case title, citations, and decision dates from text."""
    court_found = "not identified"
    for pat in COURT_PATTERNS:
        m = pat.search(text)
        if m:
            court_found = m.group(0).strip()
            break

    title_found = "not identified"
    parties: List[str] = []

    # Check line-by-line for title to prevent cross-line bleeding
    for raw_line in text.split("\n"):
        line = raw_line.strip()
        if not line:
            continue
        tm = CASE_TITLE_LINE_PATTERN.match(line)
        if tm:
            p1 = tm.group(1).strip()
            p2 = tm.group(2).strip()
            # Avoid matching random sentences that happen to have 'v.'
            if len(p1.split()) <= 8 and len(p2.split()) <= 8:
                title_found = f"{p1} v. {p2}"
                parties = [p1, p2]
                break

    refs = extract_legal_references(text)
    citations = [r.text for r in refs if r.label == "CASE_CITATION"]
    citation_found = citations[0] if citations else "not identified"

    date_found = "not identified"
    for dpat in DATE_PATTERNS:
        dm = dpat.search(text)
        if dm:
            date_found = dm.group(1).strip()
            break

    return CaseMetadata(
        title=title_found,
        citation=citation_found,
        court=court_found,
        decision_date=date_found,
        parties=parties,
    )


def analyze_case_document(text: str, request_id: Optional[str] = None, include_spans: bool = True) -> CaseAnalysisResult:
    """Extract structured case analysis distinguishing party submissions from court findings."""
    doc = preprocess_text(text)
    metadata = extract_case_metadata(doc.normalized_text)

    facts: List[CaseItem] = []
    issues: List[CaseItem] = []
    cited_provisions: List[CaseItem] = []
    petitioner_args: List[CaseItem] = []
    respondent_args: List[CaseItem] = []
    court_reasoning: List[CaseItem] = []
    outcome_item = CaseItem(text="not identified", section="outcome")
    all_spans: List[EvidenceSpan] = []
    warnings: List[str] = []

    # Extract statutory section citations
    legal_refs = extract_legal_references(doc.normalized_text)
    for ref in legal_refs:
        span = EvidenceSpan(text=ref.text, start=ref.start, end=ref.end)
        cited_provisions.append(CaseItem(text=ref.text, evidence_span=span, section="provisions"))
        if include_spans:
            all_spans.append(span)

    # Classify sentences based on linguistic markers
    for sent in doc.sentences:
        s_text = sent.text
        span = EvidenceSpan(text=s_text, start=sent.start_char, end=sent.end_char)

        if s_text.lower().startswith("whether") or ("?" in s_text and len(s_text.split()) > 4):
            issues.append(CaseItem(text=s_text, evidence_span=span, section="issues"))
            if include_spans:
                all_spans.append(span)
            continue

        if any(p.search(s_text) for p in PETITIONER_SUBMISSION_PATTERNS):
            petitioner_args.append(CaseItem(text=s_text, evidence_span=span, section="petitioner_submissions"))
            if include_spans:
                all_spans.append(span)
            continue

        if any(p.search(s_text) for p in RESPONDENT_SUBMISSION_PATTERNS):
            respondent_args.append(CaseItem(text=s_text, evidence_span=span, section="respondent_submissions"))
            if include_spans:
                all_spans.append(span)
            continue

        if any(p.search(s_text) for p in OUTCOME_PATTERNS):
            outcome_item = CaseItem(text=s_text, evidence_span=span, section="outcome")
            if include_spans:
                all_spans.append(span)
            continue

        if any(p.search(s_text) for p in COURT_FINDING_PATTERNS):
            court_reasoning.append(CaseItem(text=s_text, evidence_span=span, section="court_reasoning"))
            if include_spans:
                all_spans.append(span)
            continue

        if any(w in s_text.lower() for w in ["complainant alleged", "prosecution case", "appellant was convicted", "incident occurred", "filed an application"]):
            facts.append(CaseItem(text=s_text, evidence_span=span, section="facts"))
            if include_spans:
                all_spans.append(span)

    # Key takeaways synthesis
    takeaways: List[str] = []
    if outcome_item.text != "not identified":
        takeaways.append(f"Outcome: {outcome_item.text}")
    if court_reasoning:
        takeaways.append(f"Primary Judicial Ground: {court_reasoning[0].text}")
    if issues:
        takeaways.append(f"Primary Question Considered: {issues[0].text}")

    if not takeaways:
        takeaways.append("Document provided preliminary narrative without explicit judicial determination.")

    if metadata.court == "not identified":
        warnings.append("Court jurisdiction could not be identified from the text.")
    if metadata.title == "not identified":
        warnings.append("Case title / party captions were not explicitly identified.")

    return CaseAnalysisResult(
        request_id=request_id,
        case_metadata=metadata,
        material_facts=facts,
        legal_issues=issues,
        cited_provisions=cited_provisions,
        party_arguments=PartyArguments(
            petitioner_arguments=petitioner_args,
            respondent_arguments=respondent_args,
        ),
        court_reasoning=court_reasoning,
        outcome=outcome_item,
        key_takeaways=takeaways,
        evidence_spans=all_spans,
        warnings=warnings,
    )


def extract_pdf_document(
    file_bytes: bytes,
    filename: str,
    request_id: str,
) -> DocumentExtractResponse:
    """Extract per-page text from a PDF file using PyMuPDF with size, security, and integrity checks."""
    clean_filename = os.path.basename(filename)

    # 1. Check size limit
    if len(file_bytes) > settings.max_pdf_size_bytes:
        raise ValueError(
            f"File size exceeds maximum allowed limit of {settings.max_pdf_size_bytes} bytes."
        )

    # 2. Check magic bytes
    if not file_bytes.startswith(b"%PDF"):
        raise ValueError("Invalid file format: Document does not contain valid PDF header.")

    # 3. Load with PyMuPDF
    doc = None
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
    except Exception as exc:
        raise ValueError(f"Corrupted or unreadable PDF document: {exc}") from exc

    try:
        # Check encryption
        if doc.is_encrypted:
            raise ValueError("Password protected or encrypted PDF documents are not supported.")

        # Check page count limit
        if doc.page_count > settings.max_pdf_pages:
            raise ValueError(
                f"PDF exceeds maximum page limit of {settings.max_pdf_pages} pages (has {doc.page_count} pages)."
            )

        pages: List[PageExtraction] = []
        text_parts: List[str] = []
        total_chars = 0

        for page_idx in range(doc.page_count):
            page = doc.load_page(page_idx)
            page_text = page.get_text("text").strip()
            page_len = len(page_text)
            total_chars += page_len
            pages.append(
                PageExtraction(
                    page_number=page_idx + 1,
                    text=page_text,
                    char_count=page_len,
                )
            )
            if page_text:
                text_parts.append(page_text)

        warnings: List[str] = []
        if total_chars < 20:
            warnings.append(
                "Scanned or image-only PDF detected (extracted text is empty or negligible). "
                "Optical Character Recognition (OCR) is not supported in Phase 1."
            )

        full_text = "\n\n".join(text_parts)

        return DocumentExtractResponse(
            request_id=request_id,
            filename=clean_filename,
            page_count=doc.page_count,
            total_characters=total_chars,
            pages=pages,
            extracted_text=full_text,
            warnings=warnings,
        )
    finally:
        if doc is not None:
            doc.close()
