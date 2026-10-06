from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[4];O=R/'docs/architecture_packages/upper_hull'
im=Image.new('RGB',(1500,950),'#102033');d=ImageDraw.Draw(im)
f='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
try: big=ImageFont.truetype(f,26);font=ImageFont.truetype(f,18);small=ImageFont.truetype(f,15)
except OSError:big=font=small=ImageFont.load_default()
def text(x,y,s,c='#e5edf5',ft=font):d.text((x,y),s,fill=c,font=ft)
def line(points,c,w=3):d.line(points,fill=c,width=w)
text(30,20,'ASTRAEA: upper-shell coordinate proposal',ft=big);text(30,58,'PROPOSED DESIGN COORDINATION ONLY. No source geometry adopted. No as-built image.',c='#ffbf65')
text(35,108,'1  Theater west section');text(800,108,'2  Theater longitudinal shoulder return at Y87.5')
def p(x,y):return(50+(x+121)*11,660-(y-61)*15)
for y in [61,69.5,78,84,87.5,92]:
 a,b=p(-121,y),p(-88,y);line([a,b],'#35516e',1);text(b[0]+5,b[1]-9,f'Y{y}',ft=small)
a=[(-120,61),(-118.2,69.5),(-115.2,78),(-112.8,84),(-111,88.5),(-109.6,92)]
b=[(-120,61),(-118.5,69.5),(-118.5,87.5),(-109.6,92)]
line([p(x,y) for x,y in a],'#55c5f0',4);line([p(x,y) for x,y in b],'#ffbf65',5)
line([p(-117.7,69.5),p(-117.7,87.008),p(-107.828,92)],'#e98c43',2)
for y,label in [(72.5,'Stalls cart'),(81,'First gallery cart'),(87,'Crown gallery cart')]:
 line([p(-117,y),p(-113.6,y)],'#ff7380',6);text(215,p(-117,y)[1]-12,label+' top +3m',ft=small)
text(35,704,'Blue: general taper A   Orange: theater shoulder B',ft=small);text(35,730,'0.18m skin +0.22m frame +0.40m inspection/withdrawal band',ft=small);text(35,756,'Normal offset on slope =1.773m transverse, not 0.8m',ft=small);text(35,782,'0 chair / aisle normal-band failures; minimum route margin 0.323m',ft=small)
def q(z,w):return(820+(z+280)*3.5,640-(w-108)*26)
for z in [-275,-265,-250,-160,-115,-105]:
 line([q(z,108),q(z,120)],'#35516e',1);text(q(z,108)[0]-16,650,f'{z}',ft=small)
line([q(z,w) for z,w in [(-275,111.4),(-265,118.5),(-115,118.5),(-105,111.4)]],'#ffbf65',5)
line([q(-275,111.4),q(-105,111.4)],'#55c5f0',3)
line([q(-250,118.5),q(-160,118.5)],'#76dbb2',9)
text(835,178,'10m fore return |150m plateau |10m aft return',ft=small);text(835,220,'Pilot: Y74.5–87.5, Z−250…−160, X−118.5',c='#76dbb2',ft=small);text(835,255,'Green = bounded source-authoring pilot',ft=small);text(835,710,'Pilot: no mesh/slab/core contact candidates in decoded sources',ft=small);text(835,740,'Return triangles and full shell remain unadopted',ft=small)
text(35,837,'HOUSE / CROWN PRESERVATION',ft=font);text(35,867,'House mesh reaches X118.080, roof 106.300: wall target 119.5 fits; no duplicate 106.5 roof',ft=small);text(35,895,'Six pavilion 1.5m normal-offset polygons fit maximum outline by≥0.5m. Roof/lift fit remains open',ft=small);text(35,923,'Crown source roof 114.450 leaves 0.05m to 114.5 cap: preserve existing roof owners; never overlay another shell',ft=small)
im.save(O/'UPPER_HULL_PROFILE_PROPOSAL.png')
