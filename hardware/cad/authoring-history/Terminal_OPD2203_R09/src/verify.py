import sys,json,math
from pathlib import Path
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A,Part,Mesh
R=Path(__file__).resolve().parents[1];V=A.Vector
d=A.openDocument(str(R/'cad/Terminal_OPD2203_R09.FCStd'));report=[]
for a in json.loads((R/'preview/manifest.json').read_text()):
 c=a['id'];s=Part.Shape();s.read(str(R/'step'/(c+'.step')))
 m=Mesh.Mesh(str(R/('probes' if a['kind']=='probe' else 'stl')/(c+'.stl')))
 err=abs(abs(m.Volume)-s.Volume)/max(1,s.Volume)
 report.append(dict(id=c,valid=s.isValid(),solids=len(s.Solids),closed=m.isSolid(),relative_volume_error=err,pass_=s.isValid() and len(s.Solids)==1 and m.isSolid() and err<.015))
for a in report:a['pass']=a.pop('pass_')
(R/'validation/roundtrip.json').write_text(json.dumps(report,indent=2))
leg=d.getObject('B07').Shape;bad=[]
for n in [10,50,90]:
 t=n/100;u=1-t;y=u**3*-61+3*u*u*t*-104+3*u*t*t*25+t**3*-8;z=u**3*58+3*u*u*t*98+3*u*t*t*135+t**3*220
 for x in [0]:
  if leg.isInside(V(x,y,z),.01,True):bad.append([x,y,z])
(R/'validation/cable_channel.json').write_text(json.dumps({'sampled_points':3,'blocked':bad,'pass':not bad,'scope':'three centreline smoke checks; rigid connector verification is in usb_sweep.json'},indent=2))
# Real tablet body versus surrounding structure, excluding datum reference envelopes.
tablet=d.getObject('R01').Shape
intr=[]
for c in ['H01','H04','O01','O03']:
 v=tablet.common(d.getObject(c).Shape).Volume
 if v>.05:intr.append({'part':c,'mm3':v})
(R/'validation/tablet_clearance.json').write_text(json.dumps({'interferences':intr,'pass':not intr,'corner_radius_assumed_mm':11,'real_front_camera_not_measured':True},indent=2))
print('Mesh',sum(a['pass'] for a in report),'/',len(report),'blocked cable samples',len(bad),'tablet intersections',intr,flush=True)

port=d.getObject('P01').Shape;mouths=[]
for x,z in [(-72,22),(-50,22),(-28,22),(-8,22),(8,22),(30,22),(54,22),(80,21)]:
 q=Part.makeBox(.4,.8,.4,V(x-.2,-113.8,z-.2));vol=port.common(q).Volume
 mouths.append({'x':x,'volume':vol,'pass':vol<.001})
(R/'validation/port_mouths.json').write_text(json.dumps(mouths,indent=2))
print('Port openings',sum(a['pass'] for a in mouths),'/',len(mouths))

psu=d.getObject('R02').Shape;body=d.getObject('B07').Shape
v=psu.common(body).Volume
(R/'validation/stand_reinforcement.json').write_text(json.dumps({'source_reserved_mm':[92,64.02,39.02],'rib_inner_abs_x_mm':60,'source_half_width_mm':46,'nominal_side_gap_mm':14,'intersection_mm3':v,'pass':v<.05,'load_rating':'not physically established'},indent=2))
print('PSU reserve intersection',v)
# Root front wall must not be perforated by vertical cable entry.
rootwall=[]
for t in [.02,.04,.06,.08,.10]:
 u=1-t;y=u**3*-61+3*u*u*t*-104+3*u*t*t*25+t**3*-8;z=u**3*58+3*u*u*t*98+3*u*t*t*135+t**3*220
 q=V(0,y+13,z);ok=body.isInside(q,.001,False)
 rootwall.append({'point':[q.x,q.y,q.z],'pass':ok})
(R/'validation/root_wall.json').write_text(json.dumps(rootwall,indent=2))
print('Root closed',sum(a['pass'] for a in rootwall),'/',len(rootwall))

# Upper cable outlet must open into head interior, while rear skin remains closed.
pose=A.Placement(V(-12,10,240),A.Rotation(V(1,0,0),120))
probes=[]
for z in [33,35,37,39]:
 q=pose.multVec(V(12,-30,z));probes.append({'local_z':z,'void':not leg.isInside(q,.001,True)})
