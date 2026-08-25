import React, { useState } from 'react';

/**
 * ErrorForm component - handles user input for error analysis
 */
export default function ErrorForm({ onSubmit, isLoading, error }) {
  const [errorMessage, setErrorMessage] = useState('');
  const [stackTrace, setStackTrace] = useState('');
  const [codeSnippet, setCodeSnippet] = useState('');
  const [language, setLanguage] = useState('');
  const [inputError, setInputError] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    setInputError('');

    // Validate required field
    if (!errorMessage.trim()) {
      setInputError('Please enter an error message');
      return;
    }

    // Submit to parent component
    onSubmit({
      error_message: errorMessage,
      stack_trace: stackTrace,
      code_snippet: codeSnippet,
      language: language,
    });
  };

  const handleClearForm = () => {
    setErrorMessage('');
    setStackTrace('');
    setCodeSnippet('');
    setLanguage('');
    setInputError('');
  };

  return (
    <form onSubmit={handleSubmit} className="error-form">
      <div className="form-section">
        <label htmlFor="error-message" className="form-label required">
          Error Message
        </label>
        <textarea
          id="error-message"
          value={errorMessage}
          onChange={(e) => setErrorMessage(e.target.value)}
          placeholder="Paste your error message here..."
          className="form-input textarea-large"
          rows="4"
          disabled={isLoading}
          autoFocus
        />
        <p className="form-hint">The exact error message or exception string</p>
      </div>

      <div className="form-row">
        <div className="form-section form-section-half">
          <label htmlFor="stack-trace" className="form-label">
            Stack Trace
          </label>
          <textarea
            id="stack-trace"
            value={stackTrace}
            onChange={(e) => setStackTrace(e.target.value)}
            placeholder="Optional: paste the stack trace..."
            className="form-input textarea-medium"
            rows="3"
            disabled={isLoading}
          />
          <p className="form-hint">Optional - helps identify where the error occurred</p>
        </div>

        <div className="form-section form-section-half">
          <label htmlFor="language" className="form-label">
            Language
          </label>
          <select
            id="language"
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            className="form-input"
            disabled={isLoading}
          >
            <option value="">Detect automatically</option>
            <option value="javascript">JavaScript</option>
            <option value="typescript">TypeScript</option>
            <option value="python">Python</option>
            <option value="java">Java</option>
            <option value="c#">C#</option>
            <option value="ruby">Ruby</option>
            <option value="php">PHP</option>
            <option value="go">Go</option>
          </select>
          <p className="form-hint">Optional - helps provide language-specific fixes</p>
        </div>
      </div>

      <div className="form-section">
        <label htmlFor="code-snippet" className="form-label">
          Code Snippet
        </label>
        <textarea
          id="code-snippet"
          value={codeSnippet}
          onChange={(e) => setCodeSnippet(e.target.value)}
          placeholder="Optional: paste the relevant code..."
          className="form-input textarea-medium"
          rows="3"
          disabled={isLoading}
        />
        <p className="form-hint">Optional - the code that caused the error</p>
      </div>

      {inputError && (
        <div className="error-alert">
          {inputError}
        </div>
      )}

      {error && (
        <div className="error-alert">
          {error}
        </div>
      )}

      <div className="form-actions">
        <button
          type="submit"
          disabled={isLoading}
          className="btn btn-primary"
        >
          {isLoading ? 'Analyzing...' : 'Analyze Error'}
        </button>
        <button
          type="button"
          onClick={handleClearForm}
          disabled={isLoading}
          className="btn btn-secondary"
        >
          Clear
        </button>
      </div>
    </form>
  );
}
