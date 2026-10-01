"""NLP preprocessing pipeline for LexiLaw.

Handles input normalization, English language validation, sentence segmentation,
linguistic analysis via spaCy, and preservation of legal qualifications and negations.
"""

import re
import unicodedata
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from nlp.retrieval import get_spacy_nlp


class NonEnglishInputError(ValueError):
    """Raised when input text is detected to be predominantly non-English."""
    pass


class TokenSpan(BaseModel):
    """Token representation with linguistic annotations."""
    text: str
    lemma: str
    pos: str
    dep: str
    is_stop: bool
    start_char: int
    end_char: int


class SentenceSpan(BaseModel):
    """Sentence segment with character offsets in normalized text."""
    text: str
    start_char: int
    end_char: int
    tokens: List[TokenSpan] = Field(default_factory=list)


class LegalQualifier(BaseModel):
    """Detected legal qualification, condition, or proviso."""
    qualifier_type: str
    matched_text: str
    start_char: int
    end_char: int


class PreprocessedDocument(BaseModel):
    """Structured result of preprocessing an input text."""
    raw_text: str
    normalized_text: str
    sentences: List[SentenceSpan]
    tokens_count: int
    has_negation: bool
    negation_spans: List[Dict[str, Any]]
    legal_qualifiers: List[LegalQualifier]
    modals_present: List[str]


# Patterns for legal qualifiers that must never be stripped or altered
LEGAL_QUALIFIER_PATTERNS = [
    (r"\bnotwithstanding\b", "notwithstanding"),
    (r"\bsubject\s+to\b", "subject_to"),
    (r"\bprovided\s+that\b", "provided_that"),
    (r"\bprovided\s+further\s+that\b", "provided_further_that"),
    (r"\bwithout\s+prejudice\s+to\b", "without_prejudice_to"),
    (r"\bexcept\s+(as|where|when)?\b", "exception"),
    (r"\bunless\s+(otherwise)?\b", "conditional_unless"),
    (r"\bin\s+accordance\s+with\b", "compliance"),
    (r"\bpursuant\s+to\b", "pursuant_to"),
    (r"\bsave\s+as\s+otherwise\b", "exception_save_as"),
]

# Modal verbs that convey obligation or discretion in legal analysis
LEGAL_MODALS = {"shall", "must", "may", "ought", "should"}

# Negation indicators
NEGATION_PATTERNS = [
    r"\bnot\b",
    r"\bno\b",
    r"\bnever\b",
    r"\bneither\b",
    r"\bnor\b",
    r"\bwithout\b",
    r"\bcannot\b",
    r"\bnone\b",
    r"n't\b",
]


def detect_english_only(text: str) -> None:
    """Validate that text is predominantly Latin/English.

    Raises NonEnglishInputError if substantial non-Latin characters are detected.
    """
    alpha_chars = [c for c in text if c.isalpha()]
    if not alpha_chars:
        return  # Numbers, punctuation, etc. handled by empty check

    non_latin_count = 0
    for char in alpha_chars:
        name = unicodedata.name(char, "")
        # Standard Latin alphabet letters contain 'LATIN' in their Unicode character name
        if "LATIN" not in name:
            non_latin_count += 1

    ratio = non_latin_count / len(alpha_chars)
    if ratio > 0.15:
        raise NonEnglishInputError(
            "Phase 1 supports English-language input only. Non-English text detected."
        )


def normalize_text(text: str) -> str:
    """Normalize whitespace and Unicode while preserving punctuation and casing."""
    if not text or not text.strip():
        raise ValueError("Input text must not be empty.")

    # Unicode NFKC normalization
    normalized = unicodedata.normalize("NFKC", text)

    # Standardize line endings
    normalized = normalized.replace("\r\n", "\n").replace("\r", "\n")

    # Collapse multiple consecutive non-newline whitespace characters
    normalized = re.sub(r"[ \t]+", " ", normalized)

    # Collapse excessive newlines (keep at most 2 for paragraph breaks)
    normalized = re.sub(r"\n{3,}", "\n\n", normalized)

    return normalized.strip()


