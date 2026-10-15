"""
calculations.py
================
Decision-support engine that scores Waterfall, Agile (Scrum) and a Hybrid
(Waterfall+Agile) approach against a project baseline, and recommends the
best-fit model.

Every formula here is an original, transparent heuristic built for this
project. Nothing is copied from any reference document — the reference
material was only used to understand *which* factors (requirement
volatility, compliance, technical uncertainty, feedback cadence, billing
type, scope rigidity, budget, schedule) a real-world estimator would look
at. The math itself (weights, curves, indices) is our own.

Three independent layers feed the final recommendation:

1. Suitability scoring   -> a weighted decision matrix (0-10 per criterion)
2. Effort / Cost / Time  -> adjusts the given baseline effort per model
3. Performance indices    -> an "A-C-T" style score (Agility, Cycle-time,
                             Transformation) + an Overall Performance Index
                             (OPI) used to rank the three models.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #

def clamp(value: float, lo: float = 0.0, hi: float = 10.0) -> float:
    return max(lo, min(hi, value))


LEVEL_MAP = {"low": 3.0, "medium": 6.0, "high": 9.0}
MODELS = ("waterfall", "agile", "hybrid")


# --------------------------------------------------------------------------- #
# 1. Suitability scoring (weighted decision matrix)
# --------------------------------------------------------------------------- #

# Weights sum to 1.0 — how much each factor matters when choosing a model.
CRITERIA_WEIGHTS = {
    "requirement_stability": 0.20,
    "compliance_need": 0.15,
    "technical_uncertainty": 0.15,
    "feedback_cadence": 0.15,
    "billing_rigidity": 0.15,
    "scope_flexibility": 0.20,
}


def _level(value: str) -> float:
    return LEVEL_MAP.get((value or "medium").lower(), 6.0)


def compute_fit_scores(inputs: dict) -> dict:
    """Returns a per-criterion, per-model fit score (0-10) plus the
    weighted total suitability score (0-10) for each model."""

    change_pct = clamp(inputs["requirement_change_pct"], 0, 100)
    compliance = _level(inputs["compliance"])
    tech_unc = _level(inputs["technical_uncertainty"])
    feedback = _level(inputs["feedback"])
    billing = inputs["billing"]  # "fixed_price" | "time_material"
    fixed_scope = bool(inputs["fixed_scope"])

    stability = 100 - change_pct

    # -- Requirement stability: waterfall wants stability, agile wants
    #    volatility (it thrives on change), hybrid peaks around a balanced
    #    ~40-60% change rate (some change, not chaos).
    req = {
        "waterfall": clamp(stability / 10),
        "agile": clamp(change_pct / 10),
        "hybrid": clamp(10 - abs(stability - 50) / 5),
    }

    # -- Compliance / documentation need
    comp = {
        "waterfall": clamp(compliance),
        "agile": clamp(10 - compliance),
        "hybrid": clamp(compliance * 0.7 + 2),
    }

    # -- Technical uncertainty: high uncertainty rewards short iterative
    #    feedback loops (agile), penalises big-design-up-front (waterfall).
    tech = {
        "waterfall": clamp(10 - tech_unc),
        "agile": clamp(tech_unc),
        "hybrid": clamp(tech_unc * 0.6 + 3),
    }

    # -- Feedback cadence available from the customer/market
    fb = {
        "waterfall": clamp(10 - feedback),
        "agile": clamp(feedback),
        "hybrid": clamp(feedback * 0.5 + 4),
    }

    # -- Billing model: fixed price wants predictability (waterfall);
    #    time & material tolerates iteration (agile)
    if billing == "fixed_price":
        bill = {"waterfall": 9.0, "agile": 4.0, "hybrid": 7.0}
    else:
        bill = {"waterfall": 4.0, "agile": 9.0, "hybrid": 7.0}

    # -- Scope rigidity
    if fixed_scope:
        scope = {"waterfall": 9.0, "agile": 3.0, "hybrid": 6.5}
    else:
        scope = {"waterfall": 3.0, "agile": 9.0, "hybrid": 6.5}

    breakdown: Dict[str, Dict[str, float]] = {m: {} for m in MODELS}
    totals: Dict[str, float] = {}

    per_criterion = {
        "requirement_stability": req,
        "compliance_need": comp,
        "technical_uncertainty": tech,
        "feedback_cadence": fb,
        "billing_rigidity": bill,
        "scope_flexibility": scope,
    }

    for model in MODELS:
        total = 0.0
        for crit, weight in CRITERIA_WEIGHTS.items():
            score = per_criterion[crit][model]
            breakdown[model][crit] = round(score, 2)
            total += score * weight
        totals[model] = round(total, 3)

    return {"breakdown": breakdown, "totals": totals}


# --------------------------------------------------------------------------- #
# 2. Effort / Cost / Duration projection
# --------------------------------------------------------------------------- #

def compute_effort_cost_duration(inputs: dict) -> dict:
    base_effort = float(inputs["base_effort_pm"])
    change_pct = clamp(inputs["requirement_change_pct"], 0, 100) / 100.0
    team_cost_lakh = float(inputs["team_cost_per_pm_lakh"])
    target_duration = float(inputs["target_duration_months"])

    # Effort multipliers:
    # Waterfall — rework compounds super-linearly with late-discovered change.
    # Agile     — small ceremony overhead, change absorbed almost linearly.
    # Hybrid    — front-loaded planning + iterative build: between the two.
    effort_waterfall = base_effort * (1 + 0.80 * (change_pct ** 1.5))
    effort_agile = base_effort * (1.05 + 0.25 * change_pct)
    effort_hybrid = base_effort * (1.02 + 0.45 * (change_pct ** 1.1))

    effort = {
        "waterfall": effort_waterfall,
        "agile": effort_agile,
        "hybrid": effort_hybrid,
    }

    # Cost in ₹ crore (effort in PM * cost/PM in ₹ lakh, /100 to get crore)
    cost_cr = {m: round(((effort[m] * team_cost_lakh / 100.0) + (effort[m] * team_cost_lakh / 100.0) * 40/100) , 3) for m in MODELS}

    # Duration: sequential phases (waterfall) parallelise worse than sprints
    # (agile); hybrid is in between.
    duration_factor = {"waterfall": 1.10, "agile": 0.85, "hybrid": 0.95}
    duration_months = {
        m: round(target_duration * (effort[m] / base_effort) * duration_factor[m], 2)
        for m in MODELS
    }

    return {
        "effort_pm": {m: round(effort[m], 2) for m in MODELS},
        "cost_cr": cost_cr,
        "duration_months": duration_months,
    }


# --------------------------------------------------------------------------- #
# 3. Overall Performance Index (OPI) + ACT-style indices
# --------------------------------------------------------------------------- #

def compute_opi(fit_totals: dict, cost_cr: dict, duration_months: dict, inputs: dict) -> dict:
    target_budget = float(inputs["target_budget_cr"])
    target_duration = float(inputs["target_duration_months"])

    result = {}
    for m in MODELS:
        suitability_pct = fit_totals[m] * 10  # 0-10 -> 0-100
        cost_efficiency_pct = clamp(
            (target_budget / cost_cr[m]) * 100 if cost_cr[m] > 0 else 0, 0, 100
        )
        schedule_efficiency_pct = clamp(
            (target_duration / duration_months[m]) * 100 if duration_months[m] > 0 else 0,
            0,
            100,
        )
        opi = 0.50 * suitability_pct + 0.25 * cost_efficiency_pct + 0.25 * schedule_efficiency_pct
        result[m] = {
            "suitability_pct": round(suitability_pct, 1),
            "cost_efficiency_pct": round(cost_efficiency_pct, 1),
            "schedule_efficiency_pct": round(schedule_efficiency_pct, 1),
            "opi": round(opi, 1),
        }
    return result


def compute_act_indices(breakdown: dict, opi_data: dict) -> dict:
    """A lightweight 'Agility / Cycle-time / Transformation' index per
    model, derived purely from values we already computed above — this is
    our own composite, not the reference document's numbers."""

    act = {}
    for m in MODELS:
        b = breakdown[m]
        agility = (b["requirement_stability"] + b["technical_uncertainty"] + b["feedback_cadence"]) / 30.0
        cycle_time = opi_data[m]["schedule_efficiency_pct"] / 100.0
        transformation = (b["compliance_need"] * 0.4 + opi_data[m]["cost_efficiency_pct"] / 10 * 0.6) / 10.0
        act[m] = {
            "agility_index": round(clamp(agility, 0, 1), 3),
            "cycle_time_index": round(clamp(cycle_time, 0, 1), 3),
            "transformation_index": round(clamp(transformation, 0, 1), 3),
        }
    return act


