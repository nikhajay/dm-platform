import React from "react";

const MODEL_ACCENT = {
  waterfall: "#2563EB",
  agile: "#16A34A",
  hybrid: "#7C3AED",
};

export default function RecommendationCard({ result }) {
  const { recommendation, opi } = result;
  const winner = recommendation.recommended_model;

  return (
    <div className="verdict" style={{ "--accent": MODEL_ACCENT[winner] }}>
      <div className="verdict-left">
        <div className="card-eyebrow light">Recommendation</div>
        <h2>{recommendation.recommended_label}</h2>
        <p className="muted">
          Confidence: <strong>{recommendation.confidence}</strong> · Overall
          Performance Index {opi[winner].opi}/100
        </p>
        <ul className="reasons">
          {recommendation.reasons.map((r, i) => (
            <li key={i}>{r}</li>
          ))}
        </ul>
      </div>
      <div className="verdict-right">
        {recommendation.ranking.map((r, i) => (
          <div className={`rank-row ${r.model === winner ? "rank-winner" : ""}`} key={r.model}>
            <span className="rank-pos">{i + 1}</span>
            <span className="rank-label">{r.label}</span>
            <span className="rank-opi">{r.opi}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
