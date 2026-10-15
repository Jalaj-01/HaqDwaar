"""Unit tests for the retrieval evaluation framework, metric math, and dataset integrity."""

import json
from pathlib import Path
import pytest

from evaluation.eval_retrieval import (
    assert_not_locked,
    compute_corpus_fingerprint,
    compute_query_metrics,
    evaluate_retrieval_pipeline,
    lock_benchmark_file,
    run_threshold_sweep,
    validate_evaluation_dataset,
    verify_benchmark_lock,
)
from nlp.retrieval import CandidateProvision, LegalCorpusIndex, LegalProvision


def test_metric_calculation_perfect_ranking():
    """Rank 1 hit must yield reciprocal_rank=1.0 and expected P@K, R@K."""
    retrieved = ["PROV_A", "PROV_B", "PROV_C", "PROV_D", "PROV_E"]
    relevant = {"PROV_A"}

    metrics = compute_query_metrics(retrieved, relevant, k_precisions=[3, 5], k_recalls=[5, 10])

    assert metrics["reciprocal_rank"] == 1.0
    assert metrics["p_at_3"] == pytest.approx(1.0 / 3.0)
    assert metrics["p_at_5"] == pytest.approx(1.0 / 5.0)
    assert metrics["r_at_5"] == 1.0
    assert metrics["r_at_10"] == 1.0


def test_metric_calculation_suboptimal_ranking():
    """Hit at rank 2 must yield reciprocal_rank=0.5."""
    retrieved = ["IRRELEVANT_1", "PROV_A", "IRRELEVANT_2", "IRRELEVANT_3", "IRRELEVANT_4"]
    relevant = {"PROV_A"}

    metrics = compute_query_metrics(retrieved, relevant, k_precisions=[3, 5], k_recalls=[5, 10])

    assert metrics["reciprocal_rank"] == 0.5
    assert metrics["p_at_3"] == pytest.approx(1.0 / 3.0)
    assert metrics["p_at_5"] == pytest.approx(1.0 / 5.0)
    assert metrics["r_at_5"] == 1.0


def test_metric_calculation_no_relevant_retrieved():
    """Zero relevant items retrieved must yield reciprocal_rank=0.0 and zero P/R."""
    retrieved = ["IRRELEVANT_1", "IRRELEVANT_2", "IRRELEVANT_3"]
    relevant = {"PROV_A", "PROV_B"}

    metrics = compute_query_metrics(retrieved, relevant, k_precisions=[3, 5], k_recalls=[5, 10])

    assert metrics["reciprocal_rank"] == 0.0
    assert metrics["p_at_3"] == 0.0
    assert metrics["p_at_5"] == 0.0
    assert metrics["r_at_5"] == 0.0
    assert metrics["r_at_10"] == 0.0


def test_metric_calculation_multiple_relevant_provisions():
    """Multiple relevant provisions at ranks 1 and 3."""
    retrieved = ["PROV_A", "IRRELEVANT", "PROV_B", "IRRELEVANT_2", "IRRELEVANT_3"]
    relevant = {"PROV_A", "PROV_B"}

    metrics = compute_query_metrics(retrieved, relevant, k_precisions=[3, 5], k_recalls=[5, 10])

    assert metrics["reciprocal_rank"] == 1.0  # First hit is at rank 1
    assert metrics["p_at_3"] == pytest.approx(2.0 / 3.0)
    assert metrics["p_at_5"] == pytest.approx(2.0 / 5.0)
    assert metrics["r_at_5"] == 1.0  # Both hits inside top 5 (2/2 = 1.0)


def test_metric_calculation_empty_ground_truth_no_division_by_zero():
    """Empty ground truth must safely return 0.0 recall without division by zero."""
    retrieved = ["PROV_A", "PROV_B"]
    relevant = set()  # empty

    metrics = compute_query_metrics(retrieved, relevant, k_precisions=[3, 5], k_recalls=[5, 10])

    assert metrics["reciprocal_rank"] == 0.0
    assert metrics["p_at_3"] == 0.0
    assert metrics["r_at_5"] == 0.0
    assert metrics["r_at_10"] == 0.0


