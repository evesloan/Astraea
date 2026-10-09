from pathlib import Path
import json,math,hashlib,sys
sys.path.insert(0,'/workspace/shared/astraea_python_deps')
from shapely.geometry import Polygon,box,mapping
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
from shapely import constrained_delaunay_triangles
R=Path('/workspace/shared/Astraea_direct_recovery_20261008_hcozu5z4');O=R/'BlenderCatalogue/assets/star_atlas_upper_commons_20261009';(O/'source').mkdir(parents=True,exist_ok=True)
parts=[];floors=[];stairs=[]
def slab(name,poly,lo,hi,role='warm_stone',category='floor',collision=True):
 if poly.is_empty:return
 if poly.geom_type!='Polygon':
  for i,p in enumerate(poly.geoms):slab(name+'_'+str(i),p,lo,hi,role,category,collision)
  return
 poly=orient(poly,sign=1);vs=[];fs=[]
 for t in constrained_delaunay_triangles(poly).geoms:
  q=list(orient(t,sign=1).exterior.coords)[:3];k=len(vs);vs.extend([(x,lo,z)for x,z in q]+[(x,hi,z)for x,z in q]);fs.extend([(k,k+1,k+2),(k+5,k+4,k+3)])
 for ring in [poly.exterior,*poly.interiors]:
  for a,b in zip(ring.coords,list(ring.coords)[1:]):
   k=len(vs);vs.extend([(a[0],lo,a[1]),(a[0],hi,a[1]),(b[0],hi,b[1]),(b[0],lo,b[1])]);fs.append((k,k+1,k+2,k+3))
 parts.append({'name':name,'verts':vs,'faces':fs,'role':role,'category':category,'runtime_collision':collision})
def cube(name,a,b,role='warm_walnut',category='architecture',collision=True):slab(name,box(a[0],a[2],b[0],b[2]),a[1],b[1],role,category,collision)
def rail(name,a,b,y):
 dx,dz=b[0]-a[0],b[1]-a[1];n=math.hypot(dx,dz);ux,uz=-dz/n*.04,dx/n*.04
 poly=Polygon([(a[0]+ux,a[1]+uz),(b[0]+ux,b[1]+uz),(b[0]-ux,b[1]-uz),(a[0]-ux,a[1]-uz)])
 slab(name+'_Infill',poly,y+.08,y+1.08,'hospitality_glass','guard');slab(name+'_Cap',poly.buffer(.02,join_style=2),y+1.08,y+1.14,'champagne_metal','guard')
