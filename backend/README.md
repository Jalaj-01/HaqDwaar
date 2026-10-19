# LexiLaw Backend — NLP Legal Information & Transformation System

LexiLaw is an academic Natural Language Processing (NLP) backend for legal information retrieval and bidirectional legal-language transformation under Indian law (English-language input only in Phase 1).

---

## 1. Project Overview & Architecture

LexiLaw has exactly **two main modules**:

### Module 1: Legal Offense Decoder
Transforms ordinary-language incident accounts into structured, evidence-grounded statutory analyses:
1. Validates and normalizes input text.
2. Extracts stated facts, named entities, digital identifiers, monetary values, and explicit consent indicators.
3. Classifies incidents into an explainable provisional taxonomy.
4. Retrieves candidate legal provisions from a curated local corpus using TF-IDF and optional dense semantic retrieval.
5. Evaluates constituent statutory legal elements (`supported`, `contradicted`, `not_established`).
6. Dynamically generates neutral follow-up questions targeting unestablished essential elements.
7. Produces transparent, grounded explanations with separate visibility of lexical and semantic scores.
8. Enforces statutory legal disclaimers and strictly avoids declaring guilt or definitive conclusions.

### Module 2: Bidirectional Legal Language Transformation
- **Mode A (`legal_to_normal`)**: Translates complex statutory or contractual texts into plain English using controlled lexical substitution, clause segmentation, and obligation preservation (`shall` -> `must`). Automatically provides definitions for identified legal terms.
- **Mode B (`normal_to_legal`)**: Organizes ordinary factual narratives into formal, structured legal drafts (Parties, Chronological Recitals, Allegations, Reservation of Rights). Detects missing material details without inventing unstated claims.
- **Preservation Verification Layer**: Audits output against input to ensure zero loss of entities, dates, amounts, negation, or legal conditions, and detects unsupported additions.
- **Legal Terminology Dictionary**: Case-insensitive lookup of difficult legal terms with contextual meanings and source citations.
- **Case Document Understanding**: Segments court judgments to extract case metadata, material facts, legal issues, cited provisions, party submissions (petitioner vs. respondent), judicial reasoning, and final outcomes.
- **PDF Extraction**: Extracts text per page using PyMuPDF (`fitz`) with strict size and security validation.

---

## 2. Component Readiness Table

| Component | Status | Model / Dependency | Notes |
| :--- | :--- | :--- | :--- |
| **API & Error Handling** | Functional | FastAPI, Pydantic v2 | Standard error envelope, request ID tracking |
| **Preprocessing Pipeline** | Functional | spaCy (`en_core_web_sm`) | NFKC normalization, English-only check, qualification retention |
| **Entity & Fact Extraction** | Functional | spaCy NER, Regex | Grounded evidence spans, consent & harm indicators |
| **Incident Classification** | Baseline | Rule-based taxonomy | Flagged `is_provisional: True` |
| **Corpus Retrieval (TF-IDF)** | Functional | scikit-learn | Sublinear term frequency, cosine similarity |
| **Corpus Retrieval (Semantic)**| Functional (Optional)| `all-MiniLM-L6-v2` | Dense vector similarity; offline fallback to TF-IDF |
| **Element Matching Engine** | Functional | Rule/fact matching | `supported`, `contradicted`, `not_established` |
| **Language Transform (L2N)** | Baseline | Rule/dictionary substitution | Clause splitting, legalese replacement, preservation audit |
| **Language Transform (N2L)** | Baseline | Template/fact assembly | Structured notice/draft format, missing detail detection |
| **Terminology Dictionary** | Functional | JSON Dictionary | 29 terms (27 verified, 2 unverified), lookup via endpoint |
| **Case Analysis** | Functional | Pattern/sentence markers | Distinguishes party submissions from court findings |
| **PDF Text Extraction** | Functional | PyMuPDF (`fitz`) | 10MB limit, 50 pages max, encrypted file rejection |
| **Statutory Corpus Data** | Functional | India Code / e-Gazette | 37 provisions (35 verified, 2 unverified / provisional fixtures) |

---

## 3. Directory Structure

