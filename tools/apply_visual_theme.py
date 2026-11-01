"""Apply the sales presentation to generated or native-saved Tableau XML.

The reporting CSV, calculations, filters, shelves and data connections are never
rewritten. Keep colors in design-tokens.json so packaging cannot restore old ones.
"""
import json
from pathlib import Path
import xml.etree.ElementTree as E

PROJECT = Path(__file__).resolve().parents[1]


def apply_theme(path):
    theme = json.loads((PROJECT/'tableau/design-tokens.json').read_text(encoding='utf-8'))
    c = theme['colors'];font=theme['font'];width=theme['width'];height=theme['height']
    tree=E.parse(path);root=tree.getroot()
    replacements={'#203b43':c['ink'],'#60757b':c['muted'],'#61777d':c['muted'],
        '#147d80':c['primary'],'#be5d50':c['accent'],'#8fa4a5':c['prior'],
        '#ba852d':c['partial'],'#f6f5f0':c['paper'],'#e5e9e7':c['grid'],'#ccd5d3':c['zero']}
    for element in root.iter():
        for key,val in list(element.attrib.items()):
            if val.lower() in replacements:element.set(key,replacements[val.lower()])
    palette={'Current':c['primary'],'Prior':c['prior'],'Decline':c['accent'],'Increase':c['primary']}
    for encoding in root.findall('.//encoding'):
        if encoding.get('attr')=='color':
            for mapping in encoding.findall('map'):
                try:member=json.loads(mapping.findtext('bucket'))
                except (ValueError,TypeError):continue
                if member in palette:mapping.set('to',palette[member])
    dashboard=root.find('./dashboards/dashboard')
    size=dashboard.find('size')
    for key,val in [('maxwidth',width),('minwidth',width),('maxheight',height),('minheight',height)]:size.set(key,str(val))
    layout=dashboard.find('zones/zone')
    zones={int(z.get('id')):z for z in layout.findall('zone')}

    def style(zone,attr,value):
        s=zone.find('zone-style')
        if s is None:s=E.SubElement(zone,'zone-style')
        setting=next((f for f in s.findall('format') if f.get('attr')==attr),None)
        if setting is None:setting=E.SubElement(s,'format',attr=attr)
        setting.set('value',str(value))

    def position(key,x,y,w,h):
        z=zones[key]
        for attr,v,dimension in [('x',x,width),('y',y,height),('w',w,width),('h',h,height)]:z.set(attr,str(round(v/dimension*100000)))
        return z

    def text(key,x,y,w,h,size=12,color=None,bold=False,background=None,content=None):
        z=position(key,x,y,w,h)
        for run in z.findall('formatted-text/run'):
            run.set('fontname',font);run.set('fontsize',str(size));run.set('fontcolor',color or c['ink']);run.set('bold',str(bold).lower())
        if content is not None:
            formatted=z.find('formatted-text');formatted.clear()
            run=E.SubElement(formatted,'run',fontname=font,fontsize=str(size),fontcolor=color or c['ink'],bold=str(bold).lower());run.text=content
        style(z,'padding','10');style(z,'background-color',background or c['paper'])

    text(2,32,18,1336,30,10,c['primary'],True,content='ZAK RADEMACHER  /  MONTHLY SALES')
    text(3,32,62,1336,64,32,c['ink'],True)
    text(4,32,128,1336,44,11,c['muted'])
    for i,(label,value,context) in enumerate([(5,6,7),(8,9,10),(11,12,13)]):
        x=32+i*452;bg=['#EDF3FF','#F4F6FB','#FFF0F7'][i]
        text(label,x,190,432,34,10,c['muted'],True,bg)
        text(value,x,224,432,66,36,[c['ink'],c['primary'],c['accent']][i],True,bg)
        text(context,x,290,432,40,11,c['muted'],False,bg)
    position(14,32,364,1134,218)
    position(15,1190,396,178,108)
    position(16,32,606,650,238)
    position(17,718,606,650,238)
    text(18,32,872,1336,30,10,c['primary'],True,content='THE NEXT CHECK  /  INVESTIGATE THE GAP')
    text(19,32,908,1336,72,12,c['ink'],False,'#EDF3FF')
    text(20,32,997,1336,32,9,c['muted'])
    style(layout,'background-color',c['paper'])
    E.indent(tree);tree.write(path,encoding='utf-8',xml_declaration=True)
    return path


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('workbook',type=Path)
    args=parser.parse_args();print(apply_theme(args.workbook))
