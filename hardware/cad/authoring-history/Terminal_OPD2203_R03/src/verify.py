"""Independent STEP reimport, exported mesh edge check, service sweeps, 3MF writer."""
import sys, json, csv, math, zipfile, xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A, Part, Mesh
V=A.Vector
ROOT=Path(__file__).resolve().parents[1]
rows=list(csv.DictReader(open(ROOT/'docs/piese_si_imprimare.csv')))
P=json.loads((ROOT/'src/parameters.json').read_text())
results=[]
for r in rows:
    code=r['ID']; s=Part.Shape(); s.read(str(ROOT/'step'/(code+'.step')))
    path=ROOT/('probes' if code.startswith('Q') else 'stl')/(code+'.stl')
    m=Mesh.Mesh(str(path)); vertices,facets=m.Topology
    edges=Counter(tuple(sorted((f[i],f[(i+1)%3]))) for f in facets for i in range(3))
    ok=s.isValid() and len(s.Solids)==1 and m.isSolid() and all(n==2 for n in edges.values())
    volume_ok=abs(s.Volume/1000-float(r['Volum_cm3']))<max(.003,(s.Volume/1000)*1e-5) # STEP integration and rounded CSV tolerance
    results.append({'id':code,'step_valid':s.isValid(),'step_solid_count':len(s.Solids),'volume_roundtrip_ok':volume_ok,'mesh_solid':m.isSolid(),'all_edges_two_faces':all(n==2 for n in edges.values()),'pass':ok and volume_ok})
(ROOT/'validation/roundtrip_mesh.json').write_text(json.dumps(results,indent=2))

def read(code):
    s=Part.Shape(); s.read(str(ROOT/'step'/(code+'.step'))); return s
H=read('H01'); mask=read('O02'); pmma=read('O01'); usb=read('R03'); cass=read('O03'); shell=read('H03')
sweeps=[]
def run(name,moving,obstacles,vector,samples):
    worst=0; first=None
    for k in range(samples+1):
        s=moving.copy(); s.translate(V(*vector)*(k/samples))
        for code,o in obstacles:
            if not s.BoundBox.intersect(o.BoundBox): continue
            vol=s.common(o).Volume
            if vol>worst: worst=vol; first={'fraction':k/samples,'against':code}
    sweeps.append({'test':name,'steps':samples,'max_overlap_mm3':round(worst,6),'worst_position':first,'pass':worst<.05,'scope':'sampled rigid CAD sweep; real cable excluded'})
run('USB scoatere axiala 6mm dupa demontarea casetei',usb,[('H01',H),('O01',pmma),('O02',mask)],(6,0,0),24)
run('Tableta extragere 45mm dupa scoaterea H03/H04 si opritoarelor',read('R01'),[('H01',H)],(0,0,45),18)
run('Caseta extragere 40mm, fara masca, inainte de deconectare',cass,[('H01',H),('H03',shell),('USB',usb)],(0,0,40),24)
run('P07 Ethernet glisare +Z22 fara P10, panou demontat',read('P07'),[('B04',read('B04'))],(0,0,22),22)
run('P10 scoatere +Z12 fara stifturi P11 P12',read('P10'),[('B04',read('B04'))],(0,0,12),24)
# In real service mask stays at front until cable unplugged.
(ROOT/'validation/service_sweeps.json').write_text(json.dumps(sweeps,indent=2))

# Geometry-only 3MF in actual assembly coordinates. No slicer/G-code parameters.
ns='http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
ET.register_namespace('',ns)
model=ET.Element('{'+ns+'}model',{'unit':'millimeter','xml:lang':'en-US'})
meta=ET.SubElement(model,'{'+ns+'}metadata',{'name':'Title'}); meta.text='Terminal OPD2203 R02 geometry only, not sliced'
res=ET.SubElement(model,'{'+ns+'}resources'); build=ET.SubElement(model,'{'+ns+'}build')
manifest=json.loads((ROOT/'preview/manifest.json').read_text())
for i,it in enumerate(manifest,1):
    m=Mesh.Mesh(str(ROOT/'preview'/(it['id']+'.stl'))); verts,facets=m.Topology
    ob=ET.SubElement(res,'{'+ns+'}object',{'id':str(i),'type':'model','name':it['id']+' '+it['name']})
    msh=ET.SubElement(ob,'{'+ns+'}mesh'); vs=ET.SubElement(msh,'{'+ns+'}vertices'); ts=ET.SubElement(msh,'{'+ns+'}triangles')
    for p in verts: ET.SubElement(vs,'{'+ns+'}vertex',dict(x=f'{p.x:.6f}',y=f'{p.y:.6f}',z=f'{p.z:.6f}'))
    for f in facets: ET.SubElement(ts,'{'+ns+'}triangle',dict(v1=str(f[0]),v2=str(f[1]),v3=str(f[2])))
    ET.SubElement(build,'{'+ns+'}item',{'objectid':str(i)})
data=ET.tostring(model,encoding='utf-8',xml_declaration=True)
out=ROOT/'cad/Terminal_R03_assembly_geometry_only.3mf'
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
    z.writestr('[Content_Types].xml','<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
    z.writestr('_rels/.rels','<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
    z.writestr('3D/3dmodel.model',data)
with zipfile.ZipFile(out) as z:
    parsed=ET.fromstring(z.read('3D/3dmodel.model')); count=len(parsed.findall('.//{'+ns+'}object'))
    assert parsed.attrib['unit']=='millimeter' and count==len(manifest) and z.testzip() is None
(ROOT/'validation/3mf_check.json').write_text(json.dumps({'unit':'millimeter','objects':count,'xml_reparsed':True,'zip_crc_ok':True,'bambu_project':False,'sliced':False},indent=2))
print('Roundtrip:',sum(r['pass'] for r in results),'/',len(results))
print('Service:',json.dumps(sweeps,indent=2))
