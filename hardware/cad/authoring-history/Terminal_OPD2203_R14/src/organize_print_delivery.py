"""Copy current R14 STLs by colour and assembly quantity. No plate layouts."""
import json,struct,hashlib,math,shutil,unicodedata
from pathlib import Path
R=Path(__file__).resolve().parents[1]
out=R/'IMPRIMARE_PE_CULORI'
manifest=json.loads((R/'preview/manifest.json').read_text())
items={a['id']:a for a in manifest}
groups={
 'V21':['V21','V22','V23','V24'],
 'V31':['V31','V32','V33','V34'],
 'V41':['V41','V42','V43','V44'],
 'V51':['V51','V52','V53','V54'],
 'V61':['V61','V62']}
names={
 'V21':'Surub D12 pas 2.5 L12 pentru prinderea capului',
 'V31':'Picior sferic insurubabil D8 cu fanta',
 'V41':'Surub D8 pas 2.5 L10 pentru capacul bazei',
 'V51':'Surub D8 pas 2.5 L14 pentru capacele posterioare',
 'V61':'Surub D8 pas 2.5 L16.3 pentru capacul USB'}
def inspect(p):
 b=p.read_bytes();n=struct.unpack_from('<I',b,80)[0]
 assert len(b)==84+50*n and n>0,p
 v=[]
 for i in range(n):
  a=struct.unpack_from('<12fH',b,84+50*i);v.extend([a[3:6],a[6:9],a[9:12]])
 assert all(math.isfinite(x) for p in v for x in p)
 mn=[min(a[k] for a in v) for k in range(3)];mx=[max(a[k] for a in v) for k in range(3)]
 # Verify reused fasteners have matching normalised tessellation to 0.01 mm.
 signature=hashlib.sha256(repr(sorted(set(tuple(round(a[k]-mn[k],2) for k in range(3)) for a in v))).encode()).hexdigest()
 return dict(signature=signature,sha256=hashlib.sha256(b).hexdigest(),triangles=n,bounds_mm=[round(mx[k]-mn[k],3) for k in range(3)])
def safe(s):
 return ''.join(c if c.isalnum() or c=='.' else '_' for c in unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode())
records=[];done=set()
for a in manifest:
 c=a['id']
 if a['kind']=='reference' or c in done:continue
 probe=a['kind']=='probe';ids=groups.get(c,[c]);done.update(ids)
 folder='90_PROBE_OPTIONALE/01_PETG_ALB' if probe else '03_PETG_NATURAL_TRANSLUCID' if c=='O05' else '02_PETG_NEGRU' if c in ['P01','O01','O03','O06'] else '01_PETG_ALB'
 src=R/('probes' if probe else 'stl')/(c+'.stl');info=inspect(src)
 for other in ids[1:]:assert inspect(R/'stl'/(other+'.stl'))['signature']==info['signature'],ids
 name=names.get(c,a['name']);code=c if len(ids)==1 else c+'-'+ids[-1]
 filename=f'{len(ids):02d}_buc__{code}__{safe(name)}.stl'
 dest=out/folder/filename;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dest)
 assert hashlib.sha256(dest.read_bytes()).hexdigest()==info['sha256']
 records.append(dict(file=str(dest.relative_to(out)),name=name,codes=ids,quantity=len(ids),optional=probe,source=str(src.relative_to(R)),**info))
prod=[a for a in records if not a['optional']]
assert sum(a['quantity'] for a in prod)==len([a for a in manifest if a['kind']=='print'])
assert set(c for a in prod for c in a['codes'])==set(a['id'] for a in manifest if a['kind']=='print')
assert len(list(out.rglob('*.stl')))==len(records)
(out/'INVENTAR_VERIFICAT.json').write_text(json.dumps(records,indent=2,ensure_ascii=False))
lines=['IMPRIMARE TERMINAL OPD2203 — R14','',
 'Cantitatea din numele fisierului este numarul TOTAL de exemplare de imprimat pentru un terminal.',
 'Exemplu: 04_buc__V21-V24...stl contine un singur surub: imprima 4 exemplare, nu 4 din fiecare cod.',
 'Fisierele cu 01_buc se imprima o singura data.',
 'Nu sunt aranjate pe plate-uri. Fiecare STL contine o singura piesa; orientarile R14 au fost pastrate.',
 'Unitati: milimetri. Importa la scara 100%, fara redimensionare automata.',
 '',f'ANSAMBLU: {len(prod)} fisiere STL distincte, {sum(a["quantity"] for a in prod)} piese fizice.']
for folder in ['01_PETG_ALB','02_PETG_NEGRU','03_PETG_NATURAL_TRANSLUCID']:
 rows=[a for a in prod if a['file'].startswith(folder+'/')]
 lines.extend(['',f'{folder}: {sum(a["quantity"] for a in rows)} piese, {len(rows)} fisiere.'])
 lines.extend(f'  {a["quantity"]} buc — {", ".join(a["codes"])} — {a["name"]}' for a in rows)
lines.extend(['','PROBE OPTIONALE:',
 'Cele 15 probe din 90_PROBE_OPTIONALE sunt separate si nu intra in cele 30 de piese ale ansamblului.',
 'Cantitatea 01_buc este pentru o singura incercare; repeti doar probele necesare.',
 'Probele sunt mostenite si nu valideaza mecanismele noi H05/H06 sau caseta R14.',
 'Modelele R01–R05 (tableta, sursa, mufa si gabarite LED) NU sunt piese de imprimat si nu sunt incluse.',
 '', 'NOTE PENTRU IMPORT:',
 'O05: PETG natural/translucid, grosime 0.40 mm; primul strat 0.20 mm si al doilea 0.20 mm.',
 'Structura si suruburile: PETG alb; corpul/masca optica si porturile: PETG negru.',
 'Suruburile V61/V62 raman albe, conform modelului R14 livrat.',
 'Pachetul organizeaza geometria R14; nu contine profil de slicer sau G-code.',
 'Suporturile locale, ajustarile si incadrarea cu brim trebuie verificate in slicer; nu exista validare fizica.',
 'Instructiunile de montaj si orientarile sunt in ../index.html.',
 'INVENTAR_VERIFICAT.json pastreaza sursele, cantitatile, dimensiunile si amprentele fisierelor.'])
(out/'CITESTE_INAINTE_DE_IMPRIMARE.txt').write_text('\n'.join(lines)+'\n')
print(json.dumps(dict(folder=str(out),production_STLs=len(prod),production_pieces=sum(a['quantity'] for a in prod),optional_probes=sum(a['optional'] for a in records),oversize=[a['file'] for a in prod if max(a['bounds_mm'])>256]),indent=2))
