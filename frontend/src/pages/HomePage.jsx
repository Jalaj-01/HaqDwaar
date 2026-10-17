import React from 'react';

export default function HomePage({ onSelectTab }) {
  return (
    <div>
      <div className="home-hero">
        <h2>LexiLaw: Understand Indian Laws and Legal Texts</h2>
        <p>
          LexiLaw is a student academic project designed to help make legal texts and statutory provisions
          more accessible. It assists users in identifying relevant legal provisions for real-world incidents,
          simplifying complex legal clauses into plain English, and extracting key points from court judgments.
        </p>
        <p style={{ marginBottom: 0, fontSize: '13.5px', color: 'var(--text-light)' }}>
          Covers key Indian statutes: <strong>Indian Penal Code (1860)</strong>,{' '}
          <strong>Information Technology Act (2000)</strong>, and{' '}
          <strong>Digital Personal Data Protection Act (2023)</strong>.
        </p>
      </div>

      <div className="modules-grid">
        <div className="module-card">
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
              <span className="badge badge-info">Module 1</span>
              <h3>Legal Offense Decoder</h3>
            </div>
            <p>
              Describe an incident in everyday words. LexiLaw extracts the main facts, identifies relevant
              sections of Indian law, and checks whether the specific legal elements required for each offense
              are supported by the details you provided.
            </p>
          </div>
          <button
            type="button"
            className="btn btn-primary"
            onClick={() => onSelectTab('offense')}
          >
            Open Offense Decoder →
          </button>
        </div>

        <div className="module-card">
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
              <span className="badge badge-info">Module 2</span>
              <h3>Legal Language</h3>
            </div>
            <p>
              Convert dense legal text into clear, everyday English, or draft formal legal statements from plain
              descriptions. The system includes automated checks to ensure dates, amounts, and critical details
              are preserved accurately.
            </p>
          </div>
          <button
            type="button"
            className="btn btn-primary"
            onClick={() => onSelectTab('language')}
          >
            Open Legal Language →
          </button>
        </div>
      </div>

      <div className="supporting-section">
        <div>
          <h4>Case Analyzer</h4>
          <p>
            Review court judgments and orders by uploading a PDF or pasting the text. The tool organizes the
            ruling into material facts, legal issues, party arguments, judicial reasoning, and the final decision.
          </p>
        </div>
        <button
          type="button"
          className="btn btn-secondary"
          onClick={() => onSelectTab('case')}
          style={{ whiteSpace: 'nowrap' }}
        >
          Open Case Analyzer →
        </button>
      </div>

      <div className="card" style={{ marginTop: 24, backgroundColor: '#fcfcfc' }}>
        <h3 style={{ fontSize: '15px', marginBottom: 8 }}>How LexiLaw Works</h3>
        <ul style={{ paddingLeft: 20, fontSize: '13.5px', color: 'var(--text-muted)', lineHeight: '1.7' }}>
          <li>
            <strong>Responsible Matching:</strong> The system only suggests legal provisions when there is a meaningful connection to your described incident, avoiding misleading or random recommendations.
          </li>
          <li>
            <strong>Element-by-Element Review:</strong> Rather than just matching keywords, offenses are evaluated element by element to show which parts are supported, unproven, or missing.
          </li>
          <li>
            <strong>Verified Statutory Citations:</strong> Displays official legal references and links to India Code legislation so you can verify the original text.
          </li>
          <li>
            <strong>Fact Preservation Checks:</strong> Verifies that essential information like names, monetary figures, and deadlines are preserved without distortion during language transformation.
          </li>
        </ul>
      </div>
    </div>
  );
}
