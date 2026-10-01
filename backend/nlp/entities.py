"""Entity and structured fact extraction for legal text analysis."""

import re
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from nlp.retrieval import get_spacy_nlp


class FactOrigin(str, Enum):
    """Origin classification for extracted facts."""
    STATED = "stated"
    RULE_EXTRACTED = "rule_extracted"
    INFERRED = "inferred"


class EvidenceSpan(BaseModel):
    """Text span and character offsets in normalized input."""
    text: str = Field(..., description="Verbatim text span supporting the fact")
    start: int = Field(..., description="Starting character offset (inclusive)")
    end: int = Field(..., description="Ending character offset (exclusive)")


class ExtractedEntity(BaseModel):
    """Named entity or domain-specific legal entity."""
    text: str
    label: str  # PERSON, ORG, GPE, DATE, MONEY, IDENTIFIER, LEGAL_REF, CITATION, PROPERTY, ROLE
    start: int
    end: int
    normalized_value: Optional[str] = None


class ExtractedFact(BaseModel):
    """Structured fact grounded in textual evidence."""
    description: str = Field(..., description="Clear factual statement")
    actor: Optional[str] = Field(default=None, description="Identified actor/subject or None if unstated")
    action: Optional[str] = Field(default=None, description="Action or predicate asserted")
    evidence_span: EvidenceSpan = Field(..., description="Direct textual evidence")
    extraction_method: str = Field(..., description="Method used to extract this fact")
    confidence: Optional[float] = Field(default=None, description="Calibrated confidence if applicable")
    origin: FactOrigin = Field(default=FactOrigin.STATED, description="'stated', 'rule_extracted', or 'inferred'")


class ExtractionResult(BaseModel):
    """Aggregated entity and fact extraction output."""
    entities: List[ExtractedEntity]
    facts: List[ExtractedFact]
    consent_facts: List[ExtractedFact]
    intent_and_harm_facts: List[ExtractedFact]
    legal_references: List[ExtractedEntity]
    digital_identifiers: List[ExtractedEntity]


