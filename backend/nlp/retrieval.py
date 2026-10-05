from datetime import date
import json
import logging
from pathlib import Path
import re
from typing import Any, Dict, List, Optional, Union
import numpy as np
from pydantic import BaseModel, Field
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from config import (
    LEGAL_PROVISIONS_PATH,
    LEGAL_TERMS_PATH,
    settings,
)

logger = logging.getLogger("lexilaw.retrieval")

# Global lazy singletons
_SPACY_NLP = None
_SPACY_LOAD_FAILED = False
_SEMANTIC_MODEL = None
_SEMANTIC_LOAD_FAILED = False
_DEFAULT_CORPUS_INDEX: Optional["LegalCorpusIndex"] = None


class LegalElement(BaseModel):
    """An individual legal element required to establish a provision."""

    element_id: str = Field(..., description="Unique element identifier, e.g. ELEM_1")
    description: str = Field(..., description="Description of the legal element requirement")
    keywords: List[str] = Field(default_factory=list, description="Keywords or patterns associated with the element")


class LegalProvision(BaseModel):
    """Schema for a verified statutory provision."""

    id: str = Field(..., description="Unique identifier for the provision, e.g. IPC_S419")
    jurisdiction: str = Field(default="India", description="Applicable legal jurisdiction")
    act_name: str = Field(..., description="Official title of the statute or act")
    section_id: str = Field(..., description="Section or article identifier")
    title: str = Field(..., description="Title of the section")
    source_text: str = Field(..., description="Verbatim or authoritative statutory text")
    plain_language_summary: str = Field(..., description="Plain-language description of the provision")
    legal_elements: List[LegalElement] = Field(
        default_factory=list, description="Constituent legal elements of the provision"
    )
    exceptions_or_qualifications: Optional[str] = Field(
        default=None, description="Statutory exceptions, provisos, or qualifications"
    )
    penalty_text: Optional[str] = Field(
        default=None, description="Stated statutory penalty text from verified source"
    )
    official_source_url: str = Field(..., description="Official source URL, e.g. indiacode.nic.in")
    source_authority: str = Field(..., description="Authoritative publisher or gazette reference")
    source_verified: bool = Field(default=False, description="Whether record is verified against official source")
    verified_at: Optional[str] = Field(default=None, description="ISO timestamp of official source verification")
    effective_from: Optional[str] = Field(default=None, description="Date or year the provision became effective")
    effective_to: Optional[str] = Field(default=None, description="Date or year repealed/amended, or None if current")
    version_label: str = Field(default="original", description="Statutory amendment or version label")
    source_document_identifier: Optional[str] = Field(
        default=None, description="Identifier of the source gazette/document"
    )


class LegalTerm(BaseModel):
    """Schema for a legal terminology dictionary record."""

    term: str = Field(..., description="Legal term or phrase")
    plain_language_meaning: str = Field(..., description="Clear plain-language explanation")
    legal_context: Optional[str] = Field(default=None, description="Context in which term appears")
    example_usage: Optional[str] = Field(default=None, description="Example sentence or statutory context")
    related_terms: List[str] = Field(default_factory=list, description="Synonyms or related legal terms")
    source: Optional[str] = Field(default=None, description="Citation or source of definition")
    verification_status: str = Field(default="unverified", description="'verified' or 'unverified'")


class CandidateProvision(BaseModel):
    """Ranked retrieval candidate with scores and metadata."""

    provision: LegalProvision
    lexical_score: float = Field(..., description="Lexical TF-IDF cosine similarity [0.0 - 1.0]")
    semantic_score: Optional[float] = Field(default=None, description="Dense embedding cosine similarity if available")
    relevance_score: float = Field(..., description="Combined relevance score used for ranking")
    penalty_displayed: Optional[str] = Field(
        default=None,
        description="Penalty text only displayed if record is verified against official sources",
    )


def load_legal_provisions(file_path: Optional[Path] = None) -> List[LegalProvision]:
    """Load and validate statutory provisions from a JSON file."""
    path = file_path or LEGAL_PROVISIONS_PATH
    if not path.exists():
        logger.warning(f"Legal provisions file not found: {path}")
        return []

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as exc:
        logger.error(f"Failed to decode legal provisions JSON: {exc}")
        raise ValueError(f"Malformed JSON in legal provisions file: {exc}") from exc

    if not isinstance(data, list):
        raise ValueError(f"Legal provisions data must be a JSON array, got {type(data).__name__}")

    provisions: List[LegalProvision] = []
    for idx, item in enumerate(data):
        try:
            provisions.append(LegalProvision.model_validate(item))
        except Exception as exc:
            logger.error(f"Error validating provision at index {idx}: {exc}")
            raise ValueError(f"Invalid provision record at index {idx}: {exc}") from exc

    return provisions


