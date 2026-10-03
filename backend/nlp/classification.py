"""Incident category classification baseline for LexiLaw.

Uses an explainable rule/taxonomy-based classification pipeline labeled provisional.
Documented for future integration of supervised scikit-learn models when human-labeled
datasets become available.
"""

import re
from typing import List
from pydantic import BaseModel, Field


class IncidentCategory(BaseModel):
    """An explainable provisional incident category."""

    category_id: str = Field(..., description="Machine-readable category identifier")
    label: str = Field(..., description="Human-readable category title")
    rationale: str = Field(..., description="Explainable textual rationale for this category")
    is_provisional: bool = Field(
        default=True,
        description="Indicates provisional rule-based classification requiring verification",
    )


# Explainable Keyword and Pattern Taxonomy
CATEGORY_TAXONOMY = [
    {
        "id": "CAT_CYBER_IDENTITY",
        "label": "Cyber / Digital Identity Offense",
        "patterns": [
            r"\bfake\s+(?:account|profile|id)\b",
            r"\bimpersonat(?:e|ing|ion)\b",
            r"\bhack(?:ed|ing)?\b",
            r"\bunauthorized\s+access\b",
            r"\bsocial\s+media\b",
            r"\bphishing\b",
            r"\bstole\s+my\s+identity\b",
        ],
        "rationale": "Mentions online accounts, digital impersonation, hacking, or social media misuse.",
    },
    {
        "id": "CAT_PRIVACY_NONCONSENSUAL",
        "label": "Privacy & Non-Consensual Media",
        "patterns": [
            r"\bupload(?:ed)?\s+(?:my\s+)?photos?\b",
            r"\bpublish(?:ed)?\s+(?:my\s+)?images?\b",
            r"\bwithout\s+(?:my\s+)?permission\b",
            r"\bnon-consensual\b",
            r"\bleak(?:ed)?\s+(?:private|personal)?\b",
            r"\bintimate\s+images?\b",
            r"\bvoyeurism\b",
        ],
        "rationale": "Involves unauthorized publication or sharing of personal photos, media, or private details.",
    },
    {
        "id": "CAT_FINANCIAL_FRAUD",
        "label": "Financial Fraud & Extortion",
        "patterns": [
            r"\bextort(?:ion|ed)?\b",
            r"\bblackmail(?:ed)?\b",
            r"\bdemanded\s+money\b",
            r"\bcheat(?:ed|ing)?\b",
            r"\bfraud(?:ulent)?\b",
            r"\bransom\b",
            r"\btransferred\s+funds?\b",
            r"\blost\s+money\b",
            r"\bforg(?:ed|ery)\b",
            r"\bfabricat(?:ed|ing)\b",
            r"\bmisappropriat(?:ed|ion)\b",
            r"\bembezzl(?:ed|ement)\b",
            r"\bbreach\s+of\s+trust\b",
            r"\btheft\b",
            r"\bstole(?:n)?\b",
        ],
        "rationale": "Asserts fraudulent acquisition of money, extortion, theft, document forgery, or breach of trust.",
    },
    {
        "id": "CAT_DEFAMATION_REPUTATION",
        "label": "Defamation & Reputational Harm",
        "patterns": [
            r"\bdefam(?:e|ed|ation)\b",
            r"\bruin(?:ed)?\s+my\s+reputation\b",
            r"\bfalse\s+allegations?\b",
            r"\bslander(?:ous)?\b",
            r"\blibel(?:ous)?\b",
            r"\btarnished\s+image\b",
        ],
        "rationale": "Asserts dissemination of false statements intended to harm character or reputation.",
    },
    {
        "id": "CAT_HARASSMENT_THREATS",
        "label": "Harassment & Intimidation",
        "patterns": [
            r"\bthreatened\s+(?:me|to)\b",
            r"\bintimidation\b",
            r"\bstalk(?:ing|ed)?\b",
            r"\babus(?:ive|ed)\b",
            r"\bmental\s+harassment\b",
            r"\binsult(?:ed|ing)?\s+modesty\b",
            r"\blewd\s+remarks?\b",
            r"\bvulgar\s+messages?\b",
        ],
        "rationale": "Asserts stalking, verbal threats, abusive messages, insults to modesty, or targeted harassment.",
    },
]


def classify_incident_categories(text: str) -> List[IncidentCategory]:
    """Classify incident into explainable provisional categories.

    Uses deterministic pattern matching against a transparent taxonomy.
    Always flags results as is_provisional=True.
    """
    clean_text = text.lower()
    matched_categories: List[IncidentCategory] = []

    for cat in CATEGORY_TAXONOMY:
        for pattern in cat["patterns"]:
            if re.search(pattern, clean_text):
                matched_categories.append(
                    IncidentCategory(
                        category_id=cat["id"],
                        label=cat["label"],
                        rationale=cat["rationale"],
                        is_provisional=True,
                    )
                )
                break  # Matched category once, proceed to next

    if not matched_categories:
        # Default unclassified fallback
        matched_categories.append(
            IncidentCategory(
                category_id="CAT_GENERAL",
                label="General / Unclassified Incident",
                rationale="The stated facts do not strongly match predefined digital, financial, or harassment taxonomies.",
                is_provisional=True,
            )
        )

    return matched_categories