def test_metric_calculation_fewer_than_k_results():
    """Fewer than K results retrieved must divide hits by K (standard IR definition)."""
    retrieved = ["PROV_A"]  # Only 1 retrieved item
    relevant = {"PROV_A"}

    metrics = compute_query_metrics(retrieved, relevant, k_precisions=[3, 5], k_recalls=[5, 10])

    assert metrics["reciprocal_rank"] == 1.0
    assert metrics["p_at_3"] == pytest.approx(1.0 / 3.0)
    assert metrics["p_at_5"] == pytest.approx(1.0 / 5.0)
    assert metrics["r_at_5"] == 1.0


def test_metric_calculation_duplicate_retrieved_ids():
    """Duplicate IDs in retrieved candidates are de-duplicated preserving rank order."""
    retrieved = ["PROV_A", "PROV_A", "PROV_B", "PROV_A"]
    relevant = {"PROV_B"}

    # PROV_A at rank 1, PROV_B at rank 2 (after deduping second PROV_A)
    metrics = compute_query_metrics(retrieved, relevant, k_precisions=[3, 5], k_recalls=[5, 10])

    assert metrics["reciprocal_rank"] == 0.5  # PROV_B is at effective rank 2
    assert metrics["p_at_3"] == pytest.approx(1.0 / 3.0)


def test_metric_calculation_unknown_provision_ids():
    """Unknown or unindexed IDs in retrieved list do not break metrics."""
    retrieved = ["COMPLETELY_UNKNOWN_ID_999", "PROV_A"]
    relevant = {"PROV_A"}

    metrics = compute_query_metrics(retrieved, relevant, k_precisions=[3, 5], k_recalls=[5, 10])

    assert metrics["reciprocal_rank"] == 0.5
    assert metrics["p_at_3"] == pytest.approx(1.0 / 3.0)


def test_dataset_split_integrity_and_no_leakage():
    """The production dataset must have zero split leakage, unique IDs, and valid schemas."""
    is_valid, issues = validate_evaluation_dataset()
    assert is_valid is True, f"Dataset validation failed: {issues}"
    assert len(issues) == 0


def test_dataset_validator_detects_leakage(tmp_path: Path):
    """Validator must detect duplicate query IDs across dev and test splits."""
    leaked_data = [
        {
            "query_id": "QUERY_001",
            "query_text": "Sample dev query text",
            "relevant_provision_ids": [],
            "expected_no_match": True,
            "split": "dev",
            "annotation_status": "reviewed",
        },
        {
            "query_id": "QUERY_001",  # Duplicate ID
            "query_text": "Sample test query text",
            "relevant_provision_ids": [],
            "expected_no_match": True,
            "split": "test",
            "annotation_status": "reviewed",
        },
    ]
    leaked_file = tmp_path / "leaked_dataset.json"
    leaked_file.write_text(json.dumps(leaked_data), encoding="utf-8")

    is_valid, issues = validate_evaluation_dataset(dataset_path=leaked_file)
    assert is_valid is False
    assert any("Duplicate query_id" in issue or "Split leakage" in issue for issue in issues)


def test_dataset_validator_detects_duplicate_text(tmp_path: Path):
    """Validator must detect identical query text across different query IDs."""
    dup_data = [
        {
            "query_id": "QUERY_001",
            "query_text": "Identical incident description text.",
            "relevant_provision_ids": [],
            "expected_no_match": True,
            "split": "dev",
            "annotation_status": "reviewed",
        },
        {
            "query_id": "QUERY_002",
            "query_text": "Identical incident description text.",
            "relevant_provision_ids": [],
            "expected_no_match": True,
            "split": "dev",
            "annotation_status": "reviewed",
        },
    ]
    dup_file = tmp_path / "dup_dataset.json"
    dup_file.write_text(json.dumps(dup_data), encoding="utf-8")

    is_valid, issues = validate_evaluation_dataset(dataset_path=dup_file)
    assert is_valid is False
    assert any("Duplicate query text detected" in issue for issue in issues)


