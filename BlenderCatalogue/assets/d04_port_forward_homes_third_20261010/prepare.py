from pathlib import Path
import json,hashlib,math
from shapely.geometry import box,Polygon,mapping
from shapely.geometry.polygon import orient
from shapely import constrained_delaunay_triangles
from shapely.ops import unary_union
R=Path(__file__).resolve().parents[3];W=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
parts=[]
faces=[[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]
def add(name,vs,fs,role='champagne_metal',category='frame'):
    parts.append({'name':name,'verts':vs,'faces':fs,'role':role,'category':category,'runtime_collision':True})
def cube(name,lo,hi,role='champagne_metal',category='frame'):
    x,y,z=lo;X,Y,Z=hi
    add(name,[(x,y,z),(X,y,z),(X,Y,z),(x,Y,z),(x,y,Z),(X,y,Z),(X,Y,Z),(x,Y,Z)],faces,role,category)
def prism(name,poly,lo,hi,axis='y',role='warm_stone',category='floor'):
    poly=orient(poly,sign=1);vs=[];fs=[]
    def point(u,v,w):return [u,w,v]if axis=='y'else([w,v,u]if axis=='x'else[u,v,w])
    for tri in constrained_delaunay_triangles(poly).geoms:
        q=list(orient(tri,sign=1).exterior.coords)[:3];i=len(vs)
        vs.extend([point(u,v,w)for w in [lo,hi]for u,v in q]);fs.extend([[i,i+2,i+1],[i+3,i+4,i+5]])
    for ring in [poly.exterior,*poly.interiors]:
        for a,b in zip(ring.coords,list(ring.coords)[1:]):
            i=len(vs);vs.extend([point(*a,lo),point(*b,lo),point(*b,hi),point(*a,hi)]);fs.append([i,i+1,i+2,i+3])
    if axis in ['x','y']:fs=[list(reversed(f))for f in fs]
    add(name,vs,fs,role,category)
def segment(name,a,b,width=.12,depth=.12,role='champagne_metal',category='truss_brace'):
    # Rectangular longitudinal member, all endpoint faces retained for exact joints.
    import numpy as np
    a=np.array(a,float);b=np.array(b,float);w=(b-a)/np.linalg.norm(b-a)
    aux=np.array([1,0,0])if abs(w[0])<.9 else np.array([0,0,1])
    u=np.cross(w,aux);u/=np.linalg.norm(u);v=np.cross(w,u)
    # Local coordinates use right-handed u,v,w; bottom/top winding stays positive.
    vs=[(p+sx*u*width/2+sy*v*depth/2).tolist()for p in [a,b]for sx,sy in [(-1,-1),(1,-1),(1,1),(-1,1)]]
    add(name,vs,faces,role,category)

from shapely import affinity
import copy
base='e9100ce6629d771697a279e0ac5ac4b11395e181'
prior='BlenderCatalogue/assets/d04_port_forward_receiving_20261010'
old=json.load(open(R/prior/'PLAN.json'));all_units=old['units'];assert len(all_units)==20 and sum(u['proposed_rest_place_count']for u in all_units)==25
catalogue=json.load(open(R/'BlenderCatalogue/catalogue_manifest.json'))
source_ids=['AST-RST-QC-001','AST-RST-AQ-001','AST-SAN-001','AST-SAN-002','AST-SAN-003','AST-FUR-001','AST-FUR-002','AST-FUR-003']
sources={i:next(a for a in catalogue['assets']if a['catalogue_id']==i)for i in source_ids}
inputs=[prior+'/PLAN.json',prior+'/D04PortForwardReceiving.blend','Game/assets/models/D04_PORT_FORWARD_RECEIVING_r001.glb','Game/assets/models/D04_STAFF_WALL_PORTAL_PATCH_r001.glb','Game/data/architecture/D04_PORT_FORWARD_RECEIVING.json','Game/data/spatial_layout.json','BlenderCatalogue/catalogue_manifest.json','Game/docs/master_source/MASTER_CURRENT_APPLICATION.json','Game/docs/master_source/MASTER_FULL_CONTENT_INDEX.json','BlenderCatalogue/assets/residential_hotels/central_room_families_20261007_r001/residential-neighborhood-audit-20261007/ALL_1000_NEIGHBORHOOD_CROSSWALK.json','BlenderCatalogue/assets/group3_crew_service_20261009/source/CREW_BANK_PLACEMENTS_PROPOSAL.json','BlenderCatalogue/references/residential_20261004/Guest_suite_corridor_8077.jpg','BlenderCatalogue/references/aquatic/image(20261001-035517).png','BlenderCatalogue/references/intimate/image(20261002-000722).png','Game/assets/models/crew_home/SharedCrewHome.glb','Game/data/architecture/SHARED_CREW_HOME.json','Game/scripts/shared_crew_home.gd']
inputs.extend(['Game/scripts/grand_pool_section.gd','Game/data/architecture/GRAND_POOL_SECTION_RUNTIME.json','Game/assets/models/AST-AQU-016.glb'])
inputs.extend(['Game/scripts/crew_home_approach.gd','Game/data/architecture/CREW_HOME_APPROACH_RUNTIME.json','Game/assets/models/AST-STF-010_home_dogleg_labels002.glb'])
inputs.extend(['BlenderCatalogue/assets/d04_port_forward_homes_first_20261010/RUNTIME_PLAN.json','Game/data/architecture/D04_PORT_FORWARD_HOMES_FIRST.json','Game/scripts/d04_port_forward_homes_first.gd','Game/assets/models/D04_PORT_FORWARD_HOMES_RECEIVING_r001.glb','Game/assets/models/D04_PORT_FORWARD_HOME_GUARDS_r001.glb','BlenderCatalogue/assets/d04_port_forward_homes_first_20261010/D04HomesReceivingAndCommons.blend'])
for a in sources.values():inputs.extend(['BlenderCatalogue/'+a['source'],'BlenderCatalogue/'+a['export']])
for i in ['AST-DOR-002','AST-DOR-001']:
 a=next(a for a in catalogue['assets']if a['catalogue_id']==i);inputs.extend(['BlenderCatalogue/'+a['source'],'Game/assets/models/'+i+'.glb'])
for tag in ['first','second']:
 rp='BlenderCatalogue/assets/d04_port_forward_homes_'+tag+'_20261010/RUNTIME_PLAN.json';inputs.append(rp)
 rt=json.load(open(R/rp));inputs.extend('Game/assets/models/'+n for n in rt['model_pins'])
inputs.extend(['Game/scripts/d04_port_forward_homes_second.gd','Game/data/architecture/D04_PORT_FORWARD_HOMES_SECOND.json','BlenderCatalogue/assets/d04_port_forward_homes_second_20261010/D04SecondHomesReceivingAndCourts.blend','BlenderCatalogue/assets/d04_port_forward_homes_second_20261010/D04SecondHomeEntryGuardSuccessors.blend'])
inputs=list(dict.fromkeys(inputs))
rooms=[];feet=[]
for idx in [976,988]:
 a=copy.deepcopy(next(u for u in all_units if u['source_envelope_index']==idx));assert a['proposed_rest_place_count']==2
 west=idx==976;variant=True;x0,x1=a['allocation_x'];z0,z1=a['allocation_z'];cx=(x0+x1)/2;cz=(z0+z1)/2;prefix='D04H'+str(idx)+'_';parts=[]
 # Exact allocation preserved; architectural chamfers change the authored shell.
 chamfer=.85 if not variant else 1.15
 poly=Polygon([(x0+chamfer,z0),(x1-chamfer,z0),(x1,z0+chamfer),(x1,z1-chamfer),(x1-chamfer,z1),(x0+chamfer,z1),(x0,z1-chamfer),(x0,z0+chamfer)])
 prism(prefix+'Floor',poly,16.26,16.5);prism(prefix+'Roof',poly,20.46,20.66,role='ivory_enamel',category='roof')
 # Faceted shell, rear outlook and contained entry enclosure; front/window
 # spans are built separately so no solid wall fills either actual opening.
 wall_line=poly.buffer(-.09,join_style=2)
 for j,(a0,a1)in enumerate(zip(list(wall_line.exterior.coords)[:-1],list(wall_line.exterior.coords)[1:])):
  if abs(a0[0]-a1[0])<1e-8 and min(abs(a0[0]-x0),abs(a0[0]-x1))<.11:continue
  segment(prefix+'Shell_'+str(j),[a0[0],18.48,a0[1]],[a1[0],18.48,a1[1]],3.96,.18,role='ivory_enamel',category='shell')
 front=x1 if west else x0;rear=x0 if west else x1;doorx=front+(-.175 if west else .175);yaw=math.pi/2 if west else-math.pi/2
 # Keep whole3.48m pocket profile received inside the historical polygon.
 frontlo,fronthi=(front-.18,front)if west else(front,front+.18)
 for j,(l,h)in enumerate([(z0+chamfer,cz-1.78),(cz+1.78,z1-chamfer)]):cube(prefix+'EntryWall_'+str(j),[frontlo,16.5,l],[fronthi,20.46,h],role='ivory_enamel',category='shell')
 cube(prefix+'EntryHeader',[frontlo,19.16,cz-1.78],[fronthi,20.46,cz+1.78],role='ivory_enamel',category='shell')
 rearlo,rearhi=(rear,rear+.18)if west else(rear-.18,rear)
 cube(prefix+'GardenDado',[rearlo,16.5,z0+chamfer],[rearhi,17.65,z1-chamfer],role='warm_walnut',category='shell')
 cube(prefix+'GardenGlass',[rearlo,17.65,z0+chamfer],[rearhi,19.75,z1-chamfer],role='hospitality_glass',category='window')
 cube(prefix+'GardenHead',[rearlo,19.75,z0+chamfer],[rearhi,20.46,z1-chamfer],role='ivory_enamel',category='shell')
 for k,z in enumerate([z0+chamfer,(z0+z1)/2,z1-chamfer]):cube(prefix+'WindowMullion_'+str(k),[rearlo-.025,17.6,z-.055],[rearhi+.025,19.8,z+.055],category='window_frame')
 # Source fixtures and a screened wet/service corner, separated from entry.
 bathx=(x1-4.2)if west else(x0+2.0);bathz=z0+.8
 cube(prefix+'BathScreen',[bathx+(1.45 if west else 0),16.5,bathz+3.05],[bathx+(2.9 if west else 1.45),19.0,bathz+3.23],role='ivory_enamel',category='privacy_screen')
 cube(prefix+'BathDogleg',[bathx+(2.72 if west else-.18),16.5,bathz],[bathx+(2.90 if west else 0),19.0,bathz+3.23],role='ivory_enamel',category='privacy_screen')
 cube(prefix+'VanityMountWall',[bathx+.74,16.5,bathz-.10],[bathx+.84,19.0,bathz+1.20],role='ivory_enamel',category='fixture_support')
 components=[{'catalogue_id':'AST-SAN-001','name':'Vanity','position':[bathx+.75,16.5,bathz+.6],'yaw':math.pi}, {'catalogue_id':'AST-SAN-002','name':'Toilet','position':[bathx+1.75,16.5,bathz+.65],'yaw':math.pi}, {'catalogue_id':'AST-SAN-003','name':'Shower','position':[bathx+.75,16.5,bathz+2.05],'yaw':0}]
 # Belongings/live-care cabinet; depth and rounded outline are authored, not
 # added berths. Care/molt and aquatic cleaner operation remain held.
 sx=x0+6.4
 cabinet=box(sx-.55,z0+.25,sx+.55,z0+.85).buffer(.14,quad_segs=2)
 prism(prefix+'BelongingsCabinet',cabinet,16.5,17.75,role='warm_walnut',category='storage')
 cube(prefix+'CareShelf',[sx-1.2,17.5,z0+.22],[sx+1.2,17.64,z0+.48],role='warm_walnut',category='storage')
 if west:
  restx=x0+3.65;restyaw=-math.pi/2
  for k,rz in enumerate([z0+2.0,z1-2.0]):
   components.append({'catalogue_id':'AST-RST-QC-001','name':'ReservedCocoon_'+str(k+1),'position':[restx,16.5,rz],'yaw':restyaw,'rest_slot_id':a['proposed_rest_slot_ids'][k]})
  components.extend([{'catalogue_id':'AST-FUR-002','name':'ReadingChair','position':[x0+6.7,16.5,z1-1.85],'yaw':math.pi/2},{'catalogue_id':'AST-FUR-003','name':'FolioTable','position':[x0+8.2,16.5,z1-1.8],'yaw':0}])
  cube(prefix+'CocoonPrivacyFin',[x0+1.5,16.5,cz-.07],[x0+5.25,18.55,cz+.07],role='warm_walnut',category='privacy_screen')
  pool=None;water=None;approach=[x0+6.2,16.5,cz]
 else:
  restyaw=math.pi/2;restz=z1-2.1;basins=[]
  for k,rx in enumerate([x0+4.4,x0+8.9]):
   components.append({'catalogue_id':'AST-RST-AQ-001','name':'ReservedAquaticRest_'+str(k+1),'position':[rx,16.5,restz],'yaw':restyaw,'rest_slot_id':a['proposed_rest_slot_ids'][k]})
   basin=box(rx-2.02,restz-1.56,rx+2.02,restz+1.56).buffer(.10,quad_segs=3)
   rim=basin.buffer(.09,join_style=2).difference(basin)
   prism(prefix+'AquaticBasinRim_'+str(k),rim,16.5,17.1,role='ivory_enamel',category='aquatic_basin')
   basins.append(basin)
  pool=unary_union(basins);water=None
  cube(prefix+'AquaticPrivacyFin',[x0+6.63,16.5,z1-3.7],[x0+6.77,18.25,z1-.75],role='ivory_enamel',category='privacy_screen')
  components.extend([{'catalogue_id':'AST-FUR-002','name':'DryTransferChair','position':[x1-2.0,16.5,z0+1.65],'yaw':-math.pi/2},{'catalogue_id':'AST-FUR-003','name':'DryActivityTable','position':[x1-3.5,16.5,z0+1.65],'yaw':0}])
  approach=[x0+4.4,16.5,z0+1.45]
 # Two source-bound ceiling lamps and a lower activity light; no ambient rescue.
 lights=[]
 for k,(lx,lz)in enumerate([(cx,cz),(front+(-2.0 if west else 2.0),cz),(rear+(1.0 if west else-1.0),z1-1.8)]):
  cube(prefix+'LampHousing_'+str(k),[lx-.32,20.15,lz-.32],[lx+.32,20.38,lz+.32],role='champagne_metal',category='light_source')
  cube(prefix+'LampLens_'+str(k),[lx-.27,20.12,lz-.27],[lx+.27,20.16,lz+.27],role='opal_glow',category='light_source');lights.append({'name':prefix+'LampLens_'+str(k),'at':[lx,20.10,lz]})
 for x in ([x0+.33,x1-.30]if west else[x0+.30,x1-.30]):
  for z in [z0+.4,z1-.4]:
   fx=-44.3 if not west and x==x0+.30 else x
   f={'x':fx,'z':z,'y':12,'owner':'D03_port_forward_staff_floor_0'if x<-55.2 else'D03_protected_crew_cover','wall_contact_allowed':x<-55.2,'room_index':idx};feet.append(f)
   cube(prefix+'Pier_'+str(len(feet)),[fx-.14,12,z-.14],[fx+.14,16.3,z+.14])
 for j,z in enumerate([z0+.4,z1-.4]):
  support_x=min(f['x']-.14 for f in feet if f['room_index']==idx and abs(f['z']-z)<1e-7)
  cube(prefix+'FloorCross_'+str(j),[min(x0-(3.65 if west else 0),support_x),15.98,z-.14],[x1+(0 if west else 3.65),16.3,z+.14])
 for x in [x0+.3,x1-.3]:cube(prefix+'Long_'+str(x),[x-.14,15.98,z0],[x+.14,16.3,z1])
 rooms.append({'allocation':a,'source_index':idx,'proposed_design_species':'Mantelids'if west else'Baelins','design_assignment_status':'ordinary architectural proposal, not recovered species/home assignment','species_ready':False,'profile_proposal':('garden_cocoon_folio'if not variant else'offset_quiet_care_retreat')if west else('aquatic_garden_bath'if not variant else'offset_aquatic_dry_gallery'),'parts':parts,'components':components,'floor_geometry':mapping(poly),'floor_y':16.5,'entry':{'origin':[doorx,16.5,cz],'yaw':yaw,'persistent_id':a['proposed_runtime_id']+':entry'},'approach_world':approach,'water_geometry':mapping(pool)if pool else None,'water_level_proposed':17.025 if pool else None,'lights':lights,'model_file':f'D04_PORT_FORWARD_HOME_{idx}_r001.glb','court_side':'west'if west else'east'})
for room in rooms:
 room['parts']=[p for p in room['parts']if '_FloorCross_'not in p['name']]
parts=[]
for j,z in enumerate([-444.8,-438.4]):cube('D04H3_SharedTransfer_'+str(j),[-62.6,15.98,z-.14],[-25.4,16.3,z+.14])
shared_parts=list(parts)
parts=[];courts=[]
for side,(x0,x1)in [('west',(-62.6,-58.95)),('east',(-29.05,-25.4))]:
 z0,z1=(-445.2,-438.0)if side!='commons'else(-375.9,-364.1);poly=box(x0,z0,x1,z1);prefix='D04HC3_'+side+'_' ;prism(prefix+'Floor',poly,16.26,16.5,category='court_floor');prism(prefix+'Roof',poly,20.46,20.66,role='ivory_enamel',category='roof')
 outside=x0 if side!='east'else x1;lo,hi=(outside,outside+.18)if side!='east'else(outside-.18,outside)
 cube(prefix+'PrivacyScreen',[lo,16.5,z0],[hi,18.45,z1],role='ivory_enamel',category='privacy_screen')
 cube(prefix+'GlassUpper',[lo,18.45,z0],[hi,20.46,z1],role='hospitality_glass',category='window')
 for j,z in enumerate([z0,z1]):cube(prefix+'End_'+str(j),[x0,16.5,z-.09],[x1,20.46,z+.09],role='ivory_enamel',category='shell')
 # Purposeful planted pockets, not random decoration; plants remain static
 # fictional garden assets and imply no life-support simulation.
 for j,z in enumerate([z0+1.5,(z0+z1)/2,z1-1.5]):
  px=outside+(1.05 if side=='west'else-1.05);bed=box(px-.45,z-.65,px+.45,z+.65).buffer(.10 if side=='west'else .2,quad_segs=3);prism(prefix+'Planter_'+str(j),bed,16.5,17.02,role='warm_stone',category='planter');prism(prefix+'Soil_'+str(j),bed.buffer(-.1),17.02,17.06,role='warm_walnut',category='planter')
  for k,(dx,dz,h)in enumerate([(-.18,-.26,.7),(.18,.15,1.05),(0,.38,.65)]):prism(prefix+f'LeafMass_{j}_{k}',box(px+dx-.22,z+dz-.27,px+dx+.22,z+dz+.27).buffer(.08 if side=='west'else .18,quad_segs=2),17.05,17.05+h,role='foliage',category='plant_detail');parts[-1]['runtime_collision']=False
 courts.append({'side':side,'geometry':mapping(poly),'floor_area_m2':poly.area,'public_access':False,'staff_horticultural_service_held':True,'outlook':'physical contained planted court; no hull window or occupied-volume view'})
 # Missing-only court support spans meet selected room floor cross beams or
 # original commons transfer members. No new imaginary lower slab is used.
 zs=[-422.6,-416.2,-415.2,-408.8]if side!='commons'else[-373.5,-367.5]
 if side=='commons':
  for j,z in enumerate(zs):cube(prefix+'Transfer_'+str(j),[x0,15.98,z-.12],[x1+.2,16.3,z+.12])
commonsparts=shared_parts+list(parts);commons_components=[]
# Preserve all1000 envelope polygons; only the selected4 next allocation interiors
# receive room geometry and courts never consume any accommodation allocation.
records=json.load(open(R/inputs[9]))['records']
for court in courts:
 g=Polygon(court['geometry']['coordinates'][0])
 for a in records:assert g.intersection(box(*[a['allocation_x'][0],a['allocation_z'][0],a['allocation_x'][1],a['allocation_z'][1]])).area<1e-7,(court['side'],a['source_envelope_index'])
crew=json.load(open(R/inputs[10]))
for f in feet:
 toe=box(f['x']-.14,f['z']-.14,f['x']+.14,f['z']+.14)
 for a in crew['instances']:
  e=a['source_envelope'];assert toe.intersection(box(e['x'][0],e['z'][0],e['x'][1],e['z'][1])).area<1e-7,('crew',f,a)
removed=[];successor=[]
previous=json.load(open(R/'BlenderCatalogue/assets/d04_port_forward_homes_second_20261010/RUNTIME_PLAN.json'))
for p in previous['guard_successor_parts']:
 z0=min(v[2]for v in p['verts']);z1=max(v[2]for v in p['verts'])
 if not(z0<=-445.2 and z1>-438.0):continue
 removed.append({'name':p['name'],'preimage':p});low,high=-441.6-1.82,-441.6+1.82
 for j,(l,h)in enumerate([(z0,low),(high,z1)]):
  part=copy.deepcopy(p);part['name']='D04H3_Guard_'+str(len(removed))+'_'+str(j)
  for v in part['verts']:v[2]=l if abs(v[2]-z0)<1e-6 else h
  successor.append(part)
assert len(removed)==6 and len(successor)==12
P={'schema':'astraea.d04_port_forward_homes_third.v1','base_commit':base,'house_id':old['house_id'],'commons_programme_key':old['commons_programme_key'],'all_twenty_allocations_unchanged':all_units,'rooms':rooms,'selected_source_indices':[976,988],'new_units':0,'new_rest_places':0,'proposed_rest_reservations_preserved':4,'prior_physical_proposals_preserved':8,'physical_proposals_after_batch':10,'species_ready_rooms':0,'sources':list(sources.values()),'source_pins':{p:sha(R/p)for p in inputs},'foundation_feet':feet,'commons_parts':commonsparts,'commons_components':commons_components,'courts':courts,'guard_preimages':removed,'guard_successor_parts':successor,'commons_frame_preimages':[p for p in old['parts']if p['name']in['D04PF_CommonsTransferWest_-373.5','D04PF_CommonsTransfer_-367.5','D04PF_BayLong_-69.7']],'connection_accepted':False,'open_room_entries':False,'limits':['Two scoped double-home proposals with four exact reserved rest places, not recovered identities/occupancy/species compatibility','All20 allocation polygons/15 single5double25proposedrests and six-neighborhood distinction remain unchanged','Aquatic water/bath geometry and quiet cocoons are physical architecture; biological parameters, acoustic attenuation, pose/rig/save/cleaner/stock operation held','Private gardens supported from actual D03 slab/piers and retained receiving frame; primary load/cantilever sizing held','Full20-room neighborhood/complete original commons, other5D04 neighborhoods, D17 rooms/private outlook and all eight groups remain construction','Existing public/staff connections and lift blankD04-D07 preserved; cart-safe service vertical remains unfinished','Ordinary Godot/CRT/hardware acceptance remains held']}
P['frame_joint_preimages']=[q for q in old['parts']if q['name']in['D04PF_StreetTransfer_0','D04PF_BearingPier_08','D04PF_BearingPier_13','D04PF_TransferRaker_0','D04PF_StreetLong_-45.8','D04PF_StreetLong_-42.2']]
assert len(P['frame_joint_preimages'])==6
for room in P['rooms']:
 a=room['allocation'];cz=room['entry']['origin'][2];west=room['court_side']=='west'
 room['outlook_world']=[a['allocation_x'][0]+1.0,16.5,cz]if west else[a['allocation_x'][1]-1.35,16.5,a['allocation_z'][0]+1.5]
 room['profile_proposal']='paired_private_quiet_cocoon_gallery'if west else'paired_aquatic_garden_and_dry_transfer'
for r in P['rooms']:
 r['rest_approach_worlds']=[{'rest_slot_id':b['rest_slot_id'],'position':[b['position'][0]+2.35,16.5,b['position'][2]]if r['court_side']=='west'else[b['position'][0],16.5,r['allocation']['allocation_z'][0]+1.45],'operational_access_verified':False}for b in r['components']if'rest_slot_id'in b]
P['remaining_live_interiors_before_adoption']=12;P['remaining_live_reserved_rests_before_adoption']=17;P['remaining_after_scoped_runtime_gate']={'interiors':10,'reserved_rests':13}
(W/'PLAN.json').write_text(json.dumps(P,indent=2)+'\n');print(json.dumps({'rooms':len(rooms),'source_pins':len(P['source_pins']),'new_feet':len(feet),'guard_preimages':len(removed),'court_floor_m2':sum(c['floor_area_m2']for c in courts)}))
