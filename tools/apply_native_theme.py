"""Reapply the approved native layout after rebuilding the report."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
def apply(root=ROOT,tableau_path=None):
    root=Path(root);records=[]
    KIND='sales'
    if KIND in {'sales','hotel'}:
        from tableau_layout import apply as arrange_tableau
        paths=[Path(tableau_path)] if tableau_path else (root/'tableau').glob('*.twb')
        records.extend(arrange_tableau(p,KIND) for p in paths)
    if KIND!='hotel':
        from powerbi_layout import apply as arrange_powerbi
        c=json.loads((root/'design-tokens.json').read_text())['colors']
        for report in root.rglob('*.Report'):
            records.extend(arrange_powerbi(report,KIND))
            for p in (report/'StaticResources/RegisteredResources').glob('*.json'):
                theme=json.loads(p.read_text(encoding='utf-8-sig'))
                theme.update(name='Midnight / Blue / Orange',dataColors=[c['primary'],c['accent'],c['prior']],background=c['canvas'],foreground=c['ink'],tableAccent=c['primary'])
                theme['textClasses']={role:{'fontFace':'Segoe UI','color':c['muted'] if role=='label' else c['ink']} for role in ['title','header','label','callout']}
                p.write_text(json.dumps(theme,indent=2)+'\n',encoding='utf-8')
    return records
if __name__=='__main__':print(json.dumps(apply()))