def test_pending_annotations_excluded_from_scoring():
    """Queries marked 'pending' must be excluded from scored metrics by default."""
    sample_queries = [
        {
            "query_id": "Q_REV_1",
            "query_text": "Reviewed query text",
            "relevant_provision_ids": ["PROV_A"],
            "expected_no_match": False,
            "split": "dev",
            "annotation_status": "reviewed",
        },
        {
            "query_id": "Q_PEND_1",
            "query_text": "Pending unreviewed query text",
            "relevant_provision_ids": ["PROV_B"],
            "expected_no_match": False,
            "split": "dev",
            "annotation_status": "pending",
        },
    ]

    # Mock index
    class MockIndex:
        def retrieve(self, text, top_k=10, min_score=0.05):
            return []

    report = evaluate_retrieval_pipeline(
        dataset_queries=sample_queries,
        index=MockIndex(),  # type: ignore
        split_filter="dev",
        include_pending=False,
    )

    assert report["eligible_queries_evaluated"] == 1
    assert report["pending_queries_excluded"] == 1
    assert report["positive_queries_count"] == 1


def test_corpus_fingerprint_generation(tmp_path: Path):
    """Corpus fingerprint must generate valid SHA256 and count."""
    corpus_file = tmp_path / "sample_corpus.json"
    corpus_file.write_text(json.dumps([{"id": "P1"}, {"id": "P2"}]), encoding="utf-8")

    fp = compute_corpus_fingerprint(corpus_file)
    assert fp["exists"] is True
    assert fp["record_count"] == 2
    assert len(fp["sha256"]) == 64


def test_threshold_calibration_improves_no_match_rejection():
    """Higher threshold cutoff must convert weak residual candidates into true negatives."""
    # Mock CandidateProvision with score 0.08
    class MockProvision:
        id = "MOCK_PROV"
    class MockCandidate:
        provision = MockProvision()
        relevance_score = 0.08
        lexical_score = 0.05

    class CalibratedMockIndex:
        def retrieve(self, text, top_k=10, min_score=0.05):
            if min_score <= 0.08:
                return [MockCandidate()]
            return []

    sample_queries = [
        {
            "query_id": "Q_OUT_OF_SCOPE",
            "query_text": "Lawn mower noise complaint at noon",
            "relevant_provision_ids": [],
            "expected_no_match": True,
            "split": "dev",
            "annotation_status": "reviewed",
        }
    ]

    # At low cutoff (0.05): False Positive
    rep_low = evaluate_retrieval_pipeline(
        dataset_queries=sample_queries,
        index=CalibratedMockIndex(),  # type: ignore
        split_filter="dev",
        min_score_cutoff=0.05,
    )
    assert rep_low["modes"]["hybrid"]["no_match_detection_metrics"]["false_positives"] == 1
    assert rep_low["modes"]["hybrid"]["no_match_detection_metrics"]["true_negatives"] == 0

    # At calibrated cutoff (0.12): True Negative
    rep_cal = evaluate_retrieval_pipeline(
        dataset_queries=sample_queries,
        index=CalibratedMockIndex(),  # type: ignore
        split_filter="dev",
        min_score_cutoff=0.12,
    )
    assert rep_cal["modes"]["hybrid"]["no_match_detection_metrics"]["false_positives"] == 0
    assert rep_cal["modes"]["hybrid"]["no_match_detection_metrics"]["true_negatives"] == 1
    assert rep_cal["modes"]["hybrid"]["no_match_detection_metrics"]["no_match_accuracy"] == 1.0


