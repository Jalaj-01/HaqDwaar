# LexiLaw — Legal Annotation Policy, Product Scope, and Source-Grounding Specification

**Document Status:** **PENDING HUMAN REVIEW & SIGN-OFF**  
**Engineering & Evaluation Phase:** LexiLaw Phase 5A / Annotation Workflow Alignment  
**Date:** October 18, 2026  
**Auditor / Engineering Role:** Legal-Data Evaluation Auditor & QA Engineer  
**Workspace Root:** `G:\NLP\New`  
**Core Target Artifacts:**
- Primary Evaluation Dataset: [`backend/evaluation/retrieval_eval_dataset.json`](file:///g:/NLP/New/backend/evaluation/retrieval_eval_dataset.json) (50 total records)
- Quarantined Draft Records: 10 records (`DEV_026`–`DEV_030` and `TEST_016`–`TEST_020`)
- Active Legal Corpus: [`backend/data/legal_provisions.json`](file:///g:/NLP/New/backend/data/legal_provisions.json) (37 provisions)
- Corpus SHA-256 Digest: `becf1f001631bbdc301633df428b0cb541dca97fa45b1ad7cf05db8b1d0d00d0`
- Pending Review Dossier: [`PENDING_ANNOTATION_REVIEW.md`](file:///g:/NLP/New/PENDING_ANNOTATION_REVIEW.md)
- Operating Retrieval Cutoff: $\tau = 0.12$ (Frozen baseline)

---

## 1. Product Scope & Functional Architecture

LexiLaw is a **source-grounded legal guidance prototype** designed for laypersons, legal clinic intake workers, and initial incident assessment. It accepts natural-language descriptions of real-world grievances, identifies potentially relevant statutory provisions, explains supported statutory consequences, and provides cautious procedural guidance and practical next steps.

```
+---------------------------------------------------------------------------------------------------+
|                                 LEXILAW 8-STAGE WORKFLOW PIPELINE                                 |
+---------------------------------------------------------------------------------------------------+
| 1. Incident Understanding  : Preprocessing, entity & fact extraction, category classification     |
| 2. Candidate Retrieval     : Hybrid IR (0.40 TF-IDF + 0.60 dense MiniLM) at threshold tau = 0.12  |
| 3. Statutory Explanation   : Ingredient mapping (facts -> statutory elements: supported/unest.)  |
| 4. Penalty Guidance        : Maximum penalty display ONLY where commenced & source-verified       |
| 5. Procedural Guidance     : Cautious categorization (Cognizable/Bailable) with source caveats    |
| 6. Practical Next Steps    : Evidence preservation, official reporting channels, legal aid referral|
| 7. Clarification Questions : Neutral follow-up prompts when crucial legal facts/dates are omitted  |
| 8. Explicit Uncertainty    : Abstention on civil matters, preliminary flags, non-definitive advice|
+---------------------------------------------------------------------------------------------------+
```

### 1.1 The Strict Prohibition on Definitive Legal Advice
- LexiLaw **never** declares a user or accused "guilty" or "convicted".
- LexiLaw **never** promises legal remedies, financial recovery, or court outcomes.
- All system responses are provisional hypotheses grounded in explicit statutory citations, intended to empower users to consult qualified advocates or law-enforcement authorities effectively.

---

## 2. Intended Source Documents & Source-Status Limitations

The project design specifies two primary reference documents for the post-reform criminal legal framework:
1. **The Gazette-published Bharatiya Nyaya Sanhita, 2023 (BNS)**: Act No. 45 of 2023, published in The Gazette of India, Extraordinary, Part II, Section 1, No. 62, dated 25 December 2023.
2. **The Bharatiya Nagarik Suraksha Sanhita, 2023 (BNSS) Document marked "As Introduced in Lok Sabha"**: Parliamentary Bill No. 122 of 2023 (introduced 11 August 2023) or Bill No. 173 of 2023 (re-introduced December 2023).

### 2.1 Critical Source-Status Limitation: The BNSS Introduced Bill
> [!WARNING]
> **DO NOT TREAT THE BNSS INTRODUCED BILL AS FINAL ENACTED LAW.**
> The uploaded BNSS document is marked *"As Introduced in Lok Sabha"*. It is an unenacted legislative draft bill that underwent substantial scrutiny, public submissions, and revisions by the Parliamentary Standing Committee on Home Affairs before enactment.
> 
> **Specific Risks of Using the Introduced Bill for Procedural Law:**
> 1. **Clause Numbering Drift**: Several section numbers and clause references shifted between the introduced Bill and the final enacted Act (Act No. 46 of 2023).
> 2. **Schedule I Classification Revisions**: The First Schedule of the BNSS classifies offenses as *Cognizable vs. Non-Cognizable*, *Bailable vs. Non-Bailable*, and *Court of Trial*. Classifications in the introduced Bill were subjected to parliamentary debate and modification.
> 3. **Statutory Gaps**: Using an introduced bill to substantiate enforceable procedural claims (such as mandatory arrest guidelines under Section 35 BNSS or preliminary enquiry timelines under Section 173(3) BNSS) creates severe risk of misinformation.
> 
> **Mandatory Policy Rule:**
> - Procedural guidance derived from the BNSS Introduced Bill must be explicitly stamped as **"Provisional Procedural Guidance (Draft Lok Sabha Bill Status — Pending Verification Against Enacted Gazette Act No. 46 of 2023)"**.
> - The final enacted Gazette copy of **Act No. 46 of 2023 (Bharatiya Nagarik Suraksha Sanhita, 2023)** must be acquired and verified before removing this provisional caveat.

### 2.2 Provisions Outside the Two Intended Documents
The active 37-provision corpus contains statutes that **cannot** be substantiated by either of the two intended BNS/BNSS documents:
- **Indian Penal Code, 1860 (14 provisions)**: Requires the historical India Code primary repository for Act No. 45 of 1860.
- **Information Technology Act, 2000 (8 provisions)**: Requires India Code primary repository for Act No. 21 of 2000 as amended by the Information Technology (Amendment) Act, 2008 (Act No. 10 of 2009).
- **Digital Personal Data Protection Act, 2023 (1 provision)**: Requires The Gazette of India publication of Act No. 22 of 2023.

---

## 3. Temporal Policy & Date Materiality Framework

In July 2024, India replaced the IPC with the BNS. Under **Article 20(1) of the Constitution of India**:
> *"No person shall be convicted of any offence except for violation of a law in force at the time of the commission of the act charged as an offence, nor be subjected to a penalty greater than that which might have been inflicted under the law in force at the time of the commission of the offence."*

### 3.1 Layperson Realities: No Mandatory Date Requirement
In practical consumer applications, requiring lay complainants to enter an exact date of occurrence creates friction and leads to drop-offs or arbitrary dates. **LexiLaw does not require an incident date for every input.**

### 3.2 Definition of Date Materiality
An incident date is **material** if and only if the grievance involves conduct whose substantive statutory definition, penalty ceiling, or constituent elements changed during the 1 July 2024 transition:

| Scenario / Subject Matter | Date Materiality | Legal Reason |
| :--- | :--- | :--- |
| **Cyber Offenses under IT Act 2000** (e.g. Identity Theft § 66C, Hacking § 43/66, Data Privacy § 66E) | **NON-MATERIAL** | The Information Technology Act, 2000 applies continuously across pre- and post-2024 eras (§ 81 non-obstante clause). Temporal era does not alter governing law. |
| **Purely Civil Disputes** (Tenancy rent default, airline refund, municipal tax) | **NON-MATERIAL** | Out-of-scope non-penal matters (`expected_no_match: true`); no penal statute applies in either era. |
| **Trademark Counterfeiting** (Commercial goods imitating registered brand) | **NON-MATERIAL** | Governed by Trade Marks Act 1999 (special law outside the indexed penal corpus). |
| **Financial Fraud & Cheating** (IPC § 420 vs. BNS § 318) | **MATERIAL** | IPC § 420 had a 7-year penalty; BNS § 318 restructured cheating into tiers (subsections (1) to (4)) with distinct penalty thresholds. |
| **Fatal Negligent Driving / Hit-and-Run** (IPC § 304A vs. BNS § 106(1) vs. BNS § 106(2)) | **HIGHLY MATERIAL** | Pre-July 2024 is capped at 2 years under IPC 304A. Post-July 2024 is 5 years under BNS 106(1). Section 106(2) (10 years) is uncommenced. Article 20(1) strictly bars BNS penalties for pre-July 2024 driving. |
| **Theft & Snatching** (IPC § 379/356 vs. BNS § 303/304) | **HIGHLY MATERIAL** | BNS § 304 introduced "snatching" as a distinct statutory crime with rigorous imprisonment up to 3 years. IPC had no distinct snatching offense. |
| **Stalking & Cyber Harassment** (IPC § 354D vs. BNS § 78) | **MATERIAL** | Definitions are substantially similar, but charging document and procedural schedules differ between IPC/CrPC and BNS/BNSS. |

### 3.3 Handling Undated Incidents Without Unverified Assumptions
When a user describes an incident without specifying a date, and the offense triggers **Date Materiality**:
1. **No Silent Assumption**: The system **must not** silently assume the incident occurred post-1 July 2024 or pre-1 July 2024.
2. **Dual Transitional Presentation**:
   - The system displays the primary contemporary provision (BNS) alongside its historical counterpart (IPC).
   - A prominent **Temporal Advisory Banner** is displayed:
     > *"Incident Date Required to Confirm Applicable Code: Because criminal laws in India were revised on 1 July 2024, the governing code depends on when this incident occurred. If before 1 July 2024, the Indian Penal Code applies. If on or after 1 July 2024, the Bharatiya Nyaya Sanhita applies."*
3. **Automated Follow-up Clarification**: The system generates a neutral clarification question:
   *"Did this incident occur before or after 1 July 2024? (An approximate month and year is sufficient)."*

---

## 4. Mandatory Source-Grounded Evidence for Annotations

Every ground-truth label in LexiLaw benchmark datasets must be accompanied by verified legal evidence. An annotation lacking source grounding is invalid.

### 4.1 Required 5-Point Evidence Schema
For each annotated query, reviewers and adjudicators must supply:
1. `provision_id`: Exact canonical string from the verified corpus (e.g., `BNS_2023_S318`, `ITA_2000_S66C`).
2. `act_name`: Full statutory title with enactment year.
3. `section_id`: Specific section or sub-section number.
4. `source_reference`: Official primary source identifier:
   - For BNS: Act No. 45 of 2023, Gazette Notification S.O. 850(E) (commencement), or India Code handle.
   - For IPC: Act No. 45 of 1860, India Code repository.
   - For IT Act: Act No. 21 of 2000 as amended, India Code repository.
   - For BNSS procedural references: Note whether verified against Gazette Act No. 46 of 2023 or draft Lok Sabha Bill status.
5. `statutory_ingredient_mapping`: A concise prose explanation (2–4 sentences) demonstrating how the stated facts in the query satisfy the essential legal elements (*actus reus*, *mens rea*, property inducement, bodily harm, or digital intrusion).

### 4.2 Absolute Prohibition: Similarity Scores Are Not Legal Evidence
- Algorithmic retrieval scores ($\tau \ge 0.12$, BM25, dense cosine similarity) reflect surface textual/keyword similarity.
- A score of `0.35` indicates that query tokens resemble statutory tokens; it **does not** prove an offense occurred or that statutory elements are met.
- **Reviewers and adjudicators are strictly forbidden from citing similarity scores as justification for a ground-truth label.**

---

## 5. Universal Ground-Truth Annotation Rules

### Rule 1: Single-Label vs. Multi-Label Assignment
- **Single-Label Assignment**: Permitted when conduct constitutes an isolated offense where a specific section (*lex specialis*) fully exhausts the criminal liability (e.g. theft of a bicycle without violence -> Section 303(2) BNS).
- **Multi-Label Assignment**: Mandatory whenever an incident contains distinct elements of non-merging statutory offenses:
  - *Example 1 (`DEV_026`)*: Using stolen credentials to log into a work email account and send offensive emails satisfies:
    - Section 66C IT Act (Identity Theft: fraudulent use of unique password/identification).
    - Section 66 IT Act (Computer-Related Offenses: unauthorized access under Section 43 with fraudulent intent).
    - *Ground Truth*: Both provisions must be included in `relevant_provision_ids` or designated as primary + accepted alternative.
  - *Example 2 (`TEST_017`)*: Submitting forged invoices in Dec 2023 to divert company funds:
    - Section 468 IPC (Forgery for Cheating).
    - Section 471 IPC (Using a Forged Document).
    - Section 420 IPC (Cheating and Dishonestly Inducing Delivery of Property).
    - Section 406 IPC (Criminal Breach of Trust).
    - *Ground Truth*: Restricting the benchmark to Section 420 alone penalizes the retrieval model for identifying more specific applicable forgery statutes.

### Rule 2: Expected No-Match (`expected_no_match`) Criteria
A query must be labeled `expected_no_match: true` with `relevant_provision_ids: []` if and only if:
1. **Civil & Commercial Disputes**: Exclusive breach of contract, unpaid rent, landlord-tenant security deposit defaults, commercial invoice delays without fraudulent inception.
2. **Administrative & Municipal Matters**: Property tax reassessment notices, municipal fines, utility billing disagreements.
3. **Lawful Exercise of Rights**:
   - `TEST_018`: Photographing a company storefront from a public street sidewalk (protected public conduct; voyeurism/trespass elements absent).
   - `TEST_019`: Parody account on social media clearly labeled as satire (lacks fraudulent intent / *mens rea* for impersonation cheating).
4. **Specialized Statutes Outside Corpus**:
   - `DEV_027`: Manufacturing counterfeit branded handbags mimicking trademark logo (governed by Trade Marks Act 1999, Sections 102–104).

### Rule 3: Insufficient Facts & Preserving Uncertainty
- Reviewers **must not extrapolate or invent unstated facts**.
- If a statute has a substantive personal attribute or gender requirement (e.g. BNS § 78 / IPC § 354D stalking requiring a man tracking a woman), and the narrative is completely gender-neutral (`DEV_030`: *"Someone placed a GPS magnetic tracker under my vehicle"*):
  - Reviewers must preserve uncertainty.
  - Ground truth must record the candidate provision with an explicit caveat noting that the statutory gender prerequisite is unverified from the facts, triggering a clarification question rather than an unverified assumption.

### Rule 4: Candidate Hypotheses vs. Confirmed Labels
- **Candidate Provisions**: High-scoring algorithmic outputs generated by the retrieval pipeline (e.g. candidates with score $\ge \tau = 0.12$). They are hypotheses to inspect, NOT verified ground truth.
- **Confirmed Benchmark Labels**: Provisions whose statutory ingredients have been independently verified against official Gazette / India Code text by human legal reviewers.

---

## 6. Source-Grounded Presentation of Penalties, Procedures, and Actions

| Output Component | Presentation Condition | Permitted Display | Forbidden Display |
| :--- | :--- | :--- | :--- |
| **Statutory Penalties** | Only when provision is `source_verified: true` AND commenced. | Exact statutory range (e.g. "Imprisonment up to 3 years and fine"). | Do NOT display penalties for uncommenced statutes (`BNS 106(2)`, `DPDP 33`). Suppress penalty and flag commencement status. |
| **Procedural Guidance (Cognizable / Bailable)** | Only where supported by authoritative procedural schedule. | Cautious procedural note citing BNSS Schedule I. Must flag draft bill limitation if using Lok Sabha Introduced Bill. | Do NOT make definitive claims of non-bailable arrest powers without citing enacted Gazette Act No. 46 of 2023. |
| **Practical Next Steps** | Grounded in lawful intake practices. | Evidence preservation (screenshots, timestamps, email headers), reporting to jurisdictional Cyber Cell (`cybercrime.gov.in`), filing Zero FIR, consulting legal counsel. | Do NOT guarantee FIR registration, police action, or conviction. |
| **Clarification Questions** | Triggered when constituent facts or incident dates are missing. | Neutral, non-leading questions (e.g. "Did this incident occur before or after 1 July 2024?", "Was permission granted?"). | Do NOT suggest answers or fabricate narratives. |

---

## 7. Taxonomy: Statutory Text vs. Engineering Policy vs. Assumptions vs. Human Review

To maintain rigorous transparency, LexiLaw distinguishes four epistemic tiers:

```
+---------------------------------------------------------------------------------------------------+
| 1. STATUTORY TEXT                                                                                 |
|    - Primary legislation published in The Gazette of India or India Code.                         |
|    - Immutable ground truth: exact section numbers, elements, punishment ranges, and definitions. |
+---------------------------------------------------------------------------------------------------+
| 2. ENGINEERING POLICY & HEURISTICS                                                                |
|    - Threshold cutoffs (tau = 0.12), fusion weights (0.40 TF-IDF + 0.60 dense MiniLM).            |
|    - Regex gatekeepers (is_out_of_scope_civil_incident), temporal era detection rules.             |
|    - Penalty suppression mechanisms for unverified / uncommenced provisions.                      |
+---------------------------------------------------------------------------------------------------+
| 3. WORKING ASSUMPTIONS                                                                            |
|    - Hypotheses adopted when input narratives omit essential facts (e.g. undated incidents).      |
|    - Must always be explicitly flagged to the user with advisories and clarification prompts.     |
+---------------------------------------------------------------------------------------------------+
| 4. HUMAN-REVIEWED LEGAL INTERPRETATIONS                                                           |
|    - Multi-annotator adjudications on legal scope, lex specialis hierarchy, and mens rea.        |
|    - Independent reviewer assessments documented in formal adjudication dossiers.                 |
+---------------------------------------------------------------------------------------------------+
```

---

## 8. Authoritative Source-Coverage Audit Matrix (37 Corpus Provisions)

Audit of all 37 active provisions in `backend/data/legal_provisions.json` (SHA-256: `becf1f001631bbdc301633df428b0cb541dca97fa45b1ad7cf05db8b1d0d00d0`) against:
- **Document 1**: Gazette-published Bharatiya Nyaya Sanhita, 2023 (Act No. 45 of 2023).
- **Document 2**: Bharatiya Nagarik Suraksha Sanhita, 2023 (BNSS) marked "As Introduced in Lok Sabha".

| # | Provision ID | Act Name & Section | Supported by Doc 1 (Gazette BNS)? | Supported by Doc 2 (BNSS Bill)? | External Primary Source Required | Legal Commencement & Verification Status |
|---|---|---|---|---|---|---|
| 1 | `BNS_2023_S77` | BNS § 77 (Voyeurism) | **YES** (Substantive) | Provisional only (Schedule I) | None for offense; Gazette BNSS Act 46/2023 for procedure | Commenced 1 July 2024. Verified against Gazette Act 45/2023. |
| 2 | `BNS_2023_S78` | BNS § 78 (Stalking) | **YES** (Substantive) | Provisional only (Schedule I) | None for offense; Gazette BNSS Act 46/2023 for procedure | Commenced 1 July 2024. Verified against Gazette Act 45/2023. |
| 3 | `BNS_2023_S79` | BNS § 79 (Word/gesture to insult modesty) | **YES** (Substantive) | Provisional only (Schedule I) | None for offense; Gazette BNSS Act 46/2023 for procedure | Commenced 1 July 2024. Verified against Gazette Act 45/2023. |
| 4 | `BNS_2023_S106_SUB2_UNCOMMENCED` | BNS § 106(2) (Fatal hit-and-run) | **YES** (Enacted text) | Provisional only (Schedule I) | Gazette S.O. 850(E) (Notification excluding commencement) | **ENACTED BUT UNCOMMENCED**. Penalty suppressed. |
| 5 | `BNS_2023_S303` | BNS § 303 (Theft) | **YES** (Substantive) | Provisional only (Schedule I) | None for offense; Gazette BNSS Act 46/2023 for procedure | Commenced 1 July 2024. Verified against Gazette Act 45/2023. |
| 6 | `BNS_2023_S308` | BNS § 308 (Extortion) | **YES** (Substantive) | Provisional only (Schedule I) | None for offense; Gazette BNSS Act 46/2023 for procedure | Commenced 1 July 2024. Verified against Gazette Act 45/2023. |
| 7 | `BNS_2023_S316` | BNS § 316 (Criminal breach of trust) | **YES** (Substantive) | Provisional only (Schedule I) | None for offense; Gazette BNSS Act 46/2023 for procedure | Commenced 1 July 2024. Verified against Gazette Act 45/2023. |
| 8 | `BNS_2023_S318` | BNS § 318 (Cheating) | **YES** (Substantive) | Provisional only (Schedule I) | None for offense; Gazette BNSS Act 46/2023 for procedure | Commenced 1 July 2024. Verified against Gazette Act 45/2023. |
| 9 | `BNS_2023_S319` | BNS § 319 (Cheating by personation) | **YES** (Substantive) | Provisional only (Schedule I) | None for offense; Gazette BNSS Act 46/2023 for procedure | Commenced 1 July 2024. Verified against Gazette Act 45/2023. |
| 10 | `BNS_2023_S324` | BNS § 324 (Mischief) | **YES** (Substantive) | Provisional only (Schedule I) | None for offense; Gazette BNSS Act 46/2023 for procedure | Commenced 1 July 2024. Verified against Gazette Act 45/2023. |
| 11 | `BNS_2023_S336` | BNS § 336 (Forgery) | **YES** (Substantive) | Provisional only (Schedule I) | None for offense; Gazette BNSS Act 46/2023 for procedure | Commenced 1 July 2024. Verified against Gazette Act 45/2023. |
| 12 | `BNS_2023_S340` | BNS § 340 (Using forged record) | **YES** (Substantive) | Provisional only (Schedule I) | None for offense; Gazette BNSS Act 46/2023 for procedure | Commenced 1 July 2024. Verified against Gazette Act 45/2023. |
| 13 | `BNS_2023_S351` | BNS § 351 (Criminal intimidation) | **YES** (Substantive) | Provisional only (Schedule I) | None for offense; Gazette BNSS Act 46/2023 for procedure | Commenced 1 July 2024. Verified against Gazette Act 45/2023. |
| 14 | `BNS_2023_S356` | BNS § 356 (Defamation) | **YES** (Substantive) | Provisional only (Schedule I) | None for offense; Gazette BNSS Act 46/2023 for procedure | Commenced 1 July 2024. Verified against Gazette Act 45/2023. |
| 15 | `IPC_1860_S354C` | IPC § 354C (Voyeurism) | **NO** | **NO** | India Code (Act No. 45 of 1860) | Repealed 1 July 2024. Active for pre-July 2024 (Art. 20(1)). |
| 16 | `IPC_1860_S354D` | IPC § 354D (Stalking) | **NO** | **NO** | India Code (Act No. 45 of 1860) | Repealed 1 July 2024. Active for pre-July 2024 (Art. 20(1)). |
| 17 | `IPC_1860_S379` | IPC § 379 (Theft) | **NO** | **NO** | India Code (Act No. 45 of 1860) | Repealed 1 July 2024. Active for pre-July 2024 (Art. 20(1)). |
| 18 | `IPC_1860_S384` | IPC § 384 (Extortion) | **NO** | **NO** | India Code (Act No. 45 of 1860) | Repealed 1 July 2024. Active for pre-July 2024 (Art. 20(1)). |
| 19 | `IPC_1860_S406` | IPC § 406 (Criminal breach of trust) | **NO** | **NO** | India Code (Act No. 45 of 1860) | Repealed 1 July 2024. Active for pre-July 2024 (Art. 20(1)). |
| 20 | `IPC_1860_S419` | IPC § 419 (Cheating by personation) | **NO** | **NO** | India Code (Act No. 45 of 1860) | Repealed 1 July 2024. Active for pre-July 2024 (Art. 20(1)). |
| 21 | `IPC_1860_S420` | IPC § 420 (Cheating and dishonestly inducing delivery) | **NO** | **NO** | India Code (Act No. 45 of 1860) | Repealed 1 July 2024. Active for pre-July 2024 (Art. 20(1)). |
| 22 | `IPC_1860_S426` | IPC § 426 (Mischief) | **NO** | **NO** | India Code (Act No. 45 of 1860) | Repealed 1 July 2024. Active for pre-July 2024 (Art. 20(1)). |
| 23 | `IPC_1860_S465` | IPC § 465 (Forgery) | **NO** | **NO** | India Code (Act No. 45 of 1860) | Repealed 1 July 2024. Active for pre-July 2024 (Art. 20(1)). |
| 24 | `IPC_1860_S468` | IPC § 468 (Forgery for purpose of cheating) | **NO** | **NO** | India Code (Act No. 45 of 1860) | Repealed 1 July 2024. Active for pre-July 2024 (Art. 20(1)). |
| 25 | `IPC_1860_S471` | IPC § 471 (Using as genuine a forged record) | **NO** | **NO** | India Code (Act No. 45 of 1860) | Repealed 1 July 2024. Active for pre-July 2024 (Art. 20(1)). |
| 26 | `IPC_1860_S500` | IPC § 500 (Defamation) | **NO** | **NO** | India Code (Act No. 45 of 1860) | Repealed 1 July 2024. Active for pre-July 2024 (Art. 20(1)). |
| 27 | `IPC_1860_S506` | IPC § 506 (Criminal intimidation) | **NO** | **NO** | India Code (Act No. 45 of 1860) | Repealed 1 July 2024. Active for pre-July 2024 (Art. 20(1)). |
| 28 | `IPC_1860_S509` | IPC § 509 (Insulting modesty of a woman) | **NO** | **NO** | India Code (Act No. 45 of 1860) | Repealed 1 July 2024. Active for pre-July 2024 (Art. 20(1)). |
| 29 | `ITA_2000_S43` | IT Act § 43 (Penalty and compensation for damage) | **NO** | **NO** | India Code (Act No. 21 of 2000) | In force continuously (overriding effect § 81). |
| 30 | `ITA_2000_S66` | IT Act § 66 (Computer related offences) | **NO** | **NO** | India Code (Act No. 21 of 2000) | In force continuously. |
| 31 | `ITA_2000_S66B` | IT Act § 66B (Receiving stolen computer resource) | **NO** | **NO** | India Code (Act No. 21 of 2000) | In force continuously. |
| 32 | `ITA_2000_S66C` | IT Act § 66C (Identity theft) | **NO** | **NO** | India Code (Act No. 21 of 2000) | In force continuously. |
| 33 | `ITA_2000_S66D` | IT Act § 66D (Cheating by personation using computer resource) | **NO** | **NO** | India Code (Act No. 21 of 2000) | In force continuously. |
| 34 | `ITA_2000_S66E` | IT Act § 66E (Violation of bodily privacy) | **NO** | **NO** | India Code (Act No. 21 of 2000) | In force continuously. |
| 35 | `ITA_2000_S67` | IT Act § 67 (Publishing obscene information in electronic form) | **NO** | **NO** | India Code (Act No. 21 of 2000) | In force continuously. |
| 36 | `ITA_2000_S67A` | IT Act § 67A (Publishing sexually explicit act in electronic form) | **NO** | **NO** | India Code (Act No. 21 of 2000) | In force continuously. |
| 37 | `DPDP_2023_S33_PROVISIONAL` | DPDP Act § 33 (Penalties) | **NO** | **NO** | The Gazette of India (Act No. 22 of 2023) | **ENACTED BUT UNCOMMENCED**. Penalty suppressed. |

### Summary Audit Findings:
1. **Document 1 (BNS Gazette)** supports 14 of 37 provisions (the BNS criminal provisions).
2. **Document 2 (BNSS Lok Sabha Introduced Bill)** is an unenacted legislative draft bill that **cannot** substantiate final procedural schedules (Cognizability/Bailability) for any provision. All procedural guidance based on it is provisional.
3. **23 of 37 provisions** require independent official primary sources outside the two documents (14 IPC via India Code, 8 IT Act via India Code, 1 DPDP via Gazette).
4. Unsupported coverage is documented above as requiring external authoritative grounding; support is not fabricated.

---

## 9. Evaluator Compatibility & Programmatic Enforcement

### 9.1 Evaluator Dataset Schema
The current benchmark evaluator (`backend/evaluation/eval_retrieval.py`) enforces:
1. **Article 20(1) Non-Retroactivity Rule**: Fails validation if pre-July 2024 queries specify BNS provisions or post-July 2024 queries specify IPC provisions.
2. **Uncommenced Statute Quarantine**: Prevents provisional statutes (`DPDP_2023_S33_PROVISIONAL`) from being marked as `"reviewed"` ground truth.
3. **No-Match Consistency**: Enforces `expected_no_match: true` $\iff$ `relevant_provision_ids: []`.
4. **Disjunctive Equivalence in Metric Math**:
   - The evaluator computes `compute_query_metrics(retrieved_ids, relevant_ids)`.
   - If Option A (Dual / Disjunctive Equivalence) is used, storing both `BNS_2023_S78` and `IPC_1860_S354D` in a flat `relevant_provision_ids` list without disjunctive logic artificially halves Recall@5 to 0.50 when only one valid era's provision is returned.
   - **Recommendation**: To maintain mathematical fairness, undated queries must record the primary target in `relevant_provision_ids` and the accepted temporal counterpart in `equivalent_alternative_ids`, or the evaluator must support set-equivalence scoring.

---

## 10. Decisions Requiring Project-Lead or Legal Sign-Off

Before any pending annotation (`DEV_026`–`DEV_030`, `TEST_016`–`TEST_020`) is moved from `"pending"` to `"reviewed"`, the following formal decisions must be resolved by authorized human leads:

- [ ] **Decision 1: BNSS Source Upgrade Approval**
  Approve upgrading the procedural knowledge base from the draft Lok Sabha Bill to the final enacted Gazette Act No. 46 of 2023 (Bharatiya Nagarik Suraksha Sanhita, 2023) to substantiate binding procedural guidance.
- [ ] **Decision 2: Temporal Ground-Truth Policy Selection**
  Formally select between:
  - **Option A (Dual / Disjunctive Equivalence)**: Undated queries accept either BNS or IPC counterpart as valid.
  - **Option B (Era-Anchored Specification)**: Prompts are amended to state an explicit date.
  - **Option C (Documented Contemporary Convention)**: Undated queries benchmark against contemporary post-July 2024 BNS with documented disclaimers.
- [ ] **Decision 3: Special vs. General Law Hierarchy (`DEV_026`)**
  Decide whether Section 66C IT Act (Identity Theft) constitutes the exclusive target label under *lex specialis*, or whether Section 66 IT Act must be retained in multi-label ground truth.
- [ ] **Decision 4: Incomplete Facts & Gender Requirement Handling (`DEV_030`)**
  Confirm whether gender-neutral tracking narratives are annotated as provisional stalking hypotheses with clarification prompts, or classified as out-of-scope until facts are established.
- [ ] **Decision 5: Final Reviewer Identification & Blinding Sign-Off**
  Certify that Reviewer A and Reviewer B are distinct individuals who submitted independently without access to algorithmic scores or mutual responses.

---

## 11. Formal Sign-Off Block

*This formal block must be completed by the designated project leads. No pending evaluation record may be transitioned to `"reviewed"` status until this sign-off is completed.*

| Role | Name & Title | Date | Signature / Decision Record |
|---|---|---|---|
| **Legal Lead** | __________________________________________ | ____________ | [ ] APPROVED   [ ] REJECTED |
| **NLP Evaluation Lead** | __________________________________________ | ____________ | [ ] APPROVED   [ ] REJECTED |
| **Senior QA Auditor** | __________________________________________ | ____________ | [ ] APPROVED   [ ] REJECTED |

- **Official Policy Activation Status:** **PENDING HUMAN REVIEW & WRITTEN SIGN-OFF**  
- **Authorization to Update `retrieval_eval_dataset.json`:** **WITHHELD UNTIL APPROVED**  
- **Blind Benchmark Contamination Guard:** **ACTIVE & ENFORCED**
