import React, { useState } from 'react';
import { transformLegalLanguage, getLegalTerm } from '../services/api';
import ErrorAlert from '../components/ErrorAlert';

const SAMPLE_TEXTS = {
  legal_to_normal: {
    label: 'Indemnity Clause',
    text: 'The licensee shall indemnify, defend, and hold harmless the licensor and its affiliates from and against any and all claims, liabilities, losses, damages, or costs incurred on or before October 15, 2024 exceeding the sum of INR 500,000 arising out of any breach of warranty.',
  },
  normal_to_legal: {
    label: 'Business Contract Notice',
    text: 'If the contractor does not deliver the completed software by 15 December 2024, they must pay a penalty of INR 10,000 for each day of delay, and the client may terminate the agreement immediately.',
  },
};

const COMMON_TERMS = ['mens rea', 'affidavit', 'indemnity', 'estoppel', 'injunction', 'prima facie'];

export default function LegalLanguagePage() {
  const [inputText, setInputText] = useState('');
  const [mode, setMode] = useState('legal_to_normal'); // 'legal_to_normal' | 'normal_to_legal'
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const [copied, setCopied] = useState(false);

  // Terminology Lookup state
  const [lookupTerm, setLookupTerm] = useState('');
  const [termLoading, setTermLoading] = useState(false);
  const [termResult, setTermResult] = useState(null);
  const [termError, setTermError] = useState(null);

  const charCount = inputText.length;
  const canSubmit = charCount >= 5 && !loading;

  async function handleTransform() {
    if (!canSubmit) return;

    setLoading(true);
    setError(null);
    setCopied(false);

    try {
      const response = await transformLegalLanguage({
        text: inputText.trim(),
        mode,
      });
      setResult(response);
    } catch (err) {
      setError(err);
      setResult(null);
    } finally {
      setLoading(false);
    }
  }

  async function handleTermLookup(termToQuery) {
    const term = (termToQuery || lookupTerm).trim();
    if (!term) return;

    setTermLoading(true);
    setTermError(null);
    setTermResult(null);

    try {
      const data = await getLegalTerm(term);
      setTermResult(data);
    } catch (err) {
      if (err.status === 404) {
        setTermError(new Error(`No definition was found for "${term}". Please try another word or phrase.`));
      } else {
        setTermError(err);
      }
    } finally {
      setTermLoading(false);
    }
  }

  function handleCopyOutput() {
    if (result?.transformed_text) {
      navigator.clipboard.writeText(result.transformed_text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  }

  return (
    <div>
      <div className="page-header">
        <h1>Legal Language</h1>
        <p>
          Convert between complex legal language and plain English, ensuring important facts, dates, and terms are preserved.
        </p>
      </div>

      <div className="card">
        {/* Mode Selector */}
        <div style={{ marginBottom: 16 }}>
          <label style={{ display: 'block', fontWeight: 600, marginBottom: 6 }}>
            Select Direction
          </label>
          <div className="mode-toggle-group">
            <button
              type="button"
              className={`mode-toggle-btn ${mode === 'legal_to_normal' ? 'active' : ''}`}
              onClick={() => {
                setMode('legal_to_normal');
                setError(null);
              }}
            >
              Legal to Normal (Simplify)
            </button>
            <button
              type="button"
              className={`mode-toggle-btn ${mode === 'normal_to_legal' ? 'active' : ''}`}
              onClick={() => {
                setMode('normal_to_legal');
                setError(null);
              }}
            >
              Normal to Legal (Formal Drafting)
            </button>
          </div>
        </div>

        {/* Input Text Area */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
          <label htmlFor="language-input" style={{ fontWeight: 600 }}>
            {mode === 'legal_to_normal' ? 'Original Legal Text' : 'Plain Text to Draft'}
          </label>
          <button
            type="button"
            className="sample-btn"
            onClick={() => {
              setInputText(SAMPLE_TEXTS[mode].text);
              setError(null);
            }}
          >
            Load Example ({SAMPLE_TEXTS[mode].label})
          </button>
        </div>

        <textarea
          id="language-input"
          rows={6}
          placeholder={
            mode === 'legal_to_normal'
              ? 'Paste legal clauses, agreements, or notices to translate into plain English...'
              : 'Write ordinary English text to be converted into formal legal draft...'
          }
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          disabled={loading}
        />

        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 4 }}>
          <span style={{ fontSize: '12px', color: 'var(--text-light)' }}>
            Enter at least 5 characters.
          </span>
          <div className="char-counter">
            {charCount.toLocaleString()} characters
          </div>
        </div>

        <div style={{ marginTop: 12, textAlign: 'right' }}>
          <button
            type="button"
            className="btn btn-primary"
            disabled={!canSubmit}
            onClick={handleTransform}
          >
            {loading ? 'Processing text...' : 'Transform Text'}
          </button>
        </div>
      </div>

      <ErrorAlert error={error} onDismiss={() => setError(null)} />

      {/* Results View */}
      {result && (
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
            <h2 style={{ margin: 0 }}>Result</h2>
          </div>

          {/* Transformed Text Result */}
          <div className="card">
            <div className="card-header">
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <h3 style={{ margin: 0 }}>
                  {result.mode === 'legal_to_normal' ? 'Plain English Translation' : 'Formal Legal Draft'}
                </h3>
                {result.review_status && (
                  <span className="badge badge-warning">
                    {result.review_status === 'provisional_nlp_draft'
                      ? 'Draft generated — please review'
                      : 'Draft generated — please review'}
                  </span>
                )}
              </div>
              <button
                type="button"
                className="btn btn-secondary btn-sm"
                onClick={handleCopyOutput}
              >
                {copied ? '✓ Copied' : 'Copy'}
              </button>
            </div>

            <div className="result-box">
              {result.transformed_text}
            </div>

            {/* Warnings / Notes */}
            {result.warnings && result.warnings.length > 0 && (
              <div className="alert alert-warning" style={{ marginTop: 12, marginBottom: 0 }}>
                <strong>Important Notes:</strong>
                <ul style={{ paddingLeft: 18, marginTop: 4, marginBottom: 0, fontSize: '13px' }}>
                  {result.warnings.map((w, idx) => (
                    <li key={idx}>{w}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          {/* Fact Preservation Report */}
          {result.preservation_checks && (
            <div className="card">
              <div className="card-header">
                <h3 style={{ margin: 0 }}>Fact Preservation Check</h3>
                <span
                  className={`badge ${
                    result.preservation_checks.overall_status === 'preserved'
                      ? 'badge-success'
                      : 'badge-warning'
                  }`}
                >
                  {result.preservation_checks.overall_status === 'preserved'
                    ? 'All Key Details Preserved'
                    : 'Review Recommended'}
                </span>
              </div>

              {/* Boolean Preservation Indicators */}
              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))',
                  gap: 10,
                  marginBottom: 16,
                }}
              >
                <div style={{ padding: '8px 12px', background: '#fafafa', border: '1px solid var(--border-color)', borderRadius: 4 }}>
                  <div style={{ fontSize: '12px', color: 'var(--text-light)' }}>Dates</div>
                  <div style={{ fontWeight: 600, color: result.preservation_checks.dates_preserved ? 'var(--success-text)' : 'var(--danger-text)' }}>
                    {result.preservation_checks.dates_preserved ? '✓ Preserved' : '✗ Unpreserved'}
                  </div>
                </div>

                <div style={{ padding: '8px 12px', background: '#fafafa', border: '1px solid var(--border-color)', borderRadius: 4 }}>
                  <div style={{ fontSize: '12px', color: 'var(--text-light)' }}>Monetary Amounts</div>
                  <div style={{ fontWeight: 600, color: result.preservation_checks.amounts_preserved ? 'var(--success-text)' : 'var(--danger-text)' }}>
                    {result.preservation_checks.amounts_preserved ? '✓ Preserved' : '✗ Unpreserved'}
                  </div>
                </div>

                <div style={{ padding: '8px 12px', background: '#fafafa', border: '1px solid var(--border-color)', borderRadius: 4 }}>
                  <div style={{ fontSize: '12px', color: 'var(--text-light)' }}>Negations</div>
                  <div style={{ fontWeight: 600, color: result.preservation_checks.negation_preserved ? 'var(--success-text)' : 'var(--danger-text)' }}>
                    {result.preservation_checks.negation_preserved ? '✓ Preserved' : '✗ Unpreserved'}
                  </div>
                </div>

                <div style={{ padding: '8px 12px', background: '#fafafa', border: '1px solid var(--border-color)', borderRadius: 4 }}>
                  <div style={{ fontSize: '12px', color: 'var(--text-light)' }}>Qualifiers</div>
                  <div style={{ fontWeight: 600, color: result.preservation_checks.qualifiers_preserved ? 'var(--success-text)' : 'var(--danger-text)' }}>
                    {result.preservation_checks.qualifiers_preserved ? '✓ Preserved' : '✗ Unpreserved'}
                  </div>
                </div>
              </div>

              {/* Preservation Checks Table */}
              {result.preservation_checks.checks && result.preservation_checks.checks.length > 0 && (
                <div className="table-container">
                  <table>
                    <thead>
                      <tr>
                        <th style={{ width: '25%' }}>Check</th>
                        <th style={{ width: '20%' }}>Result</th>
                        <th style={{ width: '55%' }}>Observation</th>
                      </tr>
                    </thead>
                    <tbody>
                      {result.preservation_checks.checks.map((check, idx) => (
                        <tr key={idx}>
                          <td>
                            <strong>{check.category}</strong>
                          </td>
                          <td>
                            <span
                              className={`badge ${
                                check.status === 'preserved' || check.status === 'pass'
                                  ? 'badge-success'
                                  : 'badge-warning'
                              }`}
                            >
                              {check.status === 'preserved' || check.status === 'pass' ? 'Preserved' : 'Review'}
                            </span>
                          </td>
                          <td>{check.detail}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}

              {/* Preserved Entities */}
              {result.preservation_checks.preserved_entities && result.preservation_checks.preserved_entities.length > 0 && (
                <div style={{ fontSize: '13px', marginTop: 8 }}>
                  <strong>Key Names and Entities Identified: </strong>
                  {result.preservation_checks.preserved_entities.map((ent, idx) => (
                    <span key={idx} className="badge badge-neutral" style={{ marginRight: 4 }}>
                      {ent}
                    </span>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Detected Terminology */}
          {result.terminology_explanations && result.terminology_explanations.length > 0 && (
            <div className="card">
              <div className="card-header">
                <h3 style={{ margin: 0 }}>Legal Terms in this Text</h3>
                <span className="badge badge-info">
                  {result.terminology_explanations.length} terms explained
                </span>
              </div>
              <div>
                {result.terminology_explanations.map((termItem, idx) => (
                  <div
                    key={idx}
                    style={{
                      padding: '10px 0',
                      borderBottom: idx < result.terminology_explanations.length - 1 ? '1px solid var(--border-color)' : 'none',
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
                      <strong style={{ fontSize: '14.5px', color: 'var(--text-main)' }}>
                        {termItem.term}
                      </strong>
                    </div>
                    <p style={{ fontSize: '13.5px', marginBottom: 4 }}>
                      <strong>Meaning:</strong> {termItem.plain_language_meaning}
                    </p>
                    {termItem.legal_context && (
                      <p style={{ fontSize: '12.5px', color: 'var(--text-muted)', marginBottom: 2 }}>
                        <strong>Legal Context:</strong> {termItem.legal_context}
                      </p>
                    )}
                    {termItem.source && (
                      <div style={{ fontSize: '11.5px', color: 'var(--text-light)' }}>
                        Source: {termItem.source}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Missing Details */}
          {result.missing_details && result.missing_details.length > 0 && (
            <div className="alert alert-warning">
              <strong>Potential Missing Details:</strong>
              <ul style={{ paddingLeft: 18, margin: '4px 0 0 0', fontSize: '13px' }}>
                {result.missing_details.map((m, idx) => (
                  <li key={idx}>{m}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Simplified Legal Glossary Section */}
      <div className="card" style={{ marginTop: 24, backgroundColor: '#fcfcfc' }}>
        <h3 style={{ marginBottom: 6 }}>Understand a Legal Term</h3>
        <p style={{ fontSize: '13.5px', color: 'var(--text-muted)' }}>
          Explore the meaning of legal words and phrases.
        </p>

        <div className="sample-pills" style={{ marginBottom: 10 }}>
          <span>Common examples:</span>
          {COMMON_TERMS.map((t, idx) => (
            <button
              key={idx}
              type="button"
              className="sample-btn"
              onClick={() => {
                setLookupTerm(t);
                handleTermLookup(t);
              }}
            >
              {t}
            </button>
          ))}
        </div>

        <form
          className="term-search-bar"
          onSubmit={(e) => {
            e.preventDefault();
            handleTermLookup();
          }}
        >
          <input
            type="text"
            placeholder="Enter a legal term"
            value={lookupTerm}
            onChange={(e) => setLookupTerm(e.target.value)}
            disabled={termLoading}
          />
          <button
            type="submit"
            className="btn btn-secondary"
            disabled={termLoading || !lookupTerm.trim()}
          >
            {termLoading ? 'Searching...' : 'Search'}
          </button>
        </form>

        <ErrorAlert error={termError} onDismiss={() => setTermError(null)} />

        {termResult && (
          <div
            style={{
              marginTop: 12,
              padding: 14,
              backgroundColor: '#ffffff',
              border: '1px solid var(--border-color)',
              borderRadius: 'var(--radius-sm)',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 6 }}>
              <h4 style={{ margin: 0, fontSize: '16px' }}>{termResult.term}</h4>
            </div>
            <p style={{ fontSize: '14px', marginBottom: 8 }}>
              <strong>Meaning:</strong> {termResult.plain_language_meaning}
            </p>
            {termResult.legal_context && (
              <p style={{ fontSize: '13px', marginBottom: 6 }}>
                <strong>Legal Context:</strong> {termResult.legal_context}
              </p>
            )}
            {termResult.example_usage && (
              <p style={{ fontSize: '13px', fontStyle: 'italic', color: 'var(--text-muted)', marginBottom: 6 }}>
                "{termResult.example_usage}"
              </p>
            )}
            {termResult.related_terms && termResult.related_terms.length > 0 && (
              <div style={{ fontSize: '12px', color: 'var(--text-light)', marginTop: 6 }}>
                <strong>Related Terms:</strong> {termResult.related_terms.join(', ')}
              </div>
            )}
            {termResult.source && (
              <div style={{ fontSize: '11.5px', color: 'var(--text-light)', marginTop: 4 }}>
                <strong>Source:</strong> {termResult.source}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
