/**
 * LexiLaw API Service
 * 
 * Reusable HTTP client for interacting with the LexiLaw backend.
 * Base URL defaults to http://127.0.0.1:8000.
 */

const API_BASE_URL = (
  (typeof import.meta !== 'undefined' && import.meta.env?.VITE_API_BASE_URL) ||
  'http://127.0.0.1:8000'
).replace(/\/+$/, '');

export class ApiError extends Error {
  constructor(message, status = 0, code = 'API_ERROR', requestId = null, details = null) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.code = code;
    this.requestId = requestId;
    this.details = details;
    Object.setPrototypeOf(this, ApiError.prototype);
  }

  static isApiError(err) {
    return Boolean(
      err && (
        err instanceof ApiError ||
        err.name === 'ApiError' ||
        (typeof err === 'object' && 'status' in err && 'code' in err)
      )
    );
  }
}

/**
 * Helper to process backend error responses consistently.
 * Logs technical details to console and provides clean user-facing messages.
 */
async function parseErrorResponse(response) {
  const status = response.status;
  let errorData = null;
  let text = '';

  try {
    text = await response.text();
    errorData = text ? JSON.parse(text) : null;
  } catch {
    errorData = null;
  }

  // Log technical details for debugging/diagnostics
  if (typeof import.meta !== 'undefined' && import.meta.env?.DEV) {
    console.error(`[LexiLaw API Error] Status ${status}:`, errorData || text);
  }

  // 1. If backend returned a clear structured error message, prioritize it
  if (errorData?.error?.message) {
    return new ApiError(
      errorData.error.message,
      status,
      errorData.error.code || 'BACKEND_ERROR',
      errorData.error.request_id || null,
      errorData.error
    );
  }

  // 2. Handle validation error details if present
  if (errorData?.detail) {
    const detailMsg = typeof errorData.detail === 'string'
      ? errorData.detail
      : "The input details could not be processed. Please check your text and try again.";
    return new ApiError(
      detailMsg,
      status,
      'VALIDATION_ERROR',
      null,
      errorData.detail
    );
  }

  // 3. Status-specific user-friendly fallbacks
  if (status === 404) {
    return new ApiError('No definition found for this term.', 404, 'NOT_FOUND', errorData?.error?.request_id || null);
  }

  if (status === 429) {
    return new ApiError(
      'Too many requests. Please wait a moment before trying again.',
      429,
      'RATE_LIMIT_EXCEEDED',
      errorData?.error?.request_id || null
    );
  }

  if (status === 415) {
    return new ApiError('Please upload a valid PDF document (.pdf).', 415, 'UNSUPPORTED_MEDIA', errorData?.error?.request_id || null);
  }

  if (status === 413) {
    return new ApiError('The uploaded file or request is too large. Maximum supported size is 10 MB.', 413, 'FILE_TOO_LARGE', errorData?.error?.request_id || null);
  }

  return new ApiError(
    "We couldn't complete your request. Please try again.",
    status,
    'HTTP_ERROR',
    null,
    null
  );
}

/**
 * Generic request helper
 */
async function request(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  const defaultHeaders = {};

  if (!(options.body instanceof FormData)) {
    defaultHeaders['Content-Type'] = 'application/json';
  }

  const config = {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
  };

  try {
    const response = await fetch(url, config);

    if (!response.ok) {
      throw await parseErrorResponse(response);
    }

    return await response.json();
  } catch (err) {
    if (ApiError.isApiError(err)) {
      throw err;
    }
    // Network or connection error when server is unreachable or CORS blocked
    console.error('[LexiLaw Connection Error]:', err);
    throw new ApiError(
      'LexiLaw is temporarily unable to connect to the backend server. Please verify the server is running.',
      0,
      'NETWORK_ERROR'
    );
  }
}

/**
 * Module 1: Legal Offense Decoder
 */
export async function analyzeOffense({ incidentText, contextualAnswers = null, topK = 5 }) {
  const payload = {
    incident_text: incidentText,
    contextual_answers: contextualAnswers && contextualAnswers.length > 0 ? contextualAnswers : null,
    top_k: Number(topK) || 5,
  };

  return request('/api/v1/offense/analyze', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

/**
 * Module 2: Legal Language Transformation
 */
export async function transformLegalLanguage({ text, mode, context = null }) {
  const payload = {
    text,
    mode,
    context: context || null,
  };

  return request('/api/v1/legal-language/transform', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

/**
 * Module 2: Legal Term Lookup
 */
export async function getLegalTerm(term) {
  const cleanTerm = encodeURIComponent(term.trim());
  return request(`/api/v1/legal-language/terms/${cleanTerm}`, {
    method: 'GET',
  });
}

/**
 * Supporting Feature: PDF Document Extraction
 */
export async function extractPdfDocument(file) {
  const formData = new FormData();
  formData.append('file', file);

  return request('/api/v1/documents/extract', {
    method: 'POST',
    body: formData,
  });
}

/**
 * Supporting Feature: Case Judgment Analyzer
 */
export async function analyzeCase({ text, includeSpans = true }) {
  const payload = {
    text,
    include_spans: Boolean(includeSpans),
  };

  return request('/api/v1/legal-language/analyze-case', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

/**
 * System Status / Health
 */
export async function getSystemStatus() {
  return request('/api/v1/status', {
    method: 'GET',
  });
}

export function getBaseUrl() {
  return API_BASE_URL;
}
