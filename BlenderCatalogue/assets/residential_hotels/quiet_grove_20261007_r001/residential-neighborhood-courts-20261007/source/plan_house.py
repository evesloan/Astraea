"""Actual principal court + paired-bank house, no adoption or new registry."""
from pathlib import Path
import sys,json,math,hashlib,collections
sys.path.insert(0,'/workspace/scratch/375c2e438292/geometry-deps')
from shapely.geometry import Polygon,box,Point,LineString
from shapely.ops import unary_union,triangulate
from shapely import constrained_delaunay_triangles
S=Path(__file__).resolve().parents[1];B=S.parent/'residential-batch-neighborhood-20261006';read=lambda p:json.loads(Path(p).read_text())
whole=read(S/'inputs/whole_ship_layout.json');lux=read(S/'inputs/D17_LUXURY_HOUSES_PROPOSAL.json');census=read(S.parent/'residential-production-schedule-20261006/ALL_1000_SOURCE_COLOR_CROSSWALK.json')['records'];cross={r['source_envelope_index']:r for r in census}
family=read(B/'scale_domestic_r011/assemblies/GODOT_BATCH_INSTANCE_MAP.json');house_id='starboard_forward_upper_house';reservation=next(r for r in whole['residential_court_reservations']if r['id']=='starboard_forward_residential_court');membership=next(r for r in whole['residential_houses']if r['id']==house_id);court=Polygon(reservation['boundary']);commons=box(63,-384,97,-356)
vip=[r for r in lux['replacements']if r['house']==house_id];cut=unary_union([Polygon(r['proposed_floor_boundary'])for r in vip]);parts=[];assets=[];lights=[];contacts=[];routes=[];spaces=[]
# Only completed authored room recipes are linked. No generic placeholder shell stands in for specialty/VIP interiors.
rooms=[r for r in family['instances']if r['house']==house_id];assert len(rooms)==83

def polygon_parts(poly):
 if poly.is_empty:return []
 return [poly]if poly.geom_type=='Polygon'else[g for g in poly.geoms if g.geom_type=='Polygon']
def slab(name,poly,bottom,top,role='warm_stone',category='floor',owner=None):
 for i,p in enumerate(polygon_parts(poly)):
  if p.area<.001:continue
  triangles=list(constrained_delaunay_triangles(p).geoms);assert abs(sum(t.area for t in triangles)-p.area)<.002,(name,p.area)
  verts=[];faces=[]
  for t in triangles:
   q=list(t.exterior.coords)[:3];k=len(verts);verts.extend([(x,bottom,z)for x,z in q]+[(x,top,z)for x,z in q]);faces.extend([(k+2,k+1,k),(k+3,k+4,k+5)])
  for ring in [p.exterior,*p.interiors]:
   for a,b in zip(ring.coords,list(ring.coords)[1:]):
    k=len(verts);verts.extend([(a[0],bottom,a[1]),(b[0],bottom,b[1]),(b[0],top,b[1]),(a[0],top,a[1])]);faces.append((k,k+1,k+2,k+3))
  parts.append({'name':name+'_'+str(i),'kind':'mesh','verts':verts,'faces':faces,'role':role,'category':category,'owner':owner or name,'plan_area_m2':p.area})
def beam(name,a,b,width=.25,depth=.3,role='warm_walnut',category='support'):parts.append({'name':name,'kind':'beam','a':a,'b':b,'width':width,'depth':depth,'role':role,'category':category})
def block(name,x0,x1,y0,y1,z0,z1,role='ivory_enamel',category='architecture'):slab(name,box(x0,z0,x1,z1),y0,y1,role,category)
def railing(name,poly,y):
 name0=name
 for component_index,p in enumerate(polygon_parts(poly)):
  name=name0+"__part"+str(component_index)
  for ri,ring in enumerate([p.exterior,*p.interiors]):
   for i,(a,b)in enumerate(zip(ring.coords,list(ring.coords)[1:])):
    # Crossings into the commons have a true open edge; do not rail through access.
    mid=Point((a[0]+b[0])/2,(a[1]+b[1])/2)
    if commons.buffer(.02).contains(mid) or box(3.8,-374.02,63.02,-365.98).contains(mid):continue
    beam(f'{name}_top_{ri}_{i}',[a[0],y+1.1,a[1]],[b[0],y+1.1,b[1]],.065,.08,'champagne_metal','guard')
    beam(f'{name}_low_{ri}_{i}',[a[0],y+.18,a[1]],[b[0],y+.18,b[1]],.06,.08,'warm_walnut','guard')
    length=math.dist(a,b);n=max(1,math.ceil(length/1.1))
    for j in range(n+1):
     u=j/n;x=a[0]+(b[0]-a[0])*u;z=a[1]+(b[1]-a[1])*u;beam(f'{name}_post_{ri}_{i}_{j}',[x,y,z],[x,y+1.1,z],.045,.045,'champagne_metal','guard')
    # Restrained transparent public infill, distinct from opaque residential privacy panes.
    n=max(1,math.ceil(length/2.0))
    for j in range(n):
     u=(j+.03)/n;v=(j+.97)/n;aa=(a[0]+(b[0]-a[0])*u,a[1]+(b[1]-a[1])*u);bb=(a[0]+(b[0]-a[0])*v,a[1]+(b[1]-a[1])*v)
     beam(f'{name}_glass_{ri}_{i}_{j}',[aa[0],y+.62,aa[1]],[bb[0],y+.62,bb[1]],.015,.85,'glass','public_glass')
