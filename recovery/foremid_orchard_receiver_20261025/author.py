"""Additive, unselected upper receiving geometry; never edits retained inputs."""
import json, hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[2]
D=R/'Game/foremid_orchard_receiver_20261025'
D.mkdir(exist_ok=True)
parts=[]
def box(name,lo,hi,role):
 assert all(a<b for a,b in zip(lo,hi)), name
 parts.append(dict(name=name,lo=lo,hi=hi,role=role,collision=True))
def slab(name,x0,x1,z0,z1,y,depth=.24):box(name,[x0,y-depth,z0],[x1,y,z1],'warm_stone')
def rail(name,a,b,y):
 # Boundary only. Glass retains physical contact, never a collision omission.
 x0,z0=a;x1,z1=b
 if x0==x1:
  box(name+'_glass',[x0-.012,y+.18,min(z0,z1)],[x0+.012,y+1.1,max(z0,z1)],'glass')
  box(name+'_handrail',[x0-.07,y+1.1,min(z0,z1)],[x0+.07,y+1.18,max(z0,z1)],'warm_walnut')
 else:
  assert z0==z1
  box(name+'_glass',[min(x0,x1),y+.18,z0-.012],[max(x0,x1),y+1.1,z0+.012],'glass')
  box(name+'_handrail',[min(x0,x1),y+1.1,z0-.07],[max(x0,x1),y+1.18,z0+.07],'warm_walnut')
slab('UpperStationGallery',-13.4,-7.8,-257.6,-225,61)
# Existing D10 route owns X[-4,4]; do not duplicate its slab.
slab('MissingOnlyOverRailReceiving',-7.8,-4,-237.2,-233.2,61)
slab('UpperStairArrival',-15.8,-13.4,-254,-251.6,61)
slab('LowerStairArrival',-15.8,-13.2,-257.6,-255.2,56.1)
slab('MidLanding',-21.72,-19.72,-257.6,-251.6,58.55)
for i in range(14):
 # 175mm risers, 280mm treads, 2.4m clear flight width.
 x=-15.8-(i+1)*.28
 slab('UpWest_%02d'%i,x,x+.28,-257.6,-255.2,56.1+(i+1)*.175,.175)
 x=-19.72+i*.28
 slab('UpEast_%02d'%i,x,x+.28,-254,-251.6,58.55+(i+1)*.175,.175)
for side in [-257.6,-255.2]:
 for i in range(14):
  y=56.1+(i+1)*.175;x=-15.8-(i+1)*.28
  rail('WestFlightGuard_%s_%02d'%(side,i),(x,side),(x+.28,side),y)
for side in [-254,-251.6]:
 for i in range(14):
  y=58.55+(i+1)*.175;x=-19.72+i*.28
  rail('EastFlightGuard_%s_%02d'%(side,i),(x,side),(x+.28,side),y)
for name,a,b,y in [
 ('GalleryWestNorth',(-13.4,-257.6),(-13.4,-254),61),
 ('GalleryWestSouth',(-13.4,-251.6),(-13.4,-225),61),
 ('GalleryEastNorth',(-7.8,-257.6),(-7.8,-237.2),61),
 ('GalleryEastSouth',(-7.8,-233.2),(-7.8,-225),61),
 ('BridgeNorth',(-7.8,-237.2),(-4,-237.2),61),
 ('BridgeSouth',(-7.8,-233.2),(-4,-233.2),61),
 ('GalleryNorth',(-13.4,-257.6),(-7.8,-257.6),61),
 ('MidWest',(-21.72,-257.6),(-21.72,-251.6),58.55),
 ('MidNorth',(-21.72,-257.6),(-19.72,-257.6),58.55),
 ('MidSouth',(-21.72,-251.6),(-19.72,-251.6),58.55),
 ('UpperArrivalNorth',(-15.8,-254),(-13.4,-254),61),
 ('UpperArrivalSouth',(-15.8,-251.6),(-13.4,-251.6),61),
 ('LowerArrivalNorth',(-15.8,-257.6),(-13.2,-257.6),56.1),
 ('LowerArrivalSouth',(-15.8,-255.2),(-13.2,-255.2),56.1)]:rail(name,a,b,y)
