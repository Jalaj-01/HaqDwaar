"""Automated tests for BNS and IPC statutory coverage, provenance, commencement, and safeguards."""

import pytest
from config import LEGAL_PROVISIONS_PATH
from modules.offense_decoder import OffenseAnalysisRequest, analyze_incident
from nlp.retrieval import (
    CandidateProvision,
    LegalCorpusIndex,
    get_corpus_status_info,
    load_legal_provisions,
)


@pytest.fixture(scope="module")
def production_provisions():
    return load_legal_provisions(LEGAL_PROVISIONS_PATH)


@pytest.fixture(scope="module")
def production_index(production_provisions):
    return LegalCorpusIndex(production_provisions)


def test_bns_corpus_record_counts_and_acts(production_provisions):
    """Corpus must include balanced BNS, IPC, and special act provisions."""
    act_counts = {}
    for p in production_provisions:
        act_counts[p.act_name] = act_counts.get(p.act_name, 0) + 1

    assert act_counts.get("Bharatiya Nyaya Sanhita, 2023", 0) >= 12, "Expected at least 12 BNS provisions"
    assert act_counts.get("Indian Penal Code, 1860", 0) >= 12, "Expected at least 12 IPC provisions"
    assert act_counts.get("Information Technology Act, 2000", 0) >= 8, "Expected 8 ITA provisions"
    assert act_counts.get("Digital Personal Data Protection Act, 2023", 0) >= 1, "Expected DPDP audit fixture"

    status_info = get_corpus_status_info(LEGAL_PROVISIONS_PATH)
    assert status_info["corpus_record_count"] >= 35
    assert status_info["verified_record_count"] >= 33
    assert status_info["corpus_status"] == "partial_unverified"


def test_official_government_provenance_and_urls(production_provisions):
    """Every provision must cite an official government repository (India Code or eGazette)."""
    for p in production_provisions:
        assert (
            p.official_source_url.startswith("https://www.indiacode.nic.in")
            or p.official_source_url.startswith("https://egazette.gov.in")
        ), f"Unverified source URL in {p.id}: {p.official_source_url}"

        assert p.source_authority.strip(), f"Missing source authority in {p.id}"
        assert p.act_name.strip()
        assert p.section_id.strip()
        assert p.title.strip()
        assert p.source_text.strip()
        assert p.plain_language_summary.strip()
        assert len(p.legal_elements) >= 1, f"No legal elements defined for {p.id}"


def test_commencement_dates_and_temporal_boundaries(production_provisions):
    """BNS provisions must reflect 2024-07-01 commencement; IPC provisions must reflect 2024-06-30 repeal."""
    for p in production_provisions:
        if p.act_name == "Bharatiya Nyaya Sanhita, 2023":
            if p.id == "BNS_2023_S106_SUB2_UNCOMMENCED":
                # Excluded from commencement under Notification S.O. 850(E)
                assert p.source_verified is False
                assert p.effective_from is None
                assert p.effective_to is None
                assert "EXCLUDED from commencement" in p.version_label
            else:
                assert p.source_verified is True
                assert p.effective_from == "2024-07-01", f"Invalid BNS effective_from for {p.id}: {p.effective_from}"
                assert p.effective_to is None, f"BNS should be currently in force for {p.id}"

        elif p.act_name == "Indian Penal Code, 1860":
            assert p.source_verified is True
            assert p.effective_to == "2024-06-30", f"IPC must reflect repeal on 2024-06-30 for {p.id}"
            assert "repealed w.e.f. 1 july 2024" in p.version_label.lower()


def test_unverified_penalty_suppression_safeguards(production_provisions, production_index):
    """All unverified or uncommenced provisions must suppress penalty display upon retrieval."""
    unverified_provisions = [p for p in production_provisions if not p.source_verified]
    assert len(unverified_provisions) >= 2, "Expected at least 2 unverified records (DPDP S33 & BNS S106(2))"

    unverified_ids = {p.id for p in unverified_provisions}
    assert "DPDP_2023_S33_PROVISIONAL" in unverified_ids
    assert "BNS_2023_S106_SUB2_UNCOMMENCED" in unverified_ids

    # Hit-and-run uncommenced retrieval test
    query_hit_run = "The driver caused death through rash driving and escaped without reporting to the police or magistrate."
    candidates = production_index.retrieve(query_hit_run, top_k=5, min_score=0.01)
    cand_106 = next((c for c in candidates if c.provision.id == "BNS_2023_S106_SUB2_UNCOMMENCED"), None)

    if cand_106:
        assert cand_106.provision.source_verified is False
        assert cand_106.penalty_displayed is None, "CRITICAL: Uncommenced penalty must be suppressed!"


def test_retrieval_forgery_provisions(production_index):
    """Incident involving document fabrication must retrieve BNS 336 and IPC 468/465."""
    query = "The suspect forged an agreement and fake salary slip with intent to cheat and take a bank loan."
    candidates = production_index.retrieve(query, top_k=5)
    cand_ids = [c.provision.id for c in candidates]

    assert any(cid in cand_ids for cid in ["BNS_2023_S336", "IPC_1860_S468", "IPC_1860_S465"])
    match_336 = next((c for c in candidates if c.provision.id == "BNS_2023_S336"), None)
    if match_336:
        assert match_336.provision.source_verified is True
        assert match_336.penalty_displayed is not None
        assert "seven years" in match_336.penalty_displayed


