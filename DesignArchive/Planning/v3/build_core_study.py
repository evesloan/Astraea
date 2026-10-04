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
PDF=canvas.Canvas(str(ROOT/'Astraea_Forward_Commons_Core_Study_v3.pdf'),pagesize=(1080,675))
PDF.setTitle('Astraea Forward Commons Arrival and Core Study v3');PDF.setAuthor('Astraea planning')

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

features=json.loads((ROOT/'inputs/atlas_allocations.json').read_text())
baseline=json.loads((ROOT/'inputs/historical_baseline.json').read_text())
Y=[0,6,12,16.5,21,27,35.5,44,52.5,61,69.5,78,84,88.5,93,97.5,102,106.5]
COMMON={'name':'Port forward commons','x':[-97,-63],'z':[-384,-356]}
R1=[{'name':'Guest core','x':[-62,-56],'z':[-386,-378]},{'name':'Guest landing','x':[-63,-54],'z':[-378,-374]},{'name':'Service core','x':[-62,-56],'z':[-362,-354]},{'name':'Service landing','x':[-63,-54],'z':[-366,-362]}]
R3=[{'name':'Guest core','x':[-40,-34],'z':[-386,-378]},{'name':'Guest landing','x':[-40,-34],'z':[-378,-374]},{'name':'Service core','x':[-54,-48],'z':[-386,-378]},{'name':'Service landing','x':[-54,-48],'z':[-378,-374]}]
STAFF={'name':'Service/staff ribbon','x':[-59.5,-54.5],'z':[-541,541]}
UPPER_CROSS={'name':'Upper transverse ribbon','x':[-110,110],'z':[-374,-366]}
LANE={'name':'Port residential lane','x':[-46,-42],'z':[-541,-80]}
SIDE={'name':'Port public sidewalk','x':[-7.8,-3.2],'z':[-541,-80]}
SPUR={'name':'Proposed D12 guest spur','x':[-40,-5.5],'z':[-374,-366]}
STAFF_LINK={'name':'Proposed D12 service threshold link','length_x_m':0.5,'width_z_m':4,'x':[-54.5,-54],'z':[-378,-374]}

def intersection(a,b):
 x=[max(a['x'][0],b['x'][0]),min(a['x'][1],b['x'][1])];z=[max(a['z'][0],b['z'][0]),min(a['z'][1],b['z'][1])]
 return {'x':x,'z':z,'area_m2':round((x[1]-x[0])*(z[1]-z[0]),6)} if x[1]>x[0]+1e-8 and z[1]>z[0]+1e-8 else None

def geom(p,x,y,s,zlim,xlim,deck=None):
 z=lambda v:x+(v-zlim[0])*s;xx=lambda v:y+(v-xlim[0])*s
 p.rect(x,y,(zlim[1]-zlim[0])*s,(xlim[1]-xlim[0])*s,'#F0F0E9',LINE)
 def rec(r,fill=PALE,stroke=INK,sw=.8,dash=None):
  a,b=max(r['z'][0],zlim[0]),min(r['z'][1],zlim[1]);c,d=max(r['x'][0],xlim[0]),min(r['x'][1],xlim[1])
  if b>a and d>c:p.rect(z(a),xx(c),(b-a)*s,(d-c)*s,fill,stroke,sw,dash)
 if deck:
  for r in features:
   if r['deck']==deck:rec(r,GOLD if r['kind']=='named_allocation' else '#D7DDD8',INK,.55)
 return z,xx,rec

def routes(p,z,xx,rec,upper=False,lower=False):
 rec(SIDE,'#BFD7C2',None)
 if upper:rec(UPPER_CROSS,'#BFD7C2',None);rec(LANE,'#BFD7C2',None)
 if lower:rec(STAFF,'#A5ADB9',None)

def draw_bays(p,z,xx,rec,bays,labels=False):
 for r in bays:
  col=BLUE if r['name'].startswith('Guest') else ROSE
  rec(r,col,TEAL,1.5,'5,3')
  if labels:p.text(z(sum(r['z'])/2),xx(sum(r['x'])/2)+5,('G' if r['name'].startswith('Guest') else 'S')+('L' if 'landing' in r['name'] else ''),15,INK,True,'middle')

