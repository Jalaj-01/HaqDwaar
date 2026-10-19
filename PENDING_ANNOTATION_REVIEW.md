# LexiLaw Phase 5 — Pending Annotation Review Dossier

**Audit & Review Date:** October 16, 2026  
**Auditor / Engineering Role:** Senior NLP Evaluation Auditor & Legal Data QA Engineer  
**Workspace:** `g:\NLP\New`  
**Dataset Inspected:** `backend/evaluation/retrieval_eval_dataset.json` (50 total records)  
**Target Records:** 10 quarantined draft queries (`DEV_026`–`DEV_030` and `TEST_016`–`TEST_020`)  
**Operating Retrieval Threshold:** $\tau = 0.12$ (Frozen)  
**Current Record Status:** **ALL 10 TARGET RECORDS REMAIN IN PENDING STATUS**  
**Independent Review Status:** **NOT YET COMPLETED — AWAITING HUMAN EXPERT ADJUDICATION**  
**Benchmark Claim Status:** **NO FINAL BENCHMARK MAY BE CLAIMED OR EXECUTED**

---

## 1. Executive Summary & Review Scope

This dossier establishes the formal legal review framework and methodological instructions for the ten (10) draft evaluation records in [`backend/evaluation/retrieval_eval_dataset.json`](file:///g:/NLP/New/backend/evaluation/retrieval_eval_dataset.json) that remain in `"pending"` status.

### Critical Integrity Commitments:
1. **Zero Automated Label Assignment**: No provision IDs have been automatically assigned, no draft labels have been approved, no annotation statuses have been converted to `"reviewed"`, and no reviewer decisions or votes have been fabricated.
2. **Preservation of Evaluation State**: The primary dataset, benchmark manifest, corpus fingerprint (`becf1f001631bbdc301633df428b0cb541dca97fa45b1ad7cf05db8b1d0d00d0`), and operating retrieval threshold ($\tau = 0.12$) remain preserved and unmodified.
3. **Explicit Separation of Responsibilities**:
   - **Automated Checks**: Provide objective lexical/semantic similarity scores, candidate rankings, and threshold comparisons against the active 37-provision production index.
   - **Human Legal Judgment**: Evaluates statutory interpretation, legislative intent, mens rea thresholds, special vs. general act boundaries, and constitutional non-retroactivity under Article 20(1).
4. **Provisional Hypotheses Only**: All legal analyses, statutory interpretations, and provision suggestions in this document are strictly provisional hypotheses for human reviewer consideration, not binding conclusions.
5. **No Final Benchmark Claim**: Until independent reviews are conducted, documented, and locked by authorized human legal reviewers, no blind benchmark or final evaluation claim can be reported.

---

## 2. Master Review Table for Pending Records

The table below outlines the review status across all 10 pending cases. In strict adherence to integrity protocols, Reviewer 1, Reviewer 2, Disagreement, and Adjudication fields represent the formal review structure awaiting human completion:

| Query ID | Split | Category | Query Narrative | Draft Candidate Labels | Reviewer 1 Assessment | Reviewer 2 Assessment | Disagreement & Legal Tension | Senior Adjudication | Current Status |
|---|---|---|---|---|---|---|---|---|---|
| **`DEV_026`** | `dev` | `cyber_identity_theft` | Stolen email credentials used to send offensive emails | `['ITA_2000_S66C', 'ITA_2000_S66']` | *Awaiting Human Review* | *Awaiting Human Review* | Specific identity theft (66C) vs. general computer offense (66); personation (66D); defamation/insult content. | *Pending Adjudication* | **PENDING** |
| **`DEV_027`** | `dev` | `out_of_scope_no_match` | Counterfeit branded handbags mimicking trademark logo | `[]` (`expected_no_match: true`) | *Awaiting Human Review* | *Awaiting Human Review* | Trade Marks Act 1999 (out of scope) vs. potential consumer cheating (BNS 318) / forgery (BNS 336). | *Pending Adjudication* | **PENDING** |
| **`DEV_028`** | `dev` | `criminal_intimidation` | Threatening to leak private photos unless police complaint withdrawn | `['BNS_2023_S351']` | *Awaiting Human Review* | *Awaiting Human Review* | Criminal intimidation (BNS 351) vs. extortion (BNS 308) without property delivery; inchoate privacy (ITA 66E). | *Pending Adjudication* | **PENDING** |
| **`DEV_029`** | `dev` | `out_of_scope_no_match` | Recording conversation in a restaurant without informing attendees | `[]` (`expected_no_match: true`) | *Awaiting Human Review* | *Awaiting Human Review* | Bodily privacy under Section 66E IT Act / BNS 77 vs. non-criminal audio recording in public dining. | *Pending Adjudication* | **PENDING** |
| **`DEV_030`** | `dev` | `stalking` | GPS magnetic tracker placed under vehicle to monitor movements | `['BNS_2023_S78']` | *Awaiting Human Review* | *Awaiting Human Review* | Statutory gender requirement (man tracking woman) vs. gender-neutral narrative; trespass/mischief. | *Pending Adjudication* | **PENDING** |
| **`TEST_016`** | `test` | `unauthorized_access` | Unauthorized party guessed Wi-Fi router password and used broadband | `['ITA_2000_S43']` | *Awaiting Human Review* | *Awaiting Human Review* | Civil compensation (ITA 43) vs. criminal hacking (ITA 66) without tangible damage; identity theft (ITA 66C). | *Pending Adjudication* | **PENDING** |
| **`TEST_017`** | `test` | `financial_fraud` | December 2023 accountant fund embezzlement via forged invoices | `['IPC_1860_S420']` | *Awaiting Human Review* | *Awaiting Human Review* | Pre-BNS temporal regime (Article 20(1)); expanded IPC corpus provisions (IPC 468, 471, 406). | *Pending Adjudication* | **PENDING** |
| **`TEST_018`** | `test` | `out_of_scope_no_match` | Taking photographs of company storefront from public street sidewalk | `[]` (`expected_no_match: true`) | *Awaiting Human Review* | *Awaiting Human Review* | Lawful public photography (Art. 19(1)(a)) vs. false positive voyeurism/privacy keyword triggers. | *Pending Adjudication* | **PENDING** |
| **`TEST_019`** | `test` | `out_of_scope_no_match` | Parody account on social media clearly labeled as satire of celebrity | `[]` (`expected_no_match: true`) | *Awaiting Human Review* | *Awaiting Human Review* | Absence of fraudulent intent in labeled satire vs. cheating by personation (66D IT Act / 319 BNS). | *Pending Adjudication* | **PENDING** |
| **`TEST_020`** | `test` | `stalking` | Man sent 50 unsolicited romantic poems to coworker despite refusal | `['BNS_2023_S78']` | *Awaiting Human Review* | *Awaiting Human Review* | Criminal stalking (BNS 78) vs. workplace POSH Act 2013 civil remedies; insult to modesty (BNS 79). | *Pending Adjudication* | **PENDING** |

---

## 3. Detailed Query Review Dossiers

### Query 1: `DEV_026`

#### 1. Query Metadata & Verbatim Narrative
- **Query ID**: `DEV_026`
- **Partition**: `dev`
- **Category**: `cyber_identity_theft`
- **Verbatim Text**:
  > *"Someone logged into my work email account using stolen credentials and sent offensive emails to our leadership team."*

#### 2. Draft Candidate Labels in Repository (Pending Human Review)
- **Draft Candidate Provisions**: `["ITA_2000_S66C", "ITA_2000_S66"]`
- **Draft Expected No-Match**: `false`
- **Draft Rationale Recorded**: *"Use of stolen login credentials (66C) and unauthorized computer access/tampering (66) IT Act."*
- **Reviewer Notes in Dataset**: *"Needs confirmation on whether 66 alone or 66C+66 is the primary expectation."*
- **Annotation Status**: `pending`

#### 3. Automated Retrieval Pipeline Candidates ($\tau \ge 0.05$)
Retrieved candidates against the active 37-provision production corpus:
1. `ITA_2000_S66D` (Cheating by personation using computer resource) — **Relevance: 0.3142** (Lexical: 0.1525, Semantic: 0.4219) `[EXCEEDS TAU=0.12]`
2. `ITA_2000_S66B` (Receiving stolen computer resource) — **Relevance: 0.2535** (Lexical: 0.0995, Semantic: 0.3562) `[EXCEEDS TAU=0.12]`
3. `ITA_2000_S66C` (Punishment for identity theft) — **Relevance: 0.2525** (Lexical: 0.0747, Semantic: 0.3710) `[EXCEEDS TAU=0.12]`
4. `ITA_2000_S66` (Computer related offences) — **Relevance: 0.2146** (Lexical: 0.0000, Semantic: 0.3576) `[EXCEEDS TAU=0.12]`
5. `ITA_2000_S43` (Damage to computer system) — **Relevance: 0.2116** (Lexical: 0.0264, Semantic: 0.3350) `[EXCEEDS TAU=0.12]`

#### 4. Legal Analysis Framework
- **Facts in the Narrative**:
  - The victim's work email account was accessed by an unauthorized individual.
  - The access was achieved using stolen credentials (password/login information).
  - The intruder sent emails described as "offensive" to the leadership team.
  - No financial transaction, extortion demand, or specific text of the emails is disclosed.
- **Statutory Elements to Verify**:
  - *Section 66C IT Act*: Requires fraudulent or dishonest use of electronic signature, password, or any other unique identification feature of any other person.
  - *Section 66 IT Act*: Requires committing any act referred to in Section 43 dishonestly or fraudulently.
  - *Section 66D IT Act*: Requires cheating by personation by means of any communication device or computer resource.
- **Provisional Legal Hypotheses (Requiring Review)**:
  - *Hypothesis 1*: Section 66C is the primary specific offense (*lex specialis*) penalizing password theft and unauthorized credential usage.
  - *Hypothesis 2*: Section 66 is an umbrella offense that operates co-extensively with Section 66C or is absorbed by the specific identity theft charge.
  - *Hypothesis 3*: Section 66D may or may not apply depending on whether sending emails in another's name without commercial cheating satisfies personation under Indian law.
- **Unresolved Legal Questions Requiring Human Adjudication**:
  1. Under the doctrine *generalia specialibus non derogant*, does Section 66C represent the exclusive target label, or should Section 66 be retained as a co-primary target?
  2. Does impersonating an employee to send offensive messages satisfy the ingredients of *Cheating by Personation* under Section 66D IT Act in the absence of property inducement or tangible deception?
  3. Should offensive emails sent to leadership trigger defamation provisions (Section 356 BNS / Section 499 IPC) or insult to modesty (Section 79 BNS / Section 509 IPC), or are those provisions excluded due to lack of factual specifics?
  4. Should the evaluation ground truth accept a single label (`ITA_2000_S66C`) or a multi-label set (`ITA_2000_S66C` and `ITA_2000_S66`)?

#### 5. Temporal Ambiguity & Statutory Applicability
- **Temporal Ambiguity Flagged**: The prompt contains no date of occurrence.
- **Statutory Applicability**: The Information Technology Act, 2000 remains applicable irrespective of the IPC-to-BNS transition. However, if ancillary penal provisions (defamation, insult) are considered, temporal applicability depends on whether the act occurred before or after July 1, 2024. Reviewers must apply the project's documented temporal policy.

#### 6. Candidate Authoritative Citations for Reviewer Verification
> *[CANDIDATE CITATION — MUST BE INDEPENDENTLY VERIFIED BY REVIEWER ON INDIA CODE / OFFICIAL JUDGMENT REPOSITORIES]*
- Information Technology Act, 2000 (Act No. 21 of 2000), Sections 43, 66, 66C, 66D. India Code: `https://www.indiacode.nic.in/handle/123456789/1999`
- *Sharat Babu Digumarti v. Government of NCT of Delhi* (2017) 2 SCC 18 (Candidate ruling on the overriding effect of special IT Act provisions over general penal provisions under Section 81 IT Act).

#### 7. Standardized Independent Review Form
```
[ ] Reviewer 1: ____________________________ Date: ____________ Confidence: [ ] High [ ] Med [ ] Low
    Target Provisions: [ ] ITA_S66C only   [ ] ITA_S66C + ITA_S66   [ ] ITA_S66D included   [ ] Other: _______
    Rationale & Citations: _________________________________________________________________________________
[ ] Reviewer 2: ____________________________ Date: ____________ Confidence: [ ] High [ ] Med [ ] Low
    Target Provisions: [ ] ITA_S66C only   [ ] ITA_S66C + ITA_S66   [ ] ITA_S66D included   [ ] Other: _______
    Rationale & Citations: _________________________________________________________________________________
[ ] Disagreement Resolution / Adjudication:
    Adjudicator: ___________________________ Determination: ___________________ Date: ____________
    Final Approved Labels: _________________________________________________ Status: [ ] PENDING [ ] REVIEWED
```

---

### Query 2: `DEV_027`

#### 1. Query Metadata & Verbatim Narrative
- **Query ID**: `DEV_027`
- **Partition**: `dev`
- **Category**: `out_of_scope_no_match`
- **Verbatim Text**:
  > *"A vendor manufactured counterfeit branded handbags mimicking our registered trademark logo."*

#### 2. Draft Candidate Labels in Repository (Pending Human Review)
- **Draft Candidate Provisions**: `[]`
- **Draft Expected No-Match**: `true`
- **Draft Rationale Recorded**: *"Trademark infringement under Trade Marks Act, 1999 is outside indexed penal and cyber provisions."*
- **Reviewer Notes in Dataset**: *"Intellectual property infringement out of scope; verify if cheating (318 BNS) could arguably apply."*
- **Annotation Status**: `pending`

#### 3. Automated Retrieval Pipeline Candidates ($\tau \ge 0.05$)
Retrieved candidates against the active 37-provision production corpus:
1. `BNS_2023_S340` (Using forged document/record as genuine) — **Relevance: 0.1619** `[EXCEEDS TAU=0.12]`
2. `BNS_2023_S336` (Forgery) — **Relevance: 0.1238** `[EXCEEDS TAU=0.12]`
3. `IPC_1860_S471` (Using as genuine forged document) — **Relevance: 0.1238** `[EXCEEDS TAU=0.12]`
4. `ITA_2000_S66C` (Identity theft) — **Relevance: 0.1020** `[BELOW TAU=0.12]`
5. `IPC_1860_S468` (Forgery for purpose of cheating) — **Relevance: 0.0918** `[BELOW TAU=0.12]`

#### 4. Legal Analysis Framework
- **Facts in the Narrative**:
  - A commercial vendor manufactured physical handbags.
  - The handbags copied or mimicked a registered trademark logo.
  - The narrative does not describe a sale transaction, deception of an individual buyer, or an electronic/cyber component.
- **Statutory Elements to Verify**:
  - *Trade Marks Act, 1999 (Sections 102, 103)*: Penalizes applying false trademarks or trade descriptions.
  - *BNS 2023 Section 318 / IPC 1860 Section 415 (Cheating)*: Requires fraudulent or dishonest deception inducing delivery of property.
  - *BNS 2023 Section 336 / IPC 1860 Section 463 (Forgery)*: Requires making a false document or electronic record.
- **Provisional Legal Hypotheses (Requiring Review)**:
  - *Hypothesis 1*: Counterfeiting physical goods is an intellectual property offense governed by the Trade Marks Act, 1999, which is outside the indexed corpus, making this a true negative (`expected_no_match: true`).
  - *Hypothesis 2*: Without a specified victim who purchased the counterfeit goods under deception, general penal cheating does not arise on the stated facts.
- **Unresolved Legal Questions Requiring Human Adjudication**:
  1. Does commercial manufacturing of goods bearing a counterfeit trademark fall under special IP legislation exclusively, or can general penal provisions (BNS 318 / IPC 420) apply concurrently?
  2. Does placing a fake logo on physical leather goods constitute making a "false document" under Section 336 BNS, or is it strictly an infringement of a property mark?
  3. Should this record be affirmed as a true negative (`expected_no_match: true`) to test the retriever's ability to refrain from retrieving forgery provisions?

#### 5. Temporal Ambiguity & Statutory Applicability
- **Temporal Ambiguity Flagged**: No date of occurrence is specified.
- **Statutory Applicability**: The Trade Marks Act, 1999 has remained in force continuously. If penal provisions are considered, temporal ambiguity between IPC and BNS must be resolved via the project's temporal policy.

#### 6. Candidate Authoritative Citations for Reviewer Verification
> *[CANDIDATE CITATION — MUST BE INDEPENDENTLY VERIFIED BY REVIEWER ON INDIA CODE / OFFICIAL JUDGMENT REPOSITORIES]*
- Trade Marks Act, 1999 (Act No. 47 of 1999), Sections 102, 103, 104. India Code: `https://www.indiacode.nic.in/handle/123456789/1993`
- *State of U.P. v. Ranjit Singh* (1999) 2 SCC 617 (Candidate ruling distinguishing trademark infringement from penal offenses of forgery and cheating).

#### 7. Standardized Independent Review Form
```
[ ] Reviewer 1: ____________________________ Date: ____________ Confidence: [ ] High [ ] Med [ ] Low
    Classification: [ ] TRUE NEGATIVE (Out of scope)   [ ] BNS 318 / IPC 420   [ ] Other: _______
    Rationale & Citations: _________________________________________________________________________________
[ ] Reviewer 2: ____________________________ Date: ____________ Confidence: [ ] High [ ] Med [ ] Low
    Classification: [ ] TRUE NEGATIVE (Out of scope)   [ ] BNS 318 / IPC 420   [ ] Other: _______
    Rationale & Citations: _________________________________________________________________________________
[ ] Disagreement Resolution / Adjudication:
    Adjudicator: ___________________________ Determination: ___________________ Date: ____________
    Final Approved Labels: _________________________________________________ Status: [ ] PENDING [ ] REVIEWED
```

---

### Query 3: `DEV_028`

#### 1. Query Metadata & Verbatim Narrative
- **Query ID**: `DEV_028`
- **Partition**: `dev`
- **Category**: `criminal_intimidation`
- **Verbatim Text**:
  > *"The blackmailer told me he would post private photographs of my family unless I withdrew my police complaint."*

#### 2. Draft Candidate Labels in Repository (Pending Human Review)
- **Draft Candidate Provisions**: `["BNS_2023_S351"]`
- **Draft Expected No-Match**: `false`
- **Draft Rationale Recorded**: *"Threat to reputation to coerce omission of legal right (withdrawing complaint) constitutes criminal intimidation under 351 BNS."*
- **Reviewer Notes in Dataset**: *"Check if extortion (308 BNS) is triggered in absence of property demand."*
- **Annotation Status**: `pending`

#### 3. Automated Retrieval Pipeline Candidates ($\tau \ge 0.05$)
Retrieved candidates against the active 37-provision production corpus:
1. `ITA_2000_S66E` (Violation of privacy) — **Relevance: 0.3211** `[EXCEEDS TAU=0.12]`
2. `BNS_2023_S308` (Extortion) — **Relevance: 0.2672** `[EXCEEDS TAU=0.12]`
3. `BNS_2023_S77` (Voyeurism) — **Relevance: 0.2595** `[EXCEEDS TAU=0.12]`
4. `IPC_1860_S354C` (Voyeurism) — **Relevance: 0.2365** `[EXCEEDS TAU=0.12]`
5. `DPDP_2023_S33_PROVISIONAL` (Penalties) — **Relevance: 0.2057** `[EXCEEDS TAU=0.12]`

#### 4. Legal Analysis Framework
- **Facts in the Narrative**:
  - An individual threatened to publish private family photographs online.
  - The demand was to coerce the complainant into withdrawing a pending police complaint.
  - No money, valuable security, or property was demanded.
  - The photographs have not yet been posted or circulated.
- **Statutory Elements to Verify**:
  - *Section 351 BNS / Section 503 IPC (Criminal Intimidation)*: Threatening injury to person, reputation, or property to cause the person to do any act they are not legally bound to do, or omit any act they are legally entitled to do.
  - *Section 308 BNS / Section 383 IPC (Extortion)*: Intentionally putting in fear of injury and dishonestly inducing delivery of property or valuable security.
  - *Section 66E IT Act*: Capturing, publishing, or transmitting the image of a private area of any person without consent.
- **Provisional Legal Hypotheses (Requiring Review)**:
  - *Hypothesis 1*: Coercing the withdrawal of an FIR is an omission of a legal entitlement, satisfying criminal intimidation, not extortion (as an FIR withdrawal is not property).
  - *Hypothesis 2*: Section 66E IT Act does not apply to an unexecuted threat, as Section 66E requires actual capturing, publishing, or transmitting of intimate bodily images.
- **Unresolved Legal Questions Requiring Human Adjudication**:
  1. Does coercing the withdrawal of an FIR meet the definition of extortion in the absence of a demand for property or valuable security?
  2. Does an unexecuted threat to post private photos constitute an offense under Section 66E IT Act, or is Section 66E confined to completed publication/transmission of intimate bodily parts?
  3. Given that the retrieval engine ranks `ITA 66E` and `BNS 308` ahead of `BNS 351` based on surface keywords, how should evaluators classify candidate matches?

#### 5. Temporal Ambiguity & Statutory Applicability
- **Temporal Ambiguity Flagged**: No date is specified.
- **Statutory Applicability**: If post-July 1, 2024, BNS Section 351 applies. If pre-July 1, 2024, IPC Section 503/506 applies. Reviewers must not assume BNS applies by default; they must apply the documented temporal handling policy.

#### 6. Candidate Authoritative Citations for Reviewer Verification
> *[CANDIDATE CITATION — MUST BE INDEPENDENTLY VERIFIED BY REVIEWER ON INDIA CODE / OFFICIAL JUDGMENT REPOSITORIES]*
- Bharatiya Nyaya Sanhita, 2023, Sections 308, 351. India Code: `https://www.indiacode.nic.in/handle/123456789/20062`
- Indian Penal Code, 1860, Sections 383, 503, 506. India Code: `https://www.indiacode.nic.in/handle/123456789/2263`
- *Romesh Chandra Arora v. State* (1960) AIR SC 154 (Candidate ruling on threatening to circulate compromising photographs as criminal intimidation).

#### 7. Standardized Independent Review Form
```
[ ] Reviewer 1: ____________________________ Date: ____________ Confidence: [ ] High [ ] Med [ ] Low
    Target Provisions: [ ] BNS 351 only   [ ] BNS 351 + BNS 308   [ ] BNS 351 + IPC 506 (Dual)   [ ] Other: _______
    Rationale & Citations: _________________________________________________________________________________
[ ] Reviewer 2: ____________________________ Date: ____________ Confidence: [ ] High [ ] Med [ ] Low
    Target Provisions: [ ] BNS 351 only   [ ] BNS 351 + BNS 308   [ ] BNS 351 + IPC 506 (Dual)   [ ] Other: _______
    Rationale & Citations: _________________________________________________________________________________
[ ] Disagreement Resolution / Adjudication:
    Adjudicator: ___________________________ Determination: ___________________ Date: ____________
    Final Approved Labels: _________________________________________________ Status: [ ] PENDING [ ] REVIEWED
```

---

### Query 4: `DEV_029`

#### 1. Query Metadata & Verbatim Narrative
- **Query ID**: `DEV_029`
- **Partition**: `dev`
- **Category**: `out_of_scope_no_match`
- **Verbatim Text**:
  > *"A person recorded a conversation in a restaurant without informing the other attendees."*

#### 2. Draft Candidate Labels in Repository (Pending Human Review)
- **Draft Candidate Provisions**: `[]`
- **Draft Expected No-Match**: `true`
- **Draft Rationale Recorded**: *"Recording audio in a public restaurant where no reasonable expectation of bodily privacy exists does not constitute Section 66E IT Act."*
- **Reviewer Notes in Dataset**: *"Likely out of scope; pending review of admissibility vs statutory offense."*
- **Annotation Status**: `pending`

#### 3. Automated Retrieval Pipeline Candidates ($\tau \ge 0.05$)
Retrieved candidates against the active 37-provision production corpus:
1. `ITA_2000_S66E` (Violation of privacy) — **Relevance: 0.2710** `[EXCEEDS TAU=0.12]`
2. `BNS_2023_S77` (Voyeurism) — **Relevance: 0.2350** `[EXCEEDS TAU=0.12]`
3. `IPC_1860_S354C` (Voyeurism) — **Relevance: 0.2129** `[EXCEEDS TAU=0.12]`
4. `BNS_2023_S356` (Defamation) — **Relevance: 0.1635** `[EXCEEDS TAU=0.12]`
5. `BNS_2023_S319` (Cheating by personation) — **Relevance: 0.1613** `[EXCEEDS TAU=0.12]`

#### 4. Legal Analysis Framework
- **Facts in the Narrative**:
  - An in-person conversation took place in a public restaurant.
  - One attendee recorded audio without informing other attendees.
  - No intimate bodily images, wiretapping of telecommunication lines, or publication/broadcasting are mentioned.
- **Statutory Elements to Verify**:
  - *Section 66E IT Act*: Restricts privacy protection strictly to capturing, publishing, or transmitting images of private areas of a person.
  - *Section 77 BNS / Section 354C IPC (Voyeurism)*: Restricts offenses to observing or capturing a woman engaging in a private act.
- **Provisional Legal Hypotheses (Requiring Review)**:
  - *Hypothesis 1*: Secretly recording spoken conversation in a restaurant does not constitute a criminal offense under the indexed penal or cyber statutes, making it a true negative (`expected_no_match: true`).
  - *Hypothesis 2*: Tape recording conversation may have evidentiary consequences under evidence law, but evidentiary admissibility is distinct from penal criminality.
- **Unresolved Legal Questions Requiring Human Adjudication**:
  1. Does Indian penal or IT law create any criminal liability for one party recording an in-person public conversation without the other party's consent?
  2. Does the retrieval model's triggering of `ITA 66E` and `BNS 77` indicate semantic susceptibility to the verb "recorded"?
  3. Should this record be confirmed as `expected_no_match: true`?

#### 5. Temporal Ambiguity & Statutory Applicability
- **Temporal Ambiguity Flagged**: No date of occurrence is specified.
- **Statutory Applicability**: If lawful under both pre- and post-July 1, 2024 regimes, temporal ambiguity does not alter its status as an out-of-scope non-offense.

#### 6. Candidate Authoritative Citations for Reviewer Verification
> *[CANDIDATE CITATION — MUST BE INDEPENDENTLY VERIFIED BY REVIEWER ON INDIA CODE / OFFICIAL JUDGMENT REPOSITORIES]*
- Information Technology Act, 2000, Section 66E. India Code: `https://www.indiacode.nic.in/handle/123456789/1999`
- *R.M. Malkani v. State of Maharashtra* (1973) 1 SCC 471 (Candidate ruling on tape-recorded conversations and privacy boundaries).

#### 7. Standardized Independent Review Form
```
[ ] Reviewer 1: ____________________________ Date: ____________ Confidence: [ ] High [ ] Med [ ] Low
    Classification: [ ] TRUE NEGATIVE (Out of scope)   [ ] IN-SCOPE STATUTE: _________
    Rationale & Citations: _________________________________________________________________________________
[ ] Reviewer 2: ____________________________ Date: ____________ Confidence: [ ] High [ ] Med [ ] Low
    Classification: [ ] TRUE NEGATIVE (Out of scope)   [ ] IN-SCOPE STATUTE: _________
    Rationale & Citations: _________________________________________________________________________________
[ ] Disagreement Resolution / Adjudication:
    Adjudicator: ___________________________ Determination: ___________________ Date: ____________
    Final Approved Labels: _________________________________________________ Status: [ ] PENDING [ ] REVIEWED
```

---

### Query 5: `DEV_030`

#### 1. Query Metadata & Verbatim Narrative
- **Query ID**: `DEV_030`
- **Partition**: `dev`
- **Category**: `stalking`
- **Verbatim Text**:
  > *"Someone placed a GPS magnetic tracker under my vehicle and monitored everywhere I drove for two weeks."*

#### 2. Draft Candidate Labels in Repository (Pending Human Review)
- **Draft Candidate Provisions**: `["BNS_2023_S78"]`
- **Draft Expected No-Match**: `false`
- **Draft Rationale Recorded**: *"Electronic tracking of a woman's movements constitutes stalking under Section 78 BNS if targeted person is female."*
- **Reviewer Notes in Dataset**: *"Factual query lacks explicit gender specification; pending annotator review."*
- **Annotation Status**: `pending`

#### 3. Automated Retrieval Pipeline Candidates ($\tau \ge 0.05$)
Retrieved candidates against the active 37-provision production corpus:
1. `IPC_1860_S354D` (Stalking) — **Relevance: 0.2421** `[EXCEEDS TAU=0.12]`
2. `BNS_2023_S78` (Stalking) — **Relevance: 0.2120** `[EXCEEDS TAU=0.12]`
3. `ITA_2000_S66B` (Stolen computer resource) — **Relevance: 0.1954** `[EXCEEDS TAU=0.12]`
4. `DPDP_2023_S33_PROVISIONAL` (Penalties) — **Relevance: 0.1778** `[EXCEEDS TAU=0.12]`
5. `ITA_2000_S66C` (Identity theft) — **Relevance: 0.1628** `[EXCEEDS TAU=0.12]`

#### 4. Legal Analysis Framework
- **Facts in the Narrative**:
  - An unknown perpetrator placed a physical GPS tracker under the complainant's vehicle.
  - The perpetrator monitored vehicle movements for two weeks.
  - The gender of the perpetrator is unstated (*"Someone"*).
  - The gender of the complainant is unstated (*"my vehicle"*, *"I drove"*).
- **Statutory Elements to Verify**:
  - *Section 78 BNS / Section 354D IPC (Stalking)*: Substantive offense begins with gender-specific language: *"Whoever, being a man, follows a woman... or monitors the use by a woman of the internet, email or other form of electronic communication"*.
  - *Property / Trespass Statutes*: Physical affixation to property may involve mischief or trespass.
- **Provisional Legal Hypotheses (Requiring Review)**:
  - *Hypothesis 1*: In the absence of gender specifications, Section 78 BNS cannot be applied under strict criminal statutory construction, because the statute requires a male perpetrator and female victim.
  - *Hypothesis 2*: In consumer/complainant legal retrieval benchmarks, lay queries frequently omit legal ingredients (e.g. gender). If benchmarks require strict element satisfaction, this query could be classified as out-of-scope or flagged as ambiguous.
  - *Hypothesis 3*: Alternatively, the query text could be refined by annotators to include gender, or the annotation standard could allow an "in-scope hypothesis under assumed facts" guideline.
- **Unresolved Legal Questions Requiring Human Adjudication**:
  1. Can Section 78 BNS / Section 354D IPC be designated as ground truth for a completely gender-neutral factual scenario?
  2. If substantive criminal law requires a male accused and female victim, does labeling this scenario with BNS 78 create an unprincipled ground truth?
  3. Should the project policy require: (a) annotating strictly on stated facts (leading to out-of-scope), (b) permitting hypothetical gender fulfillment, or (c) amending the prompt narrative to supply the missing gender facts?

#### 5. Temporal Ambiguity & Statutory Applicability
- **Temporal Ambiguity Flagged**: No date is specified.
- **Statutory Applicability**: Section 78 BNS applies to post-July 1, 2024 acts; Section 354D IPC applies to pre-July 1, 2024 acts. Assuming BNS applies by default is unsupported. The documented temporal handling policy must be applied.

#### 6. Candidate Authoritative Citations for Reviewer Verification
> *[CANDIDATE CITATION — MUST BE INDEPENDENTLY VERIFIED BY REVIEWER ON INDIA CODE / OFFICIAL JUDGMENT REPOSITORIES]*
- Bharatiya Nyaya Sanhita, 2023, Section 78. India Code: `https://www.indiacode.nic.in/handle/123456789/20062`
- Indian Penal Code, 1860, Section 354D. India Code: `https://www.indiacode.nic.in/handle/123456789/2263`

#### 7. Standardized Independent Review Form
```
[ ] Reviewer 1: ____________________________ Date: ____________ Confidence: [ ] High [ ] Med [ ] Low
    Recommendation: [ ] BNS 78 (Hypothesis)   [ ] Refine query with gender   [ ] True Negative (Out of Scope)
    Rationale & Citations: _________________________________________________________________________________
[ ] Reviewer 2: ____________________________ Date: ____________ Confidence: [ ] High [ ] Med [ ] Low
    Recommendation: [ ] BNS 78 (Hypothesis)   [ ] Refine query with gender   [ ] True Negative (Out of Scope)
    Rationale & Citations: _________________________________________________________________________________
[ ] Disagreement Resolution / Adjudication:
    Adjudicator: ___________________________ Determination: ___________________ Date: ____________
    Final Approved Labels: _________________________________________________ Status: [ ] PENDING [ ] REVIEWED
```

---

### Query 6: `TEST_016`

#### 1. Query Metadata & Verbatim Narrative
- **Query ID**: `TEST_016`
- **Partition**: `test`
- **Category**: `unauthorized_access`
- **Verbatim Text**:
  > *"An unauthorized party guessed my Wi-Fi router password and used my home broadband connection for three days."*

#### 2. Draft Candidate Labels in Repository (Pending Human Review)
- **Draft Candidate Provisions**: `["ITA_2000_S43"]`
- **Draft Expected No-Match**: `false`
- **Draft Rationale Recorded**: *"Securing unauthorized access to a computer network without permission of the owner under Section 43 IT Act."*
- **Reviewer Notes in Dataset**: *"Needs annotator review on whether Section 66 is also satisfied without demonstrable damage."*
- **Annotation Status**: `pending`

#### 3. Automated Retrieval Pipeline Candidates ($\tau \ge 0.05$)
Retrieved candidates against the active 37-provision production corpus:
1. `ITA_2000_S66C` (Identity theft) — **Relevance: 0.3338** `[EXCEEDS TAU=0.12]`
2. `ITA_2000_S66` (Computer related offences) — **Relevance: 0.2405** `[EXCEEDS TAU=0.12]`
3. `ITA_2000_S66D` (Cheating by personation) — **Relevance: 0.2294** `[EXCEEDS TAU=0.12]`
4. `ITA_2000_S66B` (Stolen computer resource) — **Relevance: 0.2237** `[EXCEEDS TAU=0.12]`
5. `ITA_2000_S43` (Damage to computer system / unauthorized access) — **Relevance: 0.2129** `[EXCEEDS TAU=0.12]`

#### 4. Legal Analysis Framework
- **Facts in the Narrative**:
  - An unauthorized third party guessed a home Wi-Fi router password.
  - The party used the broadband connection for three days.
  - No data deletion, disruption, malware injection, or commercial theft is alleged.
- **Statutory Elements to Verify**:
  - *Section 43(a) IT Act*: Accessing or securing access to a computer, computer system, or computer network without permission of the owner.
  - *Section 66 IT Act*: Committing an act under Section 43 dishonestly or fraudulently, attracting criminal imprisonment up to three years.
  - *Section 66C IT Act*: Fraudulently or dishonestly using the password or unique identification feature of another person.
- **Provisional Legal Hypotheses (Requiring Review)**:
  - *Hypothesis 1*: Merely piggybacking on home Wi-Fi satisfies Section 43(a) (civil compensation), but does not meet the criminal threshold of Section 66 without demonstrable dishonest intent to cause wrongful loss/gain.
  - *Hypothesis 2*: Using a Wi-Fi password without authorization constitutes dishonest usage of a password under Section 66C or Section 66.
- **Unresolved Legal Questions Requiring Human Adjudication**:
  1. Does unauthorized Wi-Fi usage meet the criminal mens rea requirements ("fraudulently or dishonestly") under Section 66 IT Act, or is it exclusively a civil penalty offense under Section 43?
  2. Does guessing a router access password fall within Section 66C (*Identity Theft*), which was primarily drafted for personal authentication features (e.g. digital signatures, user login credentials)?
  3. Should the ground truth be `ITA_2000_S43` alone, `ITA_2000_S43` + `ITA_2000_S66`, or include `ITA_2000_S66C`?

#### 5. Temporal Ambiguity & Statutory Applicability
- **Temporal Ambiguity Flagged**: No date is specified.
- **Statutory Applicability**: The IT Act, 2000 provisions (Sections 43, 66, 66C) apply across both IPC and BNS eras without temporal disruption.

#### 6. Candidate Authoritative Citations for Reviewer Verification
> *[CANDIDATE CITATION — MUST BE INDEPENDENTLY VERIFIED BY REVIEWER ON INDIA CODE / OFFICIAL JUDGMENT REPOSITORIES]*
- Information Technology Act, 2000, Sections 43, 66, 66C. India Code: `https://www.indiacode.nic.in/handle/123456789/1999`
- Indian Penal Code, 1860, Sections 24 ("Dishonestly"), 25 ("Fraudulently") / BNS 2023 Section 2(8), 2(10).

#### 7. Standardized Independent Review Form
```
[ ] Reviewer 1: ____________________________ Date: ____________ Confidence: [ ] High [ ] Med [ ] Low
    Target Provisions: [ ] ITA_S43 only   [ ] ITA_S43 + ITA_S66   [ ] ITA_S66C included   [ ] Other: _______
    Rationale & Citations: _________________________________________________________________________________
[ ] Reviewer 2: ____________________________ Date: ____________ Confidence: [ ] High [ ] Med [ ] Low
    Target Provisions: [ ] ITA_S43 only   [ ] ITA_S43 + ITA_S66   [ ] ITA_S66C included   [ ] Other: _______
    Rationale & Citations: _________________________________________________________________________________
[ ] Disagreement Resolution / Adjudication:
    Adjudicator: ___________________________ Determination: ___________________ Date: ____________
    Final Approved Labels: _________________________________________________ Status: [ ] PENDING [ ] REVIEWED
```

---

### Query 7: `TEST_017`

#### 1. Query Metadata & Verbatim Narrative
- **Query ID**: `TEST_017`
- **Partition**: `test`
- **Category**: `financial_fraud`
- **Verbatim Text**:
  > *"In December 2023, an accountant embezzled funds by submitting forged invoices to the finance department."*

#### 2. Draft Candidate Labels in Repository (Pending Human Review)
- **Draft Candidate Provisions**: `["IPC_1860_S420"]`
- **Draft Expected No-Match**: `false`
- **Draft Rationale Recorded**: *"Historical cheating committed before 1 July 2024 governed by Section 420 IPC."*
- **Reviewer Notes in Dataset**: *"Pre-BNS fraudulent inducement; check if forgery provisions outside corpus are needed."*
- **Annotation Status**: `pending`

#### 3. Automated Retrieval Pipeline Candidates ($\tau \ge 0.05$)
Retrieved candidates against the active 37-provision production corpus:
1. `BNS_2023_S340` (Using forged record as genuine) — **Relevance: 0.3521** `[EXCEEDS TAU=0.12]`
2. `BNS_2023_S336` (Forgery) — **Relevance: 0.3181** `[EXCEEDS TAU=0.12]`
3. `IPC_1860_S468` (Forgery for purpose of cheating) — **Relevance: 0.3010** `[EXCEEDS TAU=0.12]`
4. `BNS_2023_S316` (Criminal breach of trust) — **Relevance: 0.2954** `[EXCEEDS TAU=0.12]`
5. `IPC_1860_S471` (Using as genuine forged record) — **Relevance: 0.2741** `[EXCEEDS TAU=0.12]`

#### 4. Legal Analysis Framework
- **Facts in the Narrative**:
  - The conduct occurred at an explicitly defined date: **December 2023**.
  - The actor was an accountant within an organization.
  - The mechanism involved submitting forged invoices to divert/embezzle funds.
- **Statutory Elements to Verify**:
  - *Article 20(1), Constitution of India*: Prohibits conviction under ex post facto law. An act committed in December 2023 can only be prosecuted under the law in force at that time (IPC 1860).
  - *IPC 1860 Provisions*:
    - Section 420: Cheating and dishonestly inducing delivery of property.
    - Section 468: Forgery for the purpose of cheating.
    - Section 471: Using as genuine a forged document.
    - Section 406 / 408: Criminal breach of trust / by clerk or servant.
- **Provisional Legal Hypotheses (Requiring Review)**:
  - *Hypothesis 1*: BNS provisions (e.g. BNS 340, BNS 336, BNS 316) cannot apply as governing law due to constitutional prohibition under Article 20(1).
  - *Hypothesis 2*: When `TEST_017` was originally drafted, `IPC_1860_S420` was the only relevant provision in the index. Because Phase 3 added `IPC_1860_S468`, `IPC_1860_S471`, and `IPC_1860_S406` to the corpus, retaining `IPC_1860_S420` as the sole ground truth unfairly penalizes the retrieval model for retrieving the more specific forgery and breach of trust statutes.
- **Unresolved Legal Questions Requiring Human Adjudication**:
  1. Given the explicit December 2023 temporal anchor, should all BNS candidates be disqualified as governing law?
  2. Does evaluating against `IPC_1860_S420` alone constitute an incomplete ground truth given the presence of `IPC_1860_S468` and `IPC_1860_S471` in the corpus?
  3. Should human adjudicators update the candidate set to a comprehensive multi-label ground truth (`IPC_1860_S468`, `IPC_1860_S471`, `IPC_1860_S420`, `IPC_1860_S406`)?

#### 5. Temporal Ambiguity & Statutory Applicability
- **Temporal Status**: **UNAMBIGUOUS**. The prompt explicitly specifies "In December 2023".
- **Statutory Applicability**: Strictly governed by the Indian Penal Code, 1860 pursuant to Article 20(1) of the Constitution and Section 358(2) BNS. BNS provisions cannot serve as valid governing law.

#### 6. Candidate Authoritative Citations for Reviewer Verification
> *[CANDIDATE CITATION — MUST BE INDEPENDENTLY VERIFIED BY REVIEWER ON INDIA CODE / OFFICIAL JUDGMENT REPOSITORIES]*
- Article 20(1), Constitution of India (Protection in respect of conviction for offences).
- Indian Penal Code, 1860, Sections 406, 408, 420, 468, 471. India Code: `https://www.indiacode.nic.in/handle/123456789/2263`
- Bharatiya Nyaya Sanhita, 2023, Section 358 (Repeal and savings).

#### 7. Standardized Independent Review Form
```
[ ] Reviewer 1: ____________________________ Date: ____________ Confidence: [ ] High [ ] Med [ ] Low
    Target Provisions: [ ] IPC 420 only   [ ] IPC 420 + IPC 468 + IPC 471   [ ] IPC 420 + 468 + 471 + 406   [ ] Other: _______
    Rationale & Citations: _________________________________________________________________________________
[ ] Reviewer 2: ____________________________ Date: ____________ Confidence: [ ] High [ ] Med [ ] Low
    Target Provisions: [ ] IPC 420 only   [ ] IPC 420 + IPC 468 + IPC 471   [ ] IPC 420 + 468 + 471 + 406   [ ] Other: _______
    Rationale & Citations: _________________________________________________________________________________
[ ] Disagreement Resolution / Adjudication:
    Adjudicator: ___________________________ Determination: ___________________ Date: ____________
    Final Approved Labels: _________________________________________________ Status: [ ] PENDING [ ] REVIEWED
```

---

### Query 8: `TEST_018`

#### 1. Query Metadata & Verbatim Narrative
- **Query ID**: `TEST_018`
- **Partition**: `test`
- **Category**: `out_of_scope_no_match`
- **Verbatim Text**:
  > *"Someone took pictures of our company storefront from a public street sidewalk during business hours."*

#### 2. Draft Candidate Labels in Repository (Pending Human Review)
- **Draft Candidate Provisions**: `[]`
- **Draft Expected No-Match**: `true`
- **Draft Rationale Recorded**: *"Taking photographs of a public storefront does not violate privacy or criminal provisions."*
- **Reviewer Notes in Dataset**: *"No reasonable expectation of privacy for public storefront."*
- **Annotation Status**: `pending`

#### 3. Automated Retrieval Pipeline Candidates ($\tau \ge 0.05$)
Retrieved candidates against the active 37-provision production corpus:
1. `ITA_2000_S66E` (Violation of privacy) — **Relevance: 0.2526** `[EXCEEDS TAU=0.12]`
2. `BNS_2023_S77` (Voyeurism) — **Relevance: 0.1762** `[EXCEEDS TAU=0.12]`
3. `IPC_1860_S354C` (Voyeurism) — **Relevance: 0.1365** `[EXCEEDS TAU=0.12]`
4. `BNS_2023_S303` (Theft) — **Relevance: 0.1348** `[EXCEEDS TAU=0.12]`
5. `ITA_2000_S43` (Damage to computer system) — **Relevance: 0.1139** `[BELOW TAU=0.12]`

#### 4. Legal Analysis Framework
- **Facts in the Narrative**:
  - An individual stood on a public street sidewalk during ordinary business hours.
  - The individual took photographs of the commercial exterior/storefront of a business.
  - No private residences, private acts, or intimate body areas were photographed.
- **Statutory Elements to Verify**:
  - *Section 66E IT Act*: Requires capturing/publishing images of private bodily areas.
  - *Section 77 BNS / Section 354C IPC*: Requires observing or capturing images of a woman in a private act.
- **Provisional Legal Hypotheses (Requiring Review)**:
  - *Hypothesis 1*: Photographing a commercial facade from a public sidewalk is completely lawful and does not trigger any penal or cyber offense, confirming its classification as a true negative (`expected_no_match: true`).
  - *Hypothesis 2*: The model's retrieval of `ITA 66E` and `BNS 77` reflects lexical bias toward photography terms rather than semantic comprehension of legal ingredients.
- **Unresolved Legal Questions Requiring Human Adjudication**:
  1. Does Indian penal law recognize any expectation of privacy for a commercial storefront visible from a public street?
  2. Does this scenario confirm the role of negative evaluation examples in penalizing false positives in legal retrieval engines?

#### 5. Temporal Ambiguity & Statutory Applicability
- **Temporal Ambiguity Flagged**: No date is specified.
- **Statutory Applicability**: Lawful public conduct under both pre- and post-July 1, 2024 legal regimes.

#### 6. Candidate Authoritative Citations for Reviewer Verification
> *[CANDIDATE CITATION — MUST BE INDEPENDENTLY VERIFIED BY REVIEWER ON INDIA CODE / OFFICIAL JUDGMENT REPOSITORIES]*
- Constitution of India, Article 19(1)(a).
- Information Technology Act, 2000, Section 66E. India Code: `https://www.indiacode.nic.in/handle/123456789/1999`
- Bharatiya Nyaya Sanhita, 2023, Section 77. India Code: `https://www.indiacode.nic.in/handle/123456789/20062`

#### 7. Standardized Independent Review Form
```
[ ] Reviewer 1: ____________________________ Date: ____________ Confidence: [ ] High [ ] Med [ ] Low
    Classification: [ ] TRUE NEGATIVE (Lawful Public Photography)   [ ] IN-SCOPE STATUTE: _________
    Rationale & Citations: _________________________________________________________________________________
[ ] Reviewer 2: ____________________________ Date: ____________ Confidence: [ ] High [ ] Med [ ] Low
    Classification: [ ] TRUE NEGATIVE (Lawful Public Photography)   [ ] IN-SCOPE STATUTE: _________
    Rationale & Citations: _________________________________________________________________________________
[ ] Disagreement Resolution / Adjudication:
    Adjudicator: ___________________________ Determination: ___________________ Date: ____________
    Final Approved Labels: _________________________________________________ Status: [ ] PENDING [ ] REVIEWED
```

---

### Query 9: `TEST_019`

#### 1. Query Metadata & Verbatim Narrative
- **Query ID**: `TEST_019`
- **Partition**: `test`
- **Category**: `out_of_scope_no_match`
- **Verbatim Text**:
  > *"A user created a parody account on social media clearly labeled as satire of a celebrity."*

#### 2. Draft Candidate Labels in Repository (Pending Human Review)
- **Draft Candidate Provisions**: `[]`
- **Draft Expected No-Match**: `true`
- **Draft Rationale Recorded**: *"Explicit parody/satire lacking deceptive fraudulent inducement is not criminal personation."*
- **Reviewer Notes in Dataset**: *"Parody exception under IT Act / absence of deceptive intent."*
- **Annotation Status**: `pending`

#### 3. Automated Retrieval Pipeline Candidates ($\tau \ge 0.05$)
Retrieved candidates against the active 37-provision production corpus:
1. `ITA_2000_S66D` (Cheating by personation using computer resource) — **Relevance: 0.3359** `[EXCEEDS TAU=0.12]`
2. `ITA_2000_S67` (Publishing obscene material) — **Relevance: 0.1741** `[EXCEEDS TAU=0.12]`
3. `BNS_2023_S319` (Cheating by personation) — **Relevance: 0.1620** `[EXCEEDS TAU=0.12]`
4. `ITA_2000_S66E` (Violation of privacy) — **Relevance: 0.1399** `[EXCEEDS TAU=0.12]`
5. `ITA_2000_S67A` (Sexually explicit material) — **Relevance: 0.1382** `[EXCEEDS TAU=0.12]`

#### 4. Legal Analysis Framework
- **Facts in the Narrative**:
  - A social media account was created referencing a public figure/celebrity.
  - The account carried a clear label stating it was a parody and satire account.
  - No defamatory statement, extortion, obscene publication, or commercial fraud is described.
- **Statutory Elements to Verify**:
  - *Section 66D IT Act*: Requires cheating by personation by means of computer resource, requiring deceptive intent.
  - *Section 319 BNS / Section 416 IPC (Cheating by personation)*: Requires pretending to be a person to deceive another into believing one is that person.
- **Provisional Legal Hypotheses (Requiring Review)**:
  - *Hypothesis 1*: A prominent disclosure of parody negates the mens rea of deceit required for personation, rendering the act non-criminal under penal statutes and supporting `expected_no_match: true`.
  - *Hypothesis 2*: The model's retrieval of `ITA 66D` at 0.3359 demonstrates that the embedding model confuses satire accounts with malicious impersonation.
- **Unresolved Legal Questions Requiring Human Adjudication**:
  1. Does a prominent label of satire legally negate the element of deception under Section 66D IT Act and Section 319 BNS?
  2. Does mere parody absent defamation or fraud constitute any criminal offense under Indian law?
  3. Should this record be maintained as `expected_no_match: true`?

#### 5. Temporal Ambiguity & Statutory Applicability
- **Temporal Ambiguity Flagged**: No date is specified.
- **Statutory Applicability**: Section 66D IT Act applies continuously; BNS 319 vs IPC 416 depend on date if penal provisions were considered.

#### 6. Candidate Authoritative Citations for Reviewer Verification
> *[CANDIDATE CITATION — MUST BE INDEPENDENTLY VERIFIED BY REVIEWER ON INDIA CODE / OFFICIAL JUDGMENT REPOSITORIES]*
- Section 66D, Information Technology Act, 2000. India Code: `https://www.indiacode.nic.in/handle/123456789/1999`
- Bharatiya Nyaya Sanhita, 2023, Section 319. India Code: `https://www.indiacode.nic.in/handle/123456789/20062`
- *Shreya Singhal v. Union of India* (2015) 5 SCC 1 (Candidate ruling on internet speech and freedom of expression).

#### 7. Standardized Independent Review Form
```
[ ] Reviewer 1: ____________________________ Date: ____________ Confidence: [ ] High [ ] Med [ ] Low
    Classification: [ ] TRUE NEGATIVE (Protected Parody/Satire)   [ ] IN-SCOPE (ITA 66D / BNS 319)
    Rationale & Citations: _________________________________________________________________________________
[ ] Reviewer 2: ____________________________ Date: ____________ Confidence: [ ] High [ ] Med [ ] Low
    Classification: [ ] TRUE NEGATIVE (Protected Parody/Satire)   [ ] IN-SCOPE (ITA 66D / BNS 319)
    Rationale & Citations: _________________________________________________________________________________
[ ] Disagreement Resolution / Adjudication:
    Adjudicator: ___________________________ Determination: ___________________ Date: ____________
    Final Approved Labels: _________________________________________________ Status: [ ] PENDING [ ] REVIEWED
```

---

### Query 10: `TEST_020`

#### 1. Query Metadata & Verbatim Narrative
- **Query ID**: `TEST_020`
- **Partition**: `test`
- **Category**: `stalking`
- **Verbatim Text**:
  > *"A man sent fifty unsolicited romantic poems to a coworker's official email despite her repeated requests to stop."*

#### 2. Draft Candidate Labels in Repository (Pending Human Review)
- **Draft Candidate Provisions**: `["BNS_2023_S78"]`
- **Draft Expected No-Match**: `false`
- **Draft Rationale Recorded**: *"Repeated unwanted electronic communication to a woman despite clear disinterest constitutes Section 78 BNS."*
- **Reviewer Notes in Dataset**: *"Electronic harassment / stalking."*
- **Annotation Status**: `pending`

#### 3. Automated Retrieval Pipeline Candidates ($\tau \ge 0.05$)
Retrieved candidates against the active 37-provision production corpus:
1. `IPC_1860_S354D` (Stalking) — **Relevance: 0.2837** `[EXCEEDS TAU=0.12]`
2. `BNS_2023_S78` (Stalking) — **Relevance: 0.2672** `[EXCEEDS TAU=0.12]`
3. `BNS_2023_S79` (Word, gesture or act intended to insult modesty) — **Relevance: 0.1822** `[EXCEEDS TAU=0.12]`
4. `IPC_1860_S509` (Word, gesture or act intended to insult modesty) — **Relevance: 0.1593** `[EXCEEDS TAU=0.12]`
5. `ITA_2000_S66D` (Cheating by personation) — **Relevance: 0.1579** `[EXCEEDS TAU=0.12]`

#### 4. Legal Analysis Framework
- **Facts in the Narrative**:
  - The perpetrator is explicitly identified as a man (*"A man sent..."*).
  - The recipient is explicitly identified as a female coworker (*"...her repeated requests to stop"*).
  - The medium was electronic mail (*"coworker's official email"*).
  - The volume was fifty unsolicited messages.
  - The victim clearly communicated disinterest and requested the sender to cease.
- **Statutory Elements to Verify**:
  - *Section 78(1)(ii) BNS / Section 354D(1)(ii) IPC*: Explicitly penalizes a man who monitors the use by a woman of the internet, email or other form of electronic communication, or continues to contact or attempts to contact a woman to foster personal interaction repeatedly despite a clear indication of disinterest by such woman.
  - *Section 79 BNS / Section 509 IPC*: Intending to insult the modesty of any woman by uttering any word or making any sound.
  - *POSH Act, 2013, Section 28*: Internal workplace complaints operate concurrently with criminal prosecution.
- **Provisional Legal Hypotheses (Requiring Review)**:
  - *Hypothesis 1*: Unlike `DEV_030`, the factual elements here satisfy all statutory prerequisites of Section 78 BNS / Section 354D IPC (gender of parties, repeated contact, explicit disinterest).
  - *Hypothesis 2*: The availability of civil remedies under the POSH Act, 2013 does not bar criminal proceedings under Section 78 BNS.
  - *Hypothesis 3*: Sending romantic poetry without vulgarity may fall primarily under stalking (Section 78) rather than insult to modesty (Section 79).
- **Unresolved Legal Questions Requiring Human Adjudication**:
  1. Do fifty unwanted romantic poems to a coworker's email satisfy stalking (Section 78 BNS / Section 354D IPC) as the exclusive primary charge, or should Section 79 BNS / Section 509 IPC be included as co-primary?
  2. Because the incident date is unstated, how should the temporal applicability of Section 78 BNS vs Section 354D IPC be handled under the project's documented policy?

#### 5. Temporal Ambiguity & Statutory Applicability
- **Temporal Ambiguity Flagged**: No incident date is specified.
- **Statutory Applicability**: Substantive elements exist in both Section 354D IPC (pre-July 1, 2024) and Section 78 BNS (post-July 1, 2024). Reviewers must not assume BNS applies by default, and must apply the project's documented temporal policy.

#### 6. Candidate Authoritative Citations for Reviewer Verification
> *[CANDIDATE CITATION — MUST BE INDEPENDENTLY VERIFIED BY REVIEWER ON INDIA CODE / OFFICIAL JUDGMENT REPOSITORIES]*
- Section 78, Bharatiya Nyaya Sanhita, 2023. India Code: `https://www.indiacode.nic.in/handle/123456789/20062`
- Section 354D, Indian Penal Code, 1860. India Code: `https://www.indiacode.nic.in/handle/123456789/2263`
- Sexual Harassment of Women at Workplace (Prevention, Prohibition and Redressal) Act, 2013, Section 28. India Code: `https://www.indiacode.nic.in/handle/123456789/2104`

#### 7. Standardized Independent Review Form
```
[ ] Reviewer 1: ____________________________ Date: ____________ Confidence: [ ] High [ ] Med [ ] Low
    Target Provisions: [ ] BNS 78 only   [ ] BNS 78 + IPC 354D (Dual)   [ ] BNS 78 + BNS 79   [ ] Other: _______
    Rationale & Citations: _________________________________________________________________________________
[ ] Reviewer 2: ____________________________ Date: ____________ Confidence: [ ] High [ ] Med [ ] Low
    Target Provisions: [ ] BNS 78 only   [ ] BNS 78 + IPC 354D (Dual)   [ ] BNS 78 + BNS 79   [ ] Other: _______
    Rationale & Citations: _________________________________________________________________________________
[ ] Disagreement Resolution / Adjudication:
    Adjudicator: ___________________________ Determination: ___________________ Date: ____________
    Final Approved Labels: _________________________________________________ Status: [ ] PENDING [ ] REVIEWED
```

---

## 4. Methodological Protocols for Legal Annotation

### 4.1 Temporal Ambiguity Protocol (IPC vs. BNS)

#### The Problem:
Several evaluation queries (`DEV_028`, `DEV_030`, `TEST_020`) describe factual scenarios without specifying when the incident occurred. On July 1, 2024, the Bharatiya Nyaya Sanhita (BNS), 2023 came into force, repealing the Indian Penal Code, 1860 (subject to savings under Section 358(2) BNS). Under **Article 20(1) of the Constitution of India**, penal laws cannot be applied ex post facto:
- Offenses committed **prior to July 1, 2024** are governed strictly by the **IPC 1860**.
- Offenses committed **on or after July 1, 2024** are governed strictly by the **BNS 2023**.

#### Prohibition of Unverified Assumptions:
Reviewers and automated systems **must not assume** that an undated query defaults to BNS. 

#### Recommended Temporal Policy Options:
The project must officially select and document one of three explicit policies:
- **Policy Option A (Dual / Disjunctive Labeling)**: For undated scenarios with equivalent provisions in both codes, the evaluation ground truth accepts either or both provisions (e.g. `{"allowed_matches": [["BNS_2023_S78"], ["IPC_1860_S354D"]]}`).
- **Policy Option B (Era-Anchored Query Specification)**: Amend the prompt narrative to include an explicit year or date (e.g., adding "In August 2024..." or "In 2022..."), eliminating temporal ambiguity at the source.
- **Policy Option C (Standard Benchmark Default with Explicit Assumption)**: Formalize a benchmark convention stating: *"All undated queries represent contemporary incidents occurring post-July 1, 2024 governed by BNS, except where historical dates are specified."* This convention must be documented in `evaluation/README.md` and `benchmark_manifest.json` before bench testing.

---

### 4.2 Inter-Annotator Agreement (IAA) Protocol

#### 1. Nature of the Annotation Task: Multi-Label and Out-of-Scope
Legal provision retrieval is not a single-label multiclass classification problem. An evaluation record may have:
- An empty provision list (`expected_no_match: true`, `relevant_provision_ids: []`)
- A single target provision (`["BNS_2023_S78"]`)
- Multiple co-primary or compound provisions (`["ITA_2000_S66C", "ITA_2000_S66"]` or `["IPC_1860_S468", "IPC_1860_S471", "IPC_1860_S420"]`)

#### 2. Distinct Roles of Agreement Metrics:
- **Percentage Exact-Set Agreement**:
  $$\text{Agreement}_{\text{exact}} = \frac{1}{N} \sum_{i=1}^N \mathbb{I}(\text{Set}_1^{(i)} = \text{Set}_2^{(i)})$$
  Measures strict consensus across all assigned labels. It provides an intuitive metric but fails to reward partial overlap (e.g., both reviewers identifying Section 66C, but one adding Section 66).
- **Item-Level Jaccard Similarity**:
  $$J(\text{Set}_1, \text{Set}_2) = \frac{|\text{Set}_1 \cap \text{Set}_2|}{|\text{Set}_1 \cup \text{Set}_2|}$$
  For cases where both sets are empty (`expected_no_match: true`), $J(\emptyset, \emptyset) = 1.0$.
- **Cohen's Kappa ($\kappa$) for Binary Out-of-Scope Decisions**:
  For the binary indicator `expected_no_match` ($\{\text{true}, \text{false}\}$), Cohen's kappa must be computed using standard $2 \times 2$ contingency tables:
  $$\kappa = \frac{P_o - P_e}{1 - P_e}$$
  *Prevalence Warning*: In small samples with high proportions of true negatives, Cohen's kappa suffers from the prevalence paradox (high agreement yielding low kappa). Reviewers must report both observed percentage agreement ($P_o$) and kappa ($\kappa$).
- **Per-Provision Binary Indicator Kappa / Krippendorff's Alpha**:
  To measure multi-label agreement across specific provisions, binarize decisions across the candidate provision space or calculate Krippendorff's alpha for set-valued data.

#### 3. Statistical Limitations of the 10-Item Quarantined Sample:
- With only $N = 10$ records, a single disagreement changes percentage agreement by 10.0%.
- Confidence intervals for Cohen's kappa on $N = 10$ are extremely wide (e.g., spanning $0.20$ to $0.90$).
- Therefore, statistical metrics on this small batch serve only as **preliminary indicators**, not statistically robust population estimates. Full qualitative adjudication and documentation of legal rationale are required for every disagreement.

---

## 5. Outstanding Issues and Reviewer Instructions

### Actionable Review Checklist for Human Legal Reviewers:

1. **Independent Dual Review**:
   - Reviewer 1 and Reviewer 2 must work independently without sharing draft annotations or rationales.
   - For each query, the reviewer must consult official statutory sources on **India Code** (`indiacode.nic.in`) and verify active provisions.
2. **Reviewer Submission Fields**:
   - Every completed review form must record:
     - **Reviewer ID & Date**
     - **Proposed Label Set** (`relevant_provision_ids` and `expected_no_match`)
     - **Detailed Legal Rationale** explaining statutory element mapping
     - **Verified Source Citations** (Act, Section, Gazette notification if applicable)
     - **Confidence Score** (`High`, `Medium`, or `Low`)
     - **Temporal Policy Applied** (Option A, B, or C)
3. **Disagreement Escalation & Senior Adjudication**:
   - If Jaccard similarity $< 1.0$ or if reviewers disagree on `expected_no_match`, the query must be escalated to a Senior Legal Adjudicator.
   - The adjudicator's written determination must specify why competing statutory arguments were accepted or rejected.
4. **Controlled Dataset Update**:
   - Only after dual-review and senior adjudication forms are signed and committed may an engineer update `annotation_status` from `"pending"` to `"reviewed"` in `retrieval_eval_dataset.json`.
   - Never update dataset labels based on automated model scores.
5. **Fresh Benchmark Requirement**:
   - No benchmark claim may be made using this dataset alone. A separate blind benchmark of 25–50 fresh scenarios must be authored and locked in `benchmark_manifest.json` before publishing final performance metrics.

---

## 6. Dataset Preservation & Integrity Affirmation

1. **Zero Modification to `retrieval_eval_dataset.json`**:
   - Inspected in read-only mode.
   - All 10 target records retain `annotation_status: "pending"`.
   - Exact count: 50 total records (30 dev, 20 test; 40 reviewed, 10 pending).
2. **Zero Modification to `benchmark_manifest.json`**:
   - Benchmark manifest remains intact with 0 locked benchmarks registered.
3. **Corpus Fingerprint Preserved**:
   - File: `backend/data/legal_provisions.json` (37 provisions).
   - SHA-256 Digest: `becf1f001631bbdc301633df428b0cb541dca97fa45b1ad7cf05db8b1d0d00d0`.
4. **Operating Threshold Preserved**:
   - Retrieval threshold is frozen at $\tau = 0.12$.

---

## 7. Automated Validation Command Execution

The dataset validation suite was executed to verify that the dataset remains structurally valid and completely uncorrupted.

### Command Executed:
```powershell
python evaluation/eval_retrieval.py --validate --check-provenance
```

### Actual Terminal Output:
```text
[OK] Dataset validation passed: zero schema, duplicate, or split leakage errors.
```

### Test Suite Output (`tests/test_evaluation.py`):
```text
============================= test session starts =============================
platform win32 -- Python 3.13.11, pytest-9.0.2, pluggy-1.6.0
rootdir: G:\NLP\New\backend
plugins: anyio-4.13.0, asyncio-1.4.0
collected 24 items

tests\test_evaluation.py ........................                        [100%]

============================= 24 passed in 0.18s ==============================
```
