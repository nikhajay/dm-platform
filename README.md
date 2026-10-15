# SDLC Model Advisor

A working web app that recommends **Waterfall**, **Agile/Scrum**, or a
**Hybrid** of the two for a given project — based on a baseline you enter
(the same fields as the "Project baseline" form you shared) — and shows the
reasoning with graphical reports (radar chart, bar charts, ACT indices,
detailed table).

Stack: **Python (FastAPI)** backend + **React (Vite)** frontend.

> This is an original decision engine. The reference material you shared was
> used only to understand *which factors* a real estimator considers
> (requirement volatility, compliance, technical uncertainty, feedback
> cadence, billing type, scope rigidity, budget, schedule). The scoring
> formulas, weights, and indices are our own — not copied or recalculated
> from any source document.

---

## 1. What it does

You fill in the baseline form:

- Project name, KLOC, Base effort (PM), Team cost/PM (₹ lakh)
- Target budget (₹ Cr), Target duration (months), Expected requirement change (%)
- Billing (Fixed Price / Time & Material)
- Compliance, Technical uncertainty, Feedback (low/medium/high)
- Fixed scope / Fixed price flags

The backend then:

1. **Scores suitability** — a weighted decision matrix (6 criteria × 3
   models), each criterion 0–10, weights sum to 1.0.
2. **Projects effort, cost and duration** for each model, starting from your
   base effort and adjusting for requirement volatility (Waterfall pays a
   super-linear rework penalty for late-discovered change; Agile absorbs
   change close to linearly; Hybrid sits in between).
3. **Computes an Overall Performance Index (OPI)** per model:
   `OPI = 0.50 × suitability + 0.25 × cost efficiency + 0.25 × schedule efficiency`
4. **Derives Agility / Cycle-time / Transformation (A·C·T) indices** per
   model from the same numbers, for a quick "how does this model behave in
   flight" view.
5. **Recommends** the model with the highest OPI, with the top-3 criteria
   driving that recommendation and a confidence label based on how close the
   next-best model is.

The frontend renders all of this as an interactive dashboard: a verdict
banner, a radar chart comparing the three models across all six criteria, bar
charts for OPI/cost/duration, ACT index cards, and a full numeric table.

## 2. Project structure

```
project/
├── backend/
│   ├── main.py            FastAPI app (POST /api/analyze, GET /api/history)
│   ├── calculations.py    The scoring/decision engine (pure Python, documented)
│   └── requirements.txt
└── frontend/
    ├── index.html
    ├── package.json
    ├── vite.config.js
    └── src/
        ├── App.jsx / App.css
        ├── api.js
        └── components/
            ├── BaselineForm.jsx
            ├── ResultsDashboard.jsx
            ├── RecommendationCard.jsx
            ├── RadarComparison.jsx
            ├── BarComparison.jsx
            ├── ActIndices.jsx
            ├── DetailTable.jsx
            └── HistoryList.jsx
```

## 3. Run it locally

### Backend

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate   # optional but recommended
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

The API is now live at `http://localhost:8000` (docs at `/docs`).

### Frontend

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. The Vite dev server proxies `/api/*` calls to
the FastAPI backend on port 8000 (see `vite.config.js`), so no extra CORS
setup is needed in dev.

### Production build

```bash
cd frontend
npm run build      # outputs static files to frontend/dist
```

Serve `frontend/dist` with any static host, and point it at your deployed
FastAPI backend (update the `BASE` constant in `src/api.js` or put a reverse
proxy in front of both).

## 4. Try it with the example from your screenshot

Project: **Customer Portal**, KLOC **60**, Base effort **480 PM**, Team cost
**₹1.2 lakh/PM**, Target budget **₹15 Cr**, Target duration **8 months**,
Requirement change **30%**, Billing **Fixed Price**, Compliance **high**,
Technical uncertainty **medium**, Feedback **medium**, Fixed scope ✅, Fixed
price ✅.

With those inputs the engine currently ranks **Hybrid** first (OPI ≈ 82.3),
**Waterfall** a close second (≈ 80.6, largely on compliance/billing/scope
fit), and **Agile** third (≈ 68.8, penalized by the fixed-price/fixed-scope
billing terms even though it would otherwise handle the 30% requirement
churn well). This is exactly the kind of trade-off the tool is meant to
surface — change any input (e.g. switch billing to Time & Material, or drop
compliance to "low") and watch the recommendation shift.

## 5. Extending it

This MVP focuses on the core decision-support flow (baseline → suitability
analysis → graphical report), which is the heart of what was requested. The
reference screens you shared also cover project/requirements CRUD, a
Scrum board, a test-case tracker, and cost/time drill-downs — those are
natural next modules and would slot in as additional FastAPI routers +
React pages, reading from the same `/api/analyze` payload shape.
