import React from "react";
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Legend,
  ResponsiveContainer,
  Tooltip,
} from "recharts";

export default function RadarComparison({ result }) {
  const { fit_breakdown, criteria_labels } = result;
  const criteria = Object.keys(criteria_labels);

  const data = criteria.map((crit) => ({
    criterion: criteria_labels[crit],
    Waterfall: fit_breakdown.waterfall[crit],
    Agile: fit_breakdown.agile[crit],
    Hybrid: fit_breakdown.hybrid[crit],
  }));

  return (
    <div className="card">
      <div className="card-eyebrow">02 — Criteria fit</div>
      <h3>Why each model scores the way it does</h3>
      <ResponsiveContainer width="100%" height={360}>
        <RadarChart data={data} outerRadius="75%">
          <PolarGrid stroke="#E4E1F3" />
          <PolarAngleAxis dataKey="criterion" tick={{ fill: "#6B7280", fontSize: 12 }} />
          <PolarRadiusAxis angle={30} domain={[0, 10]} tick={{ fill: "#B4AFCB", fontSize: 10 }} />
          <Radar name="Waterfall" dataKey="Waterfall" stroke="#2563EB" fill="#2563EB" fillOpacity={0.15} />
          <Radar name="Agile" dataKey="Agile" stroke="#16A34A" fill="#16A34A" fillOpacity={0.15} />
          <Radar name="Hybrid" dataKey="Hybrid" stroke="#7C3AED" fill="#7C3AED" fillOpacity={0.25} />
          <Legend />
          <Tooltip />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
}
