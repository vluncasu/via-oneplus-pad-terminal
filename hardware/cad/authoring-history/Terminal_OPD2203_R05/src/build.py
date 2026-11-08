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
doc=A.newDocument('Terminal_OPD2203_R05')
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

tw,th,tt=P['tablet_w'],P['tablet_h'],P['tablet_t']; cx=P['head_cx']
hw,hh,hr=P['head_w'],P['head_h'],P['head_r']; bc=P['bar_cx']
dw=P['diffuser_t']; gap=P['tablet_clearance_each']
fast=[(x,y) for x in (-100,-35,35,100) for y in (-98,98)]
ret=[(x,y) for x in (-75,75) for y in (-99.5,99.5)]
tablet_slot=rr(tw+2*gap,th+2*gap,P['tablet_r']+gap,60,z=0)
aperture=rr(tw-2*P['lip_overlap'],th-2*P['lip_overlap'],P['tablet_r']-P['lip_overlap'],5,z=-3)
bar_well=rr(P['bar_w']+1,P['bar_h']+1,(P['bar_w']+1)/2-.1,50,bc,0,-1)
bar_window=rr(P['bar_w']-2,P['bar_h']-2,(P['bar_w']-2)/2-.1,5,bc,0,-3)
frame=rr(hw,hh,hr,12-P['head_front_z'],cx,0,P['head_front_z'])
frame=cut(frame,[tablet_slot,aperture,bar_well,bar_window])
# Captured diffuser lower land. Strip carrier remains integral to frame.
frame=frame.cut(ring(hw-.1,hh-.1,hr-.05,1.7,2.01,cx,0,10))
carrier=ring(hw-14,hh-14,hr-7,2,7,cx,0,10)
frame=frame.fuse(carrier)
# Screw pillars are outside tablet silhouette. Blind holes for measured M3 inserts.
for x,y in fast:
    frame=frame.cut(cyl(P['insert_m3_drill']/2,6.5,x,y,4))
for x,y in ret:
    frame=frame.cut(box(15,16,6,x,y-2*math.copysign(1,y),7.1))
    frame=frame.cut(cyl(P['insert_m3_drill']/2,5.2,x,y,2))
# Side USB plug passage is within bar well and tablet pocket.
usb_slot=box(25,20,12,137,P['usb_port_y'],-.01)
frame=frame.cut(usb_slot)
# Recessed Power access; provisional location, safe neutral clearance.
power_access=box(18,14,8,-136,80,.5)
frame=frame.cut(power_access)
# Acoustic side slits below LED channel; positions provisional.
for sy in (-64,-42,42,64):
    frame=frame.cut(box(18,10,2,-138,sy,4.5))
for x,y in [(-tw/2-.4,-50),(-tw/2-.4,50),(tw/2+.4,-45),(tw/2+.4,35)]:
    frame=frame.cut(box(.8,10.3,4.4,x,y,.8))
add('H01','Rama frontala, suport PCB LED',frame,note='USB si Power necesita proba; inserturi M3 instalate inaintea tabletei')

diff=ring(hw-.6,hh-.6,hr-.3,dw,6.6,cx,0,10.2)
add('H02','Difuzor cap monobloc',diff,'DIFF',note='PETG natural; 3 mm expusi la Z12…15; capete capturate')

shell=ring(hw,hh,hr,3,19,cx,0,15)
print('SHELL initial',shell.Volume,len(shell.Solids),flush=True)
# Opaque LED baffle also bridges into outer shell above light cavity.
shell=shell.fuse(ring(hw-14,hh-14,hr-7,2,2,cx,0,17.3))
shell=shell.fuse(ring(hw,hh,hr,9,2,cx,0,18))
shell=shell.cut(ring(hw-.1,hh-.1,hr-.05,1.7,2,cx,0,15))
print('SHELL relief',shell.Volume,len(shell.Solids),flush=True)
for x,y in fast:
    pillar=cyl(2.8,22,x,y,12).fuse(box(7,12,14,x,y+math.copysign(5,y),20))
    shell=shell.fuse(pillar)
    shell=shell.cut(cyl(1.7,24,x,y,11))
print('SHELL pillars',shell.Volume,len(shell.Solids),flush=True)
# Load-bearing back bridge, two vertical ribs, all integral with shell.
bridge=box(130,56,6,0,-30,28)
bridge=bridge.fuse(box(5,110,11,-60,-55,23)).fuse(box(5,110,11,60,-55,23))
shell=shell.fuse(bridge)
print('SHELL bridge',shell.Volume,len(shell.Solids),flush=True)
mount=[(x,y) for x in (-52,52) for y in (-48,-12)]
for x,y in mount:
    shell=shell.cut(cyl(2.25,10,x,y,26)).cut(cyl(4.1,2.5,x,y,27.9))
cable_exit=rr(20,12,3,25,-20,-30,15)
shell=shell.cut(cable_exit)
# Separate intake bottom and exhaust top, no reliance on light slot.
for x in range(-100,101,20):
    for y in (-109,109): shell=shell.cut(box(11,10,3,x,y,25))
print('SHELL vents',shell.Volume,len(shell.Solids),flush=True)
# Inward ledges for cassette, separated from camera and connector keep-outs.
barfix=[(bc+17.4,-75),(bc+17.4,75)]
for x,y in barfix:
    shell=shell.fuse(cyl(3,8,x,y,26))
    shell=shell.cut(cyl(2.1,6.1,x,y,28))
    print('SHELL barfix',shell.Volume,len(shell.Solids),flush=True)
add('H03','Cochilie structurala cu traversa cap-picior',shell)
if os.environ.get('DEBUG_HEAD'):
    shell.exportStep(str(ROOT/'validation/debug_shell.step'))
    sys.exit(0)

back=rr(hw-.5,hh-.5,hr-.25,3,cx,0,34.3)
back=cut(back,[box(133,59,6,0,-30,33),rr(29,198,14,6,bc,0,33)])
for x,y in barfix: back=back.cut(box(11,9,6,x-1.5,y,33))
for x,y in fast:
    back=back.cut(cyl(1.7,6,x,y,33)).cut(cyl(3.2,1.6,x,y,35.8))
# Two purposeful grille fields, fine vertical blades connected to the cover.
for x in range(-108,109,6):
    for y in (-77,77):
        back=back.cut(rr(3.4,23,1.6,5,x,y,33.5))
back=back.cut(box(133,59,10,0,-30,33))
add('H04','Capac posterior ventilat cu nervuri fine',back)

