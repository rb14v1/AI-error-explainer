import React from 'react';

/**
 * ErrorResult component - displays the error analysis result
 */
export default function ErrorResult({ result, onNewAnalysis }) {
  if (!result) {
    return null;
  }

  const getSeverityClass = (severity) => {
    const map = {
      'Critical': 'severity-critical',
      'High': 'severity-high',
      'Medium': 'severity-medium',
      'Low': 'severity-low',
    };
    return map[severity] || 'severity-medium';
  };

  const getConfidencePercentage = (confidence) => {
    return Math.round(confidence * 100);
  };

  return (
    <div className="error-result">
      <div className="result-header">
        <h2>Error Analysis</h2>
        <button onClick={onNewAnalysis} className="btn btn-link">
          Analyze Another Error
        </button>
      </div>

      <div className="result-grid">
        <div className="result-card">
          <h3 className="result-label">Error Type</h3>
          <p className="result-value error-type">{result.error_type}</p>
        </div>

        <div className="result-card">
          <h3 className="result-label">Severity</h3>
          <div className={`severity-badge ${getSeverityClass(result.severity)}`}>
            {result.severity}
          </div>
        </div>

        <div className="result-card">
          <h3 className="result-label">Confidence</h3>
          <div className="confidence-display">
            <div className="confidence-bar">
              <div
                className="confidence-fill"
                style={{ width: `${getConfidencePercentage(result.confidence)}%` }}
              />
            </div>
            <p className="confidence-text">
              {getConfidencePercentage(result.confidence)}%
            </p>
          </div>
        </div>
      </div>

      <div className="result-section">
        <h3 className="section-title">What Happened</h3>
        <p className="section-content">
          {result.what_happened}
        </p>
      </div>

      <div className="result-section">
        <h3 className="section-title">Why It Happened</h3>
        <p className="section-content">
          {result.why_it_happened}
        </p>
      </div>

      <div className="result-section">
        <h3 className="section-title">How to Fix It</h3>
        {result.how_to_fix_it && Array.isArray(result.how_to_fix_it) && (
          <ol className="fix-list">
            {result.how_to_fix_it.map((fix, index) => (
              <li key={index} className="fix-item">
                {fix}
              </li>
            ))}
          </ol>
        )}
      </div>

      {result.corrected_code && (
        <div className="result-section">
          <h3 className="section-title">Corrected Code Example</h3>
          <div className="code-block">
            <pre>
              <code>{result.corrected_code}</code>
            </pre>
            <button
              className="btn-copy"
              onClick={() => {
                navigator.clipboard.writeText(result.corrected_code);
                alert('Code copied to clipboard!');
              }}
              title="Copy to clipboard"
            >
              📋 Copy
            </button>
          </div>
        </div>
      )}

      {result.prevention_tips && Array.isArray(result.prevention_tips) && (
        <div className="result-section">
          <h3 className="section-title">Prevention Tips</h3>
          <ul className="tips-list">
            {result.prevention_tips.map((tip, index) => (
              <li key={index} className="tip-item">
                {tip}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