q=pose.multVec(V(12,-30,47));closed=leg.isInside(q,.001,False)
(R/'validation/upper_cable.json').write_text(json.dumps({'pass':all(p['void'] for p in probes) and closed,'center_path':probes,'rear_skin_closed':closed,'rear_skin_sample_local_z_mm':47,'scope':'point samples; bend radius/plug sweep require physical cable'},indent=2))
flush=[]
inv=pose.inverse()
for code,plane in [('V51',36.3),('V52',36.3),('V53',36.3),('V54',36.3),('V61',39.6),('V62',39.6)]:
 sh=d.getObject(code).Shape.copy();sh.Placement=inv.multiply(sh.Placement)
 delta=sh.BoundBox.ZMax-plane;flush.append({'id':code,'protrusion_mm':delta,'pass':abs(delta)<.02})
(R/'validation/flush_screws.json').write_text(json.dumps(flush,indent=2))
print('Upper cable enclosed',all(p['void'] for p in probes) and closed,'flush',sum(a['pass'] for a in flush),'/',len(flush))
# Reserved continuous LED envelopes versus all printed parts, not point samples.
manifest=json.loads((R/'preview/manifest.json').read_text())
led=[]
for ref in ['R04','R05']:
 strip=d.getObject(ref).Shape
 for it in manifest:
  if it['kind']!='print':continue
  other=d.getObject(it['id']).Shape
  if not strip.BoundBox.intersect(other.BoundBox):continue
  vol=strip.common(other).Volume
  if vol>.05:led.append({'strip':ref,'part':it['id'],'mm3':vol})
(R/'validation/led_envelopes.json').write_text(json.dumps({'pass':not led,'pcb_width_reserve_mm':8.5,'radial_thickness_assumed_mm':1.5,'interferences':led},indent=2))
print('LED continuous envelopes',led,flush=True)
# Rigid 16x10x30mm plug along actual centreline, including cover crossing.
plug=Part.makeBox(16,10,30,V(-8,-5,-15));poses=[]
for i in range(19):
 t=i*.05;u=1-t
 y=u**3*-61+3*u*u*t*-104+3*u*t*t*25+t**3*-8
 z=u**3*58+3*u*u*t*98+3*u*t*t*135+t**3*220
 dy=3*(-43*u*u+258*u*t-33*t*t);dz=3*(40*u*u+74*u*t+85*t*t)
 q=plug.copy();q.rotate(V(),V(1,0,0),-math.degrees(math.atan2(dy,dz)));q.translate(V(0,y,z));poses.append(q)
conflicts=[]
for idx,q in enumerate(poses):
 for name in ['B07','H04']:
  vol=q.common(d.getObject(name).Shape).Volume
  if vol>.05:conflicts.append({'t':round(idx*.05,2),'part':name,'mm3':vol})
(R/'validation/usb_sweep.json').write_text(json.dumps({'pass':not conflicts,'rigid_plug_mm':[16,10,30],'positions':19,'interferences':conflicts,'scope':'discrete rigid-pose check before tablet/PSU installation; not a continuous swept-volume or actual cable certification'},indent=2))
print('USB plug path',conflicts,flush=True)
usb=d.getObject('R03').Shape;fits=[]
for name in ['H01','H04','O01','O03']:
 vol=usb.common(d.getObject(name).Shape).Volume
 if vol>.05:fits.append({'part':name,'mm3':vol})
(R/'validation/usb_service.json').write_text(json.dumps({'pass':not fits,'interferences':fits,'assumed_right_angle_body_mm':[16,30,10]},indent=2))
print('USB service housing',fits,flush=True)

thread_checks=[]
for code,L,plane in [('V51',14,32.3),('V52',14,32.3),('V53',14,32.3),('V54',14,32.3),('V61',16.3,35.6),('V62',16.3,35.6)]:
 sh=d.getObject(code).Shape.copy();sh.Placement=pose.inverse().multiply(sh.Placement)
 span=sh.BoundBox.ZLength
 thread_checks.append({'id':code,'expected_total_mm':L+4,'actual_total_mm':span,'pass':abs(span-(L+4))<.02 and sh.Volume>800})
(R/'validation/complete_screws.json').write_text(json.dumps(thread_checks,indent=2));print('Complete screws',thread_checks,flush=True)
