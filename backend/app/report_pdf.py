"""
report_pdf.py
=============
Renders an analysis result (baseline OR change-request) into a downloadable
PDF report, using reportlab. Pure-python, no system dependencies (unlike
wkhtmltopdf/weasyprint), so it runs anywhere pip works.

Two entry points:
    build_baseline_pdf(result, generated_at, run_label)  -> BytesIO
    build_change_pdf(result, generated_at, run_label)    -> BytesIO
"""

from __future__ import annotations
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
)

INDIGO = colors.HexColor("#4F46E5")
VIOLET = colors.HexColor("#7C3AED")
INK = colors.HexColor("#1E1B2E")
MUTED = colors.HexColor("#6B7280")
HAIRLINE = colors.HexColor("#E7E4F4")
SURFACE = colors.HexColor("#FAFAFE")

MODEL_ORDER = ["waterfall", "agile", "hybrid"]
MODEL_LABEL = {"waterfall": "Waterfall", "agile": "Agile", "hybrid": "Hybrid"}


def _styles():
    ss = getSampleStyleSheet()
    ss.add(ParagraphStyle(name="H1", fontSize=20, leading=24, textColor=INK, fontName="Helvetica-Bold"))
    ss.add(ParagraphStyle(name="H2", fontSize=13, leading=17, textColor=INDIGO, fontName="Helvetica-Bold", spaceBefore=14, spaceAfter=6))
    ss.add(ParagraphStyle(name="Meta", fontSize=9.5, leading=13, textColor=MUTED))
    ss.add(ParagraphStyle(name="Body", fontSize=10, leading=14, textColor=INK))
    ss.add(ParagraphStyle(name="ReportBullet", fontSize=10, leading=14, textColor=INK, leftIndent=12))
    return ss


def _base_table_style(header=True):
    style = [
        ("FONTSIZE", (0, 0), (-1, -1), 9.5),
        ("TEXTCOLOR", (0, 0), (-1, -1), INK),
        ("GRID", (0, 0), (-1, -1), 0.5, HAIRLINE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ]
    if header:
        style += [
            ("BACKGROUND", (0, 0), (-1, 0), INDIGO),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ]
    return TableStyle(style)


def _header(flow, styles, title, subtitle, run_label, generated_at):
    flow.append(Paragraph(title, styles["H1"]))
    flow.append(Paragraph(subtitle, styles["Meta"]))
    flow.append(Spacer(1, 4))
    flow.append(Paragraph(f"Report: {run_label} &nbsp;&middot;&nbsp; Generated: {generated_at}", styles["Meta"]))
    flow.append(Spacer(1, 8))
    flow.append(HRFlowable(width="100%", thickness=1, color=HAIRLINE))
    flow.append(Spacer(1, 10))


def _suitability_table(result):
    rows = [["Criterion", "Waterfall", "Agile", "Hybrid"]]
    for crit, label in result["criteria_labels"].items():
        rows.append([
            label,
            result["fit_breakdown"]["waterfall"][crit],
            result["fit_breakdown"]["agile"][crit],
            result["fit_breakdown"]["hybrid"][crit],
        ])
    t = Table(rows, colWidths=[7.5 * cm, 3 * cm, 3 * cm, 3 * cm])
    t.setStyle(_base_table_style())
    return t


def _metrics_table(result):
    rows = [
        ["Metric", "Waterfall", "Agile", "Hybrid"],
        ["Suitability score (/100)"] + [result["opi"][m]["suitability_pct"] for m in MODEL_ORDER],
        ["Cost efficiency (%)"] + [result["opi"][m]["cost_efficiency_pct"] for m in MODEL_ORDER],
        ["Schedule efficiency (%)"] + [result["opi"][m]["schedule_efficiency_pct"] for m in MODEL_ORDER],
        ["Overall Performance Index"] + [result["opi"][m]["opi"] for m in MODEL_ORDER],
        ["Effort (PM)"] + [result["effort_pm"][m] for m in MODEL_ORDER],
        ["Projected cost (\u20b9 Cr)"] + [result["cost_cr"][m] for m in MODEL_ORDER],
        ["Projected duration (months)"] + [result["duration_months"][m] for m in MODEL_ORDER],
    ]
    t = Table(rows, colWidths=[7.5 * cm, 3 * cm, 3 * cm, 3 * cm])
    t.setStyle(_base_table_style())
    return t


def _recommendation_block(flow, styles, result):
    rec = result["recommendation"]
    flow.append(Paragraph("Recommendation", styles["H2"]))
    flow.append(Paragraph(
        f"<b>{rec['recommended_label']}</b> &nbsp;&middot;&nbsp; Confidence: {rec['confidence']} "
        f"&nbsp;&middot;&nbsp; OPI {result['opi'][rec['recommended_model']]['opi']}/100",
        styles["Body"],
    ))
    for reason in rec["reasons"]:
        flow.append(Paragraph(f"&bull; {reason}", styles["ReportBullet"]))
    flow.append(Spacer(1, 4))
    flow.append(Paragraph("Ranking: " + ", ".join(f"{r['label']} ({r['opi']})" for r in rec["ranking"]), styles["Meta"]))


def build_baseline_pdf(result: dict, generated_at: str, run_label: str = "First-time baseline") -> BytesIO:
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, topMargin=1.8 * cm, bottomMargin=1.8 * cm,
                             leftMargin=1.8 * cm, rightMargin=1.8 * cm)
    styles = _styles()
    flow = []
    project_name = result["inputs"].get("project_name", "Project")

    _header(flow, styles, f"SDLC Model Advisor — {project_name}",
            "Waterfall vs Agile vs Hybrid suitability report", run_label, generated_at)

    _recommendation_block(flow, styles, result)

    flow.append(Paragraph("Criteria fit (0\u201310)", styles["H2"]))
    flow.append(_suitability_table(result))

    flow.append(Paragraph("Cost, schedule &amp; performance", styles["H2"]))
    flow.append(_metrics_table(result))

    flow.append(Paragraph("Baseline inputs", styles["H2"]))
    inp = result["inputs"]
    input_rows = [
        ["KLOC", inp.get("kloc"), "Base effort (PM)", inp.get("base_effort_pm")],
        ["Team cost / PM (\u20b9 lakh)", inp.get("team_cost_per_pm_lakh"), "Target budget (\u20b9 Cr)", inp.get("target_budget_cr")],
        ["Target duration (months)", inp.get("target_duration_months"), "Requirement change (%)", inp.get("requirement_change_pct")],
        ["Billing", inp.get("billing"), "Compliance", inp.get("compliance")],
        ["Technical uncertainty", inp.get("technical_uncertainty"), "Feedback", inp.get("feedback")],
        ["Fixed scope", inp.get("fixed_scope"), "Fixed price", inp.get("fixed_price")],
    ]
    t = Table(input_rows, colWidths=[5 * cm, 4 * cm, 5 * cm, 4 * cm])
    t.setStyle(_base_table_style(header=False))
    flow.append(t)

    doc.build(flow)
    buf.seek(0)
    return buf