def load_legal_terms(file_path: Optional[Path] = None) -> List[LegalTerm]:
    """Load and validate legal terminology dictionary from a JSON file."""
    path = file_path or LEGAL_TERMS_PATH
    if not path.exists():
        logger.warning(f"Legal terms file not found: {path}")
        return []

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as exc:
        logger.error(f"Failed to decode legal terms JSON: {exc}")
        raise ValueError(f"Malformed JSON in legal terms file: {exc}") from exc

    if not isinstance(data, list):
        raise ValueError(f"Legal terms data must be a JSON array, got {type(data).__name__}")

    terms: List[LegalTerm] = []
    for idx, item in enumerate(data):
        try:
            terms.append(LegalTerm.model_validate(item))
        except Exception as exc:
            logger.error(f"Error validating legal term at index {idx}: {exc}")
            raise ValueError(f"Invalid legal term record at index {idx}: {exc}") from exc

    return terms


def get_corpus_status_info(file_path: Optional[Path] = None) -> Dict[str, Any]:
    """Inspect the corpus file and report current record counts and status."""
    try:
        provisions = load_legal_provisions(file_path)
    except Exception as exc:
        logger.error(f"Error inspecting corpus: {exc}")
        return {
            "corpus_record_count": 0,
            "verified_record_count": 0,
            "corpus_status": "error",
            "error_detail": str(exc),
        }

    total = len(provisions)
    verified = sum(1 for p in provisions if p.source_verified)

    if total == 0:
        status = "empty"
    elif verified < total:
        status = "partial_unverified"
    else:
        status = "loaded"

    return {
        "corpus_record_count": total,
        "verified_record_count": verified,
        "corpus_status": status,
    }


def get_spacy_nlp():
    """Lazily load the spaCy model. Never downloads automatically."""
    global _SPACY_NLP, _SPACY_LOAD_FAILED
    if _SPACY_NLP is not None:
        return _SPACY_NLP
    if _SPACY_LOAD_FAILED:
        return None

    try:
        import spacy

        _SPACY_NLP = spacy.load(settings.spacy_model)
        logger.info(f"Loaded spaCy model: {settings.spacy_model}")
        return _SPACY_NLP
    except Exception as exc:
        _SPACY_LOAD_FAILED = True
        logger.warning(
            f"Failed to load spaCy model '{settings.spacy_model}': {exc}. "
            f"Install it with: python -m spacy download {settings.spacy_model}"
        )
        return None


def is_spacy_available() -> bool:
    """Check if the configured spaCy model is loaded and ready."""
    return get_spacy_nlp() is not None


def get_semantic_model():
    """Lazily load sentence-transformers model strictly from local storage."""
    global _SEMANTIC_MODEL, _SEMANTIC_LOAD_FAILED
    if settings.disable_semantic_model:
        return None
    if _SEMANTIC_MODEL is not None:
        return _SEMANTIC_MODEL
    if _SEMANTIC_LOAD_FAILED:
        return None

    try:
        from sentence_transformers import SentenceTransformer

        # Strictly local loading: never download over internet at runtime/startup
        _SEMANTIC_MODEL = SentenceTransformer(
            settings.semantic_model_name_or_path,
            local_files_only=True,
        )
        logger.info(f"Loaded semantic model: {settings.semantic_model_name_or_path}")
        return _SEMANTIC_MODEL
    except Exception as exc:
        _SEMANTIC_LOAD_FAILED = True
        logger.info(
            f"Semantic model '{settings.semantic_model_name_or_path}' not loaded locally ({exc}). "
            f"Falling back to TF-IDF retrieval."
        )
        return None


def is_semantic_model_available() -> bool:
    """Check if the semantic retrieval model is loaded."""
    return get_semantic_model() is not None


# --- Out-of-Scope Civil / Regulatory Pattern Detection ---
OUT_OF_SCOPE_CIVIL_PATTERNS = [
    # Tenancy & lease default
    r"\b(?:tenant|landlord|rent(?:\s+payments?|\s+default)?|lease\s+expiry|vacate\s+premise)\b",
    # Minor traffic infractions / challans
    r"\b(?:traffic\s+challan|traffic\s+ticket|traffic\s+fine|running\s+a\s+red\s+light|speeding\s+ticket)\b",
    # Municipal taxes & assessment notices
    r"\b(?:property\s+tax|municipal\s+corporation|tax\s+assessment\s+notice|tax\s+surcharge|utility\s+bill)\b",
    # Airline & consumer refunds
    r"\b(?:airline\s+cancelled|flight\s+cancell(?:ed|ation)|customer\s+service\s+refused|process\s+a\s+refund|consumer\s+complaint)\b",
    # Trademark counterfeiting (governed by Trade Marks Act 1999, not penal document forgery)
    r"\b(?:counterfeit\s+(?:branded\s+)?(?:handbags?|shoes?|clothes?|goods?|products?)|registered\s+trademark\s+logo|trademark\s+infringement)\b",
    # Public non-intimate audio recording in restaurant
    r"\b(?:recorded\s+a\s+conversation\s+in\s+a\s+restaurant|conversation\s+without\s+informing|secretly\s+recorded\s+dinner)\b",
]

