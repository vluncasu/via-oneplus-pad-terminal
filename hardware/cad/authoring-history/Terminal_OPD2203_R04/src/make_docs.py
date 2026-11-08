import json, csv, math, re, html
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
P=json.loads((ROOT/'src/parameters.json').read_text()); C=json.loads((ROOT/'validation/calculations.json').read_text())
rows=list(csv.DictReader(open(ROOT/'docs/piese_si_imprimare.csv')))
tests=json.loads((ROOT/'validation/roundtrip_mesh.json').read_text())
sweeps=json.loads((ROOT/'validation/service_sweeps.json').read_text())
coll=json.loads((ROOT/'validation/interferences.json').read_text())

def inline(t):
    t=html.escape(t)
    t=re.sub(r'\[([^\]]+)\]\(([^)]+)\)',r'<a href="\2">\1</a>',t)
    t=re.sub(r'\*\*([^*]+)\*\*',r'<strong>\1</strong>',t)
    t=re.sub(r'`([^`]+)`',r'<code>\1</code>',t)
    return t
def markdown(text):
    out=[]; para=[]; table=[]; lst=[]; listtype='ul'
    def flush():
        nonlocal para,table,lst
        if para: out.append('<p>'+inline(' '.join(para))+'</p>'); para=[]
        if table:
            data=[r for r in table if not re.match(r'^\|[\s:|−-]+\|$',r)]
            out.append('<div class="table"><table>')
            for n,r in enumerate(data):
                tag='th' if n==0 else 'td'; out.append('<tr>'+''.join(f'<{tag}>'+inline(x.strip())+f'</{tag}>' for x in r.strip('|').split('|'))+'</tr>')
            out.append('</table></div>'); table=[]
        if lst: out.append('<'+listtype+'>'+''.join('<li>'+inline(x)+'</li>' for x in lst)+'</'+listtype+'>'); lst=[]
    for line in text.splitlines():
        if not line.strip(): flush(); continue
        if line.startswith('#'):
            flush(); n=len(line)-len(line.lstrip('#')); title=line[n:].strip(); out.append(f'<h{n}>'+inline(title)+f'</h{n}>')
        elif line.startswith('|'): table.append(line)
        elif line.startswith('- '):
            if para or table: flush()
            listtype='ul'; lst.append(line[2:])
        elif re.match(r'^\d+\. ',line):
            if para or table: flush()
            listtype='ol'; lst.append(re.sub(r'^\d+\. ','',line))
        else: para.append(line)
    flush(); return '\n'.join(out)

# Dimensioned orthographic drawing. This is vector CAD-derived layout, not a render.
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1050" viewBox="0 0 800 525">',
'<defs><marker id="a" markerWidth="5" markerHeight="5" refX="2.5" refY="2.5" orient="auto"><path d="M5,0 L0,2.5 L5,5" fill="none" stroke="#52636d"/></marker></defs><rect width="800" height="525" fill="#fff"/>',
'<style>text{font-family:Arial;fill:#243640;font-size:7px}.line{fill:none;stroke:#243640;stroke-width:.65}.dim{stroke:#52636d;stroke-width:.4;marker-start:url(#a);marker-end:url(#a)}.sub{fill:#65757f;font-size:6px}</style>',
'<text x="25" y="24" style="font-size:15px">OPD2203 / R04 — geometrie de prototip</text><text x="25" y="38" class="sub">mm • planul capului si elevatie laterala • unghi real 60° • cotele componentelor neconfirmate raman parametrice</text>']
def dim(x1,y1,x2,y2,label,tx=None,ty=None):
    svg.append(f'<path d="M{x1},{y1} L{x2},{y2}" class="dim"/><text x="{tx if tx is not None else (x1+x2)/2}" y="{ty if ty is not None else (y1+y2)/2-4}" text-anchor="middle">{label}</text>')
# Front plane scale .92.
sx,sy,sc=25,100,.92
def rect(x,y,w,h,r,fill='none',stroke='#243640'):
    svg.append(f'<rect x="{sx+x*sc}" y="{sy+y*sc}" width="{w*sc}" height="{h*sc}" rx="{r*sc}" fill="{fill}" stroke="{stroke}" stroke-width=".7"/>')
