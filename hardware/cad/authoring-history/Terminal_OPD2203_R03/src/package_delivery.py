"""Refresh quickstart, check local links, and package only current revision deliverables."""
from pathlib import Path
import json,csv,re,zipfile
ROOT=Path(__file__).resolve().parents[1]
rows=list(csv.DictReader(open(ROOT/'docs/piese_si_imprimare.csv')))
manifest=json.loads((ROOT/'preview/manifest.json').read_text())
checks=json.loads((ROOT/'validation/roundtrip_mesh.json').read_text())
coll=json.loads((ROOT/'validation/interferences.json').read_text())
sweeps=json.loads((ROOT/'validation/service_sweeps.json').read_text())
marks=json.loads((ROOT/'docs/hidden_marks.json').read_text())
plates=json.loads((ROOT/'validation/plates.json').read_text())
assert all(x['pass'] for x in checks),[x for x in checks if not x['pass']]
assert not coll,coll
assert all(x['pass'] for x in sweeps),sweeps
prod=[x for x in rows if x['Tip']=='print' and not x['ID'].startswith('Q')]
probes=[x for x in rows if x['ID'].startswith('Q')]
plate_count=len(list((ROOT/'plates').glob('*.3mf')))
nmarks=sum('depth_mm' in m for m in marks)
(ROOT/'START_AICI.md').write_text(f'''# Terminal OPD2203 R03 — începe aici

Deschide **index.html** pentru randări, secțiuni, model CAD și rezultate. Pentru montaj, citește **docs/ASAMBLARE_SIMPLA.md**: este ghidul scurt, cu codurile pieselor și ordinea operațiilor.

- Porturi: nouă cartușe adâncite, ghidaje T, pieptene P10 și stifturi P11/P12. Imprimate separat, demontabile fără adeziv.
- Picior: S01/S02 și patru chei imprimate S21–S24; fără cele patru șuruburi transversale ale versiunilor anterioare. Cele opt M4 metalice de la cap/bază rămân necesare.
- Identificare: {nmarks} repere au coduri/cifre gravate pe fețe ascunse. Cele prea mici sunt identificate prin celula din placa de imprimare; lista exactă este în docs/hidden_marks.json.
- Pachet: {len(prod)} piese imprimabile pentru produs, {len(probes)} probe, {plate_count} plăci 3MF și 17 randări CAD.

## Primele imprimări

1. **Q25** — colțul tabletei (~1,5 g PETG geometric).
2. **Q21–Q24** — contur economic complet (~24 g PETG geometric).
3. **Q61 + Q62** — Ethernet și ghidajul real.
4. **Q63 + Q64** — cheia piciorului și locașul.
5. Apoi probele USB, cameră, LED și ajustaje din ghid.

Nu amesteca piese din R01/R02 cu R03. Folosește întotdeauna codul și fișierele din acest director.

## Ce s-a verificat

{sum(c['pass'] for c in checks)}/{len(checks)} modele STEP/STL trecute; {len(coll)} coliziuni peste 0,05 mm³; {sum(s['pass'] for s in sweeps)}/{len(sweeps)} mișcări de service eșantionate trecute. Acestea sunt verificări CAD, nu o garanție de imprimare sau rezistență.

Plăcile sunt containere de geometrie, fără G-code și fără suporturi validate. Configurarea și inspecția strat cu strat în Bambu Studio, potrivirea pe tableta reală, probele mecanice și testarea termică rămân necesare. Pentru prima probă, sursa 12 V rămâne externă; terminalul se ancorează de blat.
''')
# Remove only obsolete generated individual exports copied from older revisions.
valid={r['ID'] for r in rows}
for folder in ('stl','step','preview','probes'):
    for p in (ROOT/folder).glob('*'):
        if p.suffix.lower() in ('.stl','.step') and re.fullmatch(r'[A-Z]\d+[LR]?',p.stem) and p.stem not in valid:p.unlink()
for folder in ('cad','preview','step'):
    for p in (ROOT/folder).glob('*'):
        if p.name.startswith('Terminal') and ('R01' in p.name or 'R02' in p.name or p.suffix in ('.FCBak','.blend1')):p.unlink()
# Check all local HTML links/images refer to existing files.
missing=[]
for page in [ROOT/'index.html',ROOT/'plates/index.html']:
    for url in re.findall(r'(?:href|src)="([^"]+)"',page.read_text()):
        if re.match(r'^(https?:|#|data:)',url):continue
        if not (page.parent/url.split('#')[0]).exists():missing.append((str(page),url))
assert not missing,missing
(ROOT/'validation/delivery_check.json').write_text(json.dumps({'step_mesh_pass':len(checks),'production_parts':len(prod),'probes':len(probes),'plates':plate_count,'marked_parts':nmarks,'local_links_ok':True,'sliced':False,'physical_validation':False},indent=2))
include_src={'build.py','parameters.json','hidden_marks.py','mesh_cleanup.py','verify.py','plates.py','render_blender.py','make_docs.py','rebuild.command','Open_in_FreeCAD.FCMacro','package_delivery.py'}
archive=ROOT.parent/(ROOT.name+'_PACHET.zip')
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in ROOT.rglob('*'):
        if not p.is_file():continue
        rel=p.relative_to(ROOT)
        if p.name.startswith('.') or '__pycache__' in p.parts:continue
        if rel.parts[0]=='src' and p.name not in include_src:continue
        if rel.parts[0]=='validation' and (p.suffix not in ('.json','.log') or 'slicer' in p.parts):continue
        if p.suffix in ('.FCBak','.blend1') or '.FCBak' in p.name:continue
        z.write(p,ROOT.name+'/'+str(rel))
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
print(archive,archive.stat().st_size,'bytes')
