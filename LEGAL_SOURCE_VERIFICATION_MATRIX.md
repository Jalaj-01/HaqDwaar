# LexiLaw — Comprehensive Legal-Source Verification Matrix (37 Corpus Provisions)

**Document Status:** **PENDING HUMAN LEGAL REVIEW & SIGN-OFF**  
**Audit & Engineering Role:** Legal Data Quality & Evaluation Engineer  
**Date:** October 18, 2026  
**Corpus File Audited:** [`backend/data/legal_provisions.json`](file:///g:/NLP/New/backend/data/legal_provisions.json)  
**Corpus SHA-256 Digest:** `becf1f001631bbdc301633df428b0cb541dca97fa45b1ad7cf05db8b1d0d00d0` (Preserved 100% Unmodified)  
**Total Corpus Entries:** 37 provisions  

---

## 1. Epistemic Tiers Framework

In strict adherence to project integrity standards, LexiLaw distinguishes three verification tiers:
1. `SOURCE_DISCOVERED`: The authoritative government repository (India Code handle, Gazette of India notification number, and Ministry notification) has been genuinely discovered, verified, and cataloged.
2. `TEXT_VERIFIED`: The statutory wording, section number, subsection structure, and maximum statutory penalty range in the LexiLaw corpus have been verified verbatim against the official primary legislation.
3. `HUMAN_LEGAL_REVIEW_APPROVED`: A qualified human legal professional has conducted an independent legal analysis of constituent elements, exception thresholds, and advice disclaimers, and formally signed off on the provision's use in benchmark ground truth.

*Current Status Summary:*
- All 37 provisions have achieved **`SOURCE_DISCOVERED`** and **`TEXT_VERIFIED`**.
- Zero provisions are marked **`HUMAN_LEGAL_REVIEW_APPROVED`**; all await formal human sign-off on the policy decision form.

---

## 2. Exhaustive Verification Matrix (All 37 Provisions)

### Part I: Bharatiya Nyaya Sanhita, 2023 (14 Provisions)
*Primary Authority:* **Act No. 45 of 2023**, published in *The Gazette of India, Extraordinary, Part II, Section 1, No. 62*, dated 25 December 2023.  
*India Code Handle:* [India Code /20062](https://www.indiacode.nic.in/handle/123456789/20062).  
*Commencement Authority:* Ministry of Home Affairs Notification S.O. 850(E), dated 23 February 2024 (commenced 1 July 2024, except Section 106(2)).

| # | Provision ID | Section & Title | Official Primary Source Citation | Effective Dates | Verification Tier | Procedural Classification (BNSS Act 46/2023 First Sched.) | Verified Penalty & Exceptions | Unresolved Legal Questions / Notes |
|:---|:---|:---|:---|:---|:---:|:---|:---|:---|
| 1 | `BNS_2023_S77` | S. 77 (Voyeurism) | Gazette Act 45/2023; [India Code /20062](https://www.indiacode.nic.in/handle/123456789/20062) | 2024-07-01 to Present | `TEXT_VERIFIED` | 1st: Cognizable, Bailable, Any Mag; Subseq: Cognizable, Non-bailable, Any Mag | 1st: 1–3 yrs + fine; 2nd: 3–7 yrs + fine. Limiting element: Female victim, expectation of privacy. | Replaces IPC 354C. Applies where woman consented to capture but not dissemination. |
| 2 | `BNS_2023_S78` | S. 78 (Stalking) | Gazette Act 45/2023; [India Code /20062](https://www.indiacode.nic.in/handle/123456789/20062) | 2024-07-01 to Present | `TEXT_VERIFIED` | 1st: Cognizable, Bailable, Any Mag; Subseq: Cognizable, Non-bailable, Any Mag | 1st: up to 3 yrs + fine; 2nd: up to 5 yrs + fine. Limiting element: Male perpetrator, female victim. | Replaces IPC 354D. Gender-neutral stalking narratives (`DEV_030`) require clarification. |
| 3 | `BNS_2023_S79` | S. 79 (Insulting modesty of a woman) | Gazette Act 45/2023; [India Code /20062](https://www.indiacode.nic.in/handle/123456789/20062) | 2024-07-01 to Present | `TEXT_VERIFIED` | Cognizable, Bailable, Any Mag | Simple impr. up to 3 yrs + fine. Limiting element: Intention to insult modesty of a woman. | Replaces IPC 509. Frequently co-occurring in cyber trolling/harassment complaints. |
| 4 | `BNS_2023_S106_SUB2_UNCOMMENCED` | S. 106(2) (Fatal hit-and-run) | Gazette Act 45/2023; MHA Notif. S.O. 850(E) | **UNCOMMENCED** | `TEXT_VERIFIED` (Statutory text) | Enacted in Sched. I as Cognizable, Non-bailable, Mag. 1st Class | Up to 10 yrs + fine (**UNCOMMENCED**). | **IN ABEYANCE**: Excluded from commencement by S.O. 850(E). Penalty strictly suppressed. Active law is BNS 106(1). |
| 5 | `BNS_2023_S303` | S. 303 (Theft) | Gazette Act 45/2023; [India Code /20062](https://www.indiacode.nic.in/handle/123456789/20062) | 2024-07-01 to Present | `TEXT_VERIFIED` | Petty (<₹5k): Non-cog, Bailable, Any Mag; General: Cog, Non-bailable, Any Mag | Impr. up to 3 yrs, or fine, or both. Proviso introduces community service for petty theft (< ₹5,000). | Replaces IPC 379. Community service is a newly introduced statutory sentencing alternative. |
| 6 | `BNS_2023_S308` | S. 308 (Extortion) | Gazette Act 45/2023; [India Code /20062](https://www.indiacode.nic.in/handle/123456789/20062) | 2024-07-01 to Present | `TEXT_VERIFIED` | Cognizable, Non-bailable, Mag. 1st Class | Impr. up to 7 yrs, or fine, or both. Limiting element: Delivery of property induced by fear. | **MAJOR PENALTY ESCALATION**: Enhanced from 3 yrs (IPC 384) to 7 yrs. Article 20(1) bars retroactive use. |
| 7 | `BNS_2023_S316` | S. 316 (Criminal breach of trust) | Gazette Act 45/2023; [India Code /20062](https://www.indiacode.nic.in/handle/123456789/20062) | 2024-07-01 to Present | `TEXT_VERIFIED` | Cognizable, Non-bailable, Mag. 1st Class | Impr. up to 5 yrs, or fine, or both. Limiting element: Dishonest misappropriation of entrusted property. | Enhanced from 3 yrs (IPC 406) to 5 yrs. Consolidates IPC 405–409. |
| 8 | `BNS_2023_S318` | S. 318 (Cheating) | Gazette Act 45/2023; [India Code /20062](https://www.indiacode.nic.in/handle/123456789/20062) | 2024-07-01 to Present | `TEXT_VERIFIED` | Simple: Cog, Bailable; Delivery (sub-4): Cog, Non-bailable, Mag. 1st Class | Simple cheating: up to 3 yrs; Cheating with delivery (sub-4): up to 7 yrs + fine. | Consolidates IPC 415, 417, and 420. Mere contract breach without fraudulent inception is civil. |
| 9 | `BNS_2023_S319` | S. 319 (Cheating by personation) | Gazette Act 45/2023; [India Code /20062](https://www.indiacode.nic.in/handle/123456789/20062) | 2024-07-01 to Present | `TEXT_VERIFIED` | Cognizable, Bailable, Mag. 1st Class | Impr. up to 5 yrs, or fine, or both. Explanation: person personated may be real or imaginary. | Enhanced from 3 yrs (IPC 419) to 5 yrs. Inapplicable to pre-July 2024 scams under Art. 20(1). |
| 10 | `BNS_2023_S324` | S. 324 (Mischief) | Gazette Act 45/2023; [India Code /20062](https://www.indiacode.nic.in/handle/123456789/20062) | 2024-07-01 to Present | `TEXT_VERIFIED` | Non-cognizable, Bailable, Any Mag | Basic: up to 6 months, or fine, or both. Graded damages: ₹20k–₹1L (up to 1 yr); >₹1L (up to 2 yrs). | Replaces IPC 426 (which had 3-month basic penalty). Enhanced penalty cannot apply pre-July 2024. |
| 11 | `BNS_2023_S336` | S. 336 (Forgery) | Gazette Act 45/2023; [India Code /20062](https://www.indiacode.nic.in/handle/123456789/20062) | 2024-07-01 to Present | `TEXT_VERIFIED` | General: Non-cog, Bailable; Cheating (sub-3): Cog, Non-bailable, Mag. 1st Class | General: up to 2 yrs; Cheating intent (sub-3): up to 7 yrs + fine. | Consolidates IPC 463, 465, and 468. |
| 12 | `BNS_2023_S340` | S. 340 (Using forged record) | Gazette Act 45/2023; [India Code /20062](https://www.indiacode.nic.in/handle/123456789/20062) | 2024-07-01 to Present | `TEXT_VERIFIED` | Cognizable, Non-bailable, Mag. 1st Class | Punished in same manner as if offender had forged such document or electronic record. | Corresponds directly to IPC 471. |
| 13 | `BNS_2023_S351` | S. 351 (Criminal intimidation) | Gazette Act 45/2023; [India Code /20062](https://www.indiacode.nic.in/handle/123456789/20062) | 2024-07-01 to Present | `TEXT_VERIFIED` | General: Non-cog, Bailable; Death threat: Cog, Non-bailable, Mag. 1st Class | General (sub-2): up to 2 yrs, or fine, or both; Threat of death/grievous hurt (sub-3): up to 7 yrs. | Corresponds to IPC 503/506. Lawful legal notices sent in good faith do not constitute intimidation. |
| 14 | `BNS_2023_S356` | S. 356 (Defamation) | Gazette Act 45/2023; [India Code /20062](https://www.indiacode.nic.in/handle/123456789/20062) | 2024-07-01 to Present | `TEXT_VERIFIED` | Non-cognizable, Bailable, Mag. 1st Class / Court of Session | Simple impr. up to 2 yrs, or fine, or both, or with community service. | Replaces IPC 500. Retains statutory exceptions (truth for public good, fair criticism). |

---

### Part II: Indian Penal Code, 1860 (14 Historical Benchmark Provisions)
*Primary Authority:* **Act No. 45 of 1860**, Legislative Department, Ministry of Law and Justice, Government of India.  
*India Code Handle:* [India Code /2263](https://www.indiacode.nic.in/handle/123456789/2263).  
*Status:* Repealed 1 July 2024; actively applicable to pre-July 2024 conduct under Section 358(2) BNS savings and Article 20(1) Constitution of India.

| # | Provision ID | Section & Title | Official Primary Source Citation | Effective Dates | Verification Tier | Procedural Classification (CrPC 1973 Sched. I) | Verified Penalty & Exceptions | Modern BNS Counterpart |
|:---|:---|:---|:---|:---|:---:|:---|:---|:---|
| 15 | `IPC_1860_S354C` | S. 354C (Voyeurism) | Act 45/1860; [India Code /2263](https://www.indiacode.nic.in/handle/123456789/2263) (Ins. Act 13 of 2013) | 2013-02-03 to 2024-06-30 | `TEXT_VERIFIED` | 1st: Cog, Bailable; Subseq: Cog, Non-bailable | 1st: 1–3 yrs + fine; 2nd: 3–7 yrs + fine. | Replaced by BNS Section 77. |
| 16 | `IPC_1860_S354D` | S. 354D (Stalking) | Act 45/1860; [India Code /2263](https://www.indiacode.nic.in/handle/123456789/2263) (Ins. Act 13 of 2013) | 2013-02-03 to 2024-06-30 | `TEXT_VERIFIED` | 1st: Cog, Bailable; Subseq: Cog, Non-bailable | 1st: up to 3 yrs + fine; 2nd: up to 5 yrs + fine. | Replaced by BNS Section 78. |
| 17 | `IPC_1860_S379` | S. 379 (Theft) | Act 45/1860; [India Code /2263](https://www.indiacode.nic.in/handle/123456789/2263) | 1862-01-01 to 2024-06-30 | `TEXT_VERIFIED` | Cognizable, Non-bailable, Any Mag | Impr. up to 3 yrs, or fine, or both. | Replaced by BNS Section 303(2). |
| 18 | `IPC_1860_S384` | S. 384 (Extortion) | Act 45/1860; [India Code /2263](https://www.indiacode.nic.in/handle/123456789/2263) | 1862-01-01 to 2024-06-30 | `TEXT_VERIFIED` | Cognizable, Non-bailable, Mag. 1st Class | Impr. up to 3 yrs, or fine, or both. | Replaced by BNS Section 308(2) (which escalated to 7 yrs). |
| 19 | `IPC_1860_S406` | S. 406 (Criminal breach of trust) | Act 45/1860; [India Code /2263](https://www.indiacode.nic.in/handle/123456789/2263) | 1862-01-01 to 2024-06-30 | `TEXT_VERIFIED` | Cognizable, Non-bailable, Mag. 1st Class | Impr. up to 3 yrs, or fine, or both. | Replaced by BNS Section 316(2) (escalated to 5 yrs). |
| 20 | `IPC_1860_S419` | S. 419 (Cheating by personation) | Act 45/1860; [India Code /2263](https://www.indiacode.nic.in/handle/123456789/2263) | 1862-01-01 to 2024-06-30 | `TEXT_VERIFIED` | Cognizable, Bailable, Any Mag | Impr. up to 3 yrs, or fine, or both. | Replaced by BNS Section 319(2) (escalated to 5 yrs). |
| 21 | `IPC_1860_S420` | S. 420 (Cheating & property delivery) | Act 45/1860; [India Code /2263](https://www.indiacode.nic.in/handle/123456789/2263) | 1862-01-01 to 2024-06-30 | `TEXT_VERIFIED` | Cognizable, Non-bailable, Mag. 1st Class | Impr. up to 7 yrs, and liable to fine. | Replaced by BNS Section 318(4). |
| 22 | `IPC_1860_S426` | S. 426 (Mischief) | Act 45/1860; [India Code /2263](https://www.indiacode.nic.in/handle/123456789/2263) | 1862-01-01 to 2024-06-30 | `TEXT_VERIFIED` | Non-cognizable, Bailable, Any Mag | Impr. up to 3 months, or fine, or both. | Replaced by BNS Section 324(2) (doubled to 6 months). |
| 23 | `IPC_1860_S465` | S. 465 (Forgery) | Act 45/1860; [India Code /2263](https://www.indiacode.nic.in/handle/123456789/2263) | 1862-01-01 to 2024-06-30 | `TEXT_VERIFIED` | Non-cognizable, Bailable, Mag. 1st Class | Impr. up to 2 yrs, or fine, or both. | Replaced by BNS Section 336(2). |
| 24 | `IPC_1860_S468` | S. 468 (Forgery for cheating) | Act 45/1860; [India Code /2263](https://www.indiacode.nic.in/handle/123456789/2263) | 1862-01-01 to 2024-06-30 | `TEXT_VERIFIED` | Cognizable, Non-bailable, Mag. 1st Class | Impr. up to 7 yrs, and liable to fine. | Replaced by BNS Section 336(3). |
| 25 | `IPC_1860_S471` | S. 471 (Using forged record) | Act 45/1860; [India Code /2263](https://www.indiacode.nic.in/handle/123456789/2263) | 1862-01-01 to 2024-06-30 | `TEXT_VERIFIED` | Cognizable, Non-bailable, Mag. 1st Class | Punished in same manner as if offender forged document. | Replaced by BNS Section 340. |
| 26 | `IPC_1860_S500` | S. 500 (Defamation) | Act 45/1860; [India Code /2263](https://www.indiacode.nic.in/handle/123456789/2263) | 1862-01-01 to 2024-06-30 | `TEXT_VERIFIED` | Non-cognizable, Bailable, Mag. 1st Class | Simple impr. up to 2 yrs, or fine, or both. | Replaced by BNS Section 356(2). |
| 27 | `IPC_1860_S506` | S. 506 (Criminal intimidation) | Act 45/1860; [India Code /2263](https://www.indiacode.nic.in/handle/123456789/2263) | 1862-01-01 to 2024-06-30 | `TEXT_VERIFIED` | Part 1: Non-cog, Bailable; Part 2: Cog, Non-bailable | Part 1: up to 2 yrs; Part 2 (death threat): up to 7 yrs. | Replaced by BNS Section 351(2) and (3). |
| 28 | `IPC_1860_S509` | S. 509 (Insulting modesty of woman) | Act 45/1860; [India Code /2263](https://www.indiacode.nic.in/handle/123456789/2263) | 1862-01-01 to 2024-06-30 | `TEXT_VERIFIED` | Cognizable, Bailable, Any Mag | Simple impr. up to 3 yrs, and with fine. | Replaced by BNS Section 79. |

---

### Part III: Information Technology Act, 2000 (8 Continuous Provisions)
*Primary Authority:* **Act No. 21 of 2000**, as amended by Act No. 10 of 2009. Legislative Department, Ministry of Law and Justice.  
*India Code Handle:* [India Code /1999](https://www.indiacode.nic.in/handle/123456789/1999).  
*Status:* In force continuously (overriding effect under Section 81 non-obstante clause).

| # | Provision ID | Section & Title | Official Primary Source Citation | Effective Dates | Verification Tier | Procedural Classification (IT Act S. 77B) | Verified Penalty & Exceptions | Legal Scope Notes |
|:---|:---|:---|:---|:---|:---:|:---|:---|:---|
| 29 | `ITA_2000_S43` | S. 43 (Computer damage & compensation) | Act 21/2000; [India Code /1999](https://www.indiacode.nic.in/handle/123456789/1999) | 2000-10-17 to Present | `TEXT_VERIFIED` | Civil regulatory adjudication | Statutory compensation to person affected. Excludes authorized diagnostic testing. | Civil compensation remedy before Adjudicating Officer; not a criminal offense unless coupled with S. 66. |
| 30 | `ITA_2000_S66` | S. 66 (Computer related offences) | Act 10/2009; [India Code /1999](https://www.indiacode.nic.in/handle/123456789/1999) | 2009-10-27 to Present | `TEXT_VERIFIED` | Cognizable, Bailable | Impr. up to 3 yrs, or fine up to ₹5 lakh, or both. Requires mens rea (*dishonestly/fraudulently*). | Core hacking statute; converts S. 43 acts into criminal offenses. |
| 31 | `ITA_2000_S66B` | S. 66B (Receiving stolen computer resource) | Act 10/2009; [India Code /1999](https://www.indiacode.nic.in/handle/123456789/1999) | 2009-10-27 to Present | `TEXT_VERIFIED` | Cognizable, Bailable | Impr. up to 3 yrs, or fine up to ₹1 lakh, or both. | High false-positive trigger for physical device theft. |
| 32 | `ITA_2000_S66C` | S. 66C (Identity theft) | Act 10/2009; [India Code /1999](https://www.indiacode.nic.in/handle/123456789/1999) | 2009-10-27 to Present | `TEXT_VERIFIED` | Cognizable, Bailable | Impr. up to 3 yrs, and liable to fine up to ₹1 lakh. | Specific provision (*lex specialis*) for password, OTP, and digital signature theft. |
| 33 | `ITA_2000_S66D` | S. 66D (Cheating by personation) | Act 10/2009; [India Code /1999](https://www.indiacode.nic.in/handle/123456789/1999) | 2009-10-27 to Present | `TEXT_VERIFIED` | Cognizable, Bailable | Impr. up to 3 yrs, and liable to fine up to ₹1 lakh. | Phishing and scam profiles. Requires cheating + computer resource. |
| 34 | `ITA_2000_S66E` | S. 66E (Bodily privacy violation) | Act 10/2009; [India Code /1999](https://www.indiacode.nic.in/handle/123456789/1999) | 2009-10-27 to Present | `TEXT_VERIFIED` | Cognizable, Bailable | Impr. up to 3 yrs, or fine up to ₹2 lakh, or both. | Strictly limited to capturing/transmitting images of intimate body parts. Public street photography excluded. |
| 35 | `ITA_2000_S67` | S. 67 (Publishing obscene material) | Act 10/2009; [India Code /1999](https://www.indiacode.nic.in/handle/123456789/1999) | 2000-10-17 to Present | `TEXT_VERIFIED` | 1st: Cog, Bailable; 2nd: Cog, Non-bailable | 1st: up to 3 yrs + fine ₹5L; 2nd: up to 5 yrs + fine ₹10L. Excludes publications for public good/art/science. | Under *Sharat Babu Digumarti* (2017), ITA 67 overrides general penal obscenity. |
| 36 | `ITA_2000_S67A` | S. 67A (Sexually explicit material) | Act 10/2009; [India Code /1999](https://www.indiacode.nic.in/handle/123456789/1999) | 2009-10-27 to Present | `TEXT_VERIFIED` | 1st: Cog, Non-bailable; 2nd: Cog, Non-bailable | 1st: up to 5 yrs + fine ₹10L; 2nd: up to 7 yrs + fine ₹10L. | Explicit act requirement distinguishes from S. 67 obscenity. |

---

### Part IV: Digital Personal Data Protection Act, 2023 (1 Provisional Provision)
*Primary Authority:* **Act No. 22 of 2023**, Ministry of Law and Justice / MeitY. Published in *The Gazette of India, Extraordinary, Part II, Section 1, No. 22*, dated 11 August 2023.  
*India Code Handle:* [India Code /21415](https://www.indiacode.nic.in/handle/123456789/21415).  
*Status:* **Enacted but Uncommenced / Provisional**. Data Protection Board of India inquiry and penalty adjudication regulations remain unnotified.

| # | Provision ID | Section & Title | Official Primary Source Citation | Effective Dates | Verification Tier | Procedural Classification | Verified Penalty & Exceptions | Status & Safeguards |
|:---|:---|:---|:---|:---|:---:|:---|:---|:---|
| 37 | `DPDP_2023_S33_PROVISIONAL` | S. 33 (Penalties) | Gazette Act 22/2023; [India Code /21415](https://www.indiacode.nic.in/handle/123456789/21415) | None (Uncommenced) | `TEXT_VERIFIED` (Statutory text) | Civil administrative penalty before Data Protection Board of India | Civil monetary penalty up to ₹250 crore for significant security breach. (**UNCOMMENCED**). | Penalty suppressed in UI; excluded from standard cyber retrieval. |

---

## 3. Discrepancy & Proposed Corpus Correction List (Submitted for Human Review)

In accordance with strict integrity instructions, `backend/data/legal_provisions.json` has **NOT** been modified. The following two corrections are formally submitted for legal review:

1. **Proposed Addition: BNS Section 106(1) (Active Rash Driving Fatalities)**:
   - *Current Gap*: The corpus contains `BNS_2023_S106_SUB2_UNCOMMENCED` (held in abeyance), but lacks Section 106(1) (the active, commenced law carrying up to 5 years imprisonment).
   - *Action Required*: Draft provision `BNS_2023_S106_SUB1` prepared for ingestion upon human sign-off.
2. **Proposed Metadata Update: Official Source URLs**:
   - *Current Gap*: In `backend/data/legal_provisions.json`, `source_url` is currently `null` for the 23 non-BNS provisions.
   - *Action Required*: Update `source_url` with the verified India Code handles cataloged above, pending approval by the Legal Lead.
