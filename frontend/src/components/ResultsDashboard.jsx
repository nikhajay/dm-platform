import React from "react";
import RecommendationCard from "./RecommendationCard.jsx";
import RadarComparison from "./RadarComparison.jsx";
import BarComparison from "./BarComparison.jsx";
import ActIndices from "./ActIndices.jsx";
import DetailTable from "./DetailTable.jsx";
import DownloadPdfButton from "./DownloadPdfButton.jsx";
import { downloadBaselinePdf } from "../api.js";

export default function ResultsDashboard({ result, runLabel }) {
  if (!result) return null;

  return (
    <div className="results-dashboard">
      <div className="report-toolbar">
        <span className="run-tag">{runLabel}</span>
        <DownloadPdfButton
          label="Download PDF report"
          onDownload={() => downloadBaselinePdf(result.inputs, runLabel)}
        />
      </div>
      <RecommendationCard result={result} />
      <RadarComparison result={result} />
      <BarComparison result={result} />
      <ActIndices result={result} />
      <DetailTable result={result} />
    </div>
  );
}
