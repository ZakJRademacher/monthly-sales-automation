"""Build a self-contained motion-enabled view of the verified historical brief."""
import csv
from decimal import Decimal
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def build():
    source=ROOT/'tableau/Data/analysis.csv'
    review=json.loads((ROOT/'evidence/business-review.json').read_text(encoding='utf-8'))
    with source.open(encoding='utf-8-sig',newline='') as f:rows=list(csv.DictReader(f))
    assert len(rows)==67
    summary=review['summary']
    assert summary['current']['sales_units']==830303888 and summary['current']['orders']==223
    trend=[]
    for day in range(1,31):
        values={r['Series']:int(Decimal(r['Value'])*10000) for r in rows if r['View']=='trend' and int(r['Sort'])==day}
        assert set(values)=={'Current','Prior'}
        trend.append({'day':day,'current':values['Current'],'prior':values['Prior']})
    assert trend[-1]['current']==summary['current']['sales_units']
    assert trend[-1]['prior']==summary['prior']['sales_units']
    for scope in ['category','region']:
        expected={r['Label']:int(Decimal(r['Value'])*10000) for r in rows if r['View']==scope}
        observed={r['member']:r['change_units'] for r in review['drivers'][scope]}
        assert expected==observed
        assert sum(observed.values())==summary['sales_change_units']
    payload={'summary':summary,'drivers':review['drivers'],'trend':trend,'source_csv_sha256':hashlib.sha256(source.read_bytes()).hexdigest()}
    template=(ROOT/'web/report.html').read_text(encoding='utf-8')
    styles=(ROOT/'web/report.css').read_text(encoding='utf-8')+'\n'+(ROOT/'web/studio.css').read_text(encoding='utf-8')
    page=template.replace('/* REPORT_CSS */',styles).replace('/* REPORT_JS */',(ROOT/'web/report.js').read_text(encoding='utf-8'))
    page=page.replace('REPORT_DATA_JSON',json.dumps(payload,separators=(',',':')).replace('<','\\u003c'))
    output=ROOT/'deliverables/Monthly Sales Interactive.html';output.write_text(page,encoding='utf-8')
    return {'output':str(output),'source_csv_sha256':payload['source_csv_sha256'],'source_records':len(rows),'current_sales_units':summary['current']['sales_units'],'orders':summary['current']['orders'],'trend_points':len(trend),'all_driver_values_and_totals_reconciled':True}


if __name__=='__main__':print(json.dumps(build(),indent=2))
