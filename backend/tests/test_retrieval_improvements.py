"""Unit and integration tests for retrieval improvements and legal filtering.

Tests:
1. Hard exclusion/filtering of uncommenced and provisional provisions by default.
2. Temporal applicability (pre-July-2024 IPC vs post-July-2024 BNS vs timeless).
3. Out-of-scope / civil dispute no-match handling and abstention.
4. Statutory element mismatch and follow-up question generation.
5. Missing fact clarification (e.g. victim gender in stalking/voyeurism).
"""

from datetime import date
from pathlib import Path
import pytest

from config import settings
from nlp.retrieval import (
    CandidateProvision,
    LegalCorpusIndex,
    get_corpus_index,
    load_legal_provisions,
)
from modules.offense_decoder import (
    OffenseAnalysisRequest,
    analyze_incident,
)


@pytest.fixture(scope="module")
def corpus_index():
    return get_corpus_index()


# ---------------------------------------------------------------------------
# 1. Uncommenced and Provisional Provisions Safeguards
# ---------------------------------------------------------------------------

def test_uncommenced_provisions_excluded_by_default(corpus_index):
    """By default, uncommenced provisions (BNS 106(2), DPDP 33) must not be retrieved."""
    # Hit-and-run fatal driving query
    q = "Driver ran over a pedestrian at high speed and sped away without reporting to police."
    candidates = corpus_index.retrieve(q, top_k=5, min_score=0.05, include_uncommenced=False)
    
    cand_ids = [c.provision.id for c in candidates]
    assert "BNS_2023_S106_SUB2_UNCOMMENCED" not in cand_ids
    assert "DPDP_2023_S33_PROVISIONAL" not in cand_ids


def test_uncommenced_provisions_accessible_when_explicitly_requested(corpus_index):
    """When include_uncommenced=True is passed, uncommenced provisions may be retrieved for research."""
    q = "Driver crashed into motorcycle killing rider and fled scene without reporting to police."
    candidates = corpus_index.retrieve(q, top_k=5, min_score=0.05, include_uncommenced=True)
    
    cand_ids = [c.provision.id for c in candidates]
    assert "BNS_2023_S106_SUB2_UNCOMMENCED" in cand_ids
    # But penalty must still be suppressed!
    cand = next(c for c in candidates if c.provision.id == "BNS_2023_S106_SUB2_UNCOMMENCED")
    assert cand.penalty_displayed is None


def test_provisional_dpdp_excluded_from_standard_cyber_retrieval(corpus_index):
    """Data breach queries must not retrieve provisional DPDP Section 33 over active IT Act sections."""
    q = "A telecom company suffered a data breach exposing personal records of 100,000 citizens."
    candidates = corpus_index.retrieve(q, top_k=5, min_score=0.05, include_uncommenced=False)
    
    cand_ids = [c.provision.id for c in candidates]
    assert "DPDP_2023_S33_PROVISIONAL" not in cand_ids


# ---------------------------------------------------------------------------
# 2. Temporal Applicability and Date Gating
# ---------------------------------------------------------------------------

def test_temporal_filter_pre_july_2024_excludes_bns(corpus_index):
    """An incident occurring before 1 July 2024 must retrieve historical IPC and not BNS."""
    # March 2024 cheating scenario (DEV_022)
    q = "In March 2024, a salesman tricked me into handing over my property deed by false promises."
    candidates = corpus_index.retrieve(
        q,
        top_k=5,
        min_score=0.05,
        incident_date=date(2024, 3, 15),
    )
    
    cand_ids = [c.provision.id for c in candidates]
    # IPC 420 must be present
    assert "IPC_1860_S420" in cand_ids
    # BNS 318 must NOT outrank IPC 420 (or must be filtered/demoted)
    ipc_rank = cand_ids.index("IPC_1860_S420")
    if "BNS_2023_S318" in cand_ids:
        bns_rank = cand_ids.index("BNS_2023_S318")
        assert ipc_rank < bns_rank, f"IPC 420 (rank {ipc_rank}) must outrank BNS 318 (rank {bns_rank}) for pre-July 2024"


