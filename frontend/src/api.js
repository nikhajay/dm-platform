const BASE = "/api";

async function postJson(path, payload) {
  const res = await fetch(`${BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Request to ${path} failed`);
  }
  return res.json();
}

export function analyzeBaseline(payload) {
  return postJson("/analyze", payload);
}

export function analyzeChangeRequest(payload) {
  return postJson("/change-request", payload);
}

export async function fetchHistory() {
  const res = await fetch(`${BASE}/history`);
  if (!res.ok) return [];
  return res.json();
}

async function downloadPdf(path, payload, label, filenameFallback) {
  const url = `${BASE}${path}?label=${encodeURIComponent(label)}`;
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Could not generate the PDF");
  }
  const blob = await res.blob();
  const disposition = res.headers.get("Content-Disposition") || "";
  const match = disposition.match(/filename="([^"]+)"/);
  const filename = match ? match[1] : filenameFallback;

  const objectUrl = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = objectUrl;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  window.URL.revokeObjectURL(objectUrl);
}

/** label distinguishes "First-time baseline" from a later "Recalculated
 *  baseline" download — the PDF's own subtitle line reflects whichever you
 *  pass in, so both the first-time and modified-time reports are traceable. */
export function downloadBaselinePdf(payload, label = "First-time baseline") {
  return downloadPdf("/analyze/pdf", payload, label, "baseline_report.pdf");
}

export function downloadChangePdf(payload, label = "Change request") {
  return downloadPdf("/change-request/pdf", payload, label, "change_report.pdf");
}