# Regex patterns for domain entities
EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")
URL_PATTERN = re.compile(r"\b(?:https?://|www\.)[^\s/$.?#].[^\s]*\b", re.IGNORECASE)
PHONE_PATTERN = re.compile(r"\b(?:\+91[-\s]?)?[6-9]\d{9}\b")
IP_PATTERN = re.compile(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b")
SOCIAL_HANDLE_PATTERN = re.compile(r"(?:^|(?<=\s))@([A-Za-z0-9_]{3,30})\b")

# Monetary patterns (INR specific & general)
MONEY_PATTERNS = [
    re.compile(r"(?:Rs\.?|INR|₹)\s*(\d+(?:,\d+)*(?:\.\d+)?(?:\s*(?:lakh|crore|thousand))?)", re.IGNORECASE),
    re.compile(r"\b(\d+(?:,\d+)*)\s*(?:rupees|lakhs?|crores?)\b", re.IGNORECASE),
]

# Statutory and citation patterns
STATUTE_REF_PATTERN = re.compile(
    r"\b(?:Section|Sec\.|u/s)\s+(\d+[A-Z]?)(?:\s+(?:of\s+(?:the\s+)?)?([A-Za-z\s]+(?:Act|Code|IPC|CrPC|CPC|IT\s+Act)))?\b",
    re.IGNORECASE,
)
CASE_CITATION_PATTERN = re.compile(
    r"\b(?:AIR\s+\d{4}\s+(?:SC|[A-Z]+)\s+\d+|\d{4}\s+(?:SCC|SCR)\s+\d+)\b",
    re.IGNORECASE,
)

# Consent patterns
CONSENT_PATTERNS = [
    re.compile(r"\bwithout\s+(?:my\s+|any\s+|prior\s+)?(?:permission|consent|knowledge|authority|authorization)\b", re.IGNORECASE),
    re.compile(r"\bagainst\s+(?:my|his|her|their)\s+will\b", re.IGNORECASE),
    re.compile(r"\brefused\s+(?:permission|consent)\b", re.IGNORECASE),
    re.compile(r"\bdid\s+not\s+(?:give|grant|provide|have)\s+(?:permission|consent)\b", re.IGNORECASE),
    re.compile(r"\bnon-consensual(?:ly)?\b", re.IGNORECASE),
]

# Intent and Harm patterns
INTENT_PATTERNS = [
    re.compile(r"\bwith\s+(?:the\s+)?intent\s+to\s+([a-z\s]+?)(?:[,.]|$)", re.IGNORECASE),
    re.compile(r"\b(?:intentionally|knowingly|fraudulently|dishonestly)\b", re.IGNORECASE),
]

THREAT_AND_HARM_PATTERNS = [
    re.compile(r"\bthreatened\s+(?:to\s+)?([a-z\s]+?)(?:[,.]|$)", re.IGNORECASE),
    re.compile(r"\bdemanded\s+([a-z0-9\s₹Rs.]+?)(?:[,.]|$)", re.IGNORECASE),
    re.compile(r"\bblackmailed\b", re.IGNORECASE),
    re.compile(r"\b(?:suffered|caused)\s+(?:a\s+)?(?:loss|damage|injury|harm|distress)(?:\s+of\s+([a-z0-9\s₹Rs.]+))?", re.IGNORECASE),
]

# Known legal and dispute roles
ROLE_TERMS = {
    "complainant": "ROLE_COMPLAINANT",
    "victim": "ROLE_VICTIM",
    "accused": "ROLE_ACCUSED",
    "suspect": "ROLE_ACCUSED",
    "landlord": "ROLE_LANDLORD",
    "tenant": "ROLE_TENANT",
    "lessee": "ROLE_LESSEE",
    "lessor": "ROLE_LESSOR",
    "buyer": "ROLE_BUYER",
    "seller": "ROLE_SELLER",
    "employer": "ROLE_EMPLOYER",
    "employee": "ROLE_EMPLOYEE",
}


def normalize_legal_term(term: str) -> str:
    """Normalize a legal term for robust dictionary matching.

    Lowercases, strips surrounding whitespace and punctuation.
    """
    if not term:
        return ""
    clean = term.strip().lower()
    # Strip common leading/trailing quotes or punctuation
    clean = re.sub(r"^[\s\"'‘“]+|[\s\"'’”.,;:!?]+$", "", clean)
    # Collapse internal whitespace
    clean = re.sub(r"\s+", " ", clean)
    return clean


def extract_digital_identifiers(text: str) -> List[ExtractedEntity]:
    """Extract digital identifiers (emails, URLs, phone numbers, IPs, handles)."""
    entities: List[ExtractedEntity] = []

    for match in EMAIL_PATTERN.finditer(text):
        entities.append(ExtractedEntity(
            text=match.group(0),
            label="EMAIL",
            start=match.start(),
            end=match.end(),
            normalized_value=match.group(0).lower(),
        ))

    for match in URL_PATTERN.finditer(text):
        entities.append(ExtractedEntity(
            text=match.group(0),
            label="URL",
            start=match.start(),
            end=match.end(),
            normalized_value=match.group(0),
        ))

    for match in PHONE_PATTERN.finditer(text):
        entities.append(ExtractedEntity(
            text=match.group(0),
            label="PHONE",
            start=match.start(),
            end=match.end(),
            normalized_value=re.sub(r"\D", "", match.group(0)),
        ))

    for match in IP_PATTERN.finditer(text):
        entities.append(ExtractedEntity(
            text=match.group(0),
            label="IP_ADDRESS",
            start=match.start(),
            end=match.end(),
            normalized_value=match.group(0),
        ))

    for match in SOCIAL_HANDLE_PATTERN.finditer(text):
        entities.append(ExtractedEntity(
            text=match.group(0),
            label="SOCIAL_HANDLE",
            start=match.start(),
            end=match.end(),
            normalized_value=match.group(1).lower(),
        ))

    return entities


def extract_legal_references(text: str) -> List[ExtractedEntity]:
    """Extract references to statutory sections and court citations."""
    entities: List[ExtractedEntity] = []

    for match in STATUTE_REF_PATTERN.finditer(text):
        full_match = match.group(0)
        entities.append(ExtractedEntity(
            text=full_match,
            label="STATUTE_SECTION",
            start=match.start(),
            end=match.end(),
            normalized_value=full_match.strip(),
        ))

    for match in CASE_CITATION_PATTERN.finditer(text):
        full_match = match.group(0)
        entities.append(ExtractedEntity(
            text=full_match,
            label="CASE_CITATION",
            start=match.start(),
            end=match.end(),
            normalized_value=re.sub(r"\s+", " ", full_match.strip().upper()),
        ))

    return entities


def extract_consent_facts(text: str) -> List[ExtractedFact]:
    """Identify explicit assertions regarding consent or absence thereof."""
    facts: List[ExtractedFact] = []

    for pattern in CONSENT_PATTERNS:
        for match in pattern.finditer(text):
            span_text = match.group(0)
            facts.append(ExtractedFact(
                description=f"Stated lack of permission or consent: '{span_text}'",
                actor="complainant",
                action="absence_of_consent",
                evidence_span=EvidenceSpan(
                    text=span_text,
                    start=match.start(),
                    end=match.end(),
                ),
                extraction_method="regex_pattern",
                origin=FactOrigin.STATED,
            ))

    return facts


def extract_intent_and_harm_facts(text: str) -> List[ExtractedFact]:
    """Identify assertions of intent, threats, harassment, or harm."""
    facts: List[ExtractedFact] = []

    for pattern in INTENT_PATTERNS:
        for match in pattern.finditer(text):
            span_text = match.group(0)
            facts.append(ExtractedFact(
                description=f"Stated intent/mens rea: '{span_text}'",
                action="intent",
                evidence_span=EvidenceSpan(
                    text=span_text,
                    start=match.start(),
                    end=match.end(),
                ),
                extraction_method="keyword_pattern",
                origin=FactOrigin.STATED,
            ))

    for pattern in THREAT_AND_HARM_PATTERNS:
        for match in pattern.finditer(text):
            span_text = match.group(0)
            facts.append(ExtractedFact(
                description=f"Stated threat, extortion, or harm: '{span_text}'",
                action="harm_or_threat",
                evidence_span=EvidenceSpan(
                    text=span_text,
                    start=match.start(),
                    end=match.end(),
                ),
                extraction_method="keyword_pattern",
                origin=FactOrigin.STATED,
            ))

    return facts


def extract_action_facts(text: str, nlp_doc: Optional[Any] = None) -> List[ExtractedFact]:
    """Extract action/event facts using linguistic dependency parsing."""
    facts: List[ExtractedFact] = []
    nlp = get_spacy_nlp()

    doc = nlp_doc if nlp_doc is not None else (nlp(text) if nlp is not None else None)

    if doc is not None:
        for sent in doc.sents:
            # Find root verbs or main predicates
            for token in sent:
                if token.pos_ in ("VERB", "AUX") and token.dep_ in ("ROOT", "conj", "advcl", "relcl"):
                    # Find subject
                    subjects = [w for w in token.children if w.dep_ in ("nsubj", "nsubjpass")]
                    # Find object
                    objects = [w for w in token.children if w.dep_ in ("dobj", "pobj", "attr", "dative")]
                    # Check negation
                    negations = [w for w in token.children if w.dep_ == "neg"]

                    actor = subjects[0].text if subjects else None
                    neg_prefix = f"{negations[0].text} " if negations else ""
                    action = f"{neg_prefix}{token.lemma_}"

                    # Construct full predicate description
                    target_phrase = ""
                    if objects:
                        # Grab subtree of direct object
                        obj_span = "".join([t.text_with_ws for t in objects[0].subtree]).strip()
                        target_phrase = f" target: '{obj_span}'"

                    desc = f"Action: '{actor or 'Unspecified actor'}' {action}{target_phrase}"

                    # Use sentence or verbal subtree as evidence span
                    verb_subtree_tokens = list(token.subtree)
                    start_char = verb_subtree_tokens[0].idx
                    end_char = verb_subtree_tokens[-1].idx + len(verb_subtree_tokens[-1].text)
                    evidence_text = text[start_char:end_char] if 0 <= start_char < len(text) else sent.text

                    facts.append(ExtractedFact(
                        description=desc,
                        actor=actor,
                        action=action,
                        evidence_span=EvidenceSpan(
                            text=evidence_text,
                            start=max(0, start_char),
                            end=min(len(text), end_char),
                        ),
                        extraction_method="dependency_parse",
                        origin=FactOrigin.STATED,
                    ))

    return facts


def extract_all_facts(text: str) -> ExtractionResult:
    """Run full entity and fact extraction on input text."""
    entities: List[ExtractedEntity] = []

    # 1. Digital and communication identifiers
    digital_ids = extract_digital_identifiers(text)
    entities.extend(digital_ids)

    # 2. Statutory and citation references
    legal_refs = extract_legal_references(text)
    entities.extend(legal_refs)

    # 3. Monetary amounts via regex
    for pattern in MONEY_PATTERNS:
        for match in pattern.finditer(text):
            entities.append(ExtractedEntity(
                text=match.group(0),
                label="MONEY",
                start=match.start(),
                end=match.end(),
                normalized_value=match.group(0).strip(),
            ))

    # 4. SpaCy NER entities
    nlp = get_spacy_nlp()
    doc = nlp(text) if nlp is not None else None

    if doc is not None:
        for ent in doc.ents:
            # Map spaCy entity labels
            if ent.label_ in ("PERSON", "ORG", "GPE", "LOC", "FAC", "DATE", "TIME"):
                entities.append(ExtractedEntity(
                    text=ent.text,
                    label=ent.label_,
                    start=ent.start_char,
                    end=ent.end_char,
                    normalized_value=ent.text.strip(),
                ))

    # 5. Roles mentioned in text
    lower_text = text.lower()
    for role_term, role_label in ROLE_TERMS.items():
        for match in re.finditer(rf"\b{role_term}\b", lower_text):
            entities.append(ExtractedEntity(
                text=text[match.start():match.end()],
                label=role_label,
                start=match.start(),
                end=match.end(),
                normalized_value=role_term,
            ))

    # 6. Structured Facts
    facts: List[ExtractedFact] = []

    # Consent facts
    consent_facts = extract_consent_facts(text)
    facts.extend(consent_facts)

    # Intent and harm facts
    intent_harm_facts = extract_intent_and_harm_facts(text)
    facts.extend(intent_harm_facts)

    # Action / predicate facts
    action_facts = extract_action_facts(text, nlp_doc=doc)
    facts.extend(action_facts)

    return ExtractionResult(
        entities=sorted(entities, key=lambda e: e.start),
        facts=facts,
        consent_facts=consent_facts,
        intent_and_harm_facts=intent_harm_facts,
        legal_references=legal_refs,
        digital_identifiers=digital_ids,
    )
