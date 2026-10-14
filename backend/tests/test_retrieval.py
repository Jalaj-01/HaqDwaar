"""Unit tests for corpus indexing, retrieval, and ranking algorithms."""

from pathlib import Path
import pytest

from config import FIXTURES_DIR, settings
from nlp.retrieval import (
    CandidateProvision,
    LegalCorpusIndex,
    get_corpus_index,
    load_legal_provisions,
)

SYNTHETIC_FIXTURE_PATH = FIXTURES_DIR / "synthetic_provisions.json"


def test_empty_corpus_retrieval():
    """Retrieval on an empty corpus must safely return an empty candidate list."""
    index = LegalCorpusIndex([])
    candidates = index.retrieve("Someone created a fake account")
    assert candidates == []


def test_synthetic_fixtures_loaded():
    """Synthetic test fixture must load valid synthetic provisions."""
    provisions = load_legal_provisions(SYNTHETIC_FIXTURE_PATH)
    assert len(provisions) == 3
    for p in provisions:
        assert "Synthetic" in p.act_name or "SYNTHETIC" in p.title


def test_retrieval_returns_source_metadata():
    """Retrieved candidates must retain all statutory and provenance metadata."""
    provisions = load_legal_provisions(SYNTHETIC_FIXTURE_PATH)
    index = LegalCorpusIndex(provisions)

    query = "Someone created a fake profile with my likeness without my permission"
    candidates = index.retrieve(query, top_k=2)

    assert len(candidates) > 0
    top_cand = candidates[0]
    assert isinstance(top_cand, CandidateProvision)
    assert top_cand.relevance_score > 0.0
    assert top_cand.lexical_score > 0.0

    # Provenance metadata preservation
    prov = top_cand.provision
    assert prov.act_name == "Synthetic Test Act 2099"
    assert prov.official_source_url.startswith("https://example.gov.in/")
    assert prov.source_authority == "Synthetic Testing Authority"
    assert prov.version_label != ""


def test_ranking_determinism():
    """Ranking order and scores must be deterministic across identical invocations."""
    provisions = load_legal_provisions(SYNTHETIC_FIXTURE_PATH)
    index = LegalCorpusIndex(provisions)

    query = "Extortion demanding money by threatening to leak private photos"
    run_1 = index.retrieve(query, top_k=3)
    run_2 = index.retrieve(query, top_k=3)

    assert len(run_1) == len(run_2)
    for c1, c2 in zip(run_1, run_2):
        assert c1.provision.id == c2.provision.id
        assert c1.relevance_score == c2.relevance_score
        assert c1.lexical_score == c2.lexical_score


def test_unverified_record_labeling_and_penalty_suppression():
    """Unverified records must be labeled unverified and penalty text must be suppressed."""
    provisions = load_legal_provisions(SYNTHETIC_FIXTURE_PATH)
    index = LegalCorpusIndex(provisions)

    query = "uploaded photos without permission"
    candidates = index.retrieve(query, top_k=5, min_score=0.01)

    cand_s2 = next((c for c in candidates if c.provision.id == "SYNTHETIC_ACT_S2"), None)
    assert cand_s2 is not None
    # S2 is marked source_verified: False in the fixture
    assert cand_s2.provision.source_verified is False
    # CRITICAL: Penalty must be suppressed if source is not verified!
    assert cand_s2.penalty_displayed is None

    cand_s1 = next((c for c in candidates if c.provision.id == "SYNTHETIC_ACT_S1"), None)
    assert cand_s1 is not None
    # S1 is verified
    assert cand_s1.provision.source_verified is True
    assert cand_s1.penalty_displayed is not None
    assert "Synthetic penalty" in cand_s1.penalty_displayed


def test_tfidf_only_retrieval_fallback():
    """When semantic model is disabled, retrieval functions via TF-IDF only."""
    provisions = load_legal_provisions(SYNTHETIC_FIXTURE_PATH)
    orig = settings.disable_semantic_model

    try:
        settings.disable_semantic_model = True
        index = LegalCorpusIndex(provisions)
        candidates = index.retrieve("extortion demanding money", top_k=2)

        assert len(candidates) > 0
        for c in candidates:
            assert c.semantic_score is None
            assert c.relevance_score == c.lexical_score
    finally:
        settings.disable_semantic_model = orig


def test_low_relevance_cutoff():
    """Completely unrelated queries must return no candidates when below min_score threshold."""
    provisions = load_legal_provisions(SYNTHETIC_FIXTURE_PATH)
    index = LegalCorpusIndex(provisions)

    unrelated_query = "quantum gravitational wave astrophysics telescope"
    candidates = index.retrieve(unrelated_query, min_score=0.1)
    assert len(candidates) == 0


def test_top_k_bounding():
    """Top_k parameter must be respected and bounded by max_top_k."""
    provisions = load_legal_provisions(SYNTHETIC_FIXTURE_PATH)
    index = LegalCorpusIndex(provisions)

    c1 = index.retrieve("synthetic act online", top_k=1, min_score=0.01)
    assert len(c1) <= 1

    c_excess = index.retrieve("synthetic act online", top_k=9999, min_score=0.01)
    assert len(c_excess) <= settings.max_top_k
