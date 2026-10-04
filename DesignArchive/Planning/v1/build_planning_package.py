from pathlib import Path
import json, math, textwrap, hashlib, zipfile
from xml.sax.saxutils import escape
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
pdfmetrics.registerFont(TTFont("AuditSans", str(Path(__file__).parent/"inputs/fonts/DejaVuSans.ttf")))
pdfmetrics.registerFont(TTFont("AuditSansBold", str(Path(__file__).parent/"inputs/fonts/DejaVuSans-Bold.ttf")))

ROOT=Path(__file__).parent
SRC=ROOT.parent
OUT=ROOT/'editable'; OUT.mkdir(exist_ok=True)
W,H=1440,900
INK='#203F48'; MUT='#5F7274'; BG='#F8F6EF'; LINE='#C9D3D0'; GREEN='#BDD2BD'; BLUE='#CBDCE5'; GOLD='#E8D7A8'; ROSE='#D6BCC7'; TEAL='#547F80'; RUST='#B76543'; PALE='#EBECE5'; PURPLE='#826A96'
PDF=canvas.Canvas(str(ROOT/'Astraea_District_Planning_Study.pdf'),pagesize=(1080,675))
PDF.setTitle('Astraea District Planning Study');PDF.setAuthor('Astraea planning')

class Page:
 def __init__(self,n,title,sub):
  self.n=n;self.parts=[];PDF.saveState();PDF.scale(.75,.75)
  self.rect(0,0,W,H,BG,None)
  self.text(62,62,title,30,INK,True)
  self.para(62,97,sub,1295,17,MUT,leading=23)
 def rect(self,x,y,w,h,fill=None,stroke=LINE,sw=1,dash=None):
  self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill or "none"}" stroke="{stroke or "none"}" stroke-width="{sw}"'+(f' stroke-dasharray="{dash}"' if dash else '')+'/>')
  PDF.setLineWidth(sw);PDF.setDash([float(a) for a in dash.split(',')] if dash else [])
  if fill:PDF.setFillColor(HexColor(fill))
  if stroke:PDF.setStrokeColor(HexColor(stroke))
  PDF.rect(x,H-y-h,w,h,fill=int(bool(fill)),stroke=int(bool(stroke)))
 def line(self,x1,y1,x2,y2,color=LINE,sw=1,dash=None):
  self.parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{sw}"'+(f' stroke-dasharray="{dash}"' if dash else '')+'/>')
  PDF.setStrokeColor(HexColor(color));PDF.setLineWidth(sw);PDF.setDash([float(a) for a in dash.split(',')] if dash else []);PDF.line(x1,H-y1,x2,H-y2)
 def poly(self,pts,fill=None,stroke=INK,sw=1,dash=None):
  self.parts.append(f'<polygon points="'+ ' '.join(f'{x},{y}' for x,y in pts)+f'" fill="{fill or "none"}" stroke="{stroke or "none"}" stroke-width="{sw}"'+(f' stroke-dasharray="{dash}"' if dash else '')+'/>')
  PDF.setDash([float(a) for a in dash.split(',')] if dash else []); PDF.setLineWidth(sw)
  if fill:PDF.setFillColor(HexColor(fill))
  if stroke:PDF.setStrokeColor(HexColor(stroke))
  p=PDF.beginPath();p.moveTo(pts[0][0],H-pts[0][1])
  for x,y in pts[1:]:p.lineTo(x,H-y)
  p.close();PDF.drawPath(p,fill=int(bool(fill)),stroke=int(bool(stroke)))
 def text(self,x,y,s,size=18,color=INK,bold=False,anchor='start'):
  s=str(s);font='AuditSansBold' if bold else 'AuditSans'
  self.parts.append(f'<text x="{x}" y="{y}" font-family="DejaVu Sans,Arial,sans-serif" font-size="{size}" fill="{color}" font-weight="{700 if bold else 400}" text-anchor="{anchor}">{escape(s)}</text>')
  PDF.setFont(font,size);PDF.setFillColor(HexColor(color))
  if anchor=='middle':PDF.drawCentredString(x,H-y,s)
  elif anchor=='end':PDF.drawRightString(x,H-y,s)
  else:PDF.drawString(x,H-y,s)
 def para(self,x,y,s,width,size=18,color=INK,bold=False,leading=None):
  leading=leading or size*1.38;font='AuditSansBold' if bold else 'AuditSans'; yy=y
  for para in s.split('\n'):
   words=para.split();line=''
   for word in words:
    test=(line+' '+word).strip()
    if stringWidth(test,font,size)>width and line:self.text(x,yy,line,size,color,bold);yy+=leading;line=word
    else:line=test
   if line:self.text(x,yy,line,size,color,bold);yy+=leading
   elif not words:yy+=leading
  return yy
 def circle(self,x,y,r,fill=BG,stroke=INK,sw=2):
  self.parts.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>');PDF.setFillColor(HexColor(fill));PDF.setStrokeColor(HexColor(stroke));PDF.setLineWidth(sw);PDF.setDash([]);PDF.circle(x,H-y,r,fill=1,stroke=1)
 def arrow(self,x1,y1,x2,y2,color=TEAL,sw=3,dash=None):
  self.line(x1,y1,x2,y2,color,sw,dash);a=math.atan2(y2-y1,x2-x1);l=9
  self.poly([(x2,y2),(x2-l*math.cos(a-.5),y2-l*math.sin(a-.5)),(x2-l*math.cos(a+.5),y2-l*math.sin(a+.5))],color,color)
 def box(self,x,y,w,h,title,body,fill=PALE,dash=None):
  self.rect(x,y,w,h,fill,INK,1.3,dash);self.text(x+17,y+29,title,21,INK,True);self.para(x+17,y+56,body,w-34,16,MUT,leading=22)
 def finish(self,source):
  self.line(62,849,1378,849,LINE)
  self.text(62,874,source,10,MUT)
  self.text(1378,874,f'STUDY  |  02 OCT 2026  |  {self.n:02}',10,MUT,anchor='end')
  svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img"><title>Astraea planning sheet {self.n}</title>'+''.join(self.parts)+'</svg>'
  (OUT/f'{self.n:02}_planning_sheet.svg').write_text(svg)
  PDF.restoreState();PDF.showPage()

