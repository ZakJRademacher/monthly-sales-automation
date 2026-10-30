"""Package a native-saved Tableau decision brief with its reporting CSV and notices."""
from pathlib import Path
import argparse,copy,json,zipfile,xml.etree.ElementTree as E

COLORS={'Current':'#147d80','Prior':'#8fa4a5','Decline':'#be5d50','Increase':'#147d80','Observed month':'#147d80','Partial final month':'#ba852d','Lower reported net':'#be5d50','Higher reported net':'#ba852d','Gross positive sales':'#147d80'}

def package(project,name):
    source=project/'tableau'/(name+'.twb')
    tree=E.parse(source)
    for encoding in tree.findall('.//encoding'):
        if encoding.get('attr')=='color':
            for mapping in encoding.findall('map'):
                try: member=json.loads(mapping.findtext('bucket'))
                except (ValueError,TypeError):continue
                if member in COLORS:mapping.set('to',COLORS[member])
    if name.startswith('Monthly'):
        for rule in tree.findall('.//worksheet/table/style/style-rule'):
            if rule.get('element')=='axis':
                for setting in rule.findall('format'):
                    if setting.get('attr')=='title':setting.set('value','Cumulative sales' if setting.get('scope')=='rows' else 'Sales change')
        for column in tree.findall('./datasources/datasource/column'):
            if column.get('name')=='[Series]':column.set('caption','Period')
    tree.write(source,encoding='utf-8',xml_declaration=True)
    portable=copy.deepcopy(tree)
    for connection in portable.findall('.//connection'):
        if connection.get('class')=='textscan':connection.set('directory','Data')
    output=project/'deliverables'/(name+'.twbx')
    output.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED) as bundle:
        bundle.writestr(source.name,E.tostring(portable.getroot(),encoding='utf-8',xml_declaration=True))
        bundle.write(project/'tableau/Data/analysis.csv','Data/analysis.csv')
        for relative in ['data/LICENSE','NOTICE','docs/SOURCES.md','tableau/verification.json']:
            p=project/relative
            if p.exists():bundle.write(p,relative)
    return output

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('project',type=Path)
    parser.add_argument('name')
    args=parser.parse_args()
    print(package(args.project,args.name))
