import React, { Component, ReactNode } from "react";

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

/**
 * Error boundary to prevent full app crashes
 * Catches errors in child components and shows fallback UI
 */
export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error("Error boundary caught:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        this.props.fallback || (
          <div
            style={{
              padding: "2rem",
              textAlign: "center",
              background: "rgba(239, 68, 68, 0.1)",
              borderRadius: "0.5rem",
              margin: "1rem",
            }}
          >
            <h2 style={{ color: "#dc2626", marginBottom: "1rem" }}>
              Something went wrong
            </h2>
            <p style={{ color: "#666", marginBottom: "1rem" }}>
              {this.state.error?.message || "An unexpected error occurred"}
            </p>
            <button
              onClick={() => window.location.reload()}
              style={{
                padding: "0.5rem 1rem",
                background: "#3b82f6",
                color: "white",
                border: "none",
                borderRadius: "0.375rem",
                cursor: "pointer",
              }}
            >
              Reload Page
            </button>
          </div>
        )
      );
    }

    return this.props.children;
  }
}
