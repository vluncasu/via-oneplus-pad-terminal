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
from mesh_cleanup import clean as clean_mesh
V=A.Vector
ROOT=Path(__file__).resolve().parents[1]
P=json.loads((ROOT/'src/parameters.json').read_text())
for sub in ['cad','step','stl','probes','drawings','docs','validation','preview']:
    (ROOT/sub).mkdir(exist_ok=True)
doc=A.newDocument('Terminal_OPD2203_R04')
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

dw=P['diffuser_t']
# BASE: plate underneath, light ring at 9…12, upper box and local raised root.
bw,bd,br=P['base_w'],P['base_d'],P['base_r']
base=rr(bw,bd,br,20,z=12).cut(rr(bw-6,bd-6,br-3,20,z=11))
# Above subtraction intentionally leaves top roof 1 mm, then reinforce to 3 mm.
base=base.fuse(rr(bw,bd,br,3,z=29))
base=base.fuse(ring(bw-14,bd-14,br-7,2,7,z=7))
base=base.fuse(ring(bw,bd,br,9,2,z=14))
base=base.cut(ring(bw-.1,bd-.1,br-.05,1.7,2,z=12))
# Compact root from the first version; internal support, no stacked dark hood.
hump_outer=rr(156,86,18,26,0,-50,32)
hump_edges=[e for e in hump_outer.Edges if all(abs(v.Point.z-58)<.001 for v in e.Vertexes)]
hump_outer=hump_outer.makeFillet(6,hump_edges)
hump=hump_outer.cut(rr(150,80,15,26,0,-50,29))
base=base.cut(rr(148,78,14,7,0,-50,28)).fuse(hump)
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
add('B02','Difuzor baza monobloc',ring(bw-.6,bd-.6,br-.3,dw,6.6,z=7.2),'DIFF','world')
bottom=rr(bw,bd,br,6,z=3).cut(rr(bw-6,bd-6,br-3,4,z=5.5))
bottom=bottom.cut(ring(bw-.1,bd-.1,br-.05,1.7,2,z=7))
for x,y in basefast: bottom=bottom.cut(cyl(1.7,10,x,y,2)).cut(cyl(3.1,1.5,x,y,3))
for x in range(-72,73,12):
    for y in (15,35,55): bottom=bottom.cut(rr(6,12,2,5,x,y,2))
# Through-table anchors (use fitted bolts to actual worktop); separate from cover screws.
anchors=[(-87,-70),(87,-70)]
for x,y in anchors:
    bottom=bottom.fuse(cyl(9,5,x,y,5.5))
    bottom=bottom.fuse(box(25,5,3,x+math.copysign(11,x),y,5.5))
for x,y in anchors: bottom=bottom.cut(cyl(2.75,12,x,y,2))
for x,y in [(-64,-50),(64,-50),(-50,35),(50,35)]: bottom=bottom.cut(cyl(1.7,7,x,y,2))
add('B03','Capac inferior, admisie si ancorare',bottom,space='world')
for i,(x,y) in enumerate([(-100,-95),(-100,95),(100,-95),(100,95)],1):
    add('T3'+str(i),'Picior TPU '+str(i),rr(24,24,6,3,x,y,0),'TPU','world')
