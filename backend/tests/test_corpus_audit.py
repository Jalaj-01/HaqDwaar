"""Comprehensive QA regression and audit tests for the verified legal corpus and API."""

import io
from pathlib import Path
from fastapi.testclient import TestClient
import pytest

from config import LEGAL_PROVISIONS_PATH, LEGAL_TERMS_PATH
from modules.offense_decoder import OffenseAnalysisRequest, analyze_incident
from nlp.retrieval import (
    CandidateProvision,
    LegalCorpusIndex,
    LegalElement,
    LegalProvision,
    LegalTerm,
    get_corpus_status_info,
    load_legal_provisions,
    load_legal_terms,
)


def test_production_corpus_schema_and_validity():
    """All production records must strictly satisfy LegalProvision and LegalTerm schemas."""
    # 1. Statutory Provisions
    provisions = load_legal_provisions(LEGAL_PROVISIONS_PATH)
    assert len(provisions) >= 15, f"Expected at least 15 provisions, got {len(provisions)}"

    ids_seen = set()
    verified_count = 0
    unverified_count = 0

    for p in provisions:
        # Unique IDs
        assert p.id not in ids_seen, f"Duplicate provision ID: {p.id}"
        ids_seen.add(p.id)

        # No synthetic or test fixture data in production
        assert "SYNTHETIC" not in p.id.upper(), f"Synthetic ID in production corpus: {p.id}"
        assert "SYNTHETIC" not in p.act_name.upper(), f"Synthetic act in production corpus: {p.act_name}"
        assert "example.gov.in" not in p.official_source_url, f"Placeholder URL in production: {p.official_source_url}"

        # Verified URL check
        assert (
            p.official_source_url.startswith("https://www.indiacode.nic.in")
            or p.official_source_url.startswith("https://egazette.gov.in")
        ), f"Invalid official source URL for {p.id}: {p.official_source_url}"

        # Required fields present
        assert p.act_name.strip()
        assert p.section_id.strip()
        assert p.title.strip()
        assert p.source_text.strip()
        assert p.plain_language_summary.strip()
        assert len(p.legal_elements) > 0

        # Verified status tracking
        if p.source_verified:
            verified_count += 1
            assert p.verified_at is not None
            assert p.source_authority.strip()
        else:
            unverified_count += 1

    assert verified_count >= 15
    assert unverified_count >= 1  # Audit fixture explicitly checks unverified handling

    # 2. Terminology Records
    terms = load_legal_terms(LEGAL_TERMS_PATH)
    assert len(terms) >= 20, f"Expected at least 20 legal terms, got {len(terms)}"

    terms_seen = set()
    for t in terms:
        assert t.term not in terms_seen, f"Duplicate term: {t.term}"
        terms_seen.add(t.term)
        assert t.plain_language_meaning.strip()
        assert t.verification_status in ["verified", "unverified"]
        assert t.source is not None and t.source.strip()


def test_isolated_empty_corpus_behavior(tmp_path: Path):
    """An empty corpus must return clean no-reliable-match without crashing or hallucinating."""
    empty_file = tmp_path / "empty_provisions.json"
    empty_file.write_text("[]", encoding="utf-8")

    empty_provisions = load_legal_provisions(empty_file)
    empty_index = LegalCorpusIndex(empty_provisions)

    # Retrieval returns empty list
    results = empty_index.retrieve("Someone hacked my account and demanded money.")
    assert results == []

    # Offense analysis returns truthful no-match state
    req = OffenseAnalysisRequest(
        incident_text="Someone hacked my account and demanded money.",
        top_k=5,
    )
    analysis = analyze_incident(req, request_id="empty-test-1", custom_index=empty_index)

    assert analysis.no_reliable_match is True
    assert analysis.no_reliable_match_explanation is not None
    assert "No candidate provisions met the minimum relevance threshold" in analysis.no_reliable_match_explanation
    assert len(analysis.candidate_provisions) == 0


def test_isolated_unverified_only_corpus_behavior():
    """Unverified provisions must NEVER display penalty text in CandidateProvision results."""
    unverified_prov = LegalProvision(
        id="TEST_UNVERIFIED_S1",
        jurisdiction="India",
        act_name="Test Provisional Statute 2026",
        section_id="Section 1",
        title="Unauthorized Interception",
        source_text="Whoever intercepts digital transmissions commits unauthorized interception.",
        plain_language_summary="Intercepting digital messages without authority.",
        legal_elements=[
            LegalElement(
                element_id="ELEM_1",
                description="Intercepting digital transmission",
                keywords=["intercepted", "digital", "messages"],
            )
        ],
        penalty_text="Unverified penalty of imprisonment up to 5 years.",
        official_source_url="https://www.indiacode.nic.in/handle/123456789/1999",
        source_authority="Provisional draft authority",
        source_verified=False,
        version_label="draft",
    )

    unverified_index = LegalCorpusIndex([unverified_prov])
    candidates = unverified_index.retrieve("intercepted digital messages without authority", min_score=0.0)

    assert len(candidates) == 1
    cand = candidates[0]
    assert cand.provision.source_verified is False
    # STRICT PENALTY SUPPRESSION:
    assert cand.penalty_displayed is None

    # Offense analysis integration
    req = OffenseAnalysisRequest(
        incident_text="The perpetrator intercepted digital messages without authority.",
        top_k=5,
    )
    analysis = analyze_incident(req, request_id="unver-test-1", custom_index=unverified_index)
    assert len(analysis.candidate_provisions) == 1
    assert analysis.candidate_provisions[0].source_verified is False
    assert analysis.candidate_provisions[0].penalty_displayed is None


