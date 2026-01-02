/**
 * Error handling utilities for consistent error message extraction
 */

export interface ApiError {
  response?: {
    data?: {
      detail?: string | Array<{ msg: string }>;
    };
  };
  message?: string;
}

/**
 * Extracts a user-friendly error message from various API error formats
 * @param error - The error object from an API call
 * @param fallbackMessage - Default message if error details can't be extracted
 * @returns A user-friendly error message string
 */
export function getErrorMessage(
  error: ApiError,
  fallbackMessage: string = 'An error occurred. Please try again.'
): string {
  const detail = error.response?.data?.detail;

  if (typeof detail === 'string') {
    return detail;
  }

  if (Array.isArray(detail)) {
    return detail.map((e) => e.msg).join(', ');
  }

  if (error.message) {
    return error.message;
  }

  return fallbackMessage;
}