# Deep, blind cartridges slide vertically into individual T-guides from INSIDE.
panel=box(208,3,17,0,-113.5,14.5)
ports=[('USB-A',-88,13,6),('USB-A',-68,13,6),('USB-A',-48,13,6),('USB-A',-28,13,6),('USB-C',-9,9,4),('USB-C',7,9,4),('RJ45',28,14,13),('HDMI',51,15,6),('AUDIO',72,6,6)]
for i,(typ,x,w,h) in enumerate(ports,1):
    panel=panel.cut(box(w+.6,6,h+.6,x,-113.5,22-h/2-.3))
    # 1.4mm flange slides into a 1.8mm slot; mouth recessed 3.5mm.
    insert=box(w+2,1.4,14,x,-111,14)
    barrel=box(w,11.8,h,x,-105.6,22-h/2)
    cavity=box(w-2.4,10.6,h-2.4,x,-106.3,22-h/2+1.2)
    if typ=='AUDIO':cavity=Part.makeCylinder(1.65,10.6,V(x,-111.6,22),V(0,1,0))
    insert=insert.fuse(barrel).cut(cavity)
    if typ=='RJ45':
        # Eight coarse contacts on a raised shelf deep in the cavity.
        for j in range(8):insert=insert.fuse(box(.65,4,1.2,x-3.85+j*1.1,-102.1,17.8))
        insert=insert.fuse(box(5,3.5,1.5,x,-102.3,25.5))
    elif typ in ('USB-A','USB-C','HDMI'):
        insert=insert.fuse(box(w-3.2,5,.9,x,-103,21.55))
    for sign in (-1,1):
        xx=x+sign*(w/2+1.9)
        panel=panel.fuse(box(1.2,3.6,14.4,xx,-110.2,13.8))
        panel=panel.fuse(box(2.2,1.2,14.4,xx-sign*.5,-109,13.8))
    # Stop below each flange, integral with front panel.
    panel=panel.fuse(box(w+4.8,3.6,1.4,x,-110.2,12.4))
    add('P'+str(i).zfill(2),typ+' caseta adancita cu ghidaj T',insert,'BLACK','world',note='Montaj de sus in B04 demontat; retinere prin P10, fara lipici; cavitate oarba decorativa')
# A removable comb locks all nine cartridges against upward extraction.
lock=box(202,3,1.6,0,-110.1,28.8)
for x in (-99.8,99.8):
    tab=box(8,9,6.8,x,-108,21.8)
    tab=tab.cut(box(5.6,4,8,x,-110.1,22.8))
    tab=tab.cut(Part.makeCylinder(1.7,10,V(x,-113,25.6),V(0,1,0)))
    panel=panel.fuse(tab)
    lock=lock.fuse(box(5,3,7.5,x,-110.1,22.9))
    lock=lock.cut(Part.makeCylinder(1.7,6,V(x,-113,25.6),V(0,1,0)))
    pin=Part.makeCylinder(1.5,8.6,V(x,-111.8,25.6),V(0,1,0))
    pin=pin.fuse(Part.makeCylinder(2.8,1.5,V(x,-103.2,25.6),V(0,1,0)))
    add('P11' if x<0 else 'P12','Stift imprimat blocare pieptene',pin,'BLACK','world',note='Joc diametral 0.4mm; potrivire de calibrat, retenție prin dop de TPU sau proba dimensionala')
add('P10','Pieptene demontabil retinere porturi',lock,'BLACK','world')
panel=panel.cut(Part.makeCylinder(4.1,8,V(93,-118,22),V(0,1,0)))
for x in (-109,109):
    panel=panel.fuse(box(11,3,13,x,-99,15.5)).fuse(box(2,12,13,math.copysign(104.5,x),-106,15.5))
    panel=panel.cut(Part.makeCylinder(1.7,9,V(x,-107,22),V(0,1,0)))
for typ,x,w,h in ports:
    base=base.cut(box(w+5.2,13.6,17.4,x,-105.6,12.8))
for xx in (-99.8,99.8):base=base.cut(box(8.6,12,9,xx,-106.8,21.5))
base=base.cut(box(208.6,4,2.2,0,-110.1,28.5))
base_it=next(i for i in items if i['id']=='B01')
base_it['shape']=base.removeSplitter();base_it['world']=base_it['shape'].copy();base_it['obj'].Shape=base_it['world']
panel=panel.cut(base)
add('B04','Panou I/O cu ghidaje si pieptene imprimat',panel,space='world')

for it in items:
    if it['id'].startswith('P') or it['id']=='B04':print('SOLID',it['id'],len(it['shape'].Solids),it['shape'].isValid(),flush=True)
for i,a in enumerate(items):
    for b in items[i+1:]:
        if not a['world'].BoundBox.intersect(b['world'].BoundBox):continue
        vol=a['world'].common(b['world']).Volume
        if vol>.05:print('COLLISION',a['id'],b['id'],vol,flush=True)

panel=next(i['shape'] for i in items if i['id']=='B04')
for code,travel in [('P07',22),('P10',12)]:
    sh=next(i['shape'] for i in items if i['id']==code);worst=0
    for j in range(13):
        q=sh.copy();q.translate(V(0,0,travel*j/12));worst=max(worst,q.common(panel).Volume)
    print('SWEEP',code,worst,flush=True)
