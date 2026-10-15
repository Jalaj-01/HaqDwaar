import sys
import json
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from config import LEGAL_PROVISIONS_PATH
from nlp.retrieval import get_corpus_index
from evaluation.eval_retrieval import evaluate_retrieval_pipeline

dataset_path = backend_dir / "evaluation" / "retrieval_eval_dataset.json"
with open(dataset_path, "r", encoding="utf-8") as f:
    dataset = json.load(f)

index = get_corpus_index(LEGAL_PROVISIONS_PATH)

thresholds = [0.03, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.12, 0.15, 0.18, 0.20]

print("=" * 95)
print("DEVELOPMENT SPLIT THRESHOLD SWEEP (HYBRID RETRIEVAL)")
print("20 Positive Incident Queries, 5 Out-of-Scope Queries (Total: 25 Reviewed)")
print("=" * 95)
print(f"{'Threshold':<10} | {'MRR':<8} | {'P@3':<8} | {'P@5':<8} | {'R@5':<8} | {'R@10':<8} | {'TN':<4} | {'FP':<4} | {'No-Match Acc':<12} | {'FPR':<8}")
print("-" * 95)

hybrid_results = {}
for t in thresholds:
    res = evaluate_retrieval_pipeline(
        dataset,
        index,
        split_filter="dev",
        include_pending=False,
        min_score_cutoff=t,
    )
    h_pos = res["modes"]["hybrid"]["positive_retrieval_metrics"]
    h_nm = res["modes"]["hybrid"]["no_match_detection_metrics"]
    hybrid_results[t] = {"pos": h_pos, "nm": h_nm}
    print(f"{t:<10.2f} | {h_pos['MRR']:<8.4f} | {h_pos['Precision@3']:<8.4f} | {h_pos['Precision@5']:<8.4f} | {h_pos['Recall@5']:<8.4f} | {h_pos['Recall@10']:<8.4f} | {h_nm['true_negatives']:<4} | {h_nm['false_positives']:<4} | {h_nm['no_match_accuracy']:<12.4f} | {h_nm['false_positive_rate']:<8.4f}")

print("\n" + "=" * 95)
print("DEVELOPMENT SPLIT THRESHOLD SWEEP (TF-IDF RETRIEVAL)")
print("=" * 95)
print(f"{'Threshold':<10} | {'MRR':<8} | {'P@3':<8} | {'P@5':<8} | {'R@5':<8} | {'R@10':<8} | {'TN':<4} | {'FP':<4} | {'No-Match Acc':<12} | {'FPR':<8}")
print("-" * 95)

tfidf_results = {}
for t in thresholds:
    res = evaluate_retrieval_pipeline(
        dataset,
        index,
        split_filter="dev",
        include_pending=False,
        min_score_cutoff=t,
    )
    t_pos = res["modes"]["tfidf_only"]["positive_retrieval_metrics"]
    t_nm = res["modes"]["tfidf_only"]["no_match_detection_metrics"]
    tfidf_results[t] = {"pos": t_pos, "nm": t_nm}
    print(f"{t:<10.2f} | {t_pos['MRR']:<8.4f} | {t_pos['Precision@3']:<8.4f} | {t_pos['Precision@5']:<8.4f} | {t_pos['Recall@5']:<8.4f} | {t_pos['Recall@10']:<8.4f} | {t_nm['true_negatives']:<4} | {t_nm['false_positives']:<4} | {t_nm['no_match_accuracy']:<12.4f} | {t_nm['false_positive_rate']:<8.4f}")

# Save sweep results for analysis
sweep_output = {
    "split": "dev",
    "thresholds": thresholds,
    "hybrid": hybrid_results,
    "tfidf": tfidf_results,
}
with open("backend/evaluation/threshold_sweep_results.json", "w", encoding="utf-8") as f:
    json.dump(sweep_output, f, indent=2)
print("\nSaved sweep results to backend/evaluation/threshold_sweep_results.json")
