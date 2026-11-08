from pathlib import Path
import csv,json,html,zipfile,hashlib,datetime
R=Path(__file__).resolve().parents[1]
checks=json.loads((R/'validation/checks.json').read_text());coll=json.loads((R/'validation/interferences.json').read_text())
assert not coll,coll
assert all(a['pass'] for a in json.loads((R/'validation/thread_engagement.json').read_text()))
assert all(a['pass'] for a in json.loads((R/'validation/complete_screws.json').read_text()))
for name in ['led_envelopes','usb_sweep','usb_service']:
 assert json.loads((R/f'validation/{name}.json').read_text())['pass'],name
assert json.loads((R/'validation/upper_cable.json').read_text())['pass']
assert all(a['pass'] for a in json.loads((R/'validation/flush_screws.json').read_text()))
assert all(a['pass'] for a in json.loads((R/'validation/root_wall.json').read_text()))
assert json.loads((R/'validation/stand_reinforcement.json').read_text())['pass']
assert all(a['pass'] for a in json.loads((R/'validation/port_mouths.json').read_text()))
printable_ids={a['id'] for a in json.loads((R/'preview/manifest.json').read_text()) if a['kind']=='print'}
assert all(a['valid'] and a['mesh_solid'] and a['solids']==1 and (a['fits'] or a['id'] not in printable_ids) for a in checks)
assert all(a['pass'] for a in json.loads((R/'validation/roundtrip.json').read_text()))
assert json.loads((R/'validation/cable_channel.json').read_text())['pass']
assert json.loads((R/'validation/tablet_clearance.json').read_text())['pass']
rows=list(csv.DictReader(open(R/'docs/piese_si_imprimare.csv')))
report='\n'.join((R/'docs/PROIECT_SI_ASAMBLARE.md').read_text().splitlines())
imgs=['01_asamblat','02_spate','03_porturi','04_picior_monobloc','05_canal_sectiune','06_nervuri_interioare','07_caseta_optica','08_prindere_centrata','09_surub_posterior_complet','10_canal_led_baza','11_canal_led_cap','12_picior_sferic_D8','13_nervuri_picior_si_rezerva_sursa','14_intariri_radacina_picior']
page='''<!doctype html><html lang="ro"><meta charset="utf-8"><title>Terminal R09</title><style>body{background:#edf0f1;color:#172f3e;font:17px/1.6 system-ui;margin:36px auto;max-width:1100px;padding:20px}img{width:100%}a{color:#176284}pre{white-space:pre-wrap;font:inherit}table{border-collapse:collapse;width:100%}td,th{padding:8px;border-bottom:1px solid #ccc}</style><h1>Terminal R09 — mecanică integral imprimată</h1><p>Prototip PETG alb, cu porturi și casetă optică negre. Filete custom imprimate, fără sarcină admisibilă validată.</p><p><a href="preview/Terminal_OPD2203_R09_ASAMBLAT.blend">Blender ASAMBLAT</a> · <a href="cad/Terminal_OPD2203_R09.FCStd">FreeCAD</a> · <a href="plates/index.html">Plăci geometrice</a> · <a href="docs/PROIECT_SI_ASAMBLARE.md">Montaj și limite</a> · <a href="STL_ROMANA/EVIDENTA_FISIERE.csv">STL în română</a></p>'''
page+=f'<p>{len(checks)} modele; {len(coll)} interferențe raportate. Verificare geometrică; nu este un profil de print validat.</p>'
for name in imgs:page+=f'<img src="preview/{name}.png" alt="{name}">'
page+='<h2>Montaj LED 8 mm</h2><img src="docs/SECTIUNE_LED.svg" alt="Secțiune canal LED"><h2>Piese și probe</h2><table><tr><th>Cod</th><th>Denumire</th><th>Orientare</th></tr>'
for row in rows:page+='<tr>'+''.join('<td>'+html.escape(row[k])+'</td>' for k in ['ID','Denumire','Orientare'])+'</tr>'
page+='</table><h2>Documentație</h2><pre>'+html.escape(report)+'</pre></html>'
(R/'index.html').write_text(page)
(R/'START_AICI.md').write_text('R09, prototip cu prinderi integral imprimate. Deschide index.html și docs/PROIECT_SI_ASAMBLARE.md. Începe cu probele Q01–Q15. Fișierul Blender este ASAMBLAT. Nu combina cu R06. Nu există G-code sau rezistență fizică validate.\n')
valid={a['id'] for a in json.loads((R/'preview/manifest.json').read_text())}
for folder in ['stl','step','preview','probes']:
 for p in (R/folder).glob('*'):
  if p.suffix in ['.stl','.step'] and p.stem[:1] in 'BHSOVPQRL' and p.stem[1:].isdigit() and p.stem not in valid:p.unlink()
summary={'revizie':'R09','moment':datetime.datetime.now().isoformat(),'modele_verificate':len(checks),'interferente_piese':len(coll),'placi':json.loads((R/'validation/plates.json').read_text())['plates'],'stare':'VERIFICAT GEOMETRIC; PROTOTIP FIZIC NEVALIDAT','gabarit_usb_mm':[16,10,30],'pozitii_usb':19,'canal_led_mm':8.5,'sha256_cad':hashlib.sha256((R/'cad/Terminal_OPD2203_R09.FCStd').read_bytes()).hexdigest(),'nota':'Logurile build/patch pastreaza etape intermediare; rapoartele JSON finale sunt regenerate dupa corectii.'}
(R/'validation/REZULTAT_FINAL.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False))
archive=R.parent/(R.name+'_PACHET.zip')
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
 for p in R.rglob('*'):
  if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ['.blend1','.FCBak'] and 'debug' not in p.name and p.name not in {'leg_before_thread.step','leg_fixed.step'} and not p.name.startswith('.'):
   z.write(p,str(Path(R.name)/p.relative_to(R)))
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
print(archive)
