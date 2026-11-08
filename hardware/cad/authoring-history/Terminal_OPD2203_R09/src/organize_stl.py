from pathlib import Path
import csv,shutil,unicodedata,json
R=Path(__file__).resolve().parents[1];O=R/'STL_ROMANA'
if O.exists():shutil.rmtree(O)
O.mkdir()
rows=list(csv.DictReader(open(R/'docs/piese_si_imprimare.csv')))
placements=list(csv.DictReader(open(R/'plates/placements.csv')))
print('Plate columns',list(placements[0]))
def slug(s):
 s=unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode()
 return ''.join(c if c.isalnum() else '_' for c in s).strip('_')
out=[]
for a in rows:
 code=a['ID'];grp='01_PIESE_PRODUS' if a['Tip']=='print' and not code.startswith('Q') else '02_PROBE_ECONOMICE' if code.startswith('Q') else '03_REFERINTE_NU_IMPRIMA'
 dest=O/grp;dest.mkdir(exist_ok=True)
 name=code+'_'+slug(a['Denumire'])+'.stl';src=R/('probes' if code.startswith('Q') else 'stl')/(code+'.stl')
 shutil.copy2(src,dest/name)
 matches=[p['plate'] for p in placements if p['id']==code]
 out.append({'Cod':code,'Fisier':str((dest/name).relative_to(O)),'Denumire':a['Denumire'],'Material':a['Material'],'Orientare':a['Orientare'],'Placa':'; '.join(matches),'Statut':'GEOMETRIE ORIENTATA; SLICE SI PROBA NECESARE'})
with open(O/'EVIDENTA_FISIERE.csv','w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=out[0].keys());w.writeheader();w.writerows(out)
(O/'CITESTE_INAINTE.md').write_text('STL-uri în milimetri, orientate geometric. Nu conțin infill sau suporturi. Citește ../docs/PROIECT_SI_ASAMBLARE.md. Începe cu Q07. Referințele R01–R05 nu sunt piese de imprimat. Nu combina revizii.\n')
print(len(out),'fisiere organizate')
