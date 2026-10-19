# LexiLaw — Manifest of Pending Evaluation Records & Scenarios

**Manifest Version:** 1.0.0  
**Generated Date:** October 17, 2026  
**Evaluation Status:** **ALL 45 RECORDS CURRENTLY IN PENDING STATUS**  
**Machine-Readable Companion:** [`ANNOTATION_PENDING_MANIFEST.json`](file:///g:/NLP/New/backend/evaluation/annotation_workflow/ANNOTATION_PENDING_MANIFEST.json)

---

## 1. Executive Summary

| Dataset Partition | Target File | Pending Count | Reviewed Count | Lock Status | Evaluation Readiness |
| :--- | :--- | :---: | :---: | :--- | :--- |
| **Quarantined Development Split** | `backend/evaluation/retrieval_eval_dataset.json` | 5 | 25 | N/A (Dev split) | Awaiting Phase 5 Review |
| **Quarantined Test Split** | `backend/evaluation/retrieval_eval_dataset.json` | 5 | 15 | N/A (Test split) | Awaiting Phase 5 Review |
| **Independent Blind Benchmark** | `backend/evaluation/blind_benchmark_dataset.json` | 35 | 0 | Unlocked (`locked: false`) | Awaiting Phase 6 Review |
| **Total Review Portfolio** | **Two Datasets** | **45** | **40** | **Gatekeeper Active** | **Awaiting Independent Review** |

---

## 2. Part 1: Original 10 Quarantined Evaluation Records

These 10 records in `retrieval_eval_dataset.json` were quarantined during threshold tuning ($\tau = 0.12$) to prevent evaluation contamination:

| Query ID | Split | Category | Query Narrative | Current Status |
| :--- | :---: | :--- | :--- | :---: |
| **`DEV_026`** | `dev` | `cyber_identity_theft` | Someone logged into my work email account using stolen credentials and sent offensive emails to our leadership team. | **PENDING** |
| **`DEV_027`** | `dev` | `out_of_scope_no_match` | A vendor manufactured counterfeit branded handbags mimicking our registered trademark logo. | **PENDING** |
| **`DEV_028`** | `dev` | `criminal_intimidation` | The blackmailer told me he would post private photographs of my family unless I withdrew my police complaint. | **PENDING** |
| **`DEV_029`** | `dev` | `out_of_scope_no_match` | A person recorded a conversation in a restaurant without informing the other attendees. | **PENDING** |
| **`DEV_030`** | `dev` | `stalking` | Someone placed a GPS magnetic tracker under my vehicle and monitored everywhere I drove for two weeks. | **PENDING** |
| **`TEST_016`** | `test` | `unauthorized_access` | An unauthorized party guessed my Wi-Fi router password and used my home broadband connection for three days. | **PENDING** |
| **`TEST_017`** | `test` | `financial_fraud` | In December 2023, an accountant embezzled funds by submitting forged invoices to the finance department. | **PENDING** |
| **`TEST_018`** | `test` | `out_of_scope_no_match` | Someone took pictures of our company storefront from a public street sidewalk during business hours. | **PENDING** |
| **`TEST_019`** | `test` | `out_of_scope_no_match` | A user created a parody account on social media clearly labeled as satire of a celebrity. | **PENDING** |
| **`TEST_020`** | `test` | `stalking` | A man sent fifty unsolicited romantic poems to a coworker's official email despite her repeated requests to stop. | **PENDING** |

---

## 3. Part 2: 35 Independent Blind Benchmark Scenarios

These 35 held-out scenarios in `blind_benchmark_dataset.json` were newly authored with guaranteed token Jaccard isolation ($< 0.25$ similarity against dev/test) to test modern BNS 2023, historical IPC 1860, cybercrime, and civil boundaries:

| Query ID | Category | Query Narrative | Current Status |
| :--- | :--- | :--- | :---: |
| **`BLIND_001`** | `forgery` | In August 2024, a job applicant created a fake university degree certificate and submitted it to our company HR department to obtain employment. | **PENDING** |
| **`BLIND_002`** | `forgery` | In November 2023, an employee fabricated a fake vendor invoice on official company letterhead and submitted it to finance to claim a fraudulent reimbursement. | **PENDING** |
| **`BLIND_003`** | `forgery` | In September 2024, an individual presented a doctored property deed that had been forged by an unknown third party, knowing it was fake, to register a disputed land plot. | **PENDING** |
| **`BLIND_004`** | `forgery` | In January 2024, a contractor altered the date and figure on an official clearance certificate to avoid municipal inspection penalties. | **PENDING** |
| **`BLIND_005`** | `criminal_breach_of_trust` | In August 2024, a corporate treasurer was entrusted with company liquid assets but secretly siphoned twenty lakh rupees into a personal cryptocurrency wallet. | **PENDING** |
| **`BLIND_006`** | `criminal_breach_of_trust` | In March 2024, a warehouse manager entrusted with electronic goods inventory dishonestly sold fifty laptops on the grey market and kept the cash. | **PENDING** |
| **`BLIND_007`** | `mischief` | In August 2024, a disgruntled ex-employee entered the office server room and intentionally cut the fiber optic cables, destroying critical network equipment. | **PENDING** |
| **`BLIND_008`** | `mischief` | In February 2024, an individual slashed the tires of four delivery vans parked in a commercial yard following an argument with the fleet owner. | **PENDING** |
| **`BLIND_009`** | `theft` | In August 2024, an engineer copied and carried away on an external drive proprietary production firmware without company authorization. | **PENDING** |
| **`BLIND_010`** | `theft` | In May 2024, a visitor stole an unattended company laptop containing trade secrets from a conference room table. | **PENDING** |
| **`BLIND_011`** | `extortion` | In August 2024, a person sent threatening emails demanding fifty thousand rupees, stating they would release private family photos online if payment was not made. | **PENDING** |
| **`BLIND_012`** | `extortion` | In May 2024, an extortionist threatened to harm a merchant's teenage son unless monthly protection money of twenty thousand rupees was delivered. | **PENDING** |
| **`BLIND_013`** | `voyeurism` | In August 2024, a hostel warden installed a hidden surveillance camera inside the female students' private changing area. | **PENDING** |
| **`BLIND_014`** | `voyeurism` | In March 2024, an individual secretly filmed a woman through her bedroom window while she was changing clothes without her consent. | **PENDING** |
| **`BLIND_015`** | `stalking` | In September 2024, a man repeatedly sent unwanted direct messages and tracked a former coworker across her personal social media profiles despite repeated blocks. | **PENDING** |
| **`BLIND_016`** | `stalking` | In April 2024, an estranged acquaintance persistently followed a woman to her workplace daily for three weeks despite her explicit demands to cease. | **PENDING** |
| **`BLIND_017`** | `insult_modesty` | In August 2024, an individual directed sexually explicit and abusive remarks at a female transit passenger in a crowded metro carriage. | **PENDING** |
| **`BLIND_018`** | `insult_modesty` | In January 2024, a supervisor repeatedly made intrusive, vulgar comments regarding a female subordinate's physical appearance in the office corridor. | **PENDING** |
| **`BLIND_019`** | `defamation` | In August 2024, a competitor published a fabricated blog post falsely asserting that our brand used toxic industrial chemicals in infant food formulas. | **PENDING** |
| **`BLIND_020`** | `defamation` | In February 2024, an individual circulated flyers throughout a residential colony falsely alleging that a local doctor was running an illegal narcotics racket. | **PENDING** |
| **`BLIND_021`** | `criminal_intimidation` | In October 2024, a landlord threatened to set fire to a tenant's retail shop unless they immediately vacated the premises. | **PENDING** |
| **`BLIND_022`** | `criminal_intimidation` | In June 2024, an armed individual threatened to break an auto driver's bones unless he gave up his daily taxi stand queue spot. | **PENDING** |
| **`BLIND_023`** | `cyber_hacking` | A remote attacker exploited an unpatched web vulnerability to alter medical clinic database records and inject malicious ransomware payloads. | **PENDING** |
| **`BLIND_024`** | `cyber_identity_theft` | An imposter fraudulently used an executive's digital signature certificate to authorize unauthorized corporate bank transfers. | **PENDING** |
| **`BLIND_025`** | `cyber_personation` | An attacker created a fake corporate banking portal mimicking a national bank to dupe customers into revealing debit card PINs. | **PENDING** |
| **`BLIND_026`** | `privacy_violation` | A technician servicing a smartphone copied private personal photographs from the device and uploaded them to an online message board without consent. | **PENDING** |
| **`BLIND_027`** | `out_of_scope_civil_breach_of_contract` | A software development agency delivered a project four months past the agreed milestone date, and the client refused to pay the final progress invoice. | **PENDING** |
| **`BLIND_028`** | `out_of_scope_tenancy_dispute` | A landlord withheld an entire security deposit claiming normal wear and tear on apartment paint required professional repainting. | **PENDING** |
| **`BLIND_029`** | `out_of_scope_consumer_protection` | A retail customer purchased a smartphone that stopped charging after one week, and the store manager refused an exchange citing warranty exclusions. | **PENDING** |
| **`BLIND_030`** | `out_of_scope_satire_free_speech` | A political cartoonist published an editorial caricature on a news portal satirizing a public official's municipal road repair policies. | **PENDING** |
| **`BLIND_031`** | `out_of_scope_public_photography` | An amateur photographer took wide-angle street landscape photos of a crowded public heritage market, capturing faces of pedestrians in public view. | **PENDING** |
| **`BLIND_032`** | `out_of_scope_uncommenced_statute` | A driver struck a pedestrian at midnight and fled the scene without reporting the collision to the nearest police officer or magistrate. | **PENDING** |
| **`BLIND_033`** | `out_of_scope_provisional_data_protection` | A cloud data storage provider accidentally exposed an unencrypted customer email address list due to a misconfigured public access bucket. | **PENDING** |
| **`BLIND_034`** | `out_of_scope_commercial_arbitration` | Two telecom infrastructure firms entered a contractual dispute regarding the calculation of shared cell tower electricity maintenance fees. | **PENDING** |
| **`BLIND_035`** | `out_of_scope_commercial_merchandise_return` | An online e-commerce marketplace account was suspended after a customer returned a wrong size sweater and initiated a payment card chargeback. | **PENDING** |
