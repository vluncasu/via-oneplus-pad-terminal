import sys,json,math
from pathlib import Path
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A,Part,Mesh
R=Path(__file__).resolve().parents[1];V=A.Vector
d=A.openDocument(str(R/'cad/Terminal_OPD2203_R07.FCStd'));report=[]
for a in json.loads((R/'preview/manifest.json').read_text()):
 c=a['id'];s=Part.Shape();s.read(str(R/'step'/(c+'.step')))
 m=Mesh.Mesh(str(R/('probes' if a['kind']=='probe' else 'stl')/(c+'.stl')))
 err=abs(abs(m.Volume)-s.Volume)/max(1,s.Volume)
 report.append(dict(id=c,valid=s.isValid(),solids=len(s.Solids),closed=m.isSolid(),relative_volume_error=err,pass_=s.isValid() and len(s.Solids)==1 and m.isSolid() and err<.015))
for a in report:a['pass']=a.pop('pass_')
(R/'validation/roundtrip.json').write_text(json.dumps(report,indent=2))
leg=d.getObject('B07').Shape;bad=[]
for n in range(4,97,4):
 t=n/100;u=1-t;y=u**3*-61+3*u*u*t*-104+3*u*t*t*25+t**3*-8;z=u**3*58+3*u*u*t*98+3*u*t*t*135+t**3*198
 for x in [-3,0,3]:
  if leg.isInside(V(x,y,z),.01,True):bad.append([x,y,z])
(R/'validation/cable_channel.json').write_text(json.dumps({'sampled_points':72,'blocked':bad,'pass':not bad,'scope':'center corridor samples, not connector sweep'},indent=2))
# Real tablet body versus surrounding structure, excluding datum reference envelopes.
tablet=d.getObject('R01').Shape
intr=[]
for c in ['H01','H04','O01','O03']:
 v=tablet.common(d.getObject(c).Shape).Volume
 if v>.05:intr.append({'part':c,'mm3':v})
(R/'validation/tablet_clearance.json').write_text(json.dumps({'interferences':intr,'pass':not intr,'corner_radius_assumed_mm':11,'real_front_camera_not_measured':True},indent=2))
print('Mesh',sum(a['pass'] for a in report),'/',len(report),'blocked cable samples',len(bad),'tablet intersections',intr)

port=d.getObject('P01').Shape;mouths=[]
for x,z in [(-72,22),(-50,22),(-28,22),(-8,22),(8,22),(30,22),(54,22),(80,21)]:
 q=Part.makeBox(.4,.8,.4,V(x-.2,-113.8,z-.2));vol=port.common(q).Volume
 mouths.append({'x':x,'volume':vol,'pass':vol<.001})
(R/'validation/port_mouths.json').write_text(json.dumps(mouths,indent=2))
print('Port openings',sum(a['pass'] for a in mouths),'/',len(mouths))

psu=d.getObject('R02').Shape;body=d.getObject('B07').Shape
v=psu.common(body).Volume
(R/'validation/source_reinforcement.json').write_text(json.dumps({'source_reserved_mm':[92,64.02,39.02],'rib_inner_abs_x_mm':54,'source_half_width_mm':46,'nominal_side_gap_mm':8,'intersection_mm3':v,'pass':v<.05,'load_rating':'not physically established'},indent=2))
print('PSU reserve intersection',v)
# Root front wall must not be perforated by vertical cable entry.
rootwall=[]
for t in [.02,.04,.06,.08,.10]:
 u=1-t;y=u**3*-61+3*u*u*t*-104+3*u*t*t*25+t**3*-8;z=u**3*58+3*u*u*t*98+3*u*t*t*135+t**3*198
 q=V(0,y+11,z);ok=body.isInside(q,.001,False)
 rootwall.append({'point':[q.x,q.y,q.z],'pass':ok})
(R/'validation/root_wall.json').write_text(json.dumps(rootwall,indent=2))
print('Root closed',sum(a['pass'] for a in rootwall),'/',len(rootwall))
