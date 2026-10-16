"""Turn validated sales into a matched-period business review and concrete follow-up leads."""

import calendar
import html
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def rate(current, prior):
    return current / prior - 1 if prior else None


def compare(db, start, end):
    return dict(
        db.execute(
            "SELECT COUNT(*) lines,COUNT(DISTINCT order_id) orders,COALESCE(SUM(sales_units),0) sales_units "
            "FROM lines WHERE order_date BETWEEN ? AND ?",
            (start, end),
        ).fetchone()
    )


def build_review(db, metrics):
    month = metrics["last_month"]
    year, number = map(int, month.split("-"))
    day = (
        int(metrics["last_date"][-2:])
        if metrics["last_date"][:7] == month
        else calendar.monthrange(year, number)[1]
    )
    day = min(day, calendar.monthrange(year - 1, number)[1])
    start, end = f"{month}-01", f"{month}-{day:02d}"
    prior_month = f"{year-1:04d}-{number:02d}"
    prior_end = f"{prior_month}-{min(day, calendar.monthrange(year-1, number)[1]):02d}"
    prior_start = prior_month + "-01"
    known = db.execute(
        "SELECT coverage FROM periods WHERE month=?", (prior_month,)
    ).fetchone()
    available = bool(known and known[0] == "Imported")
    current = compare(db, start, end)
    prior = compare(db, prior_start, prior_end) if available else None
    current["average_order"] = (
        current["sales_units"] / 10000 / current["orders"]
        if current["orders"]
        else None
    )
    if prior:
        prior["average_order"] = (
            prior["sales_units"] / 10000 / prior["orders"] if prior["orders"] else None
        )
    summary = {
        "month": month,
        "current_start": start,
        "current_end": end,
        "prior_start": prior_start,
        "prior_end": prior_end,
        "prior_available": available,
        "current": current,
        "prior": prior,
        "sales_change_units": None,
        "sales_change_pct": None,
        "orders_change_pct": None,
        "average_order_change_pct": None,
        "order_volume_effect": None,
        "average_order_effect": None,
    }
    if prior:
        summary.update(
            sales_change_units=current["sales_units"] - prior["sales_units"],
            sales_change_pct=rate(current["sales_units"], prior["sales_units"]),
            orders_change_pct=rate(current["orders"], prior["orders"]),
        )
        if current["average_order"] is not None and prior["average_order"]:
            summary["average_order_change_pct"] = rate(
                current["average_order"], prior["average_order"]
            )
            summary["order_volume_effect"] = (
                current["orders"] - prior["orders"]
            ) * prior["average_order"]
            summary["average_order_effect"] = current["orders"] * (
                current["average_order"] - prior["average_order"]
            )
    reports = {}
    query = (ROOT / "sql/review_drivers.sql").read_text()
    parameters = {
        "start": start,
        "end": end,
        "prior_start": prior_start,
        "prior_end": prior_end,
    }
    for scope in ["category", "region"]:
        rows = [dict(row) for row in db.execute(query, {**parameters, "scope": scope})]
        for row in rows:
            row["prior_sales_units"] = row["prior_sales_units"] if available else None
            row["prior_orders"] = row["prior_orders"] if available else None
            row["change_units"] = (
                row["current_sales_units"] - row["prior_sales_units"]
                if available
                else None
            )
            row["change_pct"] = (
                rate(row["current_sales_units"], row["prior_sales_units"])
                if available
                else None
            )
        reports[scope] = sorted(
            rows,
            key=lambda r: (
                r["change_units"] if r["change_units"] is not None else 0,
                r["member"],
            ),
        )
    actions = []
    product_query = (ROOT / "sql/review_products.sql").read_text()
    for scope, rows in reports.items():
        for row in rows:
            if row["change_units"] is None or row["change_units"] >= 0:
                continue
            products = [
                dict(r)
                for r in db.execute(
                    product_query,
                    {**parameters, "scope": scope, "member": row["member"]},
                )
            ]
            focus = ", ".join(r["product_id"] for r in products[:3])
            smaller_orders = row["current_orders"] >= row["prior_orders"]
            reason = (
                "More/same orders, lower sales per order"
                if smaller_orders
                else "Fewer orders; review volume and order value"
            )
            actions.append(
                {
                    "priority": 0,
                    "scope": scope,
                    "segment": row["member"],
                    "current_sales": row["current_sales_units"] / 10000,
                    "prior_sales": row["prior_sales_units"] / 10000,
                    "sales_change": row["change_units"] / 10000,
                    "change_pct": row["change_pct"],
                    "reason": reason,
                    "product_ids_to_check": focus,
                    "next_step": "Compare the listed product IDs with their prior-period orders; check product mix and source coverage.",
                }
            )
    actions.sort(key=lambda r: (r["sales_change"], r["scope"], r["segment"]))
    for rank, action in enumerate(actions, start=1):
        action["priority"] = rank
    checks = {}
    if prior:
        for scope, rows in reports.items():
            checks[scope + "_current_sales_reconcile"] = (
                sum(r["current_sales_units"] for r in rows) == current["sales_units"]
            )
            checks[scope + "_prior_sales_reconcile"] = (
                sum(r["prior_sales_units"] for r in rows) == prior["sales_units"]
            )
            checks[scope + "_change_reconcile"] = (
                sum(r["change_units"] for r in rows) == summary["sales_change_units"]
            )
        if summary["order_volume_effect"] is not None:
            checks["arithmetic_bridge_reconciles"] = (
                abs(
                    summary["order_volume_effect"]
                    + summary["average_order_effect"]
                    - summary["sales_change_units"] / 10000
                )
                < 1e-7
            )
    if not all(checks.values()):
        raise AssertionError(checks)
    if not prior:
        headline = "Prior-year comparison unavailable: the matching monthly delivery is missing."
        interpretation = (
            "Supply the missing baseline before judging growth or ranking declines."
        )
    elif prior["sales_units"] == 0:
        headline = f"Recorded sales are {current['sales_units']/10000:,.2f}; the prior-year baseline is zero."
        interpretation = "A percentage change is unavailable against zero; compare the absolute amounts."
    else:
        direction = (
            "down"
            if summary["sales_change_units"] < 0
            else "up" if summary["sales_change_units"] > 0 else "unchanged"
        )
        headline = f"Sales {direction} {abs(summary['sales_change_pct']):.1%}; {current['orders']:,} orders versus {prior['orders']:,}."
        if summary["average_order_change_pct"] is not None:
            interpretation = f"Order count changed {summary['orders_change_pct']:+.1%}; average order value changed {summary['average_order_change_pct']:+.1%}. Review product mix and the ranked segment declines below."
        else:
            interpretation = "Inspect the absolute sales and order counts; an average-order comparison is unavailable."
    return {
        "summary": summary,
        "headline": headline,
        "interpretation": interpretation,
        "drivers": reports,
        "actions": actions,
        "checks": checks,
        "priority_rule": "Negative category and regional sales changes ranked by absolute decline; overlapping scopes must not be added.",
    }