# 1 Historical horizontal approach, with coordinates rather than affiliation colors
p=Page(1,'Forward commons arrival   a traceable horizontal route','Use the surviving upper-deck ribbons and commons door before placing new core bays. This study covers one port-forward stack on D13-D17; v2 affiliations remain unchanged.')
z,xx,rec=geom(p,62,196,4.3,[-480,-294],[-110,10],13)
routes(p,z,xx,rec,upper=True)
rec(COMMON,GOLD,INK,1.6)
p.text(z(-370),xx(-81),'COMMONS',17,INK,True,'middle');p.text(z(-370),xx(-74),'X -97..-63',14,MUT,False,'middle')
p.line(z(-432),xx(0),z(-294),xx(0),RUST,2)
p.circle(z(-432),xx(0),7,BG,RUST,2);p.text(z(-432),xx(0)+34,'Townline -432',15,RUST,True,'middle')
p.line(z(-432),xx(0),z(-432),xx(-5.5),RUST,3,'4,4')
p.arrow(z(-432),xx(-5.5),z(-370),xx(-5.5),TEAL,3)
p.arrow(z(-370),xx(-5.5),z(-370),xx(-63),TEAL,3)
p.circle(z(-370),xx(-63),6,BG,INK,2)
p.text(z(-435),xx(-14),'62 m along sidewalk',15,TEAL,True)
p.text(z(-347),xx(-35),'57.5 m',16,TEAL,True)
p.text(z(-470),xx(-49),'Local lane X -44',15,MUT)
p.text(62,173,'BOW toward Z -541  |  PORT at top  |  dimensions in metres',15,MUT)
p.text(62,742,'D13 representative; the same route ribbons and commons datum recur on D14-D17.',16,MUT)
p.text(928,184,'Historical evidence',23,INK,True)
y=224
for title,body in [('Townline stop','Plotted center: X 0, Z -432. The logical boarding vestibule and its actual exit geometry are missing.'),('Public sidewalk','X -5.5 centerline; 4.6 m drawn width. Existing upper branch starts at Z -370.'),('Commons threshold','Door marker at X -63, Z -370. Preserve the whole 8 m transverse ribbon and the existing door interface.'),('Residential branch','Local lane at X -44; 4 m drawn width. Guest rectangles and their assigned IDs remain separate evidence.')]:
 p.text(928,y,title,19,INK,True);y=p.para(928,y+27,body,450,17,MUT,leading=24)+25
p.para(62,792,'119.5 m of route is traceable along historical ribbons. The 5.5 m stop-to-sidewalk offset is only a proposed connection line. Neither distance certifies a traversable route or boarding fit.',1306,18,INK)
p.finish('Evidence: atlas pp. 15-19 vector paths and door marker; atlas p. 2 limits. No new room affiliation or unit capacity is assigned.')

# 2 Proposed located reservations, deliberately avoiding the upper routes
p=Page(2,'Preferred test   two upper core bays beside the shared route','New reservation coordinates are test inputs. The bays start at D12 and serve the D13-D17 commons stack in principle; mechanism, structural and headroom fit remain open.')
z,xx,rec=geom(p,62,162,8.7,[-400,-344],[-100,-28],13)
routes(p,z,xx,rec,upper=True);rec(COMMON,GOLD,INK,1.5);draw_bays(p,z,xx,rec,R3,True)
p.circle(z(-370),xx(-63),5,BG,INK,2)
p.text(z(-383),xx(-87),'Complete shared commons',15,INK,True)
p.text(z(-383),xx(-82),'Retain X -97..-63 / Z -384..-356',12,MUT)
p.text(z(-366)+11,xx(-65),'Existing door',13,INK,True)
p.text(z(-366)+11,xx(-60),'(-63, -370)',13,MUT)
p.text(z(-392),xx(-43),'4 m local lane',13,MUT)
p.text(z(-366)+11,xx(-37),'8 m shared cross-street',13,TEAL,True)
p.text(588,184,'Located proposal',24,INK,True)
y=225
for title,body,col in [('G  Guest core reservation','X -40..-34 / Z -386..-378\n6 x 8 m plan test; no lift count or passenger capacity inferred.',BLUE),('GL  Guest landing','X -40..-34 / Z -378..-374\n6 x 4 m, facing the retained cross-street. Aperture and moving-leaf pocket are unknown.',BLUE),('S  Service core reservation','X -54..-48 / Z -386..-378\n6 x 8 m test; separate vertical staff use. Cart turn, doors and equipment are unsized.',ROSE),('SL  Service landing','X -54..-48 / Z -378..-374\n6 x 4 m. Upper staff delivery still joins the shared public cross-street.',ROSE)]:
 p.rect(588,y-16,12,12,col,INK,.7);p.text(617,y,title,20,INK,True);y=p.para(617,y+29,body,740,17,MUT,leading=23)+31