def extract_legal_qualifiers(text: str) -> List[LegalQualifier]:
    """Identify and record spans of explicit legal qualifiers."""
    qualifiers: List[LegalQualifier] = []
    lower_text = text.lower()
    for pattern, q_type in LEGAL_QUALIFIER_PATTERNS:
        for match in re.finditer(pattern, lower_text):
            qualifiers.append(
                LegalQualifier(
                    qualifier_type=q_type,
                    matched_text=text[match.start():match.end()],
                    start_char=match.start(),
                    end_char=match.end(),
                )
            )
    return sorted(qualifiers, key=lambda q: q.start_char)


def extract_negation_spans(text: str) -> List[Dict[str, Any]]:
    """Identify negation markers with exact character offsets."""
    negations: List[Dict[str, Any]] = []
    lower_text = text.lower()
    for pattern in NEGATION_PATTERNS:
        for match in re.finditer(pattern, lower_text):
            negations.append({
                "matched_text": text[match.start():match.end()],
                "start_char": match.start(),
                "end_char": match.end(),
            })
    return sorted(negations, key=lambda n: n["start_char"])


def preprocess_text(text: str) -> PreprocessedDocument:
    """Full preprocessing pipeline.

    Validates language, normalizes text, segments sentences, parses tokens,
    and extracts legal qualifiers and negation spans.
    """
    if not isinstance(text, str):
        raise TypeError("Input text must be a string.")

    cleaned = text.strip()
    if not cleaned:
        raise ValueError("Input text must not be empty.")

    detect_english_only(cleaned)
    normalized = normalize_text(cleaned)

    nlp = get_spacy_nlp()

    sentences: List[SentenceSpan] = []
    modals_found: set = set()

    if nlp is not None:
        doc = nlp(normalized)
        for sent in doc.sents:
            token_spans: List[TokenSpan] = []
            for token in sent:
                if token.text.lower() in LEGAL_MODALS:
                    modals_found.add(token.text.lower())

                token_spans.append(
                    TokenSpan(
                        text=token.text,
                        lemma=token.lemma_,
                        pos=token.pos_,
                        dep=token.dep_,
                        is_stop=token.is_stop,
                        start_char=token.idx,
                        end_char=token.idx + len(token.text),
                    )
                )

            sentences.append(
                SentenceSpan(
                    text=sent.text.strip(),
                    start_char=sent.start_char,
                    end_char=sent.end_char,
                    tokens=token_spans,
                )
            )
    else:
        # Fallback when spaCy is not available: basic regex sentence splitter
        # Preserve functionality without crashing
        raw_sents = re.split(r"(?<=[.!?])\s+", normalized)
        curr_offset = 0
        for s in raw_sents:
            s_clean = s.strip()
            if not s_clean:
                continue
            start = normalized.find(s_clean, curr_offset)
            end = start + len(s_clean)
            curr_offset = end

            # Basic whitespace tokenization
            tokens: List[TokenSpan] = []
            for word_match in re.finditer(r"\b\w+\b|[^\w\s]", s_clean):
                w = word_match.group(0)
                if w.lower() in LEGAL_MODALS:
                    modals_found.add(w.lower())
                tokens.append(
                    TokenSpan(
                        text=w,
                        lemma=w.lower(),
                        pos="UNKNOWN",
                        dep="UNKNOWN",
                        is_stop=False,
                        start_char=start + word_match.start(),
                        end_char=start + word_match.end(),
                    )
                )

            sentences.append(
                SentenceSpan(
                    text=s_clean,
                    start_char=start,
                    end_char=end,
                    tokens=tokens,
                )
            )

    legal_qualifiers = extract_legal_qualifiers(normalized)
    negations = extract_negation_spans(normalized)
    total_tokens = sum(len(s.tokens) for s in sentences)

    return PreprocessedDocument(
        raw_text=text,
        normalized_text=normalized,
        sentences=sentences,
        tokens_count=total_tokens,
        has_negation=len(negations) > 0,
        negation_spans=negations,
        legal_qualifiers=legal_qualifiers,
        modals_present=sorted(list(modals_found)),
    )