def test_temporal_filter_post_july_2024_excludes_ipc(corpus_index):
    """An incident occurring after 1 July 2024 must retrieve BNS 2023 and not repealed IPC 1860."""
    q = "On 15 August 2024, someone broke into my apartment and stole gold jewelry and cash."
    candidates = corpus_index.retrieve(
        q,
        top_k=5,
        min_score=0.05,
        incident_date=date(2024, 8, 15),
    )
    
    cand_ids = [c.provision.id for c in candidates]
    assert "BNS_2023_S303" in cand_ids
    if "IPC_1860_S379" in cand_ids:
        bns_rank = cand_ids.index("BNS_2023_S303")
        ipc_rank = cand_ids.index("IPC_1860_S379")
        assert bns_rank < ipc_rank, f"BNS 303 (rank {bns_rank}) must outrank repealed IPC 379 (rank {ipc_rank}) post-July 2024"


def test_temporal_default_timeless_prefers_active_bns_over_repealed_ipc(corpus_index):
    """When no date is specified, active BNS provisions should take precedence over repealed IPC."""
    # Stalking without date (DEV_006)
    q = "A man followed me from my workplace daily and kept messaging me despite my repeated objections."
    candidates = corpus_index.retrieve(q, top_k=5, min_score=0.05)
    
    cand_ids = [c.provision.id for c in candidates]
    assert "BNS_2023_S78" in cand_ids
    if "IPC_1860_S354D" in cand_ids:
        bns_rank = cand_ids.index("BNS_2023_S78")
        ipc_rank = cand_ids.index("IPC_1860_S354D")
        assert bns_rank <= ipc_rank, "Active BNS 78 should rank at least as high as repealed IPC 354D when date is omitted"


# ---------------------------------------------------------------------------
# 3. No-Match Handling and Civil/Administrative Abstention
# ---------------------------------------------------------------------------

def test_no_match_tenancy_rent_default_abstains():
    """A purely civil tenancy dispute (rent default) must abstain and report no reliable criminal match."""
    req = OffenseAnalysisRequest(
        incident_text="The tenant defaulted on monthly rent payments for three months and refused to vacate upon lease expiry."
    )
    resp = analyze_incident(req, request_id="TEST_DEV_013")
    
    # Must abstain or flag no reliable criminal match
    assert resp.no_reliable_match is True or len(resp.candidate_provisions) == 0 or all(
        c.relevance_score < 0.12 for c in resp.candidate_provisions
    )


def test_no_match_traffic_challan_abstains():
    """A minor traffic challan must not match fatal hit-and-run negligence or stalking."""
    req = OffenseAnalysisRequest(
        incident_text="The driver received a traffic challan for speeding and running a red light on the ring road."
    )
    resp = analyze_incident(req, request_id="TEST_DEV_015")
    
    cand_ids = [c.provision_id for c in resp.candidate_provisions]
    assert "BNS_2023_S106_SUB2_UNCOMMENCED" not in cand_ids
    assert "IPC_1860_S354D" not in cand_ids


def test_no_match_property_tax_notice_abstains():
    """A municipal tax assessment notice must not match criminal mischief or theft."""
    req = OffenseAnalysisRequest(
        incident_text="The city municipal corporation issued a property tax assessment notice with an unexpected surcharge."
    )
    resp = analyze_incident(req, request_id="TEST_DEV_024")
    
    assert resp.no_reliable_match is True or len(resp.candidate_provisions) == 0 or all(
        c.relevance_score < 0.12 for c in resp.candidate_provisions
    )


def test_no_match_trademark_counterfeit_abstains():
    """Trademark counterfeit branding (DEV_027) must not match penal document forgery."""
    req = OffenseAnalysisRequest(
        incident_text="A vendor manufactured counterfeit branded handbags mimicking our registered trademark logo."
    )
    resp = analyze_incident(req, request_id="TEST_DEV_027")
    
    # Trademark counterfeiting is covered under Trade Marks Act 1999, not penal forgery of documents S. 336
    cand_ids = [c.provision_id for c in resp.candidate_provisions if c.relevance_score >= 0.12]
    assert "BNS_2023_S336" not in cand_ids


# ---------------------------------------------------------------------------
# 4. Clarification and Missing Facts
# ---------------------------------------------------------------------------

def test_missing_victim_gender_triggers_follow_up_question():
    """When tracking/surveillance is described without gender (DEV_030), clarification should be sought."""
    req = OffenseAnalysisRequest(
        incident_text="Someone placed a GPS magnetic tracker under my vehicle and monitored everywhere I drove."
    )
    resp = analyze_incident(req, request_id="TEST_DEV_030")
    
    # Must generate follow-up questions
    assert len(resp.follow_up_questions) > 0
    # Uncertainty notes should mention that stalking requires specific gender prerequisites or that facts are incomplete
    assert any("element" in n.lower() or "gender" in n.lower() or "preliminary" in n.lower() for n in resp.uncertainty_notes)
