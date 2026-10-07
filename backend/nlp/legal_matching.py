"""Legal element matching, support status evaluation, and follow-up question generation."""

from enum import Enum
import re
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from nlp.entities import EvidenceSpan, ExtractedFact
from nlp.preprocessing import PreprocessedDocument
from nlp.retrieval import LegalElement, LegalProvision


class ElementStatus(str, Enum):
    """Evaluation status of an individual statutory element."""
    SUPPORTED = "supported"
    CONTRADICTED = "contradicted"
    NOT_ESTABLISHED = "not_established"
    NOT_EVALUATED = "not_evaluated"


class ElementMatchResult(BaseModel):
    """Detailed match evaluation for a single statutory element."""
    element_id: str
    description: str
    status: ElementStatus
    evidence_spans: List[EvidenceSpan] = Field(default_factory=list)
    reasoning: str
    evaluation_origin: str = "stated_facts"  # "stated_facts", "contextual_answer", "unestablished"


class FollowUpQuestion(BaseModel):
    """Focused neutral question targeting unestablished statutory elements."""
    question_id: str
    provision_id: str
    element_id: str
    question_text: str
    context_note: str


# Affirmative consent patterns that indicate explicit contradiction of absence-of-consent elements
AFFIRMATIVE_CONSENT_PATTERNS = [
    re.compile(
        r"\bwith\s+(?:(?:my|our|his|her|their|explicit|prior|written|full)\s+)*(?:permission|consent|approval|authorization)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(?:i|we|he|she|they)\s+(?:gave|granted|provided|authorized|had)\s+(?:(?:my|our|prior|explicit|full)\s+)*(?:permission|consent)\b",
        re.IGNORECASE,
    ),
    re.compile(r"\bconsensual(?:ly)?\b", re.IGNORECASE),
]