# Rear-loaded tablet retainers; rigid stop plane Z7.1, no screw preload on tablet.
for i,(x,y) in enumerate(ret,1):
    yy=y-math.copysign(3,y)
    keeper=box(13,13,3,x,yy,7.1).cut(cyl(1.7,5,x,y,6))
    add('H1'+str(i),'Opritor tableta '+str(i),keeper,'BLACK')
    pad=box(10,3,.56,x,math.copysign(92.5,y),6.54)
    add('T1'+str(i),'Tampon retentie TPU '+str(i),pad,'TPU')
# Edge cushions occupy dedicated frame recesses, not nominal rigid clearance.
for i,(x,y) in enumerate([(-tw/2-.4,-50),(-tw/2-.4,50),(tw/2+.4,-45),(tw/2+.4,35)],1):
    # Nominal 0.15 mm clearance to body; calibrate with coupon.
    pad=box(.5,10,4,x,y,1)
    add('T2'+str(i),'Tampon lateral TPU '+str(i),pad,'TPU')

# Cassette PMMA, mask and service carrier are separately removable from rear.
pmma=rr(P['bar_w'],P['bar_h'],12.99,P['pmma_t'],bc,0,-1)
add('O01','Fata optica PMMA transparent',pmma,'PMMA',kind='cut')
mask=rr(P['bar_w']-.5,P['bar_h']-.5,12.7,.8,bc,0,.75)
# Elliptical windows exceed rectangular preliminary cone in both directions.
def ellipse_cut(rx,ry,x,y,z,h):
    e=Part.Ellipse(V(x,y,z),rx,ry).toShape()
    return Part.Face(Part.Wire([e])).extrude(V(0,0,h))
mask=cut(mask,[ellipse_cut(10.5,9,bc,55,-1,5),cyl(8,5,bc,-55,-1),cyl(3.2,5,bc,-80,-1)])
# Decorative optical islands, distinct shapes in one continuous dark capsule.
for code,y,r in [('O13',-28,5.5),('O14',30,3.8),('O15',82,3.1)]:
    mask=mask.cut(cyl(r+.2,3,bc,y,.5))
    insert=cyl(r,.75,bc,y,.8).fuse(cyl(r+.7,.6,bc,y,1.55))
    insert=insert.cut(cyl(r-1.1,.35,bc,y,.79))
    add(code,'Senzor optic decorativ '+code,insert,'BLACK',note='Insert fara functie; flansa lipita in spatele mastii')
mask=mask.cut(rr(8.4,12.4,1.2,3,bc,-4,.5))
array=rr(8,12,1,.75,bc,-4,.8).fuse(rr(9.4,13.4,1.2,.6,bc,-4,1.55))
for xx in (-2.2,0,2.2):
    for yy in (-3.3,0,3.3):array=array.cut(cyl(.65,.35,bc+xx,-4+yy,.79))
add('O16','Matrice decorativa 3x3 cu fund inchis',array,'BLACK')
mask=mask.cut(rr(12.4,3.4,1.5,3,bc,-40,.5))
bar=rr(12,3,1.4,.75,bc,-40,.8).fuse(rr(13.4,4.4,1.8,.6,bc,-40,1.55))
bar=bar.cut(rr(9,.9,.4,.3,bc,-40,.79))
add('O17','Fanta decorativa senzor liniar',bar,'BLACK')
for xx in (-3,0,3):mask=mask.cut(cyl(.65,.4,bc+xx,-88,.74))
add('O02','Masca optica neagra',mask,'BLACK')
# Cartridge side walls stop behind PMMA; carrier kept clear of lens and USB.
cass=ring(27,195,13.4,1.5,18,bc,0,3.3)
cass=cass.fuse(rr(27,195,13.4,2.4,bc,0,21.3))
cass=cut(cass,[box(28,24,16,bc,0,1),box(12,69,7,bc,52.5,16)])
# Back service plate retained with two M3s. Window to deplug USB accessible behind cap.
cass=cass.fuse(rr(28.5,197.5,14.2,2.7,bc,0,34.3))
for x,y in barfix:
    cass=cass.fuse(box(10,8,2.7,x-1.5,y,34.3))
    cass=cass.cut(cyl(1.7,5,x,y,33)).cut(cyl(3.1,1.3,x,y,35.7))
# Light baffles around camera / decorative lens, inside cassette wall.
for y in (18,-25): cass=cass.fuse(box(24,1.5,18,bc,y,3.3))
# PMMA retainers are rail lips, no point screws on transparent sheet.
for x in (bc-12,bc+12):
    cass=cass.fuse(box(1,138,2,x,0,1.6))
cass=cass.cut(box(28,24,16,bc,0,0))
for x in (bc-11.5,bc+11.5):
    cass=cass.fuse(box(2,130,11,x,0,23.3))
for x,y in [(bc,-55),(bc,-80),(bc-8.5,52.5),(bc+8.5,52.5)]:
    cass=cass.cut(cyl(1.2,4,x,y,21)).cut(cyl(2.6,4,x,y,34))
for x in (bc-6,bc+6): cass=cass.cut(cyl(.9,3,x,-17,21))
# Rear island uses blind annular recesses; these do not expose the electronics.
for yy,rad in [(82,3),(55,8),(28,4),(-28,5.5),(-55,8),(-80,3)]:
    ann=cyl(rad,.45,bc,yy,36.6).cut(cyl(max(rad-1,1),.6,bc,yy,36.55))
    cass=cass.cut(ann)
for xx in (-2.2,0,2.2):
    for yy in (-3.3,0,3.3):cass=cass.cut(cyl(.65,.45,bc+xx,yy,36.6))
add('O03','Caseta optica si capac service',cass,'BLACK')

# Camera cradle: edge support at PCB margins, open electronics region, interchangeable.
pcb_y=P['camera_axis_y']+(P['camera_pcb_l']/2-P['camera_axis_from_end'])
cradle=box(22,66,2,bc,pcb_y,17)
for x in (bc-4.8,bc+4.8):
    cradle=cradle.fuse(box(1.6,62,4,x,pcb_y,13))
for y in (pcb_y-31.5,pcb_y+31.5):
    cradle=cradle.fuse(box(11,2,4,bc,y,13))
