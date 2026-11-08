import sys,json
from pathlib import Path
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A,Part
R=Path(__file__).resolve().parents[1];V=A.Vector
ss={}
for code in ['S01','S02','B01','B07','P01','P05','P07']:
 s=Part.Shape();s.read(str(R/'step'/f'{code}.step'));ss[code]=s
leg=Part.makeCompound([ss['S01'],ss['S02']]);out=[]
# Exported stand and base are in mirrored world coordinates.
for label,pts in [('lower_wire_opening',[(20,-63,z) for z in range(40,68)]),('S_wire_corridor',[(20,((1-t)**3*-61+3*(1-t)**2*t*-104+3*(1-t)*t*t*25+t**3*-8)+5,(1-t)**3*58+3*(1-t)**2*t*98+3*(1-t)*t*t*135+t**3*198) for t in [i/100 for i in range(5,91)]]),('upper_wire_opening',[(32,10+15-.8660254*z,240-.8660254*30-.5*z) for z in range(34,40)])]:
 blocked=[]
 for p in pts:
  for name in ['S01','S02','B01','B07']:
   if ss[name].isInside(V(*p),.001,True):blocked.append({'point':p,'part':name})
 out.append({'test':label,'samples':len(pts),'blocked':blocked,'pass':not blocked})
out.append({'test':'integrated_body_rear','Ymin':ss['B01'].BoundBox.YMin,'recess_mm':ss['B01'].BoundBox.YMin+115,'pass':ss['B01'].BoundBox.YMin>=-115.001})
(R/'validation/r04_details.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
