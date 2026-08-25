/**
 * API service for communicating with the Django backend.
 *
 * This module handles all HTTP requests to the Error Explainer API.
 * It abstracts the API communication from React components.
 */

const API_BASE_URL = '/api';

/**
 * Health check - verify the API is running
 */
export async function checkHealth() {
  try {
    const response = await fetch(`${API_BASE_URL}/health/`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Health check failed: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Health check error:', error);
    throw error;
  }
}

/**
 * Explain an error using the Error Explainer Agent
 *
 * @param {Object} errorInput - The error information to analyze
 * @param {string} errorInput.error_message - The error message (required)
 * @param {string} [errorInput.stack_trace] - Stack trace (optional)
 * @param {string} [errorInput.code_snippet] - Code snippet (optional)
 * @param {string} [errorInput.language] - Programming language (optional)
 * @returns {Promise<Object>} - The analysis result with error explanation
 * @throws {Error} - If the request fails
 */
export async function explainError(errorInput) {
  // Validate required field
  if (!errorInput.error_message || !errorInput.error_message.trim()) {
    throw new Error('Error message is required');
  }

  try {
    const response = await fetch(`${API_BASE_URL}/explain/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        error_message: errorInput.error_message.trim(),
        stack_trace: errorInput.stack_trace?.trim() || undefined,
        code_snippet: errorInput.code_snippet?.trim() || undefined,
        language: errorInput.language?.trim() || undefined,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      const errorMessage = errorData.error || `API request failed: ${response.statusText}`;
      throw new Error(errorMessage);
    }

    const data = await response.json();

    // Validate response has required fields
    if (data.status !== 'success') {
      throw new Error('API returned non-success status');
    }

    return data;
  } catch (error) {
    console.error('Error explanation request failed:', error);
    throw error;
  }
}