def build_change_pdf(change_result: dict, generated_at: str, run_label: str = "Change request") -> BytesIO:
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, topMargin=1.8 * cm, bottomMargin=1.8 * cm,
                             leftMargin=1.8 * cm, rightMargin=1.8 * cm)
    styles = _styles()
    flow = []
    project_name = change_result["original_result"]["inputs"].get("project_name", "Project")

    _header(flow, styles, f"Change Impact Report — {project_name}",
            f"Change: {change_result['change_title']}", run_label, generated_at)

    flow.append(Paragraph("Change summary", styles["H2"]))
    flow.append(Paragraph(change_result.get("change_description") or "\u2014", styles["Body"]))
    flow.append(Paragraph(
        f"Phase at time of change: <b>{change_result['current_phase_label']}</b> "
        f"&nbsp;&middot;&nbsp; Urgency: <b>{change_result['urgency']}</b> "
        f"&nbsp;&middot;&nbsp; Model in use: <b>{change_result['chosen_model_label']}</b>",
        styles["Meta"],
    ))

    # -- Cost impact
    ci = change_result["cost_impact"]
    flow.append(Paragraph("Cost impact", styles["H2"]))
    cost_rows = [
        ["Item", "Amount"],
        ["Phase discovered", f"{ci['phase_label']} (\u00d7{ci['phase_multiplier']} cost multiplier)"],
        ["Base change cost", f"\u20b9{ci['base_change_cost_cr']} Cr"],
        ["Extra cost from late discovery", f"\u20b9{ci['late_discovery_cost_cr']} Cr"],
        ["Architecture rework cost", f"\u20b9{ci['architecture_rework_cost_cr']} Cr"],
        ["Total additional cost", f"\u20b9{ci['total_additional_cost_cr']} Cr"],
        ["Original project cost", f"\u20b9{ci['original_cost_cr']} Cr"],
        ["Revised total project cost", f"\u20b9{ci['revised_total_cost_cr']} Cr"],
    ]
    t = Table(cost_rows, colWidths=[9 * cm, 8 * cm])
    t.setStyle(_base_table_style())
    flow.append(t)

    # -- Architecture impact
    ai = change_result["architecture_impact"]
    flow.append(Paragraph("Architecture impact", styles["H2"]))
    flow.append(Paragraph(
        f"Severity: <b>{ai['severity_label']}</b> ({ai['severity_score']}/10)", styles["Body"]
    ))
    flow.append(Paragraph(ai["recommendation"], styles["Body"]))
    if ai["areas"]:
        area_rows = [["Layer touched", "Rework weight"]] + [[a["label"], a["weight"]] for a in ai["areas"]]
        t = Table(area_rows, colWidths=[9 * cm, 8 * cm])
        t.setStyle(_base_table_style())
        flow.append(Spacer(1, 4))
        flow.append(t)

    # -- Model re-evaluation
    guidance = change_result["model_reevaluation"]["guidance"]
    flow.append(Paragraph("Model re-evaluation for this change", styles["H2"]))
    flow.append(Paragraph(
        f"Original model: <b>{guidance['original_label']}</b> &nbsp;&rarr;&nbsp; "
        f"Best fit for changed portion: <b>{guidance['changed_portion_label']}</b>",
        styles["Body"],
    ))
    flow.append(Paragraph(guidance["guidance"], styles["Body"]))

    # -- Next phase plan
    np_ = change_result["next_phase_plan"]
    flow.append(Paragraph("Next-phase plan", styles["H2"]))
    plan_rows = [
        ["Item", "Value"],
        ["% complete at time of change", f"{np_['percent_complete']}%"],
        ["Remaining effort before change", f"{np_['remaining_effort_before_change_pm']} PM"],
        ["Updated remaining effort", f"{np_['updated_remaining_effort_pm']} PM"],
        ["Remaining duration before change", f"{np_['remaining_duration_before_change_months']} months"],
        ["Updated remaining duration", f"{np_['updated_remaining_duration_months']} months"],
        ["Updated remaining cost", f"\u20b9{np_['updated_remaining_cost_cr']} Cr"],
    ]
    t = Table(plan_rows, colWidths=[9 * cm, 8 * cm])
    t.setStyle(_base_table_style())
    flow.append(t)

    doc.build(flow)
    buf.seek(0)
    return buf
