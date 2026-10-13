"""LexiLaw Backend - FastAPI Main Application Entrypoint."""

import logging
import uuid
from typing import Dict, List, Optional
from fastapi import Depends, FastAPI, File, HTTPException, Request, UploadFile
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware

from config import settings
from modules.legal_language import (
    TransformRequest,
    TransformResponse,
    get_term_explanation,
    process_transformation,
)
from modules.offense_decoder import (
    OffenseAnalysisRequest,
    OffenseAnalysisResponse,
    analyze_incident,
)
from nlp.case_analysis import (
    CaseAnalysisResult,
    DocumentExtractResponse,
    analyze_case_document,
    extract_pdf_document,
)
from nlp.retrieval import (
    LegalTerm,
    get_corpus_status_info,
    is_semantic_model_available,
    is_spacy_available,
)
from security import (
    RequestSizeLimitMiddleware,
    SecurityHeadersMiddleware,
    rate_limit,
    verify_optional_api_key,
)

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("lexilaw.main")


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware to assign a unique request_id to each HTTP request."""

    async def dispatch(self, request: Request, call_next):
        req_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex
        request.state.request_id = req_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = req_id
        return response


app = FastAPI(
    title="LexiLaw API",
    description="NLP-focused legal information and legal-language transformation system for Indian law.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Register security and request tracking middleware (executed in reverse order of addition)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestSizeLimitMiddleware)
app.add_middleware(RequestIDMiddleware)

# Configure CORS with strict allowed origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Consistent error handling everywhere
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    req_id = getattr(request.state, "request_id", uuid.uuid4().hex)
    status_code_map = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        405: "METHOD_NOT_ALLOWED",
        413: "PAYLOAD_TOO_LARGE",
        415: "UNSUPPORTED_MEDIA_TYPE",
        422: "VALIDATION_ERROR",
        429: "RATE_LIMIT_EXCEEDED",
    }
    code = status_code_map.get(exc.status_code, "HTTP_ERROR")
    headers = {"X-Request-ID": req_id}
    if exc.headers:
        headers.update(exc.headers)
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": code, "message": str(exc.detail), "request_id": req_id}},
        headers=headers,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    req_id = getattr(request.state, "request_id", uuid.uuid4().hex)
    details: List[str] = []
    for err in exc.errors():
        loc = " -> ".join(str(part) for part in err.get("loc", []))
        msg = err.get("msg", "Invalid value")
        details.append(f"{loc}: {msg}" if loc else msg)
    message = "; ".join(details) if details else "Request validation failed"
    return JSONResponse(
        status_code=422,
        content={"error": {"code": "VALIDATION_ERROR", "message": message, "request_id": req_id}},
        headers={"X-Request-ID": req_id},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    req_id = getattr(request.state, "request_id", uuid.uuid4().hex)
    logger.error(
        f"Internal server error on {request.method} {request.url.path} [request_id={req_id}]: {exc}",
        exc_info=True,
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected internal server error occurred.",
                "request_id": req_id,
            }
        },
        headers={"X-Request-ID": req_id},
    )


# Health Models
class HealthResponse(BaseModel):
    status: str = Field(..., json_schema_extra={"example": "ok"})
    message: str = Field(..., json_schema_extra={"example": "API is running"})


class ConfiguredLimits(BaseModel):
    max_text_length: int
    max_top_k: int
    default_top_k: int
    max_pdf_size_bytes: int
    max_pdf_pages: int


class StatusResponse(BaseModel):
    request_id: str
    component_readiness: Dict[str, str]
    spacy_model_loaded: bool
    spacy_model_name: str
    semantic_model_loaded: bool
    semantic_model_name: str
    retrieval_mode: str
    corpus_record_count: int
    verified_record_count: int
    corpus_status: str
    configured_limits: ConfiguredLimits
    known_limitations: List[str]


@app.get("/health", response_model=HealthResponse, tags=["System"])
def health():
    """Simple API liveness endpoint."""
    return {"status": "ok", "message": "API is running"}


@app.get("/api/v1/status", response_model=StatusResponse, tags=["System"])
def system_status(request: Request):
    """Component readiness and system status reporting.

    Does not expose sensitive system paths or secrets.
    """
    req_id = getattr(request.state, "request_id", uuid.uuid4().hex)
    spacy_ok = is_spacy_available()
    semantic_ok = is_semantic_model_available()
    corpus_info = get_corpus_status_info()

    retrieval_mode = "hybrid" if semantic_ok else "tfidf_only"

    readiness = {
        "api": "ready",
        "spacy_pipeline": "ready" if spacy_ok else "unavailable",
        "retrieval_engine": "ready",
        "corpus": corpus_info["corpus_status"],
    }

    limitations = [
        "English language input only in Phase 1.",
        "Corpus is empty until project owner populates verified records from official sources.",
        "Offline-first NLP without commercial LLM APIs.",
        "Outputs are informational drafts for human review, not definitive legal conclusions.",
    ]

    return {
        "request_id": req_id,
        "component_readiness": readiness,
        "spacy_model_loaded": spacy_ok,
        "spacy_model_name": settings.spacy_model,
        "semantic_model_loaded": semantic_ok,
        "semantic_model_name": settings.semantic_model_name_or_path,
        "retrieval_mode": retrieval_mode,
        "corpus_record_count": corpus_info["corpus_record_count"],
        "verified_record_count": corpus_info["verified_record_count"],
        "corpus_status": corpus_info["corpus_status"],
        "configured_limits": {
            "max_text_length": settings.max_text_length,
            "max_top_k": settings.max_top_k,
            "default_top_k": settings.default_top_k,
            "max_pdf_size_bytes": settings.max_pdf_size_bytes,
            "max_pdf_pages": settings.max_pdf_pages,
        },
        "known_limitations": limitations,
    }


# =========================================================================
# Module 1: Legal Offense Decoder Endpoints
# =========================================================================

@app.post(
    "/api/v1/offense/analyze",
    response_model=OffenseAnalysisResponse,
    tags=["Module 1: Offense Decoder"],
    dependencies=[
        Depends(rate_limit("offense_analyze", lambda: settings.rate_limit_analyze)),
        Depends(verify_optional_api_key),
    ],
)
def offense_analyze(request: Request, payload: OffenseAnalysisRequest):
    """Analyze ordinary-language incident description against statutory provisions."""
    req_id = getattr(request.state, "request_id", uuid.uuid4().hex)
    try:
        return analyze_incident(payload, request_id=req_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


# =========================================================================
# Module 2: Legal Language Transformation Endpoints
# =========================================================================

@app.post(
    "/api/v1/legal-language/transform",
    response_model=TransformResponse,
    tags=["Module 2: Legal Language Transformation"],
    dependencies=[
        Depends(rate_limit("transform", lambda: settings.rate_limit_transform)),
        Depends(verify_optional_api_key),
    ],
)
def transform_language(request: Request, payload: TransformRequest):
    """Transform text between legal-to-normal and normal-to-legal language modes."""
    req_id = getattr(request.state, "request_id", uuid.uuid4().hex)
    try:
        return process_transformation(payload, request_id=req_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.get(
    "/api/v1/legal-language/terms/{term}",
    response_model=LegalTerm,
    tags=["Module 2: Legal Language Transformation"],
    dependencies=[
        Depends(rate_limit("term_lookup", lambda: settings.rate_limit_term_lookup)),
        Depends(verify_optional_api_key),
    ],
)
def get_term(request: Request, term: str):
    """Retrieve verified dictionary explanation and provenance for a legal term."""
    req_id = getattr(request.state, "request_id", uuid.uuid4().hex)
    clean_term = term.strip()
    if not clean_term:
        raise HTTPException(status_code=400, detail="Search term must not be empty.")
    if len(clean_term) > 100:
        raise HTTPException(status_code=400, detail="Search term must not exceed 100 characters.")

    term_record = get_term_explanation(clean_term)
    if not term_record:
        raise HTTPException(
            status_code=404,
            detail=f"Legal term '{clean_term}' was not found in the legal terms dictionary.",
        )
    return term_record


class CaseAnalysisRequest(BaseModel):
    """Payload for case document and judgment analysis."""
    text: str = Field(..., description="Full text of the legal judgment or case document")
    include_spans: Optional[bool] = Field(
        default=True, description="Whether to include character evidence spans"
    )


@app.post(
    "/api/v1/legal-language/analyze-case",
    response_model=CaseAnalysisResult,
    tags=["Module 2: Legal Language Transformation"],
    dependencies=[
        Depends(rate_limit("analyze_case", lambda: settings.rate_limit_case_analysis)),
        Depends(verify_optional_api_key),
    ],
)
def analyze_case(request: Request, payload: CaseAnalysisRequest):
    """Extract case metadata, material facts, issues, party arguments, reasoning, and outcomes."""
    req_id = getattr(request.state, "request_id", uuid.uuid4().hex)
    text = payload.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Judgment text must not be empty.")
    if len(text) > settings.max_text_length:
        raise HTTPException(
            status_code=400,
            detail=f"Input text exceeds maximum allowed length of {settings.max_text_length} characters.",
        )

    try:
        include_spans = payload.include_spans if payload.include_spans is not None else True
        return analyze_case_document(text, request_id=req_id, include_spans=include_spans)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


# =========================================================================
# Document Extraction Endpoints
# =========================================================================

@app.post(
    "/api/v1/documents/extract",
    response_model=DocumentExtractResponse,
    tags=["Document Processing"],
    dependencies=[
        Depends(rate_limit("extract_document", lambda: settings.rate_limit_extract)),
        Depends(verify_optional_api_key),
    ],
)
async def extract_document(request: Request, file: UploadFile = File(...)):
    """Extract per-page text from an uploaded PDF file safely using PyMuPDF."""
    req_id = getattr(request.state, "request_id", uuid.uuid4().hex)

    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=415, detail="Unsupported file format: Only PDF documents (.pdf) are supported.")

    # Memory-safe chunked read with strict cap to prevent memory exhaustion from oversized stream
    content = await file.read(settings.max_pdf_size_bytes + 1)

    # Size check
    if len(content) > settings.max_pdf_size_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds maximum allowed size of {settings.max_pdf_size_bytes} bytes (10 MB).",
        )

    # Magic byte check
    if not content.startswith(b"%PDF"):
        raise HTTPException(
            status_code=415,
            detail="File content does not match valid PDF specification (%PDF header missing).",
        )

    try:
        return extract_pdf_document(content, filename=file.filename, request_id=req_id)
    except ValueError as exc:
        msg = str(exc)
        if "exceeds maximum page limit" in msg:
            raise HTTPException(status_code=413, detail=msg)
        if "Corrupted or unreadable" in msg:
            raise HTTPException(status_code=400, detail="The uploaded PDF file is corrupted or unreadable.")
        raise HTTPException(status_code=400, detail=msg)