# Retained read-only baseline, transcribed from the atlas vector outline and source ID ledger.
baseline=json.loads((ROOT/'inputs/historical_baseline.json').read_text())
hull=baseline['hull_plan_zx_m']
Y=[0,6,12,16.5,21,27,35.5,44,52.5,61,69.5,78,84,88.5,93,97.5,102,106.5]

def plan(p,x,y,s):
 z=lambda v:x+(v+541)*s; a=lambda v:y+(v+120)*s
 p.poly([(z(zz),a(xx)) for zz,xx in hull],PALE,INK,1.6)
 p.rect(z(-541),a(-12),1082*s,24*s,'#E0E7E3',None)
 p.rect(z(-64),a(-48),128*s,96*s,BG,TEAL,2)
 p.text(z(0),a(-5),'ATRIUM',13,TEAL,True,'middle')
 p.rect(z(-265),a(-118),150*s,84*s,ROSE,INK,1.3)
 p.text(z(-190),a(-85),'THEATER',12,INK,True,'middle')
 route=[(-541,0),(-72,0),(-56,0),(-52,40),(52,40),(56,0),(72,0),(541,0)]
 for (za,xa),(zb,xb) in zip(route,route[1:]):p.line(z(za),a(xa),z(zb),a(xb),RUST,2)
 for zz in [-432,-216,-72,216,432]:p.circle(z(zz),a(0),3.4,BG,RUST,1.5)
 p.text(x,y-16,'BOW  Z -541 m',14,MUT);p.text(x+1082*s,y-16,'STERN  Z +541 m',14,MUT,anchor='end')
 p.text(x+1082*s/2,y-16,'PORT (-X) ABOVE   |   STARBOARD (+X) BELOW',12,MUT,anchor='middle')
 return z,a

# 1 - adjacency
p=Page(1,'Astraea as connected districts','A program and relationship study. Existing destinations anchor the plan; hotel buildings and new local connections remain proposals.')
p.box(62,165,355,135,'Homes and habitats','D04 aquatic / arboreal homes\nD13-D17 residential neighborhoods\nKnown homes; grouping remains open',BLUE)
p.box(540,165,360,135,'Grand botanical atrium','D02-D17 shared vertical landmark\nMain terraces D06 / D09 / D12 / D16\nGardens, courts, reading and family edges',GREEN)
p.box(1023,165,355,135,'Distinct hotel buildings','Alternatives A and B on sheets 3-4\nLocal guest cores and service access\nExact rooms and tiers remain open',GOLD,'7,5')
for x in [240,720,1200]:p.arrow(x,302,x,350,TEAL,3,'7,5' if x==1200 else None)
p.line(88,389,1352,389,TEAL,8)
p.text(720,369,'SHARED GUEST NETWORK',18,INK,True,'middle')
p.text(720,624,'Longitudinal promenades + five Townline catchments + existing express deck travel',18,MUT,anchor='middle')
boxes=[(62,'Active resort','D07 sport / movement\nD08 pool / baths / wellness',BLUE),(397,'Retail and local courts','D09 100 shops + 10 destinations\nMarkets, books, cafes, services',GOLD),(732,'Dining and hospitality','D10 ten venues / 2,200 places\nFood, social rooms, serving edges',GOLD),(1067,'Culture and outlooks','D11 theater / six cinemas\nD12 library / salons / observation',ROSE)]
for x,t,b,col in boxes:p.arrow(x+155,390,x+155,481,TEAL,2);p.box(x,482,311,112,t,b,col)
p.text(62,650,'Historical vertical relationships to retain in the study',21,INK,True)
p.para(62,680,'Moonwell: D08 mineral springs + D09 Paper Moon books + D10 Lantern cafe. Vesper: 240-place restaurant, two levels and a waterfall connection to the aquatic district. Connections and exact geometry need reconciliation; see sheet 7.',1290,18,MUT)
p.line(88,772,1352,772,RUST,6,'10,6')
p.text(720,753,'SEPARATE SERVICE NETWORK',18,RUST,True,'middle')
p.text(720,807,'D01 logistics / laundry / supplies   |   D02 engineering   |   D03 crew homes   |   D05 care   |   D18 command',17,MUT,anchor='middle')
p.finish('Evidence: atlas pp. 1-21; master chapters 4-7; latest user direction. Lines show relationships, not approved physical routes.')

