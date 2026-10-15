import React, { useState } from "react";

export default function DownloadPdfButton({ onDownload, label = "Download PDF report", variant = "outline" }) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);

  const handleClick = async () => {
    setBusy(true);
    setError(null);
    try {
      await onDownload();
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="pdf-download">
      <button
        type="button"
        className={variant === "dark" ? "btn-secondary" : "btn-outline"}
        onClick={handleClick}
        disabled={busy}
      >
        {busy ? "Preparing PDF…" : `⬇ ${label}`}
      </button>
      {error && <div className="pdf-error">{error}</div>}
    </div>
  );
}
