"""Pack oriented meshes onto 256mm plates; preserve Z and FDM orientations.
Separate materials, tests, production. Conservative 5mm footprint expansion,
actual mesh-vertex footprint versus installed P1S exclusion rectangle.
Output geometry-only 3MF (one file per plate) and visual plate maps.
"""
import sys,json,csv,math,zipfile,xml.etree.ElementTree as E
from pathlib import Path
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD, Mesh
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'plates'; OUT.mkdir(exist_ok=True)
rows=list(csv.DictReader(open(ROOT/'docs/piese_si_imprimare.csv')))
plates=[]; margin=5
def load(r):
    m=Mesh.Mesh(str(ROOT/('probes' if r['ID'].startswith('Q') else 'stl')/(r['ID']+'.stl')))
    return m,m.Topology
def allowed(verts,x,y):
    # Convex-hull separating-axis test with excluded rectangle expanded by 5mm.
    pts=sorted(set((round(v.x+x,4),round(v.y+y,4)) for v in verts))
    def cross(o,a,b):return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
    lower=[];upper=[]
    for p in pts:
        while len(lower)>=2 and cross(lower[-2],lower[-1],p)<=0:lower.pop()
        lower.append(p)
    for p in reversed(pts):
        while len(upper)>=2 and cross(upper[-2],upper[-1],p)<=0:upper.pop()
        upper.append(p)
    hull=lower[:-1]+upper[:-1]; rect=[(-5,-5),(23,-5),(23,33),(-5,33)]
    axes=[(1,0),(0,1)]+[(hull[(i+1)%len(hull)][1]-a[1],a[0]-hull[(i+1)%len(hull)][0]) for i,a in enumerate(hull)]
    for ax,ay in axes:
        a=[px*ax+py*ay for px,py in hull];b=[px*ax+py*ay for px,py in rect]
        if max(a)<min(b) or max(b)<min(a):return True
    return False
for r in sorted(rows,key=lambda r:float(r['X_print_mm'])*float(r['Y_print_mm']),reverse=True):
    if r['Tip']!='print': continue
    m,(verts,faces)=load(r); b=m.BoundBox; w=b.XLength; h=b.YLength
    group=('TEST' if r['ID'].startswith('Q') else 'PART')+'_'+r['Material']
    placed=False
    for p in plates:
        if p['group']!=group: continue
        # Place in a regular search grid; rectangles include a 10 mm mutual gap.
        for y in range(5,int(251-h)+1,3):
            if placed: break
            for x in range(5,int(251-w)+1,3):
                if any(not (x+w+10<=a['x'] or a['x']+a['w']+10<=x or y+h+10<=a['y'] or a['y']+a['h']+10<=y) for a in p['items']):continue
                if not allowed(verts,x,y):continue
                p['items'].append(dict(id=r['ID'],x=x,y=y,w=w,h=h,row=r)); placed=True;break
        if placed:break
    if not placed:
        x=(256-w)/2; y=(256-h)/2
        if not allowed(verts,x,y):
            # Raise plate placement past rear boundary of lower-left exclusion.
            y=34
        if x<5 or y<5 or x+w>251 or y+h>251:
            raise ValueError('Plate envelope cannot place '+r['ID'])
        plates.append({'group':group,'items':[dict(id=r['ID'],x=x,y=y,w=w,h=h,row=r)]})

