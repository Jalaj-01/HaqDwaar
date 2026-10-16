import React from 'react';

export default function Navbar({ currentTab, onSelectTab }) {
  return (
    <nav className="navbar" aria-label="Main Navigation">
      <div className="navbar-inner">
        <a
          href="#home"
          className="brand"
          onClick={(e) => {
            e.preventDefault();
            onSelectTab('home');
          }}
        >
          <span>LexiLaw</span>
        </a>

        <ul className="nav-links">
          <li>
            <button
              type="button"
              className={`nav-btn ${currentTab === 'home' ? 'active' : ''}`}
              onClick={() => onSelectTab('home')}
            >
              Home
            </button>
          </li>
          <li>
            <button
              type="button"
              className={`nav-btn ${currentTab === 'offense' ? 'active' : ''}`}
              onClick={() => onSelectTab('offense')}
            >
              Offense Decoder
            </button>
          </li>
          <li>
            <button
              type="button"
              className={`nav-btn ${currentTab === 'language' ? 'active' : ''}`}
              onClick={() => onSelectTab('language')}
            >
              Legal Language
            </button>
          </li>
          <li>
            <button
              type="button"
              className={`nav-btn ${currentTab === 'case' ? 'active' : ''}`}
              onClick={() => onSelectTab('case')}
            >
              Case Analyzer
            </button>
          </li>
        </ul>
      </div>
    </nav>
  );
}
