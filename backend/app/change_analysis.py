"""
change_analysis.py
===================
Analyses a *change request* that arrives after a project has already
started (baseline already calculated, some % of work already done).

Four original, independently-testable calculations, all built for this
project (not taken from any reference document):

1. compute_cost_impact()        -> what the change costs, given how late in
                                    the SDLC it lands (classic "cost of
                                    change rises the later you catch it"
                                    idea, with our own multiplier table).
2. compute_architecture_impact() -> how much of the architecture the change
                                    touches, and how risky that is.
3. reevaluate_model_for_change() -> re-runs the existing suitability engine
                                    (calculations.analyze) but scoped to the
                                    changed portion only, so we can tell the
                                    user whether to keep the original model
                                    or treat this slice differently.
4. compute_next_phase_plan()    -> updated remaining effort / cost / duration
                                    for the rest of the project once the
                                    change is folded in.

analyze_change_request() orchestrates all four into one payload.
"""

from __future__ import annotations
from typing import List
from calculations import analyze, clamp, MODEL_LABEL

# --------------------------------------------------------------------------- #
# Assumptions / lookup tables (documented, not hidden magic numbers)
# --------------------------------------------------------------------------- #

# How much costlier a change is, depending on the phase it's discovered in.
# This encodes the well-known SDLC principle that the same change gets more
# expensive the later it's caught — the multipliers themselves are our own
# illustrative approximation, tunable per organisation.
PHASE_MULTIPLIER = {
    "requirements": 1.0,
    "design": 2.2,
    "development": 4.5,
    "testing": 8.0,
    "deployment": 14.0,
}

PHASE_ORDER = ["requirements", "design", "development", "testing", "deployment"]

PHASE_LABEL = {
    "requirements": "Requirements",
    "design": "Design",
    "development": "Development",
    "testing": "Testing",
    "deployment": "Deployment",
}

# Relative rework weight of each architecture layer a change can touch.
ARCH_AREA_WEIGHTS = {
    "ui": 1.0,
    "api": 2.0,
    "business_logic": 2.5,
    "database": 3.5,
    "integration": 3.0,
    "infrastructure": 2.2,
}

ARCH_AREA_LABEL = {
    "ui": "UI / Frontend",
    "api": "API layer",
    "business_logic": "Business logic",
    "database": "Database schema",
    "integration": "3rd-party integration",
    "infrastructure": "Infrastructure / DevOps",
}

_MAX_ARCH_WEIGHT = sum(ARCH_AREA_WEIGHTS.values())


# --------------------------------------------------------------------------- #
# 1. Cost impact
# --------------------------------------------------------------------------- #

def compute_cost_impact(
    additional_effort_pm: float,
    team_cost_per_pm_lakh: float,
    phase: str,
    architecture_areas: List[str],
    chosen_model_cost_cr: float,
) -> dict:
    phase_mult = PHASE_MULTIPLIER.get(phase, 1.0)

    base_change_cost_cr = additional_effort_pm * team_cost_per_pm_lakh / 100.0
    # Extra cost purely from *when* the change was caught (rework, retesting,
    # re-integration of already-completed work).
    late_discovery_cost_cr = base_change_cost_cr * (phase_mult - 1.0)

    arch_weight = sum(ARCH_AREA_WEIGHTS.get(a, 0) for a in architecture_areas)
    # Extra cost from *what* the change touches — the more architectural
    # layers involved, the more coordination/regression cost on top.
    architecture_rework_cost_cr = base_change_cost_cr * (arch_weight / _MAX_ARCH_WEIGHT)

    total_additional_cost_cr = round(
        base_change_cost_cr + late_discovery_cost_cr + architecture_rework_cost_cr, 3
    )
    revised_total_cost_cr = round(chosen_model_cost_cr + total_additional_cost_cr, 3)

    return {
        "phase": phase,
        "phase_label": PHASE_LABEL.get(phase, phase),
        "phase_multiplier": phase_mult,
        "base_change_cost_cr": round(base_change_cost_cr, 3),
        "late_discovery_cost_cr": round(late_discovery_cost_cr, 3),
        "architecture_rework_cost_cr": round(architecture_rework_cost_cr, 3),
        "total_additional_cost_cr": total_additional_cost_cr,
        "original_cost_cr": round(chosen_model_cost_cr, 3),
        "revised_total_cost_cr": revised_total_cost_cr,
    }


# --------------------------------------------------------------------------- #
# 2. Architecture impact
# --------------------------------------------------------------------------- #

def compute_architecture_impact(architecture_areas: List[str], phase: str) -> dict:
    weight = sum(ARCH_AREA_WEIGHTS.get(a, 0) for a in architecture_areas)
    severity_score = round(clamp(weight / _MAX_ARCH_WEIGHT * 10, 0, 10), 1)

    if severity_score < 2.5:
        label, band = "Low", "Localized change — low regression risk."
    elif severity_score < 5.0:
        label, band = "Moderate", "Touches more than one layer — plan focused regression testing."
    elif severity_score < 7.5:
        label, band = "High", "Cross-cutting change — a short design review is recommended before coding."
    else:
        label, band = "Major", "Wide-reaching change — treat as a mini re-architecture; review before committing effort."

    phase_note = ""
    if phase in ("testing", "deployment") and severity_score >= 5.0:
        phase_note = (
            f" Because this lands in the {PHASE_LABEL.get(phase, phase)} phase, "
            "expect re-testing of already-completed areas, not just the new code."
        )

    return {
        "areas": [{"key": a, "label": ARCH_AREA_LABEL.get(a, a), "weight": ARCH_AREA_WEIGHTS.get(a, 0)} for a in architecture_areas],
        "severity_score": severity_score,
        "severity_label": label,
        "recommendation": band + phase_note,
    }


