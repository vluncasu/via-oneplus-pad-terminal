from pathlib import Path
import re,html,os
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Image,PageBreak,KeepTogether
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
root=Path(__file__).resolve().parents[1]
fonts=[]
for p in [Path('/System/Library/Fonts/Supplemental/Arial Unicode.ttf'),Path('/System/Library/Fonts/Supplemental/Arial.ttf'),Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')]:
 if p.exists():fonts.append(p)
pdfmetrics.registerFont(TTFont('VIA',str(fonts[0])))
bold=Path('/System/Library/Fonts/Supplemental/Arial Bold.ttf')
if not bold.exists():bold=Path('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf')
pdfmetrics.registerFont(TTFont('VIA-Bold',str(bold if bold.exists() else fonts[0])))
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='VBody',fontName='VIA',fontSize=9.5,leading=14,spaceAfter=9,textColor=HexColor('#26363D')))
styles.add(ParagraphStyle(name='VHeading',fontName='VIA-Bold',fontSize=14,leading=19,spaceBefore=17,spaceAfter=8,keepWithNext=True,textColor=HexColor('#164B50')))
styles.add(ParagraphStyle(name='VTitle',fontName='VIA-Bold',fontSize=36,leading=42,spaceAfter=14,textColor=HexColor('#164B50')))
styles.add(ParagraphStyle(name='VSubtitle',fontName='VIA',fontSize=18,leading=25,spaceAfter=18,textColor=HexColor('#26363D')))
styles.add(ParagraphStyle(name='VCaption',fontName='VIA',fontSize=8,leading=11,spaceAfter=13,textColor=HexColor('#596B70')))
output=root/'docs/VIA_Engineering_Design_Report.pdf'
doc=SimpleDocTemplate(str(output),pagesize=A4,rightMargin=48,leftMargin=48,topMargin=48,bottomMargin=48,title='VIA: OnePlus Pad Terminal Enclosure - Engineering Design Report',author='VIA project contributors',subject='Design rationale, additive manufacturing, serviceable tablet integration, LED channels and offline Android architecture')
def escape(t):
 t=re.sub(r'\[([^]]+)\]\(([^)]+)\)',r'\1 (\2)',t)
 return html.escape(t).replace('**','').replace('`','')
flow=[Spacer(1,12),Paragraph('VIA',styles['VTitle']),Paragraph('OnePlus Pad Terminal Enclosure<br/>Engineering Design Report',styles['VSubtitle']),Paragraph('Hardware R14.1 · Android 1.0.5<br/>Public engineering prototype · 8 November 2026',styles['VBody'])]
hero=root/'media/renders/01-oneplus-pad-terminal-front.png'
if hero.exists():flow.append(Image(str(hero),width=498,height=365));flow.append(Paragraph('Actual-mesh visualization. Materials and LED emission illustrate intent; physical performance is not certified.',styles['VCaption']))
flow.extend([Paragraph('Repository: github.com/vluncasu/via-oneplus-pad-terminal',styles['VBody']),PageBreak()])
text=(root/'docs/design-rationale.md').read_text();paragraph=[]
def flush():
 if paragraph:flow.append(Paragraph(escape(' '.join(paragraph)),styles['VBody']));paragraph.clear()
for line in text.splitlines()[1:]:
 if line.startswith('## '):flush();flow.append(Paragraph(escape(line[3:]),styles['VHeading']))
 elif not line.strip():flush()
 else:paragraph.append(line.strip())
flush()
flow.extend([PageBreak(),Paragraph('Selected engineering views',styles['VHeading'])])
for filename,caption in [('07-integrated-head-led-channel.png','Integrated head LED channel; orange volume is a reserved strip envelope.'),('09-stand-root-reinforcement.png','Reinforcement viewed from below the integrated S-stand power-volume cover.'),('10-internal-cable-duct-section.png','Inspection section through the explicit cable void. The actual print is monoblock.')]:
 p=root/'media/renders'/filename
 if p.exists():flow.append(KeepTogether([Image(str(p),width=460,height=337),Paragraph(caption,styles['VCaption'])]))
def page(canvas,doc):
 canvas.saveState();canvas.setStrokeColor(HexColor('#ADC4C2'));canvas.line(48,36,A4[0]-48,36);canvas.setFillColor(HexColor('#596B70'));canvas.setFont('VIA',7);canvas.drawString(48,24,'VIA | Engineering design report | R14.1 / 1.0.5');canvas.drawRightString(A4[0]-48,24,str(doc.page));canvas.restoreState()
doc.build(flow,onFirstPage=page,onLaterPages=page)
print(output)