def test_no_match_detection_metric_aggregation():
    """No-match metrics must accurately compute true negatives, false positives, accuracy, and FPR."""
    class MockCandidate:
        class provision:
            id = "HIT_P1"

    class MixedMockIndex:
        def retrieve(self, text, top_k=10, min_score=0.05):
            if "positive_hit" in text:
                return [MockCandidate()]
            return []

    queries = [
        # TN query 1
        {"query_id": "NM_1", "query_text": "clean out of scope", "relevant_provision_ids": [], "expected_no_match": True, "split": "dev", "annotation_status": "reviewed"},
        # TN query 2
        {"query_id": "NM_2", "query_text": "another clean out of scope", "relevant_provision_ids": [], "expected_no_match": True, "split": "dev", "annotation_status": "reviewed"},
        # FP query
        {"query_id": "NM_3", "query_text": "positive_hit noise query", "relevant_provision_ids": [], "expected_no_match": True, "split": "dev", "annotation_status": "reviewed"},
    ]

    rep = evaluate_retrieval_pipeline(queries, MixedMockIndex(), split_filter="dev", min_score_cutoff=0.05)  # type: ignore
    nm = rep["modes"]["hybrid"]["no_match_detection_metrics"]

    assert nm["total_no_match_queries"] == 3
    assert nm["true_negatives"] == 2
    assert nm["false_positives"] == 1
    assert nm["no_match_accuracy"] == pytest.approx(2.0 / 3.0, abs=1e-4)
    assert nm["false_positive_rate"] == pytest.approx(1.0 / 3.0, abs=1e-4)



def test_positive_metric_aggregation_excludes_empty_ground_truth():
    """Empty ground truth queries must not participate in positive MRR or recall sums."""
    class MockCandidate:
        class provision:
            id = "PROV_A"

    class AlwaysHitsIndex:
        def retrieve(self, text, top_k=10, min_score=0.05):
            return [MockCandidate()]

    queries = [
        # Positive query: Hit at Rank 1
        {"query_id": "POS_1", "query_text": "hacked credentials", "relevant_provision_ids": ["PROV_A"], "expected_no_match": False, "split": "dev", "annotation_status": "reviewed"},
        # Out-of-scope query: returns retrieved item, so FP for no-match, but MUST NOT dilute positive MRR
        {"query_id": "NM_1", "query_text": "airline refund", "relevant_provision_ids": [], "expected_no_match": True, "split": "dev", "annotation_status": "reviewed"},
    ]

    rep = evaluate_retrieval_pipeline(queries, AlwaysHitsIndex(), split_filter="dev")  # type: ignore
    pos = rep["modes"]["hybrid"]["positive_retrieval_metrics"]

    assert rep["positive_queries_count"] == 1
    assert rep["no_match_queries_count"] == 1
    # POS_1 has rank 1, so MRR must be 1.0 (not 0.5)
    assert pos["MRR"] == 1.0
    assert pos["Recall@5"] == 1.0


def test_dataset_validator_detects_near_duplicate_text(tmp_path: Path):
    """Validator must detect near-duplicate incident descriptions with high token overlap."""
    near_dup_data = [
        {
            "query_id": "QUERY_001",
            "query_text": "An extortionist demanded two bitcoins to unlock our sensitive company database files immediately.",
            "relevant_provision_ids": [],
            "expected_no_match": True,
            "split": "dev",
            "annotation_status": "reviewed",
        },
        {
            "query_id": "QUERY_002",
            "query_text": "An extortionist demanded two bitcoins to unlock our sensitive company database files right away.",
            "relevant_provision_ids": [],
            "expected_no_match": True,
            "split": "test",
            "annotation_status": "reviewed",
        },
    ]
    nd_file = tmp_path / "near_dup_dataset.json"
    nd_file.write_text(json.dumps(near_dup_data), encoding="utf-8")

    is_valid, issues = validate_evaluation_dataset(dataset_path=nd_file)
    assert is_valid is False
    assert any("Near-duplicate query text detected" in issue for issue in issues)


def test_validator_detects_missing_ground_truth_fields(tmp_path: Path):
    """Validator must detect missing required fields such as relevant_provision_ids or expected_no_match."""
    incomplete_data = [
        {
            "query_id": "QUERY_INCOMPLETE",
            "query_text": "A suspect hacked into the university database.",
            "split": "dev",
            "annotation_status": "reviewed",
            # missing expected_no_match and relevant_provision_ids
        }
    ]
    f = tmp_path / "incomplete_dataset.json"
    f.write_text(json.dumps(incomplete_data), encoding="utf-8")

    is_valid, issues = validate_evaluation_dataset(dataset_path=f)
    assert is_valid is False
    assert any("missing required ground-truth field" in issue for issue in issues)


