import sys,json
from pathlib import Path
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A,Part
R=Path(__file__).resolve().parents[1]
d=A.openDocument(str(R/'cad/Terminal_OPD2203_R04.FCStd'))
manifest=json.loads((R/'preview/manifest.json').read_text()); result=[]
for it in manifest:
 s=Part.Shape();s.read(str(R/'step'/(it['id']+'.step')))
 if it['space']=='head':s.Placement=A.Placement(A.Vector(12,10,240),A.Rotation(A.Vector(1,0,0),120)).multiply(s.Placement)
 target=d.getObject(it['id']).Shape
 b=s.BoundBox;t=target.BoundBox
 err=max(abs(getattr(b,k)-getattr(t,k)) for k in ['XMin','XMax','YMin','YMax','ZMin','ZMax'])
 diff=None
 if it['id'] in ['H01','H03','O03']:
  diff=abs(s.Volume+target.Volume-2*s.common(target).Volume)
 result.append({'id':it['id'],'bbox_error_mm':err,'symmetric_difference_mm3':diff,'pass':err<.001 and (diff is None or diff<.05)})
(R/'validation/assembly_frames.json').write_text(json.dumps(result,indent=2))
print('Rigid export alignment:',sum(x['pass'] for x in result),'/',len(result));print([x for x in result if not x['pass']])
