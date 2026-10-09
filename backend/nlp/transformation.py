"""Bidirectional legal language transformation and fact-preservation verification."""

import re
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field

from nlp.entities import (
    ExtractedEntity,
    ExtractedFact,
    extract_all_facts,
    normalize_legal_term,
)
from nlp.preprocessing import (
    LEGAL_QUALIFIER_PATTERNS,
    NEGATION_PATTERNS,
    preprocess_text,
)
from nlp.retrieval import LegalTerm, load_legal_terms


class PreservationCheckItem(BaseModel):
    """Specific preservation audit line item."""
    category: str
    status: str  # "passed", "warning", "review_required"
    detail: str


class PreservationReport(BaseModel):
    """Comprehensive fact and semantic preservation audit report."""
    input_entities_count: int
    preserved_entities: List[str]
    unpreserved_entities: List[str]
    dates_preserved: bool
    amounts_preserved: bool
    negation_preserved: bool
    qualifiers_preserved: bool
    unsupported_additions_detected: List[str]
    checks: List[PreservationCheckItem]
    overall_status: str  # "passed_basic_checks", "warnings", "review_required"


# Controlled dictionary of plain-language substitutions for legal-to-normal mode
# Preserves meaning, negations, and conditions
LEGAL_TO_PLAIN_REPLACEMENTS = [
    (r"\bnotwithstanding\s+anything\s+contained\s+(?:herein|in\s+clause\s+\d+)?\b", "despite what is stated"),
    (r"\bnotwithstanding\b", "despite"),
    (r"\bherein(?:after)?\b", "in this document"),
    (r"\bheretofore\b", "before this time"),
    (r"\bhereunder\b", "under this agreement"),
    (r"\bhereof\b", "of this document"),
    (r"\baforementioned\b", "previously mentioned"),
    (r"\baforesaid\b", "mentioned earlier"),
    (r"\binter\s+alia\b", "among other things"),
    (r"\bin\s+the\s+event\s+(?:that|of)\b", "if"),
    (r"\bpursuant\s+to\b", "following"),
    (r"\bwith\s+immediate\s+effect\b", "immediately"),
    (r"\bis\s+liable\s+to\b", "is legally responsible to"),
    (r"\bliable\b", "responsible"),
    (r"\blessee\b", "tenant / renter"),
    (r"\blessor\b", "landlord / property owner"),
    (r"\bindemnify\s+and\s+hold\s+harmless\b", "compensate for any loss"),
    (r"\bnull\s+and\s+void\b", "invalid"),
    (r"\bshall\s+be\s+deemed\s+to\b", "will be considered to"),
    (r"\bsubject\s+to\s+the\s+provisions\s+of\b", "depending on the rules of"),
]


def get_term_dictionary() -> Dict[str, LegalTerm]:
    """Load and index legal terminology dictionary by normalized term."""
    terms = load_legal_terms()
    indexed: Dict[str, LegalTerm] = {}
    for t in terms:
        norm = normalize_legal_term(t.term)
        if norm:
            indexed[norm] = t
    return indexed


def lookup_term(term: str) -> Optional[LegalTerm]:
    """Lookup legal term in terminology dictionary with case/lemma normalization."""
    norm = normalize_legal_term(term)
    if not norm:
        return None
    dictionary = get_term_dictionary()

    # Exact normalized match
    if norm in dictionary:
        return dictionary[norm]

    # Simple suffix stripping for plurals or possessives
    if norm.endswith("s") and norm[:-1] in dictionary:
        return dictionary[norm[:-1]]
    if norm.endswith("es") and norm[:-2] in dictionary:
        return dictionary[norm[:-2]]

    return None


def find_terms_in_text(text: str) -> List[LegalTerm]:
    """Scan text for occurrences of cataloged legal terms."""
    dictionary = get_term_dictionary()
    matched_terms: List[LegalTerm] = []
    seen = set()
    lower_text = text.lower()

    for norm_term, term_obj in dictionary.items():
        if re.search(rf"\b{re.escape(norm_term)}\b", lower_text):
            if term_obj.term not in seen:
                seen.add(term_obj.term)
                matched_terms.append(term_obj)

    return matched_terms


def transform_legal_to_normal(text: str) -> Tuple[str, List[LegalTerm], List[str]]:
    """Transform legalistic language into plain language using conservative rule-based methods.

    Returns:
    - simplified_text: str
    - term_explanations: List[LegalTerm]
    - warnings: List[str]
    """
    doc = preprocess_text(text)
    simplified_sentences: List[str] = []
    warnings: List[str] = []

    # 1. Collect dictionary terms
    found_terms = find_terms_in_text(doc.normalized_text)

    # 2. Sentence-by-sentence conservative simplification
    for sent in doc.sentences:
        s_text = sent.text

        # Apply controlled plain-language lexical substitutions
        transformed = s_text
        for pattern, replacement in LEGAL_TO_PLAIN_REPLACEMENTS:
            transformed = re.sub(pattern, replacement, transformed, flags=re.IGNORECASE)

        # Simplify common legalese passives: "notice shall be served by X" -> "X must serve notice"
        # Keep modals strict: replace 'shall' with 'must' when indicating obligation
        transformed = re.sub(r"\bshall\b", "must", transformed, flags=re.IGNORECASE)

        # Clean up double spaces or awkward punctuation introduced by substitution
        transformed = re.sub(r"\s+", " ", transformed).strip()
        simplified_sentences.append(transformed)

    simplified_text = " ".join(simplified_sentences)

    warnings.append(
        "Rule-based plain-language baseline: Legal nuances, conditional exceptions, "
        "and statutory interpretations must be verified against original legal text."
    )

    if doc.has_negation:
        warnings.append("Input text contains explicit negative obligations or conditions which have been preserved.")

    return simplified_text, found_terms, warnings


