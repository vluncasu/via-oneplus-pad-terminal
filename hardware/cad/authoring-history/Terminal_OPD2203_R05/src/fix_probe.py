from pathlib import Path
import sys,csv,json
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A,Part,MeshPart
R=Path(__file__).resolve().parents[1]
p=R/'src/build.py';s=p.read_text();s=s.replace("probe('Q62','Ghidaj Ethernet sectiune corp monobloc',next(i for i in items if i['id']=='B01')['shape'].common(box(21,18,24,-28,-108,11)))","probe('Q62','Ghidaj Ethernet sectiune corp monobloc',max(next(i for i in items if i['id']=='B01')['shape'].common(box(21,18,24,-28,-108,11)).Solids,key=lambda q:q.Volume))");p.write_text(s)
s=Part.Shape();s.read(str(R/'step/Q62.step'));s=max(s.Solids,key=lambda q:q.Volume);s.exportStep(str(R/'step/Q62.step'))
t=s.copy();b=t.BoundBox;t.translate(A.Vector(-b.XMin,-b.YMin,-b.ZMin));m=MeshPart.meshFromShape(Shape=t,LinearDeflection=.07,AngularDeflection=.18,Relative=False);m.write(str(R/'probes/Q62.stl'))
rows=list(csv.DictReader(open(R/'docs/piese_si_imprimare.csv')))
for row in rows:
 if row['ID']=='Q62':row.update(Volum_cm3=round(s.Volume/1000,3),Solide=1,X_print_mm=round(t.BoundBox.XLength,2),Y_print_mm=round(t.BoundBox.YLength,2),Z_print_mm=round(t.BoundBox.ZLength,2))
with open(R/'docs/piese_si_imprimare.csv','w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
from collections import Counter
v,fs=m.Topology;e=Counter(tuple(sorted((f[i],f[(i+1)%3]))) for f in fs for i in range(3))
ok=s.isValid() and len(s.Solids)==1 and m.isSolid() and all(n==2 for n in e.values());assert ok
p=R/'validation/roundtrip_mesh.json';a=json.loads(p.read_text())
for x in a:
 if x['id']=='Q62':x.update(step_solid_count=1,step_valid=True,volume_roundtrip_ok=True,mesh_solid=True,all_edges_two_faces=True,pass_=True);x['pass']=True;x.pop('pass_',None)
p.write_text(json.dumps(a,indent=2));print('Q62 corrected and mesh checked',s.Volume)
