"""Remove the 0.1mm flange membrane; keep the same blind rear wall and guides."""
import sys,json,csv,math
from pathlib import Path
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A, Part,MeshPart
from mesh_cleanup import clean
V=A.Vector;ROOT=Path(__file__).resolve().parents[1]
P=json.loads((ROOT/'src/parameters.json').read_text())
doc=A.openDocument(str(ROOT/'cad/Terminal_OPD2203_R03.FCStd'))
rows=list(csv.DictReader(open(ROOT/'docs/piese_si_imprimare.csv')))
manifest=json.loads((ROOT/'preview/manifest.json').read_text());checks=json.loads((ROOT/'validation/checks.json').read_text())
def box(w,h,d,x=0,y=0,z=0):return Part.makeBox(w,h,d,V(x-w/2,y-h/2,z))
ports=[('USB-A',-88,13,6),('USB-A',-68,13,6),('USB-A',-48,13,6),('USB-A',-28,13,6),('USB-C',-9,9,4),('USB-C',7,9,4),('RJ45',28,14,13),('HDMI',51,15,6),('AUDIO',72,6,6)]
original={code:doc.getObject(code).Shape.copy() for code in ['P'+str(i).zfill(2) for i in range(1,10)]}
changed=[]
for i,(typ,x,w,h) in enumerate(ports,1):
    for code in ['P'+str(i).zfill(2)]+(['Q61'] if typ=='RJ45' else []):
        sh=original['P07' if code=='Q61' else code].copy()
        tool=box(w-2.4,.6,h-2.4,-x,-111.8,22-h/2+1.2)
        if typ=='AUDIO':tool=Part.makeCylinder(1.65,.6,V(-x,-112.1,22),V(0,1,0))
        old=sh.Volume;sh=sh.cut(tool).removeSplitter()
        if typ=='RJ45':
            for j in range(8):sh=sh.fuse(box(.65,4,1.2,-x-3.85+j*1.1,-102.1,17.8))
            sh=sh.fuse(box(5,3.5,1.5,-x,-102.3,25.5))
        elif typ in ('USB-A','USB-C','HDMI'):sh=sh.fuse(box(w-3.2,5,.9,-x,-103,21.55))
        sh=sh.removeSplitter();assert sh.isValid() and len(sh.Solids)==1
        sh.exportStep(str(ROOT/'step'/(code+'.step')))
        out=sh.copy();out.rotate(V(),V(1,0,0),-90 if code.startswith('P') else 0)
        bb=out.BoundBox;out.translate(V(-bb.XMin,-bb.YMin,-bb.ZMin))
        mesh=MeshPart.meshFromShape(Shape=out,LinearDeflection=.07,AngularDeflection=.18,Relative=False);clean(mesh);assert mesh.isSolid()
        mesh.write(str(ROOT/('probes' if code.startswith('Q') else 'stl')/(code+'.stl')))
        row=next(r for r in rows if r['ID']==code);row['Volum_cm3']=round(sh.Volume/1000,3)
        if code.startswith('P'):
            doc.getObject(code).Shape=sh
            wm=MeshPart.meshFromShape(Shape=sh,LinearDeflection=.13,AngularDeflection=.22,Relative=False);clean(wm);wm.write(str(ROOT/'preview'/(code+'.stl')))
            next(r for r in manifest if r['id']==code)['volume_mm3']=sh.Volume
        # A ray through the mouth must hit only the blind back wall.
        sample=box(1,.8,1,-x,-111.6,22 if typ=='AUDIO' else 22-h/2+1.8)
        overlap=sh.common(sample).Volume
        assert overlap<.001,(code,overlap)
        if typ=='USB-A':assert sh.common(box(1,1,.4,-x,-103,21.8)).Volume>.39
        if typ=='RJ45':assert sh.common(box(.4,1,.6,-x-3.85,-103,18)).Volume>.23
        changed.append({'id':code,'removed_membrane_mm3':old-sh.Volume,'mouth_probe_overlap_mm3':overlap})
doc.recompute();doc.save()
assembly=Part.makeCompound([doc.getObject(m['id']).Shape for m in manifest]);assembly.exportStep(str(ROOT/'step/Terminal_OPD2203_R03_assembly.step'))
with open(ROOT/'docs/piese_si_imprimare.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
(ROOT/'preview/manifest.json').write_text(json.dumps(manifest,indent=2))
items=[{'id':m['id'],'kind':m['kind'],'mat':m['material'],'shape':doc.getObject(m['id']).Shape,'world':doc.getObject(m['id']).Shape} for m in manifest]
hw,hh,hr=P['head_w'],P['head_h'],P['head_r'];bw,bd,br=P['base_w'],P['base_d'],P['base_r']
src=(ROOT/'src/build.py').read_text();a=src.index('headlen=');b=src.index('# Analytic 1:1',a);exec(src[a:b])
(ROOT/'validation/port_mouths.json').write_text(json.dumps(changed,indent=2));print(changed)