def asset(aid,name,p,yaw=0,scale=1,purpose=''):
 assets.append({'catalogue_id':aid,'name':name,'world_xyz':p,'yaw':yaw,'scale':scale,'purpose':purpose})
def fixture(name,p,target,power=300,size=2):
 block(name+'_body',p[0]-.25,p[0]+.25,p[1]-.09,p[1]+.10,p[2]-.25,p[2]+.25,'champagne_metal','fixture')
 block(name+'_lens',p[0]-.20,p[0]+.20,p[1]-.115,p[1]-.09,p[2]-.20,p[2]+.20,'lens','fixture')
 lights.append({'name':name,'world_xyz':[p[0],p[1]-.14,p[2]],'target':target,'energy':power,'size':size,'runtime_budget':'Reuse current source selector; no new global light budget'})
# Ground garden, commons/lobby island and quiet private window verge all have real geometry.
slab('QuietGrove_CourtBase',court.difference(commons),83.76,84,'warm_stone')
slab('QuietGrove_D13Commons',commons,83.76,84,'warm_stone')
private_verge=box(58.95,-482.2,63,-250).difference(commons)
slab('PrivateGardenVerge',private_verge.difference(box(4,-374,63,-366)),83.76,84,'warm_stone')
# Full inward garden is distinct from the principal reservation and excludes staff risers.
inner=box(8.2,-482.2,29.05,-250)
risers=unary_union([box(*[r['lobby_x'][0],r['lobby_z'][0],r['lobby_x'][1],r['lobby_z'][1]])for r in whole['staff_riser_reservations']if r['center_xz'][0]>0])
inner=inner.difference(risers.buffer(.15))
slab('InnerQuietGardenBase',inner.difference(box(4,-374,63,-366)),83.76,84,'warm_stone')
# Five real arrivals, courts and commons; four paired-bank ordinary streets.
well=box(81.5,-381.8,87.8,-375.4)
for level,y in enumerate([84,88.5,93,97.5,102]):
 label='D'+str(13+level)
 crosslink=box(4,-374,63,-366)
 slab(label+'_CrossShipArrival',crosslink,y-.24,y,'warm_stone')
 if level<4:
  street=box(41.95,-482.2,46.05,-250).difference(crosslink)
  slab(label+'_PairedDoorStreet',street,y-.24,y,'warm_stone')
  routes.append({'id':label+'_street','points':[[44,y,-480],[44,y,-370],[44,y,-252]],'clear_width_m':4.1,'status':'source geometry; actual door entries remain at42/46'})
 if level:
  ring=court.difference(court.buffer(-4.4,join_style=2)).intersection(box(67.6,-501,101,-249))
  # Different inhabited stopping forms, not five identical balconies.
  centers=[None,(-452,6.5,10),(-309,7.5,13),(-427,10,11),(-334,7,9)]
  z,rx,rz=centers[level];pocket=Point(95,z).buffer(1,resolution=10)
  from shapely.affinity import scale
  pocket=scale(pocket,rx,rz).intersection(court)
  gallery=unary_union([ring,pocket]).difference(commons)
  floorcommons=commons.difference(well)
  if level==4:
   free=court.difference(cut.buffer(2.0,join_style=2))
   upper_detour=free.difference(free.buffer(-4.4,join_style=2)).intersection(box(67.6,-501,101,-249))
   gallery=unary_union([upper_detour,pocket.intersection(free)]).difference(commons)
   floorcommons=floorcommons.difference(cut.buffer(.10))
  slab(label+'_OuterGardenGallery',gallery,y-.28,y,'warm_stone');railing(label+'_GalleryRail',gallery,y)
  slab(label+'_CommonsIsland',floorcommons,y-.28,y,'warm_stone')
  rim=LineString(commons.exterior.coords).difference(unary_union([gallery,crosslink]).buffer(.025))
  rim_segments=[rim]if rim.geom_type=='LineString'else list(getattr(rim,'geoms',[]))
  for ri,segment in enumerate(rim_segments):
   points=list(segment.coords)
   for j,(a,b)in enumerate(zip(points,points[1:])):
    beam(f'{label}_CommonsRim_{ri}_{j}',[a[0],y+1.1,a[1]],[b[0],y+1.1,b[1]],.065,.08,'champagne_metal','guard')
    n=max(1,math.ceil(math.dist(a,b)/.6))
    for k in range(n+1):
     x=a[0]+(b[0]-a[0])*k/n;z=a[1]+(b[1]-a[1])*k/n;beam(f'{label}_CommonsPost_{ri}_{j}_{k}',[x,y,z],[x,y+1.1,z],.04,.04,'warm_walnut','guard')

  # Opposite inner-bank destinations remain separated from private panes by real garden depth.
  ingallery=inner.intersection(box(8.2,-483,12.4,-249)).difference(crosslink)
  slab(label+'_InnerReadingGallery',ingallery,y-.28,y,'warm_stone');railing(label+'_InnerGuard',ingallery,y)
  # Purposeful seating in the shaped stopping bay, outside the continuous4m route.
  for k in range(3):asset('AST-FUR-002',label+'_QuietReading_'+str(k),[92.5,y,z-3+k*3],90,1,'Quiet reading faces the long planted court')
  for k in [-1,1]:asset('AST-FUR-003',label+'_SharedTable_'+str(k),[91,y,z+k*2],0,1,'Shared table in an actual stopping bay')
 # Lobby differs by level/use, with rounded canopy and readable timber threshold.
 use=['arrival_and_reception','shared_reading','sheltered_habitat_common','family_shared_table','upper_private_lounge'][level]
 spaces.append({'id':label+'_QuietGroveCommons','programme_key':reservation['affected_programmes'][level],'use':use,'floor_y':y,'status':'New completion composition inside existing commons allocation, not new capacity'})
 block(label+'_WelcomeDesk',67,70,y,y+.98,-379,-377,'warm_walnut','furniture')
 for i,z in enumerate([-380,-359]):
  for x in [72,76]:asset('AST-FUR-002',label+'_LobbySeat_'+str(i)+'_'+str(x),[x,y,z],0 if i==0 else 180,1,'Distinct lobby stopping group')
  asset('AST-FUR-003',label+'_LobbyTable_'+str(i),[74,y,z],0)
 # Curved ceiling transitions preserve the authoredroom language, never a white slab masquerading as walls.
 ceiling=min(y+3.40,106.05)
 canopy=box(65,-380.7,79,-376).buffer(.55,join_style=1).intersection(commons)
 slab(label+'_TimberArrivalCanopy',canopy,ceiling-.16,ceiling,'warm_walnut','ceiling')
 slab(label+'_AcousticCanopyInset',canopy.buffer(-.22),ceiling-.20,ceiling-.16,'oatmeal_weave','ceiling')
 for x in [67.5,73.5,77.0]:fixture(label+'_LobbySource_'+str(x),[x,ceiling-.24,-378.2],[x,y,-378.2],220,2)
 routes.append({'id':label+'_MainArrival','points':[[3.8,y,-370],[44,y,-370],[65,y,-370],[95,y,-370]],'clear_width_m':8,'core_walls_breached':False})
