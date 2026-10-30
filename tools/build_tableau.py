"""Build two local, data-bound Tableau analysis workbooks from verified project results."""
from pathlib import Path
import calendar
import csv
import hashlib
import json
import sqlite3
import uuid
import zipfile
import xml.etree.ElementTree as E
import textwrap
from datetime import date

PROJECT = Path(__file__).resolve().parents[1]
INK, MUTED, TEAL, CORAL, GOLD, PAPER = '#203B43', '#60757B', '#147D80', '#BE5D50', '#BA852D', '#F6F5F0'
FIELDS = [('View','string'),('Label','string'),('Series','string'),('Value','real'),('Sort','integer'),('Note','string')]

def node(parent, tag, text=None, **attrs):
    item = E.SubElement(parent, tag, {k.replace('_','-'):str(v) for k,v in attrs.items()})
    if text is not None: item.text = str(text)
    return item

def fmt(parent, element, **values):
    rule=node(parent,'style-rule',element=element)
    for attr,value in values.items(): node(rule,'format',attr=attr.replace('_','-'),value=value)
    return rule

def tableau(folder, filename, rows, title, subtitle, kpis, charts, takeaway, source):
    folder.mkdir(parents=True,exist_ok=True)
    data=folder/'Data/analysis.csv';data.parent.mkdir(exist_ok=True)
    with data.open('w',encoding='utf-8-sig',newline='') as stream:
        writer=csv.writer(stream);writer.writerow([f for f,t in FIELDS]);writer.writerows(rows)
    book=E.Element('workbook',{'locale':'en_US','source-platform':'win','source-build':'2026.3.0 (20263.26.1022.1645)','version':'18.1','xmlns:user':'http://www.tableausoftware.com/xml/user'})
    node(book,'document-format-change-manifest')
    prefs=node(book,'preferences');node(prefs,'preference',name='ui.encoding.shelf.height',value='24')
    node(book,'style-theme',name='smooth')
    style=node(book,'style');fmt(style,'worksheet',font_family='Segoe UI',font_size='11',color=INK);fmt(style,'dashboard',background_color=PAPER)
    ds=node(node(book,'datasources'),'datasource',caption=title,inline='true',name='analysis',version='18.1')
    connection=node(ds,'connection',**{'class':'federated'})
    named=node(node(connection,'named-connections'),'named-connection',name='csv')
    node(named,'connection',**{'class':'textscan','directory':data.parent.as_posix(),'filename':data.name,'character-set':'UTF-8','header':'yes','separator':',','text-qualifier':'"','force-header':'yes','force-separator':'yes'})
    relation=node(connection,'relation',connection='csv',name='analysis.csv',table='[analysis.csv]',type='table')
    columns=node(relation,'columns',header='yes',locale='en_US',separator=',',character_set='UTF-8',text_qualifier='"')
    for i,(name,typ) in enumerate(FIELDS): node(columns,'column',name=name,datatype=typ,ordinal=i)
    metadata=node(connection,'metadata-records')
    for i,(name,typ) in enumerate(FIELDS):
        rec=node(metadata,'metadata-record',**{'class':'column'})
        for tag,value in [('remote-name',name),('remote-type',129 if typ=='string' else 5 if typ=='real' else 20),('local-name',f'[{name}]'),('parent-name','[analysis.csv]'),('remote-alias',name),('ordinal',i),('local-type',typ),('aggregation','Count' if typ=='string' else 'Sum'),('contains-null','false')]:node(rec,tag,value)
    for name,typ in FIELDS:
        col=node(ds,'column',name=f'[{name}]',datatype=typ,role='dimension' if typ=='string' else 'measure',type='nominal' if typ=='string' else 'quantitative')
        if name=='Value':col.set('default-format','n#,##0.00')
    # Use the same semantic colors in all sheets and in the visible legends.
    palette=node(node(node(ds,'style'),'style-rule',element='mark'),'encoding',attr='color',field='[none:Series:nk]',type='palette')
    for name,ink in [('Current',TEAL),('Prior','#8FA4A5'),('Decline',CORAL),('Increase',TEAL),('Observed month',TEAL),('Partial final month',GOLD),('Lower reported net',CORAL),('Higher reported net',GOLD),('Gross positive sales',TEAL)]:node(node(palette,'map',to=ink),'bucket',json.dumps(name))
    worksheets=node(book,'worksheets')
    for name,view,label,mark,x,y,w,h in charts:
        sheet=node(worksheets,'worksheet',name=name)
        titletext=node(node(node(sheet,'layout-options'),'title'),'formatted-text');node(titletext,'run',label,fontname='Segoe UI',fontsize='14',bold='true',fontcolor=INK)
        table=node(sheet,'table');v=node(table,'view');node(node(v,'datasources'),'datasource',name='analysis',caption=title)
        deps=node(v,'datasource-dependencies',datasource='analysis')
        for f,t in FIELDS:
            node(deps,'column',name=f'[{f}]',datatype=t,role='dimension' if t=='string' else 'measure',type='nominal' if t=='string' else 'quantitative')
            node(deps,'column-instance',column=f'[{f}]',derivation='Attribute' if f=='Note' else 'None' if t=='string' else 'Sum',name='[attr:Note:nk]' if f=='Note' else f'[none:{f}:nk]' if t=='string' else f'[sum:{f}:qk]',pivot='key',type='nominal' if t=='string' else 'quantitative')
        flt=node(v,'filter',column='[analysis].[none:View:nk]',**{'class':'categorical'})
        node(flt,'groupfilter',function='member',level='[none:View:nk]',member=json.dumps(view))
        if mark=='Bar':node(v,'sort',column='[analysis].[none:Label:nk]',using='[analysis].[sum:Value:qk]',direction='ASC',**{'class':'computed'})
        node(node(v,'slices'),'column','[analysis].[none:View:nk]');node(v,'aggregation',value='true')
        styling=node(table,'style');fmt(styling,'worksheet',background_color='#FFFFFF');fmt(styling,'cell',font_family='Segoe UI',font_size='11',color=INK)
        fmt(styling,'label',font_family='Segoe UI',font_size='10',color=MUTED)
        labels=fmt(styling,'worksheet')
        for scope in ['rows','cols']:node(labels,'format',attr='display-field-labels',scope=scope,value='false')
        axis=fmt(styling,'axis',font_family='Segoe UI',font_size='10',color=MUTED)
        node(axis,'format',attr='title',scope='cols' if mark=='Bar' else 'rows',value='GBP' if filename.startswith('Retail') else 'Recorded sales · source units')
        fmt(styling,'gridline',stroke_color='#E5E9E7',stroke_size='1');fmt(styling,'zeroline',stroke_color='#CCD5D3',stroke_size='1')
        pane=node(node(table,'panes'),'pane');node(node(pane,'view'),'breakdown',value='auto');node(pane,'mark',**{'class':'Bar' if mark=='BarTime' else mark})
        enc=node(pane,'encodings');node(enc,'color',column='[analysis].[none:Series:nk]');node(enc,'tooltip',column='[analysis].[attr:Note:nk]')
        if mark=='Bar':node(enc,'text',column='[analysis].[sum:Value:qk]')
        tooltip=node(node(pane,'customized-tooltip'),'formatted-text');node(tooltip,'run','<[analysis].[none:Label:nk]>\n<[analysis].[sum:Value:qk]>\n<[analysis].[attr:Note:nk]>',fontname='Segoe UI',fontsize='11')
        pst=node(pane,'style');fmt(pst,'mark',mark_labels_show='true' if mark=='Bar' else 'false',mark_labels_cull='true',color=TEAL)
        node(table,'rows','[analysis].[none:Label:nk]' if mark=='Bar' else '[analysis].[sum:Value:qk]')
        node(table,'cols','[analysis].[sum:Value:qk]' if mark=='Bar' else '[analysis].[none:Label:nk]')
    dashboard=node(node(book,'dashboards'),'dashboard',name='01  Decision brief')
    dashboardstyle=node(dashboard,'style');fmt(dashboardstyle,'dashboard',background_color=PAPER)
    textstyle=node(dashboardstyle,'style-rule',element='dash-text')
    node(dashboard,'size',maxheight=950,maxwidth=1400,minheight=950,minwidth=1400)
    node(node(dashboard,'datasources'),'datasource',name='analysis',caption=title)
    zones=node(dashboard,'zones');rootzone=node(zones,'zone',id=1,type='layout-basic',x=0,y=0,w=100000,h=100000)
    z=2
    def text_zone(text,x,y,w,h,size=12,color=INK,bold=False,bg=None):
        nonlocal z
        zone=node(rootzone,'zone',id=z,type='text',x=int(x/1400*100000),y=int(y/950*100000),w=int(w/1400*100000),h=int(h/950*100000));node(textstyle,'format',attr='wrap',id='dash-text_'+str(z),value='on');z+=1
        txt=node(zone,'formatted-text');node(txt,'run','\n'.join(textwrap.wrap(text,width=max(20,int((w-20)/(size*.62))))) if len(text)>150 else text,fontname='Segoe UI',fontsize=size,fontcolor=color,bold=str(bold).lower())
        zs=node(zone,'zone-style');node(zs,'format',attr='padding',value='10')
        if bg:node(zs,'format',attr='background-color',value=bg)
    text_zone('FIELDNOTES / BUSINESS ANALYSIS',24,12,1352,34,10,TEAL,True)
    text_zone(title,24,46,1352,58,28,INK,True)
    text_zone(subtitle,24,107,1352,48,12,MUTED)
    for i,(label,value,context) in enumerate(kpis):
        x=24+i*455
        text_zone(label.upper(),x,168,438,32,10,MUTED,True,'#FFFFFF')
        text_zone(value,x,200,438,62,32,INK,False,'#FFFFFF')
        text_zone(context,x,262,438,42,11,MUTED,False,'#FFFFFF')
    for name,view,label,mark,x,y,w,h in charts:
        node(rootzone,'zone',id=z,name=name,show_title='true',x=int(x/1400*100000),y=int(y/950*100000),w=int(w/1400*100000),h=int(h/950*100000));z+=1
        if mark=='Line':
            node(rootzone,'zone',id=z,type='color',name=name,param='[analysis].[none:Series:nk]',pane_specification_id=0,x=86000,y=38000,w=12000,h=10000);z+=1
    text_zone('WHAT THIS MEANS',24,813,1352,30,10,TEAL,True)
    text_zone(takeaway,24,846,1352,70,12,INK)
    text_zone(source,24,921,1352,29,9,MUTED)
    node(node(rootzone,'zone-style'),'format',attr='background-color',value=PAPER)
    windows=node(book,'windows');dw=node(windows,'window',name='01  Decision brief',**{'class':'dashboard','maximized':'true'})
    points=node(dw,'viewpoints')
    for name,*_ in charts:node(node(points,'viewpoint',name=name),'zoom',type='entire-view')
    node(dw,'active',id=-1)
    for name,*_ in charts:
        sw=node(windows,'window',name=name,**{'class':'worksheet'});cards=node(sw,'cards')
        left=node(node(cards,'edge',name='left'),'strip',size=180)
        for kind in ['pages','filters','marks']:node(left,'card',type=kind)
        top=node(cards,'edge',name='top')
        for kind in ['columns','rows','title']:node(node(top,'strip',size=2147483647),'card',type=kind)
        node(node(sw,'viewpoint'),'zoom',type='entire-view')
    node(book,'thumbnails')
    path=folder/(filename+'.twb');E.indent(book);E.ElementTree(book).write(path,encoding='utf-8',xml_declaration=True)
    manifest={'source':source,'rows':len(rows),'csv_sha256':hashlib.sha256(data.read_bytes()).hexdigest(),'report':filename,'scope':'Historical snapshot analysis; native charts use prepared aggregate records; KPI and interpretation text are regenerated together with data.'}
    (folder/'verification.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    return path

def build(database, output):
    db=sqlite3.connect(f'file:{database.resolve().as_posix()}?mode=ro',uri=True)
    db.row_factory=sqlite3.Row
    counts=db.execute('SELECT COUNT(*),COUNT(DISTINCT order_id),SUM(sales_units) FROM lines').fetchone()
    assert counts[0]==9800 and counts[1]==4922
    a='2018-12-01';b='2018-12-30';pa='2017-12-01';pb='2017-12-30'
    def totals(start,end):return db.execute('SELECT SUM(sales_units),COUNT(DISTINCT order_id) FROM lines WHERE order_date BETWEEN ? AND ?',(start,end)).fetchone()
    cur,prev=totals(a,b),totals(pa,pb);assert cur[0]==830303888 and cur[1]==223
    rows=[]
    for key in ['category','region']:
        segments=db.execute(f'SELECT DISTINCT {key} FROM lines ORDER BY {key}').fetchall()
        for i,(segment,) in enumerate(segments):
            c=db.execute(f'SELECT COALESCE(SUM(sales_units),0) FROM lines WHERE {key}=? AND order_date BETWEEN ? AND ?',(segment,a,b)).fetchone()[0]
            p=db.execute(f'SELECT COALESCE(SUM(sales_units),0) FROM lines WHERE {key}=? AND order_date BETWEEN ? AND ?',(segment,pa,pb)).fetchone()[0]
            delta=(c-p)/10000
            rows.append([key,segment,'Decline' if delta<0 else 'Increase',delta,i,'Current '+f'{c/10000:,.2f}'+'; prior '+f'{p/10000:,.2f}'+'. Category and region views overlap.'])
    assert round(sum(x[3] for x in rows if x[0]=='category'),4)==round((cur[0]-prev[0])/10000,4)
    for year,series in [(2018,'Current'),(2017,'Prior')]:
        cumulative=0
        for day in range(1,31):
            total=db.execute('SELECT COALESCE(SUM(sales_units),0) FROM lines WHERE order_date=?',(f'{year}-12-{day:02}',)).fetchone()[0]
            cumulative+=total
            rows.append(['trend',f'{day:02} Dec',series,cumulative/10000,day,series+' cumulative sales; December 1–30 only.'])
    return tableau(output,'Monthly Sales Review',rows,'Why did sales fall while orders rose?',
        'December 1–30, 2018 vs the same dates in 2017  /  Matched historical periods  /  Hover over marks for detail',
        [('Recorded sales',f'{cur[0]/10000:,.2f}','−12.6% vs matched prior period'),('Distinct orders',f'{cur[1]:,}','+33.5% vs 167 prior orders'),('Sales per order',f'{cur[0]/10000/cur[1]:,.2f}','−34.6%; arithmetic, not a causal explanation')],
        [('Sales accumulation','trend','01  The gap emerges across the month','Line',24,326,1158,210),('Category changes','category','02  Category contribution to sales change','Bar',24,556,655,236),('Regional changes','region','03  Regional contribution to sales change','Bar',704,556,672,236)],
        'Prioritize East and Office Supplies for source-record review; these are overlapping views. More orders did not offset lower sales per order. Request quantity and unit-price detail before attributing the change to pricing or product mix.',
        'Kaggle Superstore / 9,800 validated lines / Source monetary units; currency unspecified / Sales are not profit / Zak Rademacher')

if __name__ == '__main__':
    import argparse
    parser=argparse.ArgumentParser(description='Rebuild the fixed historical Tableau decision brief. Close Tableau before replacing its source.')
    parser.add_argument('--database',type=Path,required=True)
    parser.add_argument('--output',type=Path,default=PROJECT/'tableau')
    args=parser.parse_args()
    report=build(args.database,args.output)
    path=args.output/'verification.json'
    verification=json.loads(path.read_text())
    verification['database_sha256']=hashlib.sha256(args.database.read_bytes()).hexdigest()
    path.write_text(json.dumps(verification,indent=2)+'\n',encoding='utf-8')
    print(report)
