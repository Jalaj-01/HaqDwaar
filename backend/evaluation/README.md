# LexiLaw Retrieval Evaluation Framework & Benchmark

This directory contains the reproducible benchmark harness, dataset schema, and empirical measurement tools for statutory provision retrieval under the LexiLaw Indian legal information backend.

---

## 1. Overview & Core Purpose

The retrieval evaluation framework evaluates how effectively LexiLaw retrieves relevant statutory provisions given unseen, natural-language incident descriptions.

It measures:
1. **Positive Retrieval Accuracy**: When an incident falls within indexed penal or cyber law, does the system rank the applicable provisions at the top?
2. **Out-of-Scope / No-Match Handling**: When an incident falls outside the indexed criminal/cyber statutes (e.g. general civil disputes, tenancy defaults, traffic fines, tax assessments), does the system avoid false-positive statutory matches?
3. **Lexical vs. Dense Semantic Generalization**: Compares the hybrid retrieval engine (`TF-IDF + all-MiniLM-L6-v2`) against the lexical-only baseline (`TF-IDF only`).

---

## 2. Dataset Schema & Guidelines (`retrieval_eval_dataset.json`)

Each query record in the benchmark dataset adheres to the following specification:

```json
{
  "query_id": "DEV_001",
  "query_text": "Someone intercepted my net banking OTP and used my electronic signature without permission to transfer funds.",
  "relevant_provision_ids": ["ITA_2000_S66C"],
  "expected_no_match": false,
  "rationale": "Fraudulent use of electronic signature and authentication credentials constitutes identity theft under Section 66C IT Act.",
  "annotation_status": "reviewed",
  "reviewer_notes": "Clear digital credential misuse without consent.",
  "split": "dev",
  "category": "cyber_identity_theft"
}
```

### Field Definitions
- **`query_id`** *(string, required)*: Unique identifier, partitioned strictly by split (`DEV_001`... or `TEST_001`...).
- **`query_text`** *(string, required)*: Natural-language incident description reflecting realistic complainant phrasing.
- **`relevant_provision_ids`** *(list of strings)*: Expected candidate statutory provisions from the verified production corpus (`legal_provisions.json`).
- **`expected_no_match`** *(boolean)*: `true` if the incident falls outside the statutory scope of the indexed corpus. Must have an empty `relevant_provision_ids` list.
- **`rationale`** *(string)*: Grounded explanation detailing why the cited statutory provisions apply based on legal elements.
- **`annotation_status`** *(string, "reviewed" | "pending")*: Quality gate. Queries marked `"pending"` are **strictly excluded** from scored benchmark metrics.
- **`reviewer_notes`** *(string)*: Reviewer observations, edge case caveats, or questions for legal domain experts.
- **`split`** *(string, "dev" | "test")*: Partition defining development vs. exploratory test data.
- **`category`** *(string)*: Incident classification category for error analysis.

---

## 3. Dataset Split Policy & Data Leakage Prevention

1. **Disjoint Identifiers & Text**: Dev and Test splits have disjoint `query_id` namespaces and zero identical or near-duplicate `query_text` entries.
2. **Test Split Usage & Historical Inspection Disclosure**: Although the test split was originally partitioned for evaluation, documented earlier development scripts (`scripts/inspect_scores.py` and `scripts/evaluate_test_thresholds.py`) historically evaluated candidate thresholds and inspected test-query scores. Therefore, while the latest threshold selection ($\tau = 0.12$) uses and is defended strictly by the development split, the current test split functions as an **exploratory (secondary development) split** rather than an untouched, pristine held-out test set. A new, independently annotated, locked held-out test set is required for final out-of-sample evaluation.
3. **Automated Leakage Validation**: Running the validator automatically checks for overlap, duplicates, and split integrity:
   ```bash
   python backend/evaluation/eval_retrieval.py --validate
   ```
4. **No Synthetic Provisions**: Benchmark queries are evaluated solely against verified records in `backend/data/legal_provisions.json`. Synthetic test fixtures are strictly forbidden in production benchmark datasets.

---

## 4. Metric Definitions

### Positive Retrieval Metrics (For Queries with Relevant Provisions)
- **Precision@K ($K \in \{3, 5\}$)**: The proportion of retrieved candidates in the top-$K$ cutoff that are genuinely relevant.
  $$\text{Precision@K} = \frac{|\text{Retrieved}_K \cap \text{Relevant}|}{K}$$
  *Handling fewer than $K$ candidates:* Denominator remains $K$.
