"""Generate the two-page sales briefing from a validated run; requires reportlab."""

import argparse
import json
from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph

ROOT = Path(__file__).resolve().parents[1]
INK, MUTED, PAPER, RED, TEAL, LINE = (
    "#20323C",
    "#647579",
    "#F8F6F1",
    "#B74732",
    "#126F69",
    "#D6D8D2",
)
W, H, M = 1000, 740, 48


def build(stage, output):
    a = json.loads((Path(stage) / "analysis.json").read_text(encoding="utf-8"))
    r = a["business_review"]
    s = r["summary"]
    m = a["metrics"]
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    target = output / "case-study.pdf"
    c = canvas.Canvas(str(target), pagesize=(W, H), pageCompression=1)
    c.setTitle("The monthly sales review | " + s["month"])
    c.setAuthor("Zak Rademacher")

    def text(x, y, value, size=11, color=INK, font="Helvetica", right=False):
        c.setFillColor(HexColor(color))
        c.setFont(font, size)
        (c.drawRightString if right else c.drawString)(x, y, str(value))

    def para(x, y, value, width, size=11, color=MUTED, font="Helvetica", leading=None):
        p = Paragraph(
            escape(str(value)),
            ParagraphStyle(
                "body",
                fontName=font,
                fontSize=size,
                leading=leading or size * 1.4,
                textColor=HexColor(color),
            ),
        )
        _, height = p.wrap(width, 1000)
        p.drawOn(c, x, y - height)

    def rule(y):
        c.setStrokeColor(HexColor(LINE))
        c.setLineWidth(0.6)
        c.line(M, y, W - M, y)

    def base(page):
        c.setFillColor(HexColor(PAPER))
        c.rect(0, 0, W, H, fill=1, stroke=0)
        text(M, H - 42, "FIELDNOTES / SALES", 10, MUTED, "Helvetica-Bold")
        text(W - M, H - 42, s["month"], 10, MUTED, right=True)
        rule(37)
        text(
            M,
            21,
            "HISTORICAL SAMPLE / SOURCE MONETARY UNITS / CURRENCY UNSPECIFIED",
            8,
            MUTED,
        )
        text(W - M, 21, f"{page:02d} / 02", 8, MUTED, right=True)

    money = lambda x: "n.a." if x is None else f"{x:,.2f}"
    pct = lambda x: "n.a." if x is None else f"{x:+.1%}"
    tone = lambda x: RED if x is not None and x < 0 else TEAL if x else MUTED
    base(1)
    text(M, H - 98, "The monthly sales review", 35, font="Times-Roman")
    text(
        M,
        H - 123,
        f"{s['current_start']} to {s['current_end']}  /  vs {s['prior_start']} to {s['prior_end']}",
        11,
        MUTED,
    )
    rule(H - 144)
    cur, prior = s["current"], s["prior"]
    cw = (W - 2 * M - 32) / 3
    cards = [
        (
            "SALES",
            money(cur["sales_units"] / 10000),
            money(prior["sales_units"] / 10000) if prior else "missing",
            s["sales_change_pct"],
        ),
        (
            "ORDERS",
            f"{cur['orders']:,}",
            f"{prior['orders']:,}" if prior else "missing",
            s["orders_change_pct"],
        ),
        (
            "AVERAGE ORDER",
            money(cur["average_order"]),
            money(prior["average_order"]) if prior else "missing",
            s["average_order_change_pct"],
        ),
    ]
    for i, (name, value, previous, delta) in enumerate(cards):
        x = M + i * (cw + 16)
        c.setFillColor(HexColor("#FFFFFF"))
        c.rect(x, 444, cw, 132, fill=1, stroke=0)
        text(x + 18, 553, name, 10, MUTED, "Helvetica-Bold")
        text(x + 18, 512, value, 30)
        text(x + 18, 480, pct(delta), 18, tone(delta), "Helvetica-Bold")
        text(x + 18, 461, "Prior: " + previous + " / same period", 9, MUTED)
    para(M, 422, r["headline"], W - 2 * M, 23, INK, "Times-Roman", 26)
    para(M, 382, r["interpretation"], W - 2 * M, 11)
    shared_maximum = (
        max(
            [
                abs(d["change_units"])
                for rows in r["drivers"].values()
                for d in rows
                if d["change_units"] is not None
            ]
            or [1]
        )
        or 1
    )
    for scope, x in [("category", M), ("region", 538)]:
        rows = r["drivers"][scope]
        w = 414
        y = 330
        text(x, y, scope.title() + " sales change", 14, font="Helvetica-Bold")
        text(x, y - 17, "Change vs same period last year", 9, MUTED)
        y -= 45
        maximum = shared_maximum
        for d in rows[:4]:
            delta = d["change_units"]
            v = delta / 10000 if delta is not None else None
            text(x, y, d["member"], 11)
            text(x + w, y, money(v), 11, tone(v), right=True)
            center = x + w / 2
            by = y - 17
            c.setFillColor(HexColor("#E5E7E1"))
            c.rect(x, by, w, 7, fill=1, stroke=0)
            if delta is not None:
                length = (w / 2 - 8) * abs(delta) / maximum
                c.setFillColor(HexColor(tone(delta)))
                c.rect(
                    center - length if delta < 0 else center,
                    by,
                    length,
                    7,
                    fill=1,
                    stroke=0,
                )
            c.setStrokeColor(HexColor(MUTED))
            c.line(center, by - 2, center, by + 9)
            y -= 43
    para(
        M,
        95,
        "Read the largest declines first. Category and region are overlapping views of the same sales; their changes must not be added together.",
        W - 2 * M,
        10,
    )
    para(
        M,
        64,
        "Equal day-of-month cutoffs support comparison; they do not prove equal coverage or a certified accounting close.",
        W - 2 * M,
        9,
    )
    c.showPage()
    base(2)
    text(M, H - 94, "From movement to a review list", 30, font="Times-Roman")
    text(M, H - 120, "01 / EXPLAIN THE TOTAL", 10, MUTED, "Helvetica-Bold")
    bridge = [
        ("Order-volume effect", s["order_volume_effect"]),
        ("Average-order effect", s["average_order_effect"]),
        (
            "Net sales change",
            (
                s["sales_change_units"] / 10000
                if s["sales_change_units"] is not None
                else None
            ),
        ),
    ]
    for i, (name, v) in enumerate(bridge):
        x = M + i * (cw + 16)
        text(x, H - 146, name, 10, MUTED)
        text(x, H - 176, money(v), 23, tone(v))
    para(
        M,
        H - 191,
        "Volume effect = change in orders x prior average order. Average-order effect = current orders x change in average order. This bridge reconciles the sales change when averages exist; it does not establish cause.",
        W - 2 * M,
        10,
    )
    rule(H - 235)
    text(M, H - 260, "02 / TRACE THE LARGEST DECLINES", 10, MUTED, "Helvetica-Bold")
    y = H - 285
    if not r["actions"]:
        text(
            M,
            y,
            "No ranked declines available. Inspect the baseline and source coverage.",
            11,
            MUTED,
        )
    for d in r["actions"][:5]:
        text(M, y, f"{d['priority']:02d}", 11, MUTED)
        text(M + 32, y, d["segment"] + " / " + d["scope"], 11, font="Helvetica-Bold")
        text(W - M, y, money(d["sales_change"]), 12, RED, right=True)
        para(
            M + 32,
            y - 10,
            d["reason"] + " | Check: " + d["product_ids_to_check"],
            W - 2 * M - 32,
            9,
            leading=12,
        )
        y -= 46
    if len(r["actions"]) > 5:
        text(
            M,
            211,
            f"First 5 of {len(r['actions'])} declining segments. Full list: review_actions.csv",
            9,
            MUTED,
        )
    rule(197)
    text(M, 176, "03 / REPEAT THE REPORT", 10, MUTED, "Helvetica-Bold")
    para(
        M,
        161,
        "Add or replace monthly CSVs in data/incoming. Retain history. Run python refresh.py --render --pdf. A successful run publishes a new Excel, HTML, follow-up CSV and this PDF in a dated folder. Use runs/latest.json to find it. Export and import review notes before refreshing.",
        560,
        10,
    )
    para(
        655,
        176,
        f"{m['input_files']} monthly files / {m['lines']:,} lines / {m['orders']:,} distinct orders. Python + SQLite validate the delivery before publishing. Excel generation requires the compatible spreadsheet runtime; --summary-only produces HTML/CSV with Python alone.",
        297,
        9,
    )
    para(
        M,
        94,
        "Source: Kaggle rohitsahoo/sales-forecasting (data card: GPL 2). Historical sample, not a current business feed. Independent portfolio demonstration. Sales are not profit, cash receipts or forecast demand.",
        W - 2 * M,
        9,
    )
    c.linkURL(
        "https://www.kaggle.com/datasets/rohitsahoo/sales-forecasting",
        (M, 62, 600, 95),
        relative=0,
        thickness=0,
    )
    c.save()
    return target


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--stage", type=Path, default=ROOT / "evidence")
    p.add_argument("--output", type=Path, default=ROOT / "deliverables")
    args = p.parse_args()
    print(build(args.stage, args.output))