def render_html(review, output):
    e = lambda value: html.escape(str(value))
    money = lambda value: "n.a." if value is None else f"{value:,.2f}"
    pct = lambda value: "n.a." if value is None else f"{value:+.1%}"
    s = review["summary"]
    c = s["current"]
    p = s["prior"]
    metrics = [
        (
            "Sales",
            money(c["sales_units"] / 10000),
            money(p["sales_units"] / 10000) if p else "Missing baseline",
            pct(s["sales_change_pct"]),
        ),
        (
            "Orders",
            str(c["orders"]),
            str(p["orders"]) if p else "Missing baseline",
            pct(s["orders_change_pct"]),
        ),
        (
            "Average order value",
            money(c["average_order"]),
            money(p["average_order"]) if p else "Missing baseline",
            pct(s["average_order_change_pct"]),
        ),
    ]

    def table(headers, rows):
        return (
            "<table><thead><tr>"
            + "".join("<th>" + e(x) + "</th>" for x in headers)
            + "</tr></thead><tbody>"
            + "".join(
                "<tr>" + "".join("<td>" + e(x) + "</td>" for x in row) + "</tr>"
                for row in rows
            )
            + "</tbody></table>"
        )

    body = (
        "<h1>Sales review · "
        + e(s["month"])
        + '</h1><p class="context">Historical Kaggle Superstore sample · sales in source monetary units</p><h2>'
        + e(review["headline"])
        + "</h2><p>"
        + e(review["interpretation"])
        + "</p>"
    )
    body += (
        '<p class="context">Comparison: '
        + e(s["current_start"])
        + "–"
        + e(s["current_end"])
        + " versus "
        + e(s["prior_start"])
        + "–"
        + e(s["prior_end"])
        + ". Periods use the same day-of-month cutoff.</p>"
    )
    body += table(["Measure", "Current period", "Prior year", "Change"], metrics)
    for scope in ["category", "region"]:
        body += (
            "<h2>Where the change came from · "
            + scope
            + "</h2>"
            + table(
                ["Segment", "Current sales", "Prior sales", "Change", "Change %"],
                [
                    (
                        r["member"],
                        money(r["current_sales_units"] / 10000),
                        (
                            money(r["prior_sales_units"] / 10000)
                            if r["prior_sales_units"] is not None
                            else "Missing baseline"
                        ),
                        (
                            money(r["change_units"] / 10000)
                            if r["change_units"] is not None
                            else "n.a."
                        ),
                        pct(r["change_pct"]),
                    )
                    for r in review["drivers"][scope]
                ],
            )
        )
    body += "<h2>What to review first</h2>"
    if review["actions"]:
        body += table(
            [
                "Priority",
                "Segment",
                "Sales change",
                "Observed pattern",
                "Product IDs to check",
            ],
            [
                (
                    r["priority"],
                    r["scope"] + ": " + r["segment"],
                    money(r["sales_change"]),
                    r["reason"],
                    r["product_ids_to_check"],
                )
                for r in review["actions"]
            ],
        )
        body += '<p>Compare the listed product IDs with their prior-period orders. Verify coverage and product mix before deciding on a response. <a href="review_actions.csv">Download the review list</a>.</p>'
    else:
        body += (
            "<p>"
            + (
                "No negative segment changes were found in the matched comparison."
                if p
                else "A review ranking cannot be produced without the prior-year delivery."
            )
            + "</p>"
        )
    body += '<p class="context">Category and region views overlap; their declines are separate review leads, not additive lost sales. Observed changes do not establish a cause, stock shortage, margin loss or staffing requirement. This sample ends at the last observed order date, not a certified accounting close.</p>'
    style = "body{font-family:Arial,sans-serif;max-width:1120px;margin:40px auto;padding:0 24px;color:#213047;line-height:1.55}h1{font-size:30px}h2{font-size:21px;margin-top:30px}table{border-collapse:collapse;width:100%;margin:18px 0;font-size:14px}th{background:#213047;color:white;text-align:left}td,th{padding:12px;border-bottom:1px solid #dbe2ea;vertical-align:top}tr:nth-child(even){background:#f3f6fa}.context{color:#66778a;font-size:13px}a{color:#3667af} @media print{body{margin:0;max-width:none}table{font-size:11px}td,th{padding:7px}}"
    Path(output).write_text(
        '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Sales review '
        + e(s["month"])
        + "</title><style>"
        + style
        + "</style><main>"
        + body
        + "</main></html>",
        encoding="utf-8",
    )