cradle=cradle.cut(box(12,55,3,bc,pcb_y,16.5))
cradle=moved(cradle,(0,0,2))
for x in (bc-8.5,bc+8.5): cradle=cradle.cut(cyl(1.2,6,x,52.5,17)).cut(hx(x,52.5,18.9,1.7,2.4))
add('O04','Leagan OV2659 schimbabil',cradle,'BLACK',note='PCB retinut la margini; gauri modul neinventate; shim dupa masurare')
# Two clip straps on blank PCB ends, no clamp on components/lens.
for i,y in enumerate((24,81),1):
    clip=box(13,2,1,bc,y,11).fuse(box(1.6,2,5,bc-5.6,y,12)).fuse(box(1.6,2,5,bc+5.6,y,12))
    clip=moved(clip,(0,0,2)).cut(cradle)
    add('O0'+str(4+i),'Agrafa camera '+str(i),clip,'BLACK')
fake=fuse([cyl(7.8,1,bc,-55,1.1),ring(13,13,6.49,1,1.2,bc,-55,2.1),cyl(3.8,1.8,bc,-55,2.1)])
fake=moved(fake,(0,0,2)).fuse(cyl(2.4,16.4,bc,-55,4.9)).cut(cyl(.9,8,bc,-55,13.3))
add('O07','Obiectiv decorativ in trepte cu tija M2',fake,'BLACK')
small=cyl(3,1.5,bc,-80,3.1).fuse(cyl(2.4,16.7,bc,-80,4.6)).cut(cyl(.9,8,bc,-80,13.3))
add('O08','Insert optic mic decorativ cu tija M2',small,'BLACK')
# Concentric printed front rings, identical visual family on real and false optics.
for i,y in enumerate((55,-55),1):
    bezel=cyl(9.5,.8,bc,y,1.7).cut(cyl(8,.95,bc,y,1.65))
    bezel=bezel.fuse(cyl(8.8,.6,bc,y,2.5).cut(cyl(8,.8,bc,y,2.4)))
    add('O1'+str(i),'Inel concentric optic '+str(i),bezel,'BLACK',note='Fixare pe masca cu adeziv compatibil; neportant')
# Cable clamp uses screws in cassette floor; detachable.
clamp=box(17,6,5,bc,-17,16).cut(Part.makeCylinder(2.2,8,V(bc,-21,19.1),V(0,1,0)))
for x in (bc-6,bc+6): clamp=clamp.cut(cyl(1.2,7,x,-17,15))
add('O09','Clema cablu USB, strangere pe mantaua cablului',clamp,'BLACK')
# Power shuttle deliberately leaves 0.5 mm to tablet edge; stop flange limits travel.
act=box(9,8,2.5,-135.5,80,3).fuse(box(1.5,11,5,-140.75,80,1.75))
add('H20','Actuator Power de proba',act,'BLACK',note='Nu se monteaza pana la masurarea Power; cursa oprita si joc de repaus necesare')

# BASE: plate underneath, light ring at 9…12, upper box and local raised root.
bw,bd,br=P['base_w'],P['base_d'],P['base_r']
base=rr(bw,bd,br,20,z=12).cut(rr(bw-6,bd-6,br-3,20,z=11))
# Above subtraction intentionally leaves top roof 1 mm, then reinforce to 3 mm.
base=base.fuse(rr(bw,bd,br,3,z=29))
base=base.fuse(ring(bw-14,bd-14,br-7,2,7,z=7))
base=base.fuse(ring(bw,bd,br,9,2,z=14))
base=base.cut(ring(bw-.1,bd-.1,br-.05,1.7,2,z=12))
# Compact root from the first version; internal support, no stacked dark hood.
hump_outer=rr(156,110,18,26,0,-36,32)
hump_edges=[e for e in hump_outer.Edges if all(abs(v.Point.z-58)<.001 for v in e.Vertexes)]
hump_outer=hump_outer.makeFillet(6,hump_edges)
hump=hump_outer.cut(rr(150,104,15,26,0,-36,29))
base=base.cut(rr(148,102,14,7,0,-36,28)).fuse(hump)
# Load pads at root and counterbored head-side stand flange.
rootbolts=[(x,y) for x in (-60,60) for y in (-69,-43)]
for x,y in rootbolts:
    base=base.fuse(cyl(7,14,x,y,44))
    base=base.cut(cyl(2.25,20,x,y,42))
base=base.cut(rr(20,10,3,23,-20,-63,39))
basefast=[(x,y) for x in (-105,105) for y in (-94,94)]+[(0,102)]
for x,y in basefast:
    base=base.fuse(cyl(4.5,22,x,y,7))
    base=base.cut(cyl(2.1,7,x,y,6.9))
# Wide rear decorative I/O panel; actual DC remains distinct.
base=base.cut(box(209,12,20,0,-113,12))
for x in (-109,109):
    base=base.fuse(box(8,8,17.5,x,-94,14.5))
    base=base.cut(Part.makeCylinder(1.7,12,V(x,-103,22),V(0,1,0)))
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
for x,y in [(-60,-24),(60,-24),(-50,55),(50,55)]: bottom=bottom.cut(cyl(1.7,7,x,y,2))
add('B03','Capac inferior, admisie si ancorare',bottom,space='world')
for i,(x,y) in enumerate([(-100,-95),(-100,95),(100,-95),(100,95)],1):
    add('T3'+str(i),'Picior TPU '+str(i),rr(24,24,6,3,x,y,0),'TPU','world')
# Deep, blind cartridges slide vertically into individual T-guides from INSIDE.
panel=box(208,1.8,17,0,-112.9,14.5)
def connector_profile(typ,w,h,depth,x,y,z):
    if typ in ('USB-C','USB-A','AUDIO'):
        if typ=='AUDIO':return Part.makeCylinder(w/2,depth,V(x,y,z),V(0,1,0))
        q=rr(w,h,h/2-.01 if typ=='USB-C' else .6,depth)
        q.rotate(V(),V(1,0,0),-90);q.translate(V(x,y,z));return q
    if typ=='HDMI':
        pts=[V(x-w/2,y,z+h/2),V(x+w/2,y,z+h/2),V(x+w/2-1.5,y,z-h/2),V(x-w/2+1.5,y,z-h/2)]
        return Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(V(0,depth,0))
    if typ=='RJ45':
        q=box(w,depth,h-2.4,x,y+depth/2,z-h/2)
        return q.fuse(box(w*.46,depth,2.4,x,y+depth/2,z+h/2-2.4))
    return box(w,depth,h,x,y+depth/2,z-h/2)
