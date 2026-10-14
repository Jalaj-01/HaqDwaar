"""Automated tests for security hardening, rate limits, CORS, file limits, and safe errors."""

import io
from fastapi.testclient import TestClient
import fitz
import pytest

from config import settings
from security import limiter


@pytest.fixture(autouse=True)
def setup_security_tests():
    """Ensure clean security settings and limiter state for each test."""
    orig_rate_limiting = settings.enable_rate_limiting
    orig_api_key = settings.api_key
    orig_analyze_limit = settings.rate_limit_analyze
    orig_transform_limit = settings.rate_limit_transform
    orig_extract_limit = settings.rate_limit_extract
    orig_case_limit = settings.rate_limit_case_analysis
    orig_window = settings.rate_limit_window_seconds
    orig_env = settings.environment

    # Run tests with rate limiting enabled by default
    settings.enable_rate_limiting = True
    settings.api_key = None

    yield

    # Restore settings
    settings.enable_rate_limiting = orig_rate_limiting
    settings.api_key = orig_api_key
    settings.rate_limit_analyze = orig_analyze_limit
    settings.rate_limit_transform = orig_transform_limit
    settings.rate_limit_extract = orig_extract_limit
    settings.rate_limit_case_analysis = orig_case_limit
    settings.rate_limit_window_seconds = orig_window
    settings.environment = orig_env


@pytest.mark.asyncio
async def test_rate_limiting_offense_analyze(client: TestClient):
    """Exceeding endpoint rate limit must return 429 with Retry-After and standard error shape."""
    await limiter.reset()
    settings.rate_limit_analyze = 2
    settings.rate_limit_window_seconds = 60

    payload = {"incident_text": "A person hacked into our server and downloaded private customer records."}

    # Request 1: Allowed
    res1 = client.post("/api/v1/offense/analyze", json=payload)
    assert res1.status_code == 200

    # Request 2: Allowed
    res2 = client.post("/api/v1/offense/analyze", json=payload)
    assert res2.status_code == 200

    # Request 3: Exceeded -> 429
    res3 = client.post("/api/v1/offense/analyze", json=payload)
    assert res3.status_code == 429
    assert "Retry-After" in res3.headers
    retry_after = int(res3.headers["Retry-After"])
    assert retry_after > 0

    data = res3.json()
    assert "error" in data
    assert data["error"]["code"] == "RATE_LIMIT_EXCEEDED"
    assert "request_id" in data["error"]
    assert "Rate limit exceeded" in data["error"]["message"]


@pytest.mark.asyncio
async def test_rate_limiting_can_be_disabled(client: TestClient):
    """When enable_rate_limiting is False, requests should not be blocked."""
    await limiter.reset()
    settings.enable_rate_limiting = False
    settings.rate_limit_analyze = 1

    payload = {"incident_text": "A person hacked into our server and downloaded private customer records."}

    res1 = client.post("/api/v1/offense/analyze", json=payload)
    assert res1.status_code == 200

    res2 = client.post("/api/v1/offense/analyze", json=payload)
    assert res2.status_code == 200


@pytest.mark.asyncio
async def test_rate_limiting_pdf_extract(client: TestClient):
    """Rate limit on PDF extraction endpoint returns 429."""
    await limiter.reset()
    settings.rate_limit_extract = 2

    # Create minimal 1-page valid PDF
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 72), "Sample judgment text for rate limit test.")
    pdf_bytes = doc.write()
    doc.close()

    files = {"file": ("test.pdf", pdf_bytes, "application/pdf")}
    res1 = client.post("/api/v1/documents/extract", files=files)
    assert res1.status_code == 200

    files = {"file": ("test.pdf", pdf_bytes, "application/pdf")}
    res2 = client.post("/api/v1/documents/extract", files=files)
    assert res2.status_code == 200

    files = {"file": ("test.pdf", pdf_bytes, "application/pdf")}
    res3 = client.post("/api/v1/documents/extract", files=files)
    assert res3.status_code == 429
    assert res3.json()["error"]["code"] == "RATE_LIMIT_EXCEEDED"


