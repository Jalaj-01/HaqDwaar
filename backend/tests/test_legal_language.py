"""Unit tests for Module 2: Bidirectional Legal Language Transformation and Terminology."""

from fastapi.testclient import TestClient
import pytest

from modules.legal_language import (
    TransformRequest,
    get_term_explanation,
    process_transformation,
)
from nlp.transformation import (
    lookup_term,
    run_preservation_checks,
    transform_legal_to_normal,
    transform_normal_to_legal,
)


def test_legal_to_normal_preserves_facts_dates_amounts():
    """Legal-to-normal mode must simplify legalese while preserving dates, amounts, and conditions."""
    legal_text = (
        "Notwithstanding clause 3, the lessee shall pay Rs. 25,000 to the lessor "
        "on or before 5th November 2026, unless written notice is served."
    )
    req = TransformRequest(text=legal_text, mode="legal_to_normal")
    res = process_transformation(req, request_id="trans-test-1")

    assert res.mode == "legal_to_normal"
    out_lower = res.transformed_text.lower()

    # Simplification occurred
    assert "tenant" in out_lower or "renter" in out_lower
    assert "despite" in out_lower

    # Facts, dates, amounts preserved
    assert "25,000" in res.transformed_text
    assert "5th november 2026" in out_lower
    assert "unless" in out_lower

    # Term explanations populated
    terms_found = [t.term.lower() for t in res.terminology_explanations]
    assert "lessee" in terms_found
    assert "notwithstanding" in terms_found

    # Preservation audit
    report = res.preservation_checks
    assert report.dates_preserved is True
    assert report.amounts_preserved is True
    assert report.overall_status in ("passed_basic_checks", "warnings")


def test_normal_to_legal_introduces_no_unsupported_facts():
    """Normal-to-legal mode produces structured legal draft without inventing dates or amounts."""
    normal_text = (
        "Someone created a fake Instagram account using my photos and demanded Rs. 50,000 on 12th October 2026."
    )
    req = TransformRequest(text=normal_text, mode="normal_to_legal")
    res = process_transformation(req, request_id="trans-test-2")

    assert res.mode == "normal_to_legal"
    assert "FORMAL STATEMENT OF FACTS" in res.transformed_text
    assert "CHRONOLOGICAL STATEMENT" in res.transformed_text

    # Stated facts retained
    assert "50,000" in res.transformed_text
    assert "12th October 2026" in res.transformed_text

    # No unsupported additions
    report = res.preservation_checks
    assert len(report.unsupported_additions_detected) == 0


def test_preservation_checks_detect_dropped_negation():
    """Preservation check must detect dropped negation and require review."""
    input_text = "The applicant did not sign the contract and never authorized payment."
    # Fabricate an output where negation is removed
    tampered_output = "The applicant signed the contract and authorized payment."

    report = run_preservation_checks(input_text, tampered_output)
    assert report.negation_preserved is False
    assert report.overall_status == "review_required"
    neg_check = next((c for c in report.checks if c.category == "negation"), None)
    assert neg_check is not None
    assert neg_check.status == "review_required"


def test_preservation_checks_detect_dropped_money():
    """Preservation check must detect dropped monetary amounts."""
    input_text = "The borrower failed to return Rs. 75,000."
    tampered_output = "The borrower failed to return the funds."

    report = run_preservation_checks(input_text, tampered_output)
    assert report.amounts_preserved is False
    assert report.overall_status == "review_required"


def test_term_lookup_found(client: TestClient):
    """GET /api/v1/legal-language/terms/{term} must return 200 with dictionary entry."""
    response = client.get("/api/v1/legal-language/terms/lessee")
    assert response.status_code == 200
    data = response.json()

    assert data["term"] == "lessee"
    assert "plain_language_meaning" in data
    assert "verification_status" in data
    assert data["verification_status"] == "verified"

    # Test case insensitivity
    response_upper = client.get("/api/v1/legal-language/terms/NOTWITHSTANDING")
    assert response_upper.status_code == 200
    assert response_upper.json()["term"] == "notwithstanding"
    assert response_upper.json()["verification_status"] == "verified"

    # Test unverified term lookup
    response_unver = client.get("/api/v1/legal-language/terms/force majeure")
    assert response_unver.status_code == 200
    assert response_unver.json()["verification_status"] == "unverified"


def test_term_lookup_not_found(client: TestClient):
    """Unknown terms must return 404 with standardized error shape."""
    response = client.get("/api/v1/legal-language/terms/fictional_unregistered_term_999")
    assert response.status_code == 404
    data = response.json()

    assert "error" in data
    assert data["error"]["code"] == "NOT_FOUND"
    assert "request_id" in data["error"]
    assert "not found" in data["error"]["message"].lower()


def test_transform_api_endpoint(client: TestClient):
    """POST /api/v1/legal-language/transform must work for both supported modes."""
    # 1. legal_to_normal
    res_l2n = client.post(
        "/api/v1/legal-language/transform",
        json={
            "text": "The aforementioned lessee is liable for damages.",
            "mode": "legal_to_normal",
        },
    )
    assert res_l2n.status_code == 200
    d_l2n = res_l2n.json()
    assert d_l2n["mode"] == "legal_to_normal"
    assert "transformed_text" in d_l2n
    assert len(d_l2n["terminology_explanations"]) > 0

    # 2. normal_to_legal
    res_n2l = client.post(
        "/api/v1/legal-language/transform",
        json={
            "text": "Someone broke into my shop and stole inventory.",
            "mode": "normal_to_legal",
        },
    )
    assert res_n2l.status_code == 200
    d_n2l = res_n2l.json()
    assert d_n2l["mode"] == "normal_to_legal"
    assert "missing_details" in d_n2l

    # 3. Invalid mode
    res_invalid = client.post(
        "/api/v1/legal-language/transform",
        json={"text": "Some text", "mode": "unsupported_mode"},
    )
    assert res_invalid.status_code == 400
    d_inv = res_invalid.json()
    assert d_inv["error"]["code"] == "BAD_REQUEST"
