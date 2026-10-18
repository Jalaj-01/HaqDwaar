import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import HomePage from './pages/HomePage';
import OffenseDecoderPage from './pages/OffenseDecoderPage';
import LegalLanguagePage from './pages/LegalLanguagePage';
import CaseAnalyzerPage from './pages/CaseAnalyzerPage';
import { checkBackendHealth } from './services/api';
import './App.css';

function normalizeTab(raw) {
  const clean = (raw || '').replace(/^[#/]+/, '').toLowerCase();
  if (clean.startsWith('offense')) return 'offense';
  if (clean.startsWith('language') || clean.startsWith('legal')) return 'language';
  if (clean.startsWith('case')) return 'case';
  return 'home';
}

export default function App() {
  const [currentTab, setCurrentTab] = useState(() => normalizeTab(window.location.hash));

  useEffect(() => {
    // Proactively ping health endpoint to wake up backend if spinning down
    checkBackendHealth().catch(() => {});

    function handleHashChange() {
      setCurrentTab(normalizeTab(window.location.hash));
    }

    window.addEventListener('hashchange', handleHashChange);
    return () => window.removeEventListener('hashchange', handleHashChange);
  }, []);

  function handleSelectTab(tab) {
    setCurrentTab(tab);
    window.location.hash = tab;
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  return (
    <div className="app-container">
      <Navbar currentTab={currentTab} onSelectTab={handleSelectTab} />

      <main className="main-content">
        {currentTab === 'home' && <HomePage onSelectTab={handleSelectTab} />}
        {currentTab === 'offense' && <OffenseDecoderPage />}
        {currentTab === 'language' && <LegalLanguagePage />}
        {currentTab === 'case' && <CaseAnalyzerPage />}
      </main>

      <footer className="footer">
        <div style={{ maxWidth: 1080, margin: '0 auto' }}>
          <div style={{ fontWeight: 600 }}>
            LexiLaw — Student Academic Legal Project
          </div>
          <div style={{ fontSize: '12px', marginTop: 4, color: 'var(--text-light)' }}>
            Disclaimer: LexiLaw is an academic research prototype intended for informational purposes only. It does not provide formal legal representation, opinions, or advice.
          </div>
        </div>
      </footer>
    </div>
  );
}
