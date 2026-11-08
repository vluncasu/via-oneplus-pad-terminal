import sys,json
from pathlib import Path
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A,Part
R=Path(__file__).resolve().parents[1];V=A.Vector
D=A.openDocument(str(R/'cad/Terminal_OPD2203_R06.FCStd'))
def shape(code):return D.getObject(code).Shape
leg=Part.makeCompound([shape('S01'),shape('S02')]);lid=shape('B07');body=shape('B01');out=[]
def test(name,ok,**kw):out.append(dict(test=name,pass_=bool(ok),**kw))
for x in [-60,60]:
 for y in [-69,-43]:
  # A shaft fits clearance before insert; insert bore uses metal threads in assembly.
  shaft=Part.makeCylinder(2,20,V(x,y,44))
  overlap=shaft.common(leg).Volume+shaft.common(lid).Volume
  cap=Part.makeCylinder(2.1,1.5,V(x,y,64.25))
  wall=cap.common(leg).Volume/cap.Volume
  test(f'M4x20 {x},{y}',overlap<.05 and wall>.99,plastic_intersection_mm3=overlap,insert_start_z=58,insert_end_z=64,tip_z=64,engagement_mm=6,roof_probe_solid_fraction=wall)
for x,y in [(-85,-80),(85,-80),(-85,80),(85,80)]:
 shaft=Part.makeCylinder(1.5,6,V(x,y,19.1));overlap=shaft.common(body).Volume+shaft.common(lid).Volume
 test(f'B07 M3x6 {x},{y}',overlap<.05,plastic_intersection_mm3=overlap,tip_z=25.1,insert_start_z=21,insert_length=4)
# Top roof must be closed at old four corner holes, including their complete footprint.
for x in [-105,105]:
 for y in [-94,94]:
  q=Part.makeCylinder(4,1,V(x,y,30.2));f=q.common(lid).Volume/q.Volume
  test(f'closed roof {x},{y}',f>.99,solid_fraction=f)
# Rear seam has 0.30mm axial running clearance: sample continuous roof behind the wall.
for x in [-90,-45,0,45,90]:
 q=Part.makeBox(2,1,1,V(x-1,-114.5,30.5));f=q.common(lid).Volume/q.Volume
 test(f'rear roof {x}',f>.99,solid_fraction=f)
T=A.Placement(V(12,10,240),A.Rotation(V(1,0,0),120))
for x in [-52,52]:
 for y in [-48,-12]:
  shaft=Part.makeCylinder(2,10,V(x,y,30.4));shaft.Placement=T.multiply(shaft.Placement)
  overlap=shaft.common(leg).Volume+shaft.common(shape('H03')).Volume
  test(f'head M4x10 {x},{y}',overlap<.05,plastic_intersection_mm3=overlap,local_tip_z=40.4,nut_pocket_start_z=33.9,nut_pocket_end_z=37.7)
for x in [-100,-35,35,100]:
 for y in [-98,98]:
  shaft=Part.makeCylinder(1.5,30,V(x,y,5.8));shaft.Placement=T.multiply(shaft.Placement)
  overlap=sum(shaft.common(shape(c)).Volume for c in ['H01','H03','H04'])
  test(f'head cover M3x30 {x},{y}',overlap<.05,plastic_intersection_mm3=overlap,insert_start_local_z=6,insert_end_local_z=12,tip_local_z=5.8)
for x,y in [(-105,-94),(-105,94),(105,-94),(105,94),(0,102)]:
 shaft=Part.makeCylinder(1.5,8,V(x,y,4.5));overlap=shaft.common(body).Volume+shaft.common(shape('B03')).Volume
 test(f'base cover M3x8 {x},{y}',overlap<.05,plastic_intersection_mm3=overlap,insert_start_z=7,insert_end_z=13,tip_z=12.5)
for x in [-60,60]:
 for y in [-69,-43]:
  tool=Part.makeCylinder(2.5,43.8,V(x,y,0))
  overlap=tool.common(body).Volume+tool.common(lid).Volume
  test(f'base tool access {x},{y}',overlap<.05,plastic_intersection_mm3=overlap,tool_diameter_mm=5,service_cover_removed=True)
for a in out:a['pass']=a.pop('pass_')
(R/'validation/fasteners.json').write_text(json.dumps(out,indent=2));print('Fasteners and roof:',sum(a['pass'] for a in out),'/',len(out));print([a for a in out if not a['pass']])
