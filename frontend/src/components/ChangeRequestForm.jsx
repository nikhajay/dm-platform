import React, { useState } from "react";
import ToolTip from "./ToolTip.jsx";
import Field from "./Field.jsx";

const MODEL_OPTIONS = [
  { value: "waterfall", label: "Waterfall" },
  { value: "agile", label: "Agile / Scrum" },
  { value: "hybrid", label: "Hybrid (Waterfall + Agile)" },
];

const PHASE_OPTIONS = [
  ["requirements", "Requirements"],
  ["design", "Design"],
  ["development", "Development"],
  ["testing", "Testing"],
  ["deployment", "Deployment / Live"],
];

const AREA_OPTIONS = [
  ["ui", "UI / Frontend"],
  ["api", "API layer"],
  ["business_logic", "Business logic"],
  ["database", "Database schema"],
  ["integration", "3rd-party integration"],
  ["infrastructure", "Infrastructure / DevOps"],
];

const CTOOLTIP = {
  tool_change_title:'Enter a short, clear title describing the requested change. The title should allow someone to understand the change without reading the complete description.',
  tool_aditional_effort:'Enter the additional person-month effort initially estimated to implement this change. This should represent the base development effort before applying any phase-based rework, risk, or change multipliers.',
  tool_description:'Provide a detailed explanation of the requested change, including what needs to be added, modified, removed, or integrated. Mention important business, technical, or functional details that help estimate the change accurately.',
  tool_complete_when_raised: 'Enter the approximate percentage of the affected work that has already been completed when this change request is raised. This helps determine the amount of existing work that may need modification or rework',
  tool_urgency: 'Select how urgently the requested change must be implemented. Consider business impact, regulatory deadlines, customer commitments, production impact, and release deadlines.',
  tool_change_raised_in_phase: 'Select the project development phase in which the change request was raised. The phase is important because implementing a change later in the lifecycle can require more rework, testing, documentation, and cost.',
  tool_model_currently_in_use: 'Select the software development or estimation model currently being used for the project. This helps determine how requirement changes, rework, effort, cost, and schedule should be evaluated.',
  tool_requirement_volatility: 'Enter the estimated percentage of the affected requirements that are changing because of this change request. A higher percentage indicates greater requirement instability and may increase development, testing, documentation, and rework effort.',
  tool_ui_frontend: 'Select this option if the change modifies or adds anything in the user interface or frontend application, such as screens, forms, components, navigation, validation, styling, state management, or frontend business interactions.',
	tool_api_layer: 'Select this option if the change affects backend APIs, endpoints, request or response structures, API validation, authentication, authorization, API contracts, or API integrations.',
	tool_business_logic: 'Select this option if the change modifies application business rules, calculations, workflows, validations, decisions, processing logic, or domain behavior.',
	tool_database_schema: 'Select this option if the change requires modifications to the database structure, such as creating or modifying tables, columns, indexes, relationships, constraints, stored procedures, or database migrations.',
	tool_third_party_integration: 'Select this option if the change requires integration with an external system, service, API, payment gateway, authentication provider, notification service, or other third-party platform.',
	tool_infrastructure_devops: 'Select this option if the change affects deployment, cloud infrastructure, servers, containers, CI/CD pipelines, networking, monitoring, environment configuration, scaling, security infrastructure, or DevOps processes.'
}