def test_security_headers_in_responses(client: TestClient):
    """All API responses must include defensive security headers."""
    response = client.get("/health")
    assert response.status_code == 200
    headers = response.headers

    assert headers.get("X-Content-Type-Options") == "nosniff"
    assert headers.get("X-Frame-Options") == "DENY"
    assert headers.get("X-XSS-Protection") == "1; mode=block"
    assert headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
    assert "X-Request-ID" in headers


def test_request_size_limit_middleware(client: TestClient):
    """Requests exceeding max_request_body_bytes in Content-Length must be rejected with 413."""
    oversized = settings.max_request_body_bytes + 1000
    headers = {"Content-Length": str(oversized)}

    response = client.post("/api/v1/offense/analyze", headers=headers, content=b"{}")
    assert response.status_code == 413
    data = response.json()
    assert data["error"]["code"] == "PAYLOAD_TOO_LARGE"
    assert "exceeds maximum allowed size" in data["error"]["message"]


def test_unsupported_file_extension(client: TestClient):
    """Uploading non-PDF files must return 415 UNSUPPORTED_MEDIA_TYPE."""
    files = {"file": ("document.txt", b"plain text", "text/plain")}
    response = client.post("/api/v1/documents/extract", files=files)
    assert response.status_code == 415
    data = response.json()
    assert data["error"]["code"] == "UNSUPPORTED_MEDIA_TYPE"


def test_invalid_pdf_magic_bytes(client: TestClient):
    """File ending with .pdf but lacking %PDF header must return 415."""
    files = {"file": ("fake.pdf", b"NOT_A_REAL_PDF_HEADER", "application/pdf")}
    response = client.post("/api/v1/documents/extract", files=files)
    assert response.status_code == 415
    data = response.json()
    assert data["error"]["code"] == "UNSUPPORTED_MEDIA_TYPE"
    assert "%PDF header missing" in data["error"]["message"]


def test_corrupted_pdf_error_sanitization(client: TestClient):
    """Corrupted PDF must return clean 400 error without exposing internal C++ exceptions."""
    corrupt_bytes = b"%PDF-1.4\n%corrupt stream invalid data"
    files = {"file": ("corrupt.pdf", corrupt_bytes, "application/pdf")}
    response = client.post("/api/v1/documents/extract", files=files)
    assert response.status_code == 400
    data = response.json()
    assert data["error"]["code"] == "BAD_REQUEST"
    # Ensure error message is sanitized and user-friendly
    assert "corrupted or unreadable" in data["error"]["message"].lower()
    # Confirm no memory leak or C++ pointer address in error
    assert "0x" not in data["error"]["message"]


def test_oversized_pdf_upload(client: TestClient):
    """PDF exceeding max_pdf_size_bytes must return 413."""
    # Create valid PDF header followed by oversized padding
    oversized_bytes = b"%PDF-1.4\n" + (b"0" * (settings.max_pdf_size_bytes + 50))
    files = {"file": ("large.pdf", oversized_bytes, "application/pdf")}
    response = client.post("/api/v1/documents/extract", files=files)
    assert response.status_code == 413
    assert response.json()["error"]["code"] == "PAYLOAD_TOO_LARGE"


def test_excessive_pdf_page_count(client: TestClient):
    """PDF exceeding max_pdf_pages must return 413."""
    doc = fitz.open()
    for _ in range(settings.max_pdf_pages + 2):
        doc.new_page()
    pdf_bytes = doc.write()
    doc.close()

    files = {"file": ("many_pages.pdf", pdf_bytes, "application/pdf")}
    response = client.post("/api/v1/documents/extract", files=files)
    assert response.status_code == 413
    data = response.json()
    assert data["error"]["code"] == "PAYLOAD_TOO_LARGE"
    assert "exceeds maximum page limit" in data["error"]["message"]


