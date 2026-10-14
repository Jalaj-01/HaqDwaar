"""Unit tests for Case Document Understanding and safe PDF text extraction."""

import io
from fastapi.testclient import TestClient
import fitz  # PyMuPDF
import pytest

from nlp.case_analysis import analyze_case_document, extract_pdf_document


def test_case_analysis_full_extraction():
    """Judgment text extraction separates metadata, issues, party arguments, and court findings."""
    judgment_text = """
IN THE SUPREME COURT OF INDIA
State of Maharashtra v. Ramesh Patel
AIR 2021 SC 105
Date of Decision: 15th March 2021

The prosecution case is that the accused created a forged digital certificate.
Whether the evidence establishes unauthorized access under Section 66 of the IT Act?
Learned counsel for the appellant submitted that the server logs were unverified and unreliable.
Learned counsel for the respondent argued that the forensic report conclusively proved hash alteration.
In our considered view, the forensic testimony unequivocally corroborates the prosecution narrative.
In the result, the appeal is dismissed.
"""
    res = analyze_case_document(judgment_text)

    # 1. Metadata
    assert "SUPREME COURT OF INDIA" in res.case_metadata.court
    assert "State of Maharashtra v. Ramesh Patel" in res.case_metadata.title
    assert "AIR 2021 SC 105" in res.case_metadata.citation
    assert "15th March 2021" in res.case_metadata.decision_date

    # 2. Issues
    assert len(res.legal_issues) >= 1
    assert "Whether" in res.legal_issues[0].text

    # 3. Party Submissions separated
    assert len(res.party_arguments.petitioner_arguments) >= 1
    assert "appellant" in res.party_arguments.petitioner_arguments[0].text.lower()

    assert len(res.party_arguments.respondent_arguments) >= 1
    assert "respondent" in res.party_arguments.respondent_arguments[0].text.lower()

    # 4. Judicial reasoning & findings
    assert len(res.court_reasoning) >= 1
    assert "considered view" in res.court_reasoning[0].text.lower()

    # 5. Outcome
    assert "appeal is dismissed" in res.outcome.text.lower()

    # 6. Statutory provisions cited
    prov_texts = [p.text for p in res.cited_provisions]
    assert any("Section 66" in p for p in prov_texts)


def test_case_analysis_missing_fields_not_fabricated():
    """Missing case elements must be reported as 'not identified' without fabrication."""
    sparse_text = "The complainant alleged that funds were misappropriated. Notice was issued."
    res = analyze_case_document(sparse_text)

    assert res.case_metadata.court == "not identified"
    assert res.case_metadata.title == "not identified"
    assert res.case_metadata.citation == "not identified"
    assert res.outcome.text == "not identified"
    assert len(res.warnings) > 0


def test_pdf_extraction_valid_document(client: TestClient):
    """PyMuPDF safely extracts per-page text from multi-page PDF."""
    # Create an in-memory 2-page PDF
    doc = fitz.open()
    p1 = doc.new_page()
    p1.insert_text((50, 72), "First page content for LexiLaw test.")
    p2 = doc.new_page()
    p2.insert_text((50, 72), "Second page content for LexiLaw test.")
    pdf_bytes = doc.tobytes()
    doc.close()

    files = {"file": ("test_doc.pdf", pdf_bytes, "application/pdf")}
    response = client.post("/api/v1/documents/extract", files=files)

    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "test_doc.pdf"
    assert data["page_count"] == 2
    assert len(data["pages"]) == 2
    assert data["pages"][0]["page_number"] == 1
    assert "First page" in data["pages"][0]["text"]
    assert data["pages"][1]["page_number"] == 2
    assert "Second page" in data["pages"][1]["text"]


def test_pdf_extraction_scanned_image_warning(client: TestClient):
    """Empty or image-only PDF triggers an explicit OCR limitation warning."""
    # Create a 1-page PDF without text
    doc = fitz.open()
    doc.new_page()
    pdf_bytes = doc.tobytes()
    doc.close()

    files = {"file": ("scanned_blank.pdf", pdf_bytes, "application/pdf")}
    response = client.post("/api/v1/documents/extract", files=files)

    assert response.status_code == 200
    data = response.json()
    assert len(data["warnings"]) >= 1
    assert "OCR" in data["warnings"][0] and "not supported" in data["warnings"][0]


def test_pdf_extraction_invalid_magic_bytes(client: TestClient):
    """Non-PDF file with .pdf extension must be rejected."""
    fake_content = b"This is just a plain text file, not a PDF."
    files = {"file": ("corrupt.pdf", fake_content, "application/pdf")}
    response = client.post("/api/v1/documents/extract", files=files)

    assert response.status_code == 415
    data = response.json()
    assert data["error"]["code"] == "UNSUPPORTED_MEDIA_TYPE"


def test_pdf_extraction_non_pdf_extension(client: TestClient):
    """Uploaded files with non-pdf extensions must be rejected."""
    files = {"file": ("document.docx", b"%PDF-1.4 dummy", "application/octet-stream")}
    response = client.post("/api/v1/documents/extract", files=files)

    assert response.status_code == 415
    data = response.json()
    assert data["error"]["code"] == "UNSUPPORTED_MEDIA_TYPE"


def test_pdf_extraction_encrypted_rejection():
    """Encrypted/password-protected PDFs must be rejected."""
    doc = fitz.open()
    doc.new_page()
    # Save with user password encryption
    pdf_bytes = doc.tobytes(encryption=fitz.PDF_ENCRYPT_AES_256, owner_pw="owner123", user_pw="user123")
    doc.close()

    with pytest.raises(ValueError, match="Password protected or encrypted PDF"):
        extract_pdf_document(pdf_bytes, filename="secure.pdf", request_id="sec-1")


def test_pdf_extraction_excessive_pages():
    """PDF exceeding max_pdf_pages must raise a ValueError."""
    doc = fitz.open()
    for _ in range(55):  # 55 pages > max_pdf_pages (50)
        doc.new_page()
    pdf_bytes = doc.tobytes()
    doc.close()

    with pytest.raises(ValueError, match="exceeds maximum page limit"):
        extract_pdf_document(pdf_bytes, filename="large.pdf", request_id="large-1")


def test_analyze_case_http_endpoint(client: TestClient):
    """POST /api/v1/legal-language/analyze-case must return 200 with structured analysis."""
    payload = {
        "text": (
            "IN THE SUPREME COURT OF INDIA\nABC v. XYZ\nAIR 2022 SC 99\n"
            "Whether the contract was breached under Section 73 Contract Act?\n"
            "Learned counsel for the petitioner argued delay occurred.\n"
            "In our considered view, time was of the essence.\n"
            "In the result, the petition is dismissed."
        ),
        "include_spans": True,
    }
    response = client.post("/api/v1/legal-language/analyze-case", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["case_metadata"]["title"] == "ABC v. XYZ"
    assert len(data["party_arguments"]["petitioner_arguments"]) > 0
    assert "dismissed" in data["outcome"]["text"].lower()