# Arrival edge guards stop falls without sealing the inner gallery/street joins.
for level,y in enumerate([84,88.5,93,97.5,102]):
 for z in [-374,-366]:
  for a,b in [(4.05,8.2),(12.4,41.95),(46.05,62.95)]:
   beam(f'ArrivalRail_{level}_{z}_{a}',[a,y+1.1,z],[b,y+1.1,z],.065,.08,'champagne_metal','guard')
   n=max(1,math.ceil((b-a)/.65))
   for j in range(n+1):
    x=a+(b-a)*j/n;beam(f'ArrivalPost_{level}_{z}_{a}_{j}',[x,y,z],[x,y+1.1,z],.035,.035,'warm_walnut','guard')
# Street edges use actual generated room frontages, never unbuilt allocation rectangles as guard substitutes.
for level,y in enumerate([84,88.5,93,97.5]):
 deck='D'+str(13+level)
 for x in [41.95,46.05]:
  line=LineString([(x,-482.2),(x,-250)])
  built_fronts=[]
  for room in rooms:
   if room['deck']!=deck:continue
   if min(abs(x-a)for a in room['allocation_x'])<.001:
    built_fronts.append(box(x-.1,room['allocation_z'][0],x+.1,room['allocation_z'][1]))
  exposed=line.difference(unary_union(built_fronts+[box(4,-374.01,63,-365.99)]))
  segments=[exposed]if exposed.geom_type=='LineString'else list(getattr(exposed,'geoms',[]))
  for j,segment in enumerate(segments):
   if segment.length<.02:continue
   a,b=list(segment.coords)[0],list(segment.coords)[-1]
   beam(f'StreetExposedRail_{deck}_{x}_{j}',[x,y+1.1,a[1]],[x,y+1.1,b[1]],.065,.08,'champagne_metal','guard')
   n=max(1,math.ceil(segment.length/.6))
   for k in range(n+1):
    z=a[1]+(b[1]-a[1])*k/n;beam(f'StreetExposedPost_{deck}_{x}_{j}_{k}',[x,y,z],[x,y+1.1,z],.04,.04,'warm_walnut','guard')
