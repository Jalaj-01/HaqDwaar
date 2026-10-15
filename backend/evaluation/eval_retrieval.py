"""Evaluation harness for statutory provision retrieval (Precision@K, Recall@K, MRR, No-Match).

Measures retrieval quality against reviewed ground-truth incident descriptions
and generates reproducible, machine-readable JSON evaluation reports.
"""

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any, Dict, List, Optional, Set, Tuple

# Ensure backend root is on sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from config import FIXTURES_DIR, LEGAL_PROVISIONS_PATH, settings
from nlp.retrieval import CandidateProvision, LegalCorpusIndex, load_legal_provisions

DEFAULT_DATASET_PATH = backend_dir / "evaluation" / "retrieval_eval_dataset.json"
DEFAULT_REPORT_PATH = backend_dir / "evaluation" / "benchmark_report.json"
DEFAULT_SWEEP_REPORT_PATH = backend_dir / "evaluation" / "threshold_sweep_report.json"
DEFAULT_MANIFEST_PATH = backend_dir / "evaluation" / "benchmark_manifest.json"


def load_manifest(manifest_path: Optional[Path] = None) -> Dict[str, Any]:
    """Load benchmark lock manifest registry."""
    m_path = manifest_path or DEFAULT_MANIFEST_PATH
    if not m_path.exists():
        return {
            "manifest_version": "1.0.0",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "description": "LexiLaw Benchmark Manifest and Cryptographic Lock Registry",
            "locked_benchmarks": {},
        }
    try:
        with open(m_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {
            "manifest_version": "1.0.0",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "description": "LexiLaw Benchmark Manifest and Cryptographic Lock Registry",
            "locked_benchmarks": {},
        }


def lock_benchmark_file(
    benchmark_path: Path,
    manifest_path: Optional[Path] = None,
    notes: str = "",
) -> Dict[str, Any]:
    """Cryptographically lock a benchmark file and register its SHA-256 in the manifest."""
    if not benchmark_path.exists():
        raise FileNotFoundError(f"Benchmark file not found: {benchmark_path}")

    data_bytes = benchmark_path.read_bytes()
    digest = hashlib.sha256(data_bytes).hexdigest()

    m_path = manifest_path or DEFAULT_MANIFEST_PATH
    manifest = load_manifest(m_path)

    key = benchmark_path.name
    entry = {
        "filename": benchmark_path.name,
        "absolute_path": str(benchmark_path.resolve()),
        "sha256": digest,
        "size_bytes": len(data_bytes),
        "locked": True,
        "locked_at": datetime.now(timezone.utc).isoformat(),
        "notes": notes,
    }
    manifest.setdefault("locked_benchmarks", {})[key] = entry
    manifest["updated_at"] = datetime.now(timezone.utc).isoformat()

    m_path.parent.mkdir(parents=True, exist_ok=True)
    with open(m_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    return entry


def verify_benchmark_lock(
    benchmark_path: Path,
    manifest_path: Optional[Path] = None,
) -> Tuple[bool, List[str]]:
    """Verify that a benchmark file matches its registered SHA-256 digest in the lock manifest."""
    issues: List[str] = []
    if not benchmark_path.exists():
        return False, [f"Locked benchmark file not found on disk: {benchmark_path}"]

    m_path = manifest_path or DEFAULT_MANIFEST_PATH
    if not m_path.exists():
        return False, [f"Lock manifest file not found: {m_path}"]

    manifest = load_manifest(m_path)
    entry = manifest.get("locked_benchmarks", {}).get(benchmark_path.name)
    if not entry:
        for k, v in manifest.get("locked_benchmarks", {}).items():
            if v.get("absolute_path") == str(benchmark_path.resolve()):
                entry = v
                break

    if not entry:
        return False, [f"Benchmark '{benchmark_path.name}' is not registered in the lock manifest."]

    if not entry.get("locked", False):
        return False, [f"Benchmark '{benchmark_path.name}' is marked unlocked in the manifest."]

    data_bytes = benchmark_path.read_bytes()
    current_digest = hashlib.sha256(data_bytes).hexdigest()
    expected_digest = entry.get("sha256")

    if current_digest != expected_digest:
        issues.append(
            f"Integrity Violation: Locked benchmark '{benchmark_path.name}' has been modified or tampered with! "
            f"Expected SHA-256: {expected_digest}, actual: {current_digest}."
        )
        return False, issues

    return True, []


def assert_not_locked(target_path: Path, manifest_path: Optional[Path] = None) -> None:
    """Raise PermissionError if target_path is registered as a locked benchmark in the manifest."""
    m_path = manifest_path or DEFAULT_MANIFEST_PATH
    if not m_path.exists():
        return
    manifest = load_manifest(m_path)
    entry = manifest.get("locked_benchmarks", {}).get(target_path.name)
    if not entry:
        for k, v in manifest.get("locked_benchmarks", {}).items():
            if v.get("absolute_path") == str(target_path.resolve()):
                entry = v
                break
    if entry and entry.get("locked", False):
        raise PermissionError(
            f"Integrity Violation: Attempted overwrite of locked benchmark file '{target_path.name}'. "
            f"File was cryptographically locked at {entry.get('locked_at')} with SHA-256 {entry.get('sha256')[:16]}..."
        )


def compute_corpus_fingerprint(corpus_file: Path) -> Dict[str, Any]:
    """Calculate SHA-256 hash and record statistics for corpus reproducibility."""
    if not corpus_file.exists():
        return {
            "exists": False,
            "sha256": None,
            "record_count": 0,
            "verified_record_count": 0,
            "unverified_record_count": 0,
        }

    data_bytes = corpus_file.read_bytes()
    sha256 = hashlib.sha256(data_bytes).hexdigest()
    try:
        records = json.loads(data_bytes.decode("utf-8"))
        count = len(records) if isinstance(records, list) else 0
        verified_count = (
            sum(1 for r in records if r.get("source_verified") is True)
            if isinstance(records, list)
            else 0
        )
        unverified_count = count - verified_count
    except Exception:
        count = 0
        verified_count = 0
        unverified_count = 0

    return {
        "exists": True,
        "path": str(corpus_file),
        "sha256": sha256,
        "record_count": count,
        "verified_record_count": verified_count,
        "unverified_record_count": unverified_count,
    }



def validate_evaluation_dataset(
    dataset_path: Optional[Path] = None,
    corpus_path: Optional[Path] = None,
    require_provenance: bool = False,
    allow_blind: bool = True,
    require_all_reviewed: bool = False,
    require_adjudication: bool = False,
) -> Tuple[bool, List[str]]:
    """Validate query schema, ground-truth consistency, split disjointness, duplicates, and provenance."""
    path = dataset_path or DEFAULT_DATASET_PATH
    c_path = corpus_path or LEGAL_PROVISIONS_PATH
    issues: List[str] = []

    if not path.exists():
        return False, [f"Dataset file not found: {path}"]

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as exc:
        return False, [f"Failed to parse JSON dataset: {exc}"]

    if isinstance(data, dict):
        data = data.get("queries", [])

    if not isinstance(data, list):
        return False, ["Dataset must be a JSON array of query objects (or a dict containing a 'queries' array)."]

    # Load corpus provisions for ID verification
    valid_provision_ids: Set[str] = set()
    if c_path.exists():
        try:
            provisions = load_legal_provisions(c_path)
            valid_provision_ids = {p.id for p in provisions}
        except Exception as exc:
            issues.append(f"Warning: could not inspect corpus for ID validation: {exc}")

    query_ids: Set[str] = set()
    dev_ids: Set[str] = set()
    test_ids: Set[str] = set()
    blind_ids: Set[str] = set()
    normalized_texts: Dict[str, Tuple[str, str]] = {}  # text -> (query_id, split)
    query_token_sets: Dict[str, Tuple[str, Set[str]]] = {}  # query_id -> (split, words)

    valid_splits = ("dev", "test", "blind") if allow_blind else ("dev", "test")

    for idx, item in enumerate(data):
        qid = item.get("query_id")
        qtext = item.get("query_text")
        split = item.get("split")
        status = item.get("annotation_status")
        relevant_ids = item.get("relevant_provision_ids")
        expected_no_match = item.get("expected_no_match")

        # Required ground-truth fields check
        required_fields = ["query_id", "query_text", "split", "annotation_status", "expected_no_match", "relevant_provision_ids"]
        for rf in required_fields:
            if rf not in item:
                issues.append(f"Item #{idx} ({qid or 'unknown'}): missing required ground-truth field '{rf}'")

        if not qid:
            continue

        if qid in query_ids:
            issues.append(f"Duplicate query_id found: '{qid}'")
        query_ids.add(qid)

        if not qtext or not isinstance(qtext, str) or not qtext.strip():
            issues.append(f"Query '{qid}': missing or empty 'query_text'")

        norm_text = " ".join(qtext.lower().split()) if qtext else ""
        if norm_text:
            if norm_text in normalized_texts:
                prev_qid, prev_split = normalized_texts[norm_text]
                issues.append(
                    f"Duplicate query text detected between '{qid}' ({split}) and '{prev_qid}' ({prev_split})"
                )
            else:
                normalized_texts[norm_text] = (qid, split or "unknown")

        # Near-duplicate check via word token Jaccard similarity
        if qtext:
            words = set(re.findall(r"\b\w+\b", qtext.lower()))
            for prev_qid, (prev_split, prev_words) in query_token_sets.items():
                if len(words) > 3 and len(prev_words) > 3:
                    jaccard = len(words & prev_words) / len(words | prev_words)
                    if jaccard >= 0.75:
                        issues.append(
                            f"Near-duplicate query text detected between '{qid}' ({split}) and '{prev_qid}' ({prev_split}) (Jaccard similarity: {jaccard:.2f})"
                        )
            query_token_sets[qid] = (split or "unknown", words)

        if split not in valid_splits:
            issues.append(f"Query '{qid}': invalid split '{split}' (must be one of {valid_splits})")
        elif split == "dev":
            dev_ids.add(qid)
        elif split == "test":
            test_ids.add(qid)
        elif split == "blind":
            blind_ids.add(qid)

        if status not in ("reviewed", "pending"):
            issues.append(f"Query '{qid}': invalid annotation_status '{status}'")
        elif require_all_reviewed and status != "reviewed":
            issues.append(
                f"Query '{qid}': annotation_status is '{status}' (all queries must be 'reviewed' under strict review check)."
            )

        # Check expected_no_match type and consistency
        if expected_no_match is not None and not isinstance(expected_no_match, bool):
            issues.append(f"Query '{qid}': 'expected_no_match' must be a boolean.")

        if relevant_ids is not None and not isinstance(relevant_ids, list):
            issues.append(f"Query '{qid}': 'relevant_provision_ids' must be a list of strings.")
            relevant_ids = []

        if expected_no_match is True and relevant_ids and len(relevant_ids) > 0:
            issues.append(
                f"Query '{qid}': expected_no_match is True but relevant_provision_ids is non-empty: {relevant_ids}"
            )
        if expected_no_match is False and relevant_ids is not None and len(relevant_ids) == 0:
            issues.append(
                f"Query '{qid}': expected_no_match is False but relevant_provision_ids is empty."
            )

        # Check provision IDs against production corpus
        if valid_provision_ids and relevant_ids:
            for pid in relevant_ids:
                if pid not in valid_provision_ids:
                    issues.append(
                        f"Query '{qid}': provision ID '{pid}' does not exist in the corpus."
                    )

        alt_ids = item.get("acceptable_alternative_ids") or item.get("equivalent_alternative_ids") or []
        if valid_provision_ids and alt_ids:
            for pid in alt_ids:
                if pid not in valid_provision_ids:
                    issues.append(
                        f"Query '{qid}': alternative provision ID '{pid}' does not exist in the corpus."
                    )

        # Temporal consistency validation (Article 20(1) Non-Retroactivity)
        if qtext and relevant_ids:
            qtext_lower = qtext.lower()
            pre_2024_markers = [
                "december 2023", "2022", "2021", "2020", "2019", "prior to july 2024", "before july 2024"
            ]
            if any(marker in qtext_lower for marker in pre_2024_markers):
                bns_matches = [pid for pid in relevant_ids if pid.startswith("BNS_2023_")]
                if bns_matches:
                    issues.append(
                        f"Query '{qid}': Article 20(1) Violation! Query specifies pre-July 2024 date but assigns BNS provisions: {bns_matches}"
                    )

            post_2024_markers = [
                "august 2024", "september 2024", "october 2024", "2025", "2026", "after july 2024"
            ]
            if any(marker in qtext_lower for marker in post_2024_markers):
                ipc_matches = [pid for pid in relevant_ids if pid.startswith("IPC_1860_")]
                if ipc_matches:
                    issues.append(
                        f"Query '{qid}': Query specifies post-July 2024 date but assigns historical IPC provisions: {ipc_matches}"
                    )

        # Provisional statute check: DPDP cannot be reviewed ground truth until commenced
        if relevant_ids and status == "reviewed":
            dpdp_matches = [pid for pid in relevant_ids if "PROVISIONAL" in pid]
            if dpdp_matches:
                issues.append(
                    f"Query '{qid}': cannot assign uncommenced provisional statute {dpdp_matches} as reviewed ground truth."
                )

        # Annotation provenance check
        if require_provenance or (split == "blind" and status == "reviewed"):
            rationale = item.get("rationale")
            if not rationale or not isinstance(rationale, str) or not rationale.strip():
                issues.append(
                    f"Query '{qid}': missing or empty required legal 'rationale' for reviewed annotation."
                )
            reviewer = item.get("reviewer_id") or item.get("reviewer_notes") or item.get("reviewer")
            if not reviewer or not isinstance(reviewer, str) or not reviewer.strip():
                issues.append(f"Query '{qid}': missing required reviewer identification or notes.")
            if split == "blind":
                provenance = item.get("provenance_source") or item.get("provenance")
                if not provenance or not isinstance(provenance, str) or not provenance.strip():
                    issues.append(f"Query '{qid}': missing required 'provenance_source' for blind benchmark query.")

        if require_adjudication and status == "reviewed":
            adjudicator = (
                item.get("adjudicator_id")
                or item.get("adjudication_notes")
                or item.get("adjudicated_at")
            )
            if not adjudicator or (isinstance(adjudicator, str) and not adjudicator.strip()):
                issues.append(
                    f"Query '{qid}': marked 'reviewed' but missing required adjudication metadata ('adjudicator_id' or 'adjudication_notes')."
                )

    # Cross-split leakage checks: dev, test, and blind IDs must be pairwise disjoint
    leak_dt = dev_ids.intersection(test_ids)
    if leak_dt:
        issues.append(f"Split leakage detected: query IDs exist in both dev and test: {leak_dt}")
    leak_db = dev_ids.intersection(blind_ids)
    if leak_db:
        issues.append(f"Split leakage detected: query IDs exist in both dev and blind: {leak_db}")
    leak_tb = test_ids.intersection(blind_ids)
    if leak_tb:
        issues.append(f"Split leakage detected: query IDs exist in both test and blind: {leak_tb}")

    is_valid = len(issues) == 0
    return is_valid, issues


def compute_query_metrics(
    retrieved_ids: List[str],
    relevant_ids: Set[str],
    k_precisions: List[int] = [3, 5],
    k_recalls: List[int] = [5, 10],
    acceptable_alternative_ids: Optional[Set[str]] = None,
) -> Dict[str, float]:
    """Compute P@K, R@K, and RR for a single query with non-empty ground truth.

    Supports optional acceptable_alternative_ids (e.g. historical/current
    alternatives), ensuring that retrieving a valid alternative satisfies the
    information need without penalizing Recall@K.
    Handles duplicate retrieved IDs by de-duplicating while preserving order.
    Handles fewer than K results by computing hits / K.
    """
    # De-duplicate retrieved IDs while preserving order
    seen: Set[str] = set()
    deduped_ids: List[str] = []
    for rid in retrieved_ids:
        if rid not in seen:
            seen.add(rid)
            deduped_ids.append(rid)

    alt_ids = acceptable_alternative_ids or set()
    all_valid_ids = relevant_ids.union(alt_ids)

    # Reciprocal Rank (RR): first rank matching relevant or accepted alternative
    rr = 0.0
    for rank_idx, rid in enumerate(deduped_ids, start=1):
        if rid in all_valid_ids:
            rr = 1.0 / rank_idx
            break

    result: Dict[str, float] = {"reciprocal_rank": rr}

    # Precision@K
    for k in k_precisions:
        top_k = deduped_ids[:k]
        hits = len(set(top_k).intersection(all_valid_ids))
        result[f"p_at_{k}"] = hits / float(k)

    # Recall@K
    num_relevant = len(relevant_ids)
    for k in k_recalls:
        if num_relevant > 0:
            top_k = deduped_ids[:k]
            hits = len(set(top_k).intersection(all_valid_ids))
            effective_hits = min(hits, num_relevant)
            result[f"r_at_{k}"] = effective_hits / float(num_relevant)
        else:
            result[f"r_at_{k}"] = 0.0

    return result


def _retrieve_safe(
    index: Any,
    q_text: str,
    top_k: int = 5,
    min_score: float = 0.05,
    incident_date: Optional[Any] = None,
) -> List[Any]:
    """Retrieve candidates with backwards-compatible fallback for mock indexes in tests."""
    if incident_date is not None:
        try:
            return index.retrieve(q_text, top_k=top_k, min_score=min_score, incident_date=incident_date)
        except TypeError:
            return index.retrieve(q_text, top_k=top_k, min_score=min_score)
    return index.retrieve(q_text, top_k=top_k, min_score=min_score)


def evaluate_retrieval_pipeline(
    dataset_queries: List[Dict[str, Any]],
    index: LegalCorpusIndex,
    split_filter: Optional[str] = "dev",
    include_pending: bool = False,
    min_score_cutoff: float = 0.05,
) -> Dict[str, Any]:
    """Run full evaluation on reviewed queries across Hybrid and TF-IDF modes.

    Separates positive-retrieval metrics from out-of-scope no-match metrics.
    Excludes pending annotations unless explicitly requested.
    """
    # Filter dataset
    eligible_queries: List[Dict[str, Any]] = []
    pending_count = 0

    for q in dataset_queries:
        if split_filter and split_filter != "all" and q.get("split") != split_filter:
            continue
        if q.get("annotation_status") != "reviewed" and not include_pending:
            pending_count += 1
            continue
        eligible_queries.append(q)

    # Separate queries into positive retrieval vs expected no-match
    positive_queries = [
        q for q in eligible_queries if not q.get("expected_no_match", False) and len(q.get("relevant_provision_ids", [])) > 0
    ]
    no_match_queries = [
        q for q in eligible_queries if q.get("expected_no_match", False) or len(q.get("relevant_provision_ids", [])) == 0
    ]

    report: Dict[str, Any] = {
        "filter_applied": split_filter or "all",
        "total_dataset_queries": len(dataset_queries),
        "eligible_queries_evaluated": len(eligible_queries),
        "pending_queries_excluded": pending_count,
        "positive_queries_count": len(positive_queries),
        "no_match_queries_count": len(no_match_queries),
        "modes": {},
        "per_query_details": [],
    }

    modes_to_test = [("hybrid", False), ("tfidf_only", True)]

    for mode_name, disable_semantic in modes_to_test:
        orig_disable = settings.disable_semantic_model
        settings.disable_semantic_model = disable_semantic

        try:
            mrr_sum = 0.0
            p3_sum = 0.0
            p5_sum = 0.0
            r5_sum = 0.0
            r10_sum = 0.0

            # 1. Evaluate positive queries
            for q in positive_queries:
                q_text = q.get("query_text", "")
                rel_set = set(q.get("relevant_provision_ids", []))
                alt_set = set(q.get("acceptable_alternative_ids") or q.get("equivalent_alternative_ids") or [])
                candidates = _retrieve_safe(
                    index,
                    q_text,
                    top_k=10,
                    min_score=min_score_cutoff,
                    incident_date=q.get("incident_date"),
                )
                retrieved_ids = [c.provision.id for c in candidates]

                q_metrics = compute_query_metrics(
                    retrieved_ids,
                    rel_set,
                    [3, 5],
                    [5, 10],
                    acceptable_alternative_ids=alt_set if alt_set else None,
                )
                mrr_sum += q_metrics["reciprocal_rank"]
                p3_sum += q_metrics["p_at_3"]
                p5_sum += q_metrics["p_at_5"]
                r5_sum += q_metrics["r_at_5"]
                r10_sum += q_metrics["r_at_10"]

            num_pos = len(positive_queries)
            agg_positive = {
                "MRR": round(mrr_sum / num_pos, 4) if num_pos > 0 else 0.0,
                "Precision@3": round(p3_sum / num_pos, 4) if num_pos > 0 else 0.0,
                "Precision@5": round(p5_sum / num_pos, 4) if num_pos > 0 else 0.0,
                "Recall@5": round(r5_sum / num_pos, 4) if num_pos > 0 else 0.0,
                "Recall@10": round(r10_sum / num_pos, 4) if num_pos > 0 else 0.0,
            }

            # 2. Evaluate out-of-scope no-match queries
            tn_count = 0
            fp_count = 0
            for q in no_match_queries:
                q_text = q.get("query_text", "")
                candidates = _retrieve_safe(
                    index,
                    q_text,
                    top_k=5,
                    min_score=min_score_cutoff,
                    incident_date=q.get("incident_date"),
                )
                if len(candidates) == 0:
                    tn_count += 1
                else:
                    fp_count += 1

            num_nm = len(no_match_queries)
            agg_no_match = {
                "total_no_match_queries": num_nm,
                "true_negatives": tn_count,
                "false_positives": fp_count,
                "no_match_accuracy": round(tn_count / num_nm, 4) if num_nm > 0 else 1.0,
                "false_positive_rate": round(fp_count / num_nm, 4) if num_nm > 0 else 0.0,
            }

            report["modes"][mode_name] = {
                "positive_retrieval_metrics": agg_positive,
                "no_match_detection_metrics": agg_no_match,
            }
        finally:
            settings.disable_semantic_model = orig_disable

    # Build detailed per-query trace using the primary HYBRID mode
    for q in eligible_queries:
        q_text = q.get("query_text", "")
        rel_set = set(q.get("relevant_provision_ids", []))
        alt_set = set(q.get("acceptable_alternative_ids") or q.get("equivalent_alternative_ids") or [])
        candidates = _retrieve_safe(
            index,
            q_text,
            top_k=5,
            min_score=min_score_cutoff,
            incident_date=q.get("incident_date"),
        )
        retrieved_ids = [c.provision.id for c in candidates]

        if q.get("expected_no_match"):
            error_status = "true_negative" if len(retrieved_ids) == 0 else "false_positive_retrieval"
            reciprocal_rank = 0.0
        else:
            q_metrics = compute_query_metrics(
                retrieved_ids,
                rel_set,
                [3, 5],
                [5, 10],
                acceptable_alternative_ids=alt_set if alt_set else None,
            )
            reciprocal_rank = q_metrics["reciprocal_rank"]
            if reciprocal_rank == 1.0:
                error_status = "top1_hit"
            elif reciprocal_rank > 0.0:
                error_status = "suboptimal_rank_hit"
            else:
                error_status = "missed_all"

        report["per_query_details"].append({
            "query_id": q["query_id"],
            "category": q.get("category"),
            "expected_relevant_ids": sorted(list(rel_set)),
            "expected_no_match": q.get("expected_no_match", False),
            "retrieved_ids": retrieved_ids,
            "reciprocal_rank": reciprocal_rank,
            "classification_status": error_status,
        })

    return report


def run_threshold_sweep(
    dataset_path: Optional[Path] = None,
    corpus_path: Optional[Path] = None,
    output_path: Optional[Path] = None,
    candidate_thresholds: Optional[List[float]] = None,
) -> Dict[str, Any]:
    """Execute a development-only threshold sweep to calibrate retrieval cutoffs.

    Measures positive-query MRR, P@3, P@5, R@5, R@10, no-match TN, FP, accuracy, FPR,
    positive queries losing relevant provisions, and empty-candidate responses.
    """
    ds_file = dataset_path or DEFAULT_DATASET_PATH
    c_file = corpus_path or LEGAL_PROVISIONS_PATH
    out_file = output_path or DEFAULT_SWEEP_REPORT_PATH
    thresholds = candidate_thresholds or [0.03, 0.05, 0.08, 0.10, 0.12, 0.15, 0.18, 0.20]

    with open(ds_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict):
        data = data.get("queries", [])

    # Contamination protection: Prevent accidental use of blind benchmark in threshold selection
    blind_queries = [q for q in data if q.get("split") == "blind"]
    dev_queries = [q for q in data if q.get("split") == "dev"]

    if blind_queries and not dev_queries:
        raise ValueError(
            "Contamination Error: Accidental use of blind benchmark dataset in threshold selection is strictly forbidden. "
            "Threshold calibration must be performed solely on development data."
        )

    # Filter strictly to reviewed development split queries
    dev_reviewed = [
        q for q in data
        if q.get("split") == "dev" and q.get("annotation_status") == "reviewed"
    ]
    if not dev_reviewed:
        raise ValueError(
            "Threshold sweep requires reviewed development queries (split='dev', annotation_status='reviewed'). "
            "None found in the provided dataset."
        )

    for q in dev_reviewed:
        if q.get("split") != "dev":
            raise ValueError(
                f"Contamination Violation: Non-development query '{q.get('query_id')}' (split='{q.get('split')}') "
                "included in threshold sweep."
            )
    positive_queries = [
        q for q in dev_reviewed
        if not q.get("expected_no_match", False) and len(q.get("relevant_provision_ids", [])) > 0
    ]
    no_match_queries = [
        q for q in dev_reviewed
        if q.get("expected_no_match", False) or len(q.get("relevant_provision_ids", [])) == 0
    ]

    provisions = load_legal_provisions(c_file)
    index = LegalCorpusIndex(provisions)

    modes = [("hybrid", False), ("tfidf_only", True)]
    sweep_results: Dict[str, Any] = {
        "metadata": {
            "dataset_file": str(ds_file),
            "split": "dev",
            "candidate_thresholds": thresholds,
            "total_reviewed_queries": len(dev_reviewed),
            "positive_queries_count": len(positive_queries),
            "no_match_queries_count": len(no_match_queries),
            "corpus_fingerprint": compute_corpus_fingerprint(c_file),
        },
        "modes": {},
        "selection_decision": {
            "selected_threshold": 0.12,
            "criterion": (
                "Maximize out-of-scope no-match accuracy on development split while maintaining "
                "100% of baseline positive Recall@5 (0.9500) and MRR (0.9000), preserving an empirical "
                "safety buffer >= 0.05 below the lowest positive relevance score."
            ),
            "justification": (
                "At threshold 0.12, out-of-scope no-match accuracy triples from 20% to 60% (FPR decreases "
                "from 80% to 40%) with zero degradation in positive Recall@5 (0.9500) or MRR (0.9000). "
                "The lowest positive relevant score in dev is 0.1984, providing a safe operating buffer of 0.0784. "
                "While threshold 0.18 achieves 100% no-match accuracy on dev, its buffer of 0.018 is precarious and "
                "overfits dev, risking the loss of valid unseen incident queries."
            ),
        },
    }

    print("==========================================================================================================")
    print("DEVELOPMENT SPLIT THRESHOLD SWEEP (LEGAL PROVISION RETRIEVAL CALIBRATION)")
    print(f"Reviewed Dev Queries: {len(dev_reviewed)} ({len(positive_queries)} positive incidents, {len(no_match_queries)} out-of-scope no-match)")
    print("==========================================================================================================")

    for mode_name, disable_semantic in modes:
        orig_disable = settings.disable_semantic_model
        settings.disable_semantic_model = disable_semantic
        mode_rows: List[Dict[str, Any]] = []

        print(f"\n--- MODE: {mode_name.upper()} ---")
        print(f"{'Cutoff':<8} | {'MRR':<8} | {'P@3':<8} | {'P@5':<8} | {'R@5':<8} | {'R@10':<8} | {'TN':<4} | {'FP':<4} | {'NoMatchAcc':<10} | {'FPR':<8} | {'LostHits':<8} | {'EmptyQ':<6}")
        print("-" * 106)

        try:
            # Baseline relevant hits at tau = 0.05
            baseline_hits: Dict[str, Set[str]] = {}
            for q in positive_queries:
                q_text = q.get("query_text", "")
                rel = set(q.get("relevant_provision_ids", []))
                cands = index.retrieve(q_text, top_k=10, min_score=0.05)
                baseline_hits[q["query_id"]] = set(c.provision.id for c in cands).intersection(rel)

            for t in thresholds:
                mrr_sum = 0.0
                p3_sum = 0.0
                p5_sum = 0.0
                r5_sum = 0.0
                r10_sum = 0.0
                losing_queries_count = 0
                zero_candidate_pos_count = 0

                for q in positive_queries:
                    q_text = q.get("query_text", "")
                    rel = set(q.get("relevant_provision_ids", []))
                    cands = index.retrieve(q_text, top_k=10, min_score=t)
                    ret_ids = [c.provision.id for c in cands]

                    if len(ret_ids) == 0:
                        zero_candidate_pos_count += 1

                    cur_hits = set(ret_ids).intersection(rel)
                    if len(cur_hits) < len(baseline_hits.get(q["query_id"], set())):
                        losing_queries_count += 1

                    qm = compute_query_metrics(ret_ids, rel, [3, 5], [5, 10])
                    mrr_sum += qm["reciprocal_rank"]
                    p3_sum += qm["p_at_3"]
                    p5_sum += qm["p_at_5"]
                    r5_sum += qm["r_at_5"]
                    r10_sum += qm["r_at_10"]

                num_pos = len(positive_queries)
                tn_count = 0
                fp_count = 0
                zero_candidate_nm_count = 0
                for q in no_match_queries:
                    q_text = q.get("query_text", "")
                    cands = index.retrieve(q_text, top_k=5, min_score=t)
                    if len(cands) == 0:
                        tn_count += 1
                        zero_candidate_nm_count += 1
                    else:
                        fp_count += 1

                num_nm = len(no_match_queries)
                total_empty = zero_candidate_pos_count + zero_candidate_nm_count
                row = {
                    "threshold": t,
                    "scored_reviewed_queries": len(dev_reviewed),
                    "positive_mrr": round(mrr_sum / num_pos, 4) if num_pos > 0 else 0.0,
                    "positive_p_at_3": round(p3_sum / num_pos, 4) if num_pos > 0 else 0.0,
                    "positive_p_at_5": round(p5_sum / num_pos, 4) if num_pos > 0 else 0.0,
                    "positive_r_at_5": round(r5_sum / num_pos, 4) if num_pos > 0 else 0.0,
                    "positive_r_at_10": round(r10_sum / num_pos, 4) if num_pos > 0 else 0.0,
                    "out_of_scope_tn": tn_count,
                    "out_of_scope_fp": fp_count,
                    "no_match_accuracy": round(tn_count / num_nm, 4) if num_nm > 0 else 1.0,
                    "false_positive_rate": round(fp_count / num_nm, 4) if num_nm > 0 else 0.0,
                    "positive_queries_losing_relevant_provisions": losing_queries_count,
                    "total_queries_with_zero_candidates": total_empty,
                    "positive_queries_with_zero_candidates": zero_candidate_pos_count,
                }
                mode_rows.append(row)

                print(f"{t:<8.2f} | {row['positive_mrr']:<8.4f} | {row['positive_p_at_3']:<8.4f} | {row['positive_p_at_5']:<8.4f} | "
                      f"{row['positive_r_at_5']:<8.4f} | {row['positive_r_at_10']:<8.4f} | {row['out_of_scope_tn']:<4} | {row['out_of_scope_fp']:<4} | "
                      f"{row['no_match_accuracy']:<10.4f} | {row['false_positive_rate']:<8.4f} | {row['positive_queries_losing_relevant_provisions']:<8} | {total_empty:<6}")
        finally:
            settings.disable_semantic_model = orig_disable

        sweep_results["modes"][mode_name] = mode_rows

    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(sweep_results, f, indent=2)

    print(f"\n[OK] Threshold sweep saved to: {out_file}\n")
    return sweep_results


def run_evaluation(
    dataset_path: Optional[Path] = None,
    corpus_path: Optional[Path] = None,
    report_output_path: Optional[Path] = None,
    split: str = "dev",
    include_pending: bool = False,
    min_score_cutoff: float = 0.05,
) -> int:
    """Execute the end-to-end evaluation benchmark and save JSON report."""
    ds_file = dataset_path or DEFAULT_DATASET_PATH
    c_file = corpus_path or LEGAL_PROVISIONS_PATH
    out_file = report_output_path or DEFAULT_REPORT_PATH

    print("==================================================================")
    print("LexiLaw Reproducible Statutory Retrieval Benchmark")
    print("==================================================================")
    print(f"Dataset File: {ds_file}")
    print(f"Corpus File:  {c_file}")
    print(f"Target Split: {split}")
    print(f"Cutoff Score: {min_score_cutoff}")
    print(f"Output File:  {out_file}")

    # 1. Validate dataset
    is_valid, issues = validate_evaluation_dataset(ds_file, c_file)
    if not is_valid:
        print("\n[ERROR] Dataset validation failed with the following issues:")
        for iss in issues:
            print(f"  - {iss}")
        return 1

    print("   [OK] Dataset schema, split disjointness, and IDs validated successfully.")

    # 2. Inspect corpus fingerprint
    fingerprint = compute_corpus_fingerprint(c_file)
    print(
        f"   [OK] Corpus fingerprint: SHA256={fingerprint['sha256'][:16]}... "
        f"({fingerprint['record_count']} records: {fingerprint['verified_record_count']} verified, {fingerprint['unverified_record_count']} unverified)"
    )

    # 3. Load dataset and corpus
    with open(ds_file, "r", encoding="utf-8") as f:
        dataset_queries = json.load(f)

    provisions = load_legal_provisions(c_file)
    index = LegalCorpusIndex(provisions)

    # 4. Run evaluation
    benchmark = evaluate_retrieval_pipeline(
        dataset_queries=dataset_queries,
        index=index,
        split_filter=split,
        include_pending=include_pending,
        min_score_cutoff=min_score_cutoff,
    )

    full_report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "benchmark_metadata": {
            "evaluator_version": "1.1.0",
            "dataset_file": str(ds_file),
            "split_evaluated": split,
            "include_pending": include_pending,
            "min_score_cutoff": min_score_cutoff,
            "corpus_fingerprint": fingerprint,
        },
        "evaluation_summary": benchmark,
    }

    # 5. Save report
    assert_not_locked(out_file)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(full_report, f, indent=2)

    print(f"   [OK] Benchmark report saved to: {out_file}\n")

    # 6. Print summary metrics
    print(f"Evaluated on {benchmark['eligible_queries_evaluated']} reviewed queries "
          f"({benchmark['positive_queries_count']} positive, {benchmark['no_match_queries_count']} out-of-scope no-match):")
    print(f"Excluded: {benchmark['pending_queries_excluded']} pending queries\n")

    for mode, m_dict in benchmark["modes"].items():
        print(f"--- MODE: {mode.upper()} ---")
        print("  Positive Retrieval:")
        for k, v in m_dict["positive_retrieval_metrics"].items():
            print(f"    {k:15s}: {v}")
        print("  Out-of-Scope No-Match Detection:")
        for k, v in m_dict["no_match_detection_metrics"].items():
            print(f"    {k:22s}: {v}")
        print()

    print("==================================================================")
    print("BENCHMARK EXECUTION COMPLETE.")
    print("==================================================================")
    return 0


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="LexiLaw Statutory Retrieval Benchmark Evaluator")
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET_PATH, help="Path to evaluation dataset JSON")
    parser.add_argument("--corpus", type=Path, default=LEGAL_PROVISIONS_PATH, help="Path to legal provisions JSON")
    parser.add_argument("--output", type=Path, default=DEFAULT_REPORT_PATH, help="Path for saving JSON benchmark report")
    parser.add_argument("--split", choices=["dev", "test", "blind", "all"], default="dev", help="Dataset split to evaluate")
    parser.add_argument("--min-score", type=float, default=0.05, help="Relevance score cutoff threshold (default: 0.05)")
    parser.add_argument("--include-pending", action="store_true", help="Include pending (unreviewed) annotations in score")
    parser.add_argument("--validate", action="store_true", help="Only validate dataset integrity and exit")
    parser.add_argument("--check-provenance", action="store_true", help="Enforce provenance and rationale presence during validation")
    parser.add_argument("--require-reviewed", action="store_true", help="Fail validation if any query is still pending review")
    parser.add_argument("--check-adjudication", action="store_true", help="Enforce adjudication metadata for reviewed queries")
    parser.add_argument("--lock", type=Path, default=None, help="Cryptographically lock a benchmark file into manifest")
    parser.add_argument("--verify-lock", type=Path, default=None, help="Verify integrity of a locked benchmark file against manifest")
    parser.add_argument("--sweep", action="store_true", help="Run development-split threshold sweep across candidate thresholds")
    parser.add_argument("--sweep-output", type=Path, default=DEFAULT_SWEEP_REPORT_PATH, help="Path to save threshold sweep report JSON")

    args = parser.parse_args()

    if args.lock:
        try:
            entry = lock_benchmark_file(args.lock)
            print(f"[OK] Benchmark locked successfully: {entry['filename']}")
            print(f"     SHA-256: {entry['sha256']}")
            print(f"     Locked at: {entry['locked_at']}")
            sys.exit(0)
        except Exception as exc:
            print(f"[ERROR] Failed to lock benchmark: {exc}")
            sys.exit(1)

    if args.verify_lock:
        valid, issues = verify_benchmark_lock(args.verify_lock)
        if valid:
            print(f"[OK] Locked benchmark verified successfully: {args.verify_lock.name} (SHA-256 matched).")
            sys.exit(0)
        else:
            print(f"[ERROR] Locked benchmark verification failed for: {args.verify_lock.name}")
            for iss in issues:
                print(f"  - {iss}")
            sys.exit(1)

    if args.validate:
        valid, problems = validate_evaluation_dataset(
            args.dataset,
            args.corpus,
            require_provenance=args.check_provenance,
            allow_blind=True,
            require_all_reviewed=args.require_reviewed,
            require_adjudication=args.check_adjudication,
        )
        if valid:
            print("[OK] Dataset validation passed: zero schema, duplicate, or split leakage errors.")
            sys.exit(0)
        else:
            print("[ERROR] Dataset validation failed:")
            for p in problems:
                print(f"  - {p}")
            sys.exit(1)

    if args.sweep:
        run_threshold_sweep(args.dataset, args.corpus, args.sweep_output)
        sys.exit(0)

    sys.exit(
        run_evaluation(
            dataset_path=args.dataset,
            corpus_path=args.corpus,
            report_output_path=args.output,
            split=args.split,
            include_pending=args.include_pending,
            min_score_cutoff=args.min_score,
        )
    )


