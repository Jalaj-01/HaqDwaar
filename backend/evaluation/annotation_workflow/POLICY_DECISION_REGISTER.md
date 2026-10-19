# LexiLaw — Evaluation Policy Decision & Approval Register

**Document Version:** 1.0.0  
**Registration Date:** October 18, 2026  
**Document Status:** **PENDING HUMAN REVIEW & FORMAL SIGN-OFF**  
**Engineering & Quality Role:** NLP Evaluation Lead & Senior Legal QA Auditor  
**Corpus SHA-256 Digest:** `becf1f001631bbdc301633df428b0cb541dca97fa45b1ad7cf05db8b1d0d00d0`  
**Benchmark Manifest:** [`backend/evaluation/benchmark_manifest.json`](file:///g:/NLP/New/backend/evaluation/benchmark_manifest.json) (`locked: false`)  
**Companion Policy Specification:** [`TEMPORAL_POLICY_DECISION.md`](file:///g:/NLP/New/backend/evaluation/annotation_workflow/TEMPORAL_POLICY_DECISION.md)  

---

## 1. Executive Summary & Purpose

This Decision Register catalogs all unresolved legal, temporal, and methodological policy choices required before the LexiLaw benchmark portfolio (10 quarantined dev/test records and 35 independent blind scenarios) can be finalized and frozen.

In strict compliance with evaluation integrity guidelines:
- **No policy is presumed approved** prior to authentic human signature.
- **No reviewer names, credentials, dates, or signatures are fabricated.**
- The benchmark remains **unlocked (`locked: false`)** until all designated human approvers execute this register.

---

## 2. Policy Decision Register

### Decision POL-001: Authoritative BNSS Source Upgrade & Procedural Guidance Status

| Field | Detail |
| :--- | :--- |
| **Policy ID** | **`POL-001`** |
| **Subject** | Procedural Authority: BNSS 2023 Draft Bill vs. Enacted Gazette Act No. 46 of 2023 |
| **Related Records** | All procedural classification fields (Cognizable/Bailable) across all 37 provisions |
| **Statutory Context** | The project initially referenced a PDF titled *"Bharatiya Nagarik Suraksha Sanhita, 2023"* marked *"As Introduced in Lok Sabha"* (Parliamentary Bill No. 122/173 of 2023). This document is an unenacted legislative bill. The Parliament of India enacted **Act No. 46 of 2023**, published in *The Gazette of India, Extraordinary, Part II, Section 1, No. 63*, on 25 December 2023, commenced on 1 July 2024 vide Ministry of Home Affairs Notification S.O. 848(E). |
| **Core Question** | Shall LexiLaw formally upgrade its statutory source authority for procedural guidance from the draft Lok Sabha Bill to the final enacted Gazette Act No. 46 of 2023, while maintaining an explicit draft caveat on UI outputs until full textual ingestion is validated? |
| **Option A (Recommended)** | **Formally adopt Act No. 46 of 2023** as the sole governing authority for procedural guidance; ingest verified First Schedule classifications ([`BNSS_2023_ACT_46_ENACTED.json`](file:///g:/NLP/New/backend/data/authoritative_sources/BNSS_2023_ACT_46_ENACTED.json)); retain provisional UI caveat until human legal review is finalized. |
| **Option B** | Retain draft bill citations in procedural outputs without updating source metadata. |
| **Consequences** | **Option A**: Eliminates risk of legal misinformation arising from clause renumbering or Schedule I classification amendments between the draft bill and enacted Act; ensures complete judicial defensibility.<br>**Option B**: Exposes lay users to potential discrepancies between draft legislative proposals and enforceable procedural law. |
| **Recommendation** | **Adopt Option A**. Upgrades legal authority to enacted statutory standard without silently mutating runtime code. |
| **Required Approver** | Legal Lead |
| **Current Status** | **PENDING HUMAN REVIEW & SIGN-OFF** |

#### Sign-Off Block (POL-001)
- **Approver Name / Bar ID:** __________________________________________________
- **Title / Role:** Legal Lead & Regulatory Counsel
- **Decision:** [ ] APPROVED (Option A)    [ ] REJECTED (Option B)    [ ] MODIFIED
- **Date Signed:** ____________________
- **Signature / Digital Stamp:** __________________________________________________
- **Specific Conditions / Directives:** ___________________________________________

---

### Decision POL-002: Temporal Ground Truth & Undated Query Evaluation Policy

| Field | Detail |
| :--- | :--- |
| **Policy ID** | **`POL-002`** |
| **Subject** | Temporal Ground Truth & Metric Scoring for Undated Complainant Incidents |
| **Related Records** | `DEV_028`, `DEV_030`, `TEST_016`, `TEST_020`, and all undated real-world intake queries |
| **Statutory Context** | Under **Article 20(1) of the Constitution of India**, penal statutes cannot be applied retroactively. On 1 July 2024, the BNS replaced the IPC. When a lay complainant presents an undated grievance, the conduct may constitute an offense under both BNS and IPC, but the governing code depends strictly on the factual date of commission. |
| **Core Question** | How shall the retrieval benchmark evaluate undated user narratives that fall under both BNS and IPC, without forcing laypersons to provide mandatory dates or artificially penalizing the IR model? |
| **Option A (Recommended)** | **Dual / Disjunctive Equivalence with `acceptable_alternative_ids`**: The benchmark designates the contemporary BNS provision as primary, but records the historical IPC provision in `acceptable_alternative_ids`. Evaluator metric math (`compute_query_metrics`) recognizes retrieval of either or both without penalizing Recall@5 or Precision@5. |
| **Option B** | **Era-Anchored Query Modification**: Modify all undated queries in the benchmark to force an explicit date (e.g., adding "In August 2024..."). |
| **Option C** | **Strict Contemporary Convention**: Mandate that undated queries must strictly retrieve contemporary BNS 2023 provisions; treat retrieval of IPC provisions as false positives. |
| **Consequences** | **Option A**: Preserves realistic layperson narratives; maintains ecological validity; respects Article 20(1) by treating both eras as legally plausible until dated; prevents artificial halving of Recall@5.<br>**Option B**: Destroys real-world evaluation realism by eliminating the common case of undated grievances.<br>**Option C**: Violates legal reality by penalizing systems that correctly identify applicable law for incidents that may have occurred prior to July 2024. |
| **Recommendation** | **Adopt Option A**. Supported by the newly upgraded evaluator engine in [`backend/evaluation/eval_retrieval.py`](file:///g:/NLP/New/backend/evaluation/eval_retrieval.py). |
| **Required Approvers** | Legal Lead & NLP Evaluation Lead |
| **Current Status** | **PENDING HUMAN REVIEW & SIGN-OFF** |

#### Sign-Off Block (POL-002)
- **Approver 1 (Legal Lead):** ___________________________________  Date: ____________  Sign: ___________________
- **Approver 2 (NLP Lead):** _____________________________________  Date: ____________  Sign: ___________________
- **Decision:** [ ] APPROVED (Option A)    [ ] REJECTED    [ ] MODIFIED
- **Specific Conditions / Directives:** ___________________________________________

---

### Decision POL-003: Special Law vs. General Law Hierarchy & Multi-Label Ground Truth (`DEV_026`)

| Field | Detail |
| :--- | :--- |
| **Policy ID** | **`POL-003`** |
| **Subject** | Multi-Label Ground Truth & Special Law Hierarchy for Cyber Identity Theft (`DEV_026`) |
| **Related Records** | `DEV_026` (*"Someone logged into my work email account using stolen credentials and sent offensive emails to our leadership team."*) |
| **Statutory Context** | Section 66C of the Information Technology Act, 2000 penalizes identity theft (fraudulent use of electronic signature, password, or unique identification feature). Section 66 penalizes computer-related offenses (acts under Section 43 done dishonestly or fraudulently). Under Section 81 of the IT Act and Supreme Court precedent (*Sharat Babu Digumarti v. Govt of NCT of Delhi, 2017*), special cyber provisions govern electronic acts. However, in practice, police FIRs routinely charge both Sections 66 and 66C concurrently. |
| **Core Question** | Should the ground truth for `DEV_026` restrict the target to `ITA_2000_S66C` exclusively, or allow `ITA_2000_S66` as an acceptable alternative / multi-label co-charge? |
| **Option A (Recommended)** | **Multi-Label / Acceptable Alternative Ground Truth**: Designate `ITA_2000_S66C` as primary target, with `ITA_2000_S66` included in `acceptable_alternative_ids` (or multi-label set `[ITA_2000_S66C, ITA_2000_S66]`). |
| **Option B** | **Strict Single-Label Restriction**: Designate `ITA_2000_S66C` as the sole acceptable provision; treat retrieval of `ITA_2000_S66` as a non-relevant false positive. |
| **Consequences** | **Option A**: Accurately mirrors real-world Indian cyber jurisprudence and prosecution practice; rewards the model for identifying both the specific identity theft and the underlying computer access violation.<br>**Option B**: Artificially penalizes the retrieval model for returning the overarching criminal hacking section. |
| **Recommendation** | **Adopt Option A**. Multi-label alignment preserves both specific and general statutory grounding. |
| **Required Approver** | Legal Lead |
| **Current Status** | **PENDING HUMAN REVIEW & SIGN-OFF** |

#### Sign-Off Block (POL-003)
- **Approver Name / Bar ID:** __________________________________________________
- **Title / Role:** Legal Lead
- **Decision:** [ ] APPROVED (Option A)    [ ] REJECTED (Option B)    [ ] MODIFIED
- **Date Signed:** ____________________
- **Signature / Digital Stamp:** __________________________________________________
- **Specific Conditions / Directives:** ___________________________________________

---

### Decision POL-004: Incomplete Facts, Statutory Gender Prerequisites & Clarification Triggers (`DEV_030`)

| Field | Detail |
| :--- | :--- |
| **Policy ID** | **`POL-004`** |
| **Subject** | Incomplete Narrative Facts, Gender Prerequisites, and Clarification Follow-up (`DEV_030`) |
| **Related Records** | `DEV_030` (*"Someone placed a GPS magnetic tracker under my vehicle and monitored everywhere I drove for two weeks."*) |
| **Statutory Context** | Section 78 BNS and Section 354D IPC define the offense of stalking. Both statutes explicitly specify a gender requirement: the perpetrator must be a **man** and the victim must be a **woman** (*"Any man who follows a woman..."*). The narrative in `DEV_030` is completely gender-neutral ("Someone... my vehicle"). |
| **Core Question** | How should the evaluation benchmark treat a grievance where the conduct matches the physical *actus reus* of a crime (electronic tracking), but the narrative omits statutory personal characteristics (gender)? |
| **Option A (Recommended)** | **Provisional Stalking Hypothesis with Mandatory Clarification Trigger**: Designate `BNS_2023_S78` (and `IPC_1860_S354D` alternative) as provisional candidates, paired with `requires_clarification: true`. LexiLaw displays the provision with an explicit caveat noting that statutory gender elements are unestablished, and issues a neutral clarification question. |
| **Option B** | **Out-of-Scope / No-Match (`expected_no_match: true`)**: Mark the query as an out-of-scope non-offense because gender elements are unstated. |
| **Consequences** | **Option A**: Maximizes victim protection and intake utility by surfacing the relevant statute while transparently identifying missing factual elements.<br>**Option B**: Causes the system to completely abstain on vehicle stalking reports from laypersons who simply omitted gender pronouns in their initial sentence. |
| **Recommendation** | **Adopt Option A**. Aligns with Stage 7 (Clarification Questions) of the LexiLaw 8-stage pipeline. |
| **Required Approver** | Legal Lead |
| **Current Status** | **PENDING HUMAN REVIEW & SIGN-OFF** |

#### Sign-Off Block (POL-004)
- **Approver Name / Bar ID:** __________________________________________________
- **Title / Role:** Legal Lead
- **Decision:** [ ] APPROVED (Option A)    [ ] REJECTED (Option B)    [ ] MODIFIED
- **Date Signed:** ____________________
- **Signature / Digital Stamp:** __________________________________________________
- **Specific Conditions / Directives:** ___________________________________________

---

### Decision POL-005: Independent Double-Blind Annotation & Senior Adjudication Protocol

| Field | Detail |
| :--- | :--- |
| **Policy ID** | **`POL-005`** |
| **Subject** | Protocol for Reviewer Independence, Air-Gap Cryptographic Sealing, and Adjudication |
| **Related Records** | All 45 pending records (10 dev/test quarantined records + 35 blind benchmark scenarios) |
| **Methodological Context** | Scientific and academic validity requires that human ground truth be established through independent, double-blind review to prevent confirmation bias, anchor bias, or model over-fitting. |
| **Core Question** | Shall LexiLaw formally require an air-gapped double-blind review process where Reviewer A and Reviewer B submit independent determinations without model score visibility, verified via cryptographic hashes before adjudication unsealing? |
| **Option A (Recommended)** | **Cryptographically Sealed Double-Blind Protocol**: Mandate that Reviewer A and Reviewer B complete independent packets ([`REVIEWER_A_SUBMISSION_TEMPLATE.md`](file:///g:/NLP/New/backend/evaluation/annotation_workflow/REVIEWER_A_SUBMISSION_TEMPLATE.md) / [`BLIND_REVIEWER_A_TEMPLATE.md`](file:///g:/NLP/New/backend/evaluation/annotation_workflow/BLIND_REVIEWER_A_TEMPLATE.md)). Both files must be committed to `submissions/` with SHA-256 hashes recorded before the Senior Legal Adjudicator unseals them. Disagreements must be reconciled in the Adjudication Worksheet. |
| **Option B** | Single reviewer review or informal collaborative annotation without cryptographic sealing. |
| **Consequences** | **Option A**: Guarantees zero contamination, high academic credibility, measurable inter-annotator agreement (Cohen's Kappa & Jaccard), and complete reproducibility.<br>**Option B**: Risks subconscious bias, cannot verify independence, and undermines academic defensibility. |
| **Recommendation** | **Adopt Option A**. Protocol fully operationalized in `backend/evaluation/annotation_workflow/`. |
| **Required Approvers** | NLP Evaluation Lead & Senior QA Auditor |
| **Current Status** | **PENDING HUMAN REVIEW & SIGN-OFF** |

#### Sign-Off Block (POL-005)
- **Approver 1 (NLP Evaluation Lead):** ____________________________  Date: ____________  Sign: ___________________
- **Approver 2 (Senior QA Auditor):** ______________________________  Date: ____________  Sign: ___________________
- **Decision:** [ ] APPROVED (Option A)    [ ] REJECTED    [ ] MODIFIED
- **Specific Conditions / Directives:** ___________________________________________

---

## 3. Master Approval Tracking Summary

| Decision ID | Summary Topic | Recommended Option | Designated Approvers | Status | Approval Date |
| :---: | :--- | :---: | :--- | :---: | :---: |
| **`POL-001`** | Authoritative BNSS Source Upgrade | Option A | Legal Lead | **PENDING** | *Unsigned* |
| **`POL-002`** | Temporal Ground Truth & Undated Queries | Option A | Legal Lead & NLP Eval Lead | **PENDING** | *Unsigned* |
| **`POL-003`** | Special vs. General Law Hierarchy (`DEV_026`) | Option A | Legal Lead | **PENDING** | *Unsigned* |
| **`POL-004`** | Gender Prerequisites & Clarification (`DEV_030`) | Option A | Legal Lead | **PENDING** | *Unsigned* |
| **`POL-005`** | Double-Blind Reviewer & Adjudication Protocol | Option A | NLP Eval Lead & QA Auditor | **PENDING** | *Unsigned* |

---

## 4. Benchmark Freeze Prohibition Notice

> [!CAUTION]
> **STRICT REPOSITORY LOCK RULE:**
> Until all 5 decisions in this register have received authentic, written human signatures from the designated approvers:
> 1. `backend/evaluation/benchmark_manifest.json` must remain `"locked": false`.
> 2. No pending evaluation record in `retrieval_eval_dataset.json` or `blind_benchmark_dataset.json` may be transitioned to `"annotation_status": "reviewed"`.
> 3. Official blind benchmark evaluation must NOT be executed.