# 2 - baseline section
p=Page(2,'Longitudinal section and protected volume','Projected section with off-axis theater volume. Deck heights are exact; the local upper hull profile remains unresolved.')
x0,xw,yt,yb=146,1110,160,622
zx=lambda z:x0+(z+541)*xw/1082
yy=lambda v:yb-v*(yb-yt)/118
p.rect(x0,yt,xw,yb-yt,None,MUT,1.3,'6,5')
p.text(x0,yt-18,'1,082 m overall',16,INK,True);p.text(x0+xw,yt-18,'118 m reference envelope',16,INK,True,'end')
for d,v in enumerate(Y,1):
 y=yy(v);p.line(x0,y,x0+xw,y,LINE,1)
 p.text(x0-12,y+5,f'D{d:02}  {v:g}',14,MUT,anchor='end')
p.text(62,yt-18,'Deck / Y m',14,MUT)
p.rect(zx(-64),yy(106.5),128*xw/1082,yy(6)-yy(106.5),BG,TEAL,2)
p.text(zx(0),yy(65),'ATRIUM',18,TEAL,True,'middle')
p.text(zx(0),yy(59),'16 levels',14,MUT,anchor='middle')
p.text(zx(0),yy(53),'D02-D17',14,MUT,anchor='middle')
for d in range(2,18):
 y=yy(Y[d-1]);ln=17 if d in [6,9,12,16] else 7
 p.line(zx(-64),y,zx(-64)+ln,y,TEAL,4 if ln==17 else 1.5)
 p.line(zx(64)-ln,y,zx(64),y,TEAL,4 if ln==17 else 1.5)
p.rect(zx(-265),yy(91.5),150*xw/1082,22*(yb-yt)/118,ROSE,INK,1.5)
p.text(zx(-190),yy(83),'THEATER',16,INK,True,'middle')
p.text(zx(-190),yy(77),'D11-D14 volume',12,MUT,anchor='middle')
p.text(zx(-190),yy(72.5),'off-axis, port',12,MUT,anchor='middle')
p.text(zx(180),yy(91),'UPPER HOTEL STUDIES',18,INK,True)
p.text(zx(180),yy(85.5),'Existing homes + proposed lobbies and local cores',14,MUT)
p.text(zx(180),yy(72),'Public leisure and culture programs',17,MUT)
p.text(zx(180),yy(38),'Resort, gardens, care and habitats',17,MUT)
p.text(zx(180),yy(8),'Crew, engineering and logistics',17,MUT)
for z in [-432,-216,-72,216,432]:p.line(zx(z),yb+12,zx(z),yb+24,RUST,2);p.text(zx(z),yb+47,f'{z:+}',14,RUST,anchor='middle')
p.text(x0,yb+80,'Townline stop Z coordinates (m). These are catchments, not hotel boundaries.',17,MUT)
p.para(62,750,'Atrium: Z -64..+64, X -48..+48. Theater: Z -265..-115, X -118..-34, top Y 91.5 m. Existing D12-D14 floor openings and D12/D13 gallery interfaces stay protected. Vertical exaggeration 3.82x; no new openings.',630,18,INK)
p.para(765,750,'Still unresolved: upper hull clearance at every proposed building, local lift/stair shafts, multistory suite floor changes, court widths and the purpose of residual allocations. Every new vertical connection must be reconciled in plan and section.',600,18,MUT)
p.finish('Evidence: atlas pp. 2, 13-14, 21; source archive AUDITORIUMS.md and SHIP_DESIGN.md. Maximum envelope is not a roof design.')