rect(0,0,310,220,18,'#f2f1ec')
rect(.3,.3,309.4,219.4,17.7,'none','#de9a43')
# Coordinates measured from case upper left (-143,+110).
rect(143-129.015,110-94.705,258.03,189.41,11,'#152d3a')
rect(P['bar_cx']+143-13,13,26,194,13,'#1d252b')
for y,r in [(82,3.1),(55,8),(30,3.8),(-28,5.5),(-55,8),(-80,3)]:
    svg.append(f'<circle cx="{sx+(P["bar_cx"]+143)*sc}" cy="{sy+(110-y)*sc}" r="{r*sc}" fill="#526773" stroke="#99acb7" stroke-width=".7"/>')
dim(sx,sy-15,sx+310*sc,sy-15,'310')
dim(sx+310*sc+12,sy,sx+310*sc+12,sy+220*sc,'220',sx+310*sc+25,sy+110*sc)
svg.append(f'<text x="{sx}" y="{sy+220*sc+18}">PLAN CAP • centrul tabletei la X=−12 fata de carcasa</text>')
svg.append(f'<text x="{sx}" y="{sy+220*sc+30}" class="sub">Bara 26×194; axa camera Y=+55; port USB Y=0 (provizoriu)</text>')
# Side view at scale .87; front is left.
ox,oz,s=570,417,.87
def xy(y,z): return (ox-y*s,oz-z*s)
def poly(pts,fill):
    svg.append('<polygon points="'+' '.join(f'{x:.3f},{y:.3f}' for x,y in [xy(*p) for p in pts])+f'" fill="{fill}" stroke="#243640" stroke-width=".7"/>')
poly([(-115,3),(115,3),(115,32),(-115,32)],'#efeee9')
poly([(-91,32),(19,32),(19,58),(-91,58)],'#efeee9')
pts=[]
for i in range(41):
    t=i/40; u=1-t; y=u**3*-61+3*u*u*t*-104+3*u*t*t*25+t**3*-8; z=u**3*58+3*u*u*t*98+3*u*t*t*135+t**3*198; pts.append((y,z))
poly([(y-12,z) for y,z in pts]+[(y+12,z) for y,z in reversed(pts)],'#efeee9')
hp=[]
for y,z in [(-110,-1.3),(110,-1.3),(110,37.3),(-110,37.3)]: hp.append((10-.5*y-.8660254*z,240+.8660254*y-.5*z))
poly(hp,'#efeee9')
top=C['assembly_zmax_mm']; dim(713,oz,713,oz-top*s,f'{top:.1f}',737,oz-top*s/2)
dim(ox-115*s,oz+18,ox+115*s,oz+18,'230')
svg.append('<text x="470" y="467">SCHEMA LATERALA • ecran la 60°</text><text x="470" y="480" class="sub">Cap 38,6 / 39,9 cu nervuri; baza 32; radacina compacta 58</text>')
svg.append('<path d="M20,499 H780" stroke="#b6c0c4"/><text x="25" y="514" class="sub">NU ESTE DESEN ELIBERAT PENTRU FABRICATIE FINALA • Detaliile complete sunt in STEP, parametri si raport.</text></svg>')
(ROOT/'drawings/00_cote_generale.svg').write_text(''.join(svg))

