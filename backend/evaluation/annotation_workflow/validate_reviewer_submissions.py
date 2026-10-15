"""
LexiLaw — Human Annotation Submission Validator & Inter-Annotator Agreement Engine

This module provides programmatic validation and agreement metrics for:
1. Reviewer submission packets (Reviewer A & Reviewer B).
2. Ground-truth provision IDs against the 37 active corpus entries.
3. Temporal consistency under Article 20(1) (IPC pre-July 2024 vs BNS post-July 2024).
4. Inter-annotator agreement metrics:
   - Exact-Set Match Ratio
   - Mean Pairwise Jaccard Similarity
   - Cohen's Kappa for binary expected_no_match decisions
5. Adjudication completeness verification before dataset ingestion.
"""

import os
import sys
import json
import re
import argparse
from typing import Dict, List, Set, Any, Tuple, Optional

CORPUS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "legal_provisions.json")
EVAL_DATASET_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "retrieval_eval_dataset.json")
BLIND_DATASET_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "blind_benchmark_dataset.json")
MANIFEST_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ANNOTATION_PENDING_MANIFEST.json")


def load_valid_corpus_ids(corpus_path: str = CORPUS_PATH) -> Set[str]:
    """Load canonical provision IDs from the active legal corpus."""
    if not os.path.exists(corpus_path):
        raise FileNotFoundError(f"Corpus file not found: {corpus_path}")
    with open(corpus_path, "r", encoding="utf-8") as f:
        provisions = json.load(f)
    return {p.get("id") or p.get("provision_id") for p in provisions if p.get("id") or p.get("provision_id")}


def check_temporal_consistency(query_text: str, provision_ids: List[str]) -> Tuple[bool, str]:
    """Verify statutory provision era matches explicit dates in query text under Article 20(1)."""
    text_lower = query_text.lower()
    
    # Check for explicit pre-July 2024 dates
    pre_2024_matches = re.search(r"\b(in\s+)?(january|february|march|april|may|june|november|december|october)\s+2023\b|\b(in\s+)?(january|february|march|april|may|june)\s+2024\b", text_lower)
    # Check for explicit post-July 2024 dates
    post_2024_matches = re.search(r"\b(in\s+)?(july|august|september|october|november|december)\s+2024\b|\b2025\b", text_lower)
    
    for pid in provision_ids:
        if pre_2024_matches and pid.startswith("BNS_2023_"):
            return False, f"Article 20(1) Violation: Pre-July 2024 scenario contains modern provision '{pid}'"
        if post_2024_matches and pid.startswith("IPC_1860_"):
            return False, f"Article 20(1) Violation: Post-July 2024 scenario contains repealed provision '{pid}'"
            
    return True, "Temporal era consistent"


def compute_pairwise_jaccard(set_a: Set[str], set_b: Set[str]) -> float:
    """Compute Jaccard similarity coefficient between two sets."""
    if not set_a and not set_b:
        return 1.0
    union = set_a.union(set_b)
    if not union:
        return 1.0
    return len(set_a.intersection(set_b)) / len(union)


def compute_cohens_kappa(labels_a: List[bool], labels_b: List[bool]) -> float:
    """Compute Cohen's Kappa for binary classifications."""
    if len(labels_a) != len(labels_b) or len(labels_a) == 0:
        return 0.0
    n = len(labels_a)
    
    # Observed agreement
    po = sum(1 for a, b in zip(labels_a, labels_b) if a == b) / n
    
    # Marginal probabilities
    a_true = sum(1 for a in labels_a if a) / n
    a_false = 1.0 - a_true
    b_true = sum(1 for b in labels_b if b) / n
    b_false = 1.0 - b_true
    
    pe = (a_true * b_true) + (a_false * b_false)
    
    if pe == 1.0:
        return 1.0
    return (po - pe) / (1.0 - pe)