def test_validator_detects_false_expected_no_match_with_empty_provisions(tmp_path: Path):
    """If expected_no_match is False, relevant_provision_ids must not be empty."""
    invalid_data = [
        {
            "query_id": "QUERY_INVALID_MATCH",
            "query_text": "Someone transferred funds using my stolen electronic token.",
            "split": "dev",
            "annotation_status": "reviewed",
            "expected_no_match": False,
            "relevant_provision_ids": [],  # Inconsistent: expected match but empty provisions
        }
    ]
    f = tmp_path / "invalid_match_dataset.json"
    f.write_text(json.dumps(invalid_data), encoding="utf-8")

    is_valid, issues = validate_evaluation_dataset(dataset_path=f)
    assert is_valid is False
    assert any("expected_no_match is False but relevant_provision_ids is empty" in issue for issue in issues)


def test_validator_detects_missing_provenance(tmp_path: Path):
    """Validator must detect missing rationale and reviewer attribution when provenance checking is enforced."""
    no_prov_data = [
        {
            "query_id": "QUERY_NO_PROV",
            "query_text": "Someone intercepted my banking OTP.",
            "split": "dev",
            "annotation_status": "reviewed",
            "expected_no_match": False,
            "relevant_provision_ids": ["ITA_2000_S66C"],
            # Missing rationale and reviewer notes
        }
    ]
    f = tmp_path / "no_prov_dataset.json"
    f.write_text(json.dumps(no_prov_data), encoding="utf-8")

    is_valid, issues = validate_evaluation_dataset(dataset_path=f, require_provenance=True)
    assert is_valid is False
    assert any("missing or empty required legal 'rationale'" in issue for issue in issues)
    assert any("missing required reviewer identification" in issue for issue in issues)


def test_validator_detects_blind_split_leakage(tmp_path: Path):
    """Validator must detect duplicate query IDs between blind and dev/test splits."""
    leak_data = [
        {
            "query_id": "COLLIDING_ID",
            "query_text": "Incident text for dev split query.",
            "split": "dev",
            "annotation_status": "reviewed",
            "expected_no_match": True,
            "relevant_provision_ids": [],
        },
        {
            "query_id": "COLLIDING_ID",
            "query_text": "Different incident text for blind split query.",
            "split": "blind",
            "annotation_status": "pending",
            "expected_no_match": True,
            "relevant_provision_ids": [],
        },
    ]
    f = tmp_path / "blind_leak_dataset.json"
    f.write_text(json.dumps(leak_data), encoding="utf-8")

    is_valid, issues = validate_evaluation_dataset(dataset_path=f, allow_blind=True)
    assert is_valid is False
    assert any("Duplicate query_id" in issue or "Split leakage detected" in issue for issue in issues)


def test_threshold_sweep_rejects_blind_benchmark_contamination(tmp_path: Path):
    """Threshold sweep must raise ValueError if executed on a blind benchmark dataset."""
    blind_dataset = [
        {
            "query_id": "BLIND_001",
            "query_text": "Blind incident complaint description.",
            "split": "blind",
            "annotation_status": "reviewed",
            "expected_no_match": True,
            "relevant_provision_ids": [],
        }
    ]
    f = tmp_path / "blind_only_dataset.json"
    f.write_text(json.dumps(blind_dataset), encoding="utf-8")

    with pytest.raises(ValueError, match="Contamination Error"):
        run_threshold_sweep(dataset_path=f)


