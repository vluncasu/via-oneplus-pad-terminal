from pathlib import Path
import csv,json,html,zipfile
R=Path(__file__).resolve().parents[1]
checks=json.loads((R/'validation/checks.json').read_text());coll=json.loads((R/'validation/interferences.json').read_text())
assert not coll,coll
assert all(a['pass'] for a in json.loads((R/'validation/root_wall.json').read_text()))
assert json.loads((R/'validation/source_reinforcement.json').read_text())['pass']
assert all(a['pass'] for a in json.loads((R/'validation/port_mouths.json').read_text()))
assert all(a['valid'] and a['mesh_solid'] and a['solids']==1 for a in checks)
assert all(a['pass'] for a in json.loads((R/'validation/roundtrip.json').read_text()))
assert json.loads((R/'validation/cable_channel.json').read_text())['pass']
assert json.loads((R/'validation/tablet_clearance.json').read_text())['pass']
rows=list(csv.DictReader(open(R/'docs/piese_si_imprimare.csv')))
report='\n'.join((R/'docs/PROIECT_SI_ASAMBLARE.md').read_text().splitlines())
imgs=['01_asamblat','02_spate','03_porturi','04_picior_monobloc','05_canal_sectiune','06_nervuri_interioare']
page='''<!doctype html><html lang="ro"><meta charset="utf-8"><title>Terminal R07</title><style>body{background:#edf0f1;color:#172f3e;font:17px/1.6 system-ui;margin:36px auto;max-width:1100px;padding:20px}img{width:100%}a{color:#176284}pre{white-space:pre-wrap;font:inherit}table{border-collapse:collapse;width:100%}td,th{padding:8px;border-bottom:1px solid #ccc}</style><h1>Terminal R07 — mecanică integral imprimată</h1><p>Prototip PETG alb, cu porturi și casetă optică negre. Filete custom imprimate, fără sarcină admisibilă validată.</p><p><a href="preview/Terminal_OPD2203_R07_ASAMBLAT.blend">Blender ASAMBLAT</a> · <a href="cad/Terminal_OPD2203_R07.FCStd">FreeCAD</a> · <a href="plates/index.html">Plăci geometrice</a> · <a href="docs/PROIECT_SI_ASAMBLARE.md">Montaj și limite</a> · <a href="STL_ROMANA/EVIDENTA_FISIERE.csv">STL în română</a></p>'''
page+=f'<p>{len(checks)} modele; {len(coll)} interferențe raportate. Verificare geometrică; nu este un profil de print validat.</p>'
for name in imgs:page+=f'<img src="preview/{name}.png" alt="{name}">'
page+='<h2>Piese și probe</h2><table><tr><th>Cod</th><th>Denumire</th><th>Orientare</th></tr>'
for row in rows:page+='<tr>'+''.join('<td>'+html.escape(row[k])+'</td>' for k in ['ID','Denumire','Orientare'])+'</tr>'
page+='</table><h2>Documentație</h2><pre>'+html.escape(report)+'</pre></html>'
(R/'index.html').write_text(page)
(R/'START_AICI.md').write_text('R07, prototip cu prinderi integral imprimate. Deschide index.html și docs/PROIECT_SI_ASAMBLARE.md. Începe cu probele Q01–Q10. Fișierul Blender este ASAMBLAT. Nu combina cu R06. Nu există G-code sau rezistență fizică validate.\n')
valid={a['id'] for a in json.loads((R/'preview/manifest.json').read_text())}
for folder in ['stl','step','preview','probes']:
 for p in (R/folder).glob('*'):
  if p.suffix in ['.stl','.step'] and p.stem[:1] in 'BHSOVPQR' and p.stem[1:].isdigit() and p.stem not in valid:p.unlink()
archive=R.parent/(R.name+'_PACHET.zip')
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
 for p in R.rglob('*'):
  if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ['.blend1','.FCBak'] and 'debug' not in p.name and p.name not in {'leg_before_thread.step','leg_fixed.step'} and not p.name.startswith('.'):
   z.write(p,str(Path(R.name)/p.relative_to(R)))
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
print(archive)
