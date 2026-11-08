from pathlib import Path
import csv,json,shutil
R=Path(__file__).resolve().parents[1]
manifest=json.loads((R/'preview/manifest.json').read_text())
out=R/'PIESE_R13';out.mkdir(exist_ok=True)
rows=[]
for a in manifest:
 c=a['id'];colour='REFERINTE_NU_IMPRIMA' if a['kind']=='reference' else 'PROBE' if a['kind']=='probe' else 'PETG_NATURAL' if c=='O05' else 'PETG_NEGRU' if c in ['O01','O03','P01'] else 'PETG_ALB'
 target=out/colour;target.mkdir(exist_ok=True)
 import unicodedata
 name=unicodedata.normalize('NFKD',a['name']).encode('ascii','ignore').decode();name=''.join(ch if ch.isalnum() else '_' for ch in name)
 src=R/('probes' if a['kind']=='probe' else 'stl')/(c+'.stl')
 shutil.copy2(src,target/(c+'_'+name+'.stl'))
 shutil.copy2(R/'step'/(c+'.step'),target/(c+'_'+name+'.step'))
 rows.append({'Cod':c,'Denumire':a['name'],'Material':colour,'Statut':'PROTOTIP; ajustaje, cleme si imprimare de probat'})
with open(out/'EVIDENTA.csv','w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
# Remove obsolete revision names inside this new revision only.
for p in (R/'cad').iterdir():
 if p.name!='Terminal_OPD2203_R13.FCStd':p.unlink()
print(len(rows),'parts and references organised')
