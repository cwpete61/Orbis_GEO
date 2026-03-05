#!/usr/bin/env python3
"""
GEO-SEO PDF Report Generator
Generates professional, client-ready PDF reports from GEO audit data.

Usage:
    python generate_pdf_report.py <json_data_file> [output_file.pdf]

The JSON data file should contain the audit results structured as:
{
    "url": "https://example.com",
    "brand_name": "Example Co",
    "date": "2026-02-18",
    "geo_score": 62,
    "scores": { ... },
    "findings": { ... },
    ...
}

Or pipe JSON data from stdin:
    cat audit_data.json | python generate_pdf_report.py - output.pdf
"""

import sys
import json
import os
from datetime import datetime

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.units import inch, mm
    from reportlab.lib.colors import (
        HexColor, black, white, grey, lightgrey, darkgrey,
        Color
    )
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        PageBreak, HRFlowable, KeepTogether, Image as RLImage
    )
    from reportlab.graphics.shapes import Drawing, Rect, String, Circle, Line, Wedge
    from reportlab.graphics.charts.barcharts import VerticalBarChart
    from reportlab.graphics.charts.piecharts import Pie
    from reportlab.graphics import renderPDF
except ImportError:
    print("ERROR: ReportLab is required. Run: pip install reportlab")
    sys.exit(1)


# ============================================================
# ORBIS BRAND PALETTE
# ============================================================
PRIMARY = HexColor("#130f40")       # Deep Midnight Blue
SECONDARY = HexColor("#1e272e")     # Anthracite
ACCENT = HexColor("#686de0")        # Soft Indigo
HIGHLIGHT = HexColor("#f0932b")     # Vibrant Orange
SUCCESS = HexColor("#2ecc71")       # Emerald
WARNING = HexColor("#f1c40f")       # Sunflower
DANGER = HexColor("#e74c3c")        # Alizarin
INFO = HexColor("#3498db")          # Peter River
LIGHT_BG = HexColor("#f5f6fa")      # Anti-Flash White
MEDIUM_BG = HexColor("#dcdde1")     # Hint of Pensive
TEXT_PRIMARY = HexColor("#2f3640")   # Electromagnetic
TEXT_SECONDARY = HexColor("#7f8c8d") # Asbestos
WHITE = white
BLACK = black


def get_score_color(score):
    """Return color based on score value."""
    if score >= 80:
        return SUCCESS
    elif score >= 60:
        return INFO
    elif score >= 40:
        return WARNING
    else:
        return DANGER


from utils import get_distance_py, get_score_label


def create_score_gauge(score, width=120, height=120):
    """Create a visual score gauge."""
    d = Drawing(width, height)

    # Background circle
    d.add(Circle(width/2, height/2, 50, fillColor=LIGHT_BG, strokeColor=lightgrey, strokeWidth=2))

    # Score arc (simplified as colored circle)
    color = get_score_color(score)
    d.add(Circle(width/2, height/2, 45, fillColor=color, strokeColor=None))

    # Inner white circle
    d.add(Circle(width/2, height/2, 35, fillColor=WHITE, strokeColor=None))

    # Score text
    d.add(String(width/2, height/2 + 5, str(score),
                 fontSize=24, fontName='Helvetica-Bold',
                 fillColor=TEXT_PRIMARY, textAnchor='middle'))

    # Label
    d.add(String(width/2, height/2 - 12, "/100",
                 fontSize=10, fontName='Helvetica',
                 fillColor=TEXT_SECONDARY, textAnchor='middle'))

    return d


def create_bar_chart(data, labels, width=400, height=200):
    """Create a horizontal bar chart for scores."""
    d = Drawing(width, height)

    chart = VerticalBarChart()
    chart.x = 60
    chart.y = 30
    chart.height = height - 60
    chart.width = width - 80
    chart.data = [data]
    chart.categoryAxis.categoryNames = labels
    chart.categoryAxis.labels.angle = 0
    chart.categoryAxis.labels.fontSize = 8
    chart.categoryAxis.labels.fontName = 'Helvetica'
    chart.valueAxis.valueMin = 0
    chart.valueAxis.valueMax = 100
    chart.valueAxis.valueStep = 20
    chart.valueAxis.labels.fontSize = 8

    # Color each bar based on score
    for i, score in enumerate(data):
        chart.bars[0].fillColor = get_score_color(score)

    chart.bars[0].strokeColor = None
    chart.bars[0].strokeWidth = 0

    d.add(chart)
    return d


def create_platform_chart(platforms, width=450, height=180):
    """Create a chart showing platform readiness scores."""
    d = Drawing(width, height)

    bar_height = 22
    bar_max_width = 280
    start_y = height - 30
    label_x = 10

    for i, (name, score) in enumerate(platforms.items()):
        y = start_y - (i * (bar_height + 10))

        # Platform name
        d.add(String(label_x, y + 5, name,
                     fontSize=9, fontName='Helvetica',
                     fillColor=TEXT_PRIMARY, textAnchor='start'))

        # Background bar
        bar_x = 130
        d.add(Rect(bar_x, y, bar_max_width, bar_height,
                    fillColor=LIGHT_BG, strokeColor=None))

        # Score bar
        try:
            numeric_score = float(score)
        except ValueError:
            numeric_score = 0
            
        bar_width = (numeric_score / 100) * bar_max_width
        color = get_score_color(numeric_score)
        d.add(Rect(bar_x, y, bar_width, bar_height,
                    fillColor=color, strokeColor=None))

        # Score text
        d.add(String(bar_x + bar_max_width + 10, y + 6, f"{numeric_score}/100",
                     fontSize=9, fontName='Helvetica-Bold',
                     fillColor=TEXT_PRIMARY, textAnchor='start'))

    return d


