"""FreeCAD/OCC parametric terminal. Units mm. Run with FreeCAD bundled Python.
Edit parameters.json, then regenerate; FCStd contains named inspectable BReps.
No manufacturer's unprovided component geometry is implied to be measured.
"""
import sys, os, json, math, csv, traceback
from pathlib import Path
if sys.platform == 'darwin':
    sys.path.insert(0, '/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A
import Part, Mesh, MeshPart
V=A.Vector
ROOT=Path(__file__).resolve().parents[1]
P=json.loads((ROOT/'src/parameters.json').read_text())
for sub in ['cad','step','stl','probes','drawings','docs','validation','preview']:
    (ROOT/sub).mkdir(exist_ok=True)
doc=A.newDocument('Terminal_OPD2203_R06')
items=[]; probes=[]; checks=[]

def box(w,h,d,x=0,y=0,z=0):
    return Part.makeBox(w,h,d,V(x-w/2,y-h/2,z))
def cyl(r,h,x=0,y=0,z=0):
    return Part.makeCylinder(r,h,V(x,y,z))
def rr(w,h,r,d,x=0,y=0,z=0):
    # True analytic tangent arcs; fillet only vertical edges.
    s=box(w,h,d,x,y,z)
    edges=[e for e in s.Edges if abs(e.Vertexes[-1].Point.z-e.Vertexes[0].Point.z)>d-.001]
    return s.makeFillet(min(r,min(w,h)/2-.001),edges)
def ring(w,h,r,wall,d,x=0,y=0,z=0):
    return rr(w,h,r,d,x,y,z).cut(rr(w-2*wall,h-2*wall,r-wall,d+2,x,y,z-1))
def fuse(shapes):
    return shapes[0].multiFuse(shapes[1:]).removeSplitter() if len(shapes)>1 else shapes[0]
def cut(shape,tools):
    return shape.cut(Part.makeCompound(tools)).removeSplitter() if tools else shape
def moved(s,vec):
    t=s.copy(); t.translate(V(*vec)); return t
HEAD=A.Placement(V(-P['head_cx'],P['head_origin_y'],P['head_origin_z']),A.Rotation(V(1,0,0),180-P['head_angle_deg']))
def world(s,space):
    t=s.copy()
    if space=='head': t.Placement=HEAD.multiply(t.Placement)
    return t
COL={'ASA':(.84,.82,.77),'PETG':(.70,.70,.68),'BLACK':(.012,.025,.042),'TPU':(.06,.06,.06),'DIFF':(1,.71,.33),'PMMA':(.16,.20,.24),'REF':(.15,.25,.3),'PCB':(.05,.20,.10)}
def add(code,name,s,mat='ASA',space='head',kind='print',note=''):
    s=s.removeSplitter()
    if not s.isValid() or not s.Solids: raise ValueError('Invalid shape '+code)
    obj=doc.addObject('PartDesign::Feature',code)
    obj.Label=code+' — '+name; obj.Shape=world(s,space)
    for prop,val in [('Material',mat),('Status','PROTOTIP — masuratori necesare'),('LocalFrame',space),('Notes',note)]:
        obj.addProperty('App::PropertyString',prop,'Design'); setattr(obj,prop,val)
    it={'id':code,'name':name,'shape':s,'world':obj.Shape,'mat':mat,'space':space,'kind':kind,'obj':obj,'note':note}
    items.append(it); print('BUILT',code,flush=True); return s
def check(name,ok,detail): checks.append({'check':name,'pass':bool(ok),'detail':detail})
def hx(x,y,z,h=8,r=4.2):
    pts=[V(x+r*math.cos(i*math.pi/3),y+r*math.sin(i*math.pi/3),z) for i in range(6)]
    return Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(V(0,0,h))

# BASE: plate underneath, light ring at 9…12, upper box and local raised root.
bw,bd,br=P['base_w'],P['base_d'],P['base_r']
base=rr(bw,bd,br,20,z=12).cut(rr(bw-6,bd-6,br-3,20,z=11))
# Above subtraction intentionally leaves top roof 1 mm, then reinforce to 3 mm.
base=base.fuse(rr(bw,bd,br,3,z=29))
base=base.fuse(ring(bw-14,bd-14,br-7,2,7,z=7))
base=base.fuse(ring(bw,bd,br,9,2,z=14))
base=base.cut(ring(bw-.1,bd-.1,br-.05,1.7,2,z=12))
# Continuous rising saddle, lofted smoothly out of the base deck.
def loft_sections(spec):
    wires=[]
    for w,h,r,y,z in spec:
        sh=rr(w,h,r,1,0,y,z)
        face=min(sh.Faces,key=lambda f:abs(f.CenterOfMass.z-z))
        wires.append(face.OuterWire)
    return Part.makeLoft(wires,True,False)
# Last sections follow the exact S centreline, eliminating a pedestal lip.
def root_y(z):
    lo,hi=0.,1.
    for _ in range(45):
        t=(lo+hi)/2; u=1-t
        zz=u**3*58+3*u*u*t*98+3*u*t*t*135+t**3*198
        if zz<z:lo=t
        else:hi=t
    t=(lo+hi)/2;u=1-t
    return u**3*-61+3*u*u*t*-104+3*u*t*t*25+t**3*-8
root_sections=[(194,146,25,-27,29),(188,136,24,-29,32),(163,94,18,-39,43),(144,49,4,-59,65),(140,24,.15,root_y(86),86)]
hump_outer=loft_sections(root_sections)
hump_inner=loft_sections([(w-6,h-6,max(.1,r-3),y,z) for w,h,r,y,z in root_sections])
hump=hump_outer.cut(hump_inner)
base=base.cut(rr(187,139,22,8,0,-27,27)).fuse(hump)
# Internal structural landing bridges to the saddle walls, hidden outside.
for x in (-52,52):
    base=base.fuse(box(12,150,6,x,-50,52).common(hump_outer))
# Load pads at root and counterbored head-side stand flange.
rootbolts=[(x,y) for x in (-52,52) for y in (-69,-43)]
for x,y in rootbolts:
    base=base.fuse(cyl(7,14,x,y,44))
    base=base.cut(cyl(2.25,20,x,y,42))
base=base.cut(rr(24,18,4,23,-20,-55,39))
basefast=[(x,y) for x in (-105,105) for y in (-94,94)]+[(0,102),(0,-102)]
for x,y in basefast:
    base=base.fuse(cyl(4.5,22,x,y,7))
    base=base.cut(cyl(2.1,7,x,y,6.9))
# Wide rear decorative I/O panel; actual DC remains distinct.
base=base.cut(box(209,12,20,0,-113,12))
for x in (-109,109):
    base=base.fuse(box(8,9,17.5,x,-108,14.5))
    base=base.cut(Part.makeCylinder(1.7,15,V(x,-118,22),V(0,1,0)))
# Exhaust high in root, inlet in bottom cover.
# One recessed rear grille with parallel vertical openings, 2.4mm webs.
for x in range(-48,49,6):
    base=base.cut(box(3.6,35,18,x,-91,36))
add('B01','Baza tehnica cu volum local pentru sursa',base,space='world')
def bez(t):
    pts=[(-61,58),(-104,98),(25,135),(-8,198)]
    u=1-t; k=[u**3,3*u*u*t,3*u*t*t,t**3]
    return (sum(k[i]*pts[i][0] for i in range(4)),sum(k[i]*pts[i][1] for i in range(4)))
def ribbon(width,offset,x0,xlen):
    pts=[bez(i/40) for i in range(41)]
    a=[V(x0,y-width/2+offset,z) for y,z in pts]
    b=[V(x0,y+width/2+offset,z) for y,z in pts]
    ca=Part.BSplineCurve(); ca.interpolate(a)
    cb=Part.BSplineCurve(); cb.interpolate(list(reversed(b)))
    wire=Part.Wire([ca.toShape(),Part.makeLine(a[-1],b[-1]),cb.toShape(),Part.makeLine(b[0],a[0])])
    return Part.Face(wire).extrude(V(xlen,0,0))

relief=ribbon(P['leg_t']+.6,0,-70.3,140.6).fuse(rr(140.6,42.6,8.3,8,0,-56,58))
print('BEFORE',base.isValid(),base.Volume,len(base.Solids),'CUTTER',relief.isValid(),relief.Volume,len(relief.Solids),flush=True)
base.exportStep(str(ROOT/'validation/before.step'))
relief.exportStep(str(ROOT/'validation/cutter.step'))
base=base.removeSplitter().cut(relief).removeSplitter()
print('TEST BASE',base.isValid(),[(round(q.Volume,3),str(q.BoundBox)) for q in base.Solids],flush=True)
base.exportStep(str(ROOT/'validation/base_test.step'))