# --------------------------------------------------------------------------- #
# Recommendation narrative
# --------------------------------------------------------------------------- #

CRITERION_LABEL = {
    "requirement_stability": "requirement stability/volatility",
    "compliance_need": "compliance & documentation needs",
    "technical_uncertainty": "technical uncertainty",
    "feedback_cadence": "customer feedback cadence",
    "billing_rigidity": "billing model",
    "scope_flexibility": "scope flexibility",
}

MODEL_LABEL = {"waterfall": "Waterfall", "agile": "Agile / Scrum", "hybrid": "Hybrid (Waterfall + Agile)"}


def build_recommendation(fit: dict, opi_data: dict) -> dict:
    ranked = sorted(MODELS, key=lambda m: opi_data[m]["opi"], reverse=True)
    winner = ranked[0]

    # Which criteria this model wins on, sorted by its own score
    winner_breakdown = fit["breakdown"][winner]
    top_criteria = sorted(winner_breakdown.items(), key=lambda kv: kv[1], reverse=True)[:3]
    reasons = [
        f"Scores strongly on {CRITERION_LABEL[crit]} ({score}/10)."
        for crit, score in top_criteria
    ]

    gap = opi_data[winner]["opi"] - opi_data[ranked[1]]["opi"]
    confidence = "High" if gap >= 8 else "Moderate" if gap >= 3 else "Low (close call)"

    return {
        "recommended_model": winner,
        "recommended_label": MODEL_LABEL[winner],
        "ranking": [{"model": m, "label": MODEL_LABEL[m], "opi": opi_data[m]["opi"]} for m in ranked],
        "confidence": confidence,
        "reasons": reasons,
    }


# --------------------------------------------------------------------------- #
# Orchestration
# --------------------------------------------------------------------------- #

def analyze(inputs: dict) -> dict:
    fit = compute_fit_scores(inputs)
    ecd = compute_effort_cost_duration(inputs)
    opi_data = compute_opi(fit["totals"], ecd["cost_cr"], ecd["duration_months"], inputs)
    act = compute_act_indices(fit["breakdown"], opi_data)
    recommendation = build_recommendation(fit, opi_data)

    return {
        "inputs": inputs,
        "fit_breakdown": fit["breakdown"],
        "fit_totals": fit["totals"],
        "effort_pm": ecd["effort_pm"],
        "cost_cr": ecd["cost_cr"],
        "duration_months": ecd["duration_months"],
        "opi": opi_data,
        "act_indices": act,
        "recommendation": recommendation,
        "model_labels": MODEL_LABEL,
        "criteria_labels": CRITERION_LABEL,
    }
