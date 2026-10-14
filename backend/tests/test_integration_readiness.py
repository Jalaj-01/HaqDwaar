"""Comprehensive integration readiness tests covering all 8 Critical User Journeys."""

import io
from fastapi.testclient import TestClient
import fitz
import pytest


def test_journey_1_offense_analysis_submission(client: TestClient):
    """Journey 1: Submit an incident description and receive structured offense analysis."""
    payload = {
        "incident_text": "Someone intercepted my net banking OTP and used my electronic signature without permission to transfer funds.",
        "top_k": 5,
    }
    resp = client.post("/api/v1/offense/analyze", json=payload)
    assert resp.status_code == 200
    data = resp.json()

    assert "request_id" in data and len(data["request_id"]) > 0
    assert "extracted_facts" in data and len(data["extracted_facts"]) > 0
    assert "incident_categories" in data and len(data["incident_categories"]) > 0
    assert "candidate_provisions" in data and len(data["candidate_provisions"]) > 0
    assert "follow_up_questions" in data
    assert "uncertainty_notes" in data and len(data["uncertainty_notes"]) > 0
    assert "disclaimer" in data and "not constitute formal legal advice" in data["disclaimer"]
    assert data["no_reliable_match"] is False


def test_journey_2_provision_display_with_provenance_and_explanation(client: TestClient):
    """Journey 2: Display matched legal provisions with correct section, act, explanation, and provenance."""
    payload = {
        "incident_text": "Someone logged into my work email account using stolen credentials and sent offensive emails.",
        "top_k": 3,
    }
    resp = client.post("/api/v1/offense/analyze", json=payload)
    assert resp.status_code == 200
    data = resp.json()

    top_cand = data["candidate_provisions"][0]
    # Act, Section, Title
    assert top_cand["act_name"] in ["Information Technology Act, 2000", "Bharatiya Nyaya Sanhita, 2023", "Indian Penal Code, 1860"]
    assert len(top_cand["section_id"]) > 0
    assert len(top_cand["title"]) > 0
    assert len(top_cand["jurisdiction"]) > 0

    # Provenance fields
    assert top_cand["official_source_url"].startswith("http")
    assert len(top_cand["source_authority"]) > 0
    assert isinstance(top_cand["source_verified"], bool)
    assert len(top_cand["version_label"]) > 0
    assert len(top_cand["plain_language_summary"]) > 0

    # Grounded explanation and element matches
    assert len(top_cand["explanation"]) > 0
    assert "relevance score" in top_cand["explanation"].lower()
    assert len(top_cand["element_matches"]) > 0
    for em in top_cand["element_matches"]:
        assert em["status"] in ["supported", "not_established", "contradicted"]


def test_journey_3_unverified_provision_penalty_suppression(client: TestClient):
    """Journey 3: Handle unverified provisions without displaying unsupported penalties."""
    payload = {
        "incident_text": "The data fiduciary failed to implement security safeguards resulting in significant personal data breach.",
        "top_k": 5,
    }
    resp = client.post("/api/v1/offense/analyze", json=payload)
    assert resp.status_code == 200
    data = resp.json()

    # Find the provisional audit fixture if retrieved
    dpdp_matches = [c for c in data["candidate_provisions"] if c["provision_id"] == "DPDP_2023_S33_PROVISIONAL"]
    if dpdp_matches:
        dpdp = dpdp_matches[0]
        assert dpdp["source_verified"] is False
        assert dpdp["penalty_displayed"] is None  # Penalty MUST be suppressed
        assert len(dpdp["official_source_url"]) > 0
        assert any("preliminary hypotheses" in n for n in data["uncertainty_notes"])


def test_journey_4_low_confidence_and_legitimate_no_match(client: TestClient):
    """Journey 4: Handle low-confidence results and legitimate out-of-scope no-match cases."""
    payload = {
        "incident_text": "astrophysics quantum telescope galactic nebula cosmic radiation observatory deep space research",
        "top_k": 5,
    }
    resp = client.post("/api/v1/offense/analyze", json=payload)
    assert resp.status_code == 200
    data = resp.json()

    assert data["no_reliable_match"] is True
    assert len(data["candidate_provisions"]) == 0
    assert data["no_reliable_match_explanation"] is not None
    assert "No candidate provisions met the minimum relevance threshold" in data["no_reliable_match_explanation"]