alternatives=[
 {'key':'A','title':'Three distinct hotels with a deeper public base','sub':'A proposal for two different forward hotels and one quieter aft hotel. Strong individual identity; greater conflict-review burden on public decks.',
  'masses':[{'id':'A1','name':'Forward port hotel','z':[-440,-290],'x':[-94,-20],'y':[52.5,106.5],'base':'D09-D17','fill':GOLD}, {'id':'A2','name':'Forward starboard hotel','z':[-360,-110],'x':[20,104],'y':[52.5,106.5],'base':'D09-D17','fill':BLUE},{'id':'A3','name':'Aft garden hotel','z':[120,350],'x':[-104,-20],'y':[78,106.5],'base':'D12-D17','fill':GREEN}],
  'strength':'Distinct scales and arrivals; hotel life can overlap retail, dining and culture without making one enormous undifferentiated accommodation bar.',
  'risk':'A1/A2 study volumes include existing D09-D12 programs. Cinemas, shops, dining and observation remain protected allocations until exact IDs and alternatives are reviewed.'},
 {'key':'B','title':'Four smaller hotels with paired courts to resolve','sub':'Paired forward and aft hotels above the public decks. Local court locations are unresolved and are not drawn.',
  'masses':[{'id':'B1','name':'Forward port hotel','z':[-425,-285],'x':[-95,-20],'y':[78,106.5],'base':'D12-D17','fill':GOLD},{'id':'B2','name':'Forward starboard hotel','z':[-425,-285],'x':[20,95],'y':[78,106.5],'base':'D12-D17','fill':BLUE},{'id':'B3','name':'Aft port hotel','z':[150,330],'x':[-104,-20],'y':[78,106.5],'base':'D12-D17','fill':GREEN},{'id':'B4','name':'Aft starboard hotel','z':[150,330],'x':[20,104],'y':[78,106.5],'base':'D12-D17','fill':ROSE}],
  'strength':'Clearer compact neighborhoods and potential quieter upper courts. Public dining, retail and resort remain a shared layer below, reached by local cores that still need a real footprint.',
  'risk':'Additional lift/stair/service cores consume area. D12 existing library/observation uses and D13-D17 room allocations still need a complete reconciliation.'}
]
for n,alt in enumerate(alternatives,3):
 p=Page(n,f'Alternative {alt["key"]}   {alt["title"]}',alt['sub'])
 z,a=plan(p,92,184,.82)
 for m in alt['masses']:
  p.rect(z(m['z'][0]),a(m['x'][0]),(m['z'][1]-m['z'][0])*.82,(m['x'][1]-m['x'][0])*.82,m['fill'],INK,1.7,'7,4')
  p.text(z(sum(m['z'])/2),a(sum(m['x'])/2)+5,m['id'],18,INK,True,'middle')
 p.text(92,420,'Plan-hull contour traced from the atlas. All colored hotel zones are NEW study allocations.',15,MUT)
 p.text(92,445,'Tram bypass simplified; sculpted supporting floor ring omitted. No collision claim.',14,MUT)
 # Side allocation legend
 sy=177
 for m in alt['masses']:
  p.text(1035,sy,m['id']+'  '+m['name'],19,INK,True)
  p.text(1035,sy+27,f"Z {m['z'][0]} to {m['z'][1]} m",16,MUT)
  p.text(1035,sy+49,f"X {m['x'][0]} to {m['x'][1]} m | {m['base']}",16,MUT)
  sy+=81
 # projected section
 sx,sw,top,bot=92,887,476,672
 Z=lambda v:sx+(v+541)*sw/1082
 V=lambda v:bot-v*(bot-top)/118
 p.rect(sx,top,sw,bot-top,None,MUT,1.2,'6,5')
 for d in [1,9,11,12,13,16,18]:p.line(sx,V(Y[d-1]),sx+sw,V(Y[d-1]),LINE,1);p.text(sx-7,V(Y[d-1])+4,f'D{d:02}',12,MUT,anchor='end')
 drawn=set()
 for m in alt['masses']:
  k=tuple(m['z'])+tuple(m['y'])
  if k in drawn:continue
  drawn.add(k)
  lab='/'.join(q['id'] for q in alt['masses'] if tuple(q['z'])+tuple(q['y'])==k)
  p.rect(Z(m['z'][0]),V(m['y'][1]),(m['z'][1]-m['z'][0])*sw/1082,(m['y'][1]-m['y'][0])*(bot-top)/118,m['fill'],INK,1.5,'7,4')
  p.text(Z(sum(m['z'])/2),V(m['y'][1])-8,lab,16,INK,True,'middle')
 p.rect(Z(-64),V(106.5),128*sw/1082,(106.5-6)*(bot-top)/118,BG,TEAL,1.5)
 p.rect(Z(-265),V(91.5),150*sw/1082,22*(bot-top)/118,ROSE,INK,1.3)
 p.text(sx,705,'Projected section. Same-Z port/starboard hotels overlap here; they are separate masses in plan.',15,MUT)
 p.para(1035,502,'No room counts assigned',320,20,INK,True)
 p.para(1035,538,'The 1,000-unit ledger remains whole. These envelopes test relationships; they do not absorb or delete existing destinations.',320,17,MUT)
 p.para(1035,632,'Upper hull fit and local shafts are unresolved. No floor cuts, bridges or lift cabins are approved by these boxes.',320,17,RUST)
 p.para(62,754,'Opportunity: '+alt['strength'],635,17,INK)
 p.para(755,754,'Review before choosing: '+alt['risk'],620,17,MUT)
 p.finish('Base: atlas p. 13 hull and protected geometry. Hotel coordinates/heights are explicit proposals. Not a final 1,000-room allocation.')

