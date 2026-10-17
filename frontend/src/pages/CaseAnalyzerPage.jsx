import React, { useState, useRef } from 'react';
import { extractPdfDocument, analyzeCase } from '../services/api';
import ErrorAlert from '../components/ErrorAlert';

const SAMPLE_JUDGMENT = `IN THE SUPREME COURT OF INDIA
CIVIL APPELLATE JURISDICTION
CIVIL APPEAL NO. 4521 OF 2023

ABC Technologies Private Limited ... Appellant
VERSUS
State of Maharashtra & Anr. ... Respondents

DECIDED ON: 14th August 2023

CORAM: Hon'ble Justice P. S. Narasimha and Hon'ble Justice Manoj Misra

JUDGMENT:
1. The present appeal arises out of the judgment and order dated 12th January 2023 passed by the High Court of Judicature at Bombay, dismissing the Writ Petition filed by the appellant company.
2. The material facts are that the appellant is a cloud-computing service provider operating data centers within the State. In March 2022, an inspection was conducted pursuant to Section 43 of the Information Technology Act, 2000, alleging unauthorized data transfer.
3. The legal issue for consideration is whether cloud service providers can be held strictly liable for tenant data transmissions without affirmative proof of mens rea or knowing intervention.
4. The appellant contends that Section 79 of the Information Technology Act grants complete safe-harbor immunity to intermediaries unless direct involvement in unlawful acts is established. The respondent State argues that failure to report anomalous egress traffic violates prescribed security guidelines.
5. Having heard both parties, this Court reasons that statutory intermediary protections under Section 79 cannot be diluted by administrative guidelines absent statutory amendment. Mere hosting without active modification does not establish culpability.
6. Consequently, the appeal is allowed. The impugned High Court order is set aside.`;

