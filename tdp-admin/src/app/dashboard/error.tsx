"use client";

export default function DashboardError({ reset }: { reset: () => void }) {
  return (
    <div className="admin-loading" role="alert">
      <h1>Could not load dashboard</h1>
      <p>Please try again.</p>
      <button className="usa-button" onClick={reset}>
        Try again
      </button>
    </div>
  );
}
