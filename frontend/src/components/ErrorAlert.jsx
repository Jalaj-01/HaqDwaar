import React from 'react';

/**
 * Clean user-facing alert component.
 * Displays simple, readable messages without exposing internal codes or request IDs.
 */
export default function ErrorAlert({ error, onDismiss }) {
  if (!error) return null;

  // Prefer clean user-facing message
  const message = error.message || "We couldn't complete your request. Please try again.";

  return (
    <div className="alert alert-danger" role="alert" style={{ position: 'relative' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>{message}</div>
        {onDismiss && (
          <button
            type="button"
            className="btn btn-secondary btn-sm"
            onClick={onDismiss}
            style={{ marginLeft: 12, padding: '2px 8px' }}
            aria-label="Dismiss message"
          >
            ✕
          </button>
        )}
      </div>
    </div>
  );
}
