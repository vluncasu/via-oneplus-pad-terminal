import sys,json
from pathlib import Path
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A,Part
R=Path(__file__).resolve().parents[1];V=A.Vector
d=A.openDocument(str(R/'cad/Terminal_OPD2203_R12.FCStd'));H=A.Placement(V(-12,10,240),A.Rotation(V(1,0,0),120))
def local(c):
 s=d.getObject(c).Shape.copy();s.Placement=H.inverse().multiply(s.Placement);return s
h=local('H01');results={}
for c,shift in [('O01',V(0,0,-.6)),('H05',V(0,1.2,0))]:
 s=local(c);s.translate(shift);v=s.common(h).Volume
 results[c]={'attempted_locked_motion_mm':list(shift),'stop_intersection_mm3':v,'retaining_shoulder_present':v>.05}
print('RETENTION',results,flush=True)
sweep=Part.makeBox(258.03,420,6.54,V(-129.015,-94.705,0))
sweep=sweep.makeFillet(11,[e for e in sweep.Edges if abs(e.Vertexes[-1].Point.z-e.Vertexes[0].Point.z)>6.53])
travel=[]
for c in ['H01','H04','O01']:
 common=sweep.common(local(c));v=common.Volume;travel.append({'id':c,'mm3':v})
 if v>.05:print('BLOCK',c,[(s.Volume,str(s.BoundBox)) for s in common.Solids],flush=True)
results['tablet_nominal_extraction']={'collisions':travel,'scope':'rectangular body only; excludes camera protrusion, buttons and connector; H05 removed'}
(R/'validation/retention_and_extraction.json').write_text(json.dumps(results,indent=2));print('TRAVEL',travel,flush=True)