def test_journey_5_input_validation_and_malformed_requests(client: TestClient):
    """Journey 5: Handle invalid input, empty input, oversized input, and malformed requests."""
    # 1. Empty string
    r1 = client.post("/api/v1/offense/analyze", json={"incident_text": "   "})
    assert r1.status_code == 400
    assert r1.json()["error"]["code"] == "BAD_REQUEST"

    # 2. Oversized text (> 20000 chars)
    r2 = client.post("/api/v1/offense/analyze", json={"incident_text": "a" * 20001})
    assert r2.status_code == 400
    assert r2.json()["error"]["code"] == "BAD_REQUEST"
    assert "exceeds maximum allowed length" in r2.json()["error"]["message"]

    # 3. Non-English text (Devanagari script triggers NonEnglishInputError)
    r3 = client.post("/api/v1/offense/analyze", json={"incident_text": "किसी ने मेरे नाम से फर्जी सोशल मीडिया अकाउंट बनाया।"})
    assert r3.status_code == 400
    assert "Phase 1 supports English-language input only" in r3.json()["error"]["message"]

    # 4. Invalid top_k (ge=1, le=20)
    r4 = client.post("/api/v1/offense/analyze", json={"incident_text": "Valid incident description", "top_k": 25})
    assert r4.status_code == 422
    assert r4.json()["error"]["code"] == "VALIDATION_ERROR"

    # 5. Missing required fields
    r5 = client.post("/api/v1/offense/analyze", json={})
    assert r5.status_code == 422
    assert r5.json()["error"]["code"] == "VALIDATION_ERROR"

    # 6. Non-PDF upload
    r6 = client.post("/api/v1/documents/extract", files={"file": ("notes.txt", b"plain text", "text/plain")})
    assert r6.status_code == 415
    assert r6.json()["error"]["code"] == "UNSUPPORTED_MEDIA_TYPE"

    # 7. Fake PDF (invalid magic bytes)
    r7 = client.post("/api/v1/documents/extract", files={"file": ("fake.pdf", b"NOT_A_PDF_STREAM", "application/pdf")})
    assert r7.status_code == 415
    assert "header missing" in r7.json()["error"]["message"]


def test_journey_6_error_envelope_and_request_id_tracking(client: TestClient):
    """Journey 6: Handle API failures and non-existent endpoints with consistent error envelope."""
    # 404 Not Found
    resp = client.get("/api/v1/nonexistent/endpoint")
    assert resp.status_code == 404
    data = resp.json()
    assert "error" in data
    assert data["error"]["code"] == "NOT_FOUND"
    assert "request_id" in data["error"]
    assert resp.headers.get("X-Request-ID") == data["error"]["request_id"]

    # 404 Legal Term Not Found
    term_resp = client.get("/api/v1/legal-language/terms/unknown_arbitrary_term_999")
    assert term_resp.status_code == 404
    assert term_resp.json()["error"]["code"] == "NOT_FOUND"

    # 405 Method Not Allowed
    m_resp = client.post("/health")
    assert m_resp.status_code == 405
    assert m_resp.json()["error"]["code"] == "METHOD_NOT_ALLOWED"


def test_journey_7_contract_readiness_for_ui_states(client: TestClient):
    """Journey 7: Verify backend response fields adequately support loading, empty, and retry UI states."""
    # Status endpoint for initial app loading / system check
    st_resp = client.get("/api/v1/status")
    assert st_resp.status_code == 200
    st_data = st_resp.json()
    assert "component_readiness" in st_data
    assert st_data["component_readiness"]["api"] == "ready"
    assert st_data["component_readiness"]["retrieval_engine"] == "ready"
    assert "configured_limits" in st_data

    # Contextual answers follow-up workflow (retry / refinement state)
    follow_up_payload = {
        "incident_text": "Someone intercepted my OTP and took money.",
        "contextual_answers": [
            {
                "question_id": "Q_ITA_2000_S66C_ELEM_1",
                "answer": "Yes, they used my net banking password and OTP without my permission.",
            }
        ],
    }
    fu_resp = client.post("/api/v1/offense/analyze", json=follow_up_payload)
    assert fu_resp.status_code == 200
    fu_data = fu_resp.json()
    assert len(fu_data["candidate_provisions"]) > 0


