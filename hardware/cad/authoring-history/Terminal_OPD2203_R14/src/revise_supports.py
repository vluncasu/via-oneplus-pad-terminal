import sys,json
from pathlib import Path
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A,Part,MeshPart
from mesh_cleanup import clean
R=Path(__file__).resolve().parents[1];V=A.Vector
H=A.Placement(V(-12,10,240),A.Rotation(V(1,0,0),120))
d=A.openDocument(str(R.parent/'Terminal_OPD2203_R13/cad/Terminal_OPD2203_R13.FCStd'))
old=A.openDocument(str(R.parent/'Terminal_OPD2203_R11/cad/Terminal_OPD2203_R11.FCStd'))
def local(doc,c):
 s=doc.getObject(c).Shape.copy();s.Placement=H.inverse().multiply(s.Placement);return s
def box(w,h,t,x,y,z):return Part.makeBox(w,h,t,V(x-w/2,y-h/2,z))
def rr(w,h,r,t,x,y,z):
 s=box(w,h,t,x,y,z);return s.makeFillet(r,[e for e in s.Edges if abs(e.Vertexes[-1].Point.z-e.Vertexes[0].Point.z)>t-.001])
def prism(points,vec):return Part.Face(Part.makePolygon([V(*p) for p in points]+[V(*points[0])])).extrude(V(*vec))
def cylinder(rad,height,x,y,z):return Part.makeCylinder(rad,height,V(x,y,z))
h=local(d,'H01');orig_o=local(old,'O01');orig_back=local(old,'H04')
# Restore a continuous front shoulder, film inserted from the rear.
ledge=rr(30.4,198.4,14.8,.7,144,0,-1.3).cut(rr(24.2,192.2,11.7,2,144,0,-2))
h=h.fuse(ledge)
film=rr(25.6,193.6,12.6,.4,144,0,-.6)
# Separate face, flat back on the bed and all decorative relief facing upwards.
face=orig_o.common(rr(26,194,12.8,3.01,144,0,-1.01));face.translate(V(0,0,.8))
# Open carrier: flat front rim on bed, no front roof spanning the cavity.
carrier=rr(26,194,12.8,29.5,144,0,2.8).cut(rr(21.2,189.2,10.4,32,144,0,2.7))
carrier=carrier.cut(box(6,22,11.2,131.8,0,2.8))
for y in [-86,86]:
 # Solid end pedestals support existing threaded bosses throughout the build.
 carrier=carrier.fuse(cylinder(11,15.3,144,y,2.8))
carrier=carrier.fuse(orig_o.common(box(60,220,14.3,144,0,18)))
for y in [-86,86]:
 carrier=carrier.fuse(cylinder(8,.3,144,y,32.3).cut(cylinder(4.6,.5,144,y,32.2)))
# Remove obsolete two front-rail spring receivers, restoring only the old geometry locally.
for x in [-65,65]:
 region=box(10,29,5.2,x,99.5,6.6)
 h=h.cut(region).fuse(local(old,'H01').common(region).cut(box(260.4,21,9,0,104,-1.5)))
# Simple top bar with open, 45-degree side guide keys. No cantilever snap arms.
gate=rr(258.6,17,2,8.3,0,103.1,-1.3)
gate=gate.cut(rr(259.03,190.41,11.5,9,0,0,0)).cut(box(26,4,3,0,94.3,-2))
for sign in [-1,1]:
 key=prism([(sign*127,98,2),(sign*129.3,98,2),(sign*132,98,6),(sign*127,98,6)],(0,12,0))
 gate=gate.fuse(key)
 track=box(6,14,8.8,sign*132.8,105,0)
 # Groove open upwards (Y). Front ramp and rear shoulder constrain Z.
 groove=prism([(sign*126.6,97.7,1.7),(sign*129.6,97.7,1.7),(sign*132.4,97.7,6.3),(sign*126.6,97.7,6.3)],(0,16,0))
 h=h.fuse(track).cut(groove)
for x in [-65,65]:gate=gate.cut(cylinder(2.8,5.4,x,98.5,1.8))
# Rear top hatch uses the two existing upper D8 screws, not tiny added fasteners.
# Straight pins enter blind holes in the top bar and prevent it lifting.
back=local(d,'H04').common(box(400,300,60,12,-74.15,-5)) # upper boundary 75.85
hatch=orig_back.common(box(400,100,60,12,126.15,-5)) # lower boundary 76.15
for x in [-65,65]:hatch=hatch.fuse(cylinder(2.5,30.2,x,98.5,2.1))
parts={'H01':h,'H04':back,'H05':gate,'H06':hatch,'O01':carrier,'O05':film,'O06':face}
names={'H01':'Cap structural cu umar captiv foita si ghidaje sus','H04':'Capac posterior inferior structural','H05':'Traversa superioara culisanta fara snapuri','H06':'Capac posterior superior cu pini integrati de blocare','O01':'Corp caseta optica deschis pentru imprimare plana','O05':'Foita optica plana captiva 0.40 mm','O06':'Fata senzori dummy cu spate plan'}
manifest=json.loads((R/'preview/manifest.json').read_text());report=[]
for c,s in parts.items():
 s=s.removeSplitter()
 if not s.isValid():s.fix(.01,.001,.1)
 assert s.isValid() and len(s.Solids)==1,(c,s.isValid(),len(s.Solids))
 parts[c]=s
 ob=d.getObject(c) or d.addObject('PartDesign::Feature',c);ob.Label=c+' '+names[c]
 w=s.copy();w.Placement=H.multiply(s.Placement);ob.Shape=w
 entry=next((a for a in manifest if a['id']==c),None)
 if entry:entry['name']=names[c]
 else:manifest.append(dict(id=c,name=names[c],kind='print',space='head'))
 s.exportStep(str(R/'step'/(c+'.step')))
 t=s.copy()
 if c in ['H01','H04']:t.rotate(V(),V(1,0,0),90);t.rotate(V(),V(0,0,1),-45)
 elif c in ['H06','O06']:t.rotate(V(),V(1,0,0),180)
 if c in ['H05','H06']:t.rotate(V(),V(0,0,1),45)
 b=t.BoundBox;t.translate(V(-b.XMin,-b.YMin,-b.ZMin))
 for sh,p in [(t,R/'stl'/(c+'.stl')),(w,R/'preview'/(c+'.stl'))]:
  m=MeshPart.meshFromShape(Shape=sh,LinearDeflection=.045,AngularDeflection=.12,Relative=False);clean(m);assert m.isSolid(),c;m.write(str(p))
 report.append(dict(id=c,valid=True,solids=1,print_bounds=[t.BoundBox.XLength,t.BoundBox.YLength,t.BoundBox.ZLength]))
 print('EXPORTED',c,flush=True)
d.recompute();d.saveAs(str(R/'cad/Terminal_OPD2203_R14.FCStd'))
(R/'preview/manifest.json').write_text(json.dumps(manifest,indent=2))
(R/'validation/geometry.json').write_text(json.dumps(report,indent=2))
contacts=[]
for a,b in [('O01','O06'),('O06','O05'),('O05','H01'),('O01','H01'),('O01','O03'),('H05','H01'),('H06','H01'),('H06','H05'),('H06','H04'),('H05','O01'),('H05','O06')]:
 v=d.getObject(a).Shape.common(d.getObject(b).Shape).Volume;contacts.append(dict(a=a,b=b,mm3=v));print('CONTACT',a,b,v,flush=True)
(R/'validation/contacts.json').write_text(json.dumps(contacts,indent=2))
print('DONE',flush=True)
