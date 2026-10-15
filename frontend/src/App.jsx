import React, { useEffect, useState } from "react";
import BaselineForm from "./components/BaselineForm.jsx";
import ResultsDashboard from "./components/ResultsDashboard.jsx";
import ChangeRequestForm from "./components/ChangeRequestForm.jsx";
import ChangeImpactDashboard from "./components/ChangeImpactDashboard.jsx";
import HistoryList from "./components/HistoryList.jsx";
import { analyzeBaseline, analyzeChangeRequest, fetchHistory } from "./api.js";

export default function App() {
  const [tab, setTab] = useState("initial");

  const [initialResult, setInitialResult] = useState(null);
  const [initialRunCount, setInitialRunCount] = useState(0);
  const [initialLoading, setInitialLoading] = useState(false);
  const [initialError, setInitialError] = useState(null);

  const [changeResult, setChangeResult] = useState(null);
  const [changePayload, setChangePayload] = useState(null);
  const [changeRunCount, setChangeRunCount] = useState(0);
  const [changeLoading, setChangeLoading] = useState(false);
  const [changeError, setChangeError] = useState(null);

  const [history, setHistory] = useState([]);

  useEffect(() => {
    fetchHistory().then(setHistory).catch(() => {});
  }, []);

  const handleInitialSubmit = async (payload) => {
    setInitialLoading(true);
    setInitialError(null);
    try {
      const data = await analyzeBaseline(payload);
      setInitialResult(data);
      setInitialRunCount((n) => n + 1);
      setHistory(await fetchHistory());
    } catch (e) {
      setInitialError(e.message);
    } finally {
      setInitialLoading(false);
    }
  };

  const handleChangeSubmit = async (payload) => {
    setChangeLoading(true);
    setChangeError(null);
    try {
      const data = await analyzeChangeRequest(payload);
      setChangeResult(data);
      setChangePayload(payload);
      setChangeRunCount((n) => n + 1);
      setHistory(await fetchHistory());
    } catch (e) {
      setChangeError(e.message);
    } finally {
      setChangeLoading(false);
    }
  };

  // First calculation vs a later, modified re-run — both are downloadable
  // as their own labeled PDF (see ResultsDashboard / ChangeImpactDashboard).
  const initialRunLabel = initialRunCount <= 1 ? "First-time baseline" : "Recalculated baseline";
  const changeRunLabel = changeRunCount <= 1 ? "First change request" : "Recalculated change request";

  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="brand">
          <div className="brand-mark">SDLC</div>
          <div>
            <h1>Model Advisor</h1>
            <p className="muted">
              Decide between Waterfall, Agile and a Hybrid delivery model —
              then re-check that decision the moment scope changes mid-project.
            </p>
          </div>
        </div>
      </header>

      <div className="tabs">
        <button className={`tab-button ${tab === "initial" ? "active" : ""}`} onClick={() => setTab("initial")}>
          1 · Initial analysis
        </button>
        <button className={`tab-button ${tab === "change" ? "active" : ""}`} onClick={() => setTab("change")}>
          2 · Change request &amp; re-analysis
        </button>
      </div>

      {tab === "initial" && (
        <main className="app-main">
          <section className="left-col">
            <BaselineForm onSubmit={handleInitialSubmit} loading={initialLoading} />
            <HistoryList items={history} />
          </section>

          <section className="right-col">
            {initialError && <div className="card error-card">{initialError}</div>}
            {!initialResult && !initialError && (
              <div className="card empty-card">
                <div className="card-eyebrow">Awaiting input</div>
                <h3>Fill in the baseline and calculate</h3>
                <p className="muted">
                  The advisor scores Waterfall, Agile and Hybrid across six
                  weighted criteria, projects cost &amp; schedule for each, and
                  recommends the best fit with its reasoning. Recalculate any
                  time your baseline inputs change — each run is separately
                  downloadable as a PDF.
                </p>
              </div>
            )}
            <ResultsDashboard result={initialResult} runLabel={initialRunLabel} />
          </section>
        </main>
      )}

      {tab === "change" && (
        <main className="app-main">
          <section className="left-col">
            {initialResult ? (
              <ChangeRequestForm
                initialResult={initialResult}
                onSubmit={handleChangeSubmit}
                loading={changeLoading}
              />
            ) : (
              <div className="card empty-card prompt-card">
                <div className="card-eyebrow">Change request</div>
                <h3>Run an initial analysis first</h3>
                <p className="muted">
                  A change request is priced and re-evaluated against the
                  project's original baseline. Go to "Initial analysis",
                  calculate the baseline once, then come back here.
                </p>
                <button type="button" className="btn-primary" onClick={() => setTab("initial")}>
                  Go to initial analysis
                </button>
              </div>
            )}
            <HistoryList items={history} />
          </section>

          <section className="right-col">
            {changeError && <div className="card error-card">{changeError}</div>}
            {!changeResult && !changeError && initialResult && (
              <div className="card empty-card">
                <div className="card-eyebrow">Awaiting input</div>
                <h3>Describe the change and analyze impact</h3>
                <p className="muted">
                  You'll get the cost to be added, the architecture impact,
                  whether to stay on the current model or treat this slice
                  differently, and a next-phase projection — plus a
                  downloadable PDF. Re-run it again any time the change itself
                  changes.
                </p>
              </div>
            )}
            <ChangeImpactDashboard result={changeResult} payload={changePayload} runLabel={changeRunLabel} />
          </section>
        </main>
      )}

      <footer className="app-footer">
        <span>SDLC Model Advisor — FastAPI + React</span>
      </footer>
    </div>
  );
}
