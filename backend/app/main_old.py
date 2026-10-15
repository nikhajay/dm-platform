"""
main.py — FastAPI backend for the SDLC Model Advisor
(Waterfall vs Agile vs Hybrid suitability + performance analysis)

Run:
    pip install -r requirements.txt
    uvicorn main:app --reload --port 8000
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Literal, List
from app.calculations import analyze

app = FastAPI(
    title="SDLC Model Advisor API",
    description="Recommends Waterfall / Agile / Hybrid based on project baseline factors.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # dev-friendly; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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


class HistoryItem(BaseModel):
    project_name: str
    recommended_model: str
    opi: float


# Very small in-memory history so the frontend can show "recent analyses"
# without needing a database for this MVP.
_HISTORY: List[dict] = []


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/analyze")
def analyze_baseline(payload: BaselineInput):
    try:
        result = analyze(payload.dict())
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=400, detail=str(exc))

    _HISTORY.insert(
        0,
        {
            "project_name": payload.project_name,
            "recommended_model": result["recommendation"]["recommended_label"],
            "opi": result["opi"][result["recommendation"]["recommended_model"]]["opi"],
        },
    )
    del _HISTORY[20:]  # keep last 20

    return result


@app.get("/api/history")
def history():
    return _HISTORY