ports=[('USB-A',-88,13,6),('USB-A',-68,13,6),('USB-A',-48,13,6),('USB-A',-28,13,6),('USB-C',-9,9,4),('USB-C',7,9,4),('RJ45',28,14,13),('HDMI',51,15,6),('AUDIO',72,6,6)]
for i,(typ,x,w,h) in enumerate(ports,1):
    panel=panel.cut(connector_profile(typ,w+.6,h+.6,6,x,-116.5,22))
    # 1.4mm flange slides into a 1.8mm slot; mouth recessed 3.5mm.
    insert=box(w+2,1.4,14,x,-111,14)
    barrel=connector_profile(typ,w,h,11.8,x,-111.5,22)
    cavity=connector_profile(typ,w-2.4,h-2.4,11.1,x,-112.1,22)
    if typ=='AUDIO':cavity=Part.makeCylinder(1.65,11.1,V(x,-112.1,22),V(0,1,0))
    insert=insert.fuse(barrel).cut(cavity)
    if typ=='RJ45':
        # Eight coarse contacts on a raised shelf deep in the cavity.
        for j in range(8):insert=insert.fuse(box(.65,4,1.2,x-3.85+j*1.1,-102.1,17.8))
        insert=insert.fuse(box(5,3.5,1.5,x,-102.3,25.5))
    elif typ in ('USB-A','USB-C','HDMI'):
        insert=insert.fuse(box(w-3.2,9.5,.9,x,-105.25,21.55))
        n=4 if typ=='USB-A' else 6
        pitch=1.7 if typ=='USB-A' else .85
        for j in range(n):insert=insert.fuse(box(.5,7,.30,x+(j-(n-1)/2)*pitch,-105.2,22.35))

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
    add('P11' if x<0 else 'P12','Stift imprimat blocare pieptene',pin,'BLACK','world',note='Joc diametral 0.4mm; potrivire de calibrat, retentie prin potrivire calibrata; test fizic obligatoriu')
add('P10','Pieptene demontabil retinere porturi',lock,'BLACK','world')
panel=panel.cut(Part.makeCylinder(4.1,8,V(93,-118,22),V(0,1,0)))
# R05: monolithic perimeter body, integral recessed cartridge guides.
# No separate exterior I/O plate: its skin is fused to the rear wall.
body=ring(bw,bd,br,3,17,z=12)
body=body.fuse(ring(bw-14,bd-14,br-7,2,7,z=7))
body=body.fuse(ring(bw,bd,br,9,2,z=14))
body=body.cut(ring(bw-.1,bd-.1,br-.05,1.7,2,z=12))
rear_skin=box(208,3,20,0,-113.5,12)
for typ,x,w,h in ports:
    rear_skin=rear_skin.cut(connector_profile(typ,w+.6,h+.6,8,x,-118,22))
rear_skin=rear_skin.cut(Part.makeCylinder(4.1,10,V(93,-119,22),V(0,1,0)))
# Remove wall behind mouths, then fuse a true 3mm continuous skin.
body=body.cut(box(208,8,22,0,-114,11))
for typ,x,w,h in ports:body=body.cut(box(w+5.2,13.6,17.4,x,-105.6,12.8))
body=body.fuse(rear_skin).fuse(panel)
body=body.cut(ring(bw-.1,bd-.1,br-.05,1.7,2,z=12))
for x,y in basefast:
    boss=cyl(4.5,20,x,y,7).cut(cyl(2.1,7,x,y,6.9))
    body=body.fuse(boss)
    if x:
        body=body.fuse(box(16,6,8,math.copysign(111,x),y,16))
# Separate top lid with the sculpted power-supply enclosure.
topcap=base.common(box(400,400,100,0,0,29.3))
# Rear strip belongs to the single perimeter body. Clear cartridge retention.
topcap=topcap.cut(box(211,18,4,0,-109,28.9))
# Register tongue: hidden from outside, 0.30mm radial running clearance.
tongue=ring(bw-6.6,bd-6.6,br-3.3,1.5,5,z=24.6)
tongue=tongue.cut(box(220,28,7,0,-108,23.8))
topcap=topcap.fuse(tongue)
# Four hidden bolts pull lid onto hard stops; alignment does not rely on screws.
lidfast=[(-85,-80),(85,-80),(-85,80),(85,80)]
for x,y in lidfast:
    topcap=topcap.fuse(cyl(5,8.3,x,y,21)).cut(cyl(2.1,6,x,y,20.9))
    shelf=box(40,12,3,math.copysign(97,x),y,18)
    shelf=shelf.cut(cyl(1.7,5,x,y,17)).cut(cyl(3.1,1.2,x,y,17.9))
    body=body.fuse(shelf)
# Register cannot occupy bosses of lower service cover.
for x,y in basefast:topcap=topcap.cut(cyl(4.8,9,x,y,23))
body=body.removeSplitter();topcap=topcap.removeSplitter()
base_it=next(i for i in items if i['id']=='B01')
base_it['name']='Corp baza monobloc cu porturi si ghidaje interioare'
base_it['shape']=body;base_it['world']=body.copy();base_it['obj'].Shape=body
add('B07','Capac superior cu volum sursa si ghidaj ascuns',topcap,space='world',note='4 M3x8 din interior dupa scoaterea B03; limba perimetrala cu joc radial 0.30 mm')
base=body

# Adjustable trays: straps pass under electronics. No assumed OEM mounting holes.
tray=box(104,76,3,0,-24,7)
for x in (-50.5,50.5):tray=tray.fuse(box(3,76,8,x,-24,10))
for y in (-60.5,12.5):tray=tray.fuse(box(104,3,8,0,y,10))
for x in (-33,33):tray=tray.cut(box(6,72,4,x,-24,6.5))
for x in (-60,60):
    tray=tray.fuse(box(18,12,4.5,x-math.copysign(2,x),-24,5.5)).cut(cyl(1.7,5,x,-24,5))
tray=tray.cut(rr(22,12,3,22,-20,-63,5))
add('B05','Tava PSU 86x58.02x33.02 cu rezerva',tray,'BLACK','world')
etray=box(90,50,3,0,55,7)
for x in (-43,43):etray=etray.fuse(box(3,50,5,x,55,10))
for y in (32,78):etray=etray.fuse(box(90,3,5,0,y,10))
for x in (-28,28):etray=etray.cut(box(5,44,4,x,55,6.5))
for x in (-50,50):
    etray=etray.fuse(box(14,12,4.5,x-math.copysign(3,x),55,5.5)).cut(cyl(1.7,5,x,55,5))
add('B06','Tava convertor si distributie',etray,'BLACK','world')