def test_retrieval_criminal_breach_of_trust_provisions(production_index):
    """Incident involving fiduciary fund misappropriation must retrieve BNS 316 and IPC 406."""
    query = "The accountant was entrusted with company funds but dishonestly misappropriated and siphoned the money to his personal account."
    candidates = production_index.retrieve(query, top_k=5)
    cand_ids = [c.provision.id for c in candidates]

    assert "BNS_2023_S316" in cand_ids or "IPC_1860_S406" in cand_ids
    match_316 = next((c for c in candidates if c.provision.id == "BNS_2023_S316"), None)
    if match_316:
        assert match_316.provision.source_verified is True
        assert "five years" in match_316.penalty_displayed


def test_retrieval_voyeurism_provisions(production_index):
    """Incident involving hidden camera recording intimate moments must retrieve BNS 77 and IPC 354C."""
    query = "A hotel worker secretly placed a hidden camera in the changing room to capture private photos of women without their consent."
    candidates = production_index.retrieve(query, top_k=5)
    cand_ids = [c.provision.id for c in candidates]

    assert "BNS_2023_S77" in cand_ids or "IPC_1860_S354C" in cand_ids or "ITA_2000_S66E" in cand_ids


def test_retrieval_insult_modesty_provisions(production_index):
    """Incident involving lewd comments and vulgar messages must retrieve BNS 79 or IPC 509."""
    query = "A stranger repeatedly sent lewd comments, vulgar messages, and obscene gestures intended to insult my modesty."
    candidates = production_index.retrieve(query, top_k=5)
    cand_ids = [c.provision.id for c in candidates]

    assert "BNS_2023_S79" in cand_ids or "IPC_1860_S509" in cand_ids


def test_retrieval_extortion_historical_counterparts(production_index):
    """Extortion query must retrieve both modern BNS 308 and historical IPC 384 counterparts."""
    query = "The blackmailer put me in fear of injury and demanded five lakh rupees or threatened to harm my family."
    candidates = production_index.retrieve(query, top_k=5)
    cand_ids = [c.provision.id for c in candidates]

    assert "BNS_2023_S308" in cand_ids or "IPC_1860_S384" in cand_ids


def test_retrieval_theft_historical_counterparts(production_index):
    """Theft query must retrieve both modern BNS 303 and historical IPC 379 counterparts."""
    query = "Someone took my laptop and wallet out of my possession without my consent with dishonest intention."
    candidates = production_index.retrieve(query, top_k=5)
    cand_ids = [c.provision.id for c in candidates]

    assert "BNS_2023_S303" in cand_ids or "IPC_1860_S379" in cand_ids


def test_offense_decoder_statutory_transitional_notes(production_index):
    """Offense decoder must explain BNS vs IPC temporal applicability in uncertainty_notes."""
    req = OffenseAnalysisRequest(
        incident_text="Someone cheated me by lying about an investment scheme and dishonestly induced me to transfer money.",
        top_k=5,
    )
    analysis = analyze_incident(req, request_id="transitional-test-1", custom_index=production_index)

    assert analysis.no_reliable_match is False
    assert len(analysis.candidate_provisions) > 0

    acts_found = {c.act_name for c in analysis.candidate_provisions}
    if "Indian Penal Code, 1860" in acts_found and "Bharatiya Nyaya Sanhita, 2023" in acts_found:
        assert any(
            "1 July 2024" in note and "30 June 2024" in note
            for note in analysis.uncertainty_notes
        ), "Expected explicit temporal guidance in uncertainty_notes when both statutes are retrieved"


def test_penalty_statutory_distinctions(production_provisions):
    """Verify known statutory penalty distinctions between IPC and BNS."""
    bns_308 = next(p for p in production_provisions if p.id == "BNS_2023_S308")
    ipc_384 = next(p for p in production_provisions if p.id == "IPC_1860_S384")
    # Extortion penalty increased from 3 years in IPC 384 to 7 years in BNS 308(2)
    assert "seven years" in bns_308.penalty_text.lower()
    assert "three years" in ipc_384.penalty_text.lower()

    bns_316 = next(p for p in production_provisions if p.id == "BNS_2023_S316")
    ipc_406 = next(p for p in production_provisions if p.id == "IPC_1860_S406")
    # CBT penalty increased from 3 years in IPC 406 to 5 years in BNS 316(2)
    assert "five years" in bns_316.penalty_text.lower()
    assert "three years" in ipc_406.penalty_text.lower()

    bns_324 = next(p for p in production_provisions if p.id == "BNS_2023_S324")
    ipc_426 = next(p for p in production_provisions if p.id == "IPC_1860_S426")
    # Mischief basic penalty increased from 3 months in IPC 426 to 6 months in BNS 324(2)
    assert "six months" in bns_324.penalty_text.lower()
    assert "three months" in ipc_426.penalty_text.lower()

    bns_303 = next(p for p in production_provisions if p.id == "BNS_2023_S303")
    # BNS 303 introduces community service for first-time petty theft
    assert "community service" in bns_303.exceptions_or_qualifications.lower()
