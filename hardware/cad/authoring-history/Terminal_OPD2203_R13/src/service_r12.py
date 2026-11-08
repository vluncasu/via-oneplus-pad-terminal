import sys,json,csv
from pathlib import Path
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A,Part,MeshPart
from mesh_cleanup import clean
R=Path(__file__).resolve().parents[1];V=A.Vector
H=A.Placement(V(-12,10,240),A.Rotation(V(1,0,0),120))
d=A.openDocument(str(R.parent/'Terminal_OPD2203_R11/cad/Terminal_OPD2203_R11.FCStd'))
def local(c):
 s=d.getObject(c).Shape.copy();s.Placement=H.inverse().multiply(s.Placement);return s
def box(w,h,t,x,y,z):return Part.makeBox(w,h,t,V(x-w/2,y-h/2,z))
def rr(w,h,r,t,x,y,z):
 s=box(w,h,t,x,y,z);return s.makeFillet(r,[e for e in s.Edges if abs(e.Vertexes[-1].Point.z-e.Vertexes[0].Point.z)>t-.001])
def prism(points,vec):return Part.Face(Part.makePolygon([V(*p) for p in points]+[V(*points[0])])).extrude(V(*vec))
h=local('H01');o=local('O01');back=local('H04')
# Upper front rail. LED remains behind z11; tablet travels at z0..6.54.
cut=box(260.4,21,9,0,104,-1.5)
rail=h.common(box(259.8,20.4,8.7,0,104,-1.5))
h=h.cut(cut)
for x,sign in [(-65,-1),(65,1)]:
 # Spring arms lie behind tablet; hooks flex sideways, then relax in windows.
 root=box(7,3.2,3.5,x,111,6.9)
 arm=box(1.2,23,2.8,x,98,7.5)
 hook=prism([(x+sign*.5,86.5,7.5),(x+sign*1.7,88.5,7.5),(x+sign*1.7,90,7.5),(x+sign*.5,90,7.5)],(0,0,2.8))
 rail=rail.fuse(root).fuse(arm).fuse(hook)
 h=h.cut(box(7.6,3.8,4.1,x,111,6.6))
 wall=box(2,18.85,3.5,x+sign*2.1,100.075,7.1)
 h=h.fuse(wall)
 # Access to deflect the two arms through rear lid, hidden from the front.
 back=back.cut(rr(6,10,1,7,x,98,31))
# Make a full swept aperture in the front top rim.
h=h.cut(box(259.5,25,6.9,0,106,0))
# Cassette four integrated cantilevers; shoulders capture the rear of H01 front wall.
for x,sign in [(131,-1),(157,1)]:
 for cy in [-50,50]:
  # Remove a wall panel, retain the upper root, then build the sprung tongue.
  o=o.cut(box(3.4,25,6,x,cy,5.7))
  arm=box(1.2,24,2.8,x-sign*.6,cy,7.3)
  root=box(2.2,3,5.5,x-sign*.7,cy+12,6)
  hook=prism([(x-sign*.2,cy-9,7.3),(x+sign*1.0,cy-9,7.3),(x+sign*1.0,cy-9,8),(x-sign*.2,cy-9,10.1)],(0,6,0))
  o=o.fuse(root).fuse(arm).fuse(hook)
# Film and retaining black rim. Four removable printed pins retain the rim.
film=rr(24.8,192.8,11.8,.2,144,0,-1.7)
bezel=rr(29,197,14,1.2,144,0,-2.2).cut(rr(22.8,190.8,10.8,3,144,0,-3))
bezel=bezel.cut(rr(25.2,193.2,12,1.1,144,0,-1.8))
pins=[]
for x in [133,155]:
 for y in [-70,70]:
  # Cylindrical dowels with a head: calibration press fit, not structural retention.
  o=o.fuse(Part.makeCylinder(2.3,3,V(x,y,-1)))
  o=o.cut(Part.makeCylinder(1.05,3.1,V(x,y,-1.05)))
  bezel=bezel.fuse(Part.makeCylinder(2.1,1.2,V(x,y,-2.2)))
  bezel=bezel.cut(Part.makeCylinder(1.15,2,V(x,y,-2.3)))
  film=film.cut(Part.makeCylinder(2.2,1,V(x,y,-2)))
  pins.append(Part.makeCylinder(1.08,2.5,V(x,y,-2.2)).fuse(Part.makeCylinder(1.7,.5,V(x,y,-2.7))))
