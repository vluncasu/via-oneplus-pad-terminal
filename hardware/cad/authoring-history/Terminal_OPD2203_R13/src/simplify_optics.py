import sys,json
from pathlib import Path
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A,Part,MeshPart
from mesh_cleanup import clean
R=Path(__file__).resolve().parents[1];V=A.Vector
H=A.Placement(V(-12,10,240),A.Rotation(V(1,0,0),120))
d=A.openDocument(str(R/'cad/Terminal_OPD2203_R12.FCStd'))
old=A.openDocument(str(R.parent/'Terminal_OPD2203_R11/cad/Terminal_OPD2203_R11.FCStd'))
def local(doc,c):
 s=doc.getObject(c).Shape.copy();s.Placement=H.inverse().multiply(s.Placement);return s
def box(w,h,t,x,y,z):return Part.makeBox(w,h,t,V(x-w/2,y-h/2,z))
def rr(w,h,r,t,x,y,z):
 s=box(w,h,t,x,y,z);return s.makeFillet(r,[e for e in s.Edges if abs(e.Vertexes[-1].Point.z-e.Vertexes[0].Point.z)>t-.001])
# Restore the original sensor face, keeping R12 rear retaining springs.
o=local(d,'O01').common(box(80,260,60,144,0,2.05)).fuse(local(old,'O01').common(box(80,260,22.1,144,0,-20)))
# Four broad rigid pockets. The sheet flexes; no tiny separate pins or spring fingers.
for x in [131.9,156.1]:
 for y in [-55,55]:
  lip=box(1.8,18,3.6,x,y,-2.6)
  lip=lip.cut(box(24.9,20,.65,144,y,-1.8))
  o=o.fuse(lip)
o=o.removeSplitter()
if not o.isValid():o.fix(.01,.001,.1)
# Slightly stiff sheet: two 0.20 mm layers, unnotched, captured under pocket lips.
film=rr(24.8,192.8,11.8,.4,144,0,-1.65)
removed=['O04','V71','V72','V73','V74']
for c in removed:
 if d.getObject(c):d.removeObject(c)
 for folder,ext in [('stl','stl'),('step','step'),('preview','stl')]:
  (R/folder/(c+'.'+ext)).unlink(missing_ok=True)
manifest=json.loads((R/'preview/manifest.json').read_text());manifest=[a for a in manifest if a['id'] not in removed]
report=[]
for c,s,name in [('O01',o,'Caseta optica cu locasuri integrate pentru foita'),('O05',film,'Foita optica flexibila 0.40 mm fara stifturi')]:
 assert s.isValid() and len(s.Solids)==1,(c,s.isValid(),len(s.Solids))
 w=s.copy();w.Placement=H.multiply(s.Placement);ob=d.getObject(c);ob.Shape=w;ob.Label=c+' '+name
 for a in manifest:
  if a['id']==c:a['name']=name
 s.exportStep(str(R/'step'/(c+'.step')))
 t=s.copy();b=t.BoundBox;t.translate(V(-b.XMin,-b.YMin,-b.ZMin))
 for sh,p in [(t,R/'stl'/(c+'.stl')),(w,R/'preview'/(c+'.stl'))]:
  m=MeshPart.meshFromShape(Shape=sh,LinearDeflection=.04,AngularDeflection=.12,Relative=False);clean(m);assert m.isSolid();m.write(str(p))
 report.append({'id':c,'valid_solid':True,'closed_mesh':True})
 print('EXPORTED',c,flush=True)
contacts=[]
for a,b in [('O01','O05'),('O01','H01')]:
 vol=d.getObject(a).Shape.common(d.getObject(b).Shape).Volume
 contacts.append({'a':a,'b':b,'mm3':vol})
 assert vol<.001,(a,b,vol)
# A straight outward pull must meet the lips; release requires sheet flexing.
f=film.copy();f.translate(V(0,0,-.6));v=f.common(o).Volume
assert v>.1
report.append({'contacts':contacts,'outward_sheet_stop_mm3':v,'scope':'Rigid geometry only; bending, print supports and material behaviour require a physical coupon.'})
d.recompute();d.saveAs(str(R/'cad/Terminal_OPD2203_R13.FCStd'))
(R/'preview/manifest.json').write_text(json.dumps(manifest,indent=2))
(R/'validation/optica_simplificata.json').write_text(json.dumps(report,indent=2))
print('DONE',report,flush=True)