- **Recall@K ($K \in \{5, 10\}$)**: The proportion of total relevant provisions captured within the top-$K$ retrieved candidates.
  $$\text{Recall@K} = \frac{|\text{Retrieved}_K \cap \text{Relevant}|}{|\text{Relevant}|}$$
- **Mean Reciprocal Rank (MRR)**: Evaluates ranking quality based on the rank of the first relevant provision retrieved:
  $$\text{MRR} = \frac{1}{|Q|} \sum_{i=1}^{|Q|} \frac{1}{\text{rank}_i}$$
  where $\frac{1}{\text{rank}_i} = 0$ if no relevant provision is retrieved.

### Out-of-Scope No-Match Metrics
Queries where `expected_no_match: true` have an empty ground-truth set ($|\text{Relevant}| = 0$). Calculating recall would produce division by zero. They are evaluated separately:
- **True Negative (TN)**: Retrieval correctly yields zero candidates meeting the minimum relevance threshold (`min_score`).
- **False Positive (FP)**: System incorrectly retrieves candidate provisions for an out-of-scope query.
- **No-Match Detection Accuracy**: $\frac{\text{TN}}{\text{TN} + \text{FP}}$
- **False Positive Rate**: $\frac{\text{FP}}{\text{TN} + \text{FP}}$

---

## 5. How to Run the Benchmark

### 1. Validate Dataset Integrity
```powershell
python backend/evaluation/eval_retrieval.py --validate
```

### 2. Run Benchmark on Development Set with Calibrated Threshold
```powershell
# Development baseline (default threshold 0.05)
python backend/evaluation/eval_retrieval.py --split dev

# Development calibrated (threshold 0.12 selected via sweep)
python backend/evaluation/eval_retrieval.py --split dev --min-score 0.12
```

### 3. Run Benchmark on Exploratory Test Set (Frozen Cutoff)
```powershell
# Exploratory test evaluation at frozen calibrated threshold (0.12)
python backend/evaluation/eval_retrieval.py --split test --min-score 0.12
```

### 4. Custom Output Path & Pending Inclusion
```powershell
python backend/evaluation/eval_retrieval.py --split dev --min-score 0.12 --output backend/evaluation/custom_report.json --include-pending
```

### 5. Automated Evaluator Test Suite
```powershell
pytest backend/tests/test_evaluation.py -v
```

---

## 6. Threshold Calibration & Interpreting Results

1. **Threshold Sweep on Development Set**:
   - The default retrieval cutoff is `min_score = 0.05`. Sweeping candidate thresholds ($\tau \in [0.03, 0.20]$) strictly on the **development set** (25 reviewed queries: 20 positive, 5 out-of-scope) demonstrates that elevating the cutoff to `0.12` maintains 100% of baseline positive incident recall (Recall@5 = 0.9500, MRR = 0.9000) while tripling out-of-scope no-match accuracy from 20% to 60%.
   - Operating at the frozen threshold of `0.12` on the exploratory test split yields 100% positive recall (Recall@5 = 1.0000, MRR = 0.8611) and 100% out-of-scope rejection (3/3 true negatives, 0.0% false-positive rate).
2. **Dense vs. Sparse Tradeoffs**:
   - Dense embeddings enhance semantic recall on paraphrased complaints (e.g. "intercepted net banking OTP" -> `ITA_2000_S66C`).
   - Sparse TF-IDF provides high resistance against false positives on out-of-scope complaints with zero legal vocabulary overlap, but suffers lower positive recall on layperson terminology.
3. **Caveats, Chronology Disclosure & Production Requirements**:
   - **Evaluation History & Exploratory Test Split:** Earlier development scripts inspected test-query scores across candidate cutoffs. Consequently, the current test split cannot be characterized as an uninspected blind benchmark; it functions as an **exploratory (secondary development) split**. Threshold $\tau = 0.12$ is defended strictly by development-split measurements.
   - **Requirement for Locked Held-Out Test Set:** Prior to any production deployment, a new, independently annotated, locked held-out test set of 25–50 fresh incident queries must be curated to measure true out-of-sample generalization without prior exposure.
   - **Statutory Corpus Census:** The production corpus indexes 20 verified central criminal and cyber provisions and 1 uncommenced provisional audit fixture (`DPDP_2023_S33_PROVISIONAL`, where Gazette Notification G.S.R. 843(E) dated 13 November 2025 already specifies the phased commencement schedule appointing 18 months from publication—13 May 2027—as the scheduled commencement date for Sections 28–34, subject to any subsequent legal change; no new commencement notification is required on that date; `source_verified=False`, statutory penalties suppressed).