def build_styles():
    """Create custom paragraph styles."""
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name='ReportTitle',
        fontName='Helvetica-Bold',
        fontSize=28,
        textColor=PRIMARY,
        spaceAfter=12,
        leading=32,
        alignment=TA_LEFT,
    ))

    styles.add(ParagraphStyle(
        name='ReportSubtitle',
        fontName='Helvetica',
        fontSize=14,
        textColor=TEXT_SECONDARY,
        spaceBefore=10,
        spaceAfter=20,
        alignment=TA_LEFT,
    ))

    styles.add(ParagraphStyle(
        name='SectionHeader',
        fontName='Helvetica-Bold',
        fontSize=18,
        textColor=PRIMARY,
        spaceBefore=20,
        spaceAfter=10,
        alignment=TA_LEFT,
    ))

    styles.add(ParagraphStyle(
        name='SubHeader',
        fontName='Helvetica-Bold',
        fontSize=13,
        textColor=ACCENT,
        spaceBefore=14,
        spaceAfter=6,
        alignment=TA_LEFT,
    ))

    styles.add(ParagraphStyle(
        name='BodyText_Custom',
        fontName='Helvetica',
        fontSize=10,
        textColor=TEXT_PRIMARY,
        spaceBefore=4,
        spaceAfter=4,
        leading=14,
        alignment=TA_JUSTIFY,
    ))

    styles.add(ParagraphStyle(
        name='SmallText',
        fontName='Helvetica',
        fontSize=8,
        textColor=TEXT_SECONDARY,
        spaceBefore=2,
        spaceAfter=2,
    ))

    styles.add(ParagraphStyle(
        name='TableBody',
        fontName='Helvetica',
        fontSize=9,
        textColor=TEXT_PRIMARY,
        leading=12,
    ))

    styles.add(ParagraphStyle(
        name='ScoreLabel',
        fontName='Helvetica-Bold',
        fontSize=36,
        textColor=PRIMARY,
        alignment=TA_CENTER,
    ))

    styles.add(ParagraphStyle(
        name='HighlightBox',
        fontName='Helvetica',
        fontSize=10,
        textColor=TEXT_PRIMARY,
        backColor=LIGHT_BG,
        borderPadding=10,
        spaceBefore=8,
        spaceAfter=8,
        leading=14,
    ))

    styles.add(ParagraphStyle(
        name='CriticalFinding',
        fontName='Helvetica-Bold',
        fontSize=10,
        textColor=DANGER,
        spaceBefore=4,
        spaceAfter=2,
    ))

    styles.add(ParagraphStyle(
        name='Recommendation',
        fontName='Helvetica',
        fontSize=10,
        textColor=TEXT_PRIMARY,
        leftIndent=15,
        spaceBefore=3,
        spaceAfter=3,
        bulletIndent=5,
        leading=14,
    ))

    styles.add(ParagraphStyle(
        name='DetailedDescription',
        fontName='Helvetica',
        fontSize=10,
        textColor=TEXT_PRIMARY,
        spaceBefore=2,
        spaceAfter=6,
        leading=14,
        leftIndent=15,
    ))

    styles.add(ParagraphStyle(
        name='FindingImpact',
        fontName='Helvetica-Oblique',
        fontSize=9,
        textColor=TEXT_SECONDARY,
        spaceBefore=0,
        spaceAfter=6,
        leading=12,
        leftIndent=15,
    ))

    styles.add(ParagraphStyle(
        name='CodeFix',
        fontName='Courier',
        fontSize=9,
        textColor=TEXT_PRIMARY,
        backColor=LIGHT_BG,
        borderPadding=8,
        spaceBefore=4,
        spaceAfter=12,
        leading=11,
        leftIndent=25,
        rightIndent=15,
    ))

    styles.add(ParagraphStyle(
        name='Footer',
        fontName='Helvetica',
        fontSize=8,
        textColor=TEXT_SECONDARY,
        alignment=TA_CENTER,
    ))

    return styles


def header_footer(canvas, doc):
    """Add header and footer to each page."""
    canvas.saveState()

    # Header line
    canvas.setStrokeColor(ACCENT)
    canvas.setLineWidth(2)
    canvas.line(50, letter[1] - 40, letter[0] - 50, letter[1] - 40)

    # Header text
    canvas.setFont('Helvetica-Bold', 8)
    canvas.setFillColor(PRIMARY)
    canvas.drawString(50, letter[1] - 35, "ORBIS LOCAL ANALYSIS")

    # Footer
    canvas.setStrokeColor(lightgrey)
    canvas.setLineWidth(0.5)
    canvas.line(50, 40, letter[0] - 50, 40)

    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(TEXT_SECONDARY)
    canvas.drawString(50, 28, f"Generated {datetime.now().strftime('%B %d, %Y')}")
    canvas.drawRightString(letter[0] - 50, 28, f"Page {doc.page}")
    canvas.drawCentredString(letter[0] / 2, 28, "Confidential")

    canvas.restoreState()


def make_table_style(header_color=PRIMARY):
    """Create a consistent table style."""
    return TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), header_color),
        ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('TEXTCOLOR', (0, 1), (-1, -1), TEXT_PRIMARY),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, lightgrey),
        ('BACKGROUND', (0, 1), (-1, -1), WHITE),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [WHITE, LIGHT_BG]),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ])


