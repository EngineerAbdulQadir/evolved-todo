"use client";

import React, { Component, ReactNode } from "react";
import { AlertTriangle, RefreshCw, Home } from "lucide-react";

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: React.ErrorInfo | null;
}

/**
 * Error Boundary Component
 *
 * Task: T226 [P] - Add error boundaries to all pages
 *
 * Catches JavaScript errors anywhere in the child component tree,
 * logs those errors, and displays a fallback UI.
 */
export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  static getDerivedStateFromError(error: Error): State {
    // Update state so the next render will show the fallback UI
    return {
      hasError: true,
      error,
      errorInfo: null,
    };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    // Log error details to console
    console.error("Error Boundary caught an error:", error, errorInfo);

    // Update state with error info
    this.setState({
      error,
      errorInfo,
    });

    // TODO: Send error to logging service (e.g., Sentry, LogRocket)
    // logErrorToService(error, errorInfo);
  }

  handleReset = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    });
  };

  handleGoHome = () => {
    window.location.href = "/dashboard";
  };

  render() {
    if (this.state.hasError) {
      // Custom fallback UI
      if (this.props.fallback) {
        return this.props.fallback;
      }

      // Default fallback UI
      return (
        <div className="min-h-screen bg-black flex items-center justify-center p-6">
          <div className="max-w-2xl w-full">
            {/* Error Card */}
            <div className="border border-red-500/50 bg-red-950/10 p-8 rounded">
              {/* Icon and Title */}
              <div className="flex items-start gap-4 mb-6">
                <div className="p-3 bg-red-500/20 rounded-full">
                  <AlertTriangle className="w-8 h-8 text-red-400" />
                </div>
                <div className="flex-1">
                  <h1 className="text-2xl font-bold text-red-400 mb-2">
                    Something went wrong
                  </h1>
                  <p className="text-neutral-400 text-sm">
                    We encountered an unexpected error. Our team has been notified.
                  </p>
                </div>
              </div>

              {/* Error Details (Development) */}
              {process.env.NODE_ENV === "development" && this.state.error && (
                <div className="mb-6 p-4 bg-black/50 rounded border border-red-500/30">
                  <h3 className="text-xs font-bold uppercase tracking-widest text-red-400 mb-2">
                    Error Details (Development Only)
                  </h3>
                  <pre className="text-xs text-red-300 font-mono overflow-x-auto">
                    {this.state.error.toString()}
                  </pre>
                  {this.state.errorInfo && (
                    <details className="mt-4">
                      <summary className="text-xs text-neutral-500 cursor-pointer hover:text-neutral-300">
                        Stack Trace
                      </summary>
                      <pre className="text-xs text-neutral-500 font-mono overflow-x-auto mt-2">
                        {this.state.errorInfo.componentStack}
                      </pre>
                    </details>
                  )}
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex gap-4">
                <button
                  onClick={this.handleReset}
                  className="flex items-center gap-2 px-6 py-3 bg-red-500 text-white hover:bg-red-600 transition-colors font-medium rounded"
                >
                  <RefreshCw className="w-4 h-4" />
                  Try Again
                </button>
                <button
                  onClick={this.handleGoHome}
                  className="flex items-center gap-2 px-6 py-3 bg-neutral-800 text-white hover:bg-neutral-700 transition-colors font-medium rounded border border-white/10"
                >
                  <Home className="w-4 h-4" />
                  Go to Dashboard
                </button>
              </div>
            </div>

            {/* Additional Help */}
            <div className="mt-6 text-center">
              <p className="text-neutral-600 text-sm">
                If this problem persists, please{" "}
                <a
                  href="mailto:support@example.com"
                  className="text-neutral-400 hover:text-white underline"
                >
                  contact support
                </a>
                .
              </p>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

/**
 * Functional wrapper for easier usage
 */
export function withErrorBoundary<P extends object>(
  Component: React.ComponentType<P>,
  fallback?: ReactNode
) {
  return function WithErrorBoundaryWrapper(props: P) {
    return (
      <ErrorBoundary fallback={fallback}>
        <Component {...props} />
      </ErrorBoundary>
    );
  };
}
