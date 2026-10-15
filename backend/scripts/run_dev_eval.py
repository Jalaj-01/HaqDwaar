import sys
from pathlib import Path

# Add backend to sys.path
backend_path = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_path))

from nlp.retrieval import get_corpus_index
from evaluation.eval_retrieval import evaluate_retrieval_pipeline, DEFAULT_DATASET_PATH
import json

def run_dev_eval():
    with open(DEFAULT_DATASET_PATH, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    index = get_corpus_index()

    # Run on dev split only, threshold 0.12 (operating threshold)
    print("--- Evaluating DEV split (reviewed only, threshold=0.12) ---")
    report = evaluate_retrieval_pipeline(
        dataset_queries=dataset,
        index=index,
        split_filter="dev",
        include_pending=False,
        min_score_cutoff=0.12,
    )

    hybrid = report["modes"]["hybrid"]
    tfidf = report["modes"]["tfidf_only"]

    print("HYBRID MODE (0.40 TF-IDF + 0.60 dense MiniLM):")
    print(json.dumps(hybrid, indent=2))

    print("\nTFIDF ONLY MODE:")
    print(json.dumps(tfidf, indent=2))

    # Also evaluate dev with pending included (all 30 dev records)
    print("\n--- Evaluating DEV split (including pending, all 30 records, threshold=0.12) ---")
    report_all = evaluate_retrieval_pipeline(
        dataset_queries=dataset,
        index=index,
        split_filter="dev",
        include_pending=True,
        min_score_cutoff=0.12,
    )
    print("HYBRID MODE (30 dev records):")
    print(json.dumps(report_all["modes"]["hybrid"], indent=2))

if __name__ == "__main__":
    run_dev_eval()
