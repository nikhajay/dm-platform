import React from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";

const COLORS = { waterfall: "#2563EB", agile: "#16A34A", hybrid: "#7C3AED" };
const LABELS = { waterfall: "Waterfall", agile: "Agile", hybrid: "Hybrid" };

function MiniBar({ title, unit, values, format }) {
  const data = Object.keys(values).map((m) => ({
    model: LABELS[m],
    key: m,
    value: values[m],
  }));

  return (
    <div className="card mini-bar">
      <h4>{title}</h4>
      <ResponsiveContainer width="100%" height={200}>
        <BarChart data={data} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#EEECF7" vertical={false} />
          <XAxis dataKey="model" tick={{ fontSize: 12, fill: "#6B7280" }} axisLine={false} tickLine={false} />
          <YAxis tick={{ fontSize: 11, fill: "#B4AFCB" }} axisLine={false} tickLine={false} />
          <Tooltip formatter={(v) => [format ? format(v) : v, unit]} />
          <Bar dataKey="value" radius={[8, 8, 0, 0]}>
            {data.map((d) => (
              <Cell key={d.key} fill={COLORS[d.key]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export default function BarComparison({ result }) {
  const opiValues = Object.fromEntries(
    Object.entries(result.opi).map(([m, v]) => [m, v.opi])
  );

  return (
    <div className="card">
      <div className="card-eyebrow">03 — Cost, schedule &amp; overall score</div>
      <h3>How the numbers stack up</h3>
      <div className="grid grid-3">
        <MiniBar title="Overall Performance Index" unit="OPI" values={opiValues} />
        <MiniBar
          title="Projected cost (₹ Cr)"
          unit="₹ Cr"
          values={result.cost_cr}
          format={(v) => `₹${v} Cr`}
        />
        <MiniBar
          title="Projected duration (months)"
          unit="months"
          values={result.duration_months}
          format={(v) => `${v} mo`}
        />
      </div>
    </div>
  );
}
