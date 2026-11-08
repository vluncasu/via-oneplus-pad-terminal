"""R11, single-material printed mechanical prototype. mm. Custom non-ISO threads.
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
doc=A.newDocument('Terminal_R11');items=[];checks=[]
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
 if getattr(o,'ViewObject',None) is not None:
  o.ViewObject.ShapeColor=(0.035,0.045,0.055) if (code in ['P01','O01','O03'] or code.startswith('L')) else (0.86,0.86,0.84)
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
# Base monobloc, thin integral optical belt and rigid feet.
b=ring(240,230,22,3,26,z=3)
b=b.cut(ring(240.2,230.2,22.1,2.3,3,z=4)) # outside recess leaves 0.8mm optical web
b=b.fuse(ring(240,230,22,10,3,z=0))
b=b.fuse(ring(240,230,22,10,3,z=0)).fuse(ring(226,216,15,2,8.5,z=3)).removeSplitter()
# Rear opening stays within straight portion, far from corner radii.
b=b.cut(box(182,10,15.5,0,-114,13.5))
# Rear aperture bottom ledge, side guides, cartridge top stop belongs to lid.
b=b.fuse(box(188,8,1.5,0,-108,12))
print('BASE led',b.isValid(),b.Volume,len(b.Solids),flush=True)
for x in [-93,93]:b=b.fuse(box(4,11,16,x,-106.5,12))
print('BASE guides',b.isValid(),b.Volume,len(b.Solids),flush=True)
basefast=[(x,y) for x in [-96,96] for y in [-82,82]]
for x,y in basefast:
 boss=cyl(7.5,12,x,y,6)
 b=b.fuse(boss).fuse(box(29,10,3,math.copysign(108,x),y,12).common(rr(240,230,22,4,z=11.5)))
 print('BASE boss',x,y,b.isValid(),b.Volume,flush=True)
for x,y in basefast:
 b=b.removeSplitter().cut(move(thread(8,12,.3),x,y,4))
 print('BASE thread',x,y,b.isValid(),b.Volume,flush=True)
# Four shelves, lid screws accessed after lower cover removal.
lidfast=[(x,y) for x in [-90,90] for y in [-60,60]]
for x,y in lidfast:b=b.fuse(box(34,16,4,math.copysign(101,x),y,19).cut(cyl(4.4,6,x,y,18)))
add('B01','Baza monobloc cu lumina integrata si talpi rigide',b,orient='base')
bottom=rr(219.4,209.4,11.7,3,z=3)
for x,y in basefast:bottom=bottom.cut(cyl(4.4,5,x,y,2)).cut(cyl(11.9,1.1,x,y,2.9))
for x in range(-70,71,14):
 for y in [15,36,57]:bottom=bottom.cut(rr(5,13,2,5,x,y,2))
bars=[]
for cy in [15,36,57]:
 for j in range(-4,5):
  bars.append(box(150,.8,.8,0,cy+j*1.6,3))
  bars.append(box(150,.8,.8,0,cy+j*1.6+.8,4.6))
bottom=bottom.multiFuse(bars).removeSplitter()
# Open-top cable saddles on lower service cover, below the PSU envelope.
for x,y in [(80,-77),(50,-70),(20,-70)]:
 saddle=rr(8,10,2,4,x,y,6).cut(box(10,6,3.2,x,y,6.8))
 bottom=bottom.fuse(saddle)
# No unexplained holes: B03 is retained by V31–V34 and its four visible counterbores.
add('B03','Capac service inferior',bottom,orient='base')
cap=rr(240,230,22,2.7,z=29.3).cut(rr(148,102,14,5,0,-36,28))
hump=rr(156,110,18,26,0,-36,32)
edges=[e for e in hump.Edges if all(abs(v.Point.z-58)<.001 for v in e.Vertexes)]
hump_envelope=hump.makeFillet(5,edges)
hump=hump_envelope.cut(rr(150,104,15,24,0,-36,31))
cap=cap.fuse(hump)
for x in range(-48,49,6):cap=cap.cut(box(3,12,16,x,-89,36))
cap=cap.multiFuse([box(105,.8,.8,0,yy,36+j*1.6+offset).common(hump_envelope) for yy,offset in [(-90.6,0),(-89,.8)] for j in range(10)]).removeSplitter()
tongue=ring(233.4,223.4,18.7,1.5,4,z=25.5).cut(box(200,24,6,0,-108,24.5));cap=cap.fuse(tongue)
cap=cap.fuse(box(184,8,1,0,-106,28.3))
for x,y in lidfast:cap=cap.fuse(cyl(7,6.3,x,y,23)).cut(move(thread(8,10,.3),x,y,19))
rootfast=[(x,y) for x in [-48,48] for y in [-69,-49]]
# Root screws removed: stand is integral with lid.
cap=cap.cut(rr(30,24,4,16,0,-61,42))
add('B07','Capac superior cu volum sursa si prinderi de jos',cap,orient='base')
# Monolithic dummy bank, white same material; dark appearance needs finishing.
p=box(180,12,15.3,0,-107.5,13.7)
# hollow sockets point toward rear; blind walls remain inside.
def mouth(w,h,x,rounding=False):
 s=rr(w,h,min(h/2-.01,1.7),10,x,22,0) if rounding else box(w,h,10,x,22,0)
 s.rotate(V(0,0,0),V(1,0,0),90);s.translate(V(0,-103.5,0));return s
# construct apertures directly in XZ with back depth to Y.
def aperture(w,h,x,r=0):
 s=rr(w,h,r,10.3,x,21,0) if r else box(w,h,10.3,x,21,0)
 s.rotate(V(0,0,0),V(1,0,0),90);s.translate(V(0,-103.4,0));return s
for x in [-72,-50,-28]:
 p=p.cut(aperture(13,5.8,x,.7));p=p.fuse(box(10,8,.9,x,-107.3,20.2))
 for j in range(4):p=p.fuse(box(.7,5,.4,x-2.7+j*1.8,-106,21))
for x in [-8,8]:
 p=p.cut(aperture(9,3.8,x,1.8));p=p.fuse(box(6.4,8,.8,x,-107.3,20.6))
p=p.cut(aperture(14,10.5,30)).cut(aperture(6,12.5,30))
for j in range(8):p=p.fuse(box(.65,4,1,26.15+j*1.1,-105,16))
p=p.cut(aperture(14,5.8,54,.5)).fuse(box(10,8,.8,54,-107.3,20.4))
# Cable funnel: smallest opening outside, widens toward electronics; 2mm wall.
fr=P['funnel_outer_throat_radius_mm'];fb=P['funnel_outer_inner_radius_mm'];fw=P['funnel_wall_mm'];fl=P['funnel_length_mm']
outer=Part.makeCone(fr,fb,fl,V(80,-113.5,21),V(0,1,0))
inner=Part.makeCone(fr-fw,fb-fw,fl+.2,V(80,-113.6,21),V(0,1,0))
p=p.fuse(outer).cut(inner)
add('P01','Bloc unic porturi dummy cu palnie cablu',p,orient='ports')
# Clearance envelope including flare, while preserving side guides and lower ledge.
clear=box(180.6,12.6,15.9,0,-107.5,13.4).fuse(Part.makeCone(fr+.3,fb+.3,fl+.6,V(80,-113.8,21),V(0,1,0)))
for code in ['B01','B07']:
 it=next(a for a in items if a['id']==code)
 it['shape']=it['shape'].cut(clear).removeSplitter()
 if not it['shape'].isValid():it['shape'].fix(.01,.001,.1)
 it['world']=it['shape'].copy();doc.getObject(code).Shape=it['world']

# S monobloc, solid designed section with explicit support-friendly channel.
def bez(t):
 u=1-t; k=[u**3,3*u*u*t,3*u*t*t,t**3];pts=[(-61,58),(-104,98),(25,135),(-8,220)]
 return tuple(sum(k[i]*pts[i][j] for i in range(4)) for j in [0,1])
def ribbon(w,x,length):
 ps=[bez(i/40) for i in range(41)];a=[V(x,y-w/2,z) for y,z in ps];b=[V(x,y+w/2,z) for y,z in reversed(ps)]
 ca=Part.BSplineCurve();ca.interpolate(a);cb=Part.BSplineCurve();cb.interpolate(b)
 return Part.Face(Part.Wire([ca.toShape(),Part.makeLine(a[-1],b[0]),cb.toShape(),Part.makeLine(b[-1],a[0])])).extrude(V(length,0,0))
# Original straight-sided constant-width S, without intermediate foot.
leg=ribbon(28,-70,140)
# No external flange: printed sockets are contained directly in the S body.
print('LEG before duct',leg.isValid(),flush=True)
# 30mm-wide passage, 24mm high at centre, bevelled roof for printing.
channels=[]
for i in range(-15,15):
 roof=min(12,18-abs(i+.5));height=roof+12
 channels.append(move(ribbon(height,i,1.01),0,(roof-12)/2,0))
duct=union(channels)
leg=leg.cut(duct).cut(rr(30,24,4,2,0,-61,56)).cut(world(rr(30,30,5,18.5,12,-30,20),'head'))
print('LEG after duct',leg.isValid(),flush=True)
leg=leg.cut(world(box(400,400,66.3,0,0,-30),'head'))
print('LEG after trim',leg.isValid(),flush=True)
# Round the long outer side edges of the ribbon, preserving the flat mating face.
try:
 edges=[e for e in leg.Edges if e.Length>60 and all(abs(abs(v.Point.x)-70)<.01 for v in e.Vertexes) and isinstance(e.Curve,Part.BSplineCurve)]
 leg=leg.makeFillet(2,edges) if edges else leg
except Exception as exc:print('Side round deferred',str(exc),flush=True)
leg=leg.removeSplitter()
leg.exportStep(str(R/'validation/leg_before_thread.step'))
print('LEG after base threads',leg.isValid(),flush=True)
headfast=[(x,-36) for x in [-42,-12,36,66]]
for x,y in headfast:
 leg=leg.cut(world(move(thread(12,12,.35),x,y,32.3),'head'),.01).removeSplitter()
 if not leg.isValid():leg.fix(.01,.001,.1)
print('LEG after head threads',leg.isValid(),flush=True)
leg.exportStep(str(R/'validation/leg_debug.step'))
it=next(a for a in items if a['id']=='B07')
combined=it['shape'].fuse(leg).cut(duct).cut(rr(30,24,4,16,0,-61,42))
combined=combined.cut(rr(150,104,15,24,0,-36,31)).removeSplitter()
# Slim 4mm X braces on both sides of PSU; lower tips land in shell walls.
for x in [-62,62]:
 for ya,yb in [(-89,-56),(17,-76)]:
  start=V(x,ya,33);end=V(x,yb,63);direction=end-start
  rib=Part.makeCylinder(2,direction.Length,start,direction).common(hump_envelope.fuse(leg))
  combined=combined.fuse(rib)
combined=combined.removeSplitter()
if not combined.isValid():combined.fix(.01,.001,.1)
assert combined.isValid() and len(combined.Solids)==1
it['shape']=combined;it['world']=combined.copy();it['orient']='integral';it['name']='Capac sursa si picior S integrate monobloc';doc.getObject('B07').Shape=combined;doc.getObject('B07').Label='B07 '+it['name']
# Integrated head: frame, structural wall and light web, no separate diffuser.
tw,th=258.03,189.41
h=rr(310,224,18,33.3,12,0,-1.3)
h=h.cut(rr(tw+1,th+1,11.5,10,0,0,0)).cut(rr(tw-1.2,th-1.2,10.4,3,0,0,-2))
h=h.cut(rr(304,218,15,27,12,0,7))
# Continuous thin optical belt at local Z12..15, wall from .8 to3 elsewhere.
h=h.cut(ring(310.2,224.2,18.1,2.3,3,12,0,12))
h=h.fuse(ring(310,224,18,9,2.2,12,0,8.8)).fuse(ring(296,210,11,2,8.5,12,0,11))
# Integral retention ledge for the black optical insert. The optical mask is
# separate only because it is printed in black; it seats against H01.
h=h.fuse(ring(297.4,211.4,11.7,1.0,1.1,12,0,20.0)).removeSplitter()
# Side bridges close the last half-millimetre to the carrier while staying
# outside the optical ring; this keeps H01 a single printable solid.
h=h.fuse(box(3,8,.5,-135,0,19.5)).fuse(box(3,8,.5,159,0,19.5)).removeSplitter()
# Camera front notch on both long edges accommodates tablet rotated 180 degrees.
for y in [-94.3,94.3]:h=h.cut(box(26,4,3,0,y,-2))
# Real USB-C opening from the tablet edge into the optical service cassette.
h=h.cut(box(8,24,14,131,0,0))
# The optical cassette is independent service part.
h=h.cut(rr(26.6,194.6,12.9,40,144,0,-2)).cut(rr(30.4,198.4,14.8,1.4,144,0,-1.4))
# Hidden key pockets capture matching tabs on the optical cassette.
# Legacy reliefs retained, but no obstructing lateral keys on the cassette.
for x in [128,160]:
 for y in [-50,50]: h=h.cut(box(8,14,4,x,y,6.8))
coverfast=[(x,y) for x in [-96,120] for y in [-86,86]]
for x,y in coverfast:
 h=h.fuse(cyl(6.7,25,x,y,7)).fuse(box(12,30,2,x,math.copysign(99,y),7).common(rr(310,224,18,2,12,0,7)))
 # Broad rear bridge above the LED strip; its two sides share the boss load.
 h=h.fuse(box(22,26,4,x,math.copysign(99,y),23).common(rr(310,224,18,4,12,0,23)))
for x in [-48,-18,12,42,72]:
 for y in [-110,110]:h=h.cut(box(14,8,3,x,y,24))
# Micro-louvres integral with the side walls, two extrusion lines nominal.
grids=[]
for cx in [-48,-18,12,42,72]:
 for side in [-1,1]:
  for depth,offset in [(111.6,0),(110,.8)]:
   for dx in [-5.6,-4,-2.4,-.8,.8,2.4,4,5.6]:grids.append(box(.8,.8,3.4,cx+dx+offset,side*depth,23.8))
h=h.multiFuse(grids).removeSplitter()
# LED lead exit next to a corner, only above the full-width PCB support.
h=h.cut(box(8,7,3,-124,99,19))
add('H01','Cap monobloc rama structura si zona luminoasa',h,'head',orient='head')
back=rr(309.4,223.4,17.7,4,12,0,32.3)
for x,y in coverfast:
 back=back.fuse(cyl(8,4,x,y,28.3)).cut(cyl(4.4,10,x,y,27.3)).cut(cyl(6.55,4.2,x,y,32.3))
back=back.cut(rr(30.6,198.6,14,7,144,0,31))
for x,y in headfast:back=back.cut(cyl(6.4,6,x,y,31.3))
back=back.cut(rr(30,44,5,6,12,-30,31.3))
# Solid flange contact: rear lid carries load, ribs are integral.
for x in [-56,80]:back=back.fuse(box(6,130,6,x,-20,26.3))
# Rigid depth stops; no bending preload applied to tablet.
for x in [-75,75]:
 for y in [-85,85]:back=back.fuse(box(14,10,25.4,x,y,6.9))
for x in range(-96,121,6):
 for y in [-65,65]:back=back.cut(rr(3,18,1.4,6,x,y,31.3))
grids=[]
for cy in [-65,65]:
 for j in range(-6,6):
  grids.append(box(220,.8,.8,12,cy+j*1.6,35.5))
  grids.append(box(220,.8,.8,12,cy+j*1.6+.8,33.9))
back=back.multiFuse(grids).removeSplitter()
# Open underside wire groove through the right structural rib.
back=back.cut(box(8,14,5.2,80,0,26.1))
for x,y in [(40,-20),(106,0),(-40,85)]:
 guide=rr(10,8,2,6,x,y,26.3).cut(box(6,10,4.6,x,y,26.2))
 back=back.fuse(guide)
add('H04','Capac structural posterior cu opritoare tableta',back,'head',orient='head')
# One-piece optical face; all false rings and sensor forms molded in same part.
o=rr(26,194,12.8,3,144,0,-1).fuse(rr(29.8,197.8,14.5,1,144,0,-1))
o=o.fuse(ring(26,194,12.8,1.8,30,144,0,2))
# Bridge for USB-C side passage, no opaque wall over the plug.
o=o.cut(box(5,22,12,131.8,0,0))
for y,rad in [(-62,8),(-35,5),(32,5),(63,8)]:
 o=o.cut(cyl(rad,1.3,144,y,-1.05)).fuse(cyl(rad*.45,.9,144,y,-.65))
 for rr0 in [rad*.7]:o=o.cut(cyl(rr0,.3,144,y,-.7).cut(cyl(rr0-.65,.5,144,y,-.8)))
for x in [141,144,147]:
 for y in [-12,-8,-4]:o=o.cut(cyl(.7,.7,x,y,-1.05))
# Concentric lens barrels, rectangular sensor matrix, calibration ticks and aperture slots.
for cy,rad in [(-62,8),(-35,5),(32,5),(63,8)]:
 for radius in [rad*.9,rad*.55]:
  o=o.cut(cyl(radius,.45,144,cy,-.98).cut(cyl(radius-.55,.65,144,cy,-1.08)))
 for k in range(12):
  ang=k*math.pi/6
  o=o.cut(cyl(.3,.4,144+(rad+.9)*math.cos(ang),cy+(rad+.9)*math.sin(ang),-1.01))
for cy in [8,18]:
 o=o.cut(rr(13,5,1,.65,144,cy,-1.01))
 for dx in [-4,-2,0,2,4]:o=o.fuse(box(.8,3,.5,144+dx,cy,-.8))
for cy in [-78,-48,-23,45,79]:o=o.cut(rr(8,1.2,.5,.5,144,cy,-1.01))
for y in [-86,86]:o=o.fuse(cyl(10,12.7,144,y,19.3))
# Reinforced bosses and anti-drop side keys, all part of O01.
for y in [-86,86]:
 o=o.fuse(cyl(11,14.3,144,y,18)).fuse(box(22,10,4,144,y,20))
add('O01','Masca si caseta optica monobloc cu senzori dummy',o,'head',orient='headsmall')
oc=rr(34.6,202.6,16.5,3,144,0,36.6)
for y in [-86,86]:oc=oc.fuse(cyl(8,4,144,y,32.6)).cut(cyl(4.4,9,144,y,31.6)).cut(cyl(6.55,4.2,144,y,35.6))
for x in [128,160]:
 for y in [-75,75]:oc=oc.fuse(box(1.2,12,.3,x,y,36.3))
add('O03','Capac service USB al casetei optice',oc,'head',orient='headsmall')
# Printed threaded hardware is represented in correct assembly positions.
# No V11-V14: joint is one printed solid.
for i,(x,y) in enumerate(headfast,1):add('V2'+str(i),'Surub imprimat D12 P2.5 L12 cap',move(screw(12,12),x,y,32.3),'head')
def foot_screw():
 dome=Part.makeSphere(12,V(0,0,3)).common(box(30,30,8,z=-8))
 return thread(8,12).fuse(dome).cut(box(8,2,1.5,z=-8.01))
for i,(x,y) in enumerate(basefast,1):add('V3'+str(i),'Picior sferic insurubabil D8 cu fanta',move(foot_screw(),x,y,4))
for i,(x,y) in enumerate(lidfast,1):add('V4'+str(i),'Surub imprimat D8 P2.5 L10 capac baza',move(screw(8,10),x,y,19))
# Cover screws enter toward front: reflect shaft about the head-bearing plane.
def reversebolt(d,L,z,x,y):
 s=screw(d,L);s.rotate(V(0,0,0),V(1,0,0),180);return move(s,x,y,z)
# female threads above were defined forward from22.3; reverse bolt phase differs!
# Use female cuts derived from actual reverse screw, preserving handedness and assembly.
for target,positions,z in [('H04',coverfast,32.3),('O03',[(144,-86),(144,86)],35.6)]:
 parent='H01' if target=='H04' else 'O01';it=next(a for a in items if a['id']==parent)
 # Clearance for recessed-head bearing bosses on structural rear lid.
 if target=='H04':
  for x,y in positions:it['shape']=it['shape'].cut(cyl(8.3,4.4,x,y,28))
 # Cut with actual reversed thread and its clearance.
 for x,y in positions:
  tool=thread(8,14 if target=='H04' else 16.3,.3);tool.rotate(V(0,0,0),V(1,0,0),180);tool=move(tool,x,y,z)
  it['shape']=it['shape'].cut(tool,.01)
  if not it['shape'].isValid():it['shape'].fix(.01,.001,.1)
 it['shape']=it['shape'].removeSplitter();it['world']=world(it['shape'],'head');doc.getObject(parent).Shape=it['world']
 for i,(x,y) in enumerate(positions,1):add(('V5' if target=='H04' else 'V6')+str(i),'Surub imprimat capac posterior',reversebolt(8,14 if target=='H04' else 16.3,z,x,y),'head')
# Black printed light shields: mask both sides of the 3mm transmission line.
# Small connecting web at least exposed edge, clipped to actual surrounding solids.
for prefix,parent,w,hh,radius,cx,z0,z1,slit0 in [('L1','B01',233.6,223.6,18.8,0,3,13,4),('L2','H01',303.6,217.6,14.8,12,11,20,12)]:
 shield=ring(w,hh,radius,.8,z1-z0,cx,0,z0)
 shield=shield.cut(ring(w+.2,hh+.2,radius+.1,1.2,3,cx,0,slit0))
 shield=shield.fuse(box(1.2,.8,5,cx,hh/2-.4,slit0-1))
 space='world' if parent=='B01' else 'head'
 for it0 in items:
  if it0['space']==space and it0['id'] in ['B01','B07','P01','H01','H04','O01','O03']:shield=shield.cut(it0['shape'])
 shield=shield.removeSplitter()
 parent_it=next(a for a in items if a['id']==parent)
 bw,bh,br=(235,225,19.5) if parent=='B01' else (305,219,15.5)
 bands=[(3,1),(7,6)] if parent=='B01' else [(11,1),(15,5)]
 bridges=union([ring(bw,bh,br,1.4,depth,cx,0,z) for z,depth in bands])
 for other in items:
  if other['kind']=='print' and other['space']==space and other['id']!=parent:
   if bridges.BoundBox.intersect(other['shape'].BoundBox):bridges=bridges.cut(other['shape'])
 merged=parent_it['shape'].fuse(shield).fuse(bridges).removeSplitter()
 assert merged.isValid() and len(merged.Solids)==1,(parent,'LED integration disconnected')
 parent_it['shape']=merged;parent_it['world']=world(merged,space);doc.getObject(parent).Shape=parent_it['world']

# Tablet and source are envelopes, not supplied printed electronics.
add('R01','Tableta OPD2203 referinta',rr(tw,th,11,6.54),'head','reference')
add('R02','Sursa rezerva dimensionala',box(92,64.02,39.02,0,-24,11),kind='reference')
add('R03','Rezerva mufa cotita 16x30x10 de masurat',box(16,30,10,142.5,0,3).fuse(box(6.5,8,2.5,131.75,0,2)),'head','reference')
add('R04','Gabarit continuu banda LED baza 8.5mm',ring(229,219,16.5,1.5,8.5,z=3),kind='reference')
add('R05','Gabarit continuu banda LED cap 8.5mm',ring(299,213,12.5,1.5,8.5,12,0,11),'head','reference')
# Economical prototypes.
add('Q12','Gabarit mufa USB 16x10x30 de tras prin canal',rr(16,10,2,30).cut(cyl(1.5,32,z=-1)),kind='probe')
add('Q01','Surub proba D12 pas2.5',screw(12,12),kind='probe')
for i,c in enumerate([.25,.35,.45],2):add('Q0'+str(i),'Piulita proba joc '+str(c),cyl(10,10).cut(thread(12,12,c)),kind='probe')
add('Q05','Surub proba D8 pas2.5',screw(8,10),kind='probe')
add('Q06','Piulita proba D8 joc0.3',cyl(7,8).cut(thread(8,10,.3)),kind='probe')
# Actual front corner, negligible compared to whole housing; dimensional survey still needed.
q=next(a['shape'] for a in items if a['id']=='H01').common(box(30,30,9,-125,-95,-1.3))
add('Q07','Microcolt integrare tableta',q,kind='probe')
add('Q11','Proba degajare camera frontala',next(a['shape'] for a in items if a['id']=='H01').common(box(40,23,8.3,0,101.5,-1.3)),kind='probe')
# Thin light transmission coupon.
for i,t in enumerate([.6,.8,1.0],8):add('Q'+str(i).zfill(2),'Proba transmisie perete '+str(t),box(25,15,t),kind='probe')
# Minimal full-span gauges: the long width gauge is diagonal on the plate.
for code,span in [('Q13',259.03),('Q14',190.41)]:
 gauge=box(span+8,6,3)
 for xx in [-span/2-2,span/2+2]:gauge=gauge.fuse(box(4,16,8,xx,0,3))
 add(code,'Calibru deschidere '+str(span)+' mm',gauge,kind='probe',orient='gauge')
corner=next(a['shape'] for a in items if a['id']=='B01').common(box(34,24,14,108,-103,0)).removeSplitter()
add('Q15','Proba colt canal LED real 8.5mm',corner,kind='probe')
# Hidden markings only on internal mating faces.
from hidden_marks import mark
marks=[]
for it in items:
 axes={'B01':(0,0,1),'B03':(0,0,1),'B07':(0,0,-1),'S01':(0,0,-1),'H01':(0,0,1),'H04':(0,0,-1),'O01':(0,0,1),'O03':(0,0,-1),'P01':(0,1,0)}
 if it['id'] not in axes:continue
 it['shape'],record=mark(it['shape'],it['id'],axes[it['id']])
 if record:marks.append(record)
 it['world']=world(it['shape'],it['space']);doc.getObject(it['id']).Shape=it['world']
(R/'docs/hidden_marks.json').write_text(json.dumps(marks,indent=2))
# Export all local printable meshes and assembly meshes; no silently retained R06 files.
rows=[];manifest=[]
for it in items:
 s=it['shape']
 if not s.isValid():s.fix(.01,.001,.1)
 t=s.copy();code=it['id'];ori=it['orient']
 if ori=='gauge':t.rotate(V(0,0,0),V(0,0,1),45)
 elif ori in ['head','base']:
  t.rotate(V(0,0,0),V(1,0,0),90);t.rotate(V(0,0,0),V(0,0,1),-45)
 elif ori=='stand':t.rotate(V(0,0,0),V(0,1,0),90)
 elif ori=='ports':t.rotate(V(0,0,0),V(1,0,0),-90)
 elif code.startswith('V5') or code.startswith('V6'):t.rotate(V(0,0,0),V(1,0,0),180)
 bb=t.BoundBox;t.translate(V(-bb.XMin,-bb.YMin,-bb.ZMin));bb=t.BoundBox
 m=MeshPart.meshFromShape(Shape=t,LinearDeflection=.025 if code=='O01' else .06,AngularDeflection=.08 if code=='O01' else .16,Relative=False);clean(m)
 folder='probes' if it['kind']=='probe' else 'stl';m.write(str(R/folder/(code+'.stl')));s.exportStep(str(R/'step'/(code+'.step')))
 wm=MeshPart.meshFromShape(Shape=it['world'],LinearDeflection=.1,AngularDeflection=.2,Relative=False);clean(wm);wm.write(str(R/'preview'/(code+'.stl')))
 checks.append(dict(id=code,valid=s.isValid(),solids=len(s.Solids),mesh_solid=m.isSolid(),fits=max(bb.XLength,bb.YLength,bb.ZLength)<=256,xyz=[bb.XLength,bb.YLength,bb.ZLength]))
 rows.append(dict(ID=code,Denumire=it['name'],Material='PETG_NEGRU' if (code in ['P01','O01','O03'] or code.startswith('L')) else 'PETG_ALB',Tip='reference' if it['kind']=='reference' else 'print',Volum_cm3=round(s.Volume/1000,3),Solide=len(s.Solids),X_print_mm=round(bb.XLength,2),Y_print_mm=round(bb.YLength,2),Z_print_mm=round(bb.ZLength,2),Orientare=ori,Note='PROTOTIP; suporturi si rezistenta nevalidate'))
 manifest.append(dict(id=code,name=it['name'],kind=it['kind'],space=it['space']))
 print('EXPORTED',code,flush=True)
doc.recompute();doc.saveAs(str(R/'cad/Terminal_OPD2203_R11.FCStd'))
Part.makeCompound([it['world'] for it in items if it['kind']!='probe']).exportStep(str(R/'step/Terminal_OPD2203_R11_assembly.step'))
with open(R/'docs/piese_si_imprimare.csv','w') as f:w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
(R/'preview/manifest.json').write_text(json.dumps(manifest,indent=2));(R/'validation/checks.json').write_text(json.dumps(checks,indent=2))
coll=[]
prod=[a for a in items if a['kind']=='print']
for n,a in enumerate(prod):
 for b0 in prod[n+1:]:
  if not a['world'].BoundBox.intersect(b0['world'].BoundBox):continue
  v=a['world'].common(b0['world']).Volume
  if v>.05:coll.append(dict(a=a['id'],b=b0['id'],mm3=v))
(R/'validation/interferences.json').write_text(json.dumps(coll,indent=2));print('DONE',len(items),'collisions',len(coll),flush=True)
