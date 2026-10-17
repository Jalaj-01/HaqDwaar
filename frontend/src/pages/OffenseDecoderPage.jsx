import React, { useState } from 'react';
import { analyzeOffense } from '../services/api';
import ErrorAlert from '../components/ErrorAlert';

const SAMPLE_INCIDENTS = [
  {
    label: 'Online Impersonation',
    text: 'A person created a fraudulent social media account pretending to be an authorized bank officer and deceived customers into transferring funds into an unauthorized account.',
  },
  {
    label: 'Unauthorized Data Copying',
    text: 'An unauthorized user accessed a protected company server, extracted proprietary software code, and copied confidential customer databases without permission.',
  },
  {
    label: 'Misappropriation of Property',
    text: 'A person found a gold necklace on the road, knew the true owner who had just dropped it, but dishonestly converted it to their own use and sold it.',
  },
  {
    label: 'Everyday Activity (No Legal Offense)',
    text: 'I went for a routine morning walk in the public park and purchased groceries from the local store.',
  },
];

export default function OffenseDecoderPage() {
  const [incidentText, setIncidentText] = useState('');
  const [topK, setTopK] = useState(5);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  // State for follow-up answers: { [question_id]: answer_text }
  const [followUpAnswers, setFollowUpAnswers] = useState({});

  const charCount = incidentText.length;
  const isTooShort = charCount > 0 && charCount < 10;
  const isTooLong = charCount > 10000;
  const canSubmit = charCount >= 10 && !isTooLong && !loading;

  async function handleAnalyze(customAnswers = null) {
    if (!canSubmit) return;

    setLoading(true);
    setError(null);

    let contextualAnswersList = null;
    if (customAnswers && Object.keys(customAnswers).length > 0) {
      contextualAnswersList = Object.entries(customAnswers)
        .filter(([, ans]) => ans && ans.trim().length > 0)
        .map(([qId, ans]) => ({ question_id: qId, answer: ans.trim() }));
    }

    try {
      const response = await analyzeOffense({
        incidentText: incidentText.trim(),
        contextualAnswers: contextualAnswersList,
        topK: Number(topK),
      });
      setResult(response);
      setFollowUpAnswers({});
    } catch (err) {
      setError(err);
      setResult(null);
    } finally {
      setLoading(false);
    }
  }

  function handleFollowUpSubmit(e) {
    e.preventDefault();
    handleAnalyze(followUpAnswers);
  }

  function getElementStatusBadge(status) {
    switch (status) {
      case 'supported':
        return <span className="badge badge-success">Supported by facts</span>;
      case 'contradicted':
        return <span className="badge badge-danger">Contradicted</span>;
      case 'not_established':
        return <span className="badge badge-warning">Not established</span>;
      case 'not_evaluated':
      default:
        return <span className="badge badge-neutral">Needs clarification</span>;
    }
  }

  return (
    <div>
      <div className="page-header">
        <h1>Legal Offense Decoder</h1>
        <p>
          Describe an incident in everyday language to identify potentially relevant legal provisions and see how the facts match statutory requirements.
        </p>
      </div>

      <div className="card">
        <label htmlFor="incident-input" style={{ display: 'block', fontWeight: 600, marginBottom: 6 }}>
          Incident Description
        </label>
        
        <div className="sample-pills">
          <span>Try an example:</span>
          {SAMPLE_INCIDENTS.map((sample, idx) => (
            <button
              key={idx}
              type="button"
              className="sample-btn"
              onClick={() => {
                setIncidentText(sample.text);
                setError(null);
              }}
            >
              {sample.label}
            </button>
          ))}
        </div>

        <textarea
          id="incident-input"
          rows={5}
          placeholder="Describe what happened in your own words (at least 10 characters)..."
          value={incidentText}
          onChange={(e) => setIncidentText(e.target.value)}
          disabled={loading}
        />

        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 4 }}>
          <div>
            {isTooShort && (
              <span style={{ fontSize: '12px', color: 'var(--danger-text)' }}>
                Please enter at least 10 characters to analyze.
              </span>
            )}
            {isTooLong && (
              <span style={{ fontSize: '12px', color: 'var(--danger-text)' }}>
                Text exceeds maximum allowed length of 10,000 characters.
              </span>
            )}
          </div>
          <div className="char-counter">
            {charCount.toLocaleString()} / 10,000 characters
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: 12, flexWrap: 'wrap', gap: 12 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <label htmlFor="top-k-select" style={{ fontSize: '13px', color: 'var(--text-muted)' }}>
              Number of provisions to show:
            </label>
            <select
              id="top-k-select"
              value={topK}
              onChange={(e) => setTopK(e.target.value)}
              style={{ width: '80px', padding: '4px 8px', fontSize: '13px' }}
              disabled={loading}
            >
              <option value={3}>3</option>
              <option value={5}>5</option>
              <option value={10}>10</option>
            </select>
          </div>

          <button
            type="button"
            className="btn btn-primary"
            disabled={!canSubmit}
            onClick={() => handleAnalyze(null)}
          >
            {loading ? 'Analyzing incident...' : 'Analyze Incident'}
          </button>
        </div>
      </div>

      <ErrorAlert error={error} onDismiss={() => setError(null)} />

      {/* Results View */}
      {result && (
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
            <h2 style={{ margin: 0 }}>Analysis Findings</h2>
          </div>

          {/* No Relevant Match State */}
          {result.no_reliable_match ? (
            <div className="alert alert-warning" style={{ padding: '16px 20px', marginBottom: 20 }}>
              <h3 style={{ color: 'var(--warning-text)', marginBottom: 6 }}>
                No sufficiently relevant legal provision was found.
              </h3>
              <p style={{ color: 'var(--warning-text)', marginBottom: 4 }}>
                The details provided do not strongly correspond to any legal offense in our reference statutes.
              </p>
              <p style={{ fontSize: '13px', color: 'var(--warning-text)', marginBottom: 0 }}>
                This happens when an incident appears non-criminal, is missing key details, or falls outside the covered laws.
              </p>
            </div>
          ) : (
            <>
              {/* Identified Facts Section */}
              {result.extracted_facts && result.extracted_facts.length > 0 && (
                <div className="card">
                  <div className="card-header">
                    <h3 style={{ margin: 0 }}>Key Facts from the Incident</h3>
                    <span className="badge badge-info">{result.extracted_facts.length} facts identified</span>
                  </div>
                  <div className="table-container">
                    <table>
                      <thead>
                        <tr>
                          <th style={{ width: '25%' }}>Person / Action</th>
                          <th style={{ width: '45%' }}>Stated Detail</th>
                          <th style={{ width: '30%' }}>Supporting Text</th>
                        </tr>
                      </thead>
                      <tbody>
                        {result.extracted_facts.map((fact, index) => (
                          <tr key={index}>
                            <td>
                              <strong>{fact.actor || 'Unspecified person'}</strong>
                              {fact.action && <div style={{ fontSize: '12px', color: 'var(--text-light)' }}>{fact.action}</div>}
                            </td>
                            <td>{fact.description}</td>
                            <td>
                              {fact.evidence_span?.text ? (
                                <span style={{ fontStyle: 'italic', fontSize: '12px', color: 'var(--text-muted)' }}>
                                  "{fact.evidence_span.text}"
                                </span>
                              ) : (
                                <span style={{ color: 'var(--text-light)', fontSize: '12px' }}>—</span>
                              )}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* Incident Categories */}
              {result.incident_categories && result.incident_categories.length > 0 && (
                <div style={{ marginBottom: 16 }}>
                  <span style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-muted)', marginRight: 8 }}>
                    Identified Topics:
                  </span>
                  {result.incident_categories.map((cat, idx) => (
                    <span
                      key={idx}
                      className="badge badge-info"
                      style={{ marginRight: 6, marginBottom: 4 }}
                      title={cat.rationale}
                    >
                      {cat.label}
                    </span>
                  ))}
                </div>
              )}

              {/* Potentially Relevant Provisions */}
              <div style={{ marginBottom: 20 }}>
                <h3 style={{ marginBottom: 12 }}>
                  Potentially Relevant Legal Provisions ({result.candidate_provisions?.length || 0})
                </h3>

                {result.candidate_provisions?.map((prov, idx) => (
                  <div key={idx} className="provision-card">
                    <div className="provision-header">
                      <div>
                        <div className="provision-title">
                          {prov.act_name} — {prov.section_id}: {prov.title}
                        </div>
                      </div>
                      <div className="provision-scores">
                        <span className="badge badge-info">
                          Relevant Match
                        </span>
                      </div>
                    </div>

                    <div className="provision-body">
                      {/* Source Information */}
                      <div className="provision-meta">
                        <div>
                          <strong>Jurisdiction:</strong> {prov.jurisdiction || 'India'}
                        </div>
                        <div>
                          <strong>Source:</strong> {prov.source_authority || 'Official Gazette'}
                        </div>
                        {prov.official_source_url && (
                          <div>
                            <a
                              href={prov.official_source_url}
                              target="_blank"
                              rel="noopener noreferrer"
                              style={{ color: 'var(--primary)', fontSize: '12px' }}
                            >
                              Official Statute Text ↗
                            </a>
                          </div>
                        )}
                      </div>

                      {/* Summary */}
                      {prov.plain_language_summary && (
                        <p style={{ fontSize: '14px', marginBottom: 8 }}>
                          <strong>Summary:</strong> {prov.plain_language_summary}
                        </p>
                      )}

                      {/* Penalty */}
                      {prov.penalty_displayed ? (
                        <div className="penalty-box">
                          <strong>Prescribed Penalty:</strong> {prov.penalty_displayed}
                        </div>
                      ) : (
                        <div className="penalty-box suppressed">
                          <strong>Prescribed Penalty:</strong> Penalty details pending official statutory verification.
                        </div>
                      )}

                      {/* Required Legal Elements */}
                      {prov.element_matches && prov.element_matches.length > 0 && (
                        <div style={{ marginTop: 16 }}>
                          <h4 style={{ fontSize: '13.5px', marginBottom: 8, color: 'var(--text-main)' }}>
                            Required Legal Elements ({prov.supported_elements_count} supported,{' '}
                            {prov.missing_elements_count} unestablished,{' '}
                            {prov.contradicted_elements_count} contradicted)
                          </h4>

                          {prov.element_matches.map((elem, eIdx) => (
                            <div key={eIdx} className="element-match-item">
                              <div className="element-match-header">
                                <span className="element-id-label">Element {eIdx + 1}</span>
                                {getElementStatusBadge(elem.status)}
                              </div>
                              <div style={{ fontSize: '13.5px', marginBottom: 4, color: 'var(--text-main)' }}>
                                {elem.description}
                              </div>
                              <div className="element-reasoning">
                                <strong>Assessment:</strong> {elem.reasoning}
                              </div>
                              {elem.evidence_spans && elem.evidence_spans.length > 0 && (
                                <div style={{ marginTop: 4, fontSize: '12px', color: 'var(--text-muted)' }}>
                                  <strong>Found in text: </strong>
                                  {elem.evidence_spans.map((sp, sIdx) => (
                                    <span key={sIdx} style={{ fontStyle: 'italic', marginRight: 6 }}>
                                      "{sp.text}"
                                    </span>
                                  ))}
                                </div>
                              )}
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </>
          )}

          {/* Follow-up Clarification Questions */}
          {result.follow_up_questions && result.follow_up_questions.length > 0 && (
            <div className="followup-box">
              <h3 style={{ fontSize: '15px', color: '#1e3a8a', marginBottom: 6 }}>
                Questions to Clarify Missing Details
              </h3>
              <p style={{ fontSize: '13.5px', color: '#1e40af', marginBottom: 12 }}>
                Some details were not mentioned in your incident description. Answering the questions below can help refine the analysis:
              </p>

              <form onSubmit={handleFollowUpSubmit}>
                {result.follow_up_questions.map((q, idx) => (
                  <div key={q.question_id || idx} className="question-item">
                    <div style={{ fontWeight: 600, fontSize: '13.5px', color: '#1e3a8a', marginBottom: 4 }}>
                      {q.question_text}
                    </div>
                    {q.context_note && (
                      <div style={{ fontSize: '12px', color: '#3b82f6', marginBottom: 6 }}>
                        Why this matters: {q.context_note}
                      </div>
                    )}
                    <input
                      type="text"
                      placeholder="Type your response to clarify this point..."
                      value={followUpAnswers[q.question_id] || ''}
                      onChange={(e) =>
                        setFollowUpAnswers({
                          ...followUpAnswers,
                          [q.question_id]: e.target.value,
                        })
                      }
                      disabled={loading}
                      style={{ fontSize: '13px' }}
                    />
                  </div>
                ))}

                <button
                  type="submit"
                  className="btn btn-primary btn-sm"
                  style={{ marginTop: 12 }}
                  disabled={loading}
                >
                  {loading ? 'Re-evaluating...' : 'Submit Answers & Re-evaluate'}
                </button>
              </form>
            </div>
          )}

          {/* Points of Caution */}
          {result.uncertainty_notes && result.uncertainty_notes.length > 0 && (
            <div className="alert alert-info" style={{ marginBottom: 16 }}>
              <div style={{ fontWeight: 600, marginBottom: 4 }}>Important Notes:</div>
              <ul style={{ paddingLeft: 18, margin: 0, fontSize: '13px' }}>
                {result.uncertainty_notes.map((note, idx) => (
                  <li key={idx}>{note}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Legal Disclaimer */}
          {result.disclaimer && (
            <div
              style={{
                borderTop: '1px solid var(--border-color)',
                paddingTop: 12,
                fontSize: '12px',
                color: 'var(--text-light)',
                fontStyle: 'italic',
              }}
            >
              <strong>Disclaimer:</strong> {result.disclaimer}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
