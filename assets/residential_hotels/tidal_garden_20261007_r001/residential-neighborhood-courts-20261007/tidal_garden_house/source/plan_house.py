"""Full PF construction source. Actual polygons; explicit receiving holds."""
from pathlib import Path
import json,sys,math,hashlib,collections
sys.path.insert(0,'/workspace/scratch/375c2e438292/geometry-deps')
from shapely.geometry import Polygon,box,Point,LineString,mapping
from shapely.affinity import scale
from shapely.ops import unary_union
from shapely import constrained_delaunay_triangles
R=Path(__file__).resolve().parents[1];S=R.parent;W=S.parent;G=Path('/workspace/shared/astraea-godot-production-20261003')
read=lambda p:json.loads(Path(p).read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
w=read(G/'data/whole_ship_layout.json');lux=read(G/'data/architecture/D17_LUXURY_HOUSES_PROPOSAL.json');census=read(W/'residential-neighborhood-audit-20261007/ALL_1000_NEIGHBORHOOD_CROSSWALK.json')['records'];mapping85=read(R/'TIDAL_GARDEN_85_PLACEMENT_MAP.json')
house='port_forward_upper_house';reservation=next(r for r in w['residential_court_reservations']if r['id']=='port_forward_residential_court');membership=next(r for r in w['residential_houses']if r['id']==house);court=Polygon(reservation['boundary']);commons=box(-97,-384,-63,-356)
vip=[r for r in lux['replacements']if r['house']==house];vipcut=unary_union([Polygon(r['proposed_floor_boundary'])for r in vip]);rooms=mapping85['units'];parts=[];assets=[];lights=[];contacts=[];routes=[];spaces=[];floor_regions=[];owned={};Y=[84,88.5,93,97.5,102]
compiled=read(G/'data/generated/structural_meshes.json')['regions'];existing={y:unary_union([Polygon(t)for r in compiled if r['floor_y']==y for t in r['triangles']])for y in Y}
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
crosslink=box(-97,-374,-4,-366);street=box(-46.05,-482.2,-41.95,-268)
risers=unary_union([box(r['lobby_x'][0],r['lobby_z'][0],r['lobby_x'][1],r['lobby_z'][1])for r in w['staff_riser_reservations']if r['center_xz'][0]<0])
inner=box(-29.05,-482.2,-8.2,-268).difference(risers.buffer(.15));verge=box(-63,-482.2,-58.95,-268)
well=box(-86,-381.8,-79.8,-375.4);lift=box(-76.8,-382.8,-72.2,-377.8)
floor('TG_PrincipalCourtBase',court,84);floor('TG_PrivateWindowVerge',verge,84);floor('TG_InnerDryGardenBase',inner,84)
for level,y in enumerate(Y):
 label='D'+str(13+level)
 floor(label+'_CrossShipDryArrival',crosslink,y)
 if level<4:floor(label+'_PairedBankStreet',street,y)
 else:
  # Actual D17 deluxe polygon edge replaces the old paired-bank footprint.
  floor(label+'_DeluxeApproachNorth',box(-43,-459,-38,-384),y)
  floor(label+'_DeluxeApproachSouth',box(-43,-356,-38,-281),y)
  floor(label+'_DeluxeCrosslink',box(-43,-384,-38,-356),y)
 if level:
  # Contained lobe lengths alternate in section. No full-height balcony ring.
  lobez=[None,-390,-349,-389,-349][level];lobe=ellipse(-85,lobez,9.2,9)
  landing=unary_union([box(-94,-384,-63,-356),lobe]).intersection(court).difference(well).difference(lift)
  floor(label+'_OffsetTidalLanding',landing,y)
  branchz=-415 if level%2 else -325
  branch=unary_union([box(-97,min(branchz,-370),-92,max(branchz,-370)),ellipse(-91,branchz,7.8,10.2)]).intersection(court.buffer(-.15))
  floor(label+'_DryOutlookSpur',branch,y)
  # Inner-bank outlook is a planted court; its narrow public route hugs the spine.
  floor(label+'_InnerDryPromenade',inner.intersection(box(-12.8,-483,-8.2,-267)),y)
  for xx in[-89,-85]:asset('AST-FUR-002',label+'_LandingSeat_'+str(xx),[xx,y,lobez],180 if level%2 else 0,1,'Sheltered cove seat outside continuous dry arrival')
  asset('AST-FUR-003',label+'_LandingTable',[-87,y,lobez+1.1],0,1,'Shared table with court outlook')
 use=['water_garden_arrival','north_waiting_cove','south_rest_cove','family_salon_landing','private_upper_arrival'][level]
 spaces.append({'id':label+'_TidalGardenCommons','programme_key':reservation['affected_programmes'][level],'use':use,'floor_y':y,'status':'Proposed authored composition, no new units'})
 routes.append({'id':label+'_DryArrival','points':[[-4,y,-370],[-44,y,-370],[-66,y,-370],[-94,y,-370]],'clear_width_m':8,'door_access':'Existing paired-bank markers for D13-D16; true replacement approach at D17'})
 if level<4:routes.append({'id':label+'_RoomStreet','points':[[-44,y,-480],[-44,y,-370],[-44,y,-270]],'clear_width_m':4.1})
 # Two curved, sheltered coves flank the clear crosslink, with a built curved back.
 for j,zc in enumerate([-379.2,-359.8]):
  p=ellipse(-67.7,zc,3.8,3.0).intersection(commons)
  canopy=p.buffer(.28).intersection(commons);slab(label+f'_CoveCanopy_{j}',canopy,y+3.10,y+3.27,'warm_walnut','ceiling')
  slab(label+f'_CoveAcousticSoffit_{j}',canopy.buffer(-.18),y+3.05,y+3.10,'oatmeal_weave','ceiling')
  arc=[(-67.7+3.0*math.cos(math.pi*(k/10-.5)),zc+2.5*math.sin(math.pi*(k/10-.5)))for k in range(11)]
  for k,(a,b)in enumerate(zip(arc,arc[1:])):
   beam(label+f'_CoveBack_{j}_{k}',[a[0],y+1.12,a[1]],[b[0],y+1.12,b[1]],.18,2.24,'ivory_enamel','architecture')
  for z in[zc-1.5,zc+1.5]:block(label+f'_CovePier_{j}_{z}',-65.0,-64.7,y,y+3.26,z-.13,z+.13,'warm_walnut','pier')
  asset('AST-FUR-002',label+f'_CoveChair_{j}',[-68,y,zc],90,1,'Water-facing sheltered waiting seat')
  asset('AST-FUR-003',label+f'_CoveTable_{j}',[-69.35,y,zc],0,1,'Practical side table')
  fixture(label+f'_CoveLight_{j}',-67.4,y+2.96,zc,y+3.10,160)
 # Lift shaft is a reserved functional mechanism, never a claimed operating lift.
 for x in[-76.85,-72.15]:block(label+'_LiftJamb_'+str(x),x-.08,x+.08,y,y+4.18,-382.85,-377.78,'champagne_metal','architecture')
 block(label+'_LiftBack',-76.85,-72.15,y,y+4.18,-382.95,-382.78,'ivory_enamel','architecture')
 block(label+'_LiftDoorLeft',-76.75,-75.62,y,y+3.8,-377.84,-377.68,'ivory_enamel','architecture')
 block(label+'_LiftDoorRight',-73.42,-72.25,y,y+3.8,-377.84,-377.68,'ivory_enamel','architecture')
 block(label+'_LiftHeader',-75.62,-73.42,y+2.55,y+3.8,-377.84,-377.68,'warm_walnut','architecture')
 block(label+'_LiftClosedGate',-75.55,-73.49,y+.05,y+2.5,-377.86,-377.78,'champagne_metal','closed_unbuilt_lift_gate')
 contacts.append({'lift_stop_y':y,'mechanism_status':'Reserved five-stop lift; gate closed until operating mechanism authoring and actual cart test'})
# Dry continuous base route and three contained water/planting sequences.
for i,(z,rx,rz)in enumerate([(-456,7,18),(-419,9,13),(-310,10,22)]):
 pool=ellipse(-82 if i==0 else-84,z,rx,rz).intersection(court.buffer(-6)).difference(commons.buffer(4))
 if pool.area<10:continue
 cavity=pool.buffer(-.35)
 slab('TG_ContainedBasinOuter_'+str(i),pool.difference(cavity),84,84.72,'ivory_enamel','basin')
 slab('TG_ContainedBasinBottom_'+str(i),cavity,84,84.16,'warm_stone','basin')
 slab('TG_ContainedWater_'+str(i),cavity,84.68,84.70,'water','water')
 island=ellipse(-82 if i==0 else-84,z+2,2.9,5.1).intersection(cavity.buffer(-.5))
 slab('TG_RootedIsland_'+str(i),island,84.16,85.13,'warm_stone','planter');slab('TG_RootSoil_'+str(i),island.buffer(-.18),85.10,85.12,'botanical_soil','soil')
 c=island.centroid;asset('AST-BOT-011','TG_WaterGardenTree_'+str(i),[c.x,85.12,c.y],i*81,.68,'Rooted dry island in a contained ornamental water basin; no habitat simulation claim')
 for j in range(14):
  a=j*2.39996;rr=math.sqrt((j+.5)/14);x=c.x+2.2*rr*math.cos(a);zz=c.y+4.0*rr*math.sin(a)
  if island.buffer(-.3).contains(Point(x,zz)):asset(['AST-BOT-002','AST-BOT-003','AST-BOT-009'][j%3],f'TG_IslandUnderstory_{i}_{j}',[x,85.12,zz],j*43,.7,'Dry planting only')
 contacts.append({'water_basin':i,'bottom_y':84,'water_top_y':84.70,'lower_ceiling_cut':False,'engineering_status':'Contained geometric source, load/waterproofing/pump design unaccepted'})
for i,z in enumerate([-468,-427,-319,-278]):
 p=ellipse(-20,z,5.0,7.0).intersection(inner.buffer(-2));slab('TG_InnerPlanter_'+str(i),p,84,84.4,'ivory_enamel','planter');slab('TG_InnerSoil_'+str(i),p.buffer(-.18),84.32,84.36,'botanical_soil','soil')
 if p.area>10:
  c=p.centroid;asset('AST-BOT-011','TG_InnerGardenTree_'+str(i),[c.x,84.36,c.y],i*71,.52,'Real dry receiving outlook for inward rooms')
# Proper two-flight stair and landings at all transitions.
for level,y in enumerate(Y[:-1]):
 for flight in range(2):
  x0=-85.7+flight*3.0;z0=-381.8 if flight==0 else-377.64;direction=1 if flight==0 else-1
  for step in range(13):
   za=z0+direction*step*.32;zb=z0+direction*(step+1)*.32;top=y+(flight*13+step+1)*4.5/26
   block(f'Stair_{level}_{flight}_{step}',x0,x0+2.5,top-.19,top,min(za,zb),max(za,zb),'warm_stone','stair')
  for x in[x0+.07,x0+2.43]:
   beam(f'TG_StairStringer_{level}_{flight}_{x}',[x,y+flight*2.25-.08,z0],[x,y+(flight+1)*2.25-.22,z0+direction*4.16],.18,.32)
   beam(f'TG_StairRail_{level}_{flight}_{x}',[x,y+flight*2.25+1.1,z0],[x,y+(flight+1)*2.25+1.1,z0+direction*4.16],.07,.07,'champagne_metal','guard')
   for k in range(14):
    z=z0+direction*k*.32;yy=y+flight*2.25+k*2.25/13;beam(f'TG_StairBaluster_{level}_{flight}_{x}_{k}',[x,yy,z],[x,yy+1.1,z],.035,.035,'champagne_metal','guard')
 slab('TG_StairMid_'+str(level),box(-85.7,-377.64,-80.2,-375.84),y+2.01,y+2.25,'warm_stone','stair_landing')
 guard('TG_StairMidGuard_'+str(level),LineString([(-85.7,-377.64),(-85.7,-375.84),(-80.2,-375.84),(-80.2,-377.64)]),y+2.25)
 contacts.append({'stair':level,'first_tread':f'Stair_{level}_0_0_0','last_tread':f'Stair_{level}_1_12_0','top_landing_owner':'D'+str(14+level)+'_OffsetTidalLanding','geometry_status':'Exact floor contact required by checker'})
# Route guards are generated on the final union: never rail across joined floors.
for y in Y:
 built=[box(r['allocation_x'][0],r['allocation_z'][0],r['allocation_x'][1],r['allocation_z'][1])for r in rooms if r['floor_y']==y]
 openings=unary_union(built+[existing[y].buffer(.03),box(-4.10,-374.05,-3.8,-365.95)])
 rim=owned[y].buffer(-.07,join_style=2).boundary.difference(openings.buffer(.12))
 # Stair-mouth landing edges must remain open for real first/last treads.
 if y>84:rim=rim.difference(box(-85.85,-382.02,-80.05,-381.60))
 guard('TG_PublicRim_'+str(y),rim,y)
# Columns rise from the new source base only. VIP interruptions are literal.
for i,z in enumerate([-480,-452,-424,-396,-344,-316,-288,-270]):
 section=court.intersection(box(-120,z-.1,-55,z+.1))
 if section.is_empty:continue
 xmin=section.bounds[0]
 for x in[xmin+.48,-63.45]:
  p=box(x-.22,z-.22,x+.22,z+.22);top=101.68 if p.buffer(.25).intersects(vipcut)else 106.02
  block(f'TG_CourtPier_{i}_{x}',x-.22,x+.22,84,top,z-.22,z+.22,'warm_walnut','pier')
  for y in Y[1:]:
   if y<top:block(f'TG_Capital_{i}_{x}_{y}',x-.44,x+.44,y-.42,y-.24,z-.44,z+.44,'ivory_enamel','transition')
# Receiving beams explicitly omit both protected D12 programme spans.
protected_lower=[{'owner':r['programme_key'],'name':r['name'],'x':r['allocation_x'],'z':r['allocation_z'],'y':[78,83.76],'status':'Exact source intake/support unresolved; no intrusive transfer members'}for r in w['programmes']if r['deck']=='D12'and r['programme_key']in['D12_directory_01','D12_directory_03']]
for i,z in enumerate([-480,-386,-370,-274]):
 section=court.intersection(box(-120,z-.1,-55,z+.1));xmin=section.bounds[0]
 block('TG_SpineReceiver_'+str(i),-4.30,-3.70,78,78.22,z-.38,z+.38,'champagne_metal','receiver')
 beam('TG_TransferTop_'+str(i),[-4.1,83.5,z],[xmin+.35,83.5,z],.45,.52,'ivory_enamel')
 beam('TG_TransferDiagonal_'+str(i),[-4.1,78.24,z],[xmin+.35,83.5,z],.42,.42)
 contacts.append({'receiver':'TG_SpineReceiver_'+str(i),'existing_owner':('D12_fore_midship_public_core_floor' if z==-274 else 'D12_fore_route'),'point':[-3.85,78,z],'status':'Actual compiled-floor point check only, not engineered load approval'})
for x in[-95.5,-63.45,-59.2,-45.8,-42.2,-28.75,-12.4,-8.55]:
 q=LineString([(x,-480),(x,-270)])
 for p in protected_lower:q=q.difference(box(p['x'][0]-.3,p['z'][0]-.3,p['x'][1]+.3,p['z'][1]+.3))
 q=q.intersection(unary_union([court,inner,box(-59.45,-482.2,-29.05,-268)]).buffer(-.1))
 for j,l in enumerate(lines(q)):
  a,b=list(l.coords)[0],list(l.coords)[-1]
  if l.length>.5:beam(f'TG_BaseLongitudinal_{x}_{j}',[a[0],83.42,a[1]],[b[0],83.42,b[1]],.34,.68)
roof=court.difference(vipcut.buffer(.30));slab('TG_PrincipalOpaqueCover',roof,106.02,106.26,'ivory_enamel','ceiling');slab('TG_InnerOpaqueCover',inner,106.02,106.26,'ivory_enamel','ceiling')
for i,z in enumerate([-477,-451,-425,-399,-347,-321,-295,-272]):
 sec=roof.intersection(box(-120,z-.25,-55,z+.25))
 for j,p in enumerate(polys(sec)):
  a,_,b,_=p.bounds
  if b-a>2:beam(f'TG_CoverRib_{i}_{j}',[a,105.88,z],[b,105.88,z],.24,.28,'warm_walnut','ceiling_rib')
for i,z in enumerate([-468,-440,-412,-390,-347,-320,-292,-274]):
 sec=court.intersection(box(-120,z-.1,-55,z+.1));x=sec.bounds[0]+1.3
 if vipcut.buffer(.6).contains(Point(x,z)):continue
 fixture('TG_CourtLantern_'+str(i),x,103.9,z,106.08,280)
# Shaped opaque exterior retains court enclosure; no false space windows.
coords=list(court.exterior.coords)
for i,(a,b)in enumerate(zip(coords,coords[1:])):
 if abs(a[0]+63)<.01 and abs(b[0]+63)<.01:continue
 for level,y in enumerate(Y):
  wallstrip=LineString([a,b]).buffer(.09,cap_style=2)
  if level==4:wallstrip=wallstrip.difference(vipcut.buffer(.3))
  slab(f'TG_OuterEnclosure_{i}_{level}',wallstrip,y,min(y+4.5,106.26),'ivory_enamel','enclosure')
plan={'schema':'astraea.tidal_garden_house.source.v1','status':'148-unit full-house source construction;85 authored Tidal interiors;63 unbuilt reservations','house_id':house,'proposed_theme':'Tidal Garden House','source_house_membership':membership,'principal_court_reservation':reservation,'historical_house_units':148,'modeled_regular_family_interiors':85,'specialty_vip_units_reserved':63,'upper_datums':Y,'cover_y':106.5,'parts':parts,'asset_instances':assets,'lights':lights,'routes':routes,'contacts':contacts,'commons':spaces,'rooms':rooms,'floor_regions':floor_regions,'D17_replacement_reservations':vip,'D17_court_subtraction_area_m2':court.intersection(vipcut).area,'receiving_interface_blocks':protected_lower,'temporary_unbuilt_specialty_frontage_guards':[{'source_index':r['source_envelope_index'],'door_xz':r['historical_door_marker_xz']}for r in census if r['house']==house and r['production_lane']!='regular_source_supported'and r['deck']!='D17'],'source_hashes':{str(p):sha(p)for p in[G/'data/whole_ship_layout.json',G/'data/architecture/D17_LUXURY_HOUSES_PROPOSAL.json',S/'HOUSE_BUILD_BOUNDARIES.json',R/'TIDAL_GARDEN_85_PLACEMENT_MAP.json']},'limits':['No Game/Catalogue writes, engine imports, registration or adoption','46 specialty +17 VIP interiors remain unbuilt; exact polygons preserved','Five-stop lift is a closed reserved mechanism, not operating transport','D12 Horizon room and Listening salon prevent complete receiving support; no structural certification','Full-house door, cart, sightline privacy, runtime rendering and final art acceptance remain open','The water court is contained ornamental source geometry, not an aquatic population assignment']}
out=R/'outputs/house_r001';out.mkdir(exist_ok=True);(out/'PLAN.json').write_text(json.dumps(plan,indent=2)+'\n');print('TIDAL_HOUSE_PLAN_READY',len(parts),'parts',len(assets),'catalogue instances',len(rooms),'rooms')