p.text(588,715,'Keep the route hierarchy legible',21,INK,True)
p.para(588,746,'The X -44 lane remains between the bays with 2 m to each reservation. Both landings meet the full Z -374..-366 cross-street without reducing its drawn width. The commons door and allocation remain unchanged.',785,17,MUT)
p.finish('Dashed bays and landings are new proposals. Zero upper room-rectangle or ribbon intersections in the 2D screen; host feasibility is unproven.')

# 3 Rejected options catch different kinds of conflict
p=Page(3,'Why the first full-height placements fail','Room rectangles alone miss circulation conflicts. Two rejected reservations explain why the preferred test moves inboard and begins above D11.')
p.text(62,162,'R1  At the commons edge',23,INK,True)
p.text(770,162,'R2  Straight inboard stack',23,INK,True)
z,xx,rec=geom(p,62,191,4.7,[-408,-338],[-84,-20],9);routes(p,z,xx,rec,lower=True);draw_bays(p,z,xx,rec,R1)
for r in R1:
 q=intersection(r,STAFF)
 if q:rec(q,'#C77B6E',RUST,1)
p.text(62,525,'D09 representative service/staff ribbon',16,MUT)
p.para(428,212,'Protected ribbon\nX -59.5..-54.5\n5 m drawn width\nD09-D12',282,19,INK,True,leading=29)
p.para(428,362,'Each core overlaps 28 m2; each landing overlaps 20 m2 of the ribbon on every screened lower deck.',282,18,RUST,leading=25)
z,xx,rec=geom(p,770,191,4.7,[-408,-338],[-84,-20],11);routes(p,z,xx,rec,lower=True);draw_bays(p,z,xx,rec,R3)
music=next(r for r in features if r.get('stable_id')=='D11_music')
for r in R3:
 q=intersection(r,music)
 if q:rec(q,'#C77B6E',RUST,1)
p.text(770,525,'D11 Music room remains protected',16,MUT)
p.para(1133,212,'Music room\nX -54..-8\nZ -384..-316\nD11_music',245,19,INK,True,leading=29)
p.para(1133,362,'The twin cores and their landings would overlap 120 m2 of its historical allocation in total.',245,18,RUST,leading=25)
p.text(62,558,'Gray matches the service/staff legend; service-route meaning is inferred. Drawn width is not certified clear width.',16,MUT)
p.text(62,600,'Disposition',23,INK,True)
p.para(62,631,'Reject R1: keep the service/staff ribbon continuous. Reject R2 as a D09-D17 stack: retain the Music room and its public access. R3 uses the same inboard twin-bay plan only from D12 upward, with separately proposed lower-level approach links.',1300,20,INK,leading=29)
p.text(62,737,'No hidden permission to occupy the gap',21,INK,True)
p.para(62,774,'A clear 2D overlay is only a candidate. Unshown structure, service equipment, final room walls, fire/egress needs, lift pits and ceiling zones may still occupy or constrain it. No floor openings or host edits are made.',1300,18,MUT)
p.finish('Overlap areas describe geometric conflicts, never room counts, lost capacity or approval to relocate an allocation. Protected capacities remain unchanged.')