export default function ChangeRequestForm({ initialResult, onSubmit, loading }) {
  const baseline = initialResult.inputs;

  const [form, setForm] = useState({
    chosen_model: initialResult.recommendation.recommended_model,
    change_title: "",
    change_description: "",
    urgency: "medium",
    current_phase: "development",
    percent_complete: 40,
    additional_effort_pm: 20,
    architecture_areas: [],
    change_requirement_volatility_pct: 50,
  });
  const [ctooltip, setCtoolTip] = useState(CTOOLTIP);

  const update = (key) => (e) => {
    setForm((f) => ({ ...f, [key]: e.target.value }));
  };

  const toggleArea = (area) => (e) => {
    setForm((f) => {
      const set = new Set(f.architecture_areas);
      if (e.target.checked) set.add(area);
      else set.delete(area);
      return { ...f, architecture_areas: Array.from(set) };
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit({
      original_inputs: baseline,
      chosen_model: form.chosen_model,
      change_title: form.change_title || "Untitled change",
      change_description: form.change_description,
      urgency: form.urgency,
      current_phase: form.current_phase,
      percent_complete: Number(form.percent_complete),
      additional_effort_pm: Number(form.additional_effort_pm),
      architecture_areas: form.architecture_areas,
      change_requirement_volatility_pct: Number(form.change_requirement_volatility_pct),
    });
  };

  return (
    <form className="card baseline-form" onSubmit={handleSubmit}>
      <div className="card-eyebrow">Change request</div>
      <h2>What changed on &ldquo;{baseline.project_name}&rdquo;?</h2>
      <p className="muted">
        Currently running on{" "}
        <strong>{MODEL_OPTIONS.find((m) => m.value === form.chosen_model)?.label}</strong>.
        Describe the change — the advisor will price it, flag the architecture
        impact, re-check the model choice for this slice, and project the
        remaining work.
      </p>

      <div className="grid grid-4">
        <Field label="Model currently in use" toolText={ctooltip.tool_model_currently_in_use}>
          <select value={form.chosen_model} onChange={update("chosen_model")}>
            {MODEL_OPTIONS.map((m) => (
              <option key={m.value} value={m.value}>{m.label}</option>
            ))}
          </select>
        </Field>
        <Field label="Change raised in phase" toolText={ctooltip.tool_change_raised_in_phase}>
          <select value={form.current_phase} onChange={update("current_phase")}>
            {PHASE_OPTIONS.map(([v, l]) => (
              <option key={v} value={v}>{l}</option>
            ))}
          </select>
        </Field>
        <Field label="Urgency" toolText={ctooltip.tool_urgency}>
          <select value={form.urgency} onChange={update("urgency")}>
            <option value="low">low</option>
            <option value="medium">medium</option>
            <option value="high">high</option>
          </select>
        </Field>
        <Field label="% complete when raised" toolText={ctooltip.tool_complete_when_raised}>
          <input type="number" min="0" max="100" value={form.percent_complete} onChange={update("percent_complete")} />
        </Field>
      </div>

      <div className="grid grid-4">
        <Field label="Change title" toolText={ctooltip.tool_change_title}>
          <input value={form.change_title} onChange={update("change_title")} placeholder="e.g. Add UPI payment option" required />
        </Field>
        <Field label="Additional effort (PM, base estimate)" toolText={ctooltip.tool_aditional_effort}>
          <input type="number" min="0" step="0.5" value={form.additional_effort_pm} onChange={update("additional_effort_pm")} required />
        </Field>
        <Field label="Requirement volatility of this change (%)" toolText={ctooltip.tool_requirement_volatility}>
          <input type="number" min="0" max="100" value={form.change_requirement_volatility_pct} onChange={update("change_requirement_volatility_pct")} />
        </Field>
      </div>

      <Field label="Description (optional)" toolText={ctooltip.tool_model_currently_in_use}>
        <textarea
          rows={2}
          value={form.change_description}
          onChange={update("change_description")}
          placeholder="What is the customer/stakeholder asking for, and why now?"
        />
      </Field>

      <div className="field" style={{ marginTop: 14, marginBottom: 14 }}>
        <span className="field-label">Architecture layers this touches</span>
        <div className="area-grid">
          {AREA_OPTIONS.map(([v, l]) => (
            <label key={v} className="area-checkbox">
              <input
                type="checkbox"
                checked={form.architecture_areas.includes(v)}
                onChange={toggleArea(v)}
              />
              {l}
            </label>
          ))}
        </div>
      </div>

      <button className="btn-primary" type="submit" disabled={loading}>
        {loading ? "Analyzing change…" : "Analyze change impact"}
      </button>
    </form>
  );
}

// function Field({ label, children }) {
//   return (
//     <label className="field">
//       <span className="field-label">{label}</span>
//       {children}
//     </label>
//   );
// }
