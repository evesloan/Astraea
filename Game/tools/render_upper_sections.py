from pathlib import Path
import json
from PIL import Image,ImageDraw,ImageFont
from shapely.geometry import Polygon,LineString
R=Path(__file__).resolve().parents[1];s=json.loads((R/'data/architecture/UPPER_SECTION_COORDINATION.json').read_text());h=json.loads((R/'data/architecture/D17_LUXURY_HOUSES_PROPOSAL.json').read_text())
im=Image.new('RGB',(1440,1120),'#faf9f5');d=ImageDraw.Draw(im)
def f(n):return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',n)
def dashed(a,b,fill):
 ax,ay=a;bx,by=b;n=max(1,int(((bx-ax)**2+(by-ay)**2)**.5/10))
 for i in range(0,n,2):d.line((ax+(bx-ax)*i/n,ay+(by-ay)*i/n,ax+(bx-ax)*min(i+1,n)/n,ay+(by-ay)*min(i+1,n)/n),fill=fill,width=2)
d.text((32,24),'ASTRAEA / UPPER SECTION COORDINATION',font=f(28),fill='#203943')
d.text((32,68),'Candidate occupied volumes and support reservations. No final hull, engineered structure or runtime construction claimed.',font=f(16),fill='#8c4b45')
d.text((32,116),'LONGITUDINAL / port and starboard projected together / vertical scale exaggerated',font=f(19),fill='#203943')
def lon(z,y):return(87+(z+541)*1.17,405-(y-97.5)*10)
def block(point,x0,x1,y0,y1,fill,outline):d.rectangle([point(x0,y1),point(x1,y0)],fill=fill,outline=outline,width=2)
for name,y in s['canonical_decks'].items():
 d.line([lon(-541,y),lon(541,y)],fill='#c7d0d3',width=1);d.text((12,lon(0,y)[1]-7),name,font=f(12),fill='#465962')
dashed(lon(-541,114.5),lon(541,114.5),'#9a655b');d.text((1140,lon(0,114.5)[1]-23),'114.5m roof budget',font=f(14),fill='#9a655b')
block(lon,-180,202,106.5,114.5,'#d8e7e9','#477b86')
for p in s['private_upper_pavilions']:
 z0=min(v[1]for v in p['boundary']);z1=max(v[1]for v in p['boundary']);colour='#bd7180'if p['tier']=='supreme'else'#9d80b0'
 block(lon,z0,z1,106.5,p['external_roof_limit_y'],None,colour)
for r in h['replacements']:
 z0=min(v[1]for v in r['proposed_floor_boundary']);z1=max(v[1]for v in r['proposed_floor_boundary']);block(lon,z0,z1,102,106.5,None,'#a7ac9d')
d.text((lon(-100,113.0)[0],lon(-100,113.0)[1]),'Compact command crown',font=f(17),fill='#2f6270')
d.text((32,448),'Purple/red outlines: private upper levels of six existing units, at different transverse positions from the command crown.',font=f(16),fill='#465962')
d.text((32,479),'The lower hull/body profile remains unresolved. A datum line is not a proposed full flat slab or final pressure envelope.',font=f(16),fill='#8c4b45')
d.text((32,535),'TRANSVERSE AT Z=38m / central houses, atrium cover and crown / vertical scale exaggerated',font=f(19),fill='#203943')
def cross(x,y):return(92+(x+120)*5.2,935-(y-97.5)*14)
dashed(cross(-120,114.5),cross(120,114.5),'#9a655b')
block(cross,-48,48,97.5,106.26,'#f4f1e9','#dac49f');d.text(cross(-33,101.8),'Protected atrium void',font=f(18),fill='#8d734b')
block(cross,-48,48,106.26,106.5,'#8b969b','#5f6d74')
block(cross,-36,36,106.5,111,'#d8e7e9','#477b86')
block(cross,-50.5,50.5,111,114,'#ddd9ce','#90846f')
for x in [-50.5,50.5]:dashed(cross(x,102),cross(x,114),'#90846f')
d.line([cross(-52,114.5),cross(52,114.5)],fill='#477b86',width=3)
d.text(cross(-29,112.9),'Transfer zone: fit before construction',font=f(13),fill='#74634c')
d.text(cross(-23,109.3),'4.5m crown clearance reserve',font=f(13),fill='#2f6270')
for r in h['replacements']+h['replanned_standard_units']:
 p=Polygon(r['proposed_floor_boundary']).intersection(LineString([(-130,38),(130,38)]))
 if p.is_empty:continue
 x0,x1=p.bounds[0],p.bounds[2];colour={'supreme':'#c88e99','royalty':'#b69bc6'}.get(r.get('tier'),'#c8d0c0')
 block(cross,x0,x1,102,106.5,colour,'#657467')
 if r.get('upper_floor_y')is not None:block(cross,x0,x1,106.5,r['proposed_external_roof_limit_y'],colour,'#657467')
for x0,x1 in [(-94,-76),(76,94)]:
 d.line([cross(x0,102),cross(x1,102)],fill='#77966b',width=4);d.text(cross(x0,101.5),'Court',font=f(13),fill='#58774e')
d.text((32,992),'Retain the full opaque atrium/house covers. Fit perimeter bearings and crown supports without posts through the grand void.',font=f(16),fill='#465962')
d.text((32,1026),'Court/roof-garden levels, openings, wall thickness, pressure enclosure, private lifts and all-species fit remain design gates.',font=f(16),fill='#8c4b45')
d.text((32,1060),'Roof limits: general D17 106.5m / Royalty 112m / Supreme 114.5m / command crown 114.5m / provisional keel −3.5m. Unadopted.',font=f(16),fill='#465962')
im.save(R/'docs/whole_ship_plans/upper_section_coordination.png')