regions=[]
for p in ['Game/data/generated/structural_meshes.json','Game/data/generated/received_structural_meshes.json','Game/data/architecture/CENTRAL_RESIDENTIAL_STREETS.json']:regions+=json.load(open(R/p))['regions']
def existing(y):return unary_union([Polygon(t)for q in regions if abs(q['floor_y']-y)<.001 for t in q['triangles']])
room=box(-97,-14,-63,14);shaft=box(-72.2,4.2,-66.4,11.8)
voids={16:Polygon([(-89,-4),(-80,-4),(-77,-1),(-78,5),(-87,6),(-91,2)]),17:Polygon([(-86,-2),(-79,-2),(-76,1),(-79,6),(-86,5),(-89,2)])}
for deck,y in [(15,93),(16,97.5),(17,102)]:
 desired=room.union(box(-63,-3.2,-48,3.2))
 if deck>15:desired=desired.difference(shaft).difference(voids[deck])
 if deck==16:desired=desired.union(box(-86.05,-30.5,-81.95,-14)).union(box(-86.05,14,-81.95,28.5))
 add=desired.difference(existing(y));slab(f'SA_D{deck}_MissingOnlyFloor',add,y-.24,y);floors.append({'deck':deck,'floor_y':y,'desired_geometry':mapping(desired),'new_geometry':mapping(add),'new_area_m2':add.area})
 # Solid guest shell with framed west observation bays, and east public entry.
 cube(f'SA_D{deck}_WestSill',[-97,y,-14],[-96.75,y+.7,14]);cube(f'SA_D{deck}_WestHeader',[-97,y+3.5,-14],[-96.75,min(y+4.5,106.26),14])
 for j,z in enumerate([-12.5,-4.3,4.3,12.5]):cube(f'SA_D{deck}_WestPier_{j}',[-97,y+.7,z-.2],[-96.6,y+3.5,z+.2])
 for j,(a,b)in enumerate([(-12.3,-4.5),(-4.1,4.1),(4.5,12.3)]):cube(f'SA_D{deck}_WestGlass_{j}',[-96.94,y+.7,a],[-96.84,y+3.5,b],'hospitality_glass','window')
 for side,z in [('North',-14),('South',13.78)]:
  spans=[(-97,-86.05),(-81.95,-63)]if deck==16 else[(-97,-63)]
  for j,(a,b)in enumerate(spans):cube(f'SA_D{deck}_{side}Wall_{j}',[a,y,z],[b,min(y+4.5,106.26),z+.22],'ivory_enamel')
  if deck==16:cube(f'SA_D{deck}_{side}PortalHeader',[-86.05,y+3,z],[-81.95,y+4.5,z+.22],'warm_walnut')
 for j,(a,b)in enumerate([(-14,-3.2),(3.2,14)]):cube(f'SA_D{deck}_EastWall_{j}',[-63.22,y,a],[-63,y+4.5 if deck<17 else 106.26,b],'ivory_enamel')
 cube(f'SA_D{deck}_EastPortalHeader',[-63.4,y+3.3,-3.2],[-63,y+4.1,3.2])
 for z in [-3.18,3.18]:rail(f'SA_D{deck}_RingLinkGuard_{z}',(-63,z),(-54 if deck==16 else-51,z),y)
 if deck>15:
  ring=list(voids[deck].exterior.coords)
  for i,(a,b)in enumerate(zip(ring,ring[1:])):rail(f'SA_D{deck}_GalleryGuard_{i}',a,b,y)
  # Opening guards leave the upper-return landing clear at the south edge.
  for i,(a,b)in enumerate([((-72.2,4.2),(-72.2,11.8)),((-72.2,11.8),(-66.4,11.8)),((-66.4,11.8),(-66.4,4.2))]+([((-72.2,4.2),(-69.3,4.2))]if deck==17 else [])):rail(f'SA_D{deck}_StairWellGuard_{i}',a,b,y)
 if deck==16:
  for a,b in [(-30.5,-14),(14,28.5)]:
   for x in [-86.02,-81.98]:rail(f'SA_D16_HomeLink_{a}_{x}',(x,a),(x,b),y)
# Upper local stairs start on the unchanged D15 cover. No lower-library roof cut.
for deck,base in [(15,93),(16,97.5)]:
 for flight,(x0,x1,z0,z1,y0,y1)in enumerate([(-72,-69.6,4.2,8.88,base,base+2.25),(-69,-66.6,8.88,4.2,base+2.25,base+4.5)]):
  for i in range(13):
   a=z0+(z1-z0)*i/13;b=z0+(z1-z0)*(i+1)/13;top=y0+(y1-y0)*(i+1)/13
   cube(f'SA_D{deck}_StairVisual_{flight}_{i}',[x0,top-.15,min(a,b)],[x1,top,max(a,b)],'warm_stone','stair_visual',False)
  # Closed sloping underside/contact wedge, preserving all existing slab below.
  vs=[[x0,y0-.02,z0],[x1,y0-.02,z0],[x1,y0-.02,z1],[x0,y0-.02,z1],[x0,y0,z0],[x1,y0,z0],[x1,y1,z1],[x0,y1,z1]]
  parts.append({'name':f'SA_D{deck}_StairContact_{flight}','verts':vs,'faces':[f if z1>z0 else list(reversed(f))for f in [[0,1,2,3],[7,6,5,4],[0,4,5,1],[1,5,6,2],[2,6,7,3],[3,7,4,0]]],'role':'warm_stone','category':'stair_contact','runtime_collision':True})
  for edge,x in enumerate([x0,x1]):
   # Follow the incline with short guarded segments, no posts in walking width.
   for k in range(13):
    za=z0+(z1-z0)*k/13;zb=z0+(z1-z0)*(k+1)/13;yy=y0+(y1-y0)*(k+.5)/13
    rail(f'SA_D{deck}_FlightGuard_{flight}_{edge}_{k}',(x,za),(x,zb),yy)
 slab(f'SA_D{deck}_MidLanding',box(-72,8.88,-66.6,11.58),base+2.01,base+2.25)
 for edge,(a,b)in enumerate([((-72,8.88),(-72,11.58)),((-72,11.58),(-66.6,11.58)),((-66.6,11.58),(-66.6,8.88))]):rail(f'SA_D{deck}_MidLandingGuard_{edge}',a,b,base+2.25)
 stairs.append({'lower_deck':deck,'base_y':base,'mid_y':base+2.25,'upper_y':base+4.5,'flight_width':2.4,'tread_count_per_flight':13})