# Continuous sloping rails/stringers replace the first drafting pass's stepped rails.
parts[:]=[p for p in parts if not p['name'].startswith(('WestFlightGuard','EastFlightGuard'))]
for name,a,b,z0,z1 in [('West',[-15.8,56.1],[-19.72,58.55],-257.6,-255.2),('East',[-19.72,58.55],[-15.8,61],-254,-251.6)]:
 for side,z in enumerate([z0,z1]):
  parts.append(dict(name=name+'Stringer'+str(side),kind='beam',a=[a[0],a[1]-.2,z+(0.12 if side==0 else -.12)],b=[b[0],b[1]-.2,z+(0.12 if side==0 else -.12)],width=.16,depth=.32,role='champagne_metal',collision=True))
  parts.append(dict(name=name+'Handrail'+str(side),kind='beam',a=[a[0],a[1]+1.14,z],b=[b[0],b[1]+1.14,z],width=.14,depth=.08,role='warm_walnut',collision=True))
  vertices=[[x,y,z+dz] for dz in [-.012,.012] for x,y in [(a[0],a[1]+.18),(b[0],b[1]+.18),(b[0],b[1]+1.1),(a[0],a[1]+1.1)]]
  parts.append(dict(name=name+'Glass'+str(side),kind='poly',vertices=vertices,role='glass',collision=True))
# Hold the future third lift stop closed until its exact source shaft successor is fitted.
rail('ThirdStopHold',(-13.4,-225),(-7.8,-225),61)
for z in [-249,-241,-233]:
 for x in [-13.05,-8.05]:
  box('Column_%s_%s'%(x,z),[x-.08,52.5,z-.08],[x+.08,60.76,z+.08],'champagne_metal')
 box('Crossbeam_%s'%z,[-13.3,60.4,z-.1],[-7.9,60.76,z+.1],'champagne_metal')
for x in [-21.5,-19.9,-15.6]:
 for z in [-257.4,-251.8]:
  top=58.31 if x<-19 else (55.86 if z<-255 else 60.76)
  box('StairPier_%s_%s'%(x,z),[x-.1,52.5,z-.1],[x+.1,top,z+.1],'champagne_metal')
# Net clear dimensions include the 70mm handrail half-width. Widen physical
# slabs and guards together, rather than labeling a 4m slab as 4m clear.
z_receiving={-237.2:-237.3,-233.2:-233.1,-257.6:-257.7,-255.2:-255.1,-254:-254.1,-251.6:-251.5}
for p in parts:
 for k in ['lo','hi','a','b']:
  if k in p:p[k][2]=z_receiving.get(p[k][2],p[k][2])
 if p.get('kind')=='poly':
  for v in p['vertices']:
   for old,new in z_receiving.items():
    if abs(v[2]-old)<.02:v[2]+=new-old;break
 # Axis-aligned glass/handrails have +/-thickness around their center.
 if p.get('kind') is None and ('glass' in p['name'] or 'handrail' in p['name']):
  center=(p['lo'][2]+p['hi'][2])/2
  for old,new in z_receiving.items():
   if abs(center-old)<1e-6:
    p['lo'][2]+=new-old;p['hi'][2]+=new-old;break
pins={}
for path in ['Game/assets/models/AST-RTL-009.glb','Game/assets/models/AST-CIR-001.glb','Game/source_derivatives/group4_completion_20261011/AST-TRM-G4-020_foremid_north_candidate.glb','Game/data/spatial_layout.json','Game/tram_section_successor_20261024/section_plan_r002.json']:
 pins[path]=hashlib.sha256((R/path).read_bytes()).hexdigest()
contract=dict(schema='astraea.foremid_orchard_receiver.r003',selected=False,parts=parts,source_pins=pins,
 purpose='Upper public station gallery into existing D10 Orchard Exchange; partial physical connection, not scenic tram acceptance',
 original_sources_unchanged=True,deck_y=61,bridge_clear_width=4,stair_clear_width=2.4,stair_risers=28,stair_rise=4.9,
 retained_floor_seams=[[-4,61,-235.2],[4,61,-235.2]],
 holds=['Unselected authored candidate; no production changes','North approach original guard requires an exact fitted opening, not collision suppression','Existing lift requires third-stop shaft/cap successor and original identities preserved; closed hold remains','New piers/beam receivers need exact structural receiving and full neighbor fit','Stair support, headroom, handrails, real cart/guest envelopes and original egress require installed checks','Complete vehicle swept envelope below bridge remains untested','D10 gallery receiving edge and roof/room neighbors need exact installed checks','Car is not thereby moved inside grand room; track/scenic acceptance remains held','No 60FPS, engineering, capacity or Windows acceptance'])
data=(json.dumps(contract,indent=2)+'\n').encode();out=D/'RECEIVER_r003.json'
if out.exists():assert out.read_bytes()==data,'Refusing to overwrite different candidate'
else:out.write_bytes(data)
print(json.dumps({'parts':len(parts),'sha256':hashlib.sha256(data).hexdigest(),'selected':False}))
