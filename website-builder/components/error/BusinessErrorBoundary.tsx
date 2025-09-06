'use client';

/**
 * Business Error Boundary
 * 
 * Comprehensive error handling for business data loading and display
 * Provides fallback UI and error reporting
 */

import React, { Component, ErrorInfo, ReactNode } from 'react';

// Error types
export interface BusinessError {
  name: string;
  message: string;
  code?: string;
  statusCode?: number;
  endpoint?: string;
  timestamp: number;
  userAgent?: string;
  url?: string;
}

interface BusinessErrorBoundaryProps {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: BusinessError, errorInfo: ErrorInfo) => void;
  businessName?: string;
  businessPhone?: string;
  showErrorDetails?: boolean;
}

interface BusinessErrorBoundaryState {
  hasError: boolean;
  error: BusinessError | null;
  errorInfo: ErrorInfo | null;
  errorId: string | null;
}

/**
 * Business-specific error boundary with comprehensive error handling
 */
export class BusinessErrorBoundary extends Component<
  BusinessErrorBoundaryProps,
  BusinessErrorBoundaryState
> {
  constructor(props: BusinessErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      errorId: null
    };
  }

  static getDerivedStateFromError(error: Error): Partial<BusinessErrorBoundaryState> {
    const businessError: BusinessError = {
      name: error.name,
      message: error.message,
      code: (error as any).code,
      statusCode: (error as any).statusCode,
      endpoint: (error as any).endpoint,
      timestamp: Date.now(),
      userAgent: typeof window !== 'undefined' ? window.navigator.userAgent : undefined,
      url: typeof window !== 'undefined' ? window.location.href : undefined
    };

    return {
      hasError: true,
      error: businessError,
      errorId: generateErrorId()
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    const businessError = this.state.error!;
    
    // Call onError callback if provided
    if (this.props.onError) {
      this.props.onError(businessError, errorInfo);
    }

    // Log error details
    console.error('🚨 [BUSINESS-ERROR-BOUNDARY] Error caught:', {
      error: businessError,
      errorInfo,
      errorId: this.state.errorId
    });

    // Report to external service in production
    this.reportError(businessError, errorInfo);

    this.setState({ errorInfo });
  }

  private async reportError(error: BusinessError, errorInfo: ErrorInfo) {
    // Only report in production
    if (process.env.NODE_ENV !== 'production') return;

    try {
      // Report to your error tracking service
      // Example: Sentry, LogRocket, etc.
      const errorReport = {
        errorId: this.state.errorId,
        error,
        errorInfo: {
          componentStack: errorInfo.componentStack
        },
        context: {
          businessName: this.props.businessName,
          timestamp: Date.now(),
          userAgent: error.userAgent,
          url: error.url
        }
      };

      // Send to error reporting endpoint
      await fetch('/api/errors/report', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(errorReport)
      }).catch(() => {
        // Fail silently if error reporting fails
      });
    } catch {
      // Fail silently
    }
  }

  private handleRetry = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
      errorId: null
    });
  };

  private handleGoHome = () => {
    if (typeof window !== 'undefined') {
      window.location.href = '/';
    }
  };

  private handleContactSupport = () => {
    if (this.props.businessPhone && typeof window !== 'undefined') {
      window.location.href = `tel:${this.props.businessPhone}`;
    }
  };

  render() {
    if (this.state.hasError) {
      // Use custom fallback if provided
      if (this.props.fallback) {
        return this.props.fallback;
      }

      const { error, errorId } = this.state;
      const { businessName = 'Professional Services', businessPhone, showErrorDetails = false } = this.props;

      return (
        <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
          <div className="max-w-2xl w-full bg-white rounded-lg shadow-xl">
            <div className="text-center p-8">
              <div className="mx-auto w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mb-4">
                <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              </div>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">
                Something went wrong
              </h2>
              <p className="text-gray-600 mb-8">
                We're sorry, but there was an error loading the {businessName} website. 
                Our team has been notified and is working to fix the issue.
              </p>

              {/* Error Actions */}
              <div className="flex flex-col sm:flex-row gap-3 justify-center mb-6">
                <button 
                  onClick={this.handleRetry}
                  className="flex items-center justify-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                  Try Again
                </button>
                
                <button 
                  onClick={this.handleGoHome}
                  className="flex items-center justify-center gap-2 px-6 py-3 bg-gray-100 text-gray-900 rounded-lg hover:bg-gray-200 transition-colors"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
                  </svg>
                  Go Home
                </button>

                {businessPhone && (
                  <button 
                    onClick={this.handleContactSupport}
                    className="flex items-center justify-center gap-2 px-6 py-3 bg-gray-100 text-gray-900 rounded-lg hover:bg-gray-200 transition-colors"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                    </svg>
                    Call Support
                  </button>
                )}
              </div>

              {/* Error ID for support */}
              {errorId && (
                <div className="text-center p-4 bg-gray-100 rounded-lg mb-6">
                  <p className="text-sm text-gray-600">
                    <strong>Error ID:</strong> {errorId}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    Please reference this ID when contacting support
                  </p>
                </div>
              )}

              {/* Technical Details (Development/Debug Mode) */}
              {showErrorDetails && error && (
                <details className="mt-6">
                  <summary className="cursor-pointer text-sm font-medium text-gray-700 hover:text-gray-900">
                    Technical Details
                  </summary>
                  <div className="mt-3 p-4 bg-gray-100 rounded-lg text-xs font-mono">
                    <div className="space-y-2">
                      <div><strong>Error:</strong> {error.name}</div>
                      <div><strong>Message:</strong> {error.message}</div>
                      {error.code && <div><strong>Code:</strong> {error.code}</div>}
                      {error.statusCode && <div><strong>Status:</strong> {error.statusCode}</div>}
                      {error.endpoint && <div><strong>Endpoint:</strong> {error.endpoint}</div>}
                      <div><strong>Time:</strong> {new Date(error.timestamp).toISOString()}</div>
                    </div>
                  </div>
                </details>
              )}

              {/* Help Text */}
              <div className="text-center text-sm text-gray-500">
                <p>
                  If the problem persists, please contact {businessName} directly
                  {businessPhone && (
                    <>
                      {' '}at{' '}
                      <a 
                        href={`tel:${businessPhone}`}
                        className="text-blue-600 hover:text-blue-800 font-medium"
                      >
                        {businessPhone}
                      </a>
                    </>
                  )}
                </p>
              </div>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

/**
 * Generate a unique error ID for tracking
 */
function generateErrorId(): string {
  const timestamp = Date.now().toString(36);
  const random = Math.random().toString(36).substr(2, 9);
  return `err_${timestamp}_${random}`;
}

/**
 * Hook for functional components to report errors
 */
export function useErrorReporting() {
  const reportError = React.useCallback((error: Error, context?: Record<string, any>) => {
    const businessError: BusinessError = {
      name: error.name,
      message: error.message,
      code: (error as any).code,
      statusCode: (error as any).statusCode,
      endpoint: (error as any).endpoint,
      timestamp: Date.now(),
      userAgent: typeof window !== 'undefined' ? window.navigator.userAgent : undefined,
      url: typeof window !== 'undefined' ? window.location.href : undefined
    };

    console.error('🚨 [ERROR-HOOK] Error reported:', { error: businessError, context });

    // Report to external service
    if (process.env.NODE_ENV === 'production') {
      fetch('/api/errors/report', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ error: businessError, context })
      }).catch(() => {
        // Fail silently
      });
    }
  }, []);

  return { reportError };
}

/**
 * Higher-order component for wrapping components with error boundary
 */
export function withBusinessErrorBoundary<P extends object>(
  Component: React.ComponentType<P>,
  errorBoundaryProps?: Partial<BusinessErrorBoundaryProps>
) {
  const WrappedComponent = (props: P) => (
    <BusinessErrorBoundary {...errorBoundaryProps}>
      <Component {...props} />
    </BusinessErrorBoundary>
  );

  WrappedComponent.displayName = `withBusinessErrorBoundary(${Component.displayName || Component.name})`;
  return WrappedComponent;
}

export default BusinessErrorBoundary;
