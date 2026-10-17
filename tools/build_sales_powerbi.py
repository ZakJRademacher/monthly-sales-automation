"""Build the native interactive Power BI sales explorer from validated local CSV snapshots."""

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PBI = ROOT / "powerbi"
REPORT = PBI / "SalesExplorer.Report"
MODEL = PBI / "SalesExplorer.SemanticModel"
BASE = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/"
BG, PANEL, INK, MUTED = "#0B1420", "#121F2D", "#EFF4F7", "#A4B5C4"
MINT, CORAL, LILAC = "#64D8C5", "#FF927F", "#B6A5F5"


def put(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def lit(value):
    value = (
        str(value).lower()
        if isinstance(value, bool)
        else (
            str(value) + "D"
            if isinstance(value, (int, float))
            else "'" + value.replace("'", "''") + "'"
        )
    )
    return {"expr": {"Literal": {"Value": value}}}


def color(value):
    return {"solid": {"color": lit(value)}}


def field(table, column, measure=False):
    return {
        "field": {
            "Measure" if measure else "Column": {
                "Expression": {"SourceRef": {"Entity": table}},
                "Property": column,
            }
        },
        "queryRef": table + "." + column,
        "nativeQueryRef": column,
    }


def measures():
    source = (PBI / "measures.dax").read_text(encoding="utf-8")
    source = re.sub(r"^//.*$", "", source, flags=re.M)
    entries = re.split(r"^([A-Za-z][^=\n]*?)\s*=\s*", source, flags=re.M)
    result = {}
    for i in range(1, len(entries), 2):
        name, expression = entries[i].strip(), entries[i + 1].strip()
        if not expression:
            continue
        result[name] = expression
    result.update(
        {
            "Headline": """IF(NOT [Prior Delivery Available], "Prior-year delivery missing", IF(ISBLANK([Sales Change %]), "Prior sales baseline is zero", FORMAT(ABS([Sales Change %]), "0.0%") & IF([Sales Change] < 0, " less sales", IF([Sales Change] > 0," more sales"," change in sales")) & " | " & FORMAT([Matched Orders], "#,0") & " orders in the selected view"))""",
            "Filter Context": """"Region: " & IF(ISFILTERED('Sales'[Region]), CONCATENATEX(VALUES('Sales'[Region]), 'Sales'[Region], ", "), "All") & "   /   Category: " & IF(ISFILTERED('Sales'[Category]), CONCATENATEX(VALUES('Sales'[Category]), 'Sales'[Category], ", "), "All")""",
            "Window Sales": """VAR AxisDate = MAX('Dates'[Date]) VAR AxisMonth = DATE(YEAR(AxisDate), MONTH(AxisDate), 1) VAR Anchor = [Report Month] VAR Available = COUNTROWS(FILTER(ALL('DeliveryCoverage'), 'DeliveryCoverage'[Month] = AxisMonth && 'DeliveryCoverage'[Coverage] = "Imported")) > 0 RETURN IF(AxisMonth >= EDATE(Anchor,-11) && AxisMonth <= Anchor && Available, [Sales])""",
            "Order Volume Effect": """IF([Prior Delivery Available] && [Prior Matched Orders] > 0, ([Matched Orders]-[Prior Matched Orders])*[Prior Matched AOV])""",
            "Average Order Effect": """IF([Prior Delivery Available] && [Prior Matched Orders] > 0 && [Matched Orders] > 0, [Matched Orders]*([Matched AOV]-[Prior Matched AOV]))""",
            "Product Review Change": """IF([Prior Delivery Available] && ( [Matched Sales] <> 0 || [Prior Matched Sales] <> 0), [Sales Change])""",
            "Current sales": """IF([Matched Sales] <> 0 || [Prior Matched Sales] <> 0, [Matched Sales])""",
            "Prior sales": """IF([Matched Sales] <> 0 || [Prior Matched Sales] <> 0, [Prior Matched Sales])""",
        }
    )
    output = []
    for name, expression in result.items():
        fmt = (
            "0.0%"
            if name.endswith("%")
            else (
                "#,0"
                if name in {"Orders", "Matched Orders", "Prior Matched Orders"}
                else (
                    "yyyy-MM-dd"
                    if name in {"Report Month", "As Of Date", "Cutoff Date"}
                    else "#,0.00"
                )
            )
        )
        output.append(
            {
                "name": name,
                "expression": expression,
                "formatString": fmt,
                "description": "Interactive calculation. See powerbi/README.md for period and filter semantics.",
            }
        )
    return output


def model():
    tables = []
    types = {"OrderDate", "ShipDate", "Date", "Month"}
    integers = {"SalesUnits", "SourceRow", "Year", "MonthNumber", "Value"}
    pointer = json.loads((PBI / "sample-data/latest.json").read_text())
    queries = {}
    for name in ["Sales", "Dates", "DeliveryCoverage", "Quality"]:
        with (
            PBI / "sample-data/snapshots" / pointer["snapshot"] / (name + ".csv")
        ).open(encoding="utf-8-sig", newline="") as f:
            headers = next(csv.reader(f))
        columns = []
        conversions = []
        for header in headers:
            dtype = (
                "dateTime"
                if header in types
                else "int64" if header in integers else "string"
            )
            col = {
                "name": header,
                "sourceColumn": header,
                "dataType": dtype,
                "summarizeBy": "none",
            }
            if dtype == "dateTime":
                col.update(
                    formatString="yyyy-MM-dd",
                    annotations=[
                        {"name": "UnderlyingDateTimeDataType", "value": "Date"}
                    ],
                )
            if header in {"SalesUnits", "SourceRow"}:
                col["isHidden"] = True
            if header == "MonthLabel":
                col["sortByColumn"] = "MonthNumber"
            columns.append(col)
            conversions.append(
                '{"'
                + header
                + '", '
                + (
                    "type date"
                    if dtype == "dateTime"
                    else "Int64.Type" if dtype == "int64" else "type text"
                )
                + "}"
            )
        query = [
            "let",
            '    Pointer = Json.Document(File.Contents(DataFolder & "/latest.json")),',
            '    Snapshot = if Pointer[contract_version] = 1 then Pointer[snapshot] else error "Unsupported data contract",',
            f'    Source = Csv.Document(File.Contents(DataFolder & "/snapshots/" & Snapshot & "/{name}.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),',
            "    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),",
            "    Typed = Table.TransformColumnTypes(Headers, {"
            + ", ".join(conversions)
            + '}, "en-US")',
            "in",
            "    Typed",
        ]
        queries[name] = "\n".join(query)
        (PBI / "queries" / (name + ".pq")).write_text(queries[name] + "\n", encoding="utf-8")
        t = {
            "name": name,
            "columns": columns,
            "partitions": [
                {
                    "name": name,
                    "mode": "import",
                    "source": {"type": "m", "expression": query},
                }
            ],
        }
        if name == "Sales":
            t["measures"] = measures()
        tables.append(t)
    put(MODEL / "definition.pbism", {"version": "1.0"})
    put(
        MODEL / "model.bim",
        {
            "name": "SalesExplorer",
            "compatibilityLevel": 1600,
            "model": {
                "culture": "en-US",
                "defaultPowerBIDataSourceVersion": "powerBI_V3",
                "expressions": [
                    {
                        "name": "DataFolder",
                        "kind": "m",
                        "expression": '"'
                        + (PBI / "sample-data").as_posix()
                        + '" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]',
                    }
                ],
                "tables": tables,
                "relationships": [
                    {
                        "name": "Sales_Dates",
                        "fromTable": "Sales",
                        "fromColumn": "OrderDate",
                        "toTable": "Dates",
                        "toColumn": "Date",
                        "crossFilteringBehavior": "oneDirection",
                    }
                ],
                "annotations": [
                    {
                        "name": "PBI_QueryOrder",
                        "value": json.dumps(["DataFolder"] + list(queries)),
                    }
                ],
            },
        },
    )
    (PBI / "native-measures.dax").write_text(
        "\n\n".join(x["name"] + " =\n" + x["expression"] for x in measures()) + "\n",
        encoding="utf-8",
    )


def visual(
    page,
    name,
    kind,
    x,
    y,
    w,
    h,
    title=None,
    roles=None,
    objects=None,
    sort=None,
    background=PANEL,
):
    v = {"visualType": kind, "drillFilterOtherVisuals": True}
    if roles:
        v["query"] = {
            "queryState": {
                role: {"projections": [field(*p) for p in fields]}
                for role, fields in roles.items()
            }
        }
        if sort:
            v["query"]["sortDefinition"] = {
                "sort": [{"field": field(*sort[:3])["field"], "direction": sort[3]}],
                "isDefaultSort": False,
            }
    v["visualContainerObjects"] = {
        "background": [
            {
                "properties": {
                    "show": lit(True),
                    "color": color(background),
                    "transparency": lit(0),
                }
            }
        ],
        "border": [{"properties": {"show": lit(False)}}],
        "title": [
            {
                "properties": {
                    "show": lit(bool(title)),
                    "text": lit(title or ""),
                    "fontColor": color(INK),
                    "fontSize": lit(13),
                    "fontFamily": lit("Segoe UI Semibold"),
                }
            }
        ],
    }
    if objects:
        v["objects"] = objects
    put(
        REPORT / f"definition/pages/{page}/visuals/{name}/visual.json",
        {
            "$schema": BASE + "visualContainer/2.0.0/schema.json",
            "name": name,
            "position": {
                "x": x,
                "y": y,
                "width": w,
                "height": h,
                "z": 0,
                "tabOrder": y * 10 + x,
            },
            "visual": v,
        },
    )


def text(page, name, value, x, y, w, h, size=12, ink=MUTED, font="Segoe UI"):
    h = max(h, 34)
    visual(
        page,
        name,
        "textbox",
        x,
        y,
        w,
        h,
        objects={
            "general": [
                {
                    "properties": {
                        "paragraphs": [
                            {
                                "textRuns": [
                                    {
                                        "value": value,
                                        "textStyle": {
                                            "fontFamily": font,
                                            "fontSize": str(size) + "pt",
                                            "color": ink,
                                        },
                                    }
                                ]
                            }
                        ]
                    }
                }
            ]
        },
        background=BG,
    )


def card(page, name, metric, x, y, w, h, size=28, ink=INK, title=None):
    visual(
        page,
        name,
        "card",
        x,
        y,
        w,
        h,
        title,
        {"Values": [("Sales", metric, True)]},
        {
            "labels": [
                {
                    "properties": {
                        "color": color(ink),
                        "fontSize": lit(size),
                        "labelDisplayUnits": lit(1),
                        "precision": lit(
                            0
                            if "Orders" in metric and "%" not in metric
                            else 1 if "%" in metric else 2
                        ),
                    }
                }
            ],
            "categoryLabels": [{"properties": {"show": lit(False)}}],
        },
        background=BG,
    )


def slicer(page, name, table, col, x, w, single=False):
    visual(
        page,
        name,
        "slicer",
        x,
        106,
        w,
        64,
        title=col + (" | latest if clear" if single else " | all by default"),
        roles={"Values": [(table, col)]},
        objects={
            "data": [{"properties": {"mode": lit("Dropdown")}}],
            "header": [{"properties": {"show": lit(False)}}],
            "items": [
                {
                    "properties": {
                        "fontColor": color(INK),
                        "background": color(PANEL),
                        "textSize": lit(11),
                    }
                }
            ],
            "selection": [
                {
                    "properties": {
                        "singleSelect": lit(single),
                        "selectAllCheckboxEnabled": lit(not single),
                    }
                }
            ],
        },
    )
    p = REPORT / f"definition/pages/{page}/visuals/{name}/visual.json"
    j = json.loads(p.read_text())
    j["visual"]["syncGroup"] = {
        "groupName": name,
        "fieldChanges": True,
        "filterChanges": True,
    }
    put(p, j)


def charts():
    return {
        "categoryAxis": [
            {
                "properties": {
                    "labelColor": color(MUTED),
                    "fontSize": lit(10),
                    "showAxisTitle": lit(False),
                }
            }
        ],
        "valueAxis": [
            {
                "properties": {
                    "labelColor": color(MUTED),
                    "fontSize": lit(10),
                    "showAxisTitle": lit(False),
                    "gridlineColor": color("#263747"),
                }
            }
        ],
        "legend": [
            {
                "properties": {
                    "show": lit(True),
                    "labelColor": color(INK),
                    "fontSize": lit(11),
                    "position": lit("Top"),
                }
            }
        ],
        "labels": [{"properties": {"show": lit(False)}}],
    }


def report():
    put(
        PBI / "SalesExplorer.pbip",
        {"version": "1.0", "artifacts": [{"report": {"path": "SalesExplorer.Report"}}]},
    )
    put(
        REPORT / "definition.pbir",
        {
            "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definitionProperties/2.0.0/schema.json",
            "version": "4.0",
            "datasetReference": {"byPath": {"path": "../SalesExplorer.SemanticModel"}},
        },
    )
    put(
        REPORT / "definition/version.json",
        {"$schema": BASE + "versionMetadata/1.0.0/schema.json", "version": "2.0.0"},
    )
    put(
        REPORT / "StaticResources/RegisteredResources/SalesTheme.json",
        {
            "name": "The shape of sales",
            "dataColors": [MINT, CORAL, LILAC, "#EACB79"],
            "background": PANEL,
            "foreground": INK,
            "tableAccent": MINT,
            "textClasses": {
                "title": {
                    "fontFace": "Segoe UI Semibold",
                    "fontSize": 13,
                    "color": INK,
                },
                "label": {"fontFace": "Segoe UI", "fontSize": 11, "color": MUTED},
                "callout": {"fontFace": "Segoe UI", "color": INK},
            },
        },
    )
    revision = {"visual": "1.8.101", "report": "2.0.101", "page": "1.3.101"}
    put(
        REPORT / "definition/report.json",
        {
            "$schema": BASE + "report/3.0.0/schema.json",
            "themeCollection": {
                "baseTheme": {
                    "name": "CY24SU02",
                    "reportVersionAtImport": {
                        "visual": "1.8.89",
                        "report": "2.0.89",
                        "page": "1.3.89",
                    },
                    "type": "SharedResources",
                },
                "customTheme": {
                    "name": "SalesTheme.json",
                    "reportVersionAtImport": revision,
                    "type": "RegisteredResources",
                },
            },
            "resourcePackages": [
                {
                    "name": "SharedResources",
                    "type": "SharedResources",
                    "items": [
                        {
                            "name": "CY24SU02",
                            "path": "BaseThemes/CY24SU02.json",
                            "type": "BaseTheme",
                        }
                    ],
                },
                {
                    "name": "RegisteredResources",
                    "type": "RegisteredResources",
                    "items": [
                        {
                            "name": "SalesTheme.json",
                            "path": "SalesTheme.json",
                            "type": "CustomTheme",
                        }
                    ],
                },
            ],
        },
    )
    pages = {
        "shape": (
            "01  The shape of sales",
            "The shape of sales",
            "Explore the mix. Compare like-for-like periods. Follow the changes.",
        ),
        "drivers": (
            "02  Where momentum changes",
            "Where momentum changes",
            "Click a category or region to filter the comparisons. Clear the selection to return.",
        ),
        "products": (
            "03  Follow the signal",
            "Follow the signal",
            "Choose a product ID to inspect its sales and the original source order lines.",
        ),
        "quality": (
            "04  Data & refresh",
            "Behind the numbers",
            "A repeatable local workflow, with visible coverage and source lineage.",
        ),
    }
    put(
        REPORT / "definition/pages/pages.json",
        {
            "$schema": BASE + "pagesMetadata/1.0.0/schema.json",
            "pageOrder": list(pages),
            "activePageName": "shape",
        },
    )
    for page, (display, title, subtitle) in pages.items():
        put(
            REPORT / f"definition/pages/{page}/page.json",
            {
                "$schema": BASE + "page/2.0.0/schema.json",
                "name": page,
                "displayName": display,
                "displayOption": "FitToPage",
                "height": 900,
                "width": 1280,
                "objects": {
                    "background": [
                        {"properties": {"color": color(BG), "transparency": lit(0)}}
                    ]
                },
            },
        )
        text(
            page,
            "brand",
            "FIELDNOTES / INTERACTIVE SALES EXPLORER",
            32,
            0,
            1216,
            22,
            9,
            MINT,
        )
        text(page, "title", title, 32, 28, 1216, 58, 32, INK, "Georgia")
        text(page, "subtitle", subtitle, 32, 80, 1216, 27, 11)
        text(
            page,
            "footer",
            "KAGGLE SUPERSTORE / 2015–2018 HISTORICAL SAMPLE / SOURCE MONETARY UNITS, CURRENCY UNSPECIFIED",
            32,
            865,
            1216,
            25,
            9,
        )
        if page != "quality":
            slicer(page, "reportMonth", "DeliveryCoverage", "Month", 32, 334, True)
            slicer(page, "category", "Sales", "Category", 386, 420)
            slicer(page, "region", "Sales", "Region", 826, 422)
            card(page, "period", "Period Caption", 32, 177, 1216, 32, 10, MUTED)
    for i, (metric, delta, title) in enumerate(
        [
            ("Matched Sales", "Sales Change %", "Sales"),
            ("Matched Orders", "Orders Change %", "Orders"),
            ("Matched AOV", "AOV Change %", "Average order"),
        ]
    ):
        x = 32 + i * 414
        card("shape", "kpi" + str(i), metric, x, 225, 386, 91, 31, INK, title)
        card(
            "shape",
            "change" + str(i),
            delta,
            x,
            317,
            386,
            53,
            17,
            INK,
            "vs same period last year",
        )
    card("shape", "headline", "Headline", 32, 377, 1216, 56, 21, INK)
    visual(
        "shape",
        "ribbon",
        "ribbonChart",
        32,
        451,
        1216,
        355,
        "How the category mix moves | trailing 12 observed months",
        {
            "Category": [("Dates", "YearMonth")],
            "Series": [("Sales", "Category")],
            "Y": [("Sales", "Window Sales", True)],
            "Tooltips": [
                ("Sales", "Sales", True),
                ("Sales", "Orders", True),
                ("Sales", "AOV", True),
            ],
        },
        charts(),
        sort=("Dates", "YearMonth", False, "Ascending"),
    )
    text(
        "shape",
        "ribbonHelp",
        "Hover a ribbon for amounts and rank changes. Click a category ribbon to focus the view. The report-month selector anchors the KPI comparison; the ribbon shows full observed months.",
        32,
        816,
        1216,
        45,
        11,
    )
    card("drivers", "headline", "Headline", 32, 221, 1216, 55, 22, INK)
    for scope, x, w in [("Category", 32, 592), ("Region", 648, 600)]:
        bar_style = charts()
        bar_style["labels"] = [{"properties": {"show": lit(True), "color": color(INK), "labelDisplayUnits": lit(1), "labelPrecision": lit(2), "fontSize": lit(10)}}]
        visual(
            "drivers",
            scope.lower() + "Chart",
            "clusteredBarChart",
            x,
            298,
            w,
            322,
            scope + " | change in sales",
            {
                "Category": [("Sales", scope)],
                "Y": [("Sales", "Sales Change", True)],
                "Tooltips": [
                    ("Sales", "Matched Sales", True),
                    ("Sales", "Prior Matched Sales", True),
                    ("Sales", "Sales Change %", True),
                ],
            },
            bar_style,
            sort=("Sales", "Sales Change", True, "Ascending"),
        )
    for i, (metric, title) in enumerate(
        [
            ("Order Volume Effect", "Change in order count, at prior order value"),
            ("Average Order Effect", "Change in order value, at current order count"),
            ("Sales Change", "Net change in sales"),
        ]
    ):
        card(
            "drivers",
            "effect" + str(i),
            metric,
            32 + i * 414,
            655,
            386,
            105,
            24,
            INK,
            title,
        )
    text(
        "drivers",
        "bridgeHelp",
        "The arithmetic bridge reconciles the sales change; it does not establish cause. Region and category are overlapping views of the same sales and must not be added together.",
        32,
        786,
        1216,
        65,
        12,
    )
    visual(
        "products",
        "product",
        "slicer",
        32,
        220,
        1216,
        62,
        "Product ID | select to inspect, clear for all",
        {"Values": [("Sales", "ProductID")]},
        {
            "data": [{"properties": {"mode": lit("Dropdown")}}],
            "header": [{"properties": {"show": lit(False)}}],
            "items": [
                {"properties": {"fontColor": color(INK), "background": color(PANEL)}}
            ],
            "selection": [{"properties": {"singleSelect": lit(True)}}],
        },
    )
    visual(
        "products",
        "productReview",
        "tableEx",
        32,
        302,
        720,
        490,
        "Products | largest declines first, scroll for all",
        {
            "Values": [
                ("Sales", "ProductID"),
                ("Sales", "Current sales", True),
                ("Sales", "Prior sales", True),
                ("Sales", "Product Review Change", True),
                ("Sales", "Sales Change %", True),
            ]
        },
        sort=("Sales", "Product Review Change", True, "Ascending"),
    )
    visual(
        "products",
        "productHistory",
        "lineChart",
        776,
        302,
        472,
        260,
        "Product sales | trailing 12 months",
        {"Category": [("Dates", "YearMonth")], "Y": [("Sales", "Window Sales", True)]},
        charts(),
        sort=("Dates", "YearMonth", False, "Ascending"),
    )
    visual(
        "products",
        "sourceLines",
        "tableEx",
        776,
        585,
        472,
        207,
        "Source lineage | selected product, all dates",
        {
            "Values": [
                ("Sales", "OrderID"),
                ("Sales", "OrderDate"),
                ("Sales", "SourceFile"),
                ("Sales", "SourceRow"),
            ]
        },
        sort=("Sales", "OrderDate", False, "Descending"),
    )
    text(
        "products",
        "reviewHelp",
        "Select a product row to filter its history and source lines. Source detail spans all dates; the matched comparison is shown in the product table. Products use original source IDs.",
        32,
        809,
        1216,
        56,
        11,
    )
    visual(
        "quality",
        "quality",
        "tableEx",
        32,
        132,
        420,
        288,
        "Full-snapshot validation counts",
        {"Values": [("Quality", "Metric"), ("Quality", "Value")]},
    )
    visual(
        "quality",
        "coverage",
        "tableEx",
        480,
        132,
        344,
        540,
        "Monthly delivery coverage",
        {"Values": [("DeliveryCoverage", "Month"), ("DeliveryCoverage", "Coverage")]},
        sort=("DeliveryCoverage", "Month", False, "Descending"),
    )
    text(
        "quality",
        "refresh",
        "REFRESH THE REPORT\n\n1. Add or replace monthly CSVs. Retain history.\n2. Run python powerbi/export_data.py.\n3. Select Home > Refresh in Power BI.\n\nSet DataFolder to your local powerbi/sample-data folder. A validated export publishes an immutable snapshot and replaces latest.json only after all tables are written. Do not export during a Desktop refresh.",
        852,
        135,
        396,
        350,
        13,
        INK,
    )
    text(
        "quality",
        "basis",
        "MATCH THE COMPARISON\n\nOne report month, common day-of-month cutoff, with region/category filters retained. The cutoff uses the global source date and does not move when filtering products. Missing prior delivery stays unavailable; an explicitly empty file is zero. Full-month ribbon values use a different time basis.",
        32,
        461,
        420,
        295,
        13,
    )
    text(
        "quality",
        "limits",
        "SOURCE & LIMITS\n\nHistorical Kaggle Superstore sample, uploader rohitsahoo/sales-forecasting, data card GPL 2. Independent portfolio project. Sales are not profit or cash receipts. No live feed or unattended schedule is configured. Zero duplicate rows in this snapshot is an observed result, not a claimed cleanup saving.",
        852,
        505,
        396,
        270,
        12,
    )
    # Explicit data-filter interactions, rather than faint cross-highlights.
    for page, sources, targets in [
        (
            "drivers",
            ["categoryChart", "regionChart"],
            [
                "headline",
                "categoryChart",
                "regionChart",
                "effect0",
                "effect1",
                "effect2",
            ],
        ),
        ("products", ["productReview"], ["productHistory", "sourceLines"]),
    ]:
        path = REPORT / f"definition/pages/{page}/page.json"
        j = json.loads(path.read_text())
        j["visualInteractions"] = [
            {"source": s, "target": t, "type": "DataFilter"}
            for s in sources
            for t in targets
            if s != t
        ]
        put(path, j)


if __name__ == "__main__":
    model()
    report()
    print(PBI / "SalesExplorer.pbip")
