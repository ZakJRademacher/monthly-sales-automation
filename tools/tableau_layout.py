"""Native dashboard composition; no data, calculation or filter changes."""
from pathlib import Path
import copy,json,hashlib,xml.etree.ElementTree as E
W,H=1600,1000
INK='#EAF0FC';MUTED='#A2B2CC';BLUE='#66A0FF';PINK='#FFAD72';NAV='#111D33';PAPER='#0B1423';SURFACE='#142339';SOFT='#1A3252';HERO='#234E96'
def contract(book):
 parts=[]
 for node in [book.find('datasources'),book.find('shared-views'),*book.findall('./worksheets/worksheet')]:
  if node is None:continue
  node=copy.deepcopy(node)
  for p in list(node.iter()):
   for child in list(p):
    if child.tag in {'style','layout-options'}:p.remove(child)
  parts.append(E.tostring(node))
 return hashlib.sha256(b''.join(parts)).hexdigest()
def setting(parent,tag,attr,value):
 s=parent.find(tag)
 if s is None:s=E.SubElement(parent,tag)
 f=next((x for x in s.findall('format') if x.get('attr')==attr),None)
 if f is None:f=E.SubElement(s,'format',attr=attr)
 f.set('value',str(value))
def rect(z,x,y,w,h):
 for k,v,denom in [('x',x,W),('y',y,H),('w',w,W),('h',h,H)]:z.set(k,str(round(v/denom*100000)))
def text(z,x,y,w,h,size=12,ink=INK,bg=None,bold=False,content=None):
 rect(z,x,y,w,h)
 if content is not None:
  f=z.find('formatted-text')
  if f is None:f=E.SubElement(z,'formatted-text')
  f.clear();E.SubElement(f,'run').text=content
 for r in z.findall('formatted-text/run'):
  r.set('fontname','Segoe UI');r.set('fontsize',str(size));r.set('fontcolor',ink);r.set('bold',str(bold).lower())
 setting(z,'zone-style','padding',12)
 if bg:setting(z,'zone-style','background-color',bg)
def extra(layout,key,label,x,y,w,h,size=12,ink=INK,bg=None,bold=False):
 z=E.Element('zone',id=str(key),**{'type-v2':'text'});E.SubElement(z,'formatted-text');text(z,x,y,w,h,size,ink,bg,bold,label)
 index=sum(1 for old in layout.findall('zone') if int(old.get('id','0'))>=9000)
 layout.insert(index,z);return z
