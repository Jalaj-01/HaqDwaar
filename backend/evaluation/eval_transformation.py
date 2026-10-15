"""Evaluation script for bidirectional transformation fact-preservation benchmarks."""

import sys
from pathlib import Path
from typing import Dict, List

backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from nlp.transformation import (
    run_preservation_checks,
    transform_legal_to_normal,
    transform_normal_to_legal,
)

# Standard benchmark evaluation pairs
BENCHMARK_SAMPLES = [
    {
        "id": "BENCH_L2N_01",
        "direction": "legal_to_normal",
        "input_text": (
            "Notwithstanding clause 4, the lessee shall remit Rs. 15,000 on or before "
            "1st December 2026, unless prior written notice is served."
        ),
    },
    {
        "id": "BENCH_L2N_02",
        "direction": "legal_to_normal",
        "input_text": (
            "The aforementioned contractor is liable for damages and shall not subcontract "
            "the assignment without permission."
        ),
    },
    {
        "id": "BENCH_N2L_01",
        "direction": "normal_to_legal",
        "input_text": (
            "Someone created an unauthorized Instagram profile using my photos on 15th October 2026 "
            "and demanded Rs. 30,000 without my consent."
        ),
    },
    {
        "id": "BENCH_N2L_02",
        "direction": "normal_to_legal",
        "input_text": (
            "My business partner withdrew funds from our joint account without authority "
            "and refused to return Rs. 2,00,000."
        ),
    },
]


def run_transformation_evaluation() -> Dict[str, float]:
    """Run transformation preservation benchmark and output summary metrics."""
    print("=======================================================")
    print("LexiLaw Language Transformation Benchmark Evaluation")
    print("=======================================================")

    total = len(BENCHMARK_SAMPLES)
    dates_preserved_count = 0
    amounts_preserved_count = 0
    negation_preserved_count = 0
    qualifiers_preserved_count = 0
    passed_checks_count = 0
    unsupported_additions_count = 0

    for sample in BENCHMARK_SAMPLES:
        direction = sample["direction"]
        in_text = sample["input_text"]

        if direction == "legal_to_normal":
            out_text, _, _ = transform_legal_to_normal(in_text)
        else:
            out_text, _, _ = transform_normal_to_legal(in_text)

        report = run_preservation_checks(in_text, out_text)

        if report.dates_preserved:
            dates_preserved_count += 1
        if report.amounts_preserved:
            amounts_preserved_count += 1
        if report.negation_preserved:
            negation_preserved_count += 1
        if report.qualifiers_preserved:
            qualifiers_preserved_count += 1
        if report.overall_status in ("passed_basic_checks", "warnings"):
            passed_checks_count += 1
        if len(report.unsupported_additions_detected) > 0:
            unsupported_additions_count += 1

        print(f"[{sample['id']}] Direction: {direction:15s} | Status: {report.overall_status:20s}")

    metrics = {
        "Total Evaluated Samples": total,
        "Date Preservation Rate": round(dates_preserved_count / total, 4),
        "Monetary Sum Preservation Rate": round(amounts_preserved_count / total, 4),
        "Negation Preservation Rate": round(negation_preserved_count / total, 4),
        "Legal Qualifier Preservation Rate": round(qualifiers_preserved_count / total, 4),
        "Overall Acceptance Rate": round(passed_checks_count / total, 4),
        "Unsupported Addition Rate": round(unsupported_additions_count / total, 4),
    }

    print("\n---------------- Aggregate Summary ----------------")
    for k, v in metrics.items():
        if isinstance(v, float):
            print(f"  {k:35s}: {v * 100:.2f}%")
        else:
            print(f"  {k:35s}: {v}")
    print("===================================================\n")

    return metrics


if __name__ == "__main__":
    run_transformation_evaluation()
