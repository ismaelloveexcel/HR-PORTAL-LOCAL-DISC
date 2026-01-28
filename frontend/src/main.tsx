import React from "react";
import ReactDOM from "react-dom/client";
import { RouterApp } from "./RouterApp";
import { ErrorBoundary } from "./components/ErrorBoundary";
import "./index.css";

ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <ErrorBoundary>
      <RouterApp />
    </ErrorBoundary>
  </React.StrictMode>
);