# S ribbon profiles use analytic BSpline interpolation of a cubic Bezier centreline.
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
leg=ribbon(P['leg_t'],0,-70,140)
leg=leg.cut(ribbon(P['leg_t']-2*P['leg_wall'],0,-67,134))
# Longitudinal ribs reinforce a closed box section. Central seam flanges contact at X0.
for x in (-43,-1.5,40): leg=leg.fuse(ribbon(18,0,x,3))
foot=rr(140,42,8,8,0,-56,58)
top=world(rr(130,56,10,9,0,-30,34),'head')
leg=leg.fuse(foot).fuse(top)
# Cable path through flange and open S cavity left of centre seam.
leg=leg.cut(rr(20,10,3,11,-20,-63,55)).cut(world(cable_exit,'head'))
for x,y in rootbolts:
    leg=leg.cut(cyl(2.25,25,x,y,56)).cut(hx(x,y,62,4.5,4.3))
for x,y in mount:
    leg=leg.cut(world(cyl(2.25,10,x,y,32),'head')).cut(world(hx(x,y,33.9,3.8,4.3),'head'))
# Printed alignment spigots + metal clamp only at head/base; no seam bolts.
# Four short rectangular dowels prevent lateral shear and locate both shells.
seam=[]
for t in (.22,.44,.66,.84):
    y,z=bez(t);y-=3;seam.append((y,z))
    boss=box(20,12,10,0,y,z-5).common(ribbon(P['leg_t'],0,-70,140))
    leg=leg.fuse(boss)
    leg=leg.cut(box(16,5.6,5.6,0,y,z-2.8))
# Accessible cable corridor near front wall, crosses behind screw bosses with 1mm web.
leg=leg.cut(ribbon(8,5,-30,20))
# Trim the S tangent exactly against the rear structural interface, with cap clearance.
leg=leg.cut(world(rr(hw+1,hh+1,hr+.5,44,cx,0,-10),'head'))
cap_keepout=rr(hw+1,hh+1,hr+.5,5,cx,0,34).cut(box(132.5,58.5,6,0,-30,33))
leg=leg.cut(world(cap_keepout,'head'))
leg=leg.cut(world(back,'head'))
left=leg.common(box(70,400,400,-35,0,0))
right=leg.common(box(70,400,400,35,0,0))
add('S01','Picior S jumatate stanga cu traseu cablu',left,space='world')
add('S02','Picior S jumatate dreapta demontabila',right,space='world')
for i,(y,z) in enumerate(seam,1):
    pin=box(15,5,5,0,y,z-2.5)
    add('S2'+str(i),'Cheie imprimata aliniere picior '+str(i),pin,space='world',note='5x5, joc 0.3 pe parte; nu inlocuieste cele 8 M4 de la flanse')

# White removable nut-pocket plugs; TPU stems fit by calibration, no structural role.
for k,(x,y) in enumerate(rootbolts,1):
    cap=hx(x,y,66.3,1.0,4.4).fuse(hx(x,y,65.4,.9,4.0)).cut(cyl(2.6,1.5,x,y,65.3))
    add('S3'+str(k),'Dop mascare piulita baza '+str(k),cap,'TPU','world',note='TPU alb; inel in buza buzunarului, degajare centrala pentru varful surubului; probeaza jocul')

for k,(x,y) in enumerate(rootbolts,1):
    add('S4'+str(k),'Distantier surub baza 3mm '+str(k),cyl(5.5,3,x,y,41).cut(cyl(2.25,4,x,y,40.5)),'PETG','world',note='100% infill; M4x25 de la Z41 ajunge la Z66; confirma tolerantele hardware')

# Compact root ends at Z58; the split stand is assembled laterally, then bolted.

# REFERENCE COMPONENTS: a conservative envelope, not reverse-engineered exact products.
tablet=rr(tw,th,P['tablet_r'],tt)
add('R01','OnePlus Pad corp oficial / colt ipoteza',tablet,'REF',kind='reference')
rearcam=cyl(15,4,0,80,tt)
add('R02','Camera originala volum rezervat neconfirmat',rearcam,'REF',kind='reference')
usb=box(P['usb_plug_protrusion']-2,P['usb_plug_height'],P['usb_plug_depth'],tw/2+2+(P['usb_plug_protrusion']-2)/2,P['usb_port_y'],3)
usb=usb.fuse(box(2.1,8,2.8,tw/2+1.05,P['usb_port_y'],P['usb_port_z']-1.4))
add('R03','Mufa USB-C gabarit de selectare',usb,'REF',kind='reference')
pcb=box(P['camera_pcb_w'],P['camera_pcb_l'],P['camera_pcb_t'],bc,pcb_y,P['camera_pcb_front_z']+2)
lens=cyl(P['camera_lens_d']/2,P['camera_pcb_front_z']-P['camera_lens_front_z'],bc,P['camera_axis_y'],P['camera_lens_front_z']+2)
add('R04','OV2659 PCB 60x8, lentila ipoteza',pcb.fuse(lens),'PCB',kind='reference')
add('R05','Rezerva sursa dupa STEP 92x64.02x39.02',box(P['psu_w'],P['psu_d'],P['psu_h'],0,-24,11),'REF','world','reference')
add('R06','Convertor sursa USB, gabarit rezervat',box(62,38,15,-8,55,11),'PCB','world','reference')
# PCB strip envelopes at 3.0mm height, outward emission; connector breaks not guessed.
for code,w,h,r,x,y,z,space in [('R07',hw-14,hh-14,hr-7,cx,0,12,'head'),('R08',bw-14,bd-14,br-7,0,0,9,'world')]:
    led=ring(w+2,h+2,r+1,1,3,x,y,z)
    add(code,'Banda COB volum de referinta',led,'DIFF',space,'reference')

# Hidden identification marks are part of the CAD, never render-only text.
from hidden_marks import mark
mark_report=[]
for it in items:
    if it['kind']!='print':continue
    code=it['id']
    axis=(0,0,1)
    if code in ('H02','H03','H04','B01','B02','B07','O03'):axis=(0,0,-1)
    elif code=='S01':axis=(1,0,0)
    elif code=='S02':axis=(-1,0,0)
    elif code.startswith('S2'):axis=(1,0,0)
    elif code.startswith('P') or code=='B04':axis=(0,1,0)
    marked,info=mark(it['shape'],code,axis)
    if info is None:
        marked,info=mark(it['shape'],code[1:],axis)
        if info:info['full_code']=code
    it['shape']=marked;it['world']=world(marked,it['space']);it['obj'].Shape=it['world']
    mark_report.append(info or {'code':code,'status':'TOO_SMALL_FOR_SAFE_HIDDEN_MARK','identification':'separate labelled plate cell / assembly map'})