# --------------------------------------------------------------------------- #
# 3. Model re-evaluation for the changed portion
# --------------------------------------------------------------------------- #

def reevaluate_model_for_change(original_inputs: dict, change_requirement_volatility_pct: float) -> dict:
    """Re-runs the same suitability engine used for the original baseline,
    but scoped to the changed slice of work (its own requirement volatility),
    so we can tell whether the original model is still the best fit."""

    changed_inputs = dict(original_inputs)
    changed_inputs["requirement_change_pct"] = clamp(change_requirement_volatility_pct, 0, 100)
    return analyze(changed_inputs)


def build_model_guidance(original_model: str, change_result: dict) -> dict:
    changed_model = change_result["recommendation"]["recommended_model"]
    same_model = changed_model == original_model

    if same_model:
        guidance = (
            f"The changed portion still fits best with {MODEL_LABEL[original_model]} — "
            "keep executing the change inside the existing process."
        )
    else:
        guidance = (
            f"The core project fits {MODEL_LABEL[original_model]}, but this specific change "
            f"scores better under {MODEL_LABEL[changed_model]}. Consider ring-fencing this change "
            f"into a short {MODEL_LABEL[changed_model]} cycle rather than forcing it through the "
            f"existing {MODEL_LABEL[original_model]} process."
        )

    return {
        "original_model": original_model,
        "original_label": MODEL_LABEL[original_model],
        "changed_portion_model": changed_model,
        "changed_portion_label": MODEL_LABEL[changed_model],
        "same_model": same_model,
        "guidance": guidance,
    }


# --------------------------------------------------------------------------- #
# 4. Next-phase plan
# --------------------------------------------------------------------------- #

def compute_next_phase_plan(
    original_result: dict,
    original_inputs: dict,
    chosen_model: str,
    percent_complete: float,
    additional_effort_pm: float,
) -> dict:
    percent_complete = clamp(percent_complete, 0, 100)
    total_effort = original_result["effort_pm"][chosen_model]
    total_duration = original_result["duration_months"][chosen_model]
    team_cost = float(original_inputs["team_cost_per_pm_lakh"])

    remaining_effort_before_change = round(total_effort * (1 - percent_complete / 100.0), 2)
    updated_remaining_effort = round(remaining_effort_before_change + additional_effort_pm, 2)

    remaining_duration_before_change = round(total_duration * (1 - percent_complete / 100.0), 2)
    effort_ratio = (
        updated_remaining_effort / remaining_effort_before_change
        if remaining_effort_before_change > 0
        else 1.0
    )
    updated_remaining_duration = round(remaining_duration_before_change * effort_ratio, 2)
    updated_remaining_cost_cr = round(updated_remaining_effort * team_cost / 100.0, 3)

    return {
        "percent_complete": percent_complete,
        "remaining_effort_before_change_pm": remaining_effort_before_change,
        "updated_remaining_effort_pm": updated_remaining_effort,
        "remaining_duration_before_change_months": remaining_duration_before_change,
        "updated_remaining_duration_months": updated_remaining_duration,
        "updated_remaining_cost_cr": updated_remaining_cost_cr,
    }


# --------------------------------------------------------------------------- #
# Orchestration
# --------------------------------------------------------------------------- #

def analyze_change_request(payload: dict) -> dict:
    original_inputs = payload["original_inputs"]
    chosen_model = payload["chosen_model"]

    # Recompute the original baseline so this endpoint is self-contained
    # (doesn't require trusting a client-supplied result blob).
    original_result = analyze(original_inputs)

    cost_impact = compute_cost_impact(
        additional_effort_pm=float(payload["additional_effort_pm"]),
        team_cost_per_pm_lakh=float(original_inputs["team_cost_per_pm_lakh"]),
        phase=payload["current_phase"],
        architecture_areas=payload.get("architecture_areas", []),
        chosen_model_cost_cr=original_result["cost_cr"][chosen_model],
    )

    architecture_impact = compute_architecture_impact(
        architecture_areas=payload.get("architecture_areas", []),
        phase=payload["current_phase"],
    )

    change_result = reevaluate_model_for_change(
        original_inputs, float(payload["change_requirement_volatility_pct"])
    )
    model_guidance = build_model_guidance(chosen_model, change_result)

    next_phase_plan = compute_next_phase_plan(
        original_result,
        original_inputs,
        chosen_model,
        float(payload.get("percent_complete", 0)),
        float(payload["additional_effort_pm"]),
    )

    return {
        "change_title": payload.get("change_title", "Untitled change"),
        "change_description": payload.get("change_description", ""),
        "current_phase": payload["current_phase"],
        "current_phase_label": PHASE_LABEL.get(payload["current_phase"], payload["current_phase"]),
        "urgency": payload.get("urgency", "medium"),
        "chosen_model": chosen_model,
        "chosen_model_label": MODEL_LABEL[chosen_model],
        "original_result": original_result,
        "cost_impact": cost_impact,
        "architecture_impact": architecture_impact,
        "model_reevaluation": {
            "changed_portion_result": change_result,
            "guidance": model_guidance,
        },
        "next_phase_plan": next_phase_plan,
    }
