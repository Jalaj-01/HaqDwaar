# LexiLaw — Independent Human Legal Review & Adjudication Instructions

**Document Version:** 1.0.0  
**Effective Date:** October 18, 2026  
**Auditor / Engineering Role:** NLP Evaluation Lead & Senior Legal QA Auditor  
**Workspace Root:** `G:\NLP\New`  
**Target Review Portfolio:** 45 Total Records (10 Quarantined Dev/Test Records + 35 Held-Out Blind Scenarios)  
**Corpus Reference:** 37 active provisions (`backend/data/legal_provisions.json`, SHA-256: `becf1f001631bbdc301633df428b0cb541dca97fa45b1ad7cf05db8b1d0d00d0`)  
**Operating Cutoff:** $\tau = 0.12$ (Frozen retrieval baseline)  
**Document Status:** **ACTIVE OPERATIONAL INSTRUCTION MANUAL**  

---

## 1. Overview & Reviewer Role Assignments

The LexiLaw evaluation benchmark requires authentic, independent human legal review to establish ground-truth labels. The review workflow operates under a strict **air-gapped double-blind protocol** with senior legal adjudication.

```
+---------------------------------------------------------------------------------------------------+
|                                LEXILAW DOUBLE-BLIND REVIEW FLOW                                   |
+---------------------------------------------------------------------------------------------------+
|                                                                                                   |
|   [ Reviewer A (Independent) ]                   [ Reviewer B (Independent) ]                     |
|     - REVIEWER_A_SUBMISSION_TEMPLATE.md            - REVIEWER_B_SUBMISSION_TEMPLATE.md            |
|     - BLIND_REVIEWER_A_TEMPLATE.md                 - BLIND_REVIEWER_B_TEMPLATE.md                 |
|            |                                              |                                       |
|            v                                              v                                       |
|   submissions/reviewer_a/                        submissions/reviewer_b/                          |
|   (Sealed & Git SHA-256 Hashed)                  (Sealed & Git SHA-256 Hashed)                    |
|            |                                              |                                       |
|            +----------------------+-----------------------+                                       |
|                                   | (Cryptographically committed)                                |
|                                   v                                                               |
|                    [ Senior Legal Adjudicator ]                                                   |
|                      - Unseals both submissions                                                   |
|                      - Runs validate_reviewer_submissions.py --compare                            |
|                      - Reconciles disagreements with statutory reasoning                          |
|                      - Completes ADJUDICATION_TEMPLATE.md & BLIND_ADJUDICATION_TEMPLATE.md        |
|                                   |                                                               |
|                                   v                                                               |
|               [ Automated Dataset Ingestion & Lock ]                                              |
|                 - Updates annotation_status to "reviewed"                                         |
|                 - Benchmarks Lead freezes manifest (locked: true)                                 |
+---------------------------------------------------------------------------------------------------+
```

### 1.1 Reviewer Role Definitions & Assigned Forms