# Literal four-storey stair: two flights/landing, holes in new upper commons only.
for level,y in enumerate([84,88.5,93,97.5]):
 for flight in range(2):
  x0=81.8+flight*3.0;z0=-381.8 if flight==0 else -377.64;direction=1 if flight==0 else-1
  for step in range(13):
   za=z0+direction*step*.32;zb=z0+direction*(step+1)*.32;top=y+(flight*13+step+1)*(4.5/26)
   block(f'Stair_{level}_{flight}_{step}',x0,x0+2.5,top-.19,top,min(za,zb),max(za,zb),'warm_stone','stair')
  for x in [x0+.07,x0+2.43]:beam(f'StairRail_{level}_{flight}_{x}',[x,y+flight*2.25+1.10,z0],[x,y+(flight+1)*2.25+1.10,z0+direction*4.16],.07,.07,'champagne_metal','guard')
 slab('StairMid_'+str(level),box(81.8,-377.64,87.3,-375.84),y+2.25-.24,y+2.25,'warm_stone')
 contacts.append({'stair':level,'upper_landing_owner':'D'+str(14+level)+'_CommonsIsland','upper_receiving_region':[[84.8,-383.8],[87.3,-383.8],[87.3,-381.8],[84.8,-381.8]],'note':'Existing new commons owns this landing; no overlapping duplicate slab'})
 for flight in range(2):
  x0=81.8+flight*3;z0=-381.8 if flight==0 else -377.64;direction=1 if flight==0 else -1
  for x in [x0+.15,x0+2.35]:beam(f'StairStringer_{level}_{flight}_{x}',[x,y+flight*2.25-.08,z0],[x,y+(flight+1)*2.25-.22,z0+direction*4.16],.18,.32,'warm_walnut')
 for flight in range(2):
  x0=81.8+flight*3;z0=-381.8 if flight==0 else -377.64;direction=1 if flight==0 else -1
  for x in [x0+.07,x0+2.43]:
   for k in range(14):
    z=z0+direction*k*.32;foot=y+flight*2.25+k*(2.25/13);beam(f'StairBaluster_{level}_{flight}_{x}_{k}',[x,foot,z],[x,foot+1.1,z],.035,.035,'champagne_metal','guard')
 for x in [81.98,87.12]:block(f'StairLandingPier_{level}_{x}',x-.14,x+.14,y,y+2.01,-376.82,-376.54,'champagne_metal','support')
 for a,b in [((81.5,-381.8),(81.5,-375.4)),((81.5,-375.4),(87.8,-375.4)),((87.8,-375.4),(87.8,-381.8))]:
  for yedge in [y+4.5]:
   beam(f'WellRail_{level}_{a}',[a[0],yedge+1.1,a[1]],[b[0],yedge+1.1,b[1]],.07,.08,'champagne_metal','guard')
   n=math.ceil(math.dist(a,b)/.65)
   for k in range(n+1):
    x=a[0]+(b[0]-a[0])*k/n;z=a[1]+(b[1]-a[1])*k/n;beam(f'WellPost_{level}_{a}_{k}',[x,yedge,z],[x,yedge+1.1,z],.035,.035,'warm_walnut','guard')