# 5 ledger
p=Page(5,'Allocation and constraint ledger','One authoritative program, with dated evidence separated from new proposals. All 1,462 surviving IDs are preserved in the editable crosswalk.')
cols=[62,350,965,1378]
headers=['Item','Established or retained baseline','Open decision / action']
for i in range(3):p.rect(cols[i],158,cols[i+1]-cols[i],41,INK,None);p.text(cols[i]+13,185,headers[i],17,'#FFFFFF',True)
rows=[
('Hull and decks','18 decks; 1,082 m length; 240 m max beam; 118 m envelope','Use exact floor elevations; verify local roof/side clearance'),
('Guest accommodation','1,000 units; 81 luxury included, not additional','50 deluxe / 25 premium / 5 royalty / 1 supreme; exact rooms open'),
('Population','2,000 hard passenger cap; normal 1,200-2,000','Do not revive historic 2,500 maximum or force full occupancy'),
('Crew homes','400 crew including player; player shares a staff room','Old private-player-cabin allocation needs explicit reconciliation'),
('Atrium','96 x 128 m opening D02-D17; principal terraces 06/09/12/16','Purposeful courts and edges; preserve open volume and interfaces'),
('Theater','2,200 places; 84 x 150 x 22 m; D12-D14 floor openings','Protect D12/D13 gallery interfaces, access and residential detours'),
('Retail and dining','100 shops + 10 larger D09 places; D10 has 2,200 meal places','Reconcile actual footprints before any hotel overlap'),
('Transport','Five Townline catchments; express interface; tram bypass','Local hotel cores need footprints; panoramic lifts not verified'),
('Hotel alternatives','A: three study hotels; B: four smaller study hotels','No chosen scheme, assigned IDs, capacity or approved new holes'),
('Luxury sections','Multistory upper-level rooms are current direction','Exact floor relationships, suite sizes and privacy need review'),
('Moonwell / Vesper','Historical district links and Vesper 240-place program retained','Names, multi-level boundaries and water connection unresolved'),
('Asset planning','Catalogue components can be tailored while planning evolves','Keep mating interfaces adjustable; no claimed game adoption')]
y=199
for i,row in enumerate(rows):
 h=45
 for j,txt in enumerate(row):
  p.rect(cols[j],y,cols[j+1]-cols[j],h,'#FFFFFF' if i%2==0 else '#EEF1ED',LINE,.7)
  p.para(cols[j]+12,y+17,txt,cols[j+1]-cols[j]-24,14,INK if j<2 else MUT,leading=17)
 y+=h
p.para(62,778,'Crosswalk discipline: existing_id and historical program remain unchanged; proposed_hotel_id is null for every record. New hotel membership needs explicit reconciliation. Older room-class and crew-home assumptions are retained as history, not silently adopted as latest canon.',1300,17,INK)
p.finish('Evidence: latest user canon; atlas; master source archive coverage ledger. Historical source checks do not verify a recovered runtime.')

# 6 asset pairing
p=Page(6,'A district-specific kit with a real interface','First paired target: D09 salon and starboard atrium arrival. Historical interfaces guide new adjustable components.')
# XY plan, shown X horizontal and Z vertical
px,py,sc=84,210,6.0
X=lambda v:px+(v-30)*sc
Z=lambda v:py+(v+44)*sc
p.rect(X(35),Z(-42),10*sc,84*sc,'#ECD6C6',RUST,1)
p.text(X(40),Z(-34),'TRAM',13,RUST,True,'middle')
p.line(X(40),Z(-30),X(40),Z(42),RUST,3)
p.rect(X(52),Z(-34),46*sc,68*sc,None,INK,2)
p.line(X(30),Z(0),X(104),Z(0),TEAL,4)
p.text(X(76),Z(-20),'D09_salon5',19,INK,True,'middle')
p.text(X(76),Z(-14),'46 x 68 m allocation',15,MUT,anchor='middle')
p.text(X(76),Z(15),'825.8 m2 guest enclosure',14,MUT,anchor='middle')
p.text(X(76),Z(20),'final contour not recovered',14,RUST,anchor='middle')
p.circle(X(52),Z(0),6,BG,TEAL,2);p.circle(X(98),Z(0),6,BG,RUST,2)
p.text(X(52),Z(0)-12,'guest door',13,TEAL,anchor='middle')
p.text(X(98),Z(0)+27,'service door',13,RUST,anchor='middle')
p.line(X(48),Z(-14),X(48),Z(14),TEAL,5)
p.text(84,185,'X increases toward the starboard hull; Z increases downward',14,MUT)
p.text(84,773,'28 m connected terrace at Z -14..+14',17,INK,True)
p.para(84,790,'X35..45 tram reserve and the Z0 arrival/service axis stay clear.',455,16,MUT)
p.text(620,171,'Six tailored junctions and built-ins',23,INK,True)
items=[('01','Deep public portal return','Meet the existing X52 entry and preserve its turning landing.'),('02','Coved wall-to-ceiling transition','Rib, light channel and soffit share a real joined profile.'),('03','Quiet book-and-acoustic return','Integrate shelf depth, sheltered seating edge and local light.'),('04','Planted court-to-seat junction','Connect garden edge and usable resting place without a new room.'),('05','Terrace rail-to-portal terminal','Resolve the actual garden-facing threshold and guard seam.'),('06','Protected service/storage return','Frame the X98 service access with useful, shallow support depth.')]
y=215
for num,t,b in items:
 p.text(620,y,num,18,TEAL,True);p.text(661,y,t,20,INK,True);p.para(661,y+28,b,685,16,MUT);y+=79
