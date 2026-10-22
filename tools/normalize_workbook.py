"""Normalize display-only workbook theme labels without rewriting native features."""
import io, os, re, sys, zipfile
from pathlib import Path

def normalize(file):
    file = Path(file)
    original = file.read_bytes()
    output = io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(original)) as source, zipfile.ZipFile(output, 'w') as target:
        for item in source.infolist():
            data = source.read(item)
            if item.filename.startswith('xl/theme/') and item.filename.endswith('.xml'):
                data = re.sub(rb'(<(?:[A-Za-z0-9_]+:)?(?:theme|clrScheme|fmtScheme)\b[^>]*\bname=")[^"]*(")', rb'\g<1>Portfolio\2', data)
            target.writestr(item, data)
    replacement = output.getvalue()
    with zipfile.ZipFile(io.BytesIO(replacement)) as checked:
        if checked.testzip() is not None:
            raise ValueError('Workbook ZIP integrity failure')
    pending = file.with_name(file.name + '.metadata.tmp')
    try:
        pending.write_bytes(replacement)
        os.replace(pending, file)
    finally:
        if pending.exists(): pending.unlink()

if __name__ == '__main__':
    for file in sys.argv[1:]: normalize(file)