def test_journey_8_disclaimer_and_no_definitive_legal_advice(client: TestClient):
    """Journey 8: Confirm API does not invent legal claims or present uncertain results as legal advice."""
    payload = {
        "incident_text": "A man followed me from work to my home for three days and sent me unwanted messages.",
    }
    resp = client.post("/api/v1/offense/analyze", json=payload)
    assert resp.status_code == 200
    data = resp.json()

    # Statutory disclaimer must be explicit
    assert "disclaimer" in data
    assert "educational, informational, and preliminary research purposes only" in data["disclaimer"]
    assert "Consult a licensed legal advocate" in data["disclaimer"]

    # Uncertainty notes must emphasize hypotheses
    notes = " ".join(data["uncertainty_notes"])
    assert "preliminary hypotheses" in notes
    assert "does not assert guilt" in notes

    # Candidate explanations must describe legal elements neutrally
    for cand in data["candidate_provisions"]:
        assert not any(word in cand["explanation"].lower() for word in ["guilty", "convicted", "criminal liability established"])


def test_module_2_transformations_and_case_analysis(client: TestClient):
    """Module 2 journeys: legal_to_normal, normal_to_legal, term lookup, and case analysis."""
    # 1. Legal to Normal
    l2n = client.post(
        "/api/v1/legal-language/transform",
        json={
            "text": "The lessee shall forthwith vacate the demised premises upon expiry of the lease.",
            "mode": "legal_to_normal",
        },
    )
    assert l2n.status_code == 200
    assert "must" in l2n.json()["transformed_text"].lower() or "vacate" in l2n.json()["transformed_text"].lower()
    assert l2n.json()["preservation_checks"]["overall_status"] in ["passed_basic_checks", "warnings"]

    # 2. Normal to Legal
    n2l = client.post(
        "/api/v1/legal-language/transform",
        json={
            "text": "The tenant did not pay rent of fifteen thousand rupees on 1st March 2024 and refused to leave.",
            "mode": "normal_to_legal",
        },
    )
    assert n2l.status_code == 200
    assert "RECITALS" in n2l.json()["transformed_text"] or "NOTICE" in n2l.json()["transformed_text"]

    # 3. Term Lookup
    term_res = client.get("/api/v1/legal-language/terms/mens rea")
    assert term_res.status_code == 200
    assert term_res.json()["term"].lower() == "mens rea"
    assert "guilty mind" in term_res.json()["plain_language_meaning"].lower() or "mental element" in term_res.json()["plain_language_meaning"].lower()

    # 4. Case Analysis with include_spans=False (verifying bug fix)
    case_res = client.post(
        "/api/v1/legal-language/analyze-case",
        json={
            "text": "IN THE HIGH COURT OF DELHI\nRamesh v. Suresh\nWhether the appeal is maintainable?\nThe appellant argued that the order was void.\nThe appeal is dismissed.",
            "include_spans": False,
        },
    )
    assert case_res.status_code == 200
    assert len(case_res.json()["evidence_spans"]) == 0  # Verified: False is not overridden to True!

    # 5. Case Analysis with include_spans=True
    case_res_spans = client.post(
        "/api/v1/legal-language/analyze-case",
        json={
            "text": "IN THE HIGH COURT OF DELHI\nRamesh v. Suresh\nWhether the appeal is maintainable?\nThe appellant argued that the order was void.\nThe appeal is dismissed.",
            "include_spans": True,
        },
    )
    assert case_res_spans.status_code == 200
    assert len(case_res_spans.json()["evidence_spans"]) > 0
