import sys,csv,json
from pathlib import Path
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A,Part,MeshPart
R=Path(__file__).resolve().parents[1]
rows=list(csv.DictReader(open(R/'docs/piese_si_imprimare.csv')))
for row in rows:
 if row['ID'] not in ('H01','H02','H03','H04','B01','B02','B03','B04') and not row['ID'].startswith(('P','T2')):continue
 s=Part.Shape();s.read(str(R/'step'/(row['ID']+'.step')))
 if row['ID'].startswith('P'):
  s.rotate(A.Vector(),A.Vector(1,0,0),-90);desc='Flansa portului pe pat, detalii in sus'
 elif row['ID'].startswith('T2'):
  s.rotate(A.Vector(),A.Vector(0,1,0),90);desc='Fata 10x4 pe pat'
 elif row['ID']=='B04':
  s.rotate(A.Vector(),A.Vector(1,0,0),90);desc='Fata panoului pe pat, suport la urechi'
 else:
  s.rotate(A.Vector(),A.Vector(1,0,0),90);s.rotate(A.Vector(),A.Vector(0,0,1),-45);desc='Pe muchie, diagonal -45 grade; suporturi interioare obligatorii'
 b=s.BoundBox;s.translate(A.Vector(-b.XMin,-b.YMin,-b.ZMin));b=s.BoundBox
 MeshPart.meshFromShape(Shape=s,LinearDeflection=.07,AngularDeflection=.18,Relative=False).write(str(R/'stl'/(row['ID']+'.stl')))
 for k,v in [('X_print_mm',b.XLength),('Y_print_mm',b.YLength),('Z_print_mm',b.ZLength)]:row[k]=round(v,2)
 row['Orientare']=desc
 row['Brim5_in_256']=max(b.XLength+10,b.YLength+10,b.ZLength)<=256
with open(R/'docs/piese_si_imprimare.csv','w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
