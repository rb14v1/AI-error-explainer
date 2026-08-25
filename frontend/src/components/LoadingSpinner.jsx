import React from 'react';

/**
 * LoadingSpinner component - displays while API request is processing
 */
export default function LoadingSpinner() {
  return (
    <div className="loading-container">
      <div className="spinner"></div>
      <p className="loading-text">Analyzing your error...</p>
    </div>
  );
}
