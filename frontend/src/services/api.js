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

  // Specific user-friendly messages based on status
  if (status === 404) {
    return new ApiError('No definition found for this term.', 404, 'NOT_FOUND', errorData?.error?.request_id || null);
  }

  if (status === 429) {
    return new ApiError(
      errorData?.error?.message || 'Too many requests. Please wait a moment before trying again.',
      429,
      'RATE_LIMIT_EXCEEDED',
      errorData?.error?.request_id || null
    );
  }

  if (status === 415) {
    return new ApiError('Please upload a valid PDF document (.pdf).', 415, 'UNSUPPORTED_MEDIA', errorData?.error?.request_id || null);
  }

  if (status === 413) {
    return new ApiError('The uploaded file is too large. Maximum supported size is 10 MB.', 413, 'FILE_TOO_LARGE', errorData?.error?.request_id || null);
  }

  if (status === 400 && errorData?.error?.message?.toLowerCase().includes('pdf')) {
    return new ApiError('The selected PDF file is corrupted or unreadable. Please try a different document.', 400, 'CORRUPTED_PDF', errorData?.error?.request_id || null);
  }

  // Handle standard LexiLaw error envelope
  if (errorData?.error?.message) {
    // If the message is clear, use it; otherwise fall back to generic
    const rawMsg = errorData.error.message;
    return new ApiError(
      rawMsg,
      status,
      errorData.error.code || 'BACKEND_ERROR',
      errorData.error.request_id || null,
      errorData.error
    );
  }

  // Handle validation error details
  if (errorData?.detail) {
    return new ApiError(
      "The input details could not be processed. Please check your text and try again.",
      status,
      'VALIDATION_ERROR',
      null,
      errorData.detail
    );
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
    if (err instanceof ApiError) {
      throw err;
    }
    // Network or connection error when server is unreachable
    console.error('[LexiLaw Connection Error]:', err);
    throw new ApiError(
      'LexiLaw is temporarily unable to process your request. Please try again shortly.',
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
