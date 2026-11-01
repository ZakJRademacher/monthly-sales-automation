"""Recompose native report pages, retaining all existing queries and filters."""
from pathlib import Path
import json,copy,hashlib
W,H=1600,1000
SCHEMA='https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.14.0/schema.json'
def lit(v):
 if isinstance(v,bool):v=str(v).lower()
 elif isinstance(v,(int,float)):v=str(v)+'D'
 else:v="'"+v.replace("'","''")+"'"
 return {'expr':{'Literal':{'Value':v}}}
def color(v):return {'solid':{'color':lit(v)}}
def prop(d,group,**values):d.setdefault(group,[{'properties':{}}])[0]['properties'].update(values)
def position(v,box):
 x,y,w,h=box;v['position'].update(x=x,y=y,width=w,height=h,z=10)
def box(v,bg,ink,line,rounded=True):
 o=v['visual'].setdefault('visualContainerObjects',{})
 prop(o,'background',show=lit(True),color=color(bg),transparency=lit(0))
 prop(o,'border',show=lit(rounded),color=color(line),radius=lit(16 if rounded else 0),width=lit(1))
 prop(o,'padding',top=lit(14),bottom=lit(14),left=lit(18),right=lit(18))
 prop(o,'title',fontColor=color(ink),fontSize=lit(12),fontFamily=lit('Segoe UI Semibold'),titleWrap=lit(True))
def textbox(name,text,rect,size,ink,bg=None):
 v={'$schema':SCHEMA,'name':name,'position':{'x':0,'y':0,'width':1,'height':1,'z':1,'tabOrder':0},'visual':{'visualType':'textbox','drillFilterOtherVisuals':True,'objects':{'general':[{'properties':{'paragraphs':[{'textRuns':[{'value':line,'textStyle':{'fontFamily':'Segoe UI','fontSize':str(size)+'pt','color':ink}}]} for line in text.split('\n')]}}]}}}
 position(v,rect);v['position']['z']=1
 box(v,bg or '#FFFFFF',ink,bg or '#FFFFFF',False)
 if bg is None:prop(v['visual']['visualContainerObjects'],'background',show=lit(False))
 prop(v['visual']['visualContainerObjects'],'title',show=lit(False))
 prop(v['visual']['visualContainerObjects'],'padding',top=lit(0),bottom=lit(0),left=lit(0),right=lit(0))
 return v
def textstyle(v,size,ink):
 for g in v['visual'].get('objects',{}).get('general',[]):
  for p in g.get('properties',{}).get('paragraphs',[]):
   for r in p.get('textRuns',[]):r.setdefault('textStyle',{}).update(fontFamily='Segoe UI',fontSize=f'{size}pt',color=ink)
def navigator(count,blue):
 v=textbox('layout-navigator','',(20,248,176,count*58),11,'#FFFFFF')
 v['position']['z']=30;v['visual']['visualType']='pageNavigator';v['visual']['objects']={
 'layout':[{'properties':{'orientation':lit(1),'rowCount':lit(count),'columnCount':lit(1),'cellPadding':lit(6)}}],
 'shape':[{'properties':{'tileShape':lit('rectangleRounded'),'roundEdge':lit(12)}}],
 'pages':[{'properties':{'showHiddenPages':lit(False),'showTooltipPages':lit(False)}}]}
 for group in ['fill','text','outline']:
  entries=[]
  for state in ['default','hover','selected']:
   p={'show':lit(True)}
   if group=='fill':p.update(fillColor=color('#294F89' if state=='selected' else '#263D60' if state=='hover' else '#15253E'),transparency=lit(0))
   elif group=='text':p.update(fontFamily=lit('Segoe UI Semibold'),fontSize=lit(10),fontColor=color('#FFFFFF' if state=='selected' else '#BECCE1'),horizontalAlignment=lit('left'),leftMargin=lit(12))
   else:p={'show':lit(False)}
   entries.append({'properties':p,'selector':{'id':state}})
  v['visual']['objects'][group]=entries
 return v
