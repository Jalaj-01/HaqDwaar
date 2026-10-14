"""Unit tests for NLP preprocessing and entity/fact extraction pipeline."""

import pytest

from nlp.entities import (
    FactOrigin,
    extract_all_facts,
    extract_consent_facts,
    extract_digital_identifiers,
    extract_legal_references,
    normalize_legal_term,
)
from nlp.preprocessing import (
    NonEnglishInputError,
    detect_english_only,
    normalize_text,
    preprocess_text,
)


def test_empty_input_rejected():
    """Empty or whitespace-only input must raise ValueError."""
    with pytest.raises(ValueError, match="Input text must not be empty"):
        preprocess_text("")

    with pytest.raises(ValueError, match="Input text must not be empty"):
        preprocess_text("   \n\t   ")


def test_non_english_input_rejected():
    """Predominantly non-English text must be detected and rejected."""
    hindi_text = "किसी ने मेरे नाम से फर्जी सोशल मीडिया अकाउंट बनाया।"
    with pytest.raises(NonEnglishInputError, match="Phase 1 supports English-language input only"):
        preprocess_text(hindi_text)


def test_unicode_and_whitespace_normalization():
    """Unicode variants and abnormal whitespaces should be cleanly normalized."""
    raw = "The\u00A0tenant   shall pay\r\n\r\nrent on  time."
    doc = preprocess_text(raw)
    assert doc.normalized_text == "The tenant shall pay\n\nrent on time."
    assert len(doc.sentences) >= 1


def test_preservation_of_negation():
    """Negation tokens must never be stripped and must record exact spans."""
    text = "The borrower did not pay the installment and never responded."
    doc = preprocess_text(text)
    assert doc.has_negation is True
    assert len(doc.negation_spans) >= 2

    # Check offsets
    for span in doc.negation_spans:
        assert doc.normalized_text[span["start_char"]:span["end_char"]].lower() in [
            "not", "never", "no", "without"
        ]


def test_preservation_of_legal_qualifications():
    """Legal qualifications must be tracked with exact character spans."""
    text = (
        "Notwithstanding anything contained in clause 2, the license is granted "
        "subject to inspection, unless revoked earlier, provided that notice is served."
    )
    doc = preprocess_text(text)
    qualifiers = [q.qualifier_type for q in doc.legal_qualifiers]

    assert "notwithstanding" in qualifiers
    assert "subject_to" in qualifiers
    assert "conditional_unless" in qualifiers
    assert "provided_that" in qualifiers

    # Verify spans match normalized text verbatim
    for q in doc.legal_qualifiers:
        extracted = doc.normalized_text[q.start_char:q.end_char]
        assert extracted.lower() in text.lower()


def test_modals_preservation():
    """Obligation and discretion modals must be tracked."""
    text = "The tenant shall maintain the premises, but may request repairs, and must give notice."
    doc = preprocess_text(text)
    assert "shall" in doc.modals_present
    assert "may" in doc.modals_present
    assert "must" in doc.modals_present


def test_entity_and_fact_extraction_evidence_spans():
    """Extracted facts must be grounded in exact evidence spans with origin=stated."""
    incident = (
        "Someone created a fake social media account using my name and "
        "uploaded my photos without my permission."
    )
    result = extract_all_facts(incident)

    # Consent fact check
    assert len(result.consent_facts) >= 1
    consent_fact = result.consent_facts[0]
    assert consent_fact.origin == FactOrigin.STATED
    assert "without my permission" in consent_fact.evidence_span.text.lower()
    span = consent_fact.evidence_span
    assert incident[span.start:span.end].lower() == consent_fact.evidence_span.text.lower()

    # Action facts check
    assert len(result.facts) > 0
    for fact in result.facts:
        assert fact.origin in (FactOrigin.STATED, FactOrigin.RULE_EXTRACTED)
        # Ensure evidence span is valid within text bounds
        assert 0 <= fact.evidence_span.start < fact.evidence_span.end <= len(incident)


def test_digital_identifiers_and_money_extraction():
    """Extraction of online identifiers, handles, and monetary sums."""
    text = (
        "User @hacker_99 sent an extortion message to victim@example.com "
        "demanding Rs. 50,000 via http://fraud-portal.com/pay"
    )
    result = extract_all_facts(text)

    labels = {e.label: e.text for e in result.entities}
    assert "SOCIAL_HANDLE" in labels
    assert "@hacker_99" in labels["SOCIAL_HANDLE"]

    assert "EMAIL" in labels
    assert labels["EMAIL"] == "victim@example.com"

    assert "URL" in labels
    assert "http://fraud-portal.com/pay" in labels["URL"]

    assert "MONEY" in labels
    assert "50,000" in labels["MONEY"]


def test_statutory_and_citation_extraction():
    """Extraction of statutory sections and formal legal citations."""
    text = (
        "The applicant invoked Section 66C of the IT Act and Section 420 IPC, "
        "relying on AIR 2021 SC 105."
    )
    refs = extract_legal_references(text)
    labels = [r.label for r in refs]
    assert "STATUTE_SECTION" in labels
    assert "CASE_CITATION" in labels

    citation = next(r for r in refs if r.label == "CASE_CITATION")
    assert citation.text == "AIR 2021 SC 105"


def test_legal_term_normalization():
    """Term normalization must handle whitespace, casing, and trailing punctuation."""
    assert normalize_legal_term("  Notwithstanding  ") == "notwithstanding"
    assert normalize_legal_term('"Lessee"') == "lessee"
    assert normalize_legal_term("herein,") == "herein"
    assert normalize_legal_term("") == ""