def transform_normal_to_legal(text: str) -> Tuple[str, List[str], List[str]]:
    """Transform ordinary incident narrative into a structured formal legal-style draft.

    Draft is for human review only; never fabricates dates, amounts, parties, or citations.

    Returns:
    - draft_text: str
    - missing_details: List[str]
    - warnings: List[str]
    """
    doc = preprocess_text(text)
    extraction = extract_all_facts(doc.normalized_text)

    # Extract explicit entities and facts
    parties: List[str] = []
    dates: List[str] = []
    amounts: List[str] = []
    identifiers: List[str] = []

    for ent in extraction.entities:
        if ent.label in ("PERSON", "ROLE_COMPLAINANT", "ROLE_VICTIM", "ROLE_ACCUSED"):
            if ent.text not in parties:
                parties.append(ent.text)
        elif ent.label in ("DATE", "TIME"):
            if ent.text not in dates:
                dates.append(ent.text)
        elif ent.label == "MONEY":
            if ent.text not in amounts:
                amounts.append(ent.text)
        elif ent.label in ("EMAIL", "SOCIAL_HANDLE", "URL", "PHONE"):
            if ent.text not in identifiers:
                identifiers.append(f"{ent.label}: {ent.text}")

    # Identify missing essential details
    missing_details: List[str] = []
    if not dates:
        missing_details.append("Specific date(s) and time of occurrence are not stated in the narrative.")
    if not amounts and ("money" in text.lower() or "paid" in text.lower() or "lost" in text.lower()):
        missing_details.append("Exact monetary sum or transaction value is not quantified.")
    if not any("ROLE_ACCUSED" in e.label or e.label == "PERSON" for e in extraction.entities):
        missing_details.append("Identity, handle, or contact particulars of the respondent/perpetrator are unspecified.")
    if not identifiers and ("account" in text.lower() or "online" in text.lower() or "profile" in text.lower()):
        missing_details.append("Specific digital identifiers (e.g. account handle, email, platform URL) are not provided.")

    # Structure formal legal draft
    draft_lines: List[str] = [
        "FORMAL STATEMENT OF FACTS AND INCIDENT RECITATION (DRAFT FOR REVIEW ONLY)",
        "--------------------------------------------------------------------------------",
        "NOTICE: This draft is automatically formatted from stated facts for review by a licensed advocate.",
        "It does NOT constitute a finalized affidavit, formal complaint, or legally executed instrument.",
        "",
        "I. PARTIES AND IDENTIFIED ENTITIES:",
    ]

    if parties:
        for idx, p in enumerate(parties, 1):
            draft_lines.append(f"   {idx}. Stated Party / Role: {p}")
    else:
        draft_lines.append("   1. Aggrieved Party: [Name to be inserted - Complainant]")
        draft_lines.append("   2. Accused / Respondent: [Unknown Person / Particulars to be established]")

    if identifiers:
        draft_lines.append("\n   Digital / Account Identifiers Referenced:")
        for ident in identifiers:
            draft_lines.append(f"   - {ident}")

    draft_lines.append("\nII. CHRONOLOGICAL STATEMENT OF STATED FACTS:")

    # Enumerate stated sentences as numbered recitals
    for idx, sent in enumerate(doc.sentences, 1):
        draft_lines.append(f"   {idx}. That, as stated: \"{sent.text}\"")

    draft_lines.append("\nIII. MATERIAL ALLEGATIONS AND RESERVATION OF RIGHTS:")

    if extraction.consent_facts:
        for cf in extraction.consent_facts:
            draft_lines.append(f"   - Explicit lack of consent asserted: '{cf.evidence_span.text}'.")

    if extraction.intent_and_harm_facts:
        for hf in extraction.intent_and_harm_facts:
            draft_lines.append(f"   - Stated harm, threat, or intent: '{hf.evidence_span.text}'.")

    if amounts:
        for amt in amounts:
            draft_lines.append(f"   - Monetary loss / consideration stated: {amt}.")

    draft_lines.extend([
        "",
        "IV. FORMAL RESERVATION:",
        "   The aggrieved party expressly reserves all statutory rights and legal remedies available under",
        "   applicable law, subject to full evidentiary substantiation and formal legal verification.",
        "",
        "DRAFTED FOR HUMAN AND LEGAL COUNSEL REVIEW ONLY. DO NOT FILE WITHOUT ADVOCATE ENDORSEMENT.",
    ])

    draft_text = "\n".join(draft_lines)

    warnings: List[str] = [
        "Normal-to-legal transformation produces a structured preliminary draft only.",
        "No legal provisions, causes of action, or dates have been fabricated.",
        "A qualified legal professional must review, verify, and finalize this document.",
    ]

    return draft_text, missing_details, warnings


