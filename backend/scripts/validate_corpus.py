"""Validation script for statutory provisions and legal terminology files."""

import json
import sys
from pathlib import Path

# Ensure backend root is on sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from nlp.retrieval import load_legal_provisions, load_legal_terms
from config import LEGAL_PROVISIONS_PATH, LEGAL_TERMS_PATH

PROVISION_TEMPLATE = {
    "id": "ACT_SECTION_ID_TO_BE_FILLED",
    "jurisdiction": "India",
    "act_name": "TO BE FILLED FROM OFFICIAL SOURCE (e.g. Information Technology Act, 2000)",
    "section_id": "TO BE FILLED FROM OFFICIAL SOURCE (e.g. Section 66C)",
    "title": "TO BE FILLED FROM OFFICIAL SOURCE",
    "source_text": "TO BE FILLED FROM OFFICIAL SOURCE (Verbatim text from indiacode.nic.in / egazette.gov.in)",
    "plain_language_summary": "TO BE FILLED (Concise plain-English explanation)",
    "legal_elements": [
        {
            "element_id": "ELEM_1",
            "description": "TO BE FILLED (Constituent legal element)",
            "keywords": ["keyword1", "keyword2"]
        }
    ],
    "exceptions_or_qualifications": "TO BE FILLED OR null",
    "penalty_text": "TO BE FILLED FROM OFFICIAL SOURCE OR null",
    "official_source_url": "TO BE FILLED FROM OFFICIAL SOURCE (https://www.indiacode.nic.in/...)",
    "source_authority": "TO BE FILLED (e.g. Ministry of Law and Justice, Government of India)",
    "source_verified": True,
    "verified_at": "YYYY-MM-DDTHH:MM:SSZ",
    "effective_from": "YYYY-MM-DD",
    "effective_to": None,
    "version_label": "as amended up to YYYY",
    "source_document_identifier": "TO BE FILLED (Official Gazette or Act No.)"
}


def print_template():
    """Print copy-pasteable JSON template for official statutory records."""
    print("========================================")
    print("STATUTORY PROVISION JSON TEMPLATE")
    print("========================================")
    print(json.dumps(PROVISION_TEMPLATE, indent=2))
    print("========================================")


def validate_corpus() -> int:
    """Validate both legal_provisions.json and legal_terms.json against schemas."""
    errors = 0
    print("========================================")
    print("LexiLaw Corpus Validation")
    print("========================================")

    # 1. Validate Legal Provisions
    print(f"\n1. Validating statutory provisions: {LEGAL_PROVISIONS_PATH}")
    try:
        provisions = load_legal_provisions(LEGAL_PROVISIONS_PATH)
        verified_count = sum(1 for p in provisions if p.source_verified)
        print(f"   [OK] Successfully validated {len(provisions)} provision records.")
        print(f"        Verified: {verified_count}")
        print(f"        Unverified: {len(provisions) - verified_count}")
        if len(provisions) == 0:
            print("        [NOTE] Provisions list is currently EMPTY (as expected for initial state).")
    except Exception as exc:
        print(f"   [ERROR] Provisions validation failed: {exc}")
        errors += 1

    # 2. Validate Legal Terms
    print(f"\n2. Validating legal terminology: {LEGAL_TERMS_PATH}")
    try:
        terms = load_legal_terms(LEGAL_TERMS_PATH)
        verified_terms = sum(1 for t in terms if t.verification_status == "verified")
        print(f"   [OK] Successfully validated {len(terms)} term records.")
        print(f"        Verified: {verified_terms}")
        print(f"        Unverified: {len(terms) - verified_terms}")
    except Exception as exc:
        print(f"   [ERROR] Terms validation failed: {exc}")
        errors += 1

    print("\n========================================")
    if errors == 0:
        print("ALL VALIDATION CHECKS PASSED.")
        return 0
    else:
        print(f"VALIDATION FAILED with {errors} error(s).")
        return 1


if __name__ == "__main__":
    if "--template" in sys.argv or "-t" in sys.argv:
        print_template()
        sys.exit(0)
    sys.exit(validate_corpus())
