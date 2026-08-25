import React, { useState, useEffect } from 'react';
import ErrorForm from './components/ErrorForm';
import ErrorResult from './components/ErrorResult';
import LoadingSpinner from './components/LoadingSpinner';
import { explainError, checkHealth } from './services/api';
import './index.css';

/**
 * Main App component - orchestrates the error explanation workflow
 */
export default function App() {
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [apiError, setApiError] = useState('');
  const [isHealthy, setIsHealthy] = useState(false);

  // Check if backend API is available on mount
  useEffect(() => {
    const checkAPI = async () => {
      try {
        await checkHealth();
        setIsHealthy(true);
      } catch (error) {
        console.error('API not available:', error);
        setIsHealthy(false);
        setApiError('Cannot connect to backend API. Please ensure the Django server is running on http://localhost:8000');
      }
    };

    checkAPI();
  }, []);

  const handleSubmit = async (formData) => {
    setIsLoading(true);
    setApiError('');

    try {
      const response = await explainError(formData);
      setResult(response);
    } catch (error) {
      setApiError(error.message || 'Failed to analyze error. Please try again.');
      setResult(null);
    } finally {
      setIsLoading(false);
    }
  };

  const handleNewAnalysis = () => {
    setResult(null);
    setApiError('');
  };

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <h1 className="app-title">AI Error Explainer</h1>
          <p className="app-subtitle">Understand and fix programming errors instantly</p>
        </div>
        {!isHealthy && (
          <div className="api-warning">
            ⚠️ Backend API is not available
          </div>
        )}
      </header>

      <main className="app-main">
        <div className="container">
          {!result ? (
            <>
              <section className="input-section">
                <ErrorForm
                  onSubmit={handleSubmit}
                  isLoading={isLoading}
                  error={apiError}
                />
              </section>

              {isLoading && <LoadingSpinner />}
            </>
          ) : (
            <section className="result-section">
              <ErrorResult result={result} onNewAnalysis={handleNewAnalysis} />
            </section>
          )}
        </div>
      </main>

      <footer className="app-footer">
        <p>© 2024 AI Error Explainer. Built with React and Django.</p>
      </footer>
    </div>
  );
}
