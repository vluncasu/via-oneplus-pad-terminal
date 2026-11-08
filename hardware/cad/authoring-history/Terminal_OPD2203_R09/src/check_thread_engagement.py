"""R09, single-material printed mechanical prototype. mm. Custom non-ISO threads.
Printed fasteners are experimental, no rated load. Electronics remain real.
"""
import sys,json,csv,math
from pathlib import Path
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A,Part,MeshPart
from mesh_cleanup import clean
V=A.Vector;R=Path(__file__).resolve().parents[1]
for f in ['cad','step','stl','probes','preview','docs','validation']: (R/f).mkdir(exist_ok=True)
P=json.loads((R/'src/parameters.json').read_text())
doc=A.newDocument('Terminal_R09');items=[];checks=[]
def box(w,h,d,x=0,y=0,z=0):return Part.makeBox(w,h,d,V(x-w/2,y-h/2,z))
def cyl(r,h,x=0,y=0,z=0):return Part.makeCylinder(r,h,V(x,y,z))
def rr(w,h,r,d,x=0,y=0,z=0):
 s=box(w,h,d,x,y,z);return s.makeFillet(r,[e for e in s.Edges if abs(e.Vertexes[-1].Point.z-e.Vertexes[0].Point.z)>d-.001])
def ring(w,h,r,t,d,x=0,y=0,z=0):return rr(w,h,r,d,x,y,z).cut(rr(w-2*t,h-2*t,r-t,d+2,x,y,z-1))
def move(s,x=0,y=0,z=0):s=s.copy();s.translate(V(x,y,z));return s
def union(ss):return ss[0].multiFuse(ss[1:]).removeSplitter() if len(ss)>1 else ss[0]
HEAD=A.Placement(V(-12,10,240),A.Rotation(V(1,0,0),120))
def world(s,space):
 s=s.copy()
 if space=='head':s.Placement=HEAD.multiply(s.Placement)
 return s
# Stored frame uses lateral cassette at +X; assemble with this same placement.
def add(code,name,s,space='world',kind='print',orient='flat'):
 s=s.removeSplitter()
 if not s.isValid():s.fix(.01,.001,.1)
 if not s.isValid() or len(s.Solids)!=1:raise ValueError((code,'invalid or multi-solid',s.isValid(),[round(v.Volume,4) for v in s.Solids]))
 o=doc.addObject('PartDesign::Feature',code);o.Label=code+' '+name;o.Shape=world(s,space)
 items.append(dict(id=code,name=name,shape=s,world=o.Shape,space=space,kind=kind,orient=orient));print('BUILT',code,flush=True)
# Coarse rounded helical thread: radius clearance is adjustable via test nuts.
cache={}
def thread(d,L,clear=0):
 key=(d,L,clear)
 if key in cache:return cache[key].copy()
 # A single closed loft avoids unstable helical-ridge/core Boolean unions.
 # Rounded custom helical thread, pitch 2.5mm, radial depth 1mm.
 wires=[];N=48;steps=math.ceil(L/2.5*12);root=d/2-1+clear
 for i in range(steps+1):
  z=L*i/steps;pts=[]
  for j in range(N):
   angle=2*math.pi*j/N
   radius=root+.5*(1+math.cos(2*math.pi*z/2.5-angle))
   pts.append(V(radius*math.cos(angle),radius*math.sin(angle),z))
  wires.append(Part.Wire(Part.makePolygon(pts+[pts[0]]).Edges))
 s=Part.makeLoft(wires,True,False)
 assert s.isValid() and len(s.Solids)==1 and s.Volume>math.pi*root*root*L*.98,(key,'invalid thread')
 cache[key]=s;return s.copy()
def screw(d,L):
 s=thread(d,L).fuse(cyl(d*.78,4,z=-4))
 # Hand slots and a flat top: print head down, axis upright.
 s=s.cut(box(d*1.1,2,1.4,z=-4.01));return s

results=[]
for diameter in [8,12]:
 male=thread(diameter,12);female=thread(diameter,12,.3)
 nut=cyl(diameter/2+3,6,z=3).cut(female)
 assert nut.isValid() and len(nut.Solids)==1
 for deg in [0,90,180,270]:
  moved=male.copy();moved.rotate(V(),V(0,0,1),deg);moved.translate(V(0,0,2.5*deg/360))
  vol=moved.common(nut).Volume
  results.append({'diameter_mm':diameter,'turn_degrees':deg,'advance_mm':2.5*deg/360,'interference_mm3':vol,'pass':vol<.05})
  print(results[-1],flush=True)
(R/'validation/thread_engagement.json').write_text(json.dumps(results,indent=2))