NS='http://schemas.microsoft.com/3dmanufacturing/core/2015/02'; E.register_namespace('',NS)
report=[]
for pi,p in enumerate(plates,1):
    label=f'{pi:02d}_{p["group"]}'
    model=E.Element('{'+NS+'}model',{'unit':'millimeter','xml:lang':'en-US'})
    res=E.SubElement(model,'{'+NS+'}resources'); build=E.SubElement(model,'{'+NS+'}build')
    svg=['<svg xmlns="http://www.w3.org/2000/svg" width="900" height="1000" viewBox="-8 -18 272 297"><rect x="-8" y="-18" width="272" height="297" fill="#eef2f2"/>',f'<text x="0" y="-7" font-family="Arial" font-size="6">PLATE {label} / mm / geometrie, fara suporturi</text>', '<rect width="256" height="256" fill="white" stroke="#354e59" stroke-width=".6"/><rect x="0" y="228" width="18" height="28" fill="#d68478"/>']
    for i,a in enumerate(p['items'],1):
        m,(verts,faces)=load(a['row']); obj=E.SubElement(res,'{'+NS+'}object',{'id':str(i),'type':'model','name':a['id']}); mesh=E.SubElement(obj,'{'+NS+'}mesh'); vv=E.SubElement(mesh,'{'+NS+'}vertices'); tt=E.SubElement(mesh,'{'+NS+'}triangles')
        for v in verts: E.SubElement(vv,'{'+NS+'}vertex',dict(x=f'{v.x+a["x"]:.5f}',y=f'{v.y+a["y"]:.5f}',z=f'{v.z:.5f}'))
        for f in faces:E.SubElement(tt,'{'+NS+'}triangle',dict(v1=str(f[0]),v2=str(f[1]),v3=str(f[2])))
        E.SubElement(build,'{'+NS+'}item',{'objectid':str(i)})
        # Draw unique projected edges for an actual mesh footprint.
        edges=set()
        for f in faces:
            for k in range(3):edges.add(tuple(sorted((f[k],f[(k+1)%3]))))
        path=[]
        for u,v in edges:
            pu,pv=verts[u],verts[v]
            if abs(pu.x-pv.x)+abs(pu.y-pv.y)<.1:continue
            path.append(f'M{pu.x+a["x"]:.2f},{256-pu.y-a["y"]:.2f}L{pv.x+a["x"]:.2f},{256-pv.y-a["y"]:.2f}')
        svg.append('<path d="'+''.join(path)+'" fill="none" stroke="#284f61" stroke-width=".15"/>')
        svg.append(f'<text x="{a["x"]+a["w"]/2}" y="{256-a["y"]-a["h"]/2}" text-anchor="middle" font-family="Arial" font-size="5" fill="#ad6414">{a["id"]}</text>')
        report.append({'plate':label,'id':a['id'],'material':a['row']['Material'],'x':round(a['x'],2),'y':round(a['y'],2),'z':0,'mesh_footprint_exclusion_check':True,'supports_validated':False})
    svg.append('<text x="0" y="267" font-family="Arial" font-size="4.5">Rosu: zona exclusa P1S. 5 mm rezerva contur; suporturi de verificat in slicer.</text></svg>');(OUT/(label+'.svg')).write_text(''.join(svg))
    with zipfile.ZipFile(OUT/(label+'.3mf'),'w',zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml','<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
        z.writestr('_rels/.rels','<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
        z.writestr('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))
    with zipfile.ZipFile(OUT/(label+'.3mf')) as z: assert z.testzip() is None; E.fromstring(z.read('3D/3dmodel.model'))
with open(OUT/'placements.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=report[0].keys());w.writeheader();w.writerows(report)
(ROOT/'validation/plates.json').write_text(json.dumps({'plates':len(plates),'objects':len(report),'geometry_only':True,'positions':report},indent=2))
html='<html><meta charset="utf-8"><title>Plate-uri P1S</title><style>body{background:#e9edee;font:18px Arial;padding:24px}main{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}img{width:100%}a{color:#214c60}</style><h1>Plate-uri P1S · geometrie aranjată</h1><p>Separate după material și probe. Fișiere 3MF fără suporturi sau parametri validați de imprimare. La import păstrează pozițiile; nu asambla toate obiectele ca o singură piesă. Verifică fiecare strat și suporturile în slicer.</p><main>'
for pi,p in enumerate(plates,1):
    label=f'{pi:02d}_{p["group"]}'; html+=f'<a href="{label}.3mf"><img src="{label}.svg">{label} · 3MF</a>'
html+='</main></html>'; (OUT/'index.html').write_text(html)
print(len(plates),'plates',len(report),'parts')