# 4 D12 base approach and actual upper section datums
p=Page(4,'D12 transfer level and upper section strategy','Start the proposed local cores at D12 to retain the D11 Music allocation. Express and Townline remain the documented travel interfaces while these interfaces are unresolved.')
z,xx,rec=geom(p,62,183,3.65,[-478,-282],[-65,3],12);routes(p,z,xx,rec,lower=True);draw_bays(p,z,xx,rec,R3)
rec(SPUR,None,TEAL,2,'6,4');rec(STAFF_LINK,None,RUST,2,'3,2')
p.arrow(z(-432),xx(-5.5),z(-370),xx(-5.5),TEAL,2)
p.arrow(z(-370),xx(-5.5),z(-370),xx(-37),TEAL,2,'6,4')
p.arrow(z(-370),xx(-37),z(-376),xx(-37),TEAL,2,'6,4')
p.text(z(-451),xx(-28),'Horizon room',16,INK,True,'middle');p.text(z(-324),xx(-28),'Listening salon',16,INK,True,'middle')
p.circle(z(-432),xx(-8),3,INK,INK,1);p.circle(z(-324),xx(-8),3,INK,INK,1)
p.text(62,466,'Historical public entries stay on the port sidewalk; both destinations retain their full footprints.',15,MUT)
p.text(829,177,'D12 approach proposals',22,INK,True)
p.para(829,213,'Guest: new 8 m spur at Z -374..-366, X -40..-5.5, linking the known port sidewalk to the guest landing. The historical D12 transverse ribbons are elsewhere; this spur is not recovered geometry.',548,17,MUT,leading=24)
p.para(829,338,'Staff: a 0.5 m long x 4 m wide threshold link from the service ribbon edge X -54.5 to the service landing at X -54. The ribbon stays open. Exact wall, door, cart turning and support conditions need recovery.',548,17,MUT,leading=24)
p.text(62,532,'Proposed vertical travel range   exact floor datums',23,INK,True)
sy=lambda y:792-(y-69.5)*5.7
for i in range(10,18):
 yy=sy(Y[i]);p.line(177,yy,687,yy,LINE,1);p.text(152,yy+4,f'D{i+1:02}  {Y[i]:g}',14,MUT,False,'end')
for x,label,col in [(243,'Guest',BLUE),(464,'Service',ROSE)]:
 p.rect(x,sy(102),117,sy(78)-sy(102),col,TEAL,1.5,'6,4');p.text(x+58,sy(93)+5,label,17,INK,True,'middle')
 p.rect(x,sy(106.5),117,sy(102)-sy(106.5),None,RUST,1.5,'3,3')
p.text(715,sy(106.5)+4,'Headroom and D18 interface unknown',16,RUST,True)
p.text(715,sy(102)+5,'D13-D17 commons levels remain complete',16,INK,True)
p.text(715,sy(88.5),'No lift speed, cabin count or capacity assigned',16,MUT)
p.text(715,sy(78)+5,'D12 base Y78: pit and slab/support fit unresolved',16,RUST,True)
p.text(243,sy(69.5)-10,'D11 Music remains below',16,INK,True)
p.finish('Section shows intended connection range, not built shafts or slab openings. Upper hull, roof clearance, machinery and fire/egress provisions are unverified.')

# 5 Before/after ledger and concrete next asset interfaces
p=Page(5,'Protected footprints and the next interface decisions','R3 is a preferred coordinate-based test for one stack. It preserves the named programs and historical route strips in the available plan evidence, while keeping all missing host geometry explicit.')
p.text(62,161,'Protected program beside the study',22,INK,True)
rows=[('D09','Orchard market','X -54..-8 / Z -466..-398','D09_market0'),('D10','The shared table / 240 places','X -54..-8 / Z -466..-398','D10_dining0'),('D11','The music room','X -54..-8 / Z -384..-316','D11_music'),('D12','Horizon room','X -54..-8 / Z -466..-398','D12_observation0'),('D12','Listening salon','X -54..-8 / Z -358..-290','D12_listening2'),('D13-D17','Complete port forward commons','X -97..-63 / Z -384..-356','Geometry-to-ID mapping unresolved')]
y=199
for a,b,c,d in rows:
 p.text(62,y,a,16,TEAL,True);p.text(174,y,b,17,INK,True);p.text(174,y+23,c,15,MUT);p.text(174,y+44,d,13,MUT);p.line(62,y+55,715,y+55,LINE);y+=77