(ROOT/'docs/hidden_marks.json').write_text(json.dumps(mark_report,indent=2))

# H uses X right / Y up / Z rear: a left-handed viewing convention.
# Reflect assembly X once so the optical bar is visually RIGHT from the user.
# Internal construction above used a right-handed auxiliary frame; individual
# global parts and final assembly are both reflected here, preserving all fits.
for it in items:
    it['world']=it['world'].mirror(V(0,0,0),V(1,0,0))
    it['obj'].Shape=it['world']
    it['shape']=it['shape'].mirror(V(0,0,0),V(1,0,0)) # head local exports must match reflected assembly too

# PROBES made from actual production geometry, each separate printable part.
def probe(code,name,s,mat='PETG'):
    if not s.Solids: raise ValueError(code)
    probes.append({'id':code,'name':name,'shape':s.removeSplitter(),'mat':mat})
usb_probe=frame.common(box(58,60,23,135,0,-2))
usb_probe=usb_probe.fuse(box(58,60,2,135,0,20))
for y in (-29,29): usb_probe=usb_probe.fuse(box(34.4,2,21.2,146.8,y,-1))
probe('Q01','Segment tableta USB din H01 cu jug de proba',usb_probe)
probe('Q02','Caseta optica completa test',cass,'BLACK')
probe('Q03','Leagan camera test',cradle,'BLACK')
probe('Q04','Masca optica test',mask,'BLACK')
corner_clip=box(55,55,28,cx+hw/2-27.5,hh/2-27.5,-2)
probe('Q05','Colt LED suport',frame.common(corner_clip))
for i,t in enumerate((.8,1,1.2),1):
    sample=ring(hw-.6,hh-.6,hr-.3,t,6.6,cx,0,10.2).common(corner_clip)
    probe('Q0'+str(5+i),'Colt difuzor '+str(t)+' mm',sample,'DIFF')
# Low-material full-perimeter fit gauge: four L quadrants, printed flat.
# Includes true body cavity, 1 mm lip, 0.5 mm side clearance. Butt joints
# align with external two-pin bars so the trial checks both overall dimensions.
gauge=rr(tw+6,th+6,P['tablet_r']+3,8,z=-1).cut(tablet_slot).cut(aperture)
for i,(sgx,sgy) in enumerate([(-1,-1),(1,-1),(1,1),(-1,1)],1):
    quadrant=gauge.common(box((tw+6)/2,(th+6)/2,12,sgx*(tw+6)/4,sgy*(th+6)/4,-2))
    probe('Q2'+str(i),'Gabarit economic tableta cadran '+str(i),quadrant)
# A narrow 30x35 corner coupon for quick local profile check (<2g typical).
probe('Q25','Colt tableta minim',gauge.common(box(30,35,12,tw/2-12,th/2-14,-2)))
probe('Q61','Caseta Ethernet proba reala',next(i for i in items if i['id']=='P07')['shape'],'BLACK')
# B04 guide sample extends full Z so the top-loading path can be tested.
probe('Q62','Ghidaj Ethernet sectiune corp monobloc',max(next(i for i in items if i['id']=='B01')['shape'].common(box(21,18,24,-28,-108,11)).Solids,key=lambda q:q.Volume))
probe('Q63','Cheie picior 5x5',box(15,5,5))
probe('Q64','Locas cheie picior',box(14,12,10).cut(box(16,5.6,5.6,0,0,2.2)))
probe('Q26','Micro colt tableta 20x20',gauge.common(box(20,20,12,tw/2-7,th/2-7,-2)))
# Heat-set pilot ladder for the photographed inserts (outer diameters unverified).
for i,nom in enumerate((3.8,4.0,4.2),1):
    sample=box(14,14,8).cut(cyl(nom/2,6,z=2))
    probe('Q3'+str(i),'Pilot insert M3 diametru '+str(nom),sample)
# Standard M4 hex-nut pocket tolerance trials; true metal threads carry load.
for i,c in enumerate((.15,.25,.35),1):
    sample=box(16,16,8).cut(hx(0,0,4,5,(7+2*c)/math.sqrt(3))).cut(cyl(2.25,9,z=-.5))
    probe('Q4'+str(i),'Piulita M4 joc pe fata '+str(c),sample)
# Clearances stated per side, tongue separate from three sockets.
for i,c in enumerate((.2,.3,.4),1):
    block=box(24,18,5).cut(box(10+2*c,8+2*c,7,z=-1))
    probe('Q1'+str(i),'Ajustaj joc pe parte '+str(c),block)
probe('Q14','Limba calibrare 10x8',box(10,8,8))
# Closure station straight test: place both cut ends, do not trim live COB between pads.
station=box(75,14,3).fuse(box(75,3,10,0,-5.5,3))
probe('Q15','Proba inchidere LED si lipituri',station)

# Coarse printed thread trial only: custom 12 mm / 2 mm pitch, not ISO M12.
# Structural tablet load continues through metal M3/M4 fasteners.
def coarse_thread(clearance=0):
    helix=Part.makeHelix(2,8,5.25+clearance)
    pts=[V(5+clearance,0,-.65),V(6+clearance,0,-.12),V(6+clearance,0,.12),V(5+clearance,0,.65)]
    profile=Part.Wire(Part.makePolygon(pts+[pts[0]]).Edges)
    sweep=Part.Wire(helix.Edges).makePipeShell([profile],True,True)
    return cyl(5.25+clearance,8).fuse(sweep).common(cyl(6.1+clearance,8))
thread=coarse_thread()
knob=cyl(9,3,z=-3).fuse(thread)
probe('Q50','Surub imprimat custom D12 pas2 NEPORTANT',knob)
for i,c in enumerate((.2,.3,.4),1):
    nut=cyl(10,7,z=.5).cut(coarse_thread(c))
    probe('Q5'+str(i),'Piulita print custom joc radial '+str(c),nut)