---

## 7. Audit of Pending Annotations & Human Review Checklist

The production dataset (`backend/evaluation/retrieval_eval_dataset.json`) contains **10 draft queries** marked as `"annotation_status": "pending"`. In accordance with project policy, these queries are quarantined and strictly excluded from benchmark score calculations. They must not be converted to `"reviewed"` without formal legal adjudication.

### Summary Audit Table

| Query ID | Split | Incident Query Text | Expected Provision(s) | Expected No-Match | Legal Evidence & Statutory Basis | Unresolved Legal Ambiguity |
|---|---|---|---|---|---|---|
| `DEV_026` | `dev` | "Someone logged into my work email account using stolen credentials and sent offensive emails to our leadership team." | `ITA_2000_S66C`, `ITA_2000_S66` | `false` | Misuse of authentication credentials constitutes identity theft under S.66C IT Act; sending offensive emails after unauthorized access invokes S.66. | Does S.66 act as an umbrella or is S.66C the sole primary label? Multi-label expectations affect ranking metrics. |
| `DEV_027` | `dev` | "A vendor manufactured counterfeit branded handbags mimicking our registered trademark logo." | None | `true` | Trademark infringement under Trade Marks Act, 1999 is outside indexed penal and cyber provisions. | Commercial trademark counterfeiting: does cheating (S.318 BNS) apply if purchasers are deceived, or is this strictly an IP civil/special law matter? |
| `DEV_028` | `dev` | "The blackmailer told me he would post private photographs of my family unless I withdrew my police complaint." | `BNS_2023_S351` | `false` | Threat to reputation to compel omission of a legal right (withdrawing complaint) constitutes criminal intimidation under S.351 BNS. | Check if extortion (S.308 BNS) is triggered in the absence of a demand for "property" or "valuable security". |
| `DEV_029` | `dev` | "A person recorded a conversation in a restaurant without informing the other attendees." | None | `true` | Public restaurant conversation lacks bodily privacy expectation (S.66E IT Act inapplicable); conversation recording per se is not an indexed penal offense. | Pending review of Indian evidence law on admissibility of non-consensual recordings vs substantive statutory offense. |
| `DEV_030` | `dev` | "Someone placed a GPS magnetic tracker under my vehicle and monitored everywhere I drove for two weeks." | `BNS_2023_S78` | `false` | Electronic tracking of movements constitutes stalking under S.78 BNS if the targeted individual is a woman. | S.78 BNS requires a female victim and male perpetrator. Factual query lacks gender specification; element matching requires clarification. |
| `TEST_016` | `test` | "An unauthorized party guessed my Wi-Fi router password and used my home broadband connection for three days." | `ITA_2000_S43` | `false` | Unauthorized access to computer network without permission under S.43 IT Act. | Does unauthorized broadband usage satisfy S.66 penal mens rea (dishonest/fraudulent intent causing wrongful loss) without demonstrable damage? |
| `TEST_017` | `test` | "In December 2023, an accountant embezzled funds by submitting forged invoices to the finance department." | `IPC_1860_S420` | `false` | Pre-1 July 2024 cheating and dishonestly inducing delivery of property governed by S.420 IPC under Art. 20(1) Constitution of India. | Primary criminality involves forged invoices (S.465/468/471 IPC), which are outside the indexed corpus. Does evaluating solely against S.420 distort retrieval evaluation? |
| `TEST_018` | `test` | "Someone took pictures of our company storefront from a public street sidewalk during business hours." | None | `true` | Commercial storefront visible from a public street carries no reasonable expectation of bodily or spatial privacy. | Confirmation needed that zero municipal, commercial, or penal offenses apply. |
| `TEST_019` | `test` | "A user created a parody account on social media clearly labeled as satire of a celebrity." | None | `true` | Explicit parody/satire lacking deceptive fraudulent inducement is not criminal personation (S.66D IT Act / S.319 BNS). | Review potential defamation (S.356 BNS / S.500 IPC) or trademark misuse claims if the satire causes reputational harm. |
| `TEST_020` | `test` | "A man sent fifty unsolicited romantic poems to a coworker's official email despite her repeated requests to stop." | `BNS_2023_S78` | `false` | Repeated unwanted electronic communication attempting to foster personal interaction despite clear disinterest constitutes stalking under S.78 BNS. | Workplace context: evaluate interaction between criminal stalking (S.78 BNS) and civil administrative remedies under the POSH Act, 2013. |

