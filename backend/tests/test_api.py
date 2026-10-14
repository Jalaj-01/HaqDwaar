"""Tests for baseline API endpoints, status reporting, and error handling."""

from fastapi.testclient import TestClient
from pydantic import ValidationError

from config import settings
from nlp.retrieval import (
    LegalElement,
    LegalProvision,
    get_corpus_status_info,
    load_legal_provisions,
)


def test_health_endpoint(client: TestClient):
    """GET /health must return 200 with standard status ok."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["message"] == "API is running"


def test_status_endpoint(client: TestClient):
    """GET /api/v1/status must report readiness, limits, and truthful corpus state."""
    response = client.get("/api/v1/status")
    assert response.status_code == 200
    data = response.json()

    assert "request_id" in data
    assert data["corpus_status"] in ["loaded", "partial_unverified"]
    assert data["corpus_record_count"] >= 15
    assert data["verified_record_count"] >= 15
    assert data["retrieval_mode"] in ["hybrid", "tfidf_only"]
    assert isinstance(data["spacy_model_loaded"], bool)
    assert isinstance(data["semantic_model_loaded"], bool)

    # Configured limits
    limits = data["configured_limits"]
    assert limits["max_text_length"] == settings.max_text_length
    assert limits["max_top_k"] == settings.max_top_k
    assert limits["default_top_k"] == settings.default_top_k
    assert limits["max_pdf_size_bytes"] == settings.max_pdf_size_bytes
    assert limits["max_pdf_pages"] == settings.max_pdf_pages

    # Limitations list
    assert len(data["known_limitations"]) > 0

    # Ensure no internal filesystem paths or secret leaks in response string
    response_str = response.text
    assert "C:\\" not in response_str
    assert "G:\\" not in response_str
    assert "/home/" not in response_str


def test_request_id_middleware(client: TestClient):
    """Responses must return an X-Request-ID header, preserving a passed ID if provided."""
    custom_id = "test-custom-req-id-12345"
    response = client.get("/health", headers={"X-Request-ID": custom_id})
    assert response.status_code == 200
    assert response.headers.get("X-Request-ID") == custom_id


def test_consistent_404_error_shape(client: TestClient):
    """Non-existent routes must return the standardized error shape."""
    response = client.get("/api/v1/non_existent_route")
    assert response.status_code == 404
    data = response.json()

    assert "error" in data
    assert data["error"]["code"] == "NOT_FOUND"
    assert "request_id" in data["error"]
    assert "message" in data["error"]


def test_empty_corpus_handling(tmp_path):
    """Empty corpus should return empty list without crashing."""
    empty_file = tmp_path / "empty_provisions.json"
    empty_file.write_text("[]", encoding="utf-8")

    provisions = load_legal_provisions(empty_file)
    assert isinstance(provisions, list)
    assert len(provisions) == 0

    status = get_corpus_status_info(empty_file)
    assert status["corpus_status"] == "empty"
    assert status["corpus_record_count"] == 0
    assert status["verified_record_count"] == 0


def test_provision_schema_validation():
    """Provision schema must strictly enforce required fields."""
    valid_record = {
        "id": "SYN_001",
        "jurisdiction": "India",
        "act_name": "Synthetic Test Act 2026",
        "section_id": "Section 1",
        "title": "Short Title",
        "source_text": "This Act may be called the Synthetic Test Act.",
        "plain_language_summary": "Summary of synthetic test act.",
        "legal_elements": [
            {
                "element_id": "SYN_E1",
                "description": "Synthetic requirement",
                "keywords": ["test", "synthetic"],
            }
        ],
        "official_source_url": "https://example.gov.in/synthetic",
        "source_authority": "Synthetic Gazette Authority",
        "source_verified": False,
        "version_label": "original",
    }

    provision = LegalProvision.model_validate(valid_record)
    assert provision.id == "SYN_001"
    assert provision.legal_elements[0].element_id == "SYN_E1"

    # Missing mandatory field: act_name
    invalid_record = dict(valid_record)
    del invalid_record["act_name"]

    try:
        LegalProvision.model_validate(invalid_record)
        assert False, "Should have raised ValidationError"
    except ValidationError:
        pass


def test_status_semantic_fallback(client: TestClient):
    """When semantic model is disabled, status must report tfidf_only."""
    orig = settings.disable_semantic_model
    try:
        settings.disable_semantic_model = True
        response = client.get("/api/v1/status")
        assert response.status_code == 200
        data = response.json()
        assert data["semantic_model_loaded"] is False
        assert data["retrieval_mode"] == "tfidf_only"
    finally:
        settings.disable_semantic_model = orig