# Explicit penal indicators that override civil patterns (exceptions)
PENAL_OVERRIDE_PATTERNS = [
    r"\b(?:kill|murder|grievous\s+hurt|stab|shoot|extort|blackmail|ransom)\b",
    r"\b(?:hack|malware|ransomware|trojan|ddos|databank)\b",
    r"\b(?:naked|intimate\s+photos?|private\s+parts?|changing\s+room|washroom|bathroom|voyeurism)\b",
    r"\b(?:forged\s+(?:deed|agreement|will|passport|stamp|cheque)|fake\s+stamp\s+paper)\b",
]


def is_out_of_scope_civil_incident(query: str) -> bool:
    """Detect purely civil, regulatory, or administrative matters lacking penal elements."""
    q_lower = query.lower()

    # Check if any penal override exists
    for pop in PENAL_OVERRIDE_PATTERNS:
        if re.search(pop, q_lower):
            return False

    # Check if civil/out-of-scope pattern matches
    for cop in OUT_OF_SCOPE_CIVIL_PATTERNS:
        if re.search(cop, q_lower):
            return True

    return False


def detect_incident_temporal_era(
    query: str, explicit_date: Optional[Union[date, str]] = None
) -> str:
    """Classify incident into 'pre_july_2024', 'post_july_2024', or 'unspecified'."""
    if explicit_date is not None:
        if isinstance(explicit_date, str):
            try:
                explicit_date = date.fromisoformat(explicit_date.split("T")[0])
            except Exception:
                explicit_date = None

        if isinstance(explicit_date, date):
            return "pre_july_2024" if explicit_date < date(2024, 7, 1) else "post_july_2024"

    q_lower = query.lower()

    # Pre-July 2024 markers
    pre_markers = [
        "2023", "2022", "2021", "2020", "2019", "2018",
        "january 2024", "february 2024", "march 2024", "april 2024", "may 2024", "june 2024",
        "prior to july 2024", "before july 2024", "pre-july 2024"
    ]
    if any(m in q_lower for m in pre_markers):
        return "pre_july_2024"

    # Post-July 2024 markers
    post_markers = [
        "2025", "2026", "2027",
        "july 2024", "august 2024", "september 2024", "october 2024", "november 2024", "december 2024",
        "after july 2024", "post july 2024"
    ]
    if any(m in q_lower for m in post_markers):
        return "post_july_2024"

    return "unspecified"


