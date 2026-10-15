"""
main.py — FastAPI backend for the SDLC Model Advisor
(Waterfall vs Agile vs Hybrid suitability + performance analysis,
 mid-project change-impact analysis, and PDF report export)

Run:
    pip install -r requirements.txt
    uvicorn main:app --reload --port 8000
"""

import os
import sys
from datetime import datetime
from typing import List, Literal, Optional

# Make sure this file's own directory is on sys.path, so the sibling modules
# (calculations.py, change_analysis.py, report_pdf.py) are importable no
# matter what working directory the server process was started from
# (Passenger, gunicorn, a systemd unit, etc. don't always cwd into this
# folder).
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel, Field

from calculations import analyze
from change_analysis import analyze_change_request
from report_pdf import build_baseline_pdf, build_change_pdf

app = FastAPI(
    title="SDLC Model Advisor API",
    description=(
        "Recommends Waterfall / Agile / Hybrid from a project baseline, "
        "re-evaluates that choice when a mid-project change request lands, "
        "and exports either result as a PDF."
    ),
    version="1.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # dev-friendly; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------------------------------- #
# Schemas
# --------------------------------------------------------------------------- #

class BaselineInput(BaseModel):
    project_name: str = Field(..., example="Customer Portal")
    kloc: float = Field(..., gt=0, example=60)
    base_effort_pm: float = Field(..., gt=0, example=480)
    team_cost_per_pm_lakh: float = Field(..., gt=0, example=1.2)
    target_budget_cr: float = Field(..., gt=0, example=15)
    target_duration_months: float = Field(..., gt=0, example=8)
    requirement_change_pct: float = Field(..., ge=0, le=100, example=30)
    billing: Literal["fixed_price", "time_material"] = "fixed_price"
    compliance: Literal["low", "medium", "high"] = "medium"
    technical_uncertainty: Literal["low", "medium", "high"] = "medium"
    feedback: Literal["low", "medium", "high"] = "medium"
    fixed_scope: bool = True
    fixed_price: bool = True


class ChangeRequestPayload(BaseModel):
    """A change raised after the project has already started, scored
    against the original baseline that was already calculated."""

    original_inputs: BaselineInput
    chosen_model: Literal["waterfall", "agile", "hybrid"]

    change_title: str = "Untitled change"
    change_description: str = ""
    urgency: Literal["low", "medium", "high"] = "medium"

    # Where in the SDLC the change was raised — drives the cost-of-change
    # multiplier (later phase = pricier change).
    current_phase: Literal["requirements", "design", "development", "testing", "deployment"]

    # How much % of the CHOSEN model's total effort was already done when
    # this change landed.
    percent_complete: float = Field(0, ge=0, le=100)

    # Extra effort (person-months) this change is estimated to need, before
    # phase/architecture multipliers are applied.
    additional_effort_pm: float = Field(..., ge=0)

    # Which architectural layers this change touches — drives the
    # architecture-impact score.
    architecture_areas: List[
        Literal["ui", "api", "business_logic", "database", "integration", "infrastructure"]
    ] = []

    # How volatile requirements are *for this changed slice specifically* —
    # used to re-check whether the original model is still the best fit for
    # this portion of work.
    change_requirement_volatility_pct: float = Field(..., ge=0, le=100)


class HistoryItem(BaseModel):
    project_name: str
    label: str
    kind: Literal["baseline", "change"]
    opi: Optional[float] = None


# Very small in-memory history so the frontend can show "recent analyses"
# (both first-time baselines and change requests) without needing a
# database for this MVP. Replace with real persistence for production use.
_HISTORY: List[dict] = []


def _push_history(project_name: str, label: str, kind: str, opi: Optional[float]):
    _HISTORY.insert(0, {"project_name": project_name, "label": label, "kind": kind, "opi": opi})
    del _HISTORY[20:]  # keep last 20


# --------------------------------------------------------------------------- #
# Health / history
# --------------------------------------------------------------------------- #

@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/history")
def history():
    return _HISTORY


# --------------------------------------------------------------------------- #
# 1. First-time baseline analysis
# --------------------------------------------------------------------------- #

@app.post("/api/analyze")
def analyze_baseline(payload: BaselineInput):
    try:
        result = analyze(payload.dict())
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=400, detail=str(exc))

    winner = result["recommendation"]["recommended_model"]
    _push_history(payload.project_name, result["recommendation"]["recommended_label"], "baseline", result["opi"][winner]["opi"])
    return result


@app.post("/api/analyze/pdf")
def analyze_baseline_pdf(payload: BaselineInput, label: str = "First-time baseline"):
    """Download the SAME baseline result as a PDF. Call this again with a
    different `label` (e.g. 'Recalculated baseline') any time the inputs
    are revised later — the frontend tracks first-run vs modified-run."""
    try:
        result = analyze(payload.dict())
        buf = build_baseline_pdf(result, datetime.now().strftime("%d %b %Y, %H:%M"), run_label=label)
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=400, detail=str(exc))

    filename = f'{payload.project_name.strip().replace(" ", "_") or "project"}_baseline_report.pdf'
    return Response(
        content=buf.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# --------------------------------------------------------------------------- #
# 2. Mid-project change request
# --------------------------------------------------------------------------- #

@app.post("/api/change-request")
def change_request(payload: ChangeRequestPayload):
    try:
        result = analyze_change_request(payload.dict())
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=400, detail=str(exc))

    _push_history(
        payload.original_inputs.project_name,
        f"Change: {payload.change_title}",
        "change",
        result["original_result"]["opi"][payload.chosen_model]["opi"],
    )
    return result


@app.post("/api/change-request/pdf")
def change_request_pdf(payload: ChangeRequestPayload, label: str = "Change request"):
    try:
        result = analyze_change_request(payload.dict())
        buf = build_change_pdf(result, datetime.now().strftime("%d %b %Y, %H:%M"), run_label=label)
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=400, detail=str(exc))

    filename = f'{payload.original_inputs.project_name.strip().replace(" ", "_") or "project"}_change_report.pdf'
    return Response(
        content=buf.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
