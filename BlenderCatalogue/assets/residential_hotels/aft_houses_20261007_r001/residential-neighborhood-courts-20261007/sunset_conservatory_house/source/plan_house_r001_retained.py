"""Sunset whole-house construction, actual aft court and explicit support holds."""
from pathlib import Path
import json,sys,math,hashlib,collections
W=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(W/'geometry-deps'))
from shapely.geometry import Polygon,box,Point,LineString,mapping
from shapely.affinity import scale,rotate
from shapely.ops import unary_union
from shapely import constrained_delaunay_triangles
R=Path(__file__).resolve().parents[1];S=R.parent;G=Path('/workspace/shared/astraea-godot-production-20261003')
read=lambda p:json.loads(Path(p).read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
w=read(G/'data/whole_ship_layout.json');lux=read(G/'data/architecture/D17_LUXURY_HOUSES_PROPOSAL.json');census=read(W/'residential-neighborhood-audit-20261007/ALL_1000_NEIGHBORHOOD_CROSSWALK.json')['records'];roommap=read(R/'SUNSET_83_PLACEMENT_MAP.json')
house='port_aft_upper_house';reservation=next(r for r in w['residential_court_reservations']if r['id']=='port_aft_residential_court');membership=next(r for r in w['residential_houses']if r['id']==house);court=Polygon(reservation['boundary']);commons=box(-97,356,-63,384)
vip=[r for r in lux['replacements']if r['house']==house];vipcut=unary_union([Polygon(r['proposed_floor_boundary'])for r in vip]);rooms=roommap['units'];parts=[];assets=[];lights=[];contacts=[];routes=[];spaces=[];floor_regions=[];owned={};Y=[84,88.5,93,97.5,102]
compiled=read(G/'data/generated/structural_meshes.json')['regions'];existing={y:unary_union([Polygon(t)for r in compiled if r['floor_y']==y for t in r['triangles']])for y in Y}
# Reuse only neutral polygon/rail/beam construction primitives from the proven
# source workflow. All spatial composition below is new to the aft house.
def polys(p):return []if p.is_empty else[p]if p.geom_type=='Polygon'else[g for g in p.geoms if g.geom_type=='Polygon']

def slab(name,p,lo,hi,role='warm_stone',category='floor',owner=None):
 for i,q in enumerate(polys(p)):
  if q.area<.001:continue
  tris=list(constrained_delaunay_triangles(q).geoms);assert abs(sum(t.area for t in tris)-q.area)<.002;verts=[];faces=[]
  for t in tris:
   p3=list(t.exterior.coords)[:3];k=len(verts);verts.extend([(x,lo,z)for x,z in p3]+[(x,hi,z)for x,z in p3]);faces.extend([(k+2,k+1,k),(k+3,k+4,k+5)])
  for ring in[q.exterior,*q.interiors]:
   for a,b in zip(ring.coords,list(ring.coords)[1:]):
    k=len(verts);verts.extend([(a[0],lo,a[1]),(b[0],lo,b[1]),(b[0],hi,b[1]),(a[0],hi,a[1])]);faces.append((k,k+1,k+2,k+3))
  parts.append({'name':f'{name}_{i}','kind':'mesh','verts':verts,'faces':faces,'role':role,'category':category,'owner':owner or name,'plan_area_m2':q.area})

def floor(name,p,y,role='warm_stone'):
 p=p.difference(existing.get(y,Polygon())).difference(owned.get(y,Polygon()))
 if y>=102:p=p.difference(vipcut.buffer(.15))
 owned[y]=unary_union([owned.get(y,Polygon()),p]);slab(name,p,y-.24,y,role,'floor');floor_regions.append({'name':name,'floor_y':y,'geometry':mapping(p)})

def beam(name,a,b,width=.2,depth=.25,role='warm_walnut',category='support'):parts.append({'name':name,'kind':'beam','a':a,'b':b,'width':width,'depth':depth,'role':role,'category':category})

def block(name,x0,x1,y0,y1,z0,z1,role='ivory_enamel',category='architecture'):slab(name,box(x0,z0,x1,z1),y0,y1,role,category)

def asset(aid,name,point,yaw=0,scalev=1,purpose=''):assets.append({'catalogue_id':aid,'name':name,'world_xyz':point,'yaw':yaw,'scale':scalev,'purpose':purpose})

def ellipse(x,z,rx,rz):return scale(Point(x,z).buffer(1,quad_segs=12),rx,rz)

def lines(q):return[q]if q.geom_type=='LineString'else[v for v in getattr(q,'geoms',[])if v.geom_type=='LineString']

def guard(name,line,y):
 for j,seg in enumerate(lines(line)):
  for k,(a,b)in enumerate(zip(list(seg.coords),list(seg.coords)[1:])):
   if math.dist(a,b)<.03:continue
   n=max(1,math.ceil(math.dist(a,b)/.8))
   beam(f'{name}_rail_{j}_{k}',[a[0],y+1.10,a[1]],[b[0],y+1.10,b[1]],.065,.08,'champagne_metal','guard')
   for t in range(n+1):
    x=a[0]+(b[0]-a[0])*t/n;z=a[1]+(b[1]-a[1])*t/n;beam(f'{name}_post_{j}_{k}_{t}',[x,y,z],[x,y+1.10,z],.04,.04,'champagne_metal','guard')
   beam(f'{name}_infill_{j}_{k}',[a[0],y+.56,a[1]],[b[0],y+.56,b[1]],.018,.90,'glass','public_glass')

def fixture(name,x,y,z,mount_y,power=180):
 block(name+'_body',x-.22,x+.22,y-.03,y+.13,z-.22,z+.22,'champagne_metal','fixture')
 block(name+'_lens',x-.18,x+.18,y-.06,y-.03,z-.18,z+.18,'lens','fixture')
 beam(name+'_mount',[x,y+.12,z],[x,mount_y,z],.08,.08,'champagne_metal','fixture_mount')
 lights.append({'name':name,'world_xyz':[x,y-.07,z],'target':[x,y-2.8,z],'energy':power,'size':1.7,'mount_contact_world_xyz':[x,mount_y,z],'runtime_budget':'source only; no global light budget change'})
crosslink=box(-97,366,-4,374);street=box(-46.05,257.8,-41.95,482.2)
risers=unary_union([box(r['lobby_x'][0],r['lobby_z'][0],r['lobby_x'][1],r['lobby_z'][1])for r in w['staff_riser_reservations']if r['center_xz'][0]<0 and r['center_xz'][1]>0])
inner=box(-29.05,250,-8.2,483).difference(risers.buffer(.20));verge=box(-63,257.8,-58.95,482.2)
# D13 is a continuous planted conservatory base. Upper levels are shaped
# outlooks, never repeated rings or a hidden slab under a claimed open court.
well=box(-81.5,375.5,-75.3,381.9);lift=box(-71.8,377.1,-67.2,382.3)
floor('SC_ConservatoryBase',court,84);floor('SC_PrivateViewVerge',verge,84);floor('SC_InnerGardenBase',inner,84)
outerpath=LineString([(-95.4,260),(-95.4,420),(-68.0,470.3)])
for level,y in enumerate(Y):
 label='D'+str(13+level)
 floor(label+'_SunsetArrivalCrosslink',crosslink,y)
 if level<4:floor(label+'_HistoricalPairedBankStreet',street,y)
 else:
  floor(label+'_DeluxeQuietApproachNorth',box(-37,275,-32.5,356),y)
  floor(label+'_DeluxeQuietApproachSouth',box(-37,384,-32.5,455),y)
  floor(label+'_DeluxeQuietApproachMiddle',box(-37,356,-32.5,384),y)
 if level:
  # Different lengths and directions reveal the taper and neighboring landings.
  za,zb=[None,(285,370),(370,459),(308,411),(328,399)][level]
  prom=outerpath.intersection(box(-120,za,-55,zb)).buffer(2.2,cap_style=2,join_style=2).intersection(court.buffer(-.25))
  fan_z=[None,324,421,344,391][level];fan_x=-88 if fan_z<420 else-86
  fan=rotate(ellipse(fan_x,fan_z,8.7,12.0),-14 if level%2 else 18,origin=(fan_x,fan_z))
  landing=unary_union([box(-95.4,356,-63,384),prom,fan]).intersection(court.buffer(-.15)).difference(well).difference(lift)
  floor(label+'_AsymmetricConservatoryOverlook',landing,y)
  # An elevated 0.24m sitting edge stays in this level's volume. The adjacent
  # continuous level route reaches an equal-view accessible seating position.
  bay=rotate(ellipse(-85.5,fan_z,4.0,5.4),-14 if level%2 else 18,origin=(-85.5,fan_z)).intersection(landing.buffer(-.8)).difference(crosslink)
  slab(label+'_RaisedSittingEdge',bay,y,y+.24,'warm_stone','raised_sitting_edge')
  c=bay.centroid
  if not bay.is_empty:
   for j,(dx,dz,ang)in enumerate([(-1.0,-1.8,155),(.8,.2,198)]):asset('AST-FUR-002',label+'_FanSeat_'+str(j),[c.x+dx,y+.24,c.y+dz],ang,1,'Raised seating edge inside own volume; no lowered neighboring ceiling')
   asset('AST-FUR-003',label+'_FanTable',[c.x+.6,y+.24,c.y-1.0],12,1,'Oblique shared surface')
  asset('AST-FUR-002',label+'_LevelRouteSeat',[-90.8,y,fan_z],130 if level%2 else 45,1,'Equal-view level seating without climbing the raised edge')
  floor(label+'_InnerMaintenanceEdge',inner.intersection(box(-12.0,250,-8.2,483)),y)
 use=['elongated_conservatory_arrival','forward_fanned_conversation_overlook','tapered_aft_garden_overlook','long_shared_salon_overlook','quiet_upper_conservatory_arrival'][level]
 spaces.append({'id':label+'_SunsetCommons','programme_key':reservation['affected_programmes'][level],'use':use,'floor_y':y,'status':'Proposed source architecture, no new unit'})
 routes.append({'id':label+'_Crosslink','points':[[-4,y,370],[-44,y,370],[-66,y,370],[-93,y,370]],'clear_width_m':8,'purpose':'Direct ship-spine arrival to the Sunset promenade'})
 if level<4:routes.append({'id':label+'_RoomStreet','points':[[-44,y,259],[-44,y,370],[-44,y,481]],'clear_width_m':4.1,'purpose':'Retained inward guest entries; private windows stay off this street'})
 # Main commons has two fanned domestic waiting rooms, one long timber canopy
 # and a quieter writing edge. No water court or Quiet Grove reading-pod copy.
 for j,(zc,angle)in enumerate([(361.4,-22),(379.0,23)]):
  fan=rotate(ellipse(-87,zc,6.0,3.5),angle,origin=(-87,zc)).intersection(commons).difference(well.buffer(.20)).difference(lift.buffer(.20))
  slab(label+'_FannedCanopy_'+str(j),fan,y+3.14,y+3.30,'warm_walnut','ceiling')
  slab(label+'_FannedWovenSoffit_'+str(j),fan.buffer(-.24),y+3.08,y+3.14,'oatmeal_weave','ceiling')
  for x in[-92.0,-82.0]:block(label+'_CanopyPier_'+str(j)+'_'+str(x),x-.14,x+.14,y,y+3.30,zc-.16,zc+.16,'warm_walnut','pier')
  for k,(x,z,a)in enumerate([(-90,zc-.7,25),(-86.8,zc+.5,-20),(-83.8,zc-.3,-45)]):asset('AST-FUR-002',label+f'_Conversation_{j}_{k}',[x,y,z],a,1,'Fanned social seating points down the long garden view')
  asset('AST-FUR-003',label+'_ConversationTable_'+str(j),[-87.3,y,zc-.75],angle,1,'Shared conversation surface')
  fixture(label+'_CanopyLight_'+str(j),-87,y+2.98,zc,y+3.14,210)
 # Built shaft outline and closed gate reserve transport honestly.
 for x in[-71.85,-67.15]:block(label+'_LiftJamb_'+str(x),x-.08,x+.08,y,y+4.18,377.06,382.36,'champagne_metal','architecture')
 block(label+'_LiftBack',-71.85,-67.15,y,y+4.18,382.26,382.44,'ivory_enamel','architecture')
 block(label+'_LiftLeft',-71.76,-70.62,y,y+3.8,377.04,377.22,'ivory_enamel','architecture')
 block(label+'_LiftRight',-68.42,-67.24,y,y+3.8,377.04,377.22,'ivory_enamel','architecture')
 block(label+'_LiftHeader',-70.62,-68.42,y+2.55,y+3.80,377.04,377.22,'warm_walnut','architecture')
 block(label+'_ClosedLiftGate',-70.55,-68.49,y+.05,y+2.50,377.02,377.12,'champagne_metal','closed_unbuilt_lift_gate')
 contacts.append({'lift_stop_y':y,'mechanism_status':'Reserved closed five-stop lift; operating lift/cart test absent'})
# Full planted conservatory sequence, with low gardens framing long oblique
# views. Planters always start above this house floor and never sink into D12.
for i,(x,z,rx,rz,ang)in enumerate([(-79,281,8,13,-14),(-82,324,6,17,19),(-78,408,7,15,-15),(-71,455,4,10,-28)]):
 p=rotate(ellipse(x,z,rx,rz),ang,origin=(x,z)).intersection(court.buffer(-4)).difference(commons.buffer(3)).difference(outerpath.buffer(3.6))
 if p.area<3:continue
 slab('SC_GardenPlinth_'+str(i),p,84,84.38,'warm_stone','planter');slab('SC_GardenSoil_'+str(i),p.buffer(-.20),84.30,84.36,'botanical_soil','soil')
 c=p.centroid;asset('AST-BOT-011','SC_CanopyTree_'+str(i),[c.x,84.36,c.y],i*61,.75,'Rooted conservatory tree in full-scale court, never a window backdrop')
 for j in range(14):
  a=j*2.39996;rr=math.sqrt((j+.5)/14);xx=c.x+rx*.70*rr*math.cos(a);zz=c.y+rz*.72*rr*math.sin(a)
  if p.buffer(-.25).contains(Point(xx,zz)):asset(['AST-BOT-002','AST-BOT-003','AST-BOT-009'][j%3],f'SC_Understory_{i}_{j}',[xx,84.36,zz],j*37,.8,'Layered rooted planting, not a privacy substitute')
for i,z in enumerate([263,327,408,471]):
 p=ellipse(-19.4,z,5.0,8.0).intersection(inner.buffer(-.8))
 if p.area<5:continue
 slab('SC_InnerGardenPlinth_'+str(i),p,84,84.40,'warm_stone','planter');slab('SC_InnerGardenSoil_'+str(i),p.buffer(-.18),84.32,84.38,'botanical_soil','soil');c=p.centroid
 asset('AST-BOT-011','SC_InnerGardenTree_'+str(i),[c.x,84.38,c.y],i*71,.72,'Real inward receiving garden separated from service-riser reservations')
# Planted columns give the higher inward suites real nearer outlooks as well
# as the garden below. Their private maintenance interface remains explicit.
for z in[313,349,403,463]:
 block('SC_InnerTrellis_'+str(z),-15.1,-14.9,84,106.02,z-.12,z+.12,'warm_walnut','pier')
 for y in Y[1:-1]:
  p=box(-18.0,z-1.10,-14.7,z+1.10).difference(risers.buffer(.25));slab('SC_HighGardenTray_'+str(z)+'_'+str(y),p,y+.15,y+.44,'warm_stone','planter');slab('SC_HighGardenSoil_'+str(z)+'_'+str(y),p.buffer(-.15),y+.38,y+.42,'botanical_soil','soil')
  asset('AST-BOT-003','SC_HighGardenPlant_'+str(z)+'_'+str(y),[-16.1,y+.42,z],int(z+y),.85,'Authored nearer garden foliage; hidden service access not accepted')
# Actual two-flight stair: 26 risers at 173.077mm, 320mm treads, 2.5m flights.
for level,y in enumerate(Y[:-1]):
 for flight in range(2):
  x0=-81.2+flight*3.0;z0=381.9 if flight==0 else 377.74;direction=-1 if flight==0 else 1
  for step in range(13):
   za=z0+direction*step*.32;zb=z0+direction*(step+1)*.32;top=y+(flight*13+step+1)*4.5/26
   block(f'SC_Stair_{level}_{flight}_{step}',x0,x0+2.5,top-.19,top,min(za,zb),max(za,zb),'warm_stone','stair')
  for x in[x0+.07,x0+2.43]:
   beam(f'SC_StairStringer_{level}_{flight}_{x}',[x,y+flight*2.25-.08,z0],[x,y+(flight+1)*2.25-.22,z0+direction*4.16],.18,.32)
   beam(f'SC_StairRail_{level}_{flight}_{x}',[x,y+flight*2.25+1.1,z0],[x,y+(flight+1)*2.25+1.1,z0+direction*4.16],.07,.07,'champagne_metal','guard')
   for k in range(14):
    z=z0+direction*k*.32;yy=y+flight*2.25+k*2.25/13;beam(f'SC_StairBaluster_{level}_{flight}_{x}_{k}',[x,yy,z],[x,yy+1.1,z],.035,.035,'champagne_metal','guard')
 slab('SC_StairMid_'+str(level),box(-81.2,375.94,-75.7,377.74),y+2.01,y+2.25,'warm_stone','stair_landing')
 guard('SC_StairMidGuard_'+str(level),LineString([(-81.2,377.74),(-81.2,375.94),(-75.7,375.94),(-75.7,377.74)]),y+2.25)
 contacts.append({'stair':level,'first_tread':f'SC_Stair_{level}_0_0_0','last_tread':f'SC_Stair_{level}_1_12_0','top_landing_owner':'D'+str(14+level)+'_AsymmetricConservatoryOverlook','status':'Source contact check required; no normal-play route acceptance'})
# Guards follow only final union rims, so joined floors never acquire a rail.
for y in Y:
 built=[box(r['allocation_x'][0],r['allocation_z'][0],r['allocation_x'][1],r['allocation_z'][1])for r in rooms if r['floor_y']==y]
 openings=unary_union(built+[existing[y].buffer(.03),box(-4.10,365.95,-3.8,374.05)])
 rim=owned[y].buffer(-.07,join_style=2).boundary.difference(openings.buffer(.12))
 if y>84:rim=rim.difference(box(-81.35,381.70,-75.55,382.05))
 guard('SC_PublicRim_'+str(y),rim,y)
# Roof supports rise only from the authored D13 receiving interface. There is
# no asserted route to the keel and nothing intrudes into the Vesper volume.
for i,z in enumerate([260,288,316,344,396,421,451,475]):
 sec=court.intersection(box(-120,z-.1,-55,z+.1))
 if sec.is_empty:continue
 for x in[sec.bounds[0]+.48,-63.45]:
  p=box(x-.22,z-.22,x+.22,z+.22);top=101.68 if p.buffer(.25).intersects(vipcut)else 106.02
  block(f'SC_CourtPier_{i}_{x}',x-.22,x+.22,84,top,z-.22,z+.22,'warm_walnut','pier')
  contacts.append({'support':f'SC_CourtPier_{i}_{x}','base_world_xyz':[x,84,z],'receiving_status':'HOLD at D13 interface; no lower bearing source accepted','base_does_not_descend_below_y':84})
  for y in Y[1:]:
   if y<top:block(f'SC_Capital_{i}_{x}_{y}',x-.44,x+.44,y-.42,y-.24,z-.44,z+.44,'warm_stone','transition')
roof=court.difference(vipcut.buffer(.30));slab('SC_PrincipalOpaqueCover',roof,106.02,106.26,'ivory_enamel','ceiling');slab('SC_InnerOpaqueCover',inner,106.02,106.26,'ivory_enamel','ceiling')
for i,z in enumerate([262,291,320,349,389,417,451,475]):
 for j,p in enumerate(polys(roof.intersection(box(-120,z-.24,-55,z+.24)))):
  a,_,b,_=p.bounds
  if b-a>2:
   beam(f'SC_CoverRib_{i}_{j}',[a,105.88,z],[b,105.88,z],.26,.28,'warm_walnut','ceiling_rib')
   for xx in[a+.24,b-.24]:
    block(f'SC_RibBearing_{i}_{j}_{xx}',xx-.16,xx+.16,84,106.02,z-.16,z+.16,'warm_walnut','pier')
    contacts.append({'support':f'SC_RibBearing_{i}_{j}_{xx}','local_roof_contact':[xx,106.02,z],'receiving_status':'HOLD at D13 base; upper source bearing contact only'})
for i,z in enumerate([273,304,337,393,422,455]):
 sec=court.intersection(box(-120,z-.1,-55,z+.1));x=sec.bounds[0]+1.35
 if vipcut.buffer(.6).contains(Point(x,z)):continue
 fixture('SC_CourtLantern_'+str(i),x,103.92,z,106.08,300)
coords=list(court.exterior.coords)
for i,(a,b)in enumerate(zip(coords,coords[1:])):
 if abs(a[0]+63)<.01 and abs(b[0]+63)<.01:continue
 for level,y in enumerate(Y):
  wallstrip=LineString([a,b]).buffer(.09,cap_style=2)
  if level==4:wallstrip=wallstrip.difference(vipcut.buffer(.3))
  slab(f'SC_OuterEnclosure_{i}_{level}',wallstrip,y,min(y+4.5,106.26),'ivory_enamel','enclosure')
# Exact lower programme and D04 ownership are retained even where no local
# source exists. This inventory is a blocker map, not engineered support.
footprint=unary_union([court,inner,street,crosslink,verge]);lower=[]
for r in w['programmes']:
 if r['floor_y']>=84:continue
 q=box(r['allocation_x'][0],r['allocation_z'][0],r['allocation_x'][1],r['allocation_z'][1]);overlap=footprint.intersection(q).area
 if overlap>.001:lower.append({'owner':r['programme_key'],'name':r['name'],'deck':r['deck'],'allocation_x':r['allocation_x'],'allocation_z':r['allocation_z'],'floor_y':r['floor_y'],'plan_overlap_m2':round(overlap,3),'status':'Preserved owner; no lower receiving members authorized or authored'})
innerclosure=LineString([(-8.2,250),(-8.2,483)])
slab('SC_InnerGardenOpaqueBoundary',innerclosure.buffer(.09,cap_style=2),84,106.26,'ivory_enamel','enclosure')
plan={'schema':'astraea.sunset_conservatory_house.source.v1','status':'147-unit full-house source;83 ordinary/family interiors;64 honest unbuilt reservations','house_id':house,'proposed_theme':'Sunset Conservatory House','source_house_membership':membership,'principal_court_reservation':reservation,'historical_house_units':147,'modeled_regular_family_interiors':83,'specialty_vip_units_reserved':64,'upper_datums':Y,'cover_y':106.5,'parts':parts,'asset_instances':assets,'lights':lights,'routes':routes,'contacts':contacts,'commons':spaces,'rooms':rooms,'floor_regions':floor_regions,'D17_replacement_reservations':vip,'D17_court_subtraction_area_m2':court.intersection(vipcut).area,'D17_upper_volume_reservations':[r for r in vip if r.get('upper_floor_y')],'receiving_interface_blocks':lower,'base_receiving_status':'HOLD for entire new base and all upper reactions; source contact is not a load path','separate_D04_membership':next(r for r in w['residential_houses']if r['id']=='port_aft_lower_habitat_house'),'staff_riser_reservations':[r for r in w['staff_riser_reservations']if r['center_xz'][0]<0 and r['center_xz'][1]>0],'source_hashes':{str(p):sha(p)for p in[G/'data/whole_ship_layout.json',G/'data/architecture/D17_LUXURY_HOUSES_PROPOSAL.json',G/'data/generated/structural_meshes.json',S/'HOUSE_BUILD_BOUNDARIES.json',R/'SUNSET_83_PLACEMENT_MAP.json']},'limits':['No Game/Catalogue writes, Godot import, new registry, or runtime adoption','47 specialty +17 VIP interiors and royalty794 upper pavilion remain unbuilt exact reservations','Five-stop lift is closed reserved source architecture, not operating transport','All lower receiving support remains held; D12 Vesper panorama and D11 Cultural gallery protected; no structural load acceptance','Full-house actual door motion, cart, privacy with lights on/off, rendering and final art remain open','Suite outlooks are actual internal gardens/court; no exterior space-window claim through unverified hull','Six D04 houses stay independent; no species or family-age assumptions']}
out=R/'outputs/house_r001';out.mkdir(exist_ok=True);(out/'PLAN.json').write_text(json.dumps(plan,indent=2)+'\n');print('SUNSET_HOUSE_PLAN_READY',len(parts),'parts',len(assets),'assets',len(rooms),'rooms')