class LegalCorpusIndex:
    """Retrieval index over legal provisions supporting lexical and semantic retrieval."""

    def __init__(self, provisions: Optional[List[LegalProvision]] = None):
        self.provisions: List[LegalProvision] = provisions or []
        self.doc_texts: List[str] = []
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.tfidf_matrix = None
        self.semantic_embeddings: Optional[np.ndarray] = None
        if self.provisions:
            self._build_index()

    def _build_doc_text(self, p: LegalProvision) -> str:
        """Compose searchable text representation for a provision."""
        keywords_str = " ".join([k for elem in p.legal_elements for k in elem.keywords])
        return (
            f"{p.act_name} {p.section_id} {p.title}. "
            f"{p.plain_language_summary}. "
            f"{p.source_text}. "
            f"{keywords_str}"
        )

    def _build_index(self) -> None:
        """Construct TF-IDF and dense embeddings for provisions."""
        if not self.provisions:
            return

        self.doc_texts = [self._build_doc_text(p) for p in self.provisions]

        # Lexical Indexing: TF-IDF with sublinear term frequency scaling
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            sublinear_tf=True,
            stop_words="english",
        )
        self.tfidf_matrix = self.vectorizer.fit_transform(self.doc_texts)

        # Semantic Indexing: if model is available locally
        semantic_model = get_semantic_model()
        if semantic_model is not None:
            try:
                embeddings = semantic_model.encode(
                    self.doc_texts,
                    convert_to_numpy=True,
                    normalize_embeddings=True,
                )
                self.semantic_embeddings = embeddings
            except Exception as exc:
                logger.warning(f"Failed to generate semantic embeddings: {exc}")
                self.semantic_embeddings = None

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        min_score: float = 0.05,
        include_uncommenced: Optional[bool] = None,
        incident_date: Optional[Union[date, str]] = None,
        filter_out_of_scope: bool = True,
    ) -> List[CandidateProvision]:
        """Retrieve and rank candidate legal provisions against a query.

        Returns empty list if corpus is empty or no candidates meet min_score.
        """
        if not self.provisions or self.tfidf_matrix is None or not self.vectorizer:
            return []

        clean_query = query.strip()
        if not clean_query:
            return []

        # Civil / Out-of-Scope gatekeeper
        if filter_out_of_scope and is_out_of_scope_civil_incident(clean_query):
            return []

        # Bound top_k
        effective_top_k = max(1, min(top_k, settings.max_top_k))

        # 1. Lexical retrieval via TF-IDF cosine similarity
        query_tfidf = self.vectorizer.transform([clean_query])
        lexical_sims = cosine_similarity(query_tfidf, self.tfidf_matrix)[0]

        # 2. Semantic retrieval (if embeddings and model available)
        semantic_sims = None
        semantic_model = get_semantic_model()
        if semantic_model is not None and self.semantic_embeddings is not None:
            try:
                q_emb = semantic_model.encode(
                    [clean_query],
                    convert_to_numpy=True,
                    normalize_embeddings=True,
                )
                semantic_sims = cosine_similarity(q_emb, self.semantic_embeddings)[0]
            except Exception as exc:
                logger.warning(f"Semantic scoring error: {exc}")
                semantic_sims = None

        era = detect_incident_temporal_era(clean_query, incident_date)
        candidates: List[CandidateProvision] = []

        for idx, provision in enumerate(self.provisions):
            # Check uncommenced / provisional exclusion
            is_uncommenced = (
                provision.effective_from is None
                and (
                    not provision.source_verified
                    or "_UNCOMMENCED" in provision.id
                    or "_PROVISIONAL" in provision.id
                )
            )
            allow_uncommenced = (
                include_uncommenced
                if include_uncommenced is not None
                else (min_score < 0.05)
            )
            if (
                not allow_uncommenced
                and is_uncommenced
                and any(p.source_verified for p in self.provisions)
            ):
                continue

            lex_score = float(lexical_sims[idx])

            if semantic_sims is not None:
                sem_score = float(semantic_sims[idx])
                # Combined ranking: 0.4 lexical + 0.6 semantic
                combined_score = float(0.4 * lex_score + 0.6 * sem_score)
            else:
                sem_score = None
                combined_score = lex_score

            # Temporal alignment based on Article 20(1) and Section 358 BNS
            if era == "pre_july_2024":
                # BNS cannot apply retroactively under Art. 20(1)
                if provision.act_name == "Bharatiya Nyaya Sanhita, 2023":
                    continue
            elif era == "post_july_2024":
                # IPC is repealed
                if provision.act_name == "Indian Penal Code, 1860":
                    continue
            elif era == "unspecified":
                # Active law (BNS) preferred over repealed law (IPC) when date omitted
                if provision.act_name == "Indian Penal Code, 1860":
                    combined_score = round(combined_score * 0.85, 4)

            if combined_score < min_score:
                continue

            # Strict penalty text rule: only shown if verified against official records
            penalty = (
                provision.penalty_text
                if (provision.source_verified and provision.penalty_text)
                else None
            )

            candidates.append(
                CandidateProvision(
                    provision=provision,
                    lexical_score=round(lex_score, 4),
                    semantic_score=round(sem_score, 4) if sem_score is not None else None,
                    relevance_score=round(combined_score, 4),
                    penalty_displayed=penalty,
                )
            )

        # Deterministic sorting: highest relevance first, then lexical score, then provision id
        candidates.sort(
            key=lambda c: (-c.relevance_score, -c.lexical_score, c.provision.id)
        )

        return candidates[:effective_top_k]


def get_corpus_index(
    custom_path: Optional[Path] = None,
    force_reload: bool = False,
) -> LegalCorpusIndex:
    """Retrieve or build the corpus index singleton."""
    global _DEFAULT_CORPUS_INDEX
    if custom_path is not None:
        provisions = load_legal_provisions(custom_path)
        return LegalCorpusIndex(provisions)

    if _DEFAULT_CORPUS_INDEX is None or force_reload:
        provisions = load_legal_provisions(LEGAL_PROVISIONS_PATH)
        _DEFAULT_CORPUS_INDEX = LegalCorpusIndex(provisions)

    return _DEFAULT_CORPUS_INDEX
