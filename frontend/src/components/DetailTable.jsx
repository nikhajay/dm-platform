import React from "react";

export default function DetailTable({ result }) {
  const rows = [
    ["Suitability score (0-100)", (m) => result.opi[m].suitability_pct],
    ["Cost efficiency (%)", (m) => result.opi[m].cost_efficiency_pct],
    ["Schedule efficiency (%)", (m) => result.opi[m].schedule_efficiency_pct],
    ["Overall Performance Index", (m) => result.opi[m].opi],
    ["Effort (PM)", (m) => result.effort_pm[m]],
    ["Projected cost (₹ Cr)", (m) => result.cost_cr[m]],
    ["Projected duration (months)", (m) => result.duration_months[m]],
  ];

  return (
    <div className="card">
      <div className="card-eyebrow">05 — Detailed report</div>
      <h3>Full comparison table</h3>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Metric</th>
              <th>Waterfall</th>
              <th>Agile</th>
              <th>Hybrid</th>
            </tr>
          </thead>
          <tbody>
            {rows.map(([label, getter]) => (
              <tr key={label}>
                <td>{label}</td>
                <td>{getter("waterfall")}</td>
                <td>{getter("agile")}</td>
                <td>{getter("hybrid")}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
