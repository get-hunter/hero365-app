'use client';

/**
 * Simple Error Boundary
 * 
 * Minimal error boundary without external dependencies
 */

import React, { Component, ErrorInfo, ReactNode } from 'react';

interface SimpleErrorBoundaryProps {
  children: ReactNode;
  businessName?: string;
  showErrorDetails?: boolean;
}

interface SimpleErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

export class SimpleErrorBoundary extends Component<
  SimpleErrorBoundaryProps,
  SimpleErrorBoundaryState
> {
  constructor(props: SimpleErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null
    };
  }

  static getDerivedStateFromError(error: Error): Partial<SimpleErrorBoundaryState> {
    return {
      hasError: true,
      error
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('🚨 [ERROR-BOUNDARY] Error caught:', {
      error: error.message,
      stack: error.stack,
      componentStack: errorInfo.componentStack
    });
  }

  handleRetry = () => {
    this.setState({
      hasError: false,
      error: null
    });
  };

  handleGoHome = () => {
    if (typeof window !== 'undefined') {
      window.location.href = '/';
    }
  };

  render() {
    if (this.state.hasError) {
      const { businessName = 'Professional Services', showErrorDetails = false } = this.props;
      const { error } = this.state;

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
              </p>

              <div className="flex flex-col sm:flex-row gap-3 justify-center mb-6">
                <button 
                  onClick={this.handleRetry}
                  className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Try Again
                </button>
                
                <button 
                  onClick={this.handleGoHome}
                  className="px-6 py-3 bg-gray-100 text-gray-900 rounded-lg hover:bg-gray-200 transition-colors"
                >
                  Go Home
                </button>
              </div>

              {showErrorDetails && error && (
                <details className="mt-6 text-left">
                  <summary className="cursor-pointer text-sm font-medium text-gray-700 hover:text-gray-900">
                    Technical Details
                  </summary>
                  <div className="mt-3 p-4 bg-gray-100 rounded-lg text-xs font-mono">
                    <div><strong>Error:</strong> {error.name}</div>
                    <div><strong>Message:</strong> {error.message}</div>
                    {error.stack && (
                      <div className="mt-2">
                        <strong>Stack:</strong>
                        <pre className="mt-1 text-xs overflow-auto">{error.stack}</pre>
                      </div>
                    )}
                  </div>
                </details>
              )}
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default SimpleErrorBoundary;
