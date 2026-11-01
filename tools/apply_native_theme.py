"""Apply this project's native presentation tokens without changing data logic."""
from pathlib import Path
import copy,hashlib,json,re,xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[1]
TOKEN_PATH=ROOT/'design-tokens.json'

def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def semantic_json(data):
    # All query projections, filters, interactions and textual values are retained.
    if isinstance(data,list):return [semantic_json(x) for x in data]
    if not isinstance(data,dict):return data
    return {k:semantic_json(v) for k,v in data.items() if k not in {
        'visualContainerObjects','textStyle','themeCollection','resourcePackages',
        'categoryAxis','valueAxis','legend','labels','categoryLabels','dataPoint',
        'columnHeaders','values','grid','background','border','title','style','styles',
        'outspace','filterCard','pageInformation','color','fontColor',
        'backColor','fontColorPrimary','backColorPrimary'}}

def native_semantics(book):
    b=copy.deepcopy(book)
    for parent in list(b.iter()):
        for child in list(parent):
            if child.tag in {'style','style-theme','zone-style','layout-options'}:
                parent.remove(child)
    for e in b.iter():
        for key in list(e.attrib):
            if key in {'fontcolor','fontname','fontsize','bold','italic','color'}:
                del e.attrib[key]
    return E.tostring(b)

def apply(root=ROOT,tableau_path=None):
    root=Path(root);t=json.loads((root/'design-tokens.json').read_text())
    c=t['colors']; aliases={k.upper():c[v] for k,v in t['native_aliases'].items()}
    def recolor(value):
        if isinstance(value,str):return re.sub(r'#[0-9a-fA-F]{6}',lambda m:aliases.get(m[0].upper(),m[0]),value)
        if isinstance(value,list):return [recolor(x) for x in value]
        if isinstance(value,dict):return {k:('Segoe UI' if k=='fontFamily' and v=='Georgia' else recolor(v)) for k,v in value.items()}
        return value
    records=[]
    for report in root.rglob('*.Report'):
        for p in list((report/'definition').rglob('*.json'))+list((report/'StaticResources/RegisteredResources').glob('*')):
            if not p.is_file():continue
            try:a=json.loads(p.read_text(encoding='utf-8-sig'))
            except (ValueError,UnicodeError):continue
            old=digest(semantic_json(a));b=recolor(a)
            if p.name=='visual.json' and p.parent.name=='title':
                for group in b.get('visual',{}).get('objects',{}).get('general',[]):
                    for paragraph in group.get('properties',{}).get('paragraphs',[]):
                        for run in paragraph.get('textRuns',[]):
                            run.setdefault('textStyle',{}).update(fontFamily='Segoe UI Semibold',fontSize='26pt')
            # Native theme's defaults also cover new visuals added interactively.
            if p.parent.name=='RegisteredResources':
                b.update(name=t['name'],dataColors=[c['primary'],c['accent'],c['prior']],
                    background=c['canvas'],foreground=c['ink'],tableAccent=c['primary'])
                b['textClasses']={role:{'fontFace':'Segoe UI','color':c['ink'] if role!='label' else c['muted']} for role in ['title','header','label','callout']}
            else:assert digest(semantic_json(b))==old,str(p)
            if a!=b:p.write_text(json.dumps(b,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
            if p.name in {'visual.json','page.json'}:records.append({'file':p.relative_to(root).as_posix(),'semantic_sha256':old})
    paths=[Path(tableau_path)] if tableau_path else list((root/'tableau').glob('*.twb'))
    for p in paths:
        tree=E.parse(p);book=tree.getroot();before=hashlib.sha256(native_semantics(book)).hexdigest()
        for element in book.iter():
            for attr,value in list(element.attrib.items()):
                if attr in {'fontcolor','value','to','color'}:
                    element.set(attr,recolor(value))
                if attr=='fontname' and value in {'Georgia','Calibri'}:element.set(attr,'Segoe UI')
        for encoding in book.findall('.//encoding'):
            if encoding.get('attr')!='color':continue
            for mapping in encoding.findall('map'):
                try:member=json.loads(mapping.findtext('bucket'))
                except (ValueError,TypeError):continue
                if member in {'Partial final month','Higher reported net'}:mapping.set('to','#996A13')
        if root.name=='retail-sales-data-quality':
            zones={z.get('id'):z for z in book.findall('./dashboards/dashboard/zones/zone/zone')}
            for ids,bg,ink in [(['5','6','7'],'#EEEDFC',c['primary']),(['8','9','10'],'#F1F2F8',c['ink']),(['11','12','13'],'#FAEDF5',c['accent'])]:
                for key in ids:
                    z=zones.get(key)
                    if z is None:continue
                    style=z.find('zone-style')
                    if style is None:style=E.SubElement(z,'zone-style')
                    setting=next((f for f in style.findall('format') if f.get('attr')=='background-color'),None)
                    if setting is None:setting=E.SubElement(style,'format',attr='background-color')
                    setting.set('value',bg)
                    if key==ids[1]:
                        for run in z.findall('formatted-text/run'):run.set('fontcolor',ink);run.set('fontsize','34')
        assert hashlib.sha256(native_semantics(book)).hexdigest()==before,str(p)
        tree.write(p,encoding='utf-8',xml_declaration=True)
        records.append({'file':p.relative_to(root).as_posix(),'semantic_sha256':before})
    return records

if __name__=='__main__':
    print(json.dumps({'project':ROOT.name,'checked_native_objects':len(apply())}))
