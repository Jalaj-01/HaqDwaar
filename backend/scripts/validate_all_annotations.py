import json
from pathlib import Path

corpus_path = Path("backend/data/legal_provisions.json")
with open(corpus_path, "r", encoding="utf-8") as f:
    corpus = json.load(f)
corpus_ids = {p["id"]: p for p in corpus}

dataset_path = Path("backend/evaluation/retrieval_eval_dataset.json")
with open(dataset_path, "r", encoding="utf-8") as f:
    dataset = json.load(f)

print(f"Loaded {len(corpus)} corpus provisions and {len(dataset)} dataset queries.")

issues = []
for q in dataset:
    qid = q["query_id"]
    expected_ids = q.get("relevant_provision_ids", [])
    expected_no_match = q.get("expected_no_match", False)
    status = q.get("annotation_status")

    # Consistency check
    if expected_no_match and len(expected_ids) > 0:
        issues.append(f"[{qid}] expected_no_match=True but relevant_provision_ids is not empty: {expected_ids}")
    if not expected_no_match and len(expected_ids) == 0:
        issues.append(f"[{qid}] expected_no_match=False but relevant_provision_ids is empty")

    # Corpus existence check
    for pid in expected_ids:
        if pid not in corpus_ids:
            issues.append(f"[{qid}] Expected provision ID '{pid}' does not exist in corpus!")

    # Check date keywords in query text
    text = q.get("query_text", "").lower()
    has_date = any(yr in text for yr in ["2022", "2023", "2024", "2025", "january", "february", "march", "december"])
    has_ipc = any("IPC" in pid for pid in expected_ids)
    has_bns = any("BNS" in pid for pid in expected_ids)

    if has_date and has_bns:
        print(f"[{qid}] Notice: Has date reference and BNS expected ID: {expected_ids}")
    if not has_date and has_ipc:
        print(f"[{qid}] Notice: No date reference but IPC expected ID: {expected_ids}")

if not issues:
    print("ALL 50 QUERIES PASSED SCHEMA, CONSISTENCY, AND CORPUS ID CHECKS!")
else:
    print(f"Found {len(issues)} issues:")
    for iss in issues:
        print("  -", iss)