def test_benchmark_lock_manifest_and_tamper_detection(tmp_path: Path):
    """Locking a benchmark registers SHA-256 in manifest; subsequent modification fails verification."""
    benchmark_file = tmp_path / "test_benchmark.json"
    manifest_file = tmp_path / "benchmark_manifest.json"
    content = [{"query_id": "Q1", "query_text": "Text", "split": "dev", "annotation_status": "reviewed", "expected_no_match": True, "relevant_provision_ids": []}]
    benchmark_file.write_text(json.dumps(content), encoding="utf-8")

    # 1. Lock benchmark
    lock_entry = lock_benchmark_file(benchmark_file, manifest_path=manifest_file, notes="Unit test lock")
    assert lock_entry["locked"] is True
    assert len(lock_entry["sha256"]) == 64

    # 2. Verify lock passes
    is_valid, issues = verify_benchmark_lock(benchmark_file, manifest_path=manifest_file)
    assert is_valid is True
    assert len(issues) == 0

    # 3. Tamper with file
    modified_content = content + [{"query_id": "Q2", "query_text": "Tampered", "split": "dev", "annotation_status": "reviewed", "expected_no_match": True, "relevant_provision_ids": []}]
    benchmark_file.write_text(json.dumps(modified_content), encoding="utf-8")

    # 4. Verify lock detects tampering
    is_valid_after, issues_after = verify_benchmark_lock(benchmark_file, manifest_path=manifest_file)
    assert is_valid_after is False
    assert any("has been modified or tampered with" in issue for issue in issues_after)


def test_assert_not_locked_prevents_overwrite(tmp_path: Path):
    """assert_not_locked must raise PermissionError if the target file is registered as locked."""
    benchmark_file = tmp_path / "locked_benchmark.json"
    manifest_file = tmp_path / "benchmark_manifest.json"
    benchmark_file.write_text(json.dumps([]), encoding="utf-8")

    lock_benchmark_file(benchmark_file, manifest_path=manifest_file)

    with pytest.raises(PermissionError, match="Integrity Violation: Attempted overwrite of locked benchmark"):
        assert_not_locked(benchmark_file, manifest_path=manifest_file)


def test_dataset_validator_require_all_reviewed(tmp_path: Path):
    """Validator with require_all_reviewed=True must fail on pending queries and pass on all-reviewed."""
    data = [
        {
            "query_id": "Q_REV",
            "query_text": "Reviewed text query sample.",
            "relevant_provision_ids": [],
            "expected_no_match": True,
            "split": "dev",
            "annotation_status": "reviewed",
        },
        {
            "query_id": "Q_PEND",
            "query_text": "Pending text query sample.",
            "relevant_provision_ids": [],
            "expected_no_match": True,
            "split": "dev",
            "annotation_status": "pending",
        },
    ]
    f = tmp_path / "pending_check.json"
    f.write_text(json.dumps(data), encoding="utf-8")

    # Default: passes with pending
    is_valid_default, _ = validate_evaluation_dataset(dataset_path=f)
    assert is_valid_default is True

    # Strict: fails on pending query
    is_valid_strict, issues_strict = validate_evaluation_dataset(dataset_path=f, require_all_reviewed=True)
    assert is_valid_strict is False
    assert any("Q_PEND" in issue and "must be 'reviewed'" in issue for issue in issues_strict)


def test_dataset_validator_require_adjudication(tmp_path: Path):
    """Validator with require_adjudication=True must enforce adjudicator metadata on reviewed queries."""
    unadjudicated_data = [
        {
            "query_id": "Q_REV_NO_ADJ",
            "query_text": "Reviewed text query without adjudicator metadata.",
            "relevant_provision_ids": [],
            "expected_no_match": True,
            "split": "dev",
            "annotation_status": "reviewed",
            "rationale": "Sample rationale text.",
            "reviewer_id": "REV_01",
        }
    ]
    f = tmp_path / "adjudication_check.json"
    f.write_text(json.dumps(unadjudicated_data), encoding="utf-8")

    # Strict adjudication check fails when metadata is missing
    is_valid_missing, issues_missing = validate_evaluation_dataset(dataset_path=f, require_adjudication=True)
    assert is_valid_missing is False
    assert any("missing required adjudication metadata" in issue for issue in issues_missing)

    # Adding adjudication metadata passes
    adjudicated_data = [
        {
            "query_id": "Q_REV_WITH_ADJ",
            "query_text": "Reviewed text query with adjudicator metadata.",
            "relevant_provision_ids": [],
            "expected_no_match": True,
            "split": "dev",
            "annotation_status": "reviewed",
            "rationale": "Sample rationale text.",
            "reviewer_id": "REV_01",
            "adjudicator_id": "SENIOR_LEGAL_ADJUDICATOR_01",
        }
    ]
    f.write_text(json.dumps(adjudicated_data), encoding="utf-8")
    is_valid_ok, issues_ok = validate_evaluation_dataset(dataset_path=f, require_adjudication=True)
    assert is_valid_ok is True
    assert len(issues_ok) == 0


