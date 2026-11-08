from pathlib import Path
import json,html,csv,zipfile
from PIL import Image,ImageOps,ImageDraw
R=Path(__file__).resolve().parents[1];O=R/'randari_proiect'
rows=json.loads((O/'imagini.json').read_text())
cards=[]
for a in rows:
 p=O/a['file']
 with Image.open(p) as im:
  assert im.size==(2000,1600),(p,im.size)
  thumb=ImageOps.contain(im.convert('RGB'),(440,352))
 card=Image.new('RGB',(480,415),'#f2e9df');card.paste(thumb,((480-thumb.width)//2,10));draw=ImageDraw.Draw(card)
 # ASCII caption for platform-independent contact sheet font.
 import unicodedata
 caption=unicodedata.normalize('NFKD',a['title']).encode('ascii','ignore').decode()
 draw.text((16,373),a['file'][:2]+'  '+caption[:62],fill='#172d3c');cards.append(card)
for page in range((len(cards)+11)//12):
 canvas=Image.new('RGB',(1920,1245),'white')
 for i,card in enumerate(cards[page*12:page*12+12]):canvas.paste(card,((i%4)*480,(i//4)*415))
 canvas.save(O/f'Contact_{page+1:02}.jpg',quality=92)
body='''<!doctype html><html lang="ro"><meta charset="utf-8"><title>Terminal R11 — randări pentru proiect</title><style>body{margin:32px;background:#f2e9df;color:#172936;font:18px system-ui}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(360px,1fr));gap:24px}figure{margin:0;background:white;border-radius:12px;overflow:hidden}img{width:100%;display:block}figcaption{padding:16px}small{display:block;margin-top:8px;color:#52616c}a{color:#125378}header{max-width:1000px;margin-bottom:32px}</style><header><h1>Terminal OPD2203 · R11</h1><p>24 randări pe fundal cald personalizat, din geometria CAD existentă, PNG 2000 × 1600 px. Ansamblul păstrează poziția normală a pieselor. Pentru inspecțiile interne sunt ascunse componente; secțiunea virtuală este marcată explicit.</p><p>Portocaliu = gabarit LED; albastru = gabarit sursă. Randările nu simulează iluminarea LED, transmiterea prin filament, infill-ul sau rezistența mecanică. Materialele sunt reprezentări vizuale.</p><a href="Scena_randari_R11_ASAMBLAT.blend">Scena Blender, asamblată normal</a></header><main>'''
for a in rows:
 body+=f'<figure><a href="{html.escape(a["file"])}"><img loading="lazy" src="{html.escape(a["file"])}" alt="{html.escape(a["title"])}"></a><figcaption><b>{html.escape(a["title"])}</b><small>{html.escape(a["note"])}</small></figcaption></figure>'
(O/'index.html').write_text(body+'</main></html>')
with open(O/'EVIDENTA_IMAGINI.csv','w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=['file','title','note']);w.writeheader();w.writerows(rows)
with zipfile.ZipFile(R/'RANDARI_R11_PENTRU_PROIECT.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in O.iterdir():
  if p.is_file() and p.suffix!='.blend1':z.write(p,p.name)
print('PACKAGED',len(rows),'images',flush=True)