def validate_single_record(record: Dict[str, Any], valid_corpus_ids: Set[str]) -> List[str]:
    """Validate a single reviewer determination record."""
    errors = []
    qid = record.get("query_id", "UNKNOWN")
    
    # 1. Required fields
    if "expected_no_match" not in record or record["expected_no_match"] is None:
        errors.append(f"[{qid}] Missing required boolean 'expected_no_match'")
    if "relevant_provision_ids" not in record:
        errors.append(f"[{qid}] Missing list 'relevant_provision_ids'")
        
    expected_no_match = record.get("expected_no_match")
    provisions = record.get("relevant_provision_ids", [])
    
    # 2. No-match consistency
    if expected_no_match is True and len(provisions) > 0:
        errors.append(f"[{qid}] Inconsistency: expected_no_match is True, but relevant_provision_ids is not empty: {provisions}")
    elif expected_no_match is False and len(provisions) == 0:
        errors.append(f"[{qid}] Inconsistency: expected_no_match is False, but relevant_provision_ids is empty")
        
    # 3. Canonical Corpus Membership
    for pid in provisions:
        if pid not in valid_corpus_ids:
            errors.append(f"[{qid}] Invalid provision ID '{pid}' not in active 37-provision corpus")
            
    # 4. Temporal consistency if query_text is available
    if "query_text" in record and record["query_text"]:
        is_consistent, reason = check_temporal_consistency(record["query_text"], provisions)
        if not is_consistent:
            errors.append(f"[{qid}] {reason}")
            
    return errors


def compare_reviewer_submissions(sub_a: List[Dict[str, Any]], sub_b: List[Dict[str, Any]], valid_corpus_ids: Set[str]) -> Dict[str, Any]:
    """Compare submissions from Reviewer A and Reviewer B, computing inter-annotator agreement metrics."""
    records_a = {r["query_id"]: r for r in sub_a}
    records_b = {r["query_id"]: r for r in sub_b}
    
    common_qids = sorted(list(set(records_a.keys()).intersection(set(records_b.keys()))))
    
    exact_matches = []
    partial_overlaps = []
    conflicts = []
    
    no_match_a = []
    no_match_b = []
    jaccards = []
    
    for qid in common_qids:
        rec_a = records_a[qid]
        rec_b = records_b[qid]
        
        nm_a = bool(rec_a.get("expected_no_match", False))
        nm_b = bool(rec_b.get("expected_no_match", False))
        no_match_a.append(nm_a)
        no_match_b.append(nm_b)
        
        prov_a = set(rec_a.get("relevant_provision_ids", []))
        prov_b = set(rec_b.get("relevant_provision_ids", []))
        
        jacc = compute_pairwise_jaccard(prov_a, prov_b)
        jaccards.append(jacc)
        
        if nm_a != nm_b:
            conflicts.append({
                "query_id": qid,
                "type": "NO_MATCH_CONFLICT",
                "reviewer_a": nm_a,
                "reviewer_b": nm_b
            })
        elif prov_a == prov_b:
            exact_matches.append(qid)
        elif len(prov_a.intersection(prov_b)) > 0:
            partial_overlaps.append({
                "query_id": qid,
                "reviewer_a": list(prov_a),
                "reviewer_b": list(prov_b),
                "intersection": list(prov_a.intersection(prov_b))
            })
        else:
            conflicts.append({
                "query_id": qid,
                "type": "DISJOINT_PROVISIONS",
                "reviewer_a": list(prov_a),
                "reviewer_b": list(prov_b)
            })
            
    n_common = len(common_qids)
    kappa = compute_cohens_kappa(no_match_a, no_match_b) if n_common > 0 else 0.0
    mean_jaccard = sum(jaccards) / n_common if n_common > 0 else 0.0
    exact_ratio = len(exact_matches) / n_common if n_common > 0 else 0.0
    
    return {
        "total_evaluated": n_common,
        "exact_matches_count": len(exact_matches),
        "exact_match_ratio": exact_ratio,
        "partial_overlaps_count": len(partial_overlaps),
        "conflicts_count": len(conflicts),
        "mean_pairwise_jaccard": mean_jaccard,
        "cohens_kappa_no_match": kappa,
        "exact_match_qids": exact_matches,
        "partial_overlaps": partial_overlaps,
        "conflicts": conflicts
    }