def test_dataset_validator_temporal_consistency(tmp_path: Path):
    """Validator must detect Article 20(1) violations when pre-July 2024 query assigns BNS provisions."""
    invalid_pre_2024_data = [
        {
            "query_id": "Q_RETROACTIVE_BNS",
            "query_text": "In December 2023, an employee embezzled money through forged receipts.",
            "relevant_provision_ids": ["BNS_2023_S318"],  # Illegal ex post facto BNS assignment
            "expected_no_match": False,
            "split": "test",
            "annotation_status": "pending",
        }
    ]
    f = tmp_path / "retroactive_bns.json"
    f.write_text(json.dumps(invalid_pre_2024_data), encoding="utf-8")

    is_valid, issues = validate_evaluation_dataset(dataset_path=f)
    assert is_valid is False
    assert any("Article 20(1) Violation" in issue and "BNS_2023_S318" in issue for issue in issues)

    # Valid IPC assignment for pre-July 2024 passes
    valid_pre_2024_data = [
        {
            "query_id": "Q_LEGAL_IPC",
            "query_text": "In December 2023, an employee embezzled money through forged receipts.",
            "relevant_provision_ids": ["IPC_1860_S420"],  # Legal historical IPC assignment
            "expected_no_match": False,
            "split": "test",
            "annotation_status": "pending",
        }
    ]
    f.write_text(json.dumps(valid_pre_2024_data), encoding="utf-8")
    is_valid_ok, issues_ok = validate_evaluation_dataset(dataset_path=f)
    assert is_valid_ok is True
    assert len(issues_ok) == 0


def test_dataset_validator_provisional_statute_guard(tmp_path: Path):
    """Validator must reject reviewed ground truth assigning uncommenced provisional statutes."""
    provisional_data = [
        {
            "query_id": "Q_PROVISIONAL_REVIEWED",
            "query_text": "A tech platform leaked personal sensitive data without consent.",
            "relevant_provision_ids": ["DPDP_2023_S33_PROVISIONAL"],
            "expected_no_match": False,
            "split": "dev",
            "annotation_status": "reviewed",
        }
    ]
    f = tmp_path / "provisional_guard.json"
    f.write_text(json.dumps(provisional_data), encoding="utf-8")

    is_valid, issues = validate_evaluation_dataset(dataset_path=f)
    assert is_valid is False
    assert any("uncommenced provisional statute" in issue for issue in issues)


