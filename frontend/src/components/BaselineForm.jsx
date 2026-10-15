import React, { useState } from "react";
import ToolTip from "./ToolTip.jsx";
import Field from "./Field.jsx";
const DEFAULTS = {
  project_name: "Customer Portal",
  kloc: 60,
  base_effort_pm: 480,
  team_cost_per_pm_lakh: 1.2,
  target_budget_cr: 15,
  target_duration_months: 8,
  requirement_change_pct: 30,
  billing: "fixed_price",
  compliance: "high",
  technical_uncertainty: "medium",
  feedback: "medium",
  fixed_scope: true,
  fixed_price: true,
};
const TOOLTIP = {
  tool_project_name: 'Enter the name of the software project for which the estimation or change request is being created. Use a clear and recognizable project name, such as "Railway Reservation System" or "E-Commerce Platform".',
  tool_kloc: "Enter the estimated size of the software in thousands of lines of code. For example, 60 KLOC means approximately 60,000 lines of source code. Use the estimated codebase size when applying models such as COCOMO.",
  tool_base_effort_pm: "Enter the estimated development effort required before considering scope changes, rework, or additional overhead. One person-month represents the amount of work performed by one person in one month.",
  tool_team_cost_per_pm_lakh: 'Enter the average cost of one person working for one month. Include the applicable employee or contractor cost used for project estimation. Enter the value in ₹ lakh per person-month.',
  tool_target_budget_cr: 'Enter the maximum or planned project budget in crore (₹ Cr). This is the budget against which the estimated development cost will be compared.',
  tool_target_duration_months: 'Enter the planned or maximum duration allowed to complete the project, expressed in months. This value represents the schedule target against which the estimated duration is compared.',
  tool_requirement_change_pct: 'Enter the estimated percentage of requirements or project scope that may change during development. Include expected new features, requirement modifications, regulatory changes, UI changes, integrations, or other scope evolution.',
  tool_billing: "Select the billing model used for the project. This identifies how the client is charged for development work and may affect how effort, changes, and additional work are financially managed.",
  tool_compliance: "Select or describe the level of regulatory, legal, security, or organizational compliance required for the project. Consider standards, regulations, audits, documentation, security controls, and approval requirements.",
  tool_technical_uncertainty: "Select the level of uncertainty associated with the technology, architecture, integrations, infrastructure, performance, or technical implementation. Higher uncertainty means there are more unknowns that may affect effort, schedule, or rework.",
  tool_feedback: "Select how frequently or significantly stakeholder, customer, or user feedback is expected to influence requirements and implementation during the project.",
  tool_flags: 'Select any special conditions or warnings that may affect project estimation, cost, schedule, risk, or implementation. Use flags to highlight exceptional project characteristics that require attention.',
  tool_fixed_scope: true,
  tool_fixed_price: true,
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

export default function BaselineForm({ onSubmit, loading }) {
  const [form, setForm] = useState(DEFAULTS);
  const [tooltip, setToolTip] = useState(TOOLTIP);

  const update = (key) => (e) => {
    const value =
      e.target.type === "checkbox" ? e.target.checked : e.target.value;
    setForm((f) => ({ ...f, [key]: value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit({
      ...form,
      kloc: Number(form.kloc),
      base_effort_pm: Number(form.base_effort_pm),
      team_cost_per_pm_lakh: Number(form.team_cost_per_pm_lakh),
      target_budget_cr: Number(form.target_budget_cr),
      target_duration_months: Number(form.target_duration_months),
      requirement_change_pct: Number(form.requirement_change_pct),
    });
  };

  return (
    <form className="card baseline-form" onSubmit={handleSubmit}>
      <div className="card-eyebrow">01 — Project baseline</div>
      <h2>Describe the project</h2>
      <p className="muted">
        These are the same inputs used for the effort baseline — fill them in
        once, and the advisor scores Waterfall, Agile and Hybrid against them.
      </p>

      <div className="grid grid-4">
        <Field label="Project name" toolText={tooltip.tool_project_name}>
          <input value={form.project_name} onChange={update("project_name")} required />
        </Field>
        <Field label="KLOC" toolText={tooltip.tool_kloc}>
          <input type="number" min="0" step="0.1" value={form.kloc} onChange={update("kloc")} required />
        </Field>
        <Field label="Base effort (PM)" toolText={tooltip.tool_base_effort_pm}>
          <input type="number" min="0" step="1" value={form.base_effort_pm} onChange={update("base_effort_pm")} required />
        </Field>
        <Field label="Team cost / PM (₹ lakh)" toolText={tooltip.tool_team_cost_per_pm_lakh}>
          <input type="number" min="0" step="0.1" value={form.team_cost_per_pm_lakh} onChange={update("team_cost_per_pm_lakh")} required />
        </Field>
      </div>

      <div className="grid grid-4">
        <Field label="Target budget (₹ Cr)" toolText={tooltip.tool_target_budget_cr}>
          <input type="number" min="0" step="0.1" value={form.target_budget_cr} onChange={update("target_budget_cr")} required />
        </Field>
        <Field label="Target duration (months)" toolText={tooltip.tool_target_duration_months}>
          <input type="number" min="0" step="0.5" value={form.target_duration_months} onChange={update("target_duration_months")} required />
        </Field>
        <Field label="Expected requirement change (%)" toolText={tooltip.tool_requirement_change_pct}>
          <input type="number" min="0" max="100" step="1" value={form.requirement_change_pct} onChange={update("requirement_change_pct")} required />
        </Field>
        <Field label="Billing" toolText={tooltip.tool_billing}>
          <select value={form.billing} onChange={update("billing")}>
            <option value="fixed_price">Fixed Price</option>
            <option value="time_material">Time &amp; Material</option>
          </select>
        </Field>
      </div>

      <div className="grid grid-4">
        <Field label="Compliance" toolText={tooltip.tool_compliance}>
          <select value={form.compliance} onChange={update("compliance")}>
            <option value="low">low</option>
            <option value="medium">medium</option>
            <option value="high">high</option>
          </select>
        </Field>
        <Field label="Technical uncertainty" toolText={tooltip.tool_technical_uncertainty}>
          <select value={form.technical_uncertainty} onChange={update("technical_uncertainty")}>
            <option value="low">low</option>
            <option value="medium">medium</option>
            <option value="high">high</option>
          </select>
        </Field>
        <Field label="Feedback" toolText={tooltip.tool_feedback}>
          <select value={form.feedback} onChange={update("feedback")}>
            <option value="low">low</option>
            <option value="medium">medium</option>
            <option value="high">high</option>
          </select>
        </Field>
        <Field label="Flags" toolText={tooltip.tool_flags}>
          <div className="checkbox-row">
            <label>
              <input type="checkbox" checked={form.fixed_scope} onChange={update("fixed_scope")} />
              Fixed scope
            </label>
            <label>
              <input type="checkbox" checked={form.fixed_price} onChange={update("fixed_price")} />
              Fixed price
            </label>
          </div>
        </Field>
      </div>

      <button className="btn-primary" type="submit" disabled={loading}>
        {loading ? "Calculating…" : "Calculate baseline"}
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