def orientation(s,code,space,kind='print'):
    t=s.copy()
    # Head large ring: local X diagonal, local Y vertical; local Z horizontal depth.
    if code in ('H01','H02','H03','H04','B01','B02','B03','B07'):
        t.rotate(V(0,0,0),V(1,0,0),90); t.rotate(V(0,0,0),V(0,0,1),-45)
        desc='Pe muchie; X la 45 grade; Y vertical; suporturi pe interior'
    elif code in ('S01','S02'):
        t.rotate(V(0,0,0),V(0,1,0),-90 if code=='S01' else 90)
        desc='Plan separatie X0 pe pat; profil S in XY; suporturi locale'
    elif code.startswith('P'):
        t.rotate(V(0,0,0),V(1,0,0),-90); desc='Flansa din spate pe pat, detaliile portului in sus'
    elif code.startswith('T2'):
        t.rotate(V(0,0,0),V(0,1,0),90); desc='Fata 10x4 pe pat; grosime TPU 0.5 mm pe Z'
    elif code=='B04':
        t.rotate(V(0,0,0),V(1,0,0),90); desc='Fata panoului pe pat; suport sub urechile din spate'
    elif code in ('O03','Q02'):
        t.rotate(V(0,0,0),V(1,0,0),180); desc='Capac posterior pe pat, cavitate in sus'
    elif code=='B01':
        t.rotate(V(0,0,0),V(1,0,0),180); desc='Racord superior pe pat; suporturi sub acoperisul bazei'
    else: desc='Culcat; fata plana selectata, verificare suport in slicer'
    b=t.BoundBox; t.translate(V(-b.XMin,-b.YMin,-b.ZMin)); return t,desc

# Geometry and meshing are verified, with explicit distinction from physical validation.
rows=[]; manifest=[]
def export_item(it,probe_mode=False):
    code=it['id']; s=it['shape']; kind=it.get('kind','print'); space=it.get('space','world')
    stem=ROOT/('probes' if probe_mode else 'stl')/code
    orient,desc=orientation(s,code,space)
    mesh=MeshPart.meshFromShape(Shape=orient,LinearDeflection=.07,AngularDeflection=.18,Relative=False)
    clean_mesh(mesh)
    mesh.write(str(stem)+'.stl')
    s.exportStep(str(ROOT/'step'/code)+'.step')
    bb=orient.BoundBox
    topology=mesh.Topology
    closed=mesh.isSolid()
    valid=s.isValid()
    check(code+' BRep/mesh',valid and closed,{'solids':len(s.Solids),'mesh_solid':closed,'facets':mesh.CountFacets})
    if kind=='print': check(code+' envelope nominal 256',max(bb.XLength,bb.YLength,bb.ZLength)<=256,{'xyz':[round(bb.XLength,2),round(bb.YLength,2),round(bb.ZLength,2)],'supports_slicer':'NOT TESTED'})
    row={'ID':code,'Denumire':it['name'],'Material':it['mat'],'Tip':kind,'Volum_cm3':round(s.Volume/1000,3),'Solide':len(s.Solids),'X_print_mm':round(bb.XLength,2),'Y_print_mm':round(bb.YLength,2),'Z_print_mm':round(bb.ZLength,2),'Orientare':desc,'Brim5_in_256':bool(bb.XLength+10<=256 and bb.YLength+10<=256 and bb.ZLength<=256),'Note':it.get('note','')}
    rows.append(row)
    if not probe_mode:
        # In-assembly OBJ-like triangulation for reproducible Blender preview.
        wm=MeshPart.meshFromShape(Shape=it['world'],LinearDeflection=.13,AngularDeflection=.22,Relative=False)
        clean_mesh(wm)
        wm.write(str(ROOT/'preview'/code)+'.stl')
        manifest.append({'id':code,'name':it['name'],'material':it['mat'],'kind':kind,'space':space,'color':COL[it['mat']],'volume_mm3':s.Volume})
    print('EXPORTED',code,flush=True)
for it in items: export_item(it)
for it in probes:
    if it['id'] in ['Q'+str(i).zfill(2) for i in list(range(1,11))+[15]+list(range(21,27))]:
        it['shape']=it['shape'].mirror(V(0,0,0),V(1,0,0))
    export_item(it,True)

doc.recompute(); doc.saveAs(str(ROOT/'cad/Terminal_OPD2203_R05.FCStd'))
assembly=Part.makeCompound([i['world'] for i in items])
assembly.exportStep(str(ROOT/'step/Terminal_OPD2203_R05_assembly.step'))
with open(ROOT/'docs/piese_si_imprimare.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
(ROOT/'preview/manifest.json').write_text(json.dumps(manifest,indent=2))

# Report pairwise positive volume collisions; never hide them as "passed".
collisions=[]
for n,a in enumerate(items):
    for b in items[n+1:]:
        if a['kind']=='reference' and b['kind']=='reference': continue
        sa,sb=a['world'],b['world']
        if not sa.BoundBox.intersect(sb.BoundBox): continue
        v=sa.common(sb).Volume
        if v>.05: collisions.append({'a':a['id'],'b':b['id'],'volume_mm3':round(v,3)})
(ROOT/'validation/interferences.json').write_text(json.dumps(collisions,indent=2))

headlen=2*(hw-14+hh-14-4*(hr-7))+2*math.pi*(hr-7)
baselen=2*(bw-14+bd-14-4*(br-7))+2*math.pi*(br-7)
# Estimates only: material use includes exact walls and ribs; sliced infill not assumed.
massdata=[]
for it in items:
    if it['kind']!='reference':
        density=1.24 if it['mat']=='DIFF' else 1.19 if it['mat']=='PMMA' else 1.12 if it['mat']=='TPU' else 1.07
        mass=it['shape'].Volume/1000*density/1000
    elif it['id']=='R01': mass=.552
    elif it['id']=='R05': mass=.25
    elif it['id']=='R06': mass=.05
    else: mass=.012
    solids=it['world'].Solids
    c=sum((s.CenterOfMass*s.Volume for s in solids),V(0,0,0))/sum(s.Volume for s in solids)
    massdata.append((it['id'],mass,c.x,c.y,c.z))
total=sum(r[1] for r in massdata)
cg=[sum(r[1]*r[j] for r in massdata)/total for j in (2,3,4)]
# Conservative support polygon at foot centres, excludes uncertain TPU contact extension.
arms=[100-cg[0],100+cg[0],95-cg[1],95+cg[1]]
force_height=assembly.BoundBox.ZMax
sf=[total*9.81*a/(5*force_height) for a in arms]
calc={'led_path_head_mm':headlen,'led_path_base_mm':baselen,'led_total_m':(headlen+baselen)/1000,'led_W_at_7_W_m':(headlen+baselen)/1000*P['led_w_per_m'],'led_pcb_corner_radius_head_mm':hr-7,'led_pcb_corner_radius_base_mm':br-7,'led_cut_pitch_validated':False,'assembly_bbox_mm':[assembly.BoundBox.XLength,assembly.BoundBox.YLength,assembly.BoundBox.ZLength],'assembly_zmax_mm':force_height,'mass_estimate_kg':total,'cg_estimate_mm':cg,'stability_5N_at_top_sf':sf,'stability_required_sf':1.5,'freestanding_validated':False,'power_total_W':(headlen+baselen)/1000*P['led_w_per_m']+P['tablet_budget_w']/P['converter_efficiency']+1}
(ROOT/'validation/calculations.json').write_text(json.dumps(calc,indent=2))
(ROOT/'validation/checks.json').write_text(json.dumps(checks,indent=2))

# Analytic 1:1 vector contours for optical shop (nominal dimensions, no kerf applied).
def capsule_path(w,h):
    r=w/2
    return f'M {r},0 A {r},{r} 0 0 1 {w},{r} L {w},{h-r} A {r},{r} 0 0 1 {r},{h} A {r},{r} 0 0 1 0,{h-r} L 0,{r} A {r},{r} 0 0 1 {r},0 Z'
w,h=P['bar_w'],P['bar_h']
svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}mm" height="{h}mm" viewBox="0 0 {w} {h}"><path d="{capsule_path(w,h)}" fill="none" stroke="black" stroke-width="0.05"/></svg>'
(ROOT/'drawings/O01_PMMA_26x194_1to1.svg').write_text(svg)
mw,mh=w-.5,h-.5
svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{mw}mm" height="{mh}mm" viewBox="0 0 {mw} {mh}"><path d="{capsule_path(mw,mh)}" fill="none" stroke="black" stroke-width="0.05"/><ellipse cx="{mw/2}" cy="{mh/2-55}" rx="10.5" ry="9" fill="none" stroke="black" stroke-width="0.05"/><circle cx="{mw/2}" cy="{mh/2+55}" r="8" fill="none" stroke="black" stroke-width="0.05"/><circle cx="{mw/2}" cy="{mh/2+80}" r="3.2" fill="none" stroke="black" stroke-width="0.05"/></svg>'
extra=''.join(f'<circle cx="{mw/2}" cy="{mh/2-y}" r="{r}" fill="none" stroke="black" stroke-width="0.05"/>' for y,r in [(-28,5.7),(30,4),(82,3.3)])
for ww,hh_,yy,rad in [(8.4,12.4,-4,1.2),(12.4,3.4,-40,1.5)]:
    extra+=f'<rect x="{(mw-ww)/2}" y="{mh/2-yy-hh_/2}" width="{ww}" height="{hh_}" rx="{rad}" fill="none" stroke="black" stroke-width="0.05"/>'