def test_blind_benchmark_schema_and_isolation():
    """Verify that blind_benchmark_dataset.json satisfies schema, non-leakage, and pending status."""
    blind_path = Path(__file__).resolve().parent.parent / "evaluation" / "blind_benchmark_dataset.json"
    assert blind_path.exists(), "blind_benchmark_dataset.json not found!"

    with open(blind_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert len(data) >= 25, f"Expected at least 25 queries, got {len(data)}"
    for item in data:
        assert item["split"] == "blind"
        assert item["annotation_status"] == "pending", f"Query {item['query_id']} must be pending human review"
        assert item["locked"] is False

    # Validates without errors under normal validation
    is_valid, issues = validate_evaluation_dataset(dataset_path=blind_path, allow_blind=True)
    assert is_valid is True, f"Validation issues: {issues}"

    # Fails under strict require_all_reviewed because real human review is pending
    is_valid_strict, issues_strict = validate_evaluation_dataset(
        dataset_path=blind_path,
        allow_blind=True,
        require_all_reviewed=True,
    )
    assert is_valid_strict is False
    assert len(issues_strict) == len(data)


def test_blind_benchmark_manifest_integrity():
    """Verify manifest registration, SHA-256 integrity, and truthful unlocked status."""
    backend_dir = Path(__file__).resolve().parent.parent
    blind_path = backend_dir / "evaluation" / "blind_benchmark_dataset.json"
    manifest_path = backend_dir / "evaluation" / "benchmark_manifest.json"

    assert manifest_path.exists(), "benchmark_manifest.json not found!"
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    entry = manifest.get("locked_benchmarks", {}).get("blind_benchmark_dataset.json")
    assert entry is not None, "blind_benchmark_dataset.json not registered in manifest!"

    # Calculate actual sha256
    import hashlib
    actual_sha = hashlib.sha256(blind_path.read_bytes()).hexdigest()
    assert entry["sha256"] == actual_sha, f"SHA-256 mismatch! Manifest: {entry['sha256']}, actual: {actual_sha}"
    assert entry["locked"] is False, "Draft benchmark must not be marked locked before human review"
    assert entry["status"] == "draft_pending_human_annotation"

    # verify_benchmark_lock correctly reports unlocked status
    from evaluation.eval_retrieval import verify_benchmark_lock
    is_verified, issues = verify_benchmark_lock(blind_path, manifest_path)
    assert is_verified is False
    assert any("marked unlocked" in iss for iss in issues)


def test_metric_calculation_with_acceptable_alternatives():
    """Retrieving an acceptable alternative satisfies the target concept with 100% recall."""
    # Scenario: Primary target is modern BNS 78, alternative is historical IPC 354D
    retrieved = ["IPC_1860_S354D", "IRRELEVANT_1", "IRRELEVANT_2"]
    relevant = {"BNS_2023_S78"}
    alternatives = {"IPC_1860_S354D"}

    metrics = compute_query_metrics(
        retrieved,
        relevant,
        k_precisions=[3, 5],
        k_recalls=[5, 10],
        acceptable_alternative_ids=alternatives,
    )

    assert metrics["reciprocal_rank"] == 1.0
    assert metrics["p_at_3"] == pytest.approx(1.0 / 3.0)
    assert metrics["r_at_5"] == 1.0  # Not penalized to 0.0 or 0.5


def test_metric_calculation_both_primary_and_alternative_retrieved():
    """Retrieving both primary and alternative for 1 concept caps recall at 1.0."""
    retrieved = ["BNS_2023_S78", "IPC_1860_S354D", "IRRELEVANT_1"]
    relevant = {"BNS_2023_S78"}
    alternatives = {"IPC_1860_S354D"}

    metrics = compute_query_metrics(
        retrieved,
        relevant,
        k_precisions=[3, 5],
        k_recalls=[5, 10],
        acceptable_alternative_ids=alternatives,
    )

    assert metrics["reciprocal_rank"] == 1.0
    assert metrics["p_at_3"] == pytest.approx(2.0 / 3.0)
    assert metrics["r_at_5"] == 1.0  # Bounded by num_relevant (1.0), not 2.0


def test_dataset_validator_detects_invalid_alternative_provision_id(tmp_path: Path):
    """Validator must detect unindexed provision IDs inside acceptable_alternative_ids."""
    invalid_alt_data = [
        {
            "query_id": "QUERY_DEV_TEST_ALT",
            "query_text": "Sample query with invalid alternative statute ID",
            "relevant_provision_ids": ["BNS_2023_S78"],
            "acceptable_alternative_ids": ["NONEXISTENT_STATUTE_ID_999"],
            "expected_no_match": False,
            "split": "dev",
            "annotation_status": "pending",
        }
    ]
    ds_file = tmp_path / "invalid_alt_dataset.json"
    ds_file.write_text(json.dumps(invalid_alt_data), encoding="utf-8")

    from evaluation.eval_retrieval import validate_evaluation_dataset
    is_valid, issues = validate_evaluation_dataset(ds_file)
    assert is_valid is False
    assert any("alternative provision ID 'NONEXISTENT_STATUTE_ID_999' does not exist" in iss for iss in issues)