```text
backend/
    main.py                       # FastAPI entrypoint, routes, middleware, error handlers
    config.py                     # Environment-based config, limits, paths
    requirements.txt              # Pinned, verified dependencies
    .env.example                  # Environment configuration template
    README.md                     # Architecture, contract, and run documentation
    CORPUS_AUDIT_REPORT.md        # Full legal corpus audit & regression report
    openapi.json                  # Exported OpenAPI 3.1 specification

    nlp/
        __init__.py
        preprocessing.py          # Normalization, sentence segmentation, qualifier preservation
        entities.py               # Entity extraction, consent/intent facts, evidence spans
        retrieval.py              # Corpus indexing, TF-IDF, semantic retrieval, ranking
        classification.py         # Provisional incident category taxonomy
        legal_matching.py         # Element comparison, support status, follow-up questions
        transformation.py         # Legal-to-normal, normal-to-legal, preservation verification
        case_analysis.py          # Judgment parsing, party argument separation, PDF extractor

    modules/
        __init__.py
        offense_decoder.py        # Module 1 orchestration
        legal_language.py         # Module 2 orchestration

    data/
        legal_provisions.json     # Verified statutory provisions from India Code / e-Gazette
        legal_terms.json          # Verified legal terminology dictionary
        case_documents/           # Directory for uploaded / sample case records

    scripts/
        validate_corpus.py        # Validates provisions and dictionary; outputs schema template
        export_openapi.py         # Generates openapi.json

    evaluation/
        README.md                 # Evaluation methodology and metric definitions
        retrieval_eval_template.json # Template for human ground-truth annotations
        eval_retrieval.py         # Precision@K, Recall@K, MRR evaluation script
        eval_transformation.py    # Fact preservation benchmark evaluation script

    tests/
        conftest.py               # Test client fixtures and environment setup
        test_api.py               # Health, status, error handling tests
        test_preprocessing.py     # Language check, Unicode, negation, entity extraction tests
        test_retrieval.py         # Corpus indexing, ranking, penalty suppression tests
        test_offense_decoder.py   # Module 1 functional & regression tests
        test_legal_language.py    # Module 2 transformation and term lookup tests
        test_case_analysis.py     # Judgment extraction and PDF security tests
        fixtures/
            synthetic_provisions.json # Synthetic test data clearly labeled SYNTHETIC
```

---

## 4. Setup and Installation

### Prerequisites
- Python 3.11, 3.12, or 3.13.

### Step 1: Install Dependencies
```bash
pip install -r backend/requirements.txt
```

### Step 2: One-Time Model Installation (Offline Policy)
LexiLaw never downloads models automatically at runtime. Run these one-time commands:

1. **Install spaCy English model**:
   ```bash
   python -m spacy download en_core_web_sm
   ```

2. **(Optional) Cache Sentence-Transformers Semantic Model**:
   ```bash
   python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
   ```
   *Note: If the semantic model is not cached locally, LexiLaw automatically falls back to TF-IDF retrieval without errors.*

### Step 3: Configure Environment
Copy `.env.example` to `.env`:
```bash
cp backend/.env.example backend/.env
```

### Step 4: Validate Legal Corpus
```bash
python backend/scripts/validate_corpus.py
```

### Step 5: Start the Development Server
```bash
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```
Interactive API documentation is available at: `http://127.0.0.1:8000/docs`.

---

## 5. How to Add and Curate Legal Provisions

LexiLaw adheres strictly to source integrity. Real laws must never be fabricated.

1. **Generate the copy-pasteable JSON template**:
   ```bash
   python backend/scripts/validate_corpus.py --template
   ```