# Base transfer family takes bearing on real spine only outside all closed core spans.
station_z=[-480,-459,-406,-386,-350,-334,-310,-289,-250.5]
for i,z in enumerate(station_z):
 if z in [-459,-406]:
  contacts.append({'station_z':z,'status':'BLOCKED_PENDING_VERIFIED_WP06_LONG_LIBRARY_ENVELOPE','built_source_members':False,'reason':'Prior low diagonal/webs intruded D12 Long Library. No thin substitute or final support claim.'});continue
 edge=court.intersection(box(0,z-.1,110,z+.1));xmax=edge.bounds[2]if not edge.is_empty else 63
 block('SpineReceiver_'+str(i),3.70,4.30,78,78.22,z-.38,z+.38,'champagne_metal','receiver')
 beam('FullHouseTransferTop_'+str(i),[4.10,83.5,z],[xmax-.25,83.5,z],.45,.52,'ivory_enamel')
 beam('FullHouseTransferDiagonal_'+str(i),[4.10,78.24,z],[xmax-.25,83.5,z],.42,.42,'warm_walnut')
 for x in [15,30,45,60,75,90]:
  if x>=xmax:continue
  low=78.24+(x-4.1)/(xmax-.25-4.1)*(83.5-78.24)
  beam(f'TransferWeb_{i}_{x}',[x,low,z],[x,83.5,z],.24,.24,'champagne_metal')
 contacts.append({'receiver':'SpineReceiver_'+str(i),'existing_owner':'D12_fore_route','point':[3.85,78,z],'status':'Proposed geometric bearing only; exact collider/source fit and capacity remain review gates'})
# Longitudinal beams and branching piers connect the floor/terrace structure.
for x in [8.5,12.1,28.75,42.2,45.8,59.2,63.4,95.8]:
 allowed=inner if x<29.05 else (court if x>=63 else box(29.05,-482.2,63,-250))
 line=LineString([(x,-480),(x,-250.5)]).intersection(allowed.buffer(-.35))
 if 8<=x<=54:line=line.difference(box(7.8,-466.2,54.2,-397.8))
 lines=[line]if line.geom_type=='LineString'else list(getattr(line,'geoms',[]))
 for j,segment in enumerate(lines):
  if segment.length<.5:continue
  a,b=list(segment.coords)[0],list(segment.coords)[-1];beam('BaseLongitudinal_'+str(x)+'_'+str(j),[a[0],83.42,a[1]],[b[0],83.42,b[1]],.34,.68,'warm_walnut')
for i,z in enumerate(range(-474,-250,28)):
 section=court.intersection(box(0,z-.1,110,z+.1));outer=section.bounds[2]if not section.is_empty else 63
 for x in [63.45,outer-.48]:
  if cut.buffer(.15).intersects(box(x-.24,z-.24,x+.24,z+.24)):top=101.70
  else:top=105.92
  block(f'CourtPier_{i}_{x}',x-.24,x+.24,84,top,z-.24,z+.24,'warm_walnut','pier')
  for y in [88.22,92.72,97.22,101.72]:
   if y+0.5<top:block(f'PierCapital_{i}_{x}_{y}',x-.45,x+.45,y-.14,y+.26,z-.48,z+.48,'ivory_enamel','transition')
# Inner gallery columns and actual mounted lights carry the quieter counterpart.
for i,z in enumerate([-474,-446,-418,-390,-350,-322,-294,-264]):
 for x in [8.55,12.1]:
  block(f'InnerGalleryPier_{i}_{x}',x-.18,x+.18,84,106.02,z-.18,z+.18,'warm_walnut','pier')
 for level,y in enumerate([88.5,93,97.5,102]):
  beam(f'InnerGalleryBeam_{i}_{level}',[8.35,y-.43,z],[12.38,y-.43,z],.30,.30,'warm_walnut','support')
  fixture(f'InnerGallerySource_{i}_{level}',[10.2,y+2.90,z],[10.2,y,z],180,1.8)
  top=106.02 if level==3 else y+4.22
  beam(f'InnerGalleryLightMount_{i}_{level}',[10.2,y+2.98,z],[10.2,top,z],.07,.07,'champagne_metal','fixture_mount')