def generate_report(data, output_path="GEO-REPORT.pdf"):
    """Generate the full PDF report from audit data."""

    # Extract data with defaults
    url = data.get("url", "https://example.com")
    brand_name = data.get("brand_name", url.replace("https://", "").replace("http://", "").split("/")[0])
    date = data.get("date", datetime.now().strftime("%Y-%m-%d"))

    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        topMargin=55,
        bottomMargin=55,
        leftMargin=50,
        rightMargin=50,
        title=f"{brand_name} AI Search Visibility Report"
    )

    styles = build_styles()
    elements = []
    geo_score = data.get("geo_score", 0)

    scores = data.get("scores", {})
    ai_citability = scores.get("ai_citability", 0)
    brand_authority = scores.get("brand_authority", 0)
    content_eeat = scores.get("content_eeat", 0)
    technical = scores.get("technical", 0)
    schema_score = scores.get("schema", 0)
    platform_optimization = scores.get("platform_optimization", 0)

    platforms = data.get("platforms", {
        "Google AI Overviews": 0,
        "ChatGPT": 0,
        "Perplexity": 0,
        "Gemini": 0,
        "Bing Copilot": 0,
    })
    gbp = data.get("gbp", {})
    directories = data.get("directories", {})
    local_authority = scores.get("local_authority", 0)

    crawlers = data.get("crawlers", [])
    findings = data.get("findings", [])
    quick_wins = data.get("quick_wins", [])
    medium_term = data.get("medium_term", [])
    strategic = data.get("strategic", [])
    executive_summary = data.get("executive_summary", "")
    crawler_access = data.get("crawler_access", {})
    schema_findings = data.get("schema_findings", {})
    content_findings = data.get("content_findings", {})
    technical_findings = data.get("technical_findings", {})
    brand_findings = data.get("brand_findings", {})

    # ============================================================
    # COVER PAGE
    # ============================================================
    elements.append(Spacer(1, 100))

    # Orbis Local Analysis Report
    elements.append(Paragraph("Orbis Local Analysis Report", styles['ReportTitle']))
    elements.append(Spacer(1, 8))

    # Subtitle
    elements.append(Paragraph(
        f"Generative Engine Optimization Audit for <b>{brand_name}</b>",
        styles['ReportSubtitle']
    ))

    elements.append(HRFlowable(width="100%", thickness=2, color=ACCENT, spaceAfter=20))

    # Key details table
    details_data = [
        ["Website", url],
        ["Analysis Date", datetime.strptime(date, "%Y-%m-%d").strftime("%B %d, %Y") if "-" in date else date],
        ["GEO Score", f"{geo_score}/100 — {get_score_label(geo_score)}"],
    ]

    details_table = Table(details_data, colWidths=[120, 350])
    details_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('TEXTCOLOR', (0, 0), (0, -1), ACCENT),
        ('TEXTCOLOR', (1, 0), (1, -1), TEXT_PRIMARY),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('LINEBELOW', (0, 0), (-1, -2), 0.5, lightgrey),
    ]))
    elements.append(details_table)

    elements.append(Spacer(1, 30))

    # Score gauge
    gauge = create_score_gauge(geo_score, 200, 200)
    elements.append(gauge)

    elements.append(Spacer(1, 20))

    # Score label
    score_color = get_score_color(geo_score)
    elements.append(Paragraph(
        f'<font color="{score_color.hexval()}">{get_score_label(geo_score)}</font>',
        ParagraphStyle('ScoreLabelColored', parent=styles['SectionHeader'],
                       alignment=TA_CENTER, fontSize=20)
    ))

    elements.append(PageBreak())

    # ============================================================
    # GRID VISIBILITY
    # ============================================================
    elements.append(Paragraph("Grid Visibility", styles['SectionHeader']))
    elements.append(HRFlowable(width="100%", thickness=1, color=ACCENT, spaceAfter=12))
    elements.append(Paragraph(
        "This section illustrates exactly where your business is actually being seen in local searches, "
        "where your ranking fall-off starts to occur, and how far out from your physical location "
        "could realistically be captured by Orbis Local to attract more clients.",
        styles['BodyText_Custom']
    ))
    elements.append(Spacer(1, 12))

    gbp_grid = data.get("gbp_grid", {})
    if gbp_grid and "grid" in gbp_grid:
        grid = gbp_grid["grid"]
        center = gbp_grid.get("center", {})
        
        # Calculate Current Metrics
        scores_vals = [p["score"] for p in grid]
        avg_rank = sum(scores_vals) / len(scores_vals)
        fallout_count = len([s for s in scores_vals if s > 12])
        fallout_percent = (fallout_count / len(scores_vals)) * 100
        
        max_reach = 0
        for p in grid:
            if p["score"] <= 5:
                d = get_distance_py(center["lat"], center["lng"], p["lat"], p["lng"])
                if d > max_reach: max_reach = d
                
        # Calculate Potential Metrics
        pot_scores = [p.get("potential_score", p["score"]) for p in grid]
        pot_avg_rank = sum(pot_scores) / len(pot_scores)
        pot_fallout_count = len([s for s in pot_scores if s > 12])
        pot_fallout_percent = (pot_fallout_count / len(pot_scores)) * 100
        
        pot_max_reach = 0
        for p in grid:
            ps = p.get("potential_score", p["score"])
            if ps <= 5:
                d = get_distance_py(center["lat"], center["lng"], p["lat"], p["lng"])
                if d > pot_max_reach: pot_max_reach = d
        
        # Current Stats Table
        elements.append(Paragraph("Current Visibility Status", styles['SubHeader']))
        stats_data = [
            [
                Paragraph(f"<font color='{PRIMARY.hexval()}' size=10><b>Avg. Visibility</b></font><br/><br/><font size=18><b>Rank #{avg_rank:.1f}</b></font>", styles['BodyText_Custom']),
                Paragraph(f"<font color='{PRIMARY.hexval()}' size=10><b>Search Fallout</b></font><br/><br/><font size=18><b>{int(fallout_percent)}%</b></font>", styles['BodyText_Custom']),
                Paragraph(f"<font color='{PRIMARY.hexval()}' size=10><b>Effective Reach</b></font><br/><br/><font size=18><b>{max_reach:.1f} km</b></font>", styles['BodyText_Custom'])
            ]
        ]
        st = Table(stats_data, colWidths=[160, 160, 160])
        st.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]))
        elements.append(st)
        
        elements.append(Spacer(1, 15))
        
        # Potential Stats Table (Optimized)
        elements.append(Paragraph("Potential Visibility (Optimized SEO/GEO)", styles['SubHeader']))
        
        # Check if actual simulation data exists to override the simplistic potential metrics
        sim_data = data.get("simulation")
        if sim_data and sim_data.get("optimized"):
            opt_data = sim_data["optimized"]
            pot_avg_rank = opt_data.get("average_visibility", pot_avg_rank)
            pot_fallout_percent = opt_data.get("search_fallout_percent", pot_fallout_percent)
            
            # Recalculate pot_max_reach safely via grid data if present
            if "grid" in opt_data:
                pot_max_reach = 0
                for p in opt_data["grid"]:
                    if p["score"] <= 5:
                        d = get_distance_py(center["lat"], center["lng"], p["lat"], p["lng"])
                        if d > pot_max_reach: pot_max_reach = d

        pot_stats_data = [
            [
                Paragraph(f"<font color='{SUCCESS.hexval()}' size=10><b>Potential Avg.</b></font><br/><br/><font size=18><b>Rank #{pot_avg_rank:.1f}</b></font>", styles['BodyText_Custom']),
                Paragraph(f"<font color='{SUCCESS.hexval()}' size=10><b>Potential Fallout</b></font><br/><br/><font size=18><b>{int(pot_fallout_percent)}%</b></font>", styles['BodyText_Custom']),
                Paragraph(f"<font color='{SUCCESS.hexval()}' size=10><b>Potential Reach</b></font><br/><br/><font size=18><b>{pot_max_reach:.1f} km</b></font>", styles['BodyText_Custom'])
            ]
        ]
        pst = Table(pot_stats_data, colWidths=[160, 160, 160])
        pst.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('BACKGROUND', (0, 0), (-1, -1), HexColor("#f0fff4")), # Light green bg for potential
        ]))
        elements.append(pst)
        
        elements.append(Spacer(1, 25))
        
        # Add Simulation Insights if available
        if sim_data and "delta" in sim_data:
            elements.append(Paragraph("GEO Optimization Simulation Insights", styles['SubHeader']))
            delta = sim_data["delta"]
            
            sim_insights = [
                ["Metric", "Current", "Optimized", "Improvement"],
                ["Average Rank", f"#{avg_rank:.1f}", f"#{pot_avg_rank:.1f}", f"{delta.get('visibility_improvement_points', 0):.1f} pos"],
                ["Search Fallout", f"{int(fallout_percent)}%", f"{int(pot_fallout_percent)}%", f"{delta.get('fallout_reduction_percent', 0):.1f}% reduction"],
                ["Local Authority", f"{sim_data.get('baseline', {}).get('local_authority_score', 0)}", f"{sim_data.get('optimized', {}).get('local_authority_score', 0)}", f"+{sim_data.get('optimized', {}).get('local_authority_score', 0) - sim_data.get('baseline', {}).get('local_authority_score', 0)}"]
            ]
            
            sit = Table(sim_insights, colWidths=[120, 80, 80, 120])
            sit.setStyle(make_table_style())
            elements.append(sit)
            elements.append(Spacer(1, 15))


        elements.append(Paragraph("Geographic Ranking Distribution (5x5 Grid)", styles['SubHeader']))
        elements.append(Spacer(1, 10))
        
        # 5x5 Grid Table
        grid_rows_data = []
        for i in range(5):
            row = []
            for j in range(5):
                idx = i * 5 + j
                score_val = grid[idx]["score"]
                cell_color = SUCCESS if score_val <= 5 else (WARNING if score_val <= 12 else DANGER)
                row.append(Paragraph(f"<font color='{white.hexval()}'><b>{score_val}</b></font>", 
                           ParagraphStyle(f'CellStyle{idx}', alignment=TA_CENTER, backColor=cell_color, borderPadding=5)))
            grid_rows_data.append(row)
            
        gt = Table(grid_rows_data, colWidths=[50, 50, 50, 50, 50])
        gt.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 1, white),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
        ]))
        elements.append(gt)
    else:
        elements.append(Paragraph(
            "Geographic visibility analysis provides insights into search 'fallout' zones where "
            "your brand loses citable authority. Run the 'grid' audit step to populate this section.",
            styles['BodyText_Custom']
        ))

    elements.append(PageBreak())

    # ============================================================
    # EXECUTIVE SUMMARY
    # ============================================================
    elements.append(Paragraph("Executive Summary", styles['SectionHeader']))
    elements.append(HRFlowable(width="100%", thickness=1, color=ACCENT, spaceAfter=12))

    if executive_summary:
        elements.append(Paragraph(executive_summary, styles['BodyText_Custom']))
    else:
        elements.append(Paragraph(
            f"This report presents the findings of a comprehensive Generative Engine Optimization (GEO) "
            f"audit conducted on <b>{brand_name}</b> ({url}). The analysis evaluated the website's readiness "
            f"for AI-powered search engines including Google AI Overviews, ChatGPT, Perplexity, Gemini, "
            f"and Bing Copilot. The overall GEO Readiness Score is <b>{geo_score}/100</b>, "
            f"placing the site in the <b>{get_score_label(geo_score)}</b> tier.",
            styles['BodyText_Custom']
        ))

    elements.append(Spacer(1, 16))

    # ============================================================
    # SCORE BREAKDOWN
    # ============================================================
    elements.append(Paragraph("GEO Score Breakdown", styles['SectionHeader']))
    elements.append(HRFlowable(width="100%", thickness=1, color=ACCENT, spaceAfter=12))

    score_data = [
        ["Component", "Score", "Weight", "Weighted"],
        [Paragraph("AI Citability & Visibility", styles['TableBody']), f"{ai_citability}/100", "25%", f"{round(ai_citability * 0.25, 1)}"],
        [Paragraph("Brand Authority Signals", styles['TableBody']), f"{brand_authority}/100", "20%", f"{round(brand_authority * 0.20, 1)}"],
        [Paragraph("Content Quality & E-E-A-T", styles['TableBody']), f"{content_eeat}/100", "20%", f"{round(content_eeat * 0.20, 1)}"],
        [Paragraph("Technical Foundations", styles['TableBody']), f"{technical}/100", "15%", f"{round(technical * 0.15, 1)}"],
        [Paragraph("Strategic Schema Implementation", styles['TableBody']), f"{schema_score}/100", "10%", f"{round(schema_score * 0.10, 1)}"],
        [Paragraph("Platform Optimization", styles['TableBody']), f"{platform_optimization}/100", "10%", f"{round(platform_optimization * 0.10, 1)}"],
        [Paragraph("Google Business/Local Authority", styles['TableBody']), f"{local_authority}/100", "10%", f"{round(local_authority * 0.10, 1)}"],
        [Paragraph("<b>OVERALL</b>", styles['TableBody']), f"{geo_score}/100", "100%", f"{geo_score}"],
    ]

    score_table = Table(score_data, colWidths=[200, 80, 60, 80])
    style = make_table_style()

    # Bold the last row
    style.add('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold')
    style.add('BACKGROUND', (0, -1), (-1, -1), MEDIUM_BG)

    # Color-code score cells
    for i in range(1, len(score_data) - 1):
        try:
            score_val = int(float(score_data[i][1].split("/")[0]))
            color = get_score_color(score_val)
            style.add('TEXTCOLOR', (1, i), (1, i), color)
        except (ValueError, IndexError):
            continue

    score_table.setStyle(style)
    elements.append(score_table)

    elements.append(Spacer(1, 16))

    # Score bar chart
    chart_scores = [ai_citability, brand_authority, local_authority, content_eeat, technical, schema_score, platform_optimization]
    chart_labels = ["Citability", "Brand", "Local", "Content", "Technical", "Schema", "Platform"]
    elements.append(create_bar_chart(chart_scores, chart_labels))

    elements.append(PageBreak())

    # ============================================================
    # AI PLATFORM READINESS
    # ============================================================
    elements.append(Paragraph("AI Platform Readiness", styles['SectionHeader']))
    elements.append(HRFlowable(width="100%", thickness=1, color=ACCENT, spaceAfter=12))

    elements.append(Paragraph(
        "These scores reflect how likely your content is to be cited by each AI search platform. "
        "A score below 50 indicates significant barriers to citation on that platform.",
        styles['BodyText_Custom']
    ))
    elements.append(Spacer(1, 10))

    # Platform chart
    if platforms:
        elements.append(create_platform_chart(platforms))

    elements.append(Spacer(1, 40))

    platform_table_data = [["AI Platform", "Score", "Status"]]
    for name, score in platforms.items():
        status = get_score_label(score)
        platform_table_data.append([name, f"{score}/100", status])

    pt = Table(platform_table_data, colWidths=[180, 80, 150])
    pt_style = make_table_style()
    for i in range(1, len(platform_table_data)):
        score_val = int(float(platform_table_data[i][1].split("/")[0]))
        color = get_score_color(score_val)
        pt_style.add('TEXTCOLOR', (1, i), (1, i), color)
    pt.setStyle(pt_style)
    elements.append(pt)

    elements.append(PageBreak())

    # ============================================================
    # AI CRAWLER ACCESS
    # ============================================================
    elements.append(Paragraph("AI Crawler Access Status", styles['SectionHeader']))
    elements.append(HRFlowable(width="100%", thickness=1, color=ACCENT, spaceAfter=12))

    elements.append(Paragraph(
        "Blocking AI crawlers prevents AI platforms from citing your content. "
        "The table below shows which AI crawlers can currently access your site.",
        styles['BodyText_Custom']
    ))
    elements.append(Spacer(1, 8))

    if crawler_access:
        crawler_data = [["Crawler", "Platform", "Status", "Recommendation"]]
        for crawler_name, info in crawler_access.items():
            if isinstance(info, dict):
                crawler_data.append([
                    Paragraph(crawler_name, styles['TableBody']),
                    Paragraph(info.get("platform", ""), styles['TableBody']),
                    info.get("status", "Unknown"),
                    Paragraph(info.get("recommendation", ""), styles['TableBody']),
                ])
            else:
                crawler_data.append([Paragraph(crawler_name, styles['TableBody']), "", str(info), ""])

        ct = Table(crawler_data, colWidths=[100, 100, 80, 180])
        ct_style = make_table_style()

        # Color status cells
        for i in range(1, len(crawler_data)):
            status = crawler_data[i][2].upper()
            if "ALLOW" in status:
                ct_style.add('TEXTCOLOR', (2, i), (2, i), SUCCESS)
            elif "BLOCK" in status:
                ct_style.add('TEXTCOLOR', (2, i), (2, i), DANGER)

        ct.setStyle(ct_style)
        elements.append(ct)
    else:
        elements.append(Paragraph(
            "<i>Run Step 4 to populate this section with AI crawler access data.</i>",
            styles['BodyText_Custom']
        ))

    elements.append(PageBreak())
    
    # ============================================================
    # GOOGLE BUSINESS PROFILE (GBP) ANALYSIS
    # ============================================================
    elements.append(Paragraph("Google Business Profile (GBP) Analysis", styles['SectionHeader']))
    elements.append(HRFlowable(width="100%", thickness=1, color=ACCENT, spaceAfter=12))

    if gbp:
        elements.append(Paragraph(
            f"<b>Profile Analyzed:</b> {gbp.get('business_name', 'Unknown Business')}<br/>"
            f"<b>Profile URL:</b> {gbp.get('gbp_url', 'Not Provided')}<br/>"
            f"<b>Analysis Date:</b> {gbp.get('audit_date', 'N/A')}",
            styles['BodyText_Custom']
        ))
        elements.append(Spacer(1, 15))

        # Local Authority Score Card
        gbp_score = gbp.get('overall_local_score', 0)
        gbp_status = gbp.get('status', 'Fair')
        score_color = get_score_color(gbp_score)
        
        elements.append(Paragraph(
            f"<font color='{score_color}' size=14><b>Local Authority Score: {gbp_score}/100</b></font> ({gbp_status})",
            styles['BodyText_Custom']
        ))
        elements.append(Spacer(1, 15))

        # Insights Table
        if gbp.get("insights"):
            elements.append(Paragraph("AI Readiness Insights", styles['SubHeader']))
            insight_data = [["Factor", "Score", "Details"]]
            for insight in gbp["insights"]:
                insight_data.append([
                    Paragraph(insight.get("title", ""), styles['TableBody']),
                    f"{insight.get('score', 0)}/100",
                    Paragraph(insight.get("details", ""), styles['TableBody'])
                ])
            
            it = Table(insight_data, colWidths=[120, 60, 300])
            it_style = make_table_style()
            for i in range(1, len(insight_data)):
                s_val = int(float(insight_data[i][1].split("/")[0]))
                it_style.add('TEXTCOLOR', (1, i), (1, i), get_score_color(s_val))
            it.setStyle(it_style)
            elements.append(it)
            elements.append(Spacer(1, 20))
    else:
        elements.append(Paragraph(
            "No Google Business Profile was provided for analysis. Local AI search visibility "
            "may be limited without a verified and optimized GBP.",
            styles['BodyText_Custom']
        ))

    elements.append(PageBreak())

    # ============================================================
    # LOCAL DIRECTORY VISIBILITY
    # ============================================================
    elements.append(Paragraph("Local Directory Visibility", styles['SectionHeader']))
    elements.append(HRFlowable(width="100%", thickness=1, color=ACCENT, spaceAfter=12))

    if directories:
        elements.append(Paragraph(
            "Local directories are critical 'Ground Truth' sources that AI models use to verify "
            "business existence, location, and reputation.",
            styles['BodyText_Custom']
        ))
        elements.append(Spacer(1, 10))

        dir_score = directories.get("score", 0)
        dir_color = get_score_color(dir_score)

        elements.append(Paragraph(
            f"<font color='{dir_color}' size=14><b>Directory Authority Score: {dir_score}/100</b></font>",
            styles['BodyText_Custom']
        ))
        elements.append(Spacer(1, 12))

        # Recommendations for directories
        if directories.get("recommendations"):
            elements.append(Paragraph("Strategic Recommendations", styles['SubHeader']))
            for rec in directories["recommendations"]:
                elements.append(Paragraph(rec, styles['Recommendation'], bulletText='•'))
            elements.append(Spacer(1, 15))

        # Key Findings for directories
        if directories.get("key_findings"):
            elements.append(Paragraph("Key Insights", styles['SubHeader']))
            for finding in directories["key_findings"]:
                elements.append(Paragraph(finding, styles['DetailedDescription'], bulletText='-'))
    else:
        elements.append(Paragraph(
            "No local directory data was found during this scan. Optimizing your presence on "
            "Yelp, YellowPages, and industry-specific directories is highly recommended for AI visibility.",
            styles['BodyText_Custom']
        ))

    elements.append(PageBreak())

    # ============================================================
    # KEY FINDINGS
    # ============================================================
    elements.append(Paragraph("Key Findings", styles['SectionHeader']))
    elements.append(HRFlowable(width="100%", thickness=1, color=ACCENT, spaceAfter=12))

    if findings:
        for finding in findings:
            severity = finding.get("severity", "info").upper()
            title = finding.get("title", "")
            description = finding.get("description", "")
            detailed_description = finding.get("detailed_description", "")
            impact = finding.get("impact", "")
            fix_example = finding.get("fix_example", "")

            if severity == "CRITICAL" or severity == "DANGER":
                sev_color = DANGER
            elif severity == "HIGH":
                sev_color = WARNING
            elif severity == "MEDIUM":
                sev_color = INFO
            else:
                sev_color = TEXT_SECONDARY

            # Title with severity
            elements.append(Paragraph(
                f'<font color="{sev_color.hexval()}">[{severity}]</font> <b>{title}</b>',
                styles['BodyText_Custom']
            ))

            # Descriptions
            if detailed_description:
                elements.append(Paragraph(detailed_description, styles['DetailedDescription']))
            elif description:
                elements.append(Paragraph(description, styles['DetailedDescription']))

            # Impact
            if impact:
                elements.append(Paragraph(f"<b>GEO Impact:</b> {impact}", styles['FindingImpact']))

            # Fix Example
            if fix_example:
                # Clean up any potential markdown code blocks from AI
                clean_fix = fix_example.replace("```json", "").replace("```html", "").replace("```", "").strip()
                elements.append(Paragraph("<b>Fix Example:</b>", styles['DetailedDescription']))
                elements.append(Paragraph(clean_fix, styles['CodeFix']))

            elements.append(Spacer(1, 8))
    else:
        elements.append(Paragraph(
            "<i>Run a full /geo audit to populate findings.</i>",
            styles['BodyText_Custom']
        ))

    elements.append(PageBreak())

    # ============================================================
    # GEO-FIRST OPTIMIZATION ROADMAP
    # ============================================================
    elements.append(Paragraph("GEO-First Optimization Roadmap", styles['SectionHeader']))
    elements.append(HRFlowable(width="100%", thickness=1, color=ACCENT, spaceAfter=8))
    
    elements.append(Paragraph(
        "This roadmap prioritizes <b>Generative Engine Optimization (GEO)</b> to maximize visibility in AI search "
        "results (ChatGPT, Perplexity, Google SGE, etc.), followed by Local and Technical SEO enhancements.",
        styles['SmallText']
    ))
    elements.append(Spacer(1, 12))

    def render_roadmap_section(title, items, subtitle):
        elements.append(Paragraph(title, styles['SubHeader']))
        elements.append(Paragraph(subtitle, styles['SmallText']))
        elements.append(Spacer(1, 6))
        
        if items:
            for i, item in enumerate(items, 1):
                if isinstance(item, dict):
                    action = item.get("action", "")
                    cat = item.get("category", "SEO").upper()
                    impact = item.get("impact", "")
                    
                    # Color coding for categories
                    cat_color = HIGHLIGHT if cat == "GEO" else (SUCCESS if cat == "LOCAL" else INFO)
                    
                    text = f"<b>{i}. <font color='{cat_color}'>[{cat}]</font></b> {action} — <i>{impact}</i>"
                else:
                    text = f"<b>{i}.</b> {item}"
                elements.append(Paragraph(text, styles['Recommendation']))
        else:
            elements.append(Paragraph("<i>No specific items generated. Follow baseline recommendations.</i>", styles['SmallText']))
        elements.append(Spacer(1, 12))

    render_roadmap_section("Quick Wins (This Week)", quick_wins, "High impact, low effort — implement these immediately for fastest growth.")
    render_roadmap_section("Medium-Term Improvements (This Month)", medium_term, "Performance optimization — requires content or technical adjustments.")
    render_roadmap_section("Strategic Initiatives (This Quarter)", strategic, "Long-term authority — building sustainable dominance in AI search.")

    elements.append(PageBreak())

    # ============================================================
    # METHODOLOGY & GLOSSARY
    # ============================================================
    elements.append(Paragraph("Appendix: Methodology", styles['SectionHeader']))
    elements.append(HRFlowable(width="100%", thickness=1, color=ACCENT, spaceAfter=12))

    elements.append(Paragraph(
        f"This GEO audit was conducted on {date} analyzing {url}. "
        "The analysis evaluated the website across six dimensions: AI Citability & Visibility (25%), "
        "Brand Authority Signals (20%), Content Quality & E-E-A-T (20%), Technical Foundations (15%), "
        "Structured Data (10%), and Platform Optimization (10%).",
        styles['BodyText_Custom']
    ))

    elements.append(Spacer(1, 8))

    elements.append(Paragraph(
        "<b>Platforms assessed:</b> Google AI Overviews, ChatGPT Web Search, Perplexity AI, "
        "Google Gemini, Bing Copilot",
        styles['BodyText_Custom']
    ))

    elements.append(Paragraph(
        "<b>Standards referenced:</b> Google Search Quality Rater Guidelines (Dec 2025), "
        "Schema.org specification, Core Web Vitals (2026 thresholds), "
        "llms.txt emerging standard, RSL 1.0 licensing framework",
        styles['BodyText_Custom']
    ))

    elements.append(Spacer(1, 16))

    # Glossary
    elements.append(Paragraph("Glossary", styles['SubHeader']))
    elements.append(Spacer(1, 20))

    glossary = [
        ["Term", "Definition"],
        ["GEO", Paragraph("Generative Engine Optimization — optimizing content for AI search citation", styles['TableBody'])],
        ["AIO", Paragraph("AI Overviews — Google's AI-generated answer boxes in search results", styles['TableBody'])],
        ["E-E-A-T", Paragraph("Experience, Expertise, Authoritativeness, Trustworthiness", styles['TableBody'])],
        ["SSR", Paragraph("Server-Side Rendering — generating HTML on the server for crawler access", styles['TableBody'])],
        ["CWV", Paragraph("Core Web Vitals — Google's page experience metrics (LCP, INP, CLS)", styles['TableBody'])],
        ["INP", Paragraph("Interaction to Next Paint — responsiveness metric (replaced FID March 2024)", styles['TableBody'])],
        ["JSON-LD", Paragraph("JavaScript Object Notation for Linked Data — preferred structured data format", styles['TableBody'])],
        ["sameAs", Paragraph("Schema.org property linking an entity to its profiles on other platforms", styles['TableBody'])],
        ["llms.txt", Paragraph("Proposed standard file for guiding AI systems about site content", styles['TableBody'])],
        ["IndexNow", Paragraph("Protocol for instantly notifying search engines of content changes", styles['TableBody'])],
    ]

    gt = Table(glossary, colWidths=[80, 380])
    gt.setStyle(make_table_style())
    elements.append(gt)

    elements.append(Spacer(1, 30))

    # Footer disclaimer
    elements.append(HRFlowable(width="100%", thickness=0.5, color=lightgrey, spaceAfter=8))
    elements.append(Paragraph(
        "This report was generated by the GEO-SEO Claude Code Analysis Tool. "
        "Scores and recommendations are based on automated analysis and industry benchmarks. "
        "Results should be validated with platform-specific testing.",
        styles['SmallText']
    ))

    # ============================================================
    # BUILD PDF
    # ============================================================
    doc.build(elements, onFirstPage=header_footer, onLaterPages=header_footer)
    return output_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        # Generate a sample report for demonstration
        sample_data = {
            "url": "https://example.com",
            "brand_name": "Example Company",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "geo_score": 58,
            "scores": {
                "ai_citability": 45,
                "brand_authority": 62,
                "content_eeat": 70,
                "technical": 55,
                "schema": 30,
                "platform_optimization": 48,
            },
            "platforms": {
                "Google AI Overviews": 65,
                "ChatGPT": 52,
                "Perplexity": 48,
                "Gemini": 60,
                "Bing Copilot": 45,
            },
            "executive_summary": (
                "This report presents the findings of a comprehensive GEO audit "
                "conducted on Example Company (https://example.com). The site achieved "
                "an overall GEO Readiness Score of 58/100, placing it in the Moderate tier. "
                "The strongest area is Content Quality (70/100), while Structured Data (30/100) "
                "represents the biggest opportunity for improvement. Implementing schema markup, "
                "allowing AI crawlers, and optimizing content structure could increase the score "
                "to approximately 78/100 within 90 days."
            ),
            "findings": [
                {"severity": "critical", "title": "No Schema Markup Detected",
                 "description": "The site has no JSON-LD structured data, making it difficult for AI models to understand entity relationships."},
                {"severity": "high", "title": "JavaScript-Only Rendering",
                 "description": "Key content pages use client-side rendering, making them invisible to AI crawlers that don't execute JavaScript."},
                {"severity": "high", "title": "Missing llms.txt",
                 "description": "No llms.txt file exists to guide AI systems to the most important content."},
                {"severity": "medium", "title": "Weak Brand Entity Presence",
                 "description": "Brand is not present on Wikipedia or Wikidata, limiting entity recognition by AI models."},
                {"severity": "medium", "title": "Content Not Optimized for Citability",
                 "description": "Most content blocks are either too short or too long for optimal AI citation (target: 134-167 words)."},
            ],
            "quick_wins": [
                "Allow all Tier 1 AI crawlers in robots.txt",
                "Add publication dates to all content pages",
                "Create llms.txt file with key page references",
                "Add author bylines with credentials",
                "Fix meta descriptions on top 10 pages",
            ],
            "medium_term": [
                "Implement Organization schema with sameAs linking",
                "Add Article + Person schema to all blog posts",
                "Restructure content with question-based H2 headings",
                "Optimize content blocks for 134-167 word citability",
                "Implement server-side rendering for content pages",
            ],
            "strategic": [
                "Build Wikipedia/Wikidata entity presence",
                "Develop Reddit community engagement strategy",
                "Create YouTube content aligned with AI search queries",
                "Establish original research publication program",
                "Build comprehensive topical authority content clusters",
            ],
            "crawler_access": {
                "GPTBot": {"platform": "ChatGPT", "status": "Allowed", "recommendation": "Keep allowed"},
                "ClaudeBot": {"platform": "Claude", "status": "Allowed", "recommendation": "Keep allowed"},
                "PerplexityBot": {"platform": "Perplexity", "status": "Blocked", "recommendation": "Unblock for visibility"},
                "Google-Extended": {"platform": "Gemini", "status": "Allowed", "recommendation": "Keep allowed"},
                "Bingbot": {"platform": "Bing Copilot", "status": "Allowed", "recommendation": "Keep allowed"},
            },
        }

        output_file = "GEO-REPORT-sample.pdf"
        result = generate_report(sample_data, output_file)
        print(f"Report generated: {result}")

    else:
        # Load data from file or stdin
        input_path = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else "GEO-REPORT.pdf"

        if input_path == "-":
            data = json.loads(sys.stdin.read())
        else:
            with open(input_path) as f:
                data = json.load(f)

        result = generate_report(data, output_file)
        print(f"Report generated: {result}")
