"""Self-contained, accessible HTML sales briefing; no browser libraries or network calls."""

import html
from pathlib import Path


def render_html(review, output):
    e = lambda x: html.escape(str(x), quote=True)
    money = lambda x: "n.a." if x is None else f"{x:,.2f}"
    pct = lambda x: "n.a." if x is None else f"{x:+.1%}"
    s = review["summary"]
    c, p = s["current"], s["prior"]

    def tone(x):
        return "negative" if x is not None and x < 0 else "positive" if x else ""

    def card(name, current, previous, change):
        return f'<article class="metric"><h2>{name}</h2><strong>{e(current)}</strong><span class="delta {tone(change)}">{pct(change)}</span><small>vs same period last year / prior: {e(previous)}</small></article>'

    cards = "".join(
        [
            card(
                "Sales",
                money(c["sales_units"] / 10000),
                money(p["sales_units"] / 10000) if p else "missing",
                s["sales_change_pct"],
            ),
            card(
                "Orders",
                f"{c['orders']:,}",
                f"{p['orders']:,}" if p else "missing",
                s["orders_change_pct"],
            ),
            card(
                "Average order",
                money(c["average_order"]),
                money(p["average_order"]) if p else "missing",
                s["average_order_change_pct"],
            ),
        ]
    )
    panels = []
    shared_maximum = (
        max(
            [
                abs(r["change_units"])
                for rows in review["drivers"].values()
                for r in rows
                if r["change_units"] is not None
            ]
            or [1]
        )
        or 1
    )
    for scope in ["category", "region"]:
        rows = review["drivers"][scope]
        maximum = shared_maximum
        bars = []
        for r in rows:
            delta = r["change_units"]
            width = 42 * abs(delta) / maximum if delta is not None else 0
            left = 50 - width if delta is not None and delta < 0 else 50
            bars.append(
                f'<div class="driver"><div class="driver-label"><span>{e(r["member"])}</span><b class="{tone(delta)}">{money(delta/10000 if delta is not None else None)}</b></div><div class="track" aria-hidden="true"><i></i><span class="{tone(delta)}" style="left:{left:.4f}%;width:{width:.4f}%"></span></div><small>Current {money(r["current_sales_units"]/10000)} / prior {money(r["prior_sales_units"]/10000 if r["prior_sales_units"] is not None else None)} / {pct(r["change_pct"])}</small></div>'
            )
        panels.append(
            f'<section class="panel"><h3>{scope.title()} sales change</h3><p class="context">Same-period change in source monetary units</p>{"".join(bars)}</section>'
        )
    bridge = "".join(
        f'<div><small>{label}</small><strong class="{tone(value)}">{money(value)}</strong></div>'
        for label, value in [
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
    )
    actions = "".join(
        f'<tr><td>{r["priority"]:02d}</td><td><b>{e(r["segment"])}</b><small>{e(r["scope"])}</small></td><td class="negative num">{money(r["sales_change"])}</td><td>{e(r["reason"])}<small class="products">{e(r["product_ids_to_check"])}</small></td></tr>'
        for r in review["actions"]
    )
    if not actions:
        actions = (
            '<tr><td colspan="4">'
            + (
                "No declining segments in this comparison."
                if p
                else "Supply the prior-year delivery before ranking declines."
            )
            + "</td></tr>"
        )
    style = """
    :root{--ink:#20323c;--muted:#647579;--paper:#f8f6f1;--line:#d6d8d2;--red:#b74732;--teal:#126f69}
    *{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:16px/1.55 Arial,sans-serif}main{max-width:1180px;margin:auto;padding:48px 36px}header{border-bottom:1px solid var(--line);padding-bottom:26px}.eyebrow{font-size:12px;letter-spacing:.16em;font-weight:bold;color:var(--muted)}h1{font:normal clamp(36px,5vw,64px)/1.1 Georgia,serif;margin:18px 0}h2,h3,p{margin:0 0 14px}h3{font-size:20px}.context,small{color:var(--muted);font-size:13px}small{display:block}.metrics{display:grid;grid-template-columns:repeat(3,1fr);gap:20px;margin:30px 0}.metric{padding:24px;background:white;border-top:3px solid var(--ink)}.metric h2{text-transform:uppercase;letter-spacing:.08em;font-size:12px;color:var(--muted)}.metric strong{display:block;font-size:36px;font-weight:500;font-variant-numeric:tabular-nums}.delta{display:block;font-size:20px;font-weight:bold;margin:8px 0}.negative{color:var(--red)}.positive{color:var(--teal)}.story{padding:16px 0 26px}.story h2{font:normal 32px/1.2 Georgia,serif}.panels{display:grid;grid-template-columns:1fr 1fr;gap:24px}.panel{background:white;padding:26px}.driver{margin-top:25px}.driver-label{display:flex;justify-content:space-between;gap:12px;font-size:14px}.track{position:relative;height:12px;margin:10px 0 6px;background:#f4f3ef}.track i{position:absolute;left:50%;height:100%;border-left:1px solid #aab3b1}.track span{position:absolute;height:100%;background:var(--teal)}.track span.negative{background:var(--red)}.section{margin-top:38px;border-top:1px solid var(--line);padding-top:24px}.bridge{display:grid;grid-template-columns:repeat(3,1fr);gap:24px;margin:22px 0}.bridge strong{display:block;font-size:27px;font-weight:500;font-variant-numeric:tabular-nums}table{width:100%;border-collapse:collapse;font-size:14px}th{text-align:left;font-size:11px;text-transform:uppercase;letter-spacing:.06em;color:var(--muted)}td,th{padding:17px 12px;border-bottom:1px solid var(--line);vertical-align:top}td:first-child{padding-left:0}.num{white-space:nowrap;text-align:right;font-variant-numeric:tabular-nums}.products{margin-top:7px;overflow-wrap:anywhere}a{color:var(--teal)}.button{display:inline-block;border:1px solid var(--teal);padding:9px 15px;margin:10px 0;text-decoration:none}.scroll{overflow-x:auto}footer{margin-top:36px;border-top:1px solid var(--line);padding-top:22px;font-size:12px;color:var(--muted)}@media(max-width:720px){main{padding:28px 18px}.metrics,.panels{grid-template-columns:1fr}.bridge{grid-template-columns:1fr}.metric strong{font-size:32px}}@media print{body{background:white}main{padding:0;max-width:none}.metrics,.panels{gap:12px}.metric,.panel{padding:14px}.story h2{font-size:24px}.metric strong{font-size:26px}.section{margin-top:20px}.button{display:none}tr,.metric,.driver{break-inside:avoid}}
    """
    body = f"""<header><div class="eyebrow">FIELDNOTES / SALES</div><h1>The monthly sales review</h1><p class="context">{e(s['current_start'])} to {e(s['current_end'])} / vs {e(s['prior_start'])} to {e(s['prior_end'])}</p><p class="context">Historical Superstore sample. Sales use source monetary units; currency is unspecified.</p></header>
    <div class="metrics">{cards}</div><section class="story"><h2>{e(review['headline'])}</h2><p>{e(review['interpretation'])}</p></section><div class="panels">{''.join(panels)}</div>
    <section class="section"><div class="eyebrow">01 / HOW THE TOTAL CHANGED</div><div class="bridge">{bridge}</div><p class="context">Volume effect = change in orders × prior average order. Average-order effect = current orders × change in average order. These sum to the sales change when both averages are defined; this arithmetic does not establish cause.</p></section>
    <section class="section"><div class="eyebrow">02 / REVIEW FIRST</div><h3>Trace the change to source product IDs</h3><div class="scroll"><table><thead><tr><th>Rank</th><th>Segment</th><th class="num">Sales change</th><th>Review lead / product IDs</th></tr></thead><tbody>{actions}</tbody></table></div><a class="button" href="review_actions.csv" download>Download follow-up CSV</a><p class="context">Compare the listed IDs with prior-period orders. Verify product mix and source coverage before deciding on a response. Category and region views overlap; do not add their declines.</p></section>
    <footer>Periods share a day-of-month cutoff; equal cutoffs do not prove equal coverage or a certified accounting close. Missing prior-year delivery means unavailable; a delivered empty file means zero.<br>Source: <a href="https://www.kaggle.com/datasets/rohitsahoo/sales-forecasting">Rohit Sahoo / Superstore Sales Dataset</a>, Kaggle data card GPL 2. Independent portfolio demonstration. No margin, stock or causal conclusion is inferred.</footer>"""
    Path(output).write_text(
        f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Sales review {e(s["month"])}</title><style>{style}</style></head><body><main>{body}</main></body></html>',
        encoding="utf-8",
    )