for level,y in enumerate([84,88.5,93,97.5]):
 for z in [-482.2,-250]:
  beam(f'StreetTerminalGuard_{level}_{z}',[41.95,y+1.1,z],[46.05,y+1.1,z],.065,.08,'champagne_metal','guard')
  for j in range(8):
   x=41.95+4.1*j/7;beam(f'StreetTerminalPost_{level}_{z}_{j}',[x,y,z],[x,y+1.1,z],.04,.04,'warm_walnut','guard')
# Real canopy/grove islands. Different sizes maintain long views and useful paths.
for i,z in enumerate([-473,-446,-418,-326,-300,-273]):
 center=82 if z>-449 else 72.5
 p=Point(center,z).buffer(1,resolution=12)
 from shapely.affinity import scale
 bed=scale(p,6.3 if i%2==0 else 7.8,8.8).intersection(court.buffer(-5)).difference(commons)
 if bed.area<8:continue
 slab('GroveBed_'+str(i),bed,84,84.42,'ivory_enamel','planter');slab('GroveSoil_'+str(i),bed.buffer(-.18),84.35,84.38,'botanical_soil','soil')
 c=bed.centroid;asset('AST-BOT-011','QuietCanopy_'+str(i),[c.x,84.38,c.y],i*67,.84 if i%2==0 else .68,'Fullheight rooted grove; no backdrop image')
 for n in range(24):
  a=n*2.39996;r=math.sqrt((n+.5)/24);x=c.x+5*r*math.cos(a);zz=c.y+7*r*math.sin(a)
  if bed.buffer(-.5).contains(Point(x,zz)):asset(['AST-BOT-002','AST-BOT-003','AST-BOT-009'][n%3],f'Understory_{i}_{n}',[x,84.38,zz],n*49,.85+(.15*(n%3)),'Layered planting wholly within actual bed')
# Inner quiet gardens serve the inward-facing bank; separate from principal court frontage counts.
for i,z in enumerate([-468,-423,-318,-272]):
 p=Point(20,z).buffer(4.6,resolution=12).intersection(inner.buffer(-2))
 if p.area<8:continue
 slab('InnerGroveBed_'+str(i),p,84,84.40,'ivory_enamel','planter');slab('InnerSoil_'+str(i),p.buffer(-.2),84.30,84.35,'botanical_soil','soil')
 c=p.centroid;asset('AST-BOT-011','InnerCanopy_'+str(i),[c.x,84.35,c.y],i*103,.58,'Small protected inner-bank outlook grove')
for level,y in enumerate([88.5,93,97.5,102]):
 for i,z in enumerate([-465,-436,-408,-324,-296,-264]):
  section=court.intersection(box(0,z-.1,110,z+.1));outer=section.bounds[2]if not section.is_empty else 63
  x=outer-4.7
  if x<68 or cut.buffer(1).contains(Point(x,z))and level==3:continue
  block(f'GalleryPlant_{level}_{i}',x-.5,x+.5,y,y+.46,z-1.2,z+1.2,'ivory_enamel','planter')
  for j in [-.65,.65]:asset('AST-BOT-008',f'Trailing_{level}_{i}_{j}',[x,y+.43,z+j],180,.85,'Upper layered greenery at gallery edges')
  fixture(f'GalleryLight_{level}_{i}',[outer-1.8,y+2.90,z],[outer-2.2,y,z],240,2.2)
  if level==3:
   beam(f'GalleryLightCeilingDrop_{level}_{i}',[outer-1.8,y+2.98,z],[outer-1.8,106.04,z],.07,.07,'champagne_metal','fixture_mount')
  else:
   beam(f'GalleryLightWallArm_{level}_{i}',[outer-.06,y+3.04,z],[outer-1.8,y+3.04,z],.09,.09,'warm_walnut','fixture_mount')
   beam(f'GalleryLightDrop_{level}_{i}',[outer-1.8,y+3.04,z],[outer-1.8,y+2.98,z],.07,.07,'champagne_metal','fixture_mount')