2. **Retrieve official statutory text** from [India Code](https://www.indiacode.nic.in/) or [The Gazette of India](https://egazette.gov.in/).
3. **Add the entry** to `backend/data/legal_provisions.json`.
4. **Validate**:
   ```bash
   python backend/scripts/validate_corpus.py
   ```

### Statutory Provision Template
```json
{
  "id": "IPC_S419",
  "jurisdiction": "India",
  "act_name": "Indian Penal Code, 1860",
  "section_id": "Section 419",
  "title": "Punishment for cheating by personation",
  "source_text": "Whoever cheats by personation shall be punished with imprisonment...",
  "plain_language_summary": "Punishes pretending to be someone else to cheat another person.",
  "legal_elements": [
    {
      "element_id": "ELEM_1",
      "description": "Pretending to be another person",
      "keywords": ["impersonate", "pretend", "fake profile"]
    },
    {
      "element_id": "ELEM_2",
      "description": "Cheating or deceiving another person thereby",
      "keywords": ["cheat", "fraud", "deceive"]
    }
  ],
  "exceptions_or_qualifications": null,
  "penalty_text": "Imprisonment of either description for a term which may extend to three years, or with fine, or with both.",
  "official_source_url": "https://www.indiacode.nic.in/handle/123456789/2263",
  "source_authority": "Ministry of Law and Justice, Government of India",
  "source_verified": true,
  "verified_at": "2026-10-12T00:00:00Z",
  "effective_from": "1862-01-01",
  "effective_to": null,
  "version_label": "as amended",
  "source_document_identifier": "Act No. 45 of 1860"
}
```

---

## 6. API Contract Freeze (Frozen Specification)

### Consistent Error Response Shape
All 4xx and 5xx errors return the exact JSON shape:
```json
{
  "error": {
    "code": "BAD_REQUEST | NOT_FOUND | PAYLOAD_TOO_LARGE | UNSUPPORTED_MEDIA_TYPE | VALIDATION_ERROR | INTERNAL_SERVER_ERROR",
    "message": "Human-readable explanation of error",
    "request_id": "unique-request-uuid"
  }
}
```

### Contextual Answers Format
Used in `POST /api/v1/offense/analyze`:
```json
[
  {
    "question_id": "Q_PROVISION_ID_ELEMENT_ID",
    "answer": "Yes, the account was created on Instagram without my permission."
  }
]
```

### Frozen Endpoints Contract
1. `GET /health`
   - Response: `{"status": "ok", "message": "API is running"}`
2. `GET /api/v1/status`
   - Response: `StatusResponse` (component readiness, model status, truthful corpus status, limits, limitations)
3. `POST /api/v1/offense/analyze`
   - Request: `{"incident_text": str, "contextual_answers": list[ContextualAnswer] | null, "top_k": int | null}`
   - Response: `OffenseAnalysisResponse` (`request_id`, `extracted_facts`, `incident_categories`, `candidate_provisions`, `follow_up_questions`, `uncertainty_notes`, `disclaimer`, `no_reliable_match`)
4. `POST /api/v1/legal-language/transform`
   - Request: `{"text": str, "mode": "legal_to_normal" | "normal_to_legal", "context": dict | null}`
   - Response: `TransformResponse` (`request_id`, `mode`, `original_text`, `transformed_text`, `extracted_facts`, `terminology_explanations`, `missing_details`, `preservation_checks`, `warnings`, `review_status`)
5. `GET /api/v1/legal-language/terms/{term}`
   - Response: `LegalTerm` (term, plain_language_meaning, legal_context, example_usage, related_terms, source, verification_status)
6. `POST /api/v1/legal-language/analyze-case`
   - Request: `{"text": str, "include_spans": bool | null}`
   - Response: `CaseAnalysisResult` (`case_metadata`, `material_facts`, `legal_issues`, `cited_provisions`, `party_arguments`, `court_reasoning`, `outcome`, `key_takeaways`, `evidence_spans`, `warnings`)
7. `POST /api/v1/documents/extract`
   - Request: `multipart/form-data` with `file: UploadFile` (.pdf)
   - Response: `DocumentExtractResponse` (`request_id`, `filename`, `page_count`, `total_characters`, `pages`, `extracted_text`, `warnings`)

---

## 7. Running Tests & Evaluation

### Run Automated Test Suite
```bash
pytest backend/tests/ -v
```

### Run Evaluation Benchmarks
```bash
# Retrieval Metrics (Precision@K, Recall@K, MRR)
python backend/evaluation/eval_retrieval.py

# Transformation Fact-Preservation Benchmark
python backend/evaluation/eval_transformation.py
```

---

## 8. Legal Disclaimer

> [!IMPORTANT]
> LexiLaw is an academic research system designed for informational analysis and draft assistance. It does not provide actionable legal advice, formal representation, or definitive findings of guilt, criminal liability, or civil violation. Users must consult a licensed legal advocate for formal legal counsel.