p.para(620,724,'Height evidence: D09 floor +52.5 m; D10 +61 m; archived usable budget 8.25 m. Later component brief limits a quiet booth to 7.2 x 5.4 x 3.8 m and a tea bay to 6 x 3 x 3.2 m. These are historical authoring limits, not proof of recovered fit.',738,17,INK)
p.finish('Sources: D09_CONNECTED_SALON.md; D09_COMPOSITION_CONTRACT.md. Warm ivory / blue-green recess / warm wood / restrained brass.')

# 7 historical district relationships
p=Page(7,'Moonwell and Vesper remain in the district plan','Preserve the pre-loss design relationships without inventing their missing shafts, room boundaries, floor openings or water geometry.')
p.text(62,173,'Moonwell   three-level neighborhood',25,INK,True)
for x,y,t,b,col in [(62,211,'D10 +61 m','Lantern cafe in conversation\nHistorical ID candidate: D10_banquet2\nArchive name: Lantern restaurant / 240 places',GOLD),(62,385,'D09 +52.5 m','Paper Moon bookshop\nD09_books2 / Paper moon books\nQuiet browsing and shared social threshold',BLUE),(62,559,'D08 +44 m','Mineral baths / springs\nD08_bath2 / Mineral springs\nWet/dry threshold and towel/service approach',GREEN)]:p.box(x,y,585,130,t,b,col,'7,5')
p.arrow(350,346,350,380,PURPLE,3,'7,5');p.arrow(350,520,350,554,PURPLE,3,'7,5')
p.para(62,733,'These are a historical conversation grouping plus surviving ID candidates. A physical shared court, local lift, stair or open void has not been recovered. Exact room-name equivalence needs review.',585,18,MUT)
p.text(762,173,'Vesper   dining and aquatic connection',25,INK,True)
p.box(762,211,616,164,'Vesper restaurant / 240 places','D10_banquet7 is the surviving Vesper dining record. The conversation reports two levels and a connected waterfall. The second level and waterfall route are not established by the archived allocation.',ROSE,'7,5')
p.arrow(1070,379,1070,459,PURPLE,3,'7,5')
p.text(1110,422,'Historical connection',16,PURPLE)
p.box(762,469,616,111,'Aquatic district','A real adjacency goal to preserve. Do not equate the visual waterfall with a proven fluid system, floor opening or navigable route.',BLUE,'7,5')
p.text(762,629,'What this should drive in the next kit',22,INK,True)
p.para(762,664,'A coordinated wet-to-dry threshold family; quiet bookshop edge; cafe service front; stacked wayfinding; rail/soffit transitions; and a water-facing dining edge. First establish the interface dimensions and actual neighboring rooms, then author the connected components together.',614,18,INK)
p.para(762,791,'Do not count a new cafe or another 240 seats from a naming difference.',614,17,RUST)
p.finish('Sources: surviving IDs in whole_ship_coverage.json; historical conversation reports. Dashed links are unverified connections.')
# 8 - one connected assembly proposal, independent of recovered adoption
p=Page(8,'One connected assembly to test first','An adjustable proposal joining arrival, reading bay and planted return. All positions need recovered-boundary review.')
p.text(62,166,'Plan   connected threshold and bay',23,INK,True)
xx=lambda x:86+(x-45)*17
zz=lambda z:422+z*17
# precise known door/axis; all proposed strips and modules are dashed
p.line(xx(48),zz(0),xx(72),zz(0),TEAL,3)
p.rect(xx(48),zz(-2),24*17,4*17,'#E2EBE5',TEAL,1,'6,4')
p.text(xx(60),zz(0)+5,'4 m STUDY CLEAR STRIP',14,TEAL,True,'middle')
p.line(xx(52),zz(-12),xx(52),zz(12),INK,2)
p.circle(xx(52),zz(0),6,BG,INK,2)
p.text(xx(52),zz(0)+27,'X52 guest door',13,MUT,False,'middle')
p.rect(xx(60),zz(-7.4),7.2*17,5.4*17,BLUE,INK,1.5,'7,4')
p.text(xx(63.6),zz(-5.4),'Quiet bay',15,INK,True,'middle')
p.text(xx(63.6),zz(-3.8),'7.2 x 5.4 m max',12,MUT,False,'middle')
p.rect(xx(60),zz(2),7.2*17,2.5*17,GREEN,INK,1.5,'7,4')
p.text(xx(63.6),zz(3.6),'Planted return',13,INK,True,'middle')
p.line(xx(52),zz(-2),xx(60),zz(-2),TEAL,5,'7,4')
p.text(xx(56),zz(-3),'portal / cove chain',12,MUT,False,'middle')
p.text(xx(48),zz(13.7),'Terrace',14,MUT)
p.text(xx(63),zz(13.7),'Room-side study',14,MUT)
p.para(62,713,'New study coordinates: quiet bay X60..67.2 / Z-7.4..-2; planted return X60..67.2 / Z+2..+4.5. The final 825.8 m2 room contour is missing, so these are candidate positions only.',610,17,MUT)
p.text(773,166,'Section   low bay and clear route',23,INK,True)
sx=lambda v:800+(v+9)*33
sy=lambda h:551-h*34
p.line(sx(-9),sy(0),sx(8),sy(0),INK,2)
p.line(sx(-9),sy(8.25),sx(8),sy(8.25),MUT,1.2,'5,4')
p.text(sx(-9),sy(8.25)-12,'8.25 m historical usable-height budget',15,MUT)
p.line(sx(-7.4),sy(0),sx(-7.4),sy(3.8),INK,3,'7,4')
p.line(sx(-7.4),sy(3.8),sx(-2),sy(3.8),INK,3,'7,4')
p.rect(sx(-7.4),sy(.55),1.4*33,.55*34,BLUE,INK,1,'7,4')
p.rect(sx(2),sy(1.1),2.5*33,1.1*34,GREEN,INK,1,'7,4')
p.text(sx(-7.4),sy(3.8)-15,'Joined shelf / seat / cove',15,INK)
p.text(sx(0),sy(1.5),'CLEAR',14,TEAL,True,'middle')
p.text(sx(0),sy(.8),'4 m study',13,MUT,False,'middle')
p.text(sx(-9),sy(0)+28,'D09 +52.5 m   |   Z cross-section at proposed X64',14,MUT)
p.para(773,616,'The low bay uses the later 3.8 m maximum booth brief. Its ceiling must terminate into the enclosing return, with a joined light channel. The wider room ceiling remains unresolved.',605,17,INK)
p.para(773,723,'Preserve the actual door aperture, turn landings, Z0 route, X35..45 tram reserve and both service/public doors. The 4 m strip is a proposed QA allowance, not a proven body/cart clearance result.',605,17,RUST)
p.finish('Historical baseline + later component brief; all colored assembly locations and 4 m study strip are NEW proposals requiring fit review.')
PDF.save()

