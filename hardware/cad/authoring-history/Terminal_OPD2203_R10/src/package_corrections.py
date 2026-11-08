import csv,json,struct,zipfile,shutil,xml.etree.ElementTree as E,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1];old=R.parent/'Terminal_OPD2203_R09'
NS='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';E.register_namespace('',NS)
shutil.copytree(old/'plates',R/'plates',dirs_exist_ok=True)
positions=list(csv.DictReader(open(R/'plates/placements.csv')))
changed=['H01','O01','O03']
def mesh(path):
 data=path.read_bytes();n=struct.unpack_from('<I',data,80)[0];assert len(data)==84+50*n
 vertices=[];lookup={};faces=[]
 for k in range(n):
  f=[]
  for j in range(3):
   p=struct.unpack_from('<3f',data,84+50*k+12+12*j)
   if p not in lookup:lookup[p]=len(vertices);vertices.append(p)
   f.append(lookup[p])
  faces.append(f)
 return vertices,faces
updated=[]
for plate in sorted({p['plate'] for p in positions if p['id'] in changed}):
 path=R/'plates'/(plate+'.3mf')
 with zipfile.ZipFile(path) as z:files={n:z.read(n) for n in z.namelist()}
 model=E.fromstring(files['3D/3dmodel.model'])
 for p in positions:
  if p['plate']!=plate or p['id'] not in changed:continue
  obj=next(o for o in model.findall('.//{'+NS+'}object') if o.get('name')==p['id'])
  obj.remove(obj.find('{'+NS+'}mesh'));m=E.SubElement(obj,'{'+NS+'}mesh')
  vv=E.SubElement(m,'{'+NS+'}vertices');tt=E.SubElement(m,'{'+NS+'}triangles')
  verts,faces=mesh(R/'stl'/(p['id']+'.stl'))
  for x,y,z in verts:E.SubElement(vv,'{'+NS+'}vertex',x=str(x+float(p['x'])),y=str(y+float(p['y'])),z=str(z))
  for a,b,c in faces:E.SubElement(tt,'{'+NS+'}triangle',v1=str(a),v2=str(b),v3=str(c))
  updated.append(p['id'])
 files['3D/3dmodel.model']=E.tostring(model,encoding='utf-8',xml_declaration=True)
 with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:
  for n,b in files.items():z.writestr(n,b)
assert sorted(updated)==sorted(changed)
(R/'validation/plates_update.json').write_text(json.dumps({'replaced_meshes':updated,'positions':'retained from R09; unchanged outer footprints','supports_validated':False},indent=2))
subprocess.run([sys_executable:='python3',str(R/'src/organize_stl.py')],check=True)
for p in (R/'cad').iterdir():
 if p.name!='Terminal_OPD2203_R10.FCStd':p.unlink()
for p in (R/'step').glob('*assembly.step'):p.unlink()
# CADs grouped by filament, independent of display attributes in STEP/STL.
out=R/'CAD_PE_CULORI';out.mkdir(exist_ok=True)
for row in csv.DictReader(open(R/'docs/piese_si_imprimare.csv')):
 c=row['ID'];group='REFERINTE_NU_IMPRIMA' if c.startswith('R') else ('PROBE_ALB' if c.startswith('Q') else ('NEGRU' if row['Material']=='PETG_NEGRU' else 'ALB'))
 dest=out/group;dest.mkdir(exist_ok=True);shutil.copy2(R/'step'/(c+'.step'),dest/(c+'.step'))
print('Packaged corrected meshes, STEP colour groups and Romanian STL folders',flush=True)