def audit_workflow_manifest() -> Dict[str, Any]:
    """Audit the active pending manifest against disk datasets."""
    valid_ids = load_valid_corpus_ids()
    
    with open(EVAL_DATASET_PATH, "r", encoding="utf-8") as f:
        eval_data = json.load(f)
    with open(BLIND_DATASET_PATH, "r", encoding="utf-8") as f:
        blind_data = json.load(f)
        
    eval_pending = [r for r in eval_data if r.get("annotation_status") == "pending"]
    eval_reviewed = [r for r in eval_data if r.get("annotation_status") == "reviewed"]
    blind_pending = [r for r in blind_data if r.get("annotation_status") == "pending"]
    blind_reviewed = [r for r in blind_data if r.get("annotation_status") == "reviewed"]
    
    return {
        "corpus_provisions_count": len(valid_ids),
        "eval_dataset_total": len(eval_data),
        "eval_dataset_pending": len(eval_pending),
        "eval_dataset_reviewed": len(eval_reviewed),
        "eval_quarantined_qids": [r["query_id"] for r in eval_pending],
        "blind_benchmark_total": len(blind_data),
        "blind_benchmark_pending": len(blind_pending),
        "blind_benchmark_reviewed": len(blind_reviewed),
        "blind_all_pending_verified": len(blind_pending) == len(blind_data),
        "total_portfolio_pending": len(eval_pending) + len(blind_pending)
    }


def main():
    parser = argparse.ArgumentParser(description="LexiLaw Annotation Submission Validator")
    parser.add_argument("--audit-manifest", action="store_true", help="Audit the current manifest and pending portfolio")
    parser.add_argument("--validate-file", type=str, help="Validate a reviewer submission JSON file")
    parser.add_argument("--compare", nargs=2, metavar=("REV_A", "REV_B"), help="Compare two submission JSON files")
    
    args = parser.parse_args()
    
    if args.audit_manifest or len(sys.argv) == 1:
        print("\n=== LEXILAW ANNOTATION WORKFLOW PORTFOLIO AUDIT ===")
        res = audit_workflow_manifest()
        for k, v in res.items():
            print(f"  {k}: {v}")
        print("===================================================\n")
        return

    if args.validate_file:
        valid_ids = load_valid_corpus_ids()
        with open(args.validate_file, "r", encoding="utf-8") as f:
            records = json.load(f)
        all_errors = []
        for r in records:
            all_errors.extend(validate_single_record(r, valid_ids))
        if all_errors:
            print(f"Validation FAILED with {len(all_errors)} errors:")
            for err in all_errors:
                print(f"  - {err}")
            sys.exit(1)
        else:
            print(f"Validation PASSED: All {len(records)} records conform to schema and 37 corpus entries.")

    if args.compare:
        valid_ids = load_valid_corpus_ids()
        with open(args.compare[0], "r", encoding="utf-8") as f:
            sub_a = json.load(f)
        with open(args.compare[1], "r", encoding="utf-8") as f:
            sub_b = json.load(f)
        report = compare_reviewer_submissions(sub_a, sub_b, valid_ids)
        print("\n=== INTER-ANNOTATOR AGREEMENT REPORT ===")
        print(f"Total Evaluated Records: {report['total_evaluated']}")
        print(f"Exact Matches: {report['exact_matches_count']} ({report['exact_match_ratio'] * 100:.1f}%)")
        print(f"Partial Overlaps: {report['partial_overlaps_count']}")
        print(f"Direct Conflicts: {report['conflicts_count']}")
        print(f"Mean Pairwise Jaccard: {report['mean_pairwise_jaccard']:.4f}")
        print(f"Cohen's Kappa (No-Match): {report['cohens_kappa_no_match']:.4f}")
        print("=========================================\n")


if __name__ == "__main__":
    main()
