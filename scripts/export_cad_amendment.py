import sys,json,os
from pathlib import Path
if os.getenv('FREECAD_LIB'):sys.path.insert(0,os.environ['FREECAD_LIB'])
import FreeCAD as A,Part,MeshPart
repo=Path(__file__).resolve().parents[1]
native=repo/'hardware/cad/native';d=A.openDocument(str(native/'terminal-opd2203-r14-baseline.FCStd'))
labels=json.loads((repo/'hardware/cad/english-part-labels.json').read_text())
H=A.Placement(A.Vector(-12,10,240),A.Rotation(A.Vector(1,0,0),120))
metrics=[]
for ob in d.Objects:
 if hasattr(ob,'Shape') and ob.Name in labels:
  ob.Label=ob.Name+' '+labels[ob.Name].replace('_',' ')
  s=ob.Shape;b=s.BoundBox
  metrics.append(dict(id=ob.Name,valid=s.isValid(),solids=len(s.Solids),world_bounds_mm=[b.XLength,b.YLength,b.ZLength],volume_mm3=s.Volume))
d.saveAs(str(native/'terminal-opd2203-r14-baseline.FCStd'))
# Preserve the front datum of the optical film while halving its local thickness.
s=d.getObject('O05').Shape.copy();s.Placement=H.inverse().multiply(s.Placement)
m=A.Matrix();m.A33=.5;m.A34=-.3
thin=s.transformGeometry(m)
assert thin.isValid() and len(thin.Solids)==1
assert abs(thin.BoundBox.ZLength-.2)<.0001
thin.exportStep(str(repo/'hardware/cad/step/O05_captive_optical_film_0p20mm.step'))
w=thin.copy();w.Placement=H.multiply(thin.Placement)
d.getObject('O05').Shape=w;d.getObject('O05').Label='O05 captive optical film 0.20 mm'
mesh=MeshPart.meshFromShape(Shape=w,LinearDeflection=.03,AngularDeflection=.1,Relative=False);mesh.write(str(repo/'hardware/cad/assembly-meshes/O05.stl'))
d.recompute();d.saveAs(str(native/'via-oneplus-pad-r14-1-film-020.FCStd'))
(repo/'hardware/validation/native-shape-audit.json').write_text(json.dumps({'scope':'Native FreeCAD shape validity, not physical print validation. Baseline O05 metrics below are 0.40 mm; amended O05 is 0.20 mm.','parts':metrics,'amendment':{'part':'O05','thickness_mm':thin.BoundBox.ZLength,'bounds_mm':[thin.BoundBox.XLength,thin.BoundBox.YLength,thin.BoundBox.ZLength],'valid':thin.isValid()}},indent=2))
print('CAD_EXPORTED',len(metrics),'film',thin.BoundBox.ZLength)