def test_irrelevant_query_cutoff():
    """Irrelevant queries must respect relevance cutoff and return no_reliable_match."""
    index = LegalCorpusIndex(load_legal_provisions(LEGAL_PROVISIONS_PATH))

    irrelevant_text = "astrophysics quantum telescope galactic nebula cosmic radiation observatory"
    candidates = index.retrieve(irrelevant_text)
    assert len(candidates) == 0

    req = OffenseAnalysisRequest(incident_text=irrelevant_text, top_k=5)
    analysis = analyze_incident(req, request_id="irrel-test-1", custom_index=index)

    assert analysis.no_reliable_match is True
    assert analysis.no_reliable_match_explanation is not None
    assert len(analysis.candidate_provisions) == 0


def test_relevant_queries_retrieve_expected_provisions():
    """Realistic incident descriptions retrieve appropriate verified provisions."""
    index = LegalCorpusIndex(load_legal_provisions(LEGAL_PROVISIONS_PATH))

    # 1. Identity Theft
    q_id_theft = "A cybercriminal stole my electronic signature, login password, and OTP credentials to access my bank account."
    cand_id_theft = index.retrieve(q_id_theft, top_k=3)
    retrieved_ids = [c.provision.id for c in cand_id_theft]
    assert "ITA_2000_S66C" in retrieved_ids
    match_66c = next(c for c in cand_id_theft if c.provision.id == "ITA_2000_S66C")
    assert match_66c.provision.source_verified is True
    assert match_66c.penalty_displayed is not None
    assert "three years" in match_66c.penalty_displayed

    # 2. Privacy Violation / Intimate Images
    q_privacy = "Someone secretly recorded and transmitted intimate photos of my private areas without my consent."
    cand_privacy = index.retrieve(q_privacy, top_k=3)
    retrieved_privacy_ids = [c.provision.id for c in cand_privacy]
    assert "ITA_2000_S66E" in retrieved_privacy_ids
    match_66e = next(c for c in cand_privacy if c.provision.id == "ITA_2000_S66E")
    assert match_66e.provision.source_verified is True
    assert match_66e.penalty_displayed is not None

    # 3. Cyber Stalking
    q_stalking = "A man has been repeatedly messaging me despite my clear refusal, and tracking my email and online activity."
    cand_stalking = index.retrieve(q_stalking, top_k=3)
    retrieved_stalking_ids = [c.provision.id for c in cand_stalking]
    assert "BNS_2023_S78" in retrieved_stalking_ids or "IPC_1860_S354D" in retrieved_stalking_ids


def test_api_endpoints_compatibility(client: TestClient):
    """All exposed API routes must remain compatible with expected schemas and error shapes."""
    # 1. GET /health
    r_health = client.get("/health")
    assert r_health.status_code == 200
    assert r_health.json()["status"] == "ok"

    # 2. GET /api/v1/status
    r_status = client.get("/api/v1/status")
    assert r_status.status_code == 200
    status_data = r_status.json()
    assert "corpus_record_count" in status_data
    assert "verified_record_count" in status_data
    assert status_data["corpus_record_count"] >= 15
    assert status_data["verified_record_count"] >= 15
    assert status_data["corpus_status"] in ["loaded", "partial_unverified"]

    # 3. POST /api/v1/offense/analyze
    r_offense = client.post(
        "/api/v1/offense/analyze",
        json={"incident_text": "Someone stole my password and used it dishonestly.", "top_k": 3},
    )
    assert r_offense.status_code == 200
    offense_data = r_offense.json()
    assert "candidate_provisions" in offense_data
    assert "disclaimer" in offense_data
    assert "extracted_facts" in offense_data
    assert "follow_up_questions" in offense_data

    # 4. POST /api/v1/legal-language/transform
    r_trans = client.post(
        "/api/v1/legal-language/transform",
        json={"text": "Notwithstanding clause 1, the lessee shall pay Rs. 10,000.", "mode": "legal_to_normal"},
    )
    assert r_trans.status_code == 200
    trans_data = r_trans.json()
    assert "transformed_text" in trans_data
    assert "preservation_checks" in trans_data

    # 5. GET /api/v1/legal-language/terms/{term}
    r_term = client.get("/api/v1/legal-language/terms/mens rea")
    assert r_term.status_code == 200
    assert r_term.json()["term"] == "mens rea"
    assert r_term.json()["verification_status"] == "verified"

    # 6. POST /api/v1/legal-language/analyze-case
    r_case = client.post(
        "/api/v1/legal-language/analyze-case",
        json={
            "text": (
                "IN THE HIGH COURT OF DELHI AT NEW DELHI\n"
                "CRL.M.C. 101/2026\n"
                "ABC ... Petitioner\nVersus\nState & Anr. ... Respondents\n"
                "CORAM: HON'BLE MR. JUSTICE X\n"
                "The petitioner filed this petition seeking quashing of FIR.\n"
                "In the result, the petition is dismissed."
            ),
            "include_spans": True,
        },
    )
    assert r_case.status_code == 200
    case_data = r_case.json()
    assert "court" in case_data["case_metadata"]
    assert "outcome" in case_data

    # 7. POST /api/v1/documents/extract
    dummy_pdf_bytes = b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF"
    r_doc = client.post(
        "/api/v1/documents/extract",
        files={"file": ("sample.pdf", io.BytesIO(dummy_pdf_bytes), "application/pdf")},
    )
    assert r_doc.status_code == 200
    doc_data = r_doc.json()
    assert "filename" in doc_data
    assert "extracted_text" in doc_data