| Role | Profile & Qualifications | Assigned Review Templates | Target Records |
| :--- | :--- | :--- | :--- |
| **Reviewer A** | Bar-qualified legal advocate, judicial clerk, or criminal law academic. Must have zero involvement in LexiLaw model tuning. | 1. [`REVIEWER_A_SUBMISSION_TEMPLATE.md`](file:///g:/NLP/New/backend/evaluation/annotation_workflow/REVIEWER_A_SUBMISSION_TEMPLATE.md)<br>2. [`BLIND_REVIEWER_A_TEMPLATE.md`](file:///g:/NLP/New/backend/evaluation/annotation_workflow/BLIND_REVIEWER_A_TEMPLATE.md) | `DEV_026`–`DEV_030`<br>`TEST_016`–`TEST_020`<br>`BLIND_001`–`BLIND_035` |
| **Reviewer B** | Independent legal advocate or academic. Must work in complete isolation from Reviewer A. | 1. [`REVIEWER_B_SUBMISSION_TEMPLATE.md`](file:///g:/NLP/New/backend/evaluation/annotation_workflow/REVIEWER_B_SUBMISSION_TEMPLATE.md)<br>2. [`BLIND_REVIEWER_B_TEMPLATE.md`](file:///g:/NLP/New/backend/evaluation/annotation_workflow/BLIND_REVIEWER_B_TEMPLATE.md) | `DEV_026`–`DEV_030`<br>`TEST_016`–`TEST_020`<br>`BLIND_001`–`BLIND_035` |
| **Senior Legal Adjudicator** | Senior criminal counsel or retired judicial officer. Reconciles inter-annotator disagreements and authors binding rationale. | 1. [`ADJUDICATION_TEMPLATE.md`](file:///g:/NLP/New/backend/evaluation/annotation_workflow/ADJUDICATION_TEMPLATE.md)<br>2. [`BLIND_ADJUDICATION_TEMPLATE.md`](file:///g:/NLP/New/backend/evaluation/annotation_workflow/BLIND_ADJUDICATION_TEMPLATE.md) | All 45 records with focus on non-unanimous cases |

---

## 2. Permitted Source Documents & Legal Reference Rules

Reviewers must substantiate all legal determinations using official government statutory sources. The following sources may be consulted:

### 2.1 Permitted Sources on Disk
1. **The Bharatiya Nyaya Sanhita, 2023 (BNS)**:
   - Primary PDF: [`backend/data/legal_sources/BNS_2023_Gazette.pdf`](file:///g:/NLP/New/backend/data/legal_sources/BNS_2023_Gazette.pdf) (Act No. 45 of 2023, published in *The Gazette of India, Extraordinary, Part II, Section 1, No. 62*, 25 Dec 2023).
   - Searchable Text: [`backend/data/legal_sources/extracted_text/BNS_2023_Gazette.txt`](file:///g:/NLP/New/backend/data/legal_sources/extracted_text/BNS_2023_Gazette.txt).
2. **The Bharatiya Nagarik Suraksha Sanhita, 2023 (BNSS)**:
   - Primary PDF: [`backend/data/legal_sources/BNSS_2023_Gazette_Act_46.pdf`](file:///g:/NLP/New/backend/data/legal_sources/BNSS_2023_Gazette_Act_46.pdf) (Act No. 46 of 2023, published in *The Gazette of India, Extraordinary, Part II, Section 1, No. 54*, 25 Dec 2023).
   - Searchable Text: [`backend/data/legal_sources/extracted_text/BNSS_2023_Gazette_Act_46.txt`](file:///g:/NLP/New/backend/data/legal_sources/extracted_text/BNSS_2023_Gazette_Act_46.txt) (249 pages, 856,064 characters).
3. **Ministry of Home Affairs Commencement Notification S.O. 848(E)**:
   - Primary PDF: [`backend/data/legal_sources/MHA_Notification_SO_848E_2024.pdf`](file:///g:/NLP/New/backend/data/legal_sources/MHA_Notification_SO_848E_2024.pdf) (Gazette No. 809, dated 23 Feb 2024; appoints 1 July 2024, excluding Section 106(2) BNS First Schedule entry).
   - Searchable Text: [`backend/data/legal_sources/extracted_text/MHA_Notification_SO_848E_2024.txt`](file:///g:/NLP/New/backend/data/legal_sources/extracted_text/MHA_Notification_SO_848E_2024.txt).
4. **Authoritative Corpus Verification Matrix**:
   - Reference: [`LEGAL_SOURCE_VERIFICATION_MATRIX.md`](file:///g:/NLP/New/LEGAL_SOURCE_VERIFICATION_MATRIX.md) (Audits all 37 canonical provisions with verified India Code handles).

### 2.2 Statutory Status: Enacted BNSS Act No. 46 of 2023 vs. Introduced Bill
> [!IMPORTANT]
> **GOVERNING PROCEDURAL LAW: ACT NO. 46 OF 2023.**
> - The primary statutory procedural authority is **Act No. 46 of 2023 (Bharatiya Nagarik Suraksha Sanhita, 2023)**, commenced on 1 July 2024 under Notification S.O. 848(E).
> - The file [`backend/data/legal_sources/BNSS_2023_Introduced_Bill.pdf`](file:///g:/NLP/New/backend/data/legal_sources/BNSS_2023_Introduced_Bill.pdf) is retained strictly for legislative history and drafting provenance; it is an **unenacted draft bill** and must NOT be cited as binding procedural law.
> - For procedural classifications (Cognizable vs Non-Cognizable, Bailable vs Non-Bailable, Court of Trial), reviewers must rely exclusively on the First Schedule of **Act No. 46 of 2023** as verified in [`BNSS_2023_Gazette_Act_46.txt`](file:///g:/NLP/New/backend/data/legal_sources/extracted_text/BNSS_2023_Gazette_Act_46.txt).

### 2.3 Permitted External Government Sources
- **Indian Penal Code, 1860 (Act No. 45 of 1860)**: India Code repository ([indiacode.nic.in/handle/123456789/2263](https://www.indiacode.nic.in/handle/123456789/2263)).
- **Information Technology Act, 2000 (Act No. 21 of 2000)**: India Code repository ([indiacode.nic.in/handle/123456789/1999](https://www.indiacode.nic.in/handle/123456789/1999)).
- **The Gazette of India**: Official portal ([egazette.gov.in](https://egazette.gov.in)) for commencement notifications S.O. 850(E) and S.O. 848(E).

### 2.4 Strictly Prohibited Information Sources
- Reviewers are strictly forbidden from viewing:
  1. Algorithmic retrieval rankings, candidate provision lists, or cosine similarity scores ($\tau \ge 0.12$).
  2. Draft proposal labels stored in `blind_benchmark_dataset.json`.
  3. The other reviewer's submission worksheet or notes.
  4. Any external commercial LLM legal summaries.

---

## 3. How to Record Annotations

For each query record, reviewers must provide structured legal determinations:

### 3.1 Proposed Classification & Canonical Provision IDs
- `expected_no_match`:
  - Select `true` if the grievance is a purely civil breach of contract, commercial debt dispute, tenancy wear-and-tear disagreement, protected public photography, lawful satire/parody, or governed by unindexed legislation (e.g. Trade Marks Act 1999).
  - Select `false` if the narrative describes an offense actionable under the indexed criminal statutes.
- Proposed `relevant_provision_ids`:
  - When `expected_no_match` is `false`, record one or more canonical provision IDs from the active 37-provision corpus (e.g., `["BNS_2023_S318"]`, `["IPC_1860_S420"]`, `["ITA_2000_S66C"]`).
  - When `expected_no_match` is `true`, this list must be empty: `[]`.

### 3.2 Temporal Applicability & Article 20(1) Verification
Under **Article 20(1) of the Constitution of India**, penal statutes cannot be applied retroactively:
1. **Explicit Pre-1 July 2024 Scenarios**:
   - Must be annotated with **IPC 1860** provisions (e.g. `IPC_1860_S468`, `IPC_1860_S420`).
   - Assigning a BNS 2023 provision to a pre-July 2024 date is a constitutional violation and will fail validator checks.
2. **Explicit Post-1 July 2024 Scenarios**:
   - Must be annotated with **BNS 2023** provisions (e.g. `BNS_2023_S318`, `BNS_2023_S336`).
   - Assigning an IPC 1860 provision to a post-July 2024 date will fail validator checks.
3. **Continuous Cyber Offenses (IT Act 2000)**:
   - Apply continuously across both eras under the overriding effect of Section 81.
4. **Undated Scenarios (Policy POL-002 / Option A)**:
   - For layperson narratives where no date is specified, assign the contemporary post-reform BNS provision as primary, and document the historical IPC equivalent as an acceptable alternative in your reasoning notes.

### 3.3 Special vs. General Law Hierarchy (Policy POL-003)
- When conduct satisfies both a specific cyber offense under the IT Act and a general penal offense:
  - Identify the *lex specialis* provision (e.g., `ITA_2000_S66C` for identity theft/password hijacking).
  - State whether general computer intrusion (`ITA_2000_S66`) or general cheating should be accepted as a co-charge or alternative.

### 3.4 Incomplete Facts, Gender Prerequisites & Uncertainty (Policy POL-004)
- **Do not extrapolate unstated facts**: If a narrative is gender-neutral (`DEV_030`: *"Someone placed a GPS magnetic tracker under my vehicle"*), but the statute (BNS § 78 / IPC § 354D) requires a male perpetrator and female victim:
  - Do NOT assume the perpetrator is male or the complainant is female.
  - Record the candidate provision provisionally.
  - Explicitly record in Section 6 (Ambiguities) that statutory gender prerequisites are unverified from the facts, triggering a clarification question rather than an unsubstantiated conviction hypothesis.

### 3.5 Statutory Element Reasoning & Authoritative Citations
- Detail the specific factual elements in the narrative (*actus reus*, *mens rea*, property inducement, wrongful loss).
- Record the exact Act, Section, and official Gazette / India Code handle verified.

---

## 4. How and Where to Return Completed Submissions

```
backend/evaluation/annotation_workflow/submissions/
├── README.md
├── reviewer_a/               <-- Reviewer A saves completed markdown files here
│   └── reviewer_a_submission.md
├── reviewer_b/               <-- Reviewer B saves completed markdown files here
│   └── reviewer_b_submission.md
└── adjudication/             <-- Senior Adjudicator saves reconciliation files here
    └── adjudication_final_reconciliation.md
```

### 4.1 Reviewer Submission Steps
1. Open and complete your assigned template:
   - Reviewer A: [`REVIEWER_A_SUBMISSION_TEMPLATE.md`](file:///g:/NLP/New/backend/evaluation/annotation_workflow/REVIEWER_A_SUBMISSION_TEMPLATE.md) and [`BLIND_REVIEWER_A_TEMPLATE.md`](file:///g:/NLP/New/backend/evaluation/annotation_workflow/BLIND_REVIEWER_A_TEMPLATE.md).
   - Reviewer B: [`REVIEWER_B_SUBMISSION_TEMPLATE.md`](file:///g:/NLP/New/backend/evaluation/annotation_workflow/REVIEWER_B_SUBMISSION_TEMPLATE.md) and [`BLIND_REVIEWER_B_TEMPLATE.md`](file:///g:/NLP/New/backend/evaluation/annotation_workflow/BLIND_REVIEWER_B_TEMPLATE.md).
2. Save your completed file into your dedicated submission folder:
   - Reviewer A: `backend/evaluation/annotation_workflow/submissions/reviewer_a/reviewer_a_submission.md`
   - Reviewer B: `backend/evaluation/annotation_workflow/submissions/reviewer_b/reviewer_b_submission.md`
3. Generate the SHA-256 digest:
   ```powershell
   certutil -hashfile backend/evaluation/annotation_workflow/submissions/reviewer_a/reviewer_a_submission.md SHA256
   ```
4. Commit the file and hash to git. Do NOT share your file or hash with the other reviewer.

---

## 5. Adjudication Workflow & Inter-Annotator Agreement

Once both Reviewer A and Reviewer B submissions are sealed and committed to git:

1. **Unsealing & Automated Audit**:
   - The Senior Legal Adjudicator unseals both files.
   - The Adjudicator executes the submission validator to compute inter-annotator agreement metrics:
     ```powershell
     python backend/evaluation/annotation_workflow/validate_reviewer_submissions.py --audit-manifest
     ```
2. **Inter-Annotator Agreement Calculation**:
   - The validator computes:
     - **Exact-Set Match Ratio**: Percentage of records where both reviewers proposed identical provision ID sets.
     - **Mean Pairwise Jaccard**: Average set similarity $\frac{|A \cap B|}{|A \cup B|}$ across all queries.
     - **Cohen's Kappa ($\kappa$)**: Chance-corrected agreement on binary `expected_no_match` decisions.
3. **Disagreement Resolution**:
   - Where reviewers agree, the unanimous label is affirmed.
   - Where reviewers disagree (partial overlap or disjoint provisions), the Senior Legal Adjudicator examines the statutory elements and issues a binding, documented determination in [`ADJUDICATION_TEMPLATE.md`](file:///g:/NLP/New/backend/evaluation/annotation_workflow/ADJUDICATION_TEMPLATE.md) and [`BLIND_ADJUDICATION_TEMPLATE.md`](file:///g:/NLP/New/backend/evaluation/annotation_workflow/BLIND_ADJUDICATION_TEMPLATE.md).
4. **Dataset Ingestion**:
   - Only after all 45 records have been adjudicated and signed off will an automated script update `annotation_status` to `"reviewed"`.
   - The Benchmark Lead will then execute the benchmark freeze.