### Human Review Checklist & Sign-Off Requirements
Before promoting any of the 10 pending records to `"reviewed"`, the legal review team must execute the following protocol:
1. **Element Verification**: Verify that every factual assertion in the query satisfies each statutory element of the expected provision.
2. **Ambiguity Resolution**: Document a binding ruling on the unresolved legal questions in `reviewer_notes` and update `rationale`.
3. **Multi-Label Ground Truth Policy**: Confirm whether secondary provisions are co-primary or optional, avoiding artificial ranking penalties.
4. **Adjudicator Attribution**: Record `reviewer_id` and `adjudicator_id` in the dataset schema.
5. **Re-run Validation**: Execute `python backend/evaluation/eval_retrieval.py --validate --check-provenance` to confirm schema integrity.

---

## 8. Blind Benchmark Specification, Sampling Protocol & Locking Procedure

To evaluate genuine out-of-sample generalization without prior parameter exposure or historical test inspection, LexiLaw establishes an **Independent Blind Benchmark** framework.

### 1. Specification & Target Distribution
- **Target Size:** 25–50 fresh natural-language incident queries (standard: 50 queries).
- **Target Composition:**
  - **70% Positive Retrieval Incidents (35 queries):** Spanning IT Act 2000 (cyber offenses), Bharatiya Nyaya Sanhita 2023 (post-1 July 2024 offenses), and Indian Penal Code 1860 (pre-1 July 2024 historical offenses).
  - **30% Legitimate Out-of-Scope No-Match Cases (15 queries):** Spanning civil contract breaches, landlord-tenant disputes, consumer forum complaints, trademark/IP infringement, traffic infractions, and lawful daily activities.
- **Independence & Overlap Barrier:** Pairwise token Jaccard similarity must be strictly **< 0.50** against all existing development and exploratory test queries. Exact duplicate text is strictly forbidden.

### 2. Dual Annotation & Inter-Annotator Agreement Protocol
1. **Independent Dual Tagging:** Two qualified legal annotators independently assign candidate provision IDs and `expected_no_match` flags to raw incident descriptions without communicating.
2. **Agreement Threshold:** Inter-annotator agreement on binary provision relevance must achieve **Cohen's Kappa $\ge 0.80$**.
3. **Senior Legal Adjudication:** Any disagreement on provisions, out-of-scope boundaries, or statutory temporal application must be escalated to a senior legal adjudicator whose binding rationale is recorded in `adjudicator_id` and `rationale`.
4. **Provenance Metadata:** Every record must track `annotator_id`, `reviewer_id`, `adjudicator_id`, `provenance_source`, and `unresolved_ambiguity`.

### 3. Strict Isolation Protocol (Contamination Prevention)
- **Zero Threshold Exposure:** The blind benchmark must **never** be used in threshold calibration sweeps (`eval_retrieval.py --sweep` or `scripts/run_threshold_sweep.py`). Automated code guardrails enforce a hard `ValueError` if non-development queries are supplied to sweep harnesses.
- **Zero Ranking Tuning:** The blind set must never be inspected for dense embedding fine-tuning, vocabulary curation, or lexical weighting.
- **Score Blindness:** Retrieval candidate scores must not be inspected or analyzed prior to the official release evaluation run.

### 4. Cryptographic Benchmark Locking Procedure
Once the blind benchmark passes schema validation, independence checks, and provenance verification:
1. **Lock Registration:** Register the benchmark in `backend/evaluation/benchmark_manifest.json` using the automated harness:
   ```powershell
   python backend/evaluation/eval_retrieval.py --lock backend/evaluation/blind_benchmark.json
   ```
2. **Integrity Digest:** The lock manifest computes and records the canonical raw byte SHA-256 digest, file size, timestamp, and locking notes.
3. **Automated Tamper Verification:** Subsequent runs verify the locked file against the manifest:
   ```powershell
   python backend/evaluation/eval_retrieval.py --verify-lock backend/evaluation/blind_benchmark.json
   ```
4. **Overwrite Protection:** Evaluator harnesses invoke `assert_not_locked()` prior to writing output reports, preventing accidental corruption or modification of locked benchmarks.