svg=svg.replace('</svg>',extra+'</svg>')
(ROOT/'drawings/O02_masca_25.5x193.5_1to1.svg').write_text(svg)
# DXF capsule as one closed LWPOLYLINE, semicircle bulges (units INSUNITS=4 mm).
dxf=['0','SECTION','2','HEADER','9','$INSUNITS','70','4','0','ENDSEC','0','SECTION','2','ENTITIES','0','LWPOLYLINE','100','AcDbEntity','8','CUT','100','AcDbPolyline','90','4','70','1']
for x,y,b in [(0,w/2,0),(0,h-w/2,-1),(w,h-w/2,0),(w,w/2,-1)]: dxf+=['10',str(x),'20',str(y),'42',str(b)]
dxf+=['0','ENDSEC','0','EOF']; (ROOT/'drawings/O01_PMMA_1to1.dxf').write_text('\n'.join(dxf)+'\n')

# Actual BRep sections as vector views. Each connected contour is closed if face is cut.
def section_svg(name,subset,axis,at,u,v,caption):
    # Intersect with a thin slab; draw resulting section edges, sampled analytically.
    normal={'x':V(1,0,0),'y':V(0,1,0),'z':V(0,0,1)}[axis]
    origin={'x':V(at,-500,-100),'y':V(-500,at,-100),'z':V(-500,-500,at)}[axis]
    if axis=='x': plane=Part.makePlane(1000,1000,origin,normal)
    elif axis=='y': plane=Part.makePlane(1000,1000,origin,normal)
    else: plane=Part.makePlane(1000,1000,origin,normal)
    # Infinite analytical plane implemented using oversized thin box common avoids plane UV orientation surprises.
    slab=box(.001,1500,1500,at,0,-500) if axis=='x' else box(1500,.001,1500,0,at,-500) if axis=='y' else box(1500,1500,.001,0,0,at)
    paths=[]; points=[]
    for it in subset:
        sh=it['shape'] if it['space']=='head' and name.startswith('head') else it['world']
        sec=sh.common(slab)
        coords=[]
        for e in sec.Edges:
            ps=e.discretize(Deflection=.15)
            arr=[(getattr(p,u),-getattr(p,v)) for p in ps]
            if len(arr)>1: coords.append(arr); points.extend(arr)
        if coords: paths.append((it,coords))
    if not points: return
    lo=[min(p[i] for p in points) for i in (0,1)]; hi=[max(p[i] for p in points) for i in (0,1)]
    width=hi[0]-lo[0]+20; height=hi[1]-lo[1]+32
    out=[f'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="800" viewBox="{lo[0]-10} {lo[1]-22} {width} {height}"><rect x="{lo[0]-10}" y="{lo[1]-22}" width="{width}" height="{height}" fill="white"/><text x="{lo[0]-8}" y="{lo[1]-12}" font-family="Arial" font-size="4">{caption}</text>']
    for it,lines in paths:
        co='#d28100' if it['mat']=='DIFF' else '#168281' if it['kind']=='reference' else '#243544'
        for arr in lines:
            out.append('<polyline points="'+' '.join(f'{a:.3f},{b:.3f}' for a,b in arr)+f'" fill="none" stroke="{co}" stroke-width="0.25"/>')
    out.append('</svg>'); (ROOT/'drawings'/(name+'.svg')).write_text(''.join(out))
headitems=[i for i in items if i['space']=='head']
section_svg('head_USB_section',headitems,'y',0,'x','z','USB-C: sectiune Y=0; X / Z mm; turcoaz = gabarit neconfirmat')
section_svg('head_camera_section',headitems,'y',55,'x','z','Camera: sectiune Y=55; PMMA / masca / lentila / PCB / leagan')
section_svg('head_tablet_section',headitems,'x',0,'y','z','Tableta: sectiune X=0; Y / Z mm')
section_svg('assembly_center_section',items,'x',20,'y','z','Ansamblu: sectiune X=20; cabluri prin picior / volum sursa')
print('DONE',len(items),'components;',len(probes),'probes; collisions=',len(collisions),flush=True)
