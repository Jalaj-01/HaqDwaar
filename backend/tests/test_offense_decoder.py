"""Regression and functional tests for Module 1: Legal Offense Decoder."""

from fastapi.testclient import TestClient
import pytest

from config import FIXTURES_DIR, settings
from modules.offense_decoder import (
    ContextualAnswer,
    OffenseAnalysisRequest,
    analyze_incident,
)
from nlp.legal_matching import ElementStatus
from nlp.retrieval import LegalCorpusIndex, load_legal_provisions

SYNTHETIC_FIXTURE_PATH = FIXTURES_DIR / "synthetic_provisions.json"


@pytest.fixture
def synthetic_index() -> LegalCorpusIndex:
    provisions = load_legal_provisions(SYNTHETIC_FIXTURE_PATH)
    return LegalCorpusIndex(provisions)


def test_empty_corpus_analysis():
    """Analysis on empty corpus must safely return no_reliable_match=True without error."""
    empty_index = LegalCorpusIndex([])
    req = OffenseAnalysisRequest(
        incident_text="Someone created a fake profile with my photos without my permission."
    )
    res = analyze_incident(req, request_id="req-test-1", custom_index=empty_index)

    assert res.request_id == "req-test-1"
    assert res.no_reliable_match is True
    assert res.candidate_provisions == []
    assert len(res.extracted_facts) > 0
    assert len(res.incident_categories) > 0
    assert res.disclaimer != ""
    assert len(res.uncertainty_notes) > 0


def test_synthetic_offense_analysis(synthetic_index: LegalCorpusIndex):
    """Incident analysis on synthetic corpus matches provisions and evaluates elements."""
    incident = "Someone created a fake account using my name and uploaded my photos without my permission."
    req = OffenseAnalysisRequest(incident_text=incident, top_k=3)
    res = analyze_incident(req, request_id="req-test-2", custom_index=synthetic_index)

    assert res.no_reliable_match is False
    assert len(res.candidate_provisions) > 0

    top_cand = res.candidate_provisions[0]
    assert top_cand.relevance_score > 0.0

    # Element match verification
    elem_statuses = {em.element_id: em.status for em in top_cand.element_matches}

    # Absence of consent element SYN_E3 should be SUPPORTED
    if "SYN_E3" in elem_statuses:
        assert elem_statuses["SYN_E3"] == ElementStatus.SUPPORTED
        em_e3 = next(em for em in top_cand.element_matches if em.element_id == "SYN_E3")
        assert len(em_e3.evidence_spans) > 0
        assert "permission" in em_e3.evidence_spans[0].text.lower()


def test_missing_facts_are_never_contradictions(synthetic_index: LegalCorpusIndex):
    """Missing factual details must be evaluated as NOT_ESTABLISHED, never CONTRADICTED."""
    incident = "Someone created a profile online."
    req = OffenseAnalysisRequest(incident_text=incident, top_k=2)
    res = analyze_incident(req, request_id="req-test-3", custom_index=synthetic_index)

    for cand in res.candidate_provisions:
        for em in cand.element_matches:
            # Missing facts must NOT be marked contradicted
            if em.status == ElementStatus.CONTRADICTED:
                assert False, f"Element {em.element_id} was improperly marked CONTRADICTED"


def test_explicit_affirmative_consent_contradiction(synthetic_index: LegalCorpusIndex):
    """If user explicitly states they gave permission, absence-of-consent element is CONTRADICTED."""
    incident = "A colleague published my photos with my prior permission."
    req = OffenseAnalysisRequest(incident_text=incident, top_k=2)
    res = analyze_incident(req, request_id="req-test-4", custom_index=synthetic_index)

    # In S1 or S2, absence of consent should be contradicted
    all_elements = [
        em for cand in res.candidate_provisions for em in cand.element_matches
    ]
    consent_elems = [
        em for em in all_elements if "consent" in em.description.lower() or "permission" in em.description.lower()
    ]
    assert len(consent_elems) > 0
    assert any(em.status == ElementStatus.CONTRADICTED for em in consent_elems)


def test_contextual_answers_integration(synthetic_index: LegalCorpusIndex):
    """Contextual answers provided by the user must update unestablished elements to SUPPORTED."""
    incident = "Someone is harassing me online."
    req = OffenseAnalysisRequest(
        incident_text=incident,
        contextual_answers=[
            ContextualAnswer(
                question_id="Q_SYNTHETIC_ACT_S1_SYN_E1",
                answer="Yes, an unauthorized profile was created in my name on Instagram",
            )
        ],
        top_k=2,
    )
    res = analyze_incident(req, request_id="req-test-5", custom_index=synthetic_index)

    cand_s1 = next((c for c in res.candidate_provisions if c.provision_id == "SYNTHETIC_ACT_S1"), None)
    if cand_s1:
        e1_match = next((em for em in cand_s1.element_matches if em.element_id == "SYN_E1"), None)
        assert e1_match is not None
        assert e1_match.status == ElementStatus.SUPPORTED
        assert e1_match.evaluation_origin == "contextual_answer"


def test_offense_analyze_http_endpoint(client: TestClient):
    """POST /api/v1/offense/analyze must return 200 with complete response shape."""
    payload = {
        "incident_text": "Someone created a fake social media account and posted photos.",
        "top_k": 3,
    }
    response = client.post("/api/v1/offense/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert "request_id" in data
    assert "extracted_facts" in data
    assert "incident_categories" in data
    assert "candidate_provisions" in data
    assert "follow_up_questions" in data
    assert "disclaimer" in data
    assert "no_reliable_match" in data


def test_oversized_input_rejected_via_api(client: TestClient):
    """Input exceeding max_text_length must be rejected with 400 Bad Request."""
    oversized = "a" * (settings.max_text_length + 50)
    response = client.post("/api/v1/offense/analyze", json={"incident_text": oversized})
    assert response.status_code == 400
    data = response.json()
    assert data["error"]["code"] == "BAD_REQUEST"


def test_invalid_top_k_rejected(client: TestClient):
    """Top_k out of allowed bounds (1-20) must return 422 VALIDATION_ERROR."""
    response = client.post(
        "/api/v1/offense/analyze",
        json={"incident_text": "Valid incident description", "top_k": 50},
    )
    assert response.status_code == 422
    data = response.json()
    assert data["error"]["code"] == "VALIDATION_ERROR"