def apply(path,project):
 global INK,MUTED,BLUE,PINK,NAV,PAPER,SURFACE,SOFT
 path=Path(path)
 tokens=path.parent.parent/'design-tokens.json'
 if tokens.exists():
  c=json.loads(tokens.read_text())['colors']
  INK,MUTED,BLUE,PINK,PAPER,SURFACE,SOFT=[c[k] for k in ['ink','muted','primary','accent','canvas','surface','soft']]
 tree=E.parse(path);book=tree.getroot();before=contract(book);hotel=project=='hotel'
 # Replace presentation attributes only; source values and calculation syntax are untouched.
 aliases={'#FFFFFF':SURFACE,'#F3F5FA':PAPER,'#FAF7F3':PAPER,'#F5F7FC':PAPER,
 '#17243D':INK,'#132342':INK,'#18304F':INK,'#444444':MUTED,'#596883':MUTED,
 '#66738B':MUTED,'#647085':MUTED,'#2454A8':BLUE,'#2458DB':BLUE,'#3569EC':BLUE,
 '#C25170':PINK,'#C83E83':PINK,'#C92C74':PINK,'#EDF0F6':'#263B57',
 '#9BAAC5':'#7891B6','#9BA8BF':'#7891B6','#ABB8D1':'#7891B6'}
 if tokens.exists():aliases.update({k.upper():c[v] for k,v in json.loads(tokens.read_text())['native_aliases'].items() if v in c})
 for element in book.iter():
  for attr,value in list(element.attrib.items()):
   if attr in {'fontcolor','color','to','value'} and value.upper() in aliases:
    element.set(attr,aliases[value.upper()])
 for dash in book.findall('./dashboards/dashboard'):
  size=dash.find('size')
  for k,v in [('maxwidth',W),('minwidth',W),('maxheight',H),('minheight',H)]:size.set(k,str(v))
  layout=dash.find('./zones/zone')
  for z in list(layout):
   if z.tag=='zone' and int(z.get('id','0'))>=9000:layout.remove(z)
  zones={int(z.get('id')):z for z in layout.findall('zone')}
  setting(layout,'zone-style','background-color',PAPER)
  extra(layout,9000,'',0,0,216,1000,1,'#FFFFFF',NAV)
  extra(layout,9001,'ZR /',24,24,168,60,30,'#8BACFF',NAV,True)
  extra(layout,9002,'HOTEL' if hotel else 'MONTHLY',24,106,176,42,16,'#FFFFFF',NAV,True)
  extra(layout,9008,'Cancellations' if hotel else 'SALES',24,148,176,42,14,'#FFFFFF',NAV,True)
  extra(layout,9003,'RESERVATIONS REVIEW' if hotel else 'PERFORMANCE REVIEW',24,200,176,42,9,'#99A9C4',NAV)
  extra(layout,9004,'HISTORICAL ANALYSIS\n\nCompare like periods.\nKeep the population visible.\n\nZak Rademacher',24,810,176,165,10,'#A7B6CE',NAV)
  if dash.get('name')=='02  Definitions and trial':
   text(zones[200],252,36,1316,84,31,INK,bold=True)
   text(zones[201],252,130,1316,114,15,MUTED)
   text(zones[202],276,296,590,64,20,BLUE,bg=SURFACE,bold=True)
   text(zones[203],276,360,590,460,16,INK,bg=SURFACE)
   text(zones[204],930,296,614,64,20,PINK,bg=SURFACE,bold=True)
   text(zones[205],930,360,614,460,16,INK,bg=SURFACE)
   extra(layout,9010,'02 / METHOD & TRIAL',252,900,1316,48,11,MUTED)
   continue
  text(zones[2],252,22,1316,30,10,BLUE,bold=True,content='HOTEL CANCELLATIONS  /  DECISION STUDIO' if hotel else 'MONTHLY SALES  /  DECISION STUDIO')
  text(zones[3],252,58,1316,70,29,INK,bold=True)
  text(zones[4],252,126,1316,44,11,MUTED)
  if hotel:
   for i,key in enumerate([120,121,122,123]):
    rect(zones[key],24,276+i*112,168,88);setting(zones[key],'zone-style','background-color',SURFACE);setting(zones[key],'zone-style','padding',6)
   for key,box in {102:(252,190,390,142),101:(666,190,286,142),100:(976,190,286,142),103:(1286,190,282,142)}.items():
    rect(zones[key],*box);setting(zones[key],'zone-style','background-color',HERO if key==102 else SURFACE);setting(zones[key],'zone-style','padding',14)
   for key,box in {14:(252,370,636,280),15:(916,370,652,280),16:(252,684,636,238),17:(916,684,652,238)}.items():rect(zones[key],*box);setting(zones[key],'zone-style','padding',16)
   text(zones[19],252,938,180,34,9,BLUE,bold=True)
   text(zones[20],432,934,1136,40,10,INK)
   text(zones[21],252,974,1316,24,8,MUTED)
  else:
   extra(layout,9005,'DECEMBER 2018',24,282,168,42,12,'#FFFFFF',NAV,True)
   extra(layout,9006,'MATCHED WINDOW\n01–30 DEC\n\n2018 versus 2017',24,340,168,154,13,'#A7B6CE',NAV)
   extra(layout,9007,'READING ORDER\n\n01  Performance\n02  Contributions\n03  Next check',24,546,168,188,11,'#A7B6CE',NAV)
   for ids,x,w,bg,ink in [([5,6,7],252,520,HERO,'#FFFFFF'),([8,9,10],796,370,SURFACE,INK),([11,12,13],1190,378,SURFACE,INK)]:
    text(zones[ids[0]],x,190,w,38,10,'#D4DFF4' if ids[0]==5 else MUTED,bg,True)
    text(zones[ids[1]],x,228,w,78,44 if ids[0]==5 else 36,ink,bg,True)
    text(zones[ids[2]],x,306,w,44,10,'#D4DFF4' if ids[0]==5 else MUTED,bg)
   rect(zones[14],252,386,852,296);setting(zones[14],'zone-style','padding',16)
   rect(zones[15],952,422,140,70)
   rect(zones[16],252,714,852,236);setting(zones[16],'zone-style','padding',16)
   rect(zones[17],1132,386,436,296);setting(zones[17],'zone-style','padding',16)
   text(zones[18],1144,728,412,48,10,PINK,SOFT,True,content='03 / THE NEXT CHECK')
   original=' '.join(' '.join((r.text or '') for r in zones[19].findall('formatted-text/run')).split())
   text(zones[19],1144,776,412,174,12,INK,SOFT,content=original)
   text(zones[20],252,970,1316,28,8,MUTED)
  for z in layout.findall('zone'):
   if z.get('name') and not(z.get('type') or z.get('type-v2')):setting(z,'zone-style','background-color',HERO if hotel and z.get('name')=='Selected rate' else SURFACE)
  # Tableau content-model ordering: zone-style follows the formatted text/zones.
  for s in list(layout.findall('zone-style')):layout.remove(s);layout.append(s)
 for sheet in book.findall('./worksheets/worksheet'):
  name=sheet.get('name');hero=hotel and name=='Selected rate';kpi=hotel and name in {'Selected rate','Selected bookings','Selected cancellations','Canceled booked nights'}
  color='#FFFFFF' if hero else PINK if name in {'Segment rate','Selected cancellations'} else BLUE
  for r in sheet.findall('./layout-options/title/formatted-text/run'):
   r.set('fontname','Segoe UI');r.set('fontsize','11' if kpi else '14');r.set('fontcolor','#FFFFFF' if hero else INK);r.set('bold','true')
  style=sheet.find('./table/style')
  if style is not None:
   for rule in style.findall('style-rule'):
    for f in rule.findall('format'):
     if f.get('attr')=='background-color':f.set('value',HERO if hero else SURFACE)
     if f.get('attr')=='font-family':f.set('value','Segoe UI')
     if f.get('attr') in {'color','font-color'}:f.set('value','#FFFFFF' if hero else MUTED if rule.get('element') in {'axis','label'} else INK)
     if f.get('attr')=='stroke-color' and rule.get('element')=='gridline':f.set('value','#263B57')
   for target in ['pane','table','header','cell']:
    setting_rule=E.SubElement(style,'style-rule',element=target)
    E.SubElement(setting_rule,'format',attr='background-color',value=HERO if hero else SURFACE)
    E.SubElement(setting_rule,'format',attr='color',value=INK)
  for pane_style in sheet.findall('./table/panes/pane/style'):
   rule=E.SubElement(pane_style,'style-rule',element='pane')
   E.SubElement(rule,'format',attr='background-color',value=HERO if hero else SURFACE)
   rule=E.SubElement(pane_style,'style-rule',element='mark')
   E.SubElement(rule,'format',attr='color',value=INK)
   # Tableau reads the first matching mark format. Update every prior rule,
   # rather than relying on a later rule to override a native-saved value.
   for mark_rule in pane_style.findall('./style-rule[@element="mark"]'):
    for f in mark_rule.findall('format'):
     if f.get('attr')=='color':f.set('value',INK)
     if hotel and f.get('attr')=='mark-color':f.set('value',color)
     if kpi and f.get('attr')=='font-size':f.set('value','40' if hero else '32')
  if hotel:
   for s in sheet.findall('./table/panes/pane/style'):
    rule=E.SubElement(s,'style-rule',element='mark')
    for attr,value in [('mark-color',color),('color',INK),('font-size','40' if hero else '32' if kpi else '10')]:E.SubElement(rule,'format',attr=attr,value=value)
 assert contract(book)==before,'Unexpected data, worksheet or filter change'
 E.indent(tree);tree.write(path,encoding='utf-8',xml_declaration=True)
 return {'path':str(path),'business_contract_sha256':before,'width':W,'height':H}
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('workbook',type=Path);p.add_argument('--project',choices=['sales','hotel'],required=True);a=p.parse_args();print(json.dumps(apply(a.workbook,a.project)))
