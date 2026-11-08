import sys,json
from pathlib import Path
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A,Part,MeshPart
from mesh_cleanup import clean
R=Path(__file__).resolve().parents[1];V=A.Vector
d=A.openDocument(str(R/'cad/Terminal_OPD2203_R14.FCStd'))
H=A.Placement(V(-12,10,240),A.Rotation(V(1,0,0),120))
def local(c):
 s=d.getObject(c).Shape.copy();s.Placement=H.inverse().multiply(s.Placement);return s
def moved(s,v):
 c=s.copy();c.translate(V(*v));return c
report={}
report['bar_locked']=[{'direction':v,'intersection_mm3':moved(local('H05'),v).common(local(b)).Volume,'stop':b} for v,b in [((0,0,-1),'H01'),((0,0,1),'H01'),((0,1,0),'H06')]]
report['bar_unlocked_path']=[{'rise_mm':y,'intersection_mm3':moved(local('H05'),(0,y,0)).common(local('H01')).Volume} for y in [2,5,10,16]]
sweep=Part.makeBox(258.03,420,6.54,V(-129.015,-94.705,0));sweep=sweep.makeFillet(11,[e for e in sweep.Edges if abs(e.Vertexes[-1].Point.z-e.Vertexes[0].Point.z)>6.53])
report['tablet_nominal_sweep']=[{'id':c,'mm3':sweep.common(local(c)).Volume} for c in ['H01','H04','O01','O06']]
report['scope']='H05 and H06 removed for tablet sweep; no physical tablet bump/buttons/cable or load/deformation validation.'
(R/'validation/service.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