summary=f'''<div class="metrics"><div><b>310 × 230 × {top:.1f}</b><span>gabarit ansamblu / mm</span></div><div><b>{len([r for r in rows if r['Tip']=='print' and not r['ID'].startswith('Q')])} repere + {len([r for r in rows if r['ID'].startswith('Q')])} probe</b><span>piese imprimate individuale</span></div><div><b>{C['led_total_m']:.3f} m</b><span>traseu COB calculat</span></div><div><b>60°</b><span>planul ecranului fata de masa</span></div></div>'''
stats=f'''<h2>Rezultate numerice ale acestei livrări</h2><div class="table"><table><tr><th>Verificare</th><th>Rezultat executat</th></tr>
<tr><td>STEP reimportat și mesh-uri închise</td><td>{sum(t['pass'] for t in tests)} / {len(tests)} verificări complete trecute</td></tr>
<tr><td>Interferențe volumice statice</td><td>{len(coll)} perechi peste pragul 0,05 mm³; componente ipotetice conform modelului</td></tr>
<tr><td>Mișcări de service</td><td>{sum(t['pass'] for t in sweeps)} / {len(sweeps)} teste eșantionate trecute</td></tr>
<tr><td>Bandă cap / bază</td><td>{C['led_path_head_mm']:.2f} / {C['led_path_base_mm']:.2f} mm; pas de tăiere neconfirmat</td></tr>
<tr><td>Buget electric de calcul</td><td>{C['power_total_W']:.2f} W consum ipotetic; puterea sursei reale de confirmat; compatibilitatea încărcării nevalidată</td></tr>
<tr><td>Masă CAD estimată</td><td>{C['mass_estimate_kg']:.2f} kg, cu mase de componente presupuse</td></tr>
<tr><td>CG estimat global</td><td>{', '.join(f'{x:.1f}' for x in C['cg_estimate_mm'])} mm</td></tr>
<tr><td>Rezerva minimă la 5 N sus</td><td>{min(C['stability_5N_at_top_sf']):.2f} față de ținta 1,50 → ancorare de blat</td></tr>
</table></div>'''
gallery=''.join(f'<figure><img loading="lazy" src="preview/{n}.png"><figcaption>{cap}</figcaption></figure>' for n,cap in [('01_perspectiva_CAD','Perspectivă din geometria CAD — finisajul fizic necesită probe.'),('02_spate_CAD','Spate: capace și acces la prinderi.'),('03_lateral_CAD','Profil lateral, înclinare reală de 60°.'),('04_frontal_CAD','Vedere frontală, bară laterală inclusă în contur.'),('05_explodata_CAD','Explodată ilustrativă; ordinea de demontare este descrisă în raport.'),('06_porturi_detaliu','Nouă porturi false, inserții individuale cu fund închis.'),('07_camera_detaliu','Bară monoculară reală cu stilizare stereo decorativă.'),('08_LED_cap_integrare','Cap: suport PCB COB, inel difuzor și capturarea marginilor.'),('09_LED_baza_integrare','Bază deschisă: difuzor și traseu perimetral LED.'),('10_camera_interior','Caseta ascunsă pentru a vedea camera și suporturile interioare.'),('11_grile_detaliu','Grile paralele integrate în capacul posterior.'),('12_racord_baza','Racordul alb dintre bază și picior; prinderile sunt în interior.'),('13_insula_spate','Detalii decorative cu fund închis pe capacul posterior al insulei optice.'),('14_porturi_interior','Porturi adâncite: flanșe, ghidaje și pieptene de reținere.'),('15_porturi_montaj','Montaj porturi: Ethernet ridicat din ghidaj, pieptene și stifturi separate.'),('16_picior_chei','Picior separat: patru chei imprimate, fără șuruburi transversale.'),('18_porturi_macro','USB-A, USB-C și Ethernet: reliefurile reale CAD, mărite pentru inspecție.'),('17_cod_ascuns','Cod gravat pe fața interioară a piciorului; invizibil în ansamblul închis.')])
sections=''.join(f'<figure class="wide"><img loading="lazy" src="drawings/{n}.svg"><figcaption>{caption}</figcaption></figure>' for n,caption in [('00_cote_generale','Cote generale din parametrii R04.'),('LED_detaliu_cotat','Detaliu cotat: suport, bandă, spațiu optic și capturarea difuzorului.'),('head_USB_section','Secțiune CAD prin USB-C; turcoaz: componentă de referință.'),('head_camera_section','Secțiune CAD prin camera reală și straturile optice.'),('head_tablet_section','Secțiune CAD prin tabletă, traversă și capac.'),('assembly_center_section','Secțiune globală prin bază și zona traseului cablurilor.')])
document=markdown((ROOT/'docs/ASAMBLARE_SIMPLA.md').read_text())+markdown((ROOT/'docs/PROIECT.md').read_text())
css='''*{box-sizing:border-box}body{margin:0;background:#ecebe7;color:#172e39;font:16px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}header{padding:70px max(24px,calc((100vw - 1180px)/2));background:#142d39;color:#f7f5eb}header p{max-width:780px;color:#c8d6da}.eyebrow{letter-spacing:.18em;text-transform:uppercase;font-size:12px;color:#f1bf71}header h1{font-size:54px;line-height:1.05;font-weight:650;margin:16px 0}main{max-width:1220px;margin:auto;padding:28px 20px}.metrics{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:0 0 30px}.metrics div{background:#fff;padding:22px;border-top:3px solid #c7944e}.metrics b{display:block;font-size:22px}.metrics span{font-size:12px;color:#68777c}.links{display:flex;flex-wrap:wrap;gap:10px;margin-top:26px}.links a{padding:10px 16px;border:1px solid #69818c;color:#fff;text-decoration:none;border-radius:4px}a{color:#137178}figure{margin:0;background:#fff;padding:10px;break-inside:avoid}figure img{width:100%;height:auto;display:block}figcaption{font-size:13px;color:#536c77;padding:10px}.gallery{display:grid;grid-template-columns:1fr 1fr;gap:16px}.gallery figure:first-child,.gallery figure:last-child,.wide{grid-column:1/-1}.wide{margin:18px 0}article,.results{padding:36px;background:#fff;margin:24px 0}article h1{font-size:34px}h2{margin:44px 0 16px;font-size:26px;border-top:1px solid #d7dfdf;padding-top:24px}p{max-width:100ch}code{font-size:.87em;background:#f0f4f4;padding:2px 5px;border-radius:3px;overflow-wrap:anywhere}.table{overflow:auto}table{width:100%;border-collapse:collapse;font-size:14px;margin:15px 0}td,th{padding:11px 14px;text-align:left;border-bottom:1px solid #d7dfdf;vertical-align:top}th{background:#edf2f2}li{margin:9px 0}.notice{padding:18px 22px;background:#fff3db;border-left:4px solid #bc8944;margin:18px 0}footer{padding:28px;color:#526773;font-size:13px}@media(max-width:800px){header h1{font-size:36px}.metrics,.gallery{grid-template-columns:1fr 1fr}article,.results{padding:20px}td,th{padding:8px}}@media print{header{padding:25px;background:white;color:#172e39}header p{color:#172e39}.links{display:none}main{padding:0}.metrics{grid-template-columns:repeat(4,1fr)}article,.results{padding:0}body{background:white;font-size:10pt}h2{break-after:avoid}.gallery{display:block}figure{break-inside:avoid}a{color:inherit}}'''
page=f'''<!doctype html><html lang="ro"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>OPD2203 · proiect R04</title><style>{css}</style></head><body><header><div class="eyebrow">Astra / Product engineering / R04</div><h1>Un terminal în jurul tabletei.</h1><p>Carcasă albă satinată, picior portant în S, bară optică laterală și două inele de lumină caldă. Proiect parametric, exporturi CAD și probe pentru următoarea etapă fizică.</p><div class="links"><a href="cad/Terminal_OPD2203_R04.FCStd">Model FreeCAD</a><a href="step/Terminal_OPD2203_R04_assembly.step">Ansamblu STEP</a><a href="docs/piese_si_imprimare.csv">Piese și imprimare</a><a href="src/parameters.json">Parametri</a><a href="plates/index.html">Plăci P1S / 3MF</a><a href="docs/ASAMBLARE_SIMPLA.md">Ghid simplu de montaj</a><a href="docs/PROIECT.md">Raport tehnic</a></div></header><main>{summary}<div class="notice"><strong>R04 este pentru prototipare.</strong> Sursa, banda LED, cablul și modulul camerei trebuie măsurate. Modelul nu reprezintă validare mecanică, termică sau electrică. Configurația aleasă folosește ancorare de blat.</div><div class="gallery">{gallery}</div><section class="results">{stats}</section><h2>Planșe și secțiuni</h2>{sections}<article>{document}</article></main><footer>Generat din fișierele CAD ale proiectului • 20 septembrie 2026 • mm</footer></body></html>'''
(ROOT/'index.html').write_text(page)
(ROOT/'README.md').write_text('# Terminal OPD2203 R04\n\nDeschide **index.html** pentru prezentarea proiectului, randari CAD, cote, verificari si raport complet.\n\nCiteste docs/PROIECT.md inainte de imprimare. R04 este o versiune de prototip, nu o eliberare pentru fabricatie finala. Modelul parametric este src/build.py + src/parameters.json.\n\nStart economic: Q26 micro-colt tableta (~0,87 g); Q25 colt extins; apoi Q21-Q24 contur, Q11-Q14 ajustaje si probele USB/LED/camera. Placile sunt in plates/index.html.\n')
print('Wrote index.html, README.md, dimension drawing')