def evaluate_element_against_facts(
    element: LegalElement,
    facts: List[ExtractedFact],
    doc: PreprocessedDocument,
    contextual_answers: Optional[Dict[str, str]] = None,
    provision_id: str = "",
) -> ElementMatchResult:
    """Evaluate whether a single statutory element is supported, contradicted, or not established.

    Rules:
    1. Contextual answers have priority if provided.
    2. Missing facts are strictly NOT_ESTABLISHED, never CONTRADICTED.
    3. Keyword presence alone does not establish an element; factual context is checked.
    """
    answers = contextual_answers or {}
    expected_q_id = f"Q_{provision_id}_{element.element_id}"
    user_answer = answers.get(expected_q_id) or answers.get(element.element_id)

    # 1. Check contextual answers
    if user_answer:
        clean_ans = user_answer.strip().lower()
        # Direct affirmative or confirming absence of consent
        if any(aff in clean_ans for aff in ["yes", "correct", "did not permit", "no consent", "unauthorized"]):
            return ElementMatchResult(
                element_id=element.element_id,
                description=element.description,
                status=ElementStatus.SUPPORTED,
                evidence_spans=[EvidenceSpan(text=user_answer, start=0, end=len(user_answer))],
                reasoning=f"Affirmed by user contextual answer: '{user_answer}'.",
                evaluation_origin="contextual_answer",
            )
        elif any(neg in clean_ans for neg in ["no", "never happened", "i consented", "i gave permission"]):
            return ElementMatchResult(
                element_id=element.element_id,
                description=element.description,
                status=ElementStatus.CONTRADICTED,
                evidence_spans=[EvidenceSpan(text=user_answer, start=0, end=len(user_answer))],
                reasoning=f"Contradicted by user contextual answer: '{user_answer}'.",
                evaluation_origin="contextual_answer",
            )

    normalized_text = doc.normalized_text.lower()
    desc_lower = element.description.lower()
    keywords = [k.lower() for k in element.keywords]

    # 2. Check for absence of consent elements
    if any(term in desc_lower or any(term in k for k in keywords) for term in ["consent", "permission", "authorization"]):
        # Check explicit affirmative consent contradiction
        for aff_pat in AFFIRMATIVE_CONSENT_PATTERNS:
            match = aff_pat.search(doc.normalized_text)
            if match:
                return ElementMatchResult(
                    element_id=element.element_id,
                    description=element.description,
                    status=ElementStatus.CONTRADICTED,
                    evidence_spans=[
                        EvidenceSpan(
                            text=match.group(0),
                            start=match.start(),
                            end=match.end(),
                        )
                    ],
                    reasoning=f"Input explicitly states permission/consent was given: '{match.group(0)}'.",
                    evaluation_origin="stated_facts",
                )

        # Check for stated lack of consent
        consent_facts = [
            f for f in facts if f.action == "absence_of_consent" or "permission" in f.description.lower()
        ]
        if consent_facts:
            spans = [f.evidence_span for f in consent_facts]
            return ElementMatchResult(
                element_id=element.element_id,
                description=element.description,
                status=ElementStatus.SUPPORTED,
                evidence_spans=spans,
                reasoning=f"Stated facts explicitly indicate lack of permission/consent: '{spans[0].text}'.",
                evaluation_origin="stated_facts",
            )

    # 3. Match general element keywords and action facts
    matching_spans: List[EvidenceSpan] = []
    supported_indicators: List[str] = []

    for fact in facts:
        fact_desc = fact.description.lower()
        # Check if fact action or description overlaps meaningfully with element keywords
        matched_kw = [k for k in keywords if k in fact_desc or (fact.action and k in fact.action.lower())]
        if matched_kw:
            matching_spans.append(fact.evidence_span)
            supported_indicators.append(f"Fact '{fact.description}' matches requirement keywords {matched_kw}")

    # Also check direct evidence in normalized text if keyword matches sentence context
    if not matching_spans and keywords:
        matched_kw_in_text = [k for k in keywords if re.search(rf"\b{re.escape(k)}\b", normalized_text)]
        # Must match multiple keywords or a strong phrase to avoid frivolous matches
        if len(matched_kw_in_text) >= 2 or any(len(k.split()) >= 2 for k in matched_kw_in_text):
            # Locate first keyword span
            kw = matched_kw_in_text[0]
            m = re.search(rf"\b{re.escape(kw)}\b", doc.normalized_text, re.IGNORECASE)
            if m:
                matching_spans.append(EvidenceSpan(text=m.group(0), start=m.start(), end=m.end()))
                supported_indicators.append(f"Contextual match for keywords: {matched_kw_in_text}")

    if matching_spans:
        return ElementMatchResult(
            element_id=element.element_id,
            description=element.description,
            status=ElementStatus.SUPPORTED,
            evidence_spans=matching_spans[:3],
            reasoning="; ".join(supported_indicators) if supported_indicators else "Supported by stated facts.",
            evaluation_origin="stated_facts",
        )

    # 4. Default: NOT_ESTABLISHED (Never contradicted simply because info is missing!)
    return ElementMatchResult(
        element_id=element.element_id,
        description=element.description,
        status=ElementStatus.NOT_ESTABLISHED,
        evidence_spans=[],
        reasoning=f"No stated facts or evidence in the input established '{element.description}'.",
        evaluation_origin="unestablished",
    )


def generate_follow_up_questions(
    provision: LegalProvision,
    unestablished_matches: List[ElementMatchResult],
) -> List[FollowUpQuestion]:
    """Generate neutral, focused follow-up questions for unestablished legal elements."""
    questions: List[FollowUpQuestion] = []

    for match in unestablished_matches:
        q_id = f"Q_{provision.id}_{match.element_id}"
        desc = match.description.strip()

        # Construct specific question based on description
        if any(term in desc.lower() for term in ["consent", "permission", "authorization"]):
            q_text = "Did you or any authorized person grant permission or consent for this activity?"
        elif any(term in desc.lower() for term in ["money", "property", "extortion", "financial"]):
            q_text = "Was there any demand for money, valuable property, or financial payment?"
        elif any(term in desc.lower() for term in ["photo", "image", "media", "likeness"]):
            q_text = "Were personal photos, visual media, or private images published or shared?"
        elif any(term in desc.lower() for term in ["threat", "threaten", "blackmail", "intimidat"]):
            q_text = "Were any explicit threats or intimidating demands communicated?"
        elif any(term in desc.lower() for term in ["account", "profile", "identity", "impersonat"]):
            q_text = "Was a specific online profile, handle, or digital identity created in your name?"
        elif any(term in desc.lower() for term in ["man", "woman", "gender requirement", "female"]):
            q_text = "Was the targeted individual a woman, and was the person engaging in the conduct a man?"
        else:
            q_text = f"Did the incident involve: {desc}?"

        questions.append(
            FollowUpQuestion(
                question_id=q_id,
                provision_id=provision.id,
                element_id=match.element_id,
                question_text=q_text,
                context_note=f"Required to assess '{desc}' under {provision.act_name} {provision.section_id}.",
            )
        )

    return questions
