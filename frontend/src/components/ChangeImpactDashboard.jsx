import React from "react";
import DownloadPdfButton from "./DownloadPdfButton.jsx";
import { downloadChangePdf } from "../api.js";

export default function ChangeImpactDashboard({ result, payload, runLabel }) {
  if (!result) return null;

  const { cost_impact: ci, architecture_impact: ai, model_reevaluation, next_phase_plan: np } = result;
  const guidance = model_reevaluation.guidance;
  const accent = guidance.same_model ? "#16A34A" : "#D97706";

  return (
    <div className="results-dashboard">
      <div className="verdict" style={{ "--accent": accent }}>
        <div className="verdict-left">
          <div className="card-eyebrow light">Model re-evaluation for this change</div>
          <h2>{guidance.same_model ? "Stay the course" : "Consider a different track"}</h2>
          <p className="muted">{guidance.guidance}</p>
        </div>
        <div className="verdict-right">
          <span className="run-tag light">{runLabel}</span>
          <DownloadPdfButton
            variant="dark"
            label="Download change-impact PDF"
            onDownload={() => downloadChangePdf(payload, runLabel)}
          />
        </div>
      </div>

      <div className="grid grid-3">
        <div className="card">
          <div className="card-eyebrow">Cost to be added</div>
          <h3>₹{ci.total_additional_cost_cr} Cr</h3>
          <p className="muted">
            Raised in the <strong>{ci.phase_label}</strong> phase (&times;{ci.phase_multiplier} cost
            multiplier vs. catching it at requirements time).
          </p>
          <ul className="mini-list">
            <li><span>Base change cost</span><span>₹{ci.base_change_cost_cr} Cr</span></li>
            <li><span>Late-discovery cost</span><span>₹{ci.late_discovery_cost_cr} Cr</span></li>
            <li><span>Architecture rework cost</span><span>₹{ci.architecture_rework_cost_cr} Cr</span></li>
          </ul>
          <p className="muted total-line">
            Revised total: <strong>₹{ci.revised_total_cost_cr} Cr</strong> (was ₹{ci.original_cost_cr} Cr)
          </p>
        </div>

        <div className="card">
          <div className="card-eyebrow">Architecture impact</div>
          <h3>{ai.severity_label}</h3>
          <p className="muted">Severity score {ai.severity_score}/10</p>
          <p className="muted">{ai.recommendation}</p>
          {ai.areas.length > 0 && (
            <ul className="mini-list">
              {ai.areas.map((a) => (
                <li key={a.key}><span>{a.label}</span><span>weight {a.weight}</span></li>
              ))}
            </ul>
          )}
        </div>

        <div className="card">
          <div className="card-eyebrow">Next-phase calculation</div>
          <h3>{np.updated_remaining_effort_pm} PM remaining</h3>
          <p className="muted">
            Before this change: {np.remaining_effort_before_change_pm} PM /{" "}
            {np.remaining_duration_before_change_months} months.
          </p>
          <p className="muted">
            After folding it in: <strong>{np.updated_remaining_duration_months} months</strong>,{" "}
            <strong>₹{np.updated_remaining_cost_cr} Cr</strong> to complete
            (change raised at {np.percent_complete}% complete).
          </p>
        </div>
      </div>

      <div className="card">
        <div className="card-eyebrow">Full re-scored suitability (changed slice)</div>
        <h3>How Waterfall / Agile / Hybrid score on just this change</h3>
        <p className="muted">
          This re-runs the same six-criterion engine used for the original
          baseline, but with this change's own requirement volatility — it's
          what decided the guidance above.
        </p>
        <div className="table-wrap">
          <table>
            <thead>
              <tr><th>Metric</th><th>Waterfall</th><th>Agile</th><th>Hybrid</th></tr>
            </thead>
            <tbody>
              <tr>
                <td>Overall Performance Index</td>
                <td>{model_reevaluation.changed_portion_result.opi.waterfall.opi}</td>
                <td>{model_reevaluation.changed_portion_result.opi.agile.opi}</td>
                <td>{model_reevaluation.changed_portion_result.opi.hybrid.opi}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