def run_preservation_checks(input_text: str, output_text: str) -> PreservationReport:
    """Compare input and output texts to audit fact and semantic preservation."""
    in_extraction = extract_all_facts(input_text)
    out_extraction = extract_all_facts(output_text)

    checks: List[PreservationCheckItem] = []
    overall_status = "passed_basic_checks"

    # 1. Audit Entities (Dates, Money, Persons, Identifiers)
    in_ents = {e.text.strip(): e for e in in_extraction.entities}
    out_text_lower = output_text.lower()

    preserved_ents: List[str] = []
    unpreserved_ents: List[str] = []

    for ent_text, ent in in_ents.items():
        if ent_text.lower() in out_text_lower:
            preserved_ents.append(ent_text)
        else:
            unpreserved_ents.append(ent_text)

    # Date preservation check
    in_dates = [e.text for e in in_extraction.entities if e.label in ("DATE", "TIME")]
    out_dates = [e.text for e in out_extraction.entities if e.label in ("DATE", "TIME")]
    dates_ok = all(d.lower() in out_text_lower for d in in_dates)

    if in_dates and not dates_ok:
        checks.append(PreservationCheckItem(
            category="dates",
            status="review_required",
            detail=f"Input date(s) {in_dates} were not fully found in output.",
        ))
        overall_status = "review_required"
    else:
        checks.append(PreservationCheckItem(
            category="dates",
            status="passed",
            detail="All input dates are preserved.",
        ))

    # Money preservation check
    in_money = [e.text for e in in_extraction.entities if e.label == "MONEY"]
    money_ok = all(m.lower() in out_text_lower for m in in_money)

    if in_money and not money_ok:
        checks.append(PreservationCheckItem(
            category="monetary_amounts",
            status="review_required",
            detail=f"Input monetary sum(s) {in_money} were not preserved in output.",
        ))
        overall_status = "review_required"
    else:
        checks.append(PreservationCheckItem(
            category="monetary_amounts",
            status="passed",
            detail="All input monetary amounts are preserved.",
        ))

    # Negation preservation check
    in_doc = preprocess_text(input_text)
    out_doc = preprocess_text(output_text)

    negation_ok = True
    if in_doc.has_negation and not out_doc.has_negation:
        negation_ok = False
        checks.append(PreservationCheckItem(
            category="negation",
            status="review_required",
            detail="Input contained explicit negation markers that were omitted in output.",
        ))
        overall_status = "review_required"
    else:
        checks.append(PreservationCheckItem(
            category="negation",
            status="passed",
            detail="Negation status preserved.",
        ))

    # Legal qualifiers preservation check (unless, except, provided that, subject to)
    qualifiers_ok = True
    for q in in_doc.legal_qualifiers:
        if q.matched_text.lower() not in out_text_lower:
            # Check if equivalent plain meaning exists
            if q.qualifier_type in ("notwithstanding", "subject_to"):
                if "despite" not in out_text_lower and "depending" not in out_text_lower:
                    qualifiers_ok = False
            else:
                qualifiers_ok = False

    if not qualifiers_ok:
        checks.append(PreservationCheckItem(
            category="legal_qualifiers",
            status="warning",
            detail="One or more conditional legal qualifiers may have had phrasing altered.",
        ))
        if overall_status != "review_required":
            overall_status = "warnings"
    else:
        checks.append(PreservationCheckItem(
            category="legal_qualifiers",
            status="passed",
            detail="Essential legal qualifiers and conditions preserved.",
        ))

    # Check for unsupported additions in output (invented money or dates)
    unsupported_additions: List[str] = []
    # If output has new monetary sums not mentioned in input
    for om in [e.text for e in out_extraction.entities if e.label == "MONEY"]:
        if om.lower() not in input_text.lower():
            unsupported_additions.append(f"Invented monetary sum: {om}")

    if unsupported_additions:
        checks.append(PreservationCheckItem(
            category="unsupported_additions",
            status="review_required",
            detail="; ".join(unsupported_additions),
        ))
        overall_status = "review_required"

    return PreservationReport(
        input_entities_count=len(in_extraction.entities),
        preserved_entities=preserved_ents,
        unpreserved_entities=unpreserved_ents,
        dates_preserved=dates_ok,
        amounts_preserved=money_ok,
        negation_preserved=negation_ok,
        qualifiers_preserved=qualifiers_ok,
        unsupported_additions_detected=unsupported_additions,
        checks=checks,
        overall_status=overall_status,
    )
