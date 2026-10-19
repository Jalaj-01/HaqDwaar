# LexiLaw Frontend — Academic Legal NLP Interface

Clean, minimal, readable web interface for the **LexiLaw** M.Tech Natural Language Processing academic project.

Built with **React**, **Vite**, and **Vanilla CSS** without heavy CSS frameworks, commercial SaaS bloat, or excessive dashboard decorations.

---

## 1. Project Architecture

The frontend maps directly to the LexiLaw backend modules:

```
frontend/
├── src/
│   ├── components/
│   │   ├── Navbar.jsx         # Simple top navigation with clean text links
│   │   └── ErrorAlert.jsx     # Clean user-facing error messages in plain language
│   ├── pages/
│   │   ├── HomePage.jsx           # Clean overview and module navigation cards
│   │   ├── OffenseDecoderPage.jsx # Module 1: Incident analysis, element matching, follow-up questions
│   │   ├── LegalLanguagePage.jsx  # Module 2: Bi-directional translation, preservation check, glossary lookup
│   │   └── CaseAnalyzerPage.jsx   # Supporting feature: Case judgment text analysis and PDF extraction
│   ├── services/
│   │   └── api.js             # Reusable client with error parsing & console diagnostics
│   ├── App.jsx                # Main application container with tab hash routing
│   ├── App.css                # Component-specific styles
│   ├── index.css              # Base styling and design tokens
│   └── main.jsx               # Application entry point
├── .env                       # Local environment variables
├── .env.example               # Template environment configuration
└── package.json
```

---

## 2. API Configuration

The API client reads the backend URL from the Vite environment variable:

- `VITE_API_BASE_URL` (default: `http://127.0.0.1:8000`)

To change the backend address, edit `.env`:
```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

---

## 3. Endpoints Integrated

| Module | Backend Endpoint | HTTP Method | Payload / Response |
| :--- | :--- | :--- | :--- |
| **System** | `/api/v1/status` | `GET` | Component readiness, corpus count, limits |
| **Module 1** | `/api/v1/offense/analyze` | `POST` | Incident text, top_k, contextual follow-up answers |
| **Module 2** | `/api/v1/legal-language/transform` | `POST` | Text, mode (`legal_to_normal` / `normal_to_legal`), context |
| **Module 2** | `/api/v1/legal-language/terms/{term}` | `GET` | Legal term definition, plain meaning, statutory context |
| **Supporting**| `/api/v1/documents/extract` | `POST` | Multipart PDF upload, PyMuPDF page text extraction |
| **Supporting**| `/api/v1/legal-language/analyze-case` | `POST` | Judgment text, include_spans boolean |

---

## 4. Running Locally

### Prerequisites
- Node.js (v18+)
- Running LexiLaw backend (`uvicorn main:app --host 127.0.0.1 --port 8000` from `backend/`)

### Setup & Run
```bash
# 1. Install dependencies
npm install

# 2. Run local development server
npm run dev

# 3. Build for production
npm run build

# 4. Preview production build
npm run preview
```

---

## 5. Academic Viva Talking Points

1. **Why Plain CSS and No UI Library?**
   - The interface is designed as an honest, student-built academic prototype. Avoiding heavyweight component libraries keeps the bundle light, ensures transparent DOM structure, and eliminates visual bloat.
2. **How is the No-Reliable-Match Handled?**
   - When the hybrid BM25 + dense retrieval score falls below the empirically calibrated threshold ($\tau = 0.12$), the frontend clearly renders a designated warning rather than displaying low-scoring false positives.
3. **How Does the Element-Level Evaluation Work?**
   - For every candidate provision, the UI breaks down statutory elements into discrete statuses: *Supported*, *Unestablished*, or *Contradicted*, with reasoning and character evidence spans.
4. **Safety Guardrails:**
   - For provisional or unverified statutory entries (such as Section 33 DPDP Act), penalty text is suppressed in the backend and explicitly rendered as a cautionary note in the frontend.