p.text(780,161,'Before and after',22,INK,True)
y=p.para(780,201,'R1: conflicts with the lower service/staff ribbon. Rejected.\nR2: clears that ribbon but intersects D11 Music. Rejected as a continuous lower-to-upper core.\nR3: starts at D12, with new guest and staff approach stubs. Bays avoid protected plan footprints; the guest spur deliberately joins the sidewalk.',598,18,INK,leading=26)+18
p.text(780,y,'Hard evidence gates',21,INK,True);y+=34
for t in ['Recover wall, floor/support and lift-pit geometry at Y78; no assumption that stopping above Music avoids an underfloor conflict.','Verify moving door clear span, clear head, leaf travel and cassette on each landing; no dimensions borrowed from salon fixtures.','Check actual cart/body turns and supported routes. Upper delivery shares the public cross-street; segregated back-of-house access is not established.','Recover upper hull and machinery/headroom; reconcile 1,000 units and 81 luxury units by ID and real room geometry.']:
 y=p.para(780,y,t,590,16,MUT,leading=22)+13
p.para(62,687,'Door markers on the port public side remain X -8: market / dining / Horizon at Z -432; Music at -350; Listening at -324.',650,15,MUT,leading=20)
p.text(62,746,'Planning to asset handoff',22,INK,True)
p.para(62,780,'Next useful kit: a paired guest landing return and service threshold/stow edge, parametric to the 6 x 4 m study landings. Preserve the 8 m cross-street and 4 m residential lane. Test a calm commons-facing guest identity beside a clearly serviceable cart-side interface before authoring shafts or moving mechanisms.',1310,18,MUT)
p.finish('D09 shops and upper guest rectangles are also screened and unchanged. No new room IDs, capacities, allocations, runtime geometry or floor cuts are produced.')
PDF.save()

# Structured, reproducible conflict screen. Geometry-record counts are never capacity.
def hits(shapes,decks):
 out=[]
 for deck in decks:
  for r in features:
   if r['deck']!=deck:continue
   for shape in shapes:
    q=intersection(shape,r)
    if q:out.append({'deck':deck,'reservation':shape['name'],'protected_record':r,'intersection':q})
 return out
