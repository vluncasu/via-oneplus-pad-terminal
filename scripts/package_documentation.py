"""Package the expanded gallery and PDFs without changing application/hardware releases."""
from pathlib import Path
import hashlib,json,shutil,zipfile
r=Path(__file__).resolve().parents[1];out=r/'release-assets';out.mkdir(exist_ok=True)
manifest=json.loads((r/'media/render-manifest.json').read_text())
for m in manifest:
 if not (r/m['file']).exists():raise FileNotFoundError(m['file'])
gallery=out/'VIA_Gallery_33_Views_and_Blender_R14_1.zip'
with zipfile.ZipFile(gallery,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 files=[r/m['file'] for m in manifest]+[r/'media/render-manifest.json',r/'media/via-oneplus-pad-r14-1-assembled.blend',r/'docs/gallery.md',r/'docs/gallery-product.md',r/'docs/gallery-engineering.md',r/'docs/gallery-components.md']
 for p in files:z.write(p,p.relative_to(r))
assets=[gallery]
for name in ['VIA_Assembly_and_Demo_Handbook.pdf','VIA_Engineering_Design_Report.pdf']:
 p=r/'docs'/name;shutil.copy2(p,out/name);assets.append(out/name)
checks=out/'SHA256SUMS_DOCS_EDITION2.txt'
checks.write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name+'\n' for p in sorted(assets)))
with zipfile.ZipFile(gallery) as z:
 assert z.testzip() is None
print('\n'.join(f'{p.name}: {p.stat().st_size:,} bytes' for p in [*assets,checks]))