def apply(report,project):
 report=Path(report);pages=report/'definition/pages';metadata=json.loads((pages/'pages.json').read_text(encoding='utf-8-sig'));count=len(metadata['pageOrder'])
 dark=True;canvas='#0B1423';surface='#142339';ink='#EAF0FC';muted='#A2B2CC';line='#263B57';blue='#66A0FF';accent='#FFAD72'
 tokens=report.parent.parent/'design-tokens.json'
 if tokens.exists():
  c=json.loads(tokens.read_text())['colors'];canvas,surface,ink,muted,line,blue,accent=[c[k] for k in ['canvas','surface','ink','muted','line','primary','accent']]
 names={'sales':'Monthly\nSales','marketing':'Marketing\nCampaigns','commerce':'Commerce\nOperations'}
 results=[]
 for pagepath in pages.glob('*/page.json'):
  page=json.loads(pagepath.read_text(encoding='utf-8-sig'));page.update(width=W,height=H,displayOption='FitToPage');prop(page.setdefault('objects',{}),'background',color=color(canvas),transparency=lit(0));pagepath.write_text(json.dumps(page,indent=2)+'\n')
  folder=pagepath.parent/'visuals';visuals={f.parent.name:json.loads(f.read_text(encoding='utf-8-sig')) for f in folder.glob('*/visual.json') if not f.parent.name.startswith('layout-')}
  contracts={k:copy.deepcopy({a:v['visual'].get(a) for a in ['query','filterConfig','drillFilterOtherVisuals']}) for k,v in visuals.items()}
  def move(k,rect,bg=None,size=None,fg=None):
   if k not in visuals:return
   v=visuals[k];position(v,rect);box(v,bg or surface,fg or ink,line,v['visual']['visualType']!='textbox')
   if v['visual']['visualType']=='textbox':prop(v['visual']['visualContainerObjects'],'padding',top=lit(0),bottom=lit(0),left=lit(0),right=lit(0))
   if size:textstyle(v,size,fg or ink)
   if v['visual']['visualType']=='textbox' and bg is None:prop(v['visual']['visualContainerObjects'],'background',show=lit(False))
  for k,v in visuals.items():
   ty=v['visual']['visualType'];o=v['visual'].setdefault('objects',{})
   # Recolor presentation objects, never query definitions or source data.
   aliases={'#FFFFFF':surface,'#F3F5FA':canvas,'#F4F2FB':canvas,'#17243D':ink,'#132342':ink,'#66738B':muted,'#596883':muted,'#E1E6F0':line,'#E3E8E5':line,'#3569EC':blue,'#6250DF':blue,'#2458DB':blue,'#C83E83':accent,'#C92C74':accent,'#BD3B97':accent,'#FFAC6C':accent,'#4D91FF':blue,'#2454A8':blue,'#C25170':accent,'#F8EAF2':'#1A3252','#EEF2FC':'#1A3252','#EDF2FF':'#1A3252'}
   if tokens.exists():aliases.update({k.upper():c[v] for k,v in json.loads(tokens.read_text())['native_aliases'].items() if v in c})
   def recolor(obj):
    if isinstance(obj,str):
     import re
     return re.sub(r'#[0-9a-fA-F]{6}',lambda m:aliases.get(m[0].upper(),m[0]),obj)
    if isinstance(obj,list):return [recolor(x) for x in obj]
    if isinstance(obj,dict):return {k:recolor(x) for k,x in obj.items()}
    return obj
   v['visual']['objects']=o=recolor(o)
   def original_colors(value):
    if isinstance(value,str):return value.replace('#3B4ED4',blue).replace('#B32787',accent).replace('#202143',ink)
    if isinstance(value,list):return [original_colors(x) for x in value]
    if isinstance(value,dict):return {k:original_colors(x) for k,x in value.items()}
    return value
   v['visual']['objects']=o=original_colors(o)
   box(v,surface,ink,line,ty!='textbox')
   if ty=='textbox':textstyle(v,12,ink)
   if ty=='slicer':
    prop(o,'items',fontColor=color('#E9F0FC'),background=color('#15253E'),textSize=lit(10));prop(o,'header',fontColor=color('#B5C4DC'),textSize=lit(10));box(v,'#15253E','#B5C4DC','#273D5D',True)
   if ty in {'card','multiRowCard'}:
    prop(o,'labels',color=color(ink),fontSize=lit(32 if ty=='card' else 15))
    if ty=='multiRowCard':
     prop(o,'dataLabels',color=color(ink),fontSize=lit(13));prop(o,'cardTitle',color=color(ink),fontSize=lit(13));prop(o,'categoryLabels',show=lit(False));prop(o,'card',barShow=lit(False))
   if ty in {'lineChart','ribbonChart','clusteredBarChart','clusteredColumnChart'}:
    for axis in ['categoryAxis','valueAxis']:prop(o,axis,labelColor=color(muted),titleColor=color(muted),gridlineColor=color(line),fontSize=lit(10))
    prop(o,'legend',labelColor=color(muted),fontSize=lit(10))
    prop(o,'labels',color=color(ink),fontSize=lit(11))
   if ty=='tableEx':
    prop(o,'columnHeaders',fontColor=color(muted),backColor=color(surface),fontSize=lit(10))
    prop(o,'values',fontColorPrimary=color(ink),fontColorSecondary=color(ink),backColorPrimary=color(surface),backColorSecondary=color('#1B2C45' if dark else '#F4F6FB'),fontSize=lit(10))
    prop(o,'total',fontColor=color(ink),backColor=color(surface))
  move('title',(252,30,1316,76),size=27)
  for k in ['sub','subtitle','instructions','intro']:move(k,(252,112,1316,52),size=12,fg=muted)
  for k in ['eyebrow','brand']:move(k,(24,890,168,64),size=9,fg='#9CADC9')
  move('footer',(252,964,1316,30),size=8,fg=muted)
  # The existing source/period filters become a persistent left control rail.
  filters=[k for k in ['reportMonth','month','filter0','category','filter1','region','state','filter2'] if k in visuals]
  start=516 if count>2 else 444
  for i,k in enumerate(filters):
   move(k,(20,start+i*122,176,106),bg='#15253E',fg='#C4D1E6')
   prop(visuals[k]['visual']['visualContainerObjects'],'padding',top=lit(8),bottom=lit(8),left=lit(12),right=lit(12))
  name=pagepath.parent.name
  if project=='marketing':
   if name=='decision':
    for k,r in {'kpi2':(252,188,390,152),'kpi0':(666,188,286,152),'kpi1':(976,188,286,152),'kpi3':(1286,188,282,152),'outcomes':(252,382,750,306),'workload':(1030,382,538,306),'finding':(252,720,1316,76),'action':(252,824,1316,108)}.items():move(k,r)
    box(visuals['kpi2'],'#234E96','#FFFFFF','#3869AE');prop(visuals['kpi2']['visual']['objects'],'labels',color=color('#FFFFFF'),fontSize=lit(44))
    move('action',(252,824,1316,108),bg='#1A3252',size=12)
   else:
    move('evidence',(252,202,1316,246));move('bands',(252,482,632,330));move('definitions',(916,482,652,330),bg=surface,size=13);move('small',(252,850,1316,92),bg='#1A3252',size=12)
  elif project=='commerce' and report.name=='DeliveryPriorities.Report':
   if name=='decision':
    for k,r in {'kpi2':(252,188,390,152),'kpi0':(666,188,286,152),'kpi1':(976,188,286,152),'kpi3':(1286,188,282,152),'workload':(252,382,746,394),'rate':(1026,382,542,394),'reading':(252,798,1316,28),'interpretation':(252,834,1316,64),'snapshotfinding':(252,912,1316,44)}.items():move(k,r)
    box(visuals['kpi2'],'#214D99','#FFFFFF','#3969B8');prop(visuals['kpi2']['visual']['objects'],'labels',color=color('#FFFFFF'),fontSize=lit(44))
    move('reading',(252,798,1316,28),size=10,fg=accent);move('snapshotfinding',(252,912,1316,44),size=10,fg=muted)
   else:
    move('checks',(252,206,620,412));move('method',(902,206,666,504),bg=surface,size=14);move('refresh',(252,746,1316,130),bg=surface,size=13)
  elif project=='commerce':
   for k,r in {'kpi648':(252,190,390,146),'kpi24':(666,190,286,146),'kpi336':(976,190,286,146),'kpi960':(1286,190,282,146)}.items():move(k,r)
   for k in ['kpi24','kpi336']:
    prop(visuals[k]['visual']['objects'],'labels',fontSize=lit(24))
   box(visuals['kpi648'],'#214D99','#FFFFFF','#3969B8');prop(visuals['kpi648']['visual']['objects'],'labels',color=color('#FFFFFF'),fontSize=lit(40))
   if name=='overview':move('trend',(252,378,846,370));move('status',(1126,378,442,370));move('guide',(252,788,1316,146),bg=surface,size=13)
   elif name=='delivery':move('states',(252,378,640,300));move('lateTrend',(920,378,648,300));move('stateReview',(252,714,1316,220))
   elif name=='products':move('categoryGroups',(252,378,686,488));move('categoryDetail',(966,378,602,488));move('scope',(252,890,1316,60),size=11,fg=muted)
   else:move('instructions',(252,112,1316,30),size=11,fg=muted);move('refreshGuide',(252,146,1316,38),size=11,fg=muted);move('checks',(252,378,786,324));move('snapshot',(1066,378,502,142));move('rules',(1066,544,502,260),bg=surface,size=13);move('limitations',(252,832,1316,110),size=12)
  else:
   move('period',(252,164,1316,48))
   if 'period' in visuals:
    prop(visuals['period']['visual']['objects'],'labels',fontSize=lit(13))
    prop(visuals['period']['visual']['visualContainerObjects'],'title',show=lit(False))
    prop(visuals['period']['visual']['visualContainerObjects'],'padding',top=lit(4),bottom=lit(4),left=lit(12),right=lit(12))
   if name=='shape':
    for i,(x,w) in enumerate([(252,520),(796,370),(1190,378)]):
     move(f'kpi{i}',(x,220,w,110));move(f'change{i}',(x,334,w,64))
     prop(visuals[f'change{i}']['visual']['objects'],'labels',fontSize=lit(16))
     prop(visuals[f'change{i}']['visual']['visualContainerObjects'],'padding',top=lit(4),bottom=lit(4),left=lit(12),right=lit(12))
     prop(visuals[f'change{i}']['visual']['visualContainerObjects'],'title',fontSize=lit(10))
    box(visuals['kpi0'],'#234E96','#FFFFFF','#3869AE');box(visuals['change0'],'#234E96','#FFFFFF','#3869AE');prop(visuals['kpi0']['visual']['objects'],'labels',color=color('#FFFFFF'),fontSize=lit(40));prop(visuals['change0']['visual']['objects'],'labels',color=color('#FFD1AE'),fontSize=lit(15))
    prop(visuals['change0']['visual']['visualContainerObjects'],'padding',top=lit(4),bottom=lit(4),left=lit(12),right=lit(12))
    prop(visuals['change0']['visual']['visualContainerObjects'],'title',fontSize=lit(10))
    move('headline',(252,402,1316,60));move('ribbon',(252,494,1316,370));move('ribbonHelp',(252,890,1316,58),size=11,fg=muted)
   elif name=='drivers':
    move('headline',(252,218,1316,58));move('categoryChart',(252,312,640,330));move('regionChart',(920,312,648,330))
    for i in range(3):move(f'effect{i}',(252+i*446,680,424,112))
    move('bridgeHelp',(252,824,1316,110),bg='#1A3252',size=12)
   elif name=='products':move('product',(252,218,1316,86));move('productReview',(252,316,750,490));move('productHistory',(1030,316,538,240));move('sourceLines',(1030,580,538,226));move('reviewHelp',(252,838,1316,102),size=12)
   else:
    move('quality',(252,184,398,290));move('basis',(252,504,398,408),bg=surface,size=13);move('coverage',(678,184,400,728));move('refresh',(1106,184,462,390),bg=surface,size=13);move('limits',(1106,604,462,308),bg=surface,size=13)
  if project=='sales' and 'headline' in visuals:
   prop(visuals['headline']['visual']['objects'],'labels',fontSize=lit(21))
   prop(visuals['headline']['visual']['visualContainerObjects'],'padding',top=lit(6),bottom=lit(6),left=lit(12),right=lit(12))
  decorations=[textbox('layout-rail','',(0,0,216,1000),1,'#FFFFFF','#111D33'),textbox('layout-mark','ZR /',(24,28,168,56),28,'#87ACFF'),textbox('layout-name',names[project],(24,112,176,92),20,'#FFFFFF'),textbox('layout-pages','REPORT PAGES',(24,216,168,22),9,'#91A6C7'),navigator(count,blue)]
  for v in decorations:
   if v['name']=='layout-rail':v['position']['z']=0
  for k,v in visuals.items():
   assert contracts[k]=={a:v['visual'].get(a) for a in ['query','filterConfig','drillFilterOtherVisuals']},k
   f=folder/k/'visual.json';f.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
  for v in decorations:
   f=folder/v['name']/'visual.json';f.parent.mkdir(exist_ok=True);f.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
  results.append({'page':name,'existing_visuals':len(visuals),'new_layout_objects':len(decorations),'queries_filters_interactions_preserved':True})
 return results
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('report',type=Path);p.add_argument('--project',choices=['sales','marketing','commerce'],required=True);a=p.parse_args();print(json.dumps(apply(a.report,a.project)))