export default function CaseAnalyzerPage() {
  const [judgmentText, setJudgmentText] = useState('');
  const [includeSpans, setIncludeSpans] = useState(true);

  // Extraction state
  const [extractingPdf, setExtractingPdf] = useState(false);
  const [pdfExtractInfo, setPdfExtractInfo] = useState(null);
  const [extractError, setExtractError] = useState(null);

  // Analysis state
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisError, setAnalysisError] = useState(null);
  const [caseResult, setCaseResult] = useState(null);

  const fileInputRef = useRef(null);

  const charCount = judgmentText.length;
  const canAnalyze = charCount >= 20 && !analyzing;

  async function handleFileUpload(e) {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.name.toLowerCase().endsWith('.pdf')) {
      setExtractError(new Error('Please select a valid PDF document (.pdf).'));
      return;
    }

    setExtractingPdf(true);
    setExtractError(null);
    setPdfExtractInfo(null);

    try {
      const response = await extractPdfDocument(file);
      setPdfExtractInfo(response);
      setJudgmentText(response.extracted_text || '');
    } catch (err) {
      setExtractError(err);
    } finally {
      setExtractingPdf(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  }

  async function handleAnalyzeCase() {
    if (!canAnalyze) return;

    setAnalyzing(true);
    setAnalysisError(null);

    try {
      const response = await analyzeCase({
        text: judgmentText.trim(),
        includeSpans,
      });
      setCaseResult(response);
    } catch (err) {
      setAnalysisError(err);
      setCaseResult(null);
    } finally {
      setAnalyzing(false);
    }
  }

  return (
    <div>
      <div className="page-header">
        <h1>Case Analyzer</h1>
        <p>
          Extract material facts, legal issues, party arguments, court reasoning, and outcomes from court judgments.
        </p>
      </div>

      {/* PDF Upload Card */}
      <div className="card">
        <h3 style={{ fontSize: '15px', marginBottom: 6 }}>Option A: Upload Court Judgment (PDF)</h3>
        <p style={{ fontSize: '13px', color: 'var(--text-muted)', marginBottom: 12 }}>
          Upload a court order or judgment in PDF format to load and inspect its text.
        </p>

        <div className="pdf-upload-box">
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,application/pdf"
            onChange={handleFileUpload}
            style={{ display: 'none' }}
            id="pdf-file-input"
            disabled={extractingPdf}
          />
          <label htmlFor="pdf-file-input" className="btn btn-secondary" style={{ cursor: 'pointer' }}>
            {extractingPdf ? 'Reading PDF...' : 'Choose PDF File'}
          </label>
          <div style={{ fontSize: '12px', color: 'var(--text-light)', marginTop: 8 }}>
            Supports PDF files up to 10 MB. Extracted text will appear in the box below.
          </div>
        </div>

        <ErrorAlert error={extractError} onDismiss={() => setExtractError(null)} />

        {pdfExtractInfo && (
          <div className="alert alert-success" style={{ marginBottom: 0, fontSize: '13px' }}>
            <strong>Document loaded:</strong> Read text from <strong>{pdfExtractInfo.filename}</strong> ({pdfExtractInfo.page_count} page{pdfExtractInfo.page_count === 1 ? '' : 's'}). You can review or edit the text below before analyzing.
          </div>
        )}
      </div>

      {/* Text Input Card */}
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
          <h3 style={{ fontSize: '15px', margin: 0 }}>Option B: Paste or Type Judgment Text</h3>
          <button
            type="button"
            className="sample-btn"
            onClick={() => {
              setJudgmentText(SAMPLE_JUDGMENT);
              setAnalysisError(null);
            }}
          >
            Load Example Judgment
          </button>
        </div>

        <textarea
          rows={10}
          placeholder="Paste or edit judgment text here..."
          value={judgmentText}
          onChange={(e) => setJudgmentText(e.target.value)}
          disabled={analyzing}
        />

        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 4 }}>
          <label style={{ fontSize: '13px', display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer' }}>
            <input
              type="checkbox"
              checked={includeSpans}
              onChange={(e) => setIncludeSpans(e.target.checked)}
              disabled={analyzing}
              style={{ width: 'auto' }}
            />
            <span>Highlight supporting text references</span>
          </label>
          <div className="char-counter">
            {charCount.toLocaleString()} characters
          </div>
        </div>

        <div style={{ textAlign: 'right', marginTop: 12 }}>
          <button
            type="button"
            className="btn btn-primary"
            disabled={!canAnalyze}
            onClick={handleAnalyzeCase}
          >
            {analyzing ? 'Analyzing judgment...' : 'Analyze Case'}
          </button>
        </div>
      </div>

      <ErrorAlert error={analysisError} onDismiss={() => setAnalysisError(null)} />

      {/* Results View */}
      {caseResult && (
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
            <h2 style={{ margin: 0 }}>Case Analysis Findings</h2>
          </div>

          {/* Case Metadata */}
          {caseResult.case_metadata && (
            <div className="card">
              <h3 style={{ marginBottom: 12 }}>Case Details</h3>
              <div className="grid-2" style={{ fontSize: '13.5px' }}>
                <div>
                  <strong>Case Title:</strong> {caseResult.case_metadata.title || 'Not identified'}
                </div>
                <div>
                  <strong>Citation:</strong> {caseResult.case_metadata.citation || 'Not identified'}
                </div>
                <div>
                  <strong>Court:</strong> {caseResult.case_metadata.court || 'Not identified'}
                </div>
                <div>
                  <strong>Decision Date:</strong> {caseResult.case_metadata.decision_date || 'Not identified'}
                </div>
              </div>
              {caseResult.case_metadata.parties && caseResult.case_metadata.parties.length > 0 && (
                <div style={{ marginTop: 10, fontSize: '13.5px' }}>
                  <strong>Parties Involved: </strong>
                  {caseResult.case_metadata.parties.join(', ')}
                </div>
              )}
            </div>
          )}

          {/* Material Facts */}
          {caseResult.material_facts && caseResult.material_facts.length > 0 && (
            <div className="card">
              <div className="card-header">
                <h3 style={{ margin: 0 }}>Material Facts</h3>
                <span className="badge badge-info">{caseResult.material_facts.length} facts</span>
              </div>
              <ul style={{ paddingLeft: 18, margin: 0, fontSize: '13.5px' }}>
                {caseResult.material_facts.map((item, idx) => (
                  <li key={idx} style={{ marginBottom: 6 }}>
                    {item.text}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Legal Issues */}
          {caseResult.legal_issues && caseResult.legal_issues.length > 0 && (
            <div className="card">
              <div className="card-header">
                <h3 style={{ margin: 0 }}>Legal Issues</h3>
                <span className="badge badge-info">{caseResult.legal_issues.length} issues</span>
              </div>
              <ul style={{ paddingLeft: 18, margin: 0, fontSize: '13.5px' }}>
                {caseResult.legal_issues.map((item, idx) => (
                  <li key={idx} style={{ marginBottom: 6 }}>
                    {item.text}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Cited Statutory Provisions */}
          {caseResult.cited_provisions && caseResult.cited_provisions.length > 0 && (
            <div className="card">
              <div className="card-header">
                <h3 style={{ margin: 0 }}>Cited Legal Provisions</h3>
                <span className="badge badge-neutral">{caseResult.cited_provisions.length} provisions</span>
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                {caseResult.cited_provisions.map((item, idx) => (
                  <span key={idx} className="badge badge-info" style={{ padding: '4px 10px', fontSize: '13px' }}>
                    {item.text}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Party Arguments */}
          {caseResult.party_arguments && (
            <div className="card">
              <h3 style={{ marginBottom: 8 }}>Arguments Presented</h3>
              <div className="case-arguments-grid">
                <div className="argument-column">
                  <h4>Appellant / Petitioner Arguments</h4>
                  {caseResult.party_arguments.petitioner_arguments &&
                  caseResult.party_arguments.petitioner_arguments.length > 0 ? (
                    <ul style={{ paddingLeft: 16, margin: 0, fontSize: '13px' }}>
                      {caseResult.party_arguments.petitioner_arguments.map((arg, idx) => (
                        <li key={idx} style={{ marginBottom: 6 }}>
                          {arg.text}
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <span style={{ fontSize: '13px', color: 'var(--text-light)' }}>
                      No specific appellant arguments identified.
                    </span>
                  )}
                </div>

                <div className="argument-column">
                  <h4>Respondent Arguments</h4>
                  {caseResult.party_arguments.respondent_arguments &&
                  caseResult.party_arguments.respondent_arguments.length > 0 ? (
                    <ul style={{ paddingLeft: 16, margin: 0, fontSize: '13px' }}>
                      {caseResult.party_arguments.respondent_arguments.map((arg, idx) => (
                        <li key={idx} style={{ marginBottom: 6 }}>
                          {arg.text}
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <span style={{ fontSize: '13px', color: 'var(--text-light)' }}>
                      No specific respondent arguments identified.
                    </span>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Court Reasoning */}
          {caseResult.court_reasoning && caseResult.court_reasoning.length > 0 && (
            <div className="card">
              <div className="card-header">
                <h3 style={{ margin: 0 }}>Court Reasoning</h3>
                <span className="badge badge-info">{caseResult.court_reasoning.length} points</span>
              </div>
              <ul style={{ paddingLeft: 18, margin: 0, fontSize: '13.5px' }}>
                {caseResult.court_reasoning.map((item, idx) => (
                  <li key={idx} style={{ marginBottom: 6 }}>
                    {item.text}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Final Outcome */}
          {caseResult.outcome && (
            <div className="card" style={{ borderLeft: '4px solid var(--primary)' }}>
              <h3 style={{ marginBottom: 6 }}>Final Decision / Outcome</h3>
              <div style={{ fontSize: '14.5px', color: 'var(--text-main)' }}>
                {caseResult.outcome.text}
              </div>
            </div>
          )}

          {/* Key Takeaways */}
          {caseResult.key_takeaways && caseResult.key_takeaways.length > 0 && (
            <div className="card">
              <h3 style={{ marginBottom: 8 }}>Key Takeaways</h3>
              <ul style={{ paddingLeft: 18, margin: 0, fontSize: '13.5px' }}>
                {caseResult.key_takeaways.map((takeaway, idx) => (
                  <li key={idx} style={{ marginBottom: 4 }}>
                    {takeaway}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Warnings / Notes */}
          {caseResult.warnings && caseResult.warnings.length > 0 && (
            <div className="alert alert-warning">
              <strong>Notes on this Document:</strong>
              <ul style={{ paddingLeft: 18, margin: '4px 0 0 0', fontSize: '13px' }}>
                {caseResult.warnings.map((w, idx) => (
                  <li key={idx}>{w}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
