'use client';

/**
 * Business Error Boundary
 * 
 * Comprehensive error handling for business data loading and display
 * Provides fallback UI and error reporting
 */

import React, { Component, ErrorInfo, ReactNode } from 'react';
import { AlertTriangle, RefreshCw, Home, Phone } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

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
          <Card className="max-w-2xl w-full shadow-xl">
            <CardHeader className="text-center">
              <div className="mx-auto w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mb-4">
                <AlertTriangle className="w-8 h-8 text-red-600" />
              </div>
              <CardTitle className="text-2xl font-bold text-gray-900">
                Something went wrong
              </CardTitle>
              <p className="text-gray-600 mt-2">
                We're sorry, but there was an error loading the {businessName} website. 
                Our team has been notified and is working to fix the issue.
              </p>
            </CardHeader>

            <CardContent className="space-y-6">
              {/* Error Actions */}
              <div className="flex flex-col sm:flex-row gap-3 justify-center">
                <Button 
                  onClick={this.handleRetry}
                  className="flex items-center gap-2"
                  variant="default"
                >
                  <RefreshCw className="w-4 h-4" />
                  Try Again
                </Button>
                
                <Button 
                  onClick={this.handleGoHome}
                  className="flex items-center gap-2"
                  variant="outline"
                >
                  <Home className="w-4 h-4" />
                  Go Home
                </Button>

                {businessPhone && (
                  <Button 
                    onClick={this.handleContactSupport}
                    className="flex items-center gap-2"
                    variant="outline"
                  >
                    <Phone className="w-4 h-4" />
                    Call Support
                  </Button>
                )}
              </div>

              {/* Error ID for support */}
              {errorId && (
                <div className="text-center p-4 bg-gray-100 rounded-lg">
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
            </CardContent>
          </Card>
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
