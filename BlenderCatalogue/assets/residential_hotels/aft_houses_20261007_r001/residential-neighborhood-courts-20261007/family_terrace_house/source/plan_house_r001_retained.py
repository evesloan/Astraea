"""Whole starboard-aft source: shared terraced commons, honest support holds."""
from pathlib import Path
import json,sys,math,hashlib,collections,ast
W=Path(__file__).resolve().parents[3];R=Path(__file__).resolve().parents[1];S=R.parent;G=Path('/workspace/shared/astraea-godot-production-20261003')
sys.path.insert(0,str(W/'geometry-deps'))
from shapely.geometry import Polygon,box,Point,LineString,mapping
from shapely.affinity import scale
from shapely.ops import unary_union
from shapely import constrained_delaunay_triangles
read=lambda p:json.loads(Path(p).read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
w=read(G/'data/whole_ship_layout.json');lux=read(G/'data/architecture/D17_LUXURY_HOUSES_PROPOSAL.json');census=read(W/'residential-neighborhood-audit-20261007/ALL_1000_NEIGHBORHOOD_CROSSWALK.json')['records'];roommap=read(R/'FAMILY_TERRACE_82_PLACEMENT_MAP.json')
house='starboard_aft_upper_house';reservation=next(r for r in w['residential_court_reservations']if r['id']=='starboard_aft_residential_court');membership=next(r for r in w['residential_houses']if r['id']==house);court=Polygon(reservation['boundary']);commons=box(63,356,97,384)
vip=[r for r in lux['replacements']if r['house']==house];vipcut=unary_union([Polygon(r['proposed_floor_boundary'])for r in vip]);rooms=roommap['units'];parts=[];assets=[];lights=[];contacts=[];routes=[];spaces=[];floor_regions=[];owned={};Y=[84,88.5,93,97.5,102]
compiled=read(G/'data/generated/structural_meshes.json')['regions'];existing={y:unary_union([Polygon(t)for r in compiled if r['floor_y']==y for t in r['triangles']])for y in Y}
# Reuse generic metric triangulation/guard primitives, never Tidal room/lobby design.
util=S/'tidal_garden_house/source/plan_house.py'
for node in ast.parse(util.read_text()).body:
 if isinstance(node,ast.FunctionDef):exec(compile(ast.Module(body=[node],type_ignores=[]),str(util),'exec'),globals())

def group_table(name,x,z,y,length=3.8):
 q=box(x-1.0,z-length/2,x+1.0,z+length/2).buffer(.20,join_style=1)
 slab(name+'_Top',q,y+.73,y+.82,'warm_walnut','furniture')
 for j,zz in enumerate([z-length*.30,z+length*.30]):block(name+'_Trestle_'+str(j),x-.80,x+.80,y,y+.74,zz-.11,zz+.11,'ivory_enamel','furniture')
 for side in[-1,1]:
  for j,zz in enumerate([z-length*.29,z+length*.29]):asset('AST-FUR-002',name+f'_Seat_{side}_{j}',[x+side*1.65,y,zz],90 if side>0 else-90,1,'Four-person group place off the through-route')
 return q.buffer(1.20)

def pavilion(name,x0,x1,z0,z1,y):
 poly=Polygon([(x0,z0+.6),(x0+.6,z0),(x1-.6,z0),(x1,z0+.6),(x1,z1-.6),(x1-.6,z1),(x0+.6,z1),(x0,z1-.6)])
 slab(name+'_Canopy',poly,y+3.06,y+3.28,'warm_walnut','ceiling');slab(name+'_WovenUnder',poly.buffer(-.18),y+3.01,y+3.06,'oatmeal_weave','ceiling')
 for j,(x,z)in enumerate([(x0+.25,z0+.70),(x1-.25,z0+.70),(x0+.25,z1-.70),(x1-.25,z1-.70)]):
  block(name+'_Pier_'+str(j),x-.13,x+.13,y,y+3.28,z-.13,z+.13,'ivory_enamel','pier');block(name+'_PierCap_'+str(j),x-.24,x+.24,y+2.84,y+3.08,z-.24,z+.24,'warm_walnut','transition')
 fixture(name+'_TableTask',(x0+x1)/2,y+2.78,(z0+z1)/2,y+3.08,210)

crosslink=box(4,366,97,374);street=box(41.95,257.8,46.05,482.2)
risers=unary_union([box(r['lobby_x'][0],r['lobby_z'][0],r['lobby_x'][1],r['lobby_z'][1])for r in w['staff_riser_reservations']if r['center_xz'][0]>0])
inner=box(8.2,257.8,29.05,482.2).difference(risers.buffer(.15));verge=box(58.95,257.8,63,482.2)
well=box(79.2,376.0,85.3,382.5);lift=box(88.0,377.4,92.6,382.5)
floor('FT_PrincipalTerraceCourtBase',court,84);floor('FT_PrivatePlantedWindowSetback',verge,84);floor('FT_InwardGardenBase',inner,84)
for level,y in enumerate(Y):
 label='D'+str(level+13)
 floor(label+'_CartSafeArrival',crosslink,y)
 if level<4:floor(label+'_PairedBankStreet',street,y)
 else:floor(label+'_ActualDeluxeApproach',box(55.15,275,61.45,450),y)
 if level:
  # Broad terraces have deliberately different outlines and occupied ends.
  if level==1:q=Polygon([(63,350),(69,350),(69,335),(85,335),(91,343),(91,356),(97,356),(97,384),(63,384)])
  elif level==2:q=Polygon([(63,356),(97,356),(97,391),(91,391),(85,405),(69,405),(69,390),(63,390)])
  elif level==3:q=Polygon([(63,346),(73,346),(78,339),(91,339),(91,354),(97,358),(97,389),(87,401),(72,397),(72,384),(63,384)])
  else:q=Polygon([(63,356),(95,356),(97,362),(97,382),(92,388),(68,388),(63,382)])
  landing=q.intersection(court).difference(well).difference(lift)
  floor(label+'_InhabitedFamilyTerrace',landing,y)
  # Inward windows address an actual planted volume. Upper public access remains
  # near the spine, far from their rear glass.
  floor(label+'_InnerGardenQuietWalk',inner.intersection(box(8.2,257.8,12.9,482.2)),y)
  quietz=[0,344,395,348,360][level]
  if level<4:
   pavilion(label+'_UpperGatheringCanopy',72,87,quietz-5.0,quietz+5.0,y);group_table(label+'_UpperGroupTable',79.5,quietz,y,4.2)
  else:
   group_table(label+'_UpperQuietTable',79.0,360.8,y,3.5)
 # Shared domestic portals and group-sized tables flank, rather than occupy,
 # the continuous8m cross-ship through-route.
 for k,zc in enumerate([360.8,379.1]):
  pavilion(label+f'_MeetingPortal_{k}',64.1,76.6,zc-3.3,zc+3.3,y)
  group_table(label+f'_MeetingTable_{k}',70.2,zc,y,3.3)
  # Integrated shared belongings storage at the rear of each pocket.
  block(label+f'_MeetingStoragePlinth_{k}',64.3,65.05,y,y+.16,zc-2.35,zc+2.35,'warm_walnut','furniture')
  for j,zz in enumerate([zc-2.35,zc-.80,zc+.80,zc+2.28]):block(label+f'_MeetingStorageDivider_{k}_{j}',64.3,65.05,y+.16,y+1.3,zz,zz+.07,'ivory_enamel','furniture')
  for j,h in enumerate([.55,1.25]):block(label+f'_MeetingStorageShelf_{k}_{j}',64.3,65.05,y+h,y+h+.06,zc-2.35,zc+2.35,'warm_walnut','furniture')
 # Quieter reading on the remote commons edge, behind planting/acoustic screen.
 for k,zc in enumerate([359,381]):
  block(label+f'_QuietRootPlanter_{k}',94.0,96.4,y,y+.50,zc-1.3,zc+1.3,'ivory_enamel','planter');block(label+f'_QuietSoil_{k}',94.15,96.25,y+.43,y+.48,zc-1.15,zc+1.15,'botanical_soil','soil')
  asset('AST-BOT-002',label+f'_QuietPlant_{k}',[95.2,y+.48,zc],k*73,1.2,'Planted visual separator rooted in a contained commons planter')
  asset('AST-FUR-002',label+f'_QuietChair_{k}',[93.2,y,363.0 if k==0 else 374.8],90,1,'Quiet reading seat outside the table activity pocket')
  block(label+f'_QuietAcousticCheek_{k}',95.9,96.2,y+.55,y+2.20,zc-1.2,zc+1.2,'oatmeal_weave','architecture')
 spaces.append({'id':label+'_FamilyTerraceCommons','programme_key':reservation['affected_programmes'][level],'use':['arrival_and_regroup_tables','shared_project_terrace','conversation_and_quiet_edge','household_garden_terrace','quiet_upper_meeting'][level],'floor_y':y,'status':'Proposed inhabited source, no new guest units'})
 routes.append({'id':label+'_CartThroughRoute','points':[[4,y,370],[44,y,370],[63,y,370],[96,y,370]],'clear_width_m':8,'status':'Source route; actual cart/door runtime proof pending'})
 if level<4:routes.append({'id':label+'_RoomStreet','points':[[44,y,259],[44,y,370],[44,y,480]],'clear_width_m':4.1})
 else:routes.append({'id':label+'_VIPApproach','points':[[58.1,y,276],[58.1,y,370],[58.1,y,449]],'clear_width_m':6.3,'status':'Only approach; all16 VIP interiors unbuilt'})
 # Lift mechanism is explicitly reserved and visibly closed.
 for x in[87.95,92.65]:block(label+'_LiftJamb_'+str(x),x-.08,x+.08,y,y+4.15,377.35,382.55,'champagne_metal','architecture')
 block(label+'_LiftBack',87.95,92.65,y,y+4.15,382.45,382.60,'ivory_enamel','architecture')
 for x0,x1 in[(88.0,89.2),(91.4,92.6)]:block(label+'_LiftFront_'+str(x0),x0,x1,y,y+4.15,377.28,377.44,'ivory_enamel','architecture')
 block(label+'_LiftHeader',89.2,91.4,y+2.55,y+4.15,377.28,377.44,'warm_walnut','architecture');block(label+'_LiftClosedGate',89.27,91.33,y+.05,y+2.50,377.30,377.39,'champagne_metal','closed_unbuilt_lift_gate');contacts.append({'lift_stop_y':y,'mechanism_status':'Closed five-stop reserved mechanism; not operating transport'})
# Four contained planted social islands terminate long views. No sunk terrace
# penetrates the lower Celestial lounge or Reading nooks programme ceilings.
for i,(x,z,rx,rz)in enumerate([(83,282,8,16),(83,319,7,11),(82,420,7,14),(73,458,5.0,13)]):
 p=ellipse(x,z,rx,rz).intersection(court.buffer(-3)).difference(commons.buffer(5))
 if p.area<10:continue
 slab('FT_RootedGardenPlinth_'+str(i),p,84,84.54,'ivory_enamel','planter');slab('FT_RootedGardenSoil_'+str(i),p.buffer(-.22),84.46,84.50,'botanical_soil','soil');c=p.centroid
 asset('AST-BOT-011','FT_GardenCanopy_'+str(i),[c.x,84.50,c.y],i*67,.62 if i<3 else .43,'Tree canopy tied to rooted plinth, receiving outlook and activity pause')
 for j in range(12):
  a=j*2.39996;rr=math.sqrt((j+.5)/12);xx=c.x+rx*.64*rr*math.cos(a);zz=c.y+rz*.64*rr*math.sin(a)
  if p.buffer(-.35).contains(Point(xx,zz)):asset(['AST-BOT-002','AST-BOT-003','AST-BOT-009'][j%3],f'FT_GardenUnderplant_{i}_{j}',[xx,84.5,zz],j*41,.82,'Rooted shrub/groundcover hierarchy')
 # Seat ends and a table sit on the base floor beside, not in, the planting.
 if i<3:
  asset('AST-FUR-001','FT_GardenPauseBench_'+str(i),[min(96,c.x+rx+2.1),84,c.y],90,1,'Rest place at the end of the garden outlook')
for i,z in enumerate([278,309,344,397,424,462]):
 p=ellipse(20,z,4.7,6.4).intersection(inner.buffer(-1.5))
 if p.area<6:continue
 slab('FT_InwardPlanter_'+str(i),p,84,84.45,'ivory_enamel','planter');slab('FT_InwardSoil_'+str(i),p.buffer(-.18),84.36,84.41,'botanical_soil','soil');c=p.centroid;asset('AST-BOT-011','FT_InwardCanopy_'+str(i),[c.x,84.41,c.y],i*37,.47,'Real inner-bank garden outlook; no private opposing suite aperture')
# Independent two-flight stair adjoining the clear arrival; no diagonal bridge grid.
for level,y in enumerate(Y[:-1]):
 for flight in range(2):
  x0=79.45+flight*3.0;z0=376.0 if flight==0 else 380.16;direction=1 if flight==0 else-1
  for step in range(13):
   za=z0+direction*step*.32;zb=z0+direction*(step+1)*.32;top=y+(flight*13+step+1)*4.5/26
   block(f'Stair_{level}_{flight}_{step}',x0,x0+2.5,top-.19,top,min(za,zb),max(za,zb),'warm_stone','stair')
  for x in[x0+.07,x0+2.43]:
   beam(f'FT_StairStringer_{level}_{flight}_{x}',[x,y+flight*2.25-.08,z0],[x,y+(flight+1)*2.25-.22,z0+direction*4.16],.18,.32)
   beam(f'FT_StairRail_{level}_{flight}_{x}',[x,y+flight*2.25+1.1,z0],[x,y+(flight+1)*2.25+1.1,z0+direction*4.16],.07,.07,'champagne_metal','guard')
   for k in range(14):
    zz=z0+direction*k*.32;yy=y+flight*2.25+k*2.25/13;beam(f'FT_StairBaluster_{level}_{flight}_{x}_{k}',[x,yy,zz],[x,yy+1.1,zz],.035,.035,'champagne_metal','guard')
 slab('FT_StairMid_'+str(level),box(79.45,380.16,84.95,381.96),y+2.01,y+2.25,'warm_stone','stair_landing');guard('FT_StairMidGuard_'+str(level),LineString([(79.45,380.16),(79.45,381.96),(84.95,381.96),(84.95,380.16)]),y+2.25)
# New floor guards follow its final union and do not cross real suite entrances.
for y in Y:
 built=[box(r['allocation_x'][0],r['allocation_z'][0],r['allocation_x'][1],r['allocation_z'][1])for r in rooms if r['floor_y']==y]
 openings=unary_union(built+[existing[y].buffer(.03),box(3.8,365.95,4.10,374.05)])
 rim=owned[y].buffer(-.025,join_style=2).boundary.difference(openings.buffer(.12))
 if y>84:rim=rim.difference(box(79.1,375.8,85.45,376.2))
 guard('FT_PublicRim_'+str(y),rim,y)
# Explicit above-base wall piers support finite cover and landing edges. Their
# base receiving/load interface remains HOLD; no invented truss spans below84.
for i,z in enumerate([261,293,325,351,389,417,445,471]):
 sec=court.intersection(box(60,z-.1,105,z+.1))
 if sec.is_empty:continue
 for x in[63.45,sec.bounds[2]-.48]:
  p=box(x-.22,z-.22,x+.22,z+.22);top=101.68 if p.buffer(.25).intersects(vipcut)else 106.02
  block(f'FT_CourtPier_{i}_{x}',x-.22,x+.22,84,top,z-.22,z+.22,'warm_walnut','pier')
# Principal cover respects all actual replacement footprints and Royalty797 upper.
roof=court.difference(vipcut.buffer(.30));slab('FT_PrincipalOpaqueCover',roof,106.02,106.26,'ivory_enamel','ceiling');slab('FT_InwardGardenCover',inner,106.02,106.26,'ivory_enamel','ceiling')
for i,z in enumerate([261,293,325,351,389,417,445,471]):
 for j,p in enumerate(polys(roof.intersection(box(60,z-.20,105,z+.20)))):
  x0,_,x1,_=p.bounds
  if x1-x0>1:beam(f'FT_CoverRib_{i}_{j}',[x0+.12,105.90,z],[x1-.12,105.90,z],.26,.28,'warm_walnut','ceiling_rib')
for i,z in enumerate([280,315,345,393,417,450,475]):
 sec=roof.intersection(box(60,z-.1,105,z+.1))
 if sec.is_empty:continue
 x=(sec.bounds[0]+sec.bounds[2])/2
 if vipcut.buffer(.8).contains(Point(x,z)):continue
 fixture('FT_CourtLantern_'+str(i),x,103.85,z,106.08,290)
# Enclosure follows the true court polygon and leaves suite receiving view side
# open to the private planted setback; no generic starfield or fake space window.
coords=list(court.exterior.coords)
for i,(a,b)in enumerate(zip(coords,coords[1:])):
 if abs(a[0]-63)<.01 and abs(b[0]-63)<.01:continue
 for level,y in enumerate(Y):
  strip=LineString([a,b]).buffer(.09,cap_style=2)
  if level==4:strip=strip.difference(vipcut.buffer(.30))
  slab(f'FT_CourtEnclosure_{i}_{level}',strip,y,min(y+4.5,106.26),'ivory_enamel','enclosure')
protected_lower=[{'owner':r['programme_key'],'name':r['name'],'x':r['allocation_x'],'z':r['allocation_z'],'y':[78,83.76],'status':'Protected lower programme; no intrusive transfer members authored'}for r in w['programmes']if r['programme_key']in['D12_directory_10','D12_directory_08']]
held=[{'id':'FT_BASE_RECEIVING_HOLD','scope':'All proposed new Y84 base floors and the court frame above them','status':'No lower load path accepted. Source floors are layout source only; do not adopt before receiving structure is resolved owner-by-owner.','protected_lower_programmes':protected_lower,'unmodeled_transfer_members':True},{'id':'FT_CONCEALED_SERVICE_HOLD','scope':'Staff riser connection and service partitions','status':'Existing five starboard riser reservations protected, no unproved guest/service merge'},{'id':'FT_D17_ROYALTY797_UPPER_HOLD','source_index':797,'scope':'Exact upper level at106.5 and roof112','status':'Reservation only; no public cover or ordinary shell claimed'}]
plan={'schema':'astraea.family_terrace_house.source.v1','status':'145-member whole-house proposed architectural source;82 interiors;63 explicit unbuilt reservations','house_id':house,'proposed_theme':'Family Terrace House','source_house_membership':membership,'principal_court_reservation':reservation,'historical_house_units':145,'modeled_regular_family_interiors':82,'specialty_vip_units_reserved':63,'upper_datums':Y,'cover_y':106.5,'parts':parts,'asset_instances':assets,'lights':lights,'routes':routes,'contacts':contacts,'commons':spaces,'rooms':rooms,'floor_regions':floor_regions,'D17_replacement_reservations':vip,'D17_court_subtraction_area_m2':court.intersection(vipcut).area,'receiving_interface_blocks':protected_lower,'structural_support_holds':held,'temporary_unbuilt_specialty_frontage_guards':[{'source_index':r['source_envelope_index'],'door_xz':r['historical_door_marker_xz']}for r in census if r['house']==house and r['production_lane']!='regular_source_supported'and r['deck']!='D17'],'source_hashes':{str(p):sha(p)for p in[G/'data/whole_ship_layout.json',G/'data/generated/structural_meshes.json',G/'data/architecture/HULL_BODY_SECTION_PROPOSAL.json',G/'data/architecture/D17_LUXURY_HOUSES_PROPOSAL.json',G/'data/architecture/AFT_PUBLIC_CORE.json',G/'data/architecture/AFT_MIDSHIP_PUBLIC_CORE.json',S/'HOUSE_BUILD_BOUNDARIES.json',R/'FAMILY_TERRACE_82_PLACEMENT_MAP.json',util]},'limits':['No Game/Catalogue edits, engine imports, registration or adoption','47 specialty+16 VIP interiors remain unbuilt; exact identities and polygons retained','Family means three real berths, not automatic children/nursery or species population','Base receiving structure is HOLD; no invented long diagonal transfer or lower-hull columns','Five-stop lift visibly closed and unbuilt; source stairs do not establish transport acceptance','Full-house moving-door/cart/species, privacy, concealed-service, load and native art acceptance remain open']}
out=R/'outputs/house_r001';out.mkdir(exist_ok=True);(out/'PLAN.json').write_text(json.dumps(plan,indent=2)+'\n');print('FAMILY_TERRACE_WHOLE_HOUSE_PLAN',len(parts),len(assets),len(rooms),len(held))
