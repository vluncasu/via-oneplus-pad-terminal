"""Create the illustrated handbook from maintained English Markdown and actual-mesh figures.
Requires reportlab. Fonts: Arial on macOS or DejaVu Sans on Linux.
"""
from pathlib import Path
import re,html,json,os
from urllib.parse import quote
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Image,PageBreak,KeepTogether,LongTable,TableStyle,Flowable,CondPageBreak
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
r=Path(__file__).resolve().parents[1]
font=next((p for p in [Path('/System/Library/Fonts/Supplemental/Arial Unicode.ttf'),Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')] if p.exists()),None)
bold=next((p for p in [Path('/System/Library/Fonts/Supplemental/Arial Bold.ttf'),Path('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf')] if p.exists()),font)
if font is None:raise RuntimeError('Install Arial Unicode or DejaVu Sans first')
pdfmetrics.registerFont(TTFont('Handbook',str(font)));pdfmetrics.registerFont(TTFont('HandbookBold',str(bold)))
styles=getSampleStyleSheet()
for name,size,leading,color in [('Body',9,13,'#26363d'),('Cell',7.4,10.5,'#26363d'),('Caption',8,11,'#53666d')]:
 styles.add(ParagraphStyle(name='V'+name,fontName='Handbook',fontSize=size,leading=leading,spaceAfter=7,textColor=HexColor(color)))
styles.add(ParagraphStyle(name='VH1',fontName='HandbookBold',fontSize=22,leading=28,spaceAfter=16,textColor=HexColor('#164b50'),keepWithNext=True))
styles.add(ParagraphStyle(name='VH2',fontName='HandbookBold',fontSize=12.5,leading=17,spaceBefore=14,spaceAfter=8,textColor=HexColor('#164b50'),keepWithNext=True))
styles.add(ParagraphStyle(name='VTitle',fontName='HandbookBold',fontSize=34,leading=39,spaceAfter=14,textColor=HexColor('#164b50')))
width=A4[0]-92
manifest={m['figure']:m for m in json.loads((r/'media/render-manifest.json').read_text())}
def markup(text,source):
 # Resolve local links to browsable public documentation; leave prose readable.
 chunks=[];pos=0
 for match in re.finditer(r'\[([^]]+)\]\(([^)]+)\)',text):
  chunks.append(html.escape(text[pos:match.start()]))
  label,target=match.groups()
  if not target.startswith(('http://','https://')):
   target='https://github.com/vluncasu/via-oneplus-pad-terminal/blob/main/'+quote(str((source.parent/target).resolve().relative_to(r)),safe='/')
  chunks.append(f'<a href="{html.escape(target,quote=True)}" color="#164b50">{html.escape(label)}</a>');pos=match.end()
 chunks.append(html.escape(text[pos:]));out=''.join(chunks)
 out=re.sub(r'\*\*([^*]+)\*\*',r'<b>\1</b>',out);out=out.replace('`','')
 return out
class InterfaceDiagram(Flowable):
 def __init__(self,kind):
  Flowable.__init__(self);self.kind=kind;self.width=width;self.height=75 if kind=='structure' else 155
 def draw(self):
  c=self.canv
  def box(x,y,w,h,lines):
   c.setStrokeColor(HexColor('#779b94'));c.setFillColor(HexColor('#edf4f1'));c.roundRect(x,y,w,h,5,stroke=1,fill=1)
   c.setFillColor(HexColor('#164b50'));c.setFont('Handbook',7.5)
   for i,line in enumerate(lines):c.drawCentredString(x+w/2,y+h/2+(len(lines)-1)*5-i*10,line)
  def arrow(x1,y1,x2,y2):
   c.setStrokeColor(HexColor('#3b635c'));c.setLineWidth(.8);c.line(x1,y1,x2,y2)
   import math
   a=math.atan2(y2-y1,x2-x1)
   for delta in [-.45,.45]:c.line(x2,y2,x2-5*math.cos(a+delta),y2-5*math.sin(a+delta))
  if self.kind=='structure':
   labels=[['Tablet'],['H01 / head','interface'],['B07','S stand'],['Root / upper','cover'],['B01 base'],['Feet / desk']]
   w=(width-5*9)/6
   for i,text in enumerate(labels):
    box(i*(w+9),20,w,38,text)
    if i<5:arrow(i*(w+9)+w,39,(i+1)*(w+9),39)
  else:
   w=(width-34)/3;x=[0,w+17,2*(w+17)]
   for pos,text in zip(x,[['Real incoming','low-voltage cable'],['P01 funnel /','actual strain relief'],['Base power','distribution']]):box(pos,100,w,38,text)
   for i in [0,1]:arrow(x[i]+w,119,x[i+1],119)
   for pos,text in zip(x,[['Base LED feed'],['B07 internal duct'],['Tablet USB-C /','head LED feed']]):box(pos,18,w,38,text)
   arrow(x[2]+w/2,100,x[1]+w/2,56);arrow(x[2],100,x[0]+w/2,56);arrow(x[1]+w,37,x[2],37)
flow=[Paragraph('VIA',styles['VTitle']),Paragraph('Illustrated Assembly<br/>and Demo Handbook',styles['VH1']),Paragraph('OnePlus Pad OPD2203 · Hardware R14.1 · Applications 1.0.5<br/>Expanded documentation edition · 8 November 2026',styles['VBody'])]
hero=r/manifest[16]['file']
if hero.exists():flow += [Image(str(hero),width=width,height=width*1250/1700)]
flow += [Spacer(1,10),Paragraph('A practical companion to the engineering rationale: part selection, printed joints, hidden wiring, tablet service and the local phone/tablet demonstration. Actual-mesh illustrations communicate geometry; physical qualification remains a separate step.',styles['VBody']),Paragraph('github.com/vluncasu/via-oneplus-pad-terminal',styles['VCaption'])]
chapters=[('README.md',None),('part-catalog.md',None),('dimensions-and-clearances.md',14),('manufacturing-workflow.md',11),('interfaces-and-retention.md',20),('assembly.md',21),('fasteners-and-service.md',24),('led-and-wiring.md',30),('acceptance-test-plan.md',23),('demo-runbook.md',None),('troubleshooting.md',None),('requirements-traceability.md',None)]
def figure(number):
 m=manifest[number];p=r/m['file']
 if not p.exists():
  if os.environ.get('VIA_HANDBOOK_DRAFT'):
   flow.append(Paragraph(f'Figure {number:02d} pending rendering.',styles['VCaption']));return
  raise FileNotFoundError(p)
 group=[Image(str(p),width=width,height=width*1250/1700),Paragraph(f"Figure {number:02d}. {m['caption']}",styles['VCaption'])]
 if flow and isinstance(flow[-1],Paragraph) and flow[-1].style.name in ['VH1','VH2']:group.insert(0,flow.pop())
 flow.append(KeepTogether(group))
for chapter,(filename,number) in enumerate(chapters,1):
 source=r/'docs'/filename;lines=source.read_text().splitlines();flow.append(CondPageBreak(540 if number and Path(manifest[number]['file']).name not in source.read_text() else 300))
 title=lines[0].lstrip('# ');flow.append(Paragraph(f'{chapter}. '+html.escape(title),styles['VH1']))
 if number and Path(manifest[number]['file']).name not in source.read_text():figure(number)
 para=[];table=[];code=False
 def flush_para():
  if para:flow.append(Paragraph(markup(' '.join(para),source),styles['VBody']));para.clear()
 def flush_table():
  if not table:return
  cells=[[Paragraph(markup(v,source),styles['VCell']) for v in row] for row in table]
  n=len(cells[0]);weights={2:[.28,.72],3:[.25,.36,.39],4:[.20,.27,.22,.31],5:[.16,.32,.08,.15,.29]}.get(n,[1/n]*n)
  t=LongTable(cells,colWidths=[width*x for x in weights],repeatRows=1,hAlign='LEFT')
  t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),HexColor('#dfece8')),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),5),('RIGHTPADDING',(0,0),(-1,-1),5),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5),('LINEBELOW',(0,0),(-1,-1),.3,HexColor('#ccd6d4')),('ROWBACKGROUNDS',(0,1),(-1,-1),[HexColor('#ffffff'),HexColor('#f4f7f6')])]))
  flow.extend([t,Spacer(1,10)]);table.clear()
 for line in lines[1:]:
  if line.startswith('```'):
   flush_para();flush_table();code=not code
   if code:
    flow.append(InterfaceDiagram('structure' if filename=='interfaces-and-retention.md' else 'wiring'))
    flow.append(Paragraph('Intended interface relationships; the wiring view is a functional topology, not an electrical schematic.',styles['VCaption']))
   continue
  if code:continue
  if line.startswith('|'):
   flush_para();row=[x.strip() for x in line.strip().strip('|').split('|')]
   if all(re.fullmatch(r':?-+:?',v) for v in row):continue
   table.append(row);continue
  flush_table()
  if line.startswith('!['):
   flush_para();target=re.search(r'\]\(([^)]+)\)',line).group(1)
   match=next((m for m in manifest.values() if Path(m['file']).name==Path(target).name),None)
   if match:figure(match['figure'])
   continue
  if line.startswith('## '):flush_para();flow.append(Paragraph(markup(line[3:],source),styles['VH2']))
  elif line.startswith('### '):flush_para();flow.append(Paragraph(markup(line[4:],source),styles['VH2']))
  elif not line.strip():flush_para()
  elif re.match(r'^(?:- |\d+\. )',line):flush_para();flow.append(Paragraph(markup(line,source),styles['VBody']))
  else:para.append(line.strip())
 flush_para();flush_table()
def footer(c,doc):
 c.saveState();c.setStrokeColor(HexColor('#a5bcb8'));c.line(46,37,A4[0]-46,37);c.setFillColor(HexColor('#53666d'));c.setFont('Handbook',7);c.drawString(46,24,'VIA | Illustrated assembly and demo handbook | R14.1');c.drawRightString(A4[0]-46,24,str(doc.page));c.restoreState()
class HandbookDoc(SimpleDocTemplate):
 def afterFlowable(self,flowable):
  if isinstance(flowable,Paragraph) and flowable.style.name=='VH1':
   key='chapter-'+str(self.seq.nextf('chapter'))
   self.canv.bookmarkPage(key)
   self.canv.addOutlineEntry(flowable.getPlainText(),key,level=0,closed=False)
out=r/'docs/VIA_Assembly_and_Demo_Handbook.pdf'
HandbookDoc(str(out),pagesize=A4,leftMargin=46,rightMargin=46,topMargin=44,bottomMargin=48,title='VIA OnePlus Pad Terminal — Illustrated Assembly and Demo Handbook',author='VIA project contributors',subject='3D printing, part catalog, tablet retention, integrated LED channels, cable routing and offline demo').build(flow,onFirstPage=footer,onLaterPages=footer)
print(out)