# Visible continuous receiving lines and framed enclosure stay in this programme.
for x in [-95.7,-74.5,-64.2]:
 for z in [-12.7,12.7]:cube(f'SA_Column_{x}_{z}',[x-.16,93,z-.16],[x+.16,106.26,z+.16],'champagne_metal')
 for y in [97.26,101.76,106.26]:cube(f'SA_LongBeam_{x}_{y}',[x-.18,y-.28,-12.7],[x+.18,y,12.7],'warm_walnut')
for y in [97.26,101.76,106.26]:
 for z in [-12.7,12.7]:cube(f'SA_CrossBeam_{z}_{y}',[-95.7,y-.28,z-.18],[-64.2,y,z+.18],'warm_walnut')
slab('SA_TopEnclosure',room,106.26,106.44,'ivory_enamel','ceiling')
# Built-in curved reading alcoves make the upper levels legible before detail polish.
for deck,y,cx,cz in [(15,93,-91,-8),(16,97.5,-91,9),(17,102,-91,-8)]:
 for i in range(8):
  a=math.pi*.2+math.pi*1.6*i/8;b=math.pi*.2+math.pi*1.6*(i+1)/8
  poly=Polygon([(cx+rr*math.cos(t),cz+rr*math.sin(t))for rr,t in[(2.5,a),(2.5,b),(2.85,b),(2.85,a)]])
  seat=Polygon([(cx+rr*math.cos(t),cz+rr*math.sin(t))for rr,t in[(2.1,a),(2.1,b),(2.85,b),(2.85,a)]])
  slab(f'SA_D{deck}_ReadingAlcove_{i}',seat,y,y+.5,'teal_weave','furniture')
  for h in [.85,1.55,2.25]:slab(f'SA_D{deck}_AlcoveShelf_{i}_{h}',poly,y+h,y+h+.1,'warm_walnut','furniture')
lights=[]
for deck,y in [(15,93),(16,97.5),(17,102)]:
 for i,(x,z)in enumerate([(-92,-8),(-92,8),(-76,-8),(-64.8,0)]):
  cube(f'SA_D{deck}_CeilingFixture_{i}',[x-.55,y+3.8,z-.25],[x+.55,y+3.88,z+.25],'opal_glow','fixture',False)
  lights.append({'name':f'SA_D{deck}_Light_{i}','position':[x,y+3.78,z],'range':8,'energy':1.1})
# Exact source pins preserve lower room, installed homes/streets and current crown.
paths=['Game/assets/models/AST-LIB-011.glb','Game/data/generated/structural_meshes.json','Game/data/architecture/CENTRAL_RESIDENTIAL_STREETS.json','Game/data/architecture/CENTRAL_CROWN_RUNTIME.json','Game/assets/models/D18_directory_05.glb']
pins={p:hashlib.sha256((R/p).read_bytes()).hexdigest()for p in paths}
plan={'schema':'astraea.star_atlas_upper_commons.v1','parts':parts,'floors':floors,'stairs':stairs,'lights':lights,'source_pins':pins,'programme_keys':['D15_directory_03','D16_directory_03','D17_directory_03'],'existing_lower_library_unchanged':True,'existing_D15_cover_reused':True,'existing_85_homes_unchanged':True,'new_guest_units':0,'status':'CONSTRUCTION_CANDIDATE','limits':'Final in-engine visual review, detailed traversal, furnishing/lighting/interaction passes and full residential service completion remain open.'}
(O/'PLAN.json').write_text(json.dumps(plan,indent=2)+'\n');print('STAR_UPPER_PLAN',len(parts),[(f['deck'],round(f['new_area_m2'],3))for f in floors])
