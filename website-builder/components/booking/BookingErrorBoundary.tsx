/**
 * Booking Error Boundary
 * 
 * Catches and handles errors in the booking wizard with recovery options
 */

'use client';

import React, { Component, ErrorInfo, ReactNode } from 'react';
import { AlertTriangle, RefreshCw, Phone, Mail, ArrowLeft } from 'lucide-react';
import { Button } from '../ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';

interface Props {
  children: ReactNode;
  businessName?: string;
  businessPhone?: string;
  businessEmail?: string;
  onReset?: () => void;
  onGoBack?: () => void;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
  errorId: string;
}

export class BookingErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      errorId: ''
    };
  }

  static getDerivedStateFromError(error: Error): Partial<State> {
    // Update state so the next render will show the fallback UI
    return {
      hasError: true,
      error,
      errorId: `ERR-${Date.now().toString().slice(-6)}`
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Log the error to analytics/monitoring service
    console.error('Booking Widget Error:', error, errorInfo);
    
    this.setState({
      error,
      errorInfo
    });

    // Send error to analytics
    if (typeof window !== 'undefined') {
      // Track error event
      const errorEvent = {
        event: 'booking_widget_error',
        properties: {
          error: error.message,
          stack: error.stack,
          componentStack: errorInfo.componentStack,
          errorId: this.state.errorId,
          timestamp: new Date().toISOString(),
          userAgent: navigator.userAgent,
          url: window.location.href
        }
      };

      // Send to analytics service
      fetch('/api/v1/analytics/errors', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(errorEvent),
      }).catch(err => {
        console.warn('Failed to send error analytics:', err);
      });
    }
  }

  handleRetry = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
      errorId: ''
    });

    // Call parent reset handler if provided
    if (this.props.onReset) {
      this.props.onReset();
    }
  };

  handleGoBack = () => {
    if (this.props.onGoBack) {
      this.props.onGoBack();
    } else {
      // Fallback: reload the page
      window.location.reload();
    }
  };

  render() {
    if (this.state.hasError) {
      const { businessName = 'our team', businessPhone, businessEmail } = this.props;
      const { error, errorId } = this.state;

      return (
        <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
          <Card className="w-full max-w-2xl">
            <CardHeader className="text-center">
              <div className="mx-auto w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mb-4">
                <AlertTriangle className="w-8 h-8 text-red-600" />
              </div>
              <CardTitle className="text-2xl text-gray-900">
                Something went wrong
              </CardTitle>
              <p className="text-gray-600 mt-2">
                We encountered an unexpected error while processing your booking request.
                Don't worry - your information is safe and we're here to help.
              </p>
            </CardHeader>

            <CardContent className="space-y-6">
              {/* Error Details */}
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-700">Error Reference</span>
                  <Badge variant="secondary" className="font-mono text-xs">
                    {errorId}
                  </Badge>
                </div>
                <p className="text-sm text-gray-600">
                  Please reference this ID when contacting support.
                </p>
              </div>

              {/* Recovery Options */}
              <div className="space-y-4">
                <h3 className="font-semibold text-gray-900">What you can do:</h3>
                
                <div className="grid gap-3">
                  {/* Retry Option */}
                  <Button
                    onClick={this.handleRetry}
                    className="w-full justify-start"
                    variant="outline"
                  >
                    <RefreshCw className="w-4 h-4 mr-2" />
                    Try Again
                  </Button>

                  {/* Go Back Option */}
                  <Button
                    onClick={this.handleGoBack}
                    className="w-full justify-start"
                    variant="outline"
                  >
                    <ArrowLeft className="w-4 h-4 mr-2" />
                    Go Back to Website
                  </Button>

                  {/* Contact Options */}
                  {businessPhone && (
                    <Button
                      onClick={() => window.open(`tel:${businessPhone}`, '_self')}
                      className="w-full justify-start"
                      variant="outline"
                    >
                      <Phone className="w-4 h-4 mr-2" />
                      Call {businessName} - {businessPhone}
                    </Button>
                  )}

                  {businessEmail && (
                    <Button
                      onClick={() => window.open(`mailto:${businessEmail}?subject=Booking Error ${errorId}`, '_self')}
                      className="w-full justify-start"
                      variant="outline"
                    >
                      <Mail className="w-4 h-4 mr-2" />
                      Email {businessName}
                    </Button>
                  )}
                </div>
              </div>

              {/* Alternative Booking Methods */}
              <div className="bg-blue-50 rounded-lg p-4">
                <h4 className="font-medium text-blue-900 mb-2">
                  Need immediate assistance?
                </h4>
                <p className="text-sm text-blue-800">
                  {businessPhone ? (
                    <>Call us directly at <strong>{businessPhone}</strong> and we'll help you schedule your service right away.</>
                  ) : (
                    <>Contact {businessName} directly and we'll help you schedule your service right away.</>
                  )}
                </p>
              </div>

              {/* Technical Details (Development Only) */}
              {process.env.NODE_ENV === 'development' && error && (
                <details className="bg-red-50 rounded-lg p-4">
                  <summary className="font-medium text-red-900 cursor-pointer">
                    Technical Details (Development)
                  </summary>
                  <div className="mt-2 space-y-2">
                    <div>
                      <strong className="text-red-800">Error:</strong>
                      <pre className="text-xs text-red-700 mt-1 whitespace-pre-wrap">
                        {error.message}
                      </pre>
                    </div>
                    {error.stack && (
                      <div>
                        <strong className="text-red-800">Stack Trace:</strong>
                        <pre className="text-xs text-red-700 mt-1 whitespace-pre-wrap overflow-x-auto">
                          {error.stack}
                        </pre>
                      </div>
                    )}
                  </div>
                </details>
              )}
            </CardContent>
          </Card>
        </div>
      );
    }

    return this.props.children;
  }
}

// HOC for easier usage
export function withBookingErrorBoundary<P extends object>(
  Component: React.ComponentType<P>,
  errorBoundaryProps?: Omit<Props, 'children'>
) {
  return function WrappedComponent(props: P) {
    return (
      <BookingErrorBoundary {...errorBoundaryProps}>
        <Component {...props} />
      </BookingErrorBoundary>
    );
  };
}

export default BookingErrorBoundary;
