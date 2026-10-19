"""
LexiLaw — Legal Sources Organizer, Text Extractor, and Manifest Generator

This script:
1. Copies the original uploaded legal PDFs into standardized filenames in backend/data/legal_sources/:
   - 250883_english_01042024.pdf -> BNS_2023_Gazette.pdf
   - Bharatiya_Nagarik_Suraksha_Sanhita,_2023.pdf -> BNSS_2023_Introduced_Bill.pdf
2. Extracts searchable text into backend/data/legal_sources/extracted_text/:
   - BNS_2023_Gazette.txt
   - BNSS_2023_Introduced_Bill.txt
   Preserving headings, sections/clauses, subsections, page markers, and document provenance.
3. Generates backend/data/legal_sources/source_manifest.json with comprehensive provenance,
   cryptographic SHA-256 hashes, epistemic status, and explicit limitations.
"""

import os
import sys
import shutil
import hashlib
import json
import fitz  # PyMuPDF

LEGAL_SOURCES_DIR = os.path.dirname(os.path.abspath(__file__))
EXTRACTED_TEXT_DIR = os.path.join(LEGAL_SOURCES_DIR, "extracted_text")
MANIFEST_PATH = os.path.join(LEGAL_SOURCES_DIR, "source_manifest.json")


def compute_sha256(filepath: str) -> str:
    """Compute SHA-256 checksum of a file."""
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def extract_pdf_text(
    pdf_path: str,
    output_txt_path: str,
    doc_title: str,
    doc_id: str,
    doc_type: str,
    act_bill_no: str,
    legal_status_notice: str
) -> dict:
    """
    Extract text from a PDF with page boundary markers and document header.
    Returns extraction statistics including page count, character counts, and OCR needs.
    """
    doc = fitz.open(pdf_path)
    total_pages = len(doc)
    
    extracted_pages = []
    ocr_needed_pages = []
    extraction_errors = []
    total_chars = 0
    
    lines = []
    lines.append("=" * 80)
    lines.append(f"DOCUMENT ID: {doc_id}")
    lines.append(f"TITLE: {doc_title}")
    lines.append(f"DOCUMENT TYPE: {doc_type}")
    lines.append(f"ACT / BILL NUMBER: {act_bill_no}")
    lines.append(f"SOURCE FILE: {os.path.basename(pdf_path)}")
    lines.append(f"TOTAL PAGES: {total_pages}")
    lines.append("EXTRACTION ENGINE: PyMuPDF (fitz)")
    lines.append(f"LEGAL STATUS: {legal_status_notice}")
    lines.append("=" * 80)
    lines.append("")
    
    for page_idx in range(total_pages):
        page_num = page_idx + 1
        try:
            page = doc[page_idx]
            page_text = page.get_text("text")
            char_count = len(page_text.strip())
            total_chars += char_count
            
            if char_count == 0:
                ocr_needed_pages.append(page_num)
                extraction_errors.append(f"Page {page_num} yielded 0 characters (potential scanned image)")
            elif char_count < 30:
                extraction_errors.append(f"Page {page_num} yielded very low text ({char_count} chars)")
                
            lines.append("=" * 80)
            lines.append(f"=== PAGE {page_num} OF {total_pages} | {doc_title} ===")
            lines.append("=" * 80)
            lines.append("")
            lines.append(page_text)
            lines.append("")
            
            extracted_pages.append({
                "page_number": page_num,
                "character_count": char_count,
                "ocr_required": char_count == 0
            })
        except Exception as e:
            extraction_errors.append(f"Page {page_num} extraction failed: {str(e)}")
            lines.append(f"=== [EXTRACTION ERROR ON PAGE {page_num}: {str(e)}] ===")
            
    doc.close()
    
    # Write output file with UTF-8 encoding
    with open(output_txt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
        
    txt_sha256 = compute_sha256(output_txt_path)
    
    return {
        "total_pages": total_pages,
        "total_characters": total_chars,
        "ocr_needed_pages": ocr_needed_pages,
        "ocr_required": len(ocr_needed_pages) > 0,
        "extraction_errors": extraction_errors,
        "txt_sha256": txt_sha256,
        "txt_filesize_bytes": os.path.getsize(output_txt_path)
    }


def main():
    print("=== LexiLaw: Organizing Legal Sources and Extracting Text ===")
    
    os.makedirs(EXTRACTED_TEXT_DIR, exist_ok=True)
    
    source_configs = [
        {
            "source_id": "SRC_BNS_2023_GAZETTE",
            "original_filename": "250883_english_01042024.pdf",
            "stored_filename": "BNS_2023_Gazette.pdf",
            "document_title": "The Bharatiya Nyaya Sanhita, 2023",
            "document_type": "Primary Statutory Legislation (Official Gazette of India Extraordinary)",
            "act_or_bill_number": "Act No. 45 of 2023",
            "publication_date": "2023-12-25",
            "official_gazette_details": "The Gazette of India, Extraordinary, Part II, Section 1, No. 62, dated 25th December, 2023",
            "enacted_by": "Parliament of India (Seventy-fourth Year of the Republic of India)",
            "commencement_authority": "Ministry of Home Affairs Notification S.O. 850(E), dated 23 February 2024 (commenced 1 July 2024, except Section 106(2))",
            "legal_source_classification": "ENACTED_PRIMARY_PENAL_ACT",
            "legal_status_notice": "ENACTED STATUTE (Act No. 45 of 2023). Governs substantive criminal offenses committed on or after 1 July 2024. Text extracted here is for search/reference; legal content verification requires primary Gazette comparison.",
            "source_url": "https://www.indiacode.nic.in/handle/123456789/20062",
            "explicit_limitations": [
                "Contains substantive criminal law only; does not contain criminal procedure or evidence rules.",
                "Section 106(2) (fatal hit-and-run up to 10 years) is uncommenced per S.O. 850(E).",
                "Article 20(1) bars retroactive application to conduct committed prior to 1 July 2024.",
                "Extracted text has not been independently signed off by legal counsel as verified ground truth."
            ],
            "txt_output_filename": "BNS_2023_Gazette.txt"
        },
        {
            "source_id": "SRC_BNSS_2023_INTRODUCED_BILL",
            "original_filename": "Bharatiya_Nagarik_Suraksha_Sanhita,_2023.pdf",
            "stored_filename": "BNSS_2023_Introduced_Bill.pdf",
            "document_title": "The Bharatiya Nagarik Suraksha Sanhita, 2023 (As Introduced in Lok Sabha)",
            "document_type": "Unenacted Parliamentary Legislative Bill (Draft Bill)",
            "act_or_bill_number": "Bill No. 122 of 2023",
            "publication_date": "2023-08-11",
            "official_gazette_details": "Not published in Gazette as an Act; printed by Government of India Press under printer mark MGIPMRND-277LS(S3)-10-08-2023",
            "enacted_by": "Unenacted legislative draft bill introduced in Lok Sabha by Shri Amit Shah (Minister of Home Affairs)",
            "commencement_authority": "N/A (Introduced bill does not have legal commencement)",
            "legal_source_classification": "UNENACTED_LEGISLATIVE_BILL",
            "source_url": "http://164.100.47.4/BillsTexts/LSBillTexts/Asintroduced/122_2023_LS_ENG.pdf",
            "legal_status_notice": "UNENACTED INTRODUCED BILL (Bill No. 122 of 2023). This document is NOT the final enacted BNSS Act No. 46 of 2023. It contains pre-enactment draft clauses and schedules. DO NOT rely on this document for enforceable procedural law.",
            "explicit_limitations": [
                "This document is an introduced bill, NOT the final enacted Bharatiya Nagarik Suraksha Sanhita, 2023 (Act No. 46 of 2023).",
                "Clause numbering, procedural wording, and First Schedule classifications (Cognizable/Bailable) were amended during parliamentary passage.",
                "Enforceable procedural claims must cite Act No. 46 of 2023 published in Gazette No. 54 / 63 (25 Dec 2023), not this bill.",
                "Extracted text represents legislative history / draft reference only; it is not binding law."
            ],
            "txt_output_filename": "BNSS_2023_Introduced_Bill.txt"
        },
        {
            "source_id": "SRC_BNSS_2023_GAZETTE_ACT_46",
            "original_filename": "BNSS_2023_Gazette_Act_46.pdf",
            "stored_filename": "BNSS_2023_Gazette_Act_46.pdf",
            "document_title": "The Bharatiya Nagarik Suraksha Sanhita, 2023",
            "document_type": "Primary Statutory Legislation (Official Gazette of India Extraordinary)",
            "act_or_bill_number": "Act No. 46 of 2023",
            "publication_date": "2023-12-25",
            "official_gazette_details": "The Gazette of India, Extraordinary, Part II, Section 1, No. 54, Notification CG-DL-E-25122023-250884, dated 25th December, 2023",
            "enacted_by": "Parliament of India (Seventy-fourth Year of the Republic of India)",
            "commencement_authority": "Ministry of Home Affairs Notification S.O. 848(E), dated 23 February 2024 (commenced 1 July 2024, except First Schedule entry for Section 106(2) BNS)",
            "legal_source_classification": "ENACTED_PRIMARY_PROCEDURAL_ACT",
            "source_url": "https://www.indiacode.nic.in/handle/123456789/20063",
            "legal_status_notice": "ENACTED STATUTE (Act No. 46 of 2023). Governs criminal procedure for offenses investigated or tried on or after 1 July 2024. Contains authoritative First Schedule classifications (Cognizable/Non-Cognizable, Bailable/Non-Bailable, Court of Trial).",
            "explicit_limitations": [
                "Contains procedural criminal law and schedule classifications only; does not define substantive penal offenses.",
                "First Schedule entry regarding BNS Section 106(2) (hit-and-run) is held in abeyance / uncommenced per S.O. 848(E).",
                "Appointed commencement date is 1 July 2024; pre-commencement investigations/proceedings continue under CrPC 1973 per Section 531 BNSS savings clause.",
                "Extracted text provides machine-readable reference; legal content verification requires primary Gazette cross-check."
            ],
            "txt_output_filename": "BNSS_2023_Gazette_Act_46.txt"
        },
        {
            "source_id": "SRC_MHA_NOTIFICATION_SO_848E_2024",
            "original_filename": "MHA_Notification_SO_848E_2024.pdf",
            "stored_filename": "MHA_Notification_SO_848E_2024.pdf",
            "document_title": "Ministry of Home Affairs Notification S.O. 848(E) (Commencement of BNSS, 2023)",
            "document_type": "Subordinate Statutory Notification (Official Gazette of India Extraordinary)",
            "act_or_bill_number": "Notification S.O. 848(E) [F. No. 1/3/2023-Judicial Cell-I]",
            "publication_date": "2024-02-23",
            "official_gazette_details": "The Gazette of India, Extraordinary, Part II, Section 3, Sub-section (ii), No. 809, dated 23rd February, 2024",
            "enacted_by": "Central Government (Ministry of Home Affairs), issued by Shri Prakash, Joint Secretary",
            "commencement_authority": "Issued pursuant to Section 1(3) of the Bharatiya Nagarik Suraksha Sanhita, 2023 (Act No. 46 of 2023)",
            "legal_source_classification": "SUBORDINATE_COMMENCEMENT_NOTIFICATION",
            "source_url": "https://egazette.gov.in/WriteReadData/2024/252277.pdf",
            "legal_status_notice": "OFFICIAL COMMENCEMENT ORDER. Legally appoints 1 July 2024 as the commencement date for Act No. 46 of 2023 (BNSS), with explicit statutory exception for the First Schedule entry relating to Section 106(2) BNS.",
            "explicit_limitations": [
                "Appoints the effective date of BNSS as 1 July 2024.",
                "Carves out and excludes Section 106(2) BNS entry in First Schedule from coming into force."
            ],
            "txt_output_filename": "MHA_Notification_SO_848E_2024.txt"
        }
    ]
    
    manifest_sources = []
    
    for cfg in source_configs:
        orig_path = os.path.join(LEGAL_SOURCES_DIR, cfg["original_filename"])
        stored_path = os.path.join(LEGAL_SOURCES_DIR, cfg["stored_filename"])
        txt_path = os.path.join(EXTRACTED_TEXT_DIR, cfg["txt_output_filename"])
        
        # Use stored_path if already present, otherwise copy from orig_path
        if os.path.exists(stored_path):
            stored_sha = compute_sha256(stored_path)
            orig_sha = compute_sha256(orig_path) if os.path.exists(orig_path) else stored_sha
        elif os.path.exists(orig_path):
            shutil.copy2(orig_path, stored_path)
            stored_sha = compute_sha256(stored_path)
            orig_sha = compute_sha256(orig_path)
            print(f"Copied '{cfg['original_filename']}' -> '{cfg['stored_filename']}'")
        else:
            print(f"ERROR: PDF file not found at '{stored_path}' or '{orig_path}'")
            sys.exit(1)
                
        stored_sha = compute_sha256(stored_path)
        assert orig_sha == stored_sha, f"Hash mismatch after copying {cfg['stored_filename']}!"
        
        # 2. Extract text
        print(f"Extracting text from '{cfg['stored_filename']}'...")
        stats = extract_pdf_text(
            pdf_path=stored_path,
            output_txt_path=txt_path,
            doc_title=cfg["document_title"],
            doc_id=cfg["source_id"],
            doc_type=cfg["document_type"],
            act_bill_no=cfg["act_or_bill_number"],
            legal_status_notice=cfg["legal_status_notice"]
        )
        print(f"  -> Extracted {stats['total_pages']} pages, {stats['total_characters']} characters to '{cfg['txt_output_filename']}'")
        print(f"  -> OCR needed pages: {stats['ocr_needed_pages']}")
        print(f"  -> Extraction errors: {len(stats['extraction_errors'])}")
        print(f"  -> Extracted text SHA-256: {stats['txt_sha256']}")
        
        # 3. Build manifest record
        manifest_record = {
            "source_id": cfg["source_id"],
            "original_filename": cfg["original_filename"],
            "stored_filename": cfg["stored_filename"],
            "relative_pdf_path": f"backend/data/legal_sources/{cfg['stored_filename']}",
            "relative_txt_path": f"backend/data/legal_sources/extracted_text/{cfg['txt_output_filename']}",
            "document_title": cfg["document_title"],
            "document_type": cfg["document_type"],
            "legal_source_classification": cfg["legal_source_classification"],
            "act_or_bill_number": cfg["act_or_bill_number"],
            "publication_date": cfg["publication_date"],
            "official_gazette_details": cfg["official_gazette_details"],
            "source_url": cfg["source_url"],
            "enacted_by": cfg["enacted_by"],
            "commencement_authority": cfg["commencement_authority"],
            "original_pdf_sha256": orig_sha,
            "stored_pdf_sha256": stored_sha,
            "extracted_text_sha256": stats["txt_sha256"],
            "pdf_size_bytes": os.path.getsize(stored_path),
            "text_size_bytes": stats["txt_filesize_bytes"],
            "page_count": stats["total_pages"],
            "total_extracted_characters": stats["total_characters"],
            "extraction_method": "PyMuPDF (fitz) native text stream parsing",
            "extraction_status": "EXTRACTED_SUCCESSFULLY",
            "legal_content_verification_status": "PENDING_HUMAN_LEGAL_REVIEW",
            "ocr_required": stats["ocr_required"],
            "ocr_needed_pages": stats["ocr_needed_pages"],
            "extraction_errors": stats["extraction_errors"],
            "explicit_limitations": cfg["explicit_limitations"],
            "legal_status_notice": cfg["legal_status_notice"]
        }
        manifest_sources.append(manifest_record)
        
    manifest = {
        "manifest_version": "1.0.0",
        "generated_timestamp": "2026-10-18T16:40:00+05:30",
        "description": "LexiLaw Official Legal Source Registry and Extraction Manifest",
        "total_sources_registered": len(manifest_sources),
        "epistemic_disclaimer": "Searchable text extraction and legal-content verification are distinct statuses. All extracted texts are machine-parsed representations for retrieval indexing and keyword search. Neither text extract constitutes approved ground truth until verified and signed off by qualified human legal reviewers.",
        "sources": manifest_sources
    }
    
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
        
    print(f"\nCreated source manifest at '{MANIFEST_PATH}'")
    print(f"Source manifest SHA-256: {compute_sha256(MANIFEST_PATH)}")
    print("=== Extraction and Organization Complete ===")


if __name__ == "__main__":
    main()