# Explicit opaque ceiling, clipped away from proposed VIP upper volumes. No fake space glass.
slab('InnerGardenOpaqueCover',inner,106.02,106.26,'ivory_enamel','ceiling')
roof=court.difference(cut.buffer(.20));slab('PrincipalCourtOpaqueCover',roof,106.02,106.26,'ivory_enamel','ceiling')
for i,z in enumerate(range(-473,-260,26)):
 section=roof.intersection(box(0,z-.45,110,z+.45))
 if section.is_empty:continue
 x0,_,x1,_=section.bounds
 # Segmented arched ribs preserve the demonstrated ceiling curve vocabulary.
 points=[[x0+(x1-x0)*j/8,104.90+1.03*math.sin(math.pi*j/8),z]for j in range(9)]
 for j,(a,b)in enumerate(zip(points,points[1:])):
  if LineString([(a[0],a[2]),(b[0],b[2])]).buffer(.22).intersects(cut):continue
  beam(f'CeilingArch_{i}_{j}',a,b,.28,.24,'warm_walnut','ceiling_rib')
 x=(x0+x1)/2
 fixture('CourtCanopyLight_'+str(i),[x,105.70,z],[x,84,z],1700,8)
 beam('CourtCanopyLightMount_'+str(i),[x,105.78,z],[x,106.04,z],.14,.14,'champagne_metal','fixture_mount')
# Outer public boundary is a real five-storey enclosure; the west suite-facing edge stays open to the planted verge.
for k,(a,b)in enumerate(zip(list(court.exterior.coords),list(court.exterior.coords)[1:])):
 if abs(a[0]-63)<.01 and abs(b[0]-63)<.01:continue
 edge=LineString([a,b]);n=max(1,math.ceil(edge.length/6))
 for j in range(n):
  u=(j+.004)/n;v=(j+.996)/n;aa=edge.interpolate(u,normalized=True);bb=edge.interpolate(v,normalized=True)
  for level,y in enumerate([84,88.5,93,97.5,102]):
   if level==4 and LineString([(aa.x,aa.y),(bb.x,bb.y)]).buffer(.12).intersects(cut):continue
   beam(f'OuterEnclosure_{k}_{j}_{level}',[aa.x,y+2.1,aa.y],[bb.x,y+2.1,bb.y],.16,4.2,'ivory_enamel','enclosure')
   beam(f'OuterEnclosureTimber_{k}_{j}_{level}',[aa.x,y+3.4,aa.y],[bb.x,y+3.4,bb.y],.21,.22,'warm_walnut','transition')
# No residential capacity is created by public furniture or use markers.
plan={'status':'FULL_147_UNIT_HOUSE_SOURCE_CONSTRUCTION; not adopted or finished','house_id':house_id,'proposed_theme':'Quiet Grove; completion proposal, not a recovered branded hotel name','source_house_membership':membership,'principal_court_reservation':reservation,'historical_house_units':147,'historical_direct_outward_candidates':76,'inward_bank_units':71,'modeled_regular_family_interiors':83,'specialty_vip_units_reserved':64,'upper_datums':[84,88.5,93,97.5,102],'cover_y':106.5,'parts':parts,'asset_instances':assets,'lights':lights,'routes':routes,'contacts':contacts,'commons':spaces,'rooms':rooms,'room_prototypes':family['prototypes'],'D17_replacement_reservations':vip,'D17_court_subtraction_area_m2':court.intersection(cut).area,'temporary_unbuilt_specialty_frontage_guards':[{'source_index':r['source_envelope_index'],'door_xz':r['historical_door_marker_xz'],'entry_status':'Unavailable until specialty floor/shell/environmental interface is authored; current safety rail is temporary'}for r in census if r['house']==house_id and r['deck']in['D13','D14','D15','D16']and r['historical_class']=='specialty_unsplit'],'receiving_interface_blocks':[{'owner':'D12 Long Library/WP06','conservative_volume':{'x':[8,54],'z':[-466,-398],'y':[78,84]},'status':'Exact source intake unverified; interfering transfer rows and longitudinal spans omitted. No final support/load claim.'}],'limits':['All source-only; exact receiving/contact/route checks remain','No old floor or void cut; no Game/Catalogue change','No invented specialty habitat anatomy or scaled-standard luxury rooms','No standalone three-room adoption','Principal court historical frontal count is not current luxury-facing acceptance']}
(S/'SF_FULL_HOUSE_PLAN.json').write_text(json.dumps(plan,indent=2)+'\n')
print('FULL_HOUSE_PLAN',len(parts),'architectural parts',len(assets),'asset instances',len(rooms),'real source rooms','VIPcourt area',plan['D17_court_subtraction_area_m2'])