# Editable source and traceable ledgers
coverage=baseline
programs={1:'logistics',2:'engineering',3:'crew_homes_and_operations',4:'habitat_homes',5:'medical_species_care',6:'botanical',7:'active_resort',8:'aquatic_wellness',9:'retail_social',10:'dining',11:'culture',12:'library_observation',13:'quiet_homes',14:'mixed_homes',15:'adaptive_homes',16:'family_homes',17:'premier_homes',18:'command'}
crosswalk={'schema':'astraea_reversible_program_crosswalk_v1','status':'historical_records_with_unassigned_proposed_hotels','source':'Astraea_Master_Design_Source.zip / project_docs/architecture/whole_ship_coverage.json','historical_snapshot':coverage['scope']['inventory_snapshot_utc'],'total_records':len(coverage['rooms']),'notes':['All source IDs and historical capacities are retained unchanged.','No current-runtime verification or room relocation is implied.','Latest luxury split, occupancy range and shared crew room override older assumptions; detailed affected IDs are unresolved.'],'rooms':[{'existing_id':r['id'],'historical_name':r['name'],'deck':r['deck'],'historical_kind':r['kind'],'historical_family':r['family_id'],'historical_capacity':r['registered_capacity'],'program_group':programs[r['deck']],'proposed_hotel_id':None,'allocation_status':'unassigned_pending_reconciliation'} for r in coverage['rooms']]}
(OUT/'Astraea_1462_ID_program_crosswalk.json').write_text(json.dumps(crosswalk,indent=2))
ledger={'schema':'astraea_district_study_v1','date':'2026-10-02','authority':'Latest user canon overrides older documents; every hotel box is a new proposal.','canonical':{'decks':18,'length_m':1082,'max_beam_m':240,'reference_height_m':118,'floor_elevations_m':Y,'guest_units':1000,'luxury_units_within_total':{'deluxe':50,'premium':25,'royalty':5,'supreme':1},'passenger_hard_cap':2000,'normal_passenger_occupancy':[1200,2000],'crew_including_player':400,'player_home':'shares existing crew room; exact ID reconciliation open'},'historical_geometry':{'hull_plan_source':'atlas page 13 vector outline; extracted without alterations','hull_plan_zx_m':hull,'atrium':{'x':[-48,48],'z':[-64,64],'decks':[2,17],'main_terraces':[6,9,12,16]},'theater':{'x':[-118,-34],'z':[-265,-115],'y':[69.5,91.5]},'townline_stop_z_m':[-432,-216,-72,216,432],'express_arrival_xz_m':[5.5,-72]},'hotel_alternatives':alternatives,'unresolved':['Upper hull profile and roof clearance','Exact hotel number and names','Membership of all 1000 units and 81 luxury units','All new local lift/stair/service shafts','Multistory suite floor relationships','Moonwell exact boundaries and physical connections','Vesper second-level allocation and waterfall route','Actual current runtime and later pre-loss edits'],'source_policy':'Published study cites filenames and dates, not private Library download URLs.'}
ledger['historical_geometry']['theater']['floor_opening_decks']=[12,13,14]
ledger['historical_geometry']['theater']['gallery_interfaces']=[{'deck':12,'world_xyz_m':[-34,78,-126]},{'deck':13,'world_xyz_m':[-34,84,-126]}]
ledger['historical_geometry']['tram_diagram_note']='Plan bypass is simplified; the sculpted supporting floor ring is omitted. No collision claim.'
ledger['hotel_alternatives'][1]['court_locations']='unresolved; not drawn'
ledger['canonical']['species']=['Koblins','Mantelids','Humans','Baelins','Munkos','Mindos']
ledger['canonical']['court_privacy']='Sleeping areas may overlook courts; selective privacy and acoustic treatment remain design choices.'
ledger['salon_assembly_proposal']={'status':'new adjustable study, not recovered installed geometry','guest_door_xz_m':[52,0],'service_door_xz_m':[98,0],'historical_usable_height_m':8.25,'quiet_bay_candidate_x_m':[60,67.2],'quiet_bay_candidate_z_m':[-7.4,-2],'quiet_bay_max_height_m':3.8,'planted_return_candidate_x_m':[60,67.2],'planted_return_candidate_z_m':[2,4.5],'proposed_study_clear_strip_z_m':[-2,2],'clear_strip_warning':'Not a validated cart/body clearance or replacement for actual turn-landings.','historical_exclusions':['tram strip X35..45','Z0 arrival/service axis','actual X52 and X98 door apertures and turn landings','28m terrace interface Z-14..14'],'unresolved':['final 825.8m2 guest polygon','actual floor/ceiling seams','recovered door aperture and body envelopes']}
ledger['source_hashes']={'D09_CONNECTED_SALON.md':'e917ed91037d5792dd32e7d11d20faedb69ddfb849724bf7b398916b078d39d4','D09_COMPOSITION_CONTRACT.md':'d52e36366f5fc0bfae1ae6ae655b1cdf35f28026f0c82a036338907632f0f137'}
(OUT/'Astraea_allocation_constraint_ledger.json').write_text(json.dumps(ledger,indent=2))
# planning package provenance and limits
readme='''Astraea District Planning Study\n02 October 2026\n\nPurpose\nA reversible whole-ship planning package for district relationships, true deck elevations, two proposed hotel-massing alternatives and a paired district-to-asset kit. It creates no game scene, new floor cuts or room reassignment. Planning and tailored component production can proceed together while exact integration remains gated on recovered geometry and review.\n\nFiles\nAstraea_District_Planning_Study.pdf: eight compact vector sheets\neditable/01..08_planning_sheet.svg: editable vector versions of the sheets\neditable/Astraea_allocation_constraint_ledger.json: dimensions, proposed massing coordinates, assumptions and unresolved allocations\neditable/Astraea_1462_ID_program_crosswalk.json: all surviving stable IDs with historical capacities; no proposed hotel assignments\nbuild_planning_package.py: regenerates the graphics from the retained read-only baseline in inputs/\n\nInterpretation\nSolid geometry is a dated source baseline, not current-runtime verification. Dashed hotel boxes and connections are proposals or explicitly identified historical conversation relationships. The hotel boxes fit inside the known atlas plan footprint and maximum height range, but a detailed upper hull/roof profile has not survived in this package. No full room allocation or new local vertical core is approved.\n\nSources\nAstraea-current-layout-atlas.pdf, 1 October 2026, 21 pages; especially pages 2, 13-14 and 21\nAstraea_Master_Game_Design.pdf, version 0.3, 1 October 2026, 59 pages; historical reference\nAstraea_Master_Design_Source.zip, version 2: SHIP_DESIGN.md, AUDITORIUMS.md, D09_CONNECTED_SALON.md, D09_COMPOSITION_CONTRACT.md, WHOLE_SHIP_COVERAGE.md and whole_ship_coverage.json\nFour original core blueprint sheets: master overview, accommodations, public amenities, and crew/medical/engineering/logistics. Architectural intent only where their labels or totals conflict\nLatest confirmed user direction: 1,000 units including 81 luxury; 2,000 hard passenger cap; normal 1,200-2,000; 400 crew including shared-room player; six species; multistory upper luxury; distinct hotel structures and purposeful courts\nHistorical conversation reports: Moonwell links D08 mineral baths, D09 Paper Moon bookshop and D10 Lantern cafe; Vesper has 240 places, two levels and a waterfall connection to aquatic district. These are preserved without current geometry verification\n\nImportant reconciliation\nThe source archive contains later reports of crew/changing remediation, residential midship cupboards and tested wayfinding positions. Older failures in the master PDF must not be repeated as current facts. Historical test claims do not certify today's missing build.\n\nNext review\nChoose preferred hotel strategy only after program conflicts and circulation are reviewed. Assign each existing ID once, resolve upper hull fit and local cores, and prove suite units versus occupied levels. First coordinated asset kit: D09 salon/atrium threshold, ceiling transitions, quiet built-ins, garden/rail terminals and service returns. Avoid rebuilding the early oversized salon section; use later component language and adjustable interfaces.\n'''
(ROOT/'README.txt').write_text(readme)
assert len(crosswalk['rooms'])==1462 and len({r['existing_id'] for r in crosswalk['rooms']})==1462
print('Created PDF, 8 SVGs, ledgers and README; 1,462 unique source IDs retained')