# Clearance for the new bezel bosses in the structural frame.
for x in [133,155]:
 for y in [-70,70]:h=h.cut(Part.makeCylinder(2.6,3.4,V(x,y,-1.2)))
# Independent cassette catches act at z7.3: matching relief starts above the shoulder.
for x in [131,157]:
 for cy in [-50,50]:h=h.cut(box(4,26,4.3,x,cy,7.1))
parts={'H01':h,'H04':back,'O01':o,'H05':rail,'O04':bezel,'O05':film}
for i,p in enumerate(pins,1):parts['V7'+str(i)]=p
cache=R/'validation/service_brep';cache.mkdir(exist_ok=True)
for c,s in parts.items():s.exportBrep(str(cache/(c+'.brep')))
names={'H05':'Traversa superioara cu doua cleme ascunse','O04':'Rama captiva foita optica','O05':'Foita optica PETG natural 0.20 mm'}
manifest=json.loads((R/'preview/manifest.json').read_text());report=[]
for c,s in parts.items():
 s=s.removeSplitter()
 if len(s.Solids)!=1:print('SOLIDS',c,[(a.Volume,str(a.BoundBox)) for a in s.Solids],flush=True)
 assert s.isValid() and len(s.Solids)==1,(c,'invalid',len(s.Solids))
 obj=d.getObject(c) or d.addObject('PartDesign::Feature',c)
 if c not in [a['id'] for a in manifest]:
  name=names.get(c,'Stift imprimat rama optica '+c);obj.Label=c+' '+name
  manifest.append(dict(id=c,name=name,kind='print',space='head'))
 w=s.copy();w.Placement=H.multiply(s.Placement);obj.Shape=w
 s.exportStep(str(R/'step'/(c+'.step')))
 t=s.copy()
 if c in ['H01','H04','H05']:t.rotate(V(),V(1,0,0),90);t.rotate(V(),V(0,0,1),-45)
 elif c=='O05':pass
 b=t.BoundBox;t.translate(V(-b.XMin,-b.YMin,-b.ZMin))
 for shape,path in [(t,R/'stl'/(c+'.stl')),(w,R/'preview'/(c+'.stl'))]:
  m=MeshPart.meshFromShape(Shape=shape,LinearDeflection=.045,AngularDeflection=.12,Relative=False);clean(m);assert m.isSolid(),c;m.write(str(path))
 report.append(dict(id=c,valid=True,solids=1,print_bounds=[t.BoundBox.XLength,t.BoundBox.YLength,t.BoundBox.ZLength]))
 print('EXPORTED',c,flush=True)
d.recompute();d.saveAs(str(R/'cad/Terminal_OPD2203_R12.FCStd'))
(R/'preview/manifest.json').write_text(json.dumps(manifest,indent=2))
(R/'validation/service_r12.json').write_text(json.dumps(report,indent=2))
coll=[]
for c in parts:
 for a in manifest:
  b=a['id']
  if a['kind']!='print' or b==c or (b in parts and b<c):continue
  sa=d.getObject(c).Shape;sb=d.getObject(b).Shape
  if not sa.BoundBox.intersect(sb.BoundBox):continue
  v=sa.common(sb).Volume
  if v>.05:coll.append(dict(a=c,b=b,mm3=v))
 print('CHECKED',c,flush=True)
(R/'validation/service_interferences.json').write_text(json.dumps(coll,indent=2));print('COLLISIONS',coll,flush=True)