r1_staff=[{'deck':deck,'reservation':r['name'],'intersection':intersection(r,STAFF)} for deck in range(9,13) for r in R1]
r2_hits=hits(R3,range(9,18));r3_hits=hits(R3+[SPUR,STAFF_LINK],range(12,18))
# The D12 spur and link only exist on D12; above it the historical cross-street is retained.
r3_hits=hits(R3,range(12,18))+hits([SPUR,STAFF_LINK],[12])
ledger={'schema':'astraea_forward_commons_core_study_v3','date':'2026-10-02','authority':'preferred provisional coordinate study; no implementation or accepted shaft allocation','source_policy':'historical atlas drawings and dated source claims, not a current runtime survey','preserved_prior_revision':{'v2_pdf_sha256':'4186a5279aa0d1d9546e4bea0e37993ea614e3debccc057fa928ab97505a20b0','v2_zip_sha256':'3e8f2163ceac3bcc36ad708d9a0d0edb67780cefe0c010aa40ec202ebeafcdd5'},'existing_upper_arrival':{'decks':list(range(13,18)),'stop_center_xz':[0,-432],'boarding_to_sidewalk':'unverified; nominal 5.5m offset only','verified_drawing_trace_xz':[[-5.5,-432],[-5.5,-370],[-63,-370]],'drawing_trace_length_m':119.5,'sidewalk':SIDE,'transverse':UPPER_CROSS,'residential_lane':LANE,'commons':COMMON,'navigation_certification':False},'existing_lower_service_ribbon':{'decks':[9,10,11,12],'semantic_status':'Service-route interpretation from service/staff legend color; vector position/width explicit, built clearance unverified',**STAFF},'candidate_dispositions':[{'id':'R1','status':'rejected','decks':list(range(9,18)),'reservations':R1,'reason':'lower service/staff ribbon intersections','ribbon_intersections':r1_staff,'room_intersections':hits(R1,range(9,18))},{'id':'R2','status':'rejected as D09-D17 stack','decks':list(range(9,18)),'reservations':R3,'reason':'D11 Music room intersections','room_intersections':r2_hits},{'id':'R3','status':'preferred conditional test','decks':list(range(12,18)),'reservations':R3,'proposed_d12_guest_spur':SPUR,'proposed_d12_service_link':STAFF_LINK,'room_intersections':r3_hits,'lower_floor_y_m':78,'last_served_floor_y_m':102,'upper_headroom_zone':'unresolved, including interface to D18 Y106.5','lift_pit_and_structure':'unresolved; Music remains protected below','capacity':None,'mechanism_or_cabin_count':None,'floor_openings_authorized':False}],'protected_public_front_doors_xz':{'D09_market0':[-8,-432],'D10_dining0':[-8,-432],'D11_music':[-8,-350],'D12_observation0':[-8,-432],'D12_listening2':[-8,-324]},'protected_neighbor_ids':['D09_market0','D10_dining0','D11_music','D12_observation0','D12_listening2'],'unchanged_registry_id_count':1462,'new_room_id_assignments':0,'guest_units':1000,'luxury_in_total':{'deluxe':50,'premium':25,'royalty':5,'supreme':1},'accommodation_reconciliation':'unresolved; no unit counts from rectangles','unknown_interfaces':['Townline boarding vestibule and exit','Forward commons door dimensions and leaf pockets','Proposed landing apertures and service/cart turns','All structural slabs and core support','D12 pit and Music ceiling coexistence','Upper hull and shaft headroom','Protected fire/egress provision','Final room polygons and ID mapping'],'next_asset_pairing':{'proposal':'paired guest landing return and service threshold/stow edge','landing_plan_test_m':[6,4],'moving_mechanisms':'unassigned','route_reservations_to_preserve':[UPPER_CROSS,LANE]}}
(OUT/'Astraea_forward_core_constraint_ledger_v3.json').write_text(json.dumps(ledger,indent=2))
(ROOT/'README.txt').write_text('''Astraea Forward Commons Arrival and Core Study v3
02 October 2026

Scope
A five-sheet reversible coordinate study of one port-forward commons stack. It follows v2's mixed-use affiliation strategy, and preserves the final v2 PDF and editable archive under history/. No runtime, floor cuts, room reassignment, original-project or asset-catalogue edits are made.

Conclusions
The historical upper arrival trace runs from the port sidewalk at X-5.5/Z-432 to Z-370 and then to the commons door X-63/Z-370. That is 119.5m of drawn route, with a separate unresolved 5.5m nominal stop connection. Atlas ribbons are authored markings/access links, not independently certified navigation.
R1 is rejected because its bays intersect the 5m lower service/staff-colored ribbon. Its service-route meaning is inferred from the atlas legend; its drawn width is not a certified clear width. R2 is rejected as a continuous D09-D17 stack because its bays and landings intersect D11 Music. R3 is a conditional test beginning at D12: two 6x8m core reservations and separate 6x4m landings, preserving the full upper cross-street and local residential lane. No lift count, capacity, pit, shaft or headroom fit is implied.

Contents
Astraea_Forward_Commons_Core_Study_v3.pdf: visually reviewed five-sheet study
editable/: five SVG sheets and a structured before/after constraint ledger
inputs/: historical atlas allocation records, route evidence, baseline registry, font files
history/: unchanged final v2 PDF, editable archive and manifest
build_core_study.py and validate_core_study.py: regeneration/check scripts (Python3, reportlab, PyMuPDF)

Sources and limits
Astraea-current-layout-atlas.pdf, historical 1 October 2026 snapshot. Main-plan room rectangles and route vectors are read from pp11-19; the atlas itself warns that ribbons are not navigation certification. All 1,462 registry IDs remain unchanged. The commons vector label is not silently assigned to a source ID. Upper hull fit, 81 luxury assignments, exact doors, slab support, service mechanisms and later room polygons remain unresolved. The D12 shaft-base proposal can still conflict below its floor if the lift pit or support intrudes into Music; no such fit is assumed.

Asset coordination
The next useful candidate is an adjustable guest landing return paired with a cart-side service threshold/stow edge, tested against a 6x4m landing and the preserved 8m/4m route ribbons. These are planning reservations, not adopted host dimensions.
''')
print('Created v3 five-sheet coordinate study and ledger')