def test_empty_incident_text_rejected(client: TestClient):
    """Empty or whitespace-only incident text must return 400."""
    response = client.post("/api/v1/offense/analyze", json={"incident_text": "   "})
    assert response.status_code == 400
    data = response.json()
    assert data["error"]["code"] == "BAD_REQUEST"
    assert "must not be empty" in data["error"]["message"]


def test_oversized_incident_text_rejected(client: TestClient):
    """Incident text exceeding max_text_length must return 400."""
    long_text = "a" * (settings.max_text_length + 10)
    response = client.post("/api/v1/offense/analyze", json={"incident_text": long_text})
    assert response.status_code == 400
    assert "exceeds maximum allowed length" in response.json()["error"]["message"]


def test_case_analysis_empty_and_oversized_text(client: TestClient):
    """Case analysis validates empty and oversized input text."""
    # Empty
    res_empty = client.post("/api/v1/legal-language/analyze-case", json={"text": "  "})
    assert res_empty.status_code == 400

    # Oversized
    long_text = "Word " * (settings.max_text_length + 10)
    res_long = client.post("/api/v1/legal-language/analyze-case", json={"text": long_text})
    assert res_long.status_code == 400


def test_term_lookup_length_validation(client: TestClient):
    """Term lookup rejects oversized terms."""
    long_term = "x" * 150
    response = client.get(f"/api/v1/legal-language/terms/{long_term}")
    assert response.status_code == 400
    assert "must not exceed 100 characters" in response.json()["error"]["message"]


def test_cors_behavior_allowed_and_disallowed(client: TestClient):
    """CORS middleware returns origin header only for authorized origins."""
    # Authorized origin 1: localhost
    res_auth1 = client.get("/health", headers={"Origin": "http://localhost:5173"})
    assert res_auth1.headers.get("access-control-allow-origin") == "http://localhost:5173"

    # Authorized origin 2: 127.0.0.1
    res_auth2 = client.get("/health", headers={"Origin": "http://127.0.0.1:5173"})
    assert res_auth2.headers.get("access-control-allow-origin") == "http://127.0.0.1:5173"

    # Unauthorized origin
    res_unauth = client.get("/health", headers={"Origin": "http://evil-attacker.com"})
    assert res_unauth.headers.get("access-control-allow-origin") is None


def test_cors_production_wildcard_rejected():
    """Config validator prohibits wildcard '*' origin in production environment."""
    from config import Settings

    with pytest.raises(ValueError, match="Wildcard CORS origin"):
        Settings(
            environment="production",
            cors_origins=["*"],
        )


def test_optional_api_key_authentication(client: TestClient):
    """Optional API key restricts endpoints when configured, but stays open when None."""
    # 1. When api_key is None (academic demo mode), requests succeed without key
    settings.api_key = None
    res_open = client.post("/api/v1/offense/analyze", json={"incident_text": "Valid test incident description."})
    assert res_open.status_code == 200

    # 2. When api_key is set (protected mode), requests require matching X-API-Key
    settings.api_key = "secure-lexilaw-token-456"

    # Missing key -> 401
    res_missing = client.post("/api/v1/offense/analyze", json={"incident_text": "Valid test incident description."})
    assert res_missing.status_code == 401
    assert res_missing.json()["error"]["code"] == "UNAUTHORIZED"

    # Invalid key -> 401
    res_wrong = client.post(
        "/api/v1/offense/analyze",
        headers={"X-API-Key": "wrong-key"},
        json={"incident_text": "Valid test incident description."},
    )
    assert res_wrong.status_code == 401

    # Correct key -> 200
    res_correct = client.post(
        "/api/v1/offense/analyze",
        headers={"X-API-Key": "secure-lexilaw-token-456"},
        json={"incident_text": "Valid test incident description."},
    )
    assert res_correct.status_code == 200
