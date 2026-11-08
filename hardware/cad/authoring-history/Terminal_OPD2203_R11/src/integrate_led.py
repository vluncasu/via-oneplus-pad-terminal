"""Integrate both optical baffles into their structural parent, with real bridges."""
import sys,json,csv
from pathlib import Path
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A,Part,MeshPart
from mesh_cleanup import clean
R=Path(__file__).resolve().parents[1];V=A.Vector
d=A.openDocument(str(R.parent/'Terminal_OPD2203_R10/cad/Terminal_OPD2203_R10.FCStd'))
head=A.Placement(V(-12,10,240),A.Rotation(V(1,0,0),120))
def local(code,space):
 s=d.getObject(code).Shape.copy()
 if space=='head':s.Placement=head.inverse().multiply(s.Placement)
 return s
def world(s,space):
 s=s.copy()
 if space=='head':s.Placement=head.multiply(s.Placement)
 return s
def rr(w,h,r,z,depth,cx=0):
 s=Part.makeBox(w,h,depth,V(cx-w/2,-h/2,z))
 return s.makeFillet(r,[e for e in s.Edges if abs(e.Vertexes[-1].Point.z-e.Vertexes[0].Point.z)>depth-.001])
def ring(w,h,r,t,z,depth,cx=0):return rr(w,h,r,z,depth,cx).cut(rr(w-2*t,h-2*t,r-t,z-1,depth+2,cx))
manifest=json.loads((R/'preview/manifest.json').read_text());reports=[]
for parent,mask,space,w,h,r,cx,bands in [
 ('B01','L11','world',235,225,19.5,0,[(3,1),(7,6)]),
 ('H01','L21','head',305,219,15.5,12,[(11,1),(15,5)])]:
 original=local(parent,space);shield=local(mask,space)
 bridges=ring(w,h,r,1.4,bands[0][0],bands[0][1],cx).fuse(ring(w,h,r,1.4,bands[1][0],bands[1][1],cx))
 # Preserve every mating clearance; no bonds through another assembly part.
 for a in manifest:
  if a['kind']=='print' and a['id'] not in [parent,mask] and a['space']==space:
   other=local(a['id'],space)
   if bridges.BoundBox.intersect(other.BoundBox):bridges=bridges.cut(other)
 s=original.fuse(shield).fuse(bridges).removeSplitter()
 assert s.isValid() and len(s.Solids)==1,(parent,'not a connected printable solid',len(s.Solids))
 led=local('R04' if parent=='B01' else 'R05',space)
 intrusion=s.common(led).Volume;assert intrusion<.05,(parent,'LED obstructed',intrusion)
 wshape=world(s,space);d.getObject(parent).Shape=wshape
 s.exportStep(str(R/'step'/(parent+'.step')))
 t=s.copy();t.rotate(V(),V(1,0,0),90);t.rotate(V(),V(0,0,1),-45)
 b=t.BoundBox;t.translate(V(-b.XMin,-b.YMin,-b.ZMin));b=t.BoundBox
 for shape,path in [(t,R/'stl'/(parent+'.stl')),(wshape,R/'preview'/(parent+'.stl'))]:
  m=MeshPart.meshFromShape(Shape=shape,LinearDeflection=.06,AngularDeflection=.16,Relative=False);clean(m)
  assert m.isSolid(),parent;m.write(str(path))
 reports.append({'id':parent,'valid':True,'solids':len(s.Solids),'LED_interference_mm3':intrusion,'integrated_baffle':mask,'volume_mm3':s.Volume,'print_bounds':[b.XLength,b.YLength,b.ZLength]})
 print('INTEGRATED',parent,mask,flush=True)
for mask in ['L11','L21']:d.removeObject(mask)
d.recompute();d.saveAs(str(R/'cad/Terminal_OPD2203_R11.FCStd'))
manifest=[a for a in manifest if a['id'] not in ['L11','L21']]
(R/'preview/manifest.json').write_text(json.dumps(manifest,indent=2))
rows=list(csv.DictReader(open(R/'docs/piese_si_imprimare.csv')))
rows=[a for a in rows if a['ID'] not in ['L11','L21']]
for row in rows:
 for a in reports:
  if row['ID']==a['id']:
   row['Volum_cm3']=round(a['volume_mm3']/1000,3)
   for key,value in zip(['X_print_mm','Y_print_mm','Z_print_mm'],a['print_bounds']):row[key]=round(value,2)
with open(R/'docs/piese_si_imprimare.csv','w',newline='') as f:
 wri=csv.DictWriter(f,fieldnames=rows[0].keys());wri.writeheader();wri.writerows(rows)
(R/'validation/led_integrat.json').write_text(json.dumps(reports,indent=2))
coll=[]
for parent in ['B01','H01']:
 s=d.getObject(parent).Shape
 for a in manifest:
  if a['kind']!='print' or a['id']==parent:continue
  other=d.getObject(a['id']).Shape
  if not s.BoundBox.intersect(other.BoundBox):continue
  v=s.common(other).Volume
  if v>.05:coll.append({'a':parent,'b':a['id'],'mm3':v})
 print('CHECKED',parent,flush=True)
(R/'validation/interferences.json').write_text(json.dumps(coll,indent=2))
print('RESULT',coll,flush=True)
