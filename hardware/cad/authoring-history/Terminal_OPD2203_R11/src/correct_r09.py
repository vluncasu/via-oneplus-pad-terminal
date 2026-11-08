"""Incremental, auditable correction of the delivered R09 CAD; no rebuilt threads."""
import sys,json,csv,shutil,os
from pathlib import Path
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A, Part, MeshPart
from mesh_cleanup import clean
R=Path(__file__).resolve().parents[1]; V=A.Vector
head=A.Placement(V(-12,10,240),A.Rotation(V(1,0,0),120))
fast=os.environ.get('R10_REPAIR_H01')=='1'
d=A.openDocument(str(R/'cad/Terminal_OPD2203_R10.FCStd') if fast else str(R.parent/'Terminal_OPD2203_R09/cad/Terminal_OPD2203_R09.FCStd'))
def box(w,h,zheight,x,y,z):return Part.makeBox(w,h,zheight,V(x-w/2,y-h/2,z))
def local(code):
 s=d.getObject(code).Shape.copy();s.Placement=head.inverse().multiply(s.Placement);return s
changed={}
h=local('H01')
if fast:
 old=A.openDocument(str(R.parent/'Terminal_OPD2203_R09/cad/Terminal_OPD2203_R09.FCStd'))
 h=old.getObject('H01').Shape.copy();h.Placement=head.inverse().multiply(h.Placement)
for x in [-96,120]:
 for y in [-99,99]:
  cy=86 if y>0 else -86
  bridge=box(22,26,4,x,y,23).cut(Part.makeCylinder(4.6,6,V(x,cy,22)))
  h=h.fuse(bridge)
changed['H01']=h.removeSplitter()
o=local('O01')
# Remove side keys: these obstruct front insertion, rather than retain it.
for x in [121,167]:
 for y in [-50,50]:o=o.cut(box(20,14.2,3.2,x,y,6.9))
# 0.3 mm axial clearance to the service lid bosses starting at 32.6 mm.
o=o.cut(box(100,240,10,144,0,32.3))
changed['O01']=o.removeSplitter()
oc=local('O03')
for x in [128,160]:
 for y in [-75,75]:oc=oc.fuse(box(1.2,12,.3,x,y,36.3))
changed['O03']=oc.removeSplitter()
result=[]
for code,s in changed.items():
 if fast and code!='H01':continue
 assert s.isValid() and len(s.Solids)==1,(code,s.isValid(),len(s.Solids))
 w=s.copy();w.Placement=head.multiply(s.Placement);d.getObject(code).Shape=w
 s.exportStep(str(R/'step'/(code+'.step')))
 t=s.copy()
 if code=='H01':
  t.rotate(V(),V(1,0,0),90);t.rotate(V(),V(0,0,1),-45)
 b=t.BoundBox;t.translate(V(-b.XMin,-b.YMin,-b.ZMin))
 for shape,path in [(t,R/'stl'/(code+'.stl')),(w,R/'preview'/(code+'.stl'))]:
  mesh=MeshPart.meshFromShape(Shape=shape,LinearDeflection=.025 if code=='O01' else .06,AngularDeflection=.08 if code=='O01' else .16,Relative=False)
  clean(mesh);assert mesh.isSolid(),code;mesh.write(str(path))
 result.append({'id':code,'valid':True,'solids':1,'volume_mm3':s.Volume,'print_bounds_mm':[t.BoundBox.XLength,t.BoundBox.YLength,t.BoundBox.ZLength]})
 print('CORRECTED',code,flush=True)
manifest=json.loads((R/'preview/manifest.json').read_text())
# Native CAD groups by intended filament; actual GUI material is set in Blender.
for name,label,predicate in [
 ('Alb','01 PETG ALB',lambda a:a['kind']=='print' and a['id'] not in ['P01','O01','O03'] and not a['id'].startswith('L')),
 ('Negru','02 PETG NEGRU',lambda a:a['kind']=='print' and (a['id'] in ['P01','O01','O03'] or a['id'].startswith('L'))),
 ('Probe','03 PROBE',lambda a:a['kind']=='probe'),('Referinte','04 REFERINTE NU IMPRIMA',lambda a:a['kind']=='reference')]:
 g=d.getObject(name) or d.addObject('App::DocumentObjectGroup',name);g.Label=label
 for a in manifest:
  if predicate(a):g.addObject(d.getObject(a['id']))
d.recompute();d.saveAs(str(R/'cad/Terminal_OPD2203_R10.FCStd'))
# Individual STEP files preserve exact geometry; avoid redundant compound export.
(R/'validation/corrections_R10.json').write_text(json.dumps(result,indent=2))
prod=[a for a in manifest if a['kind']=='print'];coll=[]
for i,a in enumerate(prod):
 sa=d.getObject(a['id']).Shape
 for b in prod[i+1:]:
  if a['id'] not in changed and b['id'] not in changed:continue
  sb=d.getObject(b['id']).Shape
  if not sa.BoundBox.intersect(sb.BoundBox):continue
  volume=sa.common(sb).Volume
  if volume>.05:coll.append({'a':a['id'],'b':b['id'],'mm3':volume})
 print('CHECKED',a['id'],flush=True)
(R/'validation/interferences.json').write_text(json.dumps(coll,indent=2))
(R/'validation/interference_scope.json').write_text(json.dumps({'scope':'H01/O01/O03 versus every production part; unchanged pairs not retested','excluded_pairs':[],'threshold_mm3':.05},indent=2))
# Rear service lid has four bearing pads touching H04, not merely hovering.
contacts=[]
for x in [128,160]:
 for y in [-75,75]:
  pad=box(1.2,12,.3,x,y,36.3);pad.Placement=head.multiply(pad.Placement)
  contacts.append({'x':x,'y':y,'distance_to_H04_mm':pad.distToShape(d.getObject('H04').Shape)[0]})
(R/'validation/cassette_bearing.json').write_text(json.dumps(contacts,indent=2))
print('COLLISIONS',coll,'CONTACTS',contacts,flush=True)
