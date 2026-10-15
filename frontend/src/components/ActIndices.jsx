import React from "react";

const LABELS = { waterfall: "Waterfall", agile: "Agile", hybrid: "Hybrid" };
const COLORS = { waterfall: "#2563EB", agile: "#16A34A", hybrid: "#7C3AED" };

export default function ActIndices({ result }) {
  return (
    <div className="card">
      <div className="card-eyebrow">04 — A·C·T performance indices</div>
      <h3>Agility · Cycle-time · Transformation</h3>
      <p className="muted">
        A composite view of how each model behaves once work is underway —
        computed from the same baseline, not just the up-front fit score.
      </p>
      <div className="grid grid-3">
        {Object.keys(result.act_indices).map((m) => {
          const idx = result.act_indices[m];
          return (
            <div className="act-card" key={m} style={{ "--accent": COLORS[m] }}>
              <div className="act-title">{LABELS[m]}</div>
              <ActBar label="Agility" value={idx.agility_index} />
              <ActBar label="Cycle-time" value={idx.cycle_time_index} />
              <ActBar label="Transformation" value={idx.transformation_index} />
            </div>
          );
        })}
      </div>
    </div>
  );
}

function ActBar({ label, value }) {
  const pct = Math.round(value * 100);
  return (
    <div className="act-bar-row">
      <span className="act-bar-label">{label}</span>
      <div className="act-bar-track">
        <div className="act-bar-fill" style={{ width: `${pct}%` }} />
      </div>
      <span className="act-bar-value">{pct}%</span>
    </div>
  );
}
