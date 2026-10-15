import React from "react";

export default function HistoryList({ items }) {
  if (!items || items.length === 0) {
    return (
      <div className="card history-card">
        <div className="card-eyebrow">History</div>
        <p className="muted">Your analyzed projects will show up here.</p>
      </div>
    );
  }

  return (
    <div className="card history-card">
      <div className="card-eyebrow">History</div>
      <h4>Recent analyses</h4>
      <ul className="history-list">
        {items.map((h, i) => (
          <li key={i}>
            <span className={`history-kind kind-${h.kind}`}>{h.kind === "change" ? "CR" : "BASE"}</span>
            <span className="history-name">{h.project_name}</span>
            <span className="history-model">{h.label}</span>
            <span className="history-opi">{h.opi != null ? h.opi : "—"}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
