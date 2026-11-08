"""Validate local documentation targets, PNG headers and gallery inventory without dependencies."""
from pathlib import Path
import json,re,struct,hashlib,sys
r=Path(__file__).resolve().parents[1]
errors=[];links=0
for p in [r/'README.md',*sorted((r/'docs').glob('*.md')),*sorted((r/'hardware/cad').glob('*.md'))]:
 for target in re.findall(r'\]\(([^)]+)\)',p.read_text()):
  if target.startswith(('https://','http://','mailto:','#')):continue
  links+=1;dest=(p.parent/target.split('#')[0]).resolve()
  if not dest.exists():errors.append(f'{p.relative_to(r)}: missing {target}')
manifest=json.loads((r/'media/render-manifest.json').read_text())
if '--refresh-render-hashes' in sys.argv:
 for m in manifest:
  p=r/m['file'];data=p.read_bytes();m['sha256']=hashlib.sha256(data).hexdigest();m['pixels']=list(struct.unpack('>II',data[16:24]))
 (r/'media/render-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
seen=set()
for m in manifest:
 if m['figure'] in seen:errors.append(f'duplicate figure {m["figure"]}')
 seen.add(m['figure']);p=r/m['file']
 if not p.exists():errors.append(f'missing figure {m["file"]}');continue
 b=p.read_bytes()[:24]
 if b[:8]!=b'\x89PNG\r\n\x1a\n':errors.append(f'invalid PNG {m["file"]}');continue
 w,h=struct.unpack('>II',b[16:24])
 if m.get('sha256') and hashlib.sha256(p.read_bytes()).hexdigest()!=m['sha256']:errors.append(f'hash mismatch {m["file"]}')
 if m.get('pixels') and m['pixels']!=[w,h]:errors.append(f'dimension mismatch {m["file"]}')
 if min(w,h)<1000:errors.append(f'undersized render {m["file"]}: {w}x{h}')
 if not m.get('caption'):errors.append(f'missing caption {m["file"]}')
if errors:raise SystemExit('\n'.join(errors))
print(f'PASS: {links} local links, {len(manifest)} captioned PNG figures, unique figure IDs.')
