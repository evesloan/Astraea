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
base='77d8897b8c6e30a69c04f9af2c4386e47c466b8c'
prior='BlenderCatalogue/assets/d04_port_forward_receiving_20261010'
old=json.load(open(R/prior/'PLAN.json'));all_units=old['units'];assert len(all_units)==20 and sum(u['proposed_rest_place_count']for u in all_units)==25
catalogue=json.load(open(R/'BlenderCatalogue/catalogue_manifest.json'))
source_ids=['AST-RST-QC-001','AST-RST-AQ-001','AST-SAN-001','AST-SAN-002','AST-SAN-003','AST-FUR-001','AST-FUR-002','AST-FUR-003']
sources={i:next(a for a in catalogue['assets']if a['catalogue_id']==i)for i in source_ids}
inputs=[prior+'/PLAN.json',prior+'/D04PortForwardReceiving.blend','Game/assets/models/D04_PORT_FORWARD_RECEIVING_r001.glb','Game/assets/models/D04_STAFF_WALL_PORTAL_PATCH_r001.glb','Game/data/architecture/D04_PORT_FORWARD_RECEIVING.json','Game/data/spatial_layout.json','BlenderCatalogue/catalogue_manifest.json','Game/docs/master_source/MASTER_CURRENT_APPLICATION.json','Game/docs/master_source/MASTER_FULL_CONTENT_INDEX.json','BlenderCatalogue/assets/residential_hotels/central_room_families_20261007_r001/residential-neighborhood-audit-20261007/ALL_1000_NEIGHBORHOOD_CROSSWALK.json','BlenderCatalogue/assets/group3_crew_service_20261009/source/CREW_BANK_PLACEMENTS_PROPOSAL.json','BlenderCatalogue/references/residential_20261004/Guest_suite_corridor_8077.jpg','BlenderCatalogue/references/aquatic/image(20261001-035517).png','BlenderCatalogue/references/intimate/image(20261002-000722).png','Game/assets/models/crew_home/SharedCrewHome.glb','Game/data/architecture/SHARED_CREW_HOME.json','Game/scripts/shared_crew_home.gd']
for a in sources.values():inputs.extend(['BlenderCatalogue/'+a['source'],'BlenderCatalogue/'+a['export']])
for i in ['AST-DOR-002','AST-DOR-001']:
 a=next(a for a in catalogue['assets']if a['catalogue_id']==i);inputs.extend(['BlenderCatalogue/'+a['source'],'Game/assets/models/'+i+'.glb'])
rooms=[];feet=[]
for idx in [880,892,904,916]:
 a=copy.deepcopy(next(u for u in all_units if u['source_envelope_index']==idx));assert a['proposed_rest_place_count']==1
 west=idx in [880,904];variant=idx in [904,916];x0,x1=a['allocation_x'];z0,z1=a['allocation_z'];cx=(x0+x1)/2;cz=(z0+z1)/2;prefix='D04H'+str(idx)+'_';parts=[]
 # Exact allocation preserved; architectural chamfers change the authored shell.
 chamfer=.65 if not variant else 1.0
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
 sx=(x0+5.2)if west else(x0+4.4)
 cabinet=box(sx-.55,z1-.85,sx+.55,z1-.25).buffer(.14,quad_segs=2)
 prism(prefix+'BelongingsCabinet',cabinet,16.5,17.75,role='warm_walnut',category='storage')
 cube(prefix+'CareShelf',[sx-1.2,17.5,z1-.48],[sx+1.2,17.64,z1-.22],role='warm_walnut',category='storage')
 if west:
  restx=x0+3.1;restz=(cz-.55)if not variant else(cz+.65);restyaw=-math.pi/2
  components.append({'catalogue_id':'AST-RST-QC-001','name':'ReservedCocoon','position':[restx,16.5,restz],'yaw':restyaw,'rest_slot_id':a['proposed_rest_slot_ids'][0]})
  components.extend([{'catalogue_id':'AST-FUR-002','name':'ReadingChair','position':[x0+(6.8 if variant else 1.75),16.5,z1-1.85],'yaw':math.pi/2},{'catalogue_id':'AST-FUR-003','name':'FolioTable','position':[x0+(8.3 if variant else 3.3),16.5,z1-1.8],'yaw':0}])
  # Curved visual absorption screen separates cocoon from entry/care; source
  # cocoon remains open at the true approach. No acoustic simulation claim.
  path=Polygon([(x0+5.8,z0+.9),(x0+5.8,cz-2.0),(x0+5.25,cz-1.55),(x0+4.9,cz-1.45)]).buffer(.12,quad_segs=2)
  prism(prefix+'QuietWing',path,16.5,19.1,role='warm_walnut',category='privacy_screen')
  pool=None;water=None;approach=[restx+2.35,16.5,restz]
 else:
  restx=x1-3.4;restz=(cz-.2)if not variant else(cz+.45);restyaw=math.pi/2
  components.append({'catalogue_id':'AST-RST-AQ-001','name':'ReservedAquaticRest','position':[restx,16.5,restz],'yaw':restyaw,'rest_slot_id':a['proposed_rest_slot_ids'][0]})
  # Shaped, real contained aquatic basin with a dry approach around it.
  pool=box(restx-2.25,restz-1.85,restx+2.25,restz+1.85).buffer(.28,quad_segs=3)
  outer=pool.buffer(.15,join_style=2);rim=outer.difference(pool)
  prism(prefix+'AquaticBasinRim',rim,16.5,17.1,role='ivory_enamel',category='aquatic_basin')
  water=pool.difference(box(restx-1.9,restz-1.5,restx+1.9,restz+1.5))
  # Source cradle provides its own retained water surface; added water occupies
  # the receiving basin outside the original cradle envelope.
  for j,g in enumerate([water]if water.geom_type=='Polygon'else water.geoms):
   prism(prefix+'Water_'+str(j),g,17.02,17.025,role='water',category='water');parts[-1]['runtime_collision']=False
  components.extend([{'catalogue_id':'AST-FUR-002','name':'DryTransferChair','position':[x0+2.5,16.5,z1-1.4],'yaw':math.pi/2},{'catalogue_id':'AST-FUR-003','name':'DryActivityTable','position':[x0+4.0,16.5,z1-1.35],'yaw':0}])
  approach=[restx-3.6,16.5,restz]
 # Two source-bound ceiling lamps and a lower activity light; no ambient rescue.
 lights=[]
 for k,(lx,lz)in enumerate([(cx,cz),(front+(-2.0 if west else 2.0),cz),(rear+(1.0 if west else-1.0),z1-1.8)]):
  cube(prefix+'LampHousing_'+str(k),[lx-.32,20.15,lz-.32],[lx+.32,20.38,lz+.32],role='champagne_metal',category='light_source')
  cube(prefix+'LampLens_'+str(k),[lx-.27,20.12,lz-.27],[lx+.27,20.16,lz+.27],role='opal_glow',category='light_source');lights.append({'name':prefix+'LampLens_'+str(k),'at':[lx,20.10,lz]})
 for x in ([x0+.33,x1-.30]if west else[x0+.30,x1-.30]):
  for z in [z0+.4,z1-.4]:
   fx=-44.3 if idx==916 and x==x0+.30 and z==z0+.4 else x
   f={'x':fx,'z':z,'y':12,'owner':'D03_port_forward_staff_floor_0'if x<-55.2 else'D03_protected_crew_cover','wall_contact_allowed':x<-55.2,'room_index':idx};feet.append(f)
   cube(prefix+'Pier_'+str(len(feet)),[fx-.14,12,z-.14],[fx+.14,16.3,z+.14])
 for j,z in enumerate([z0+.4,z1-.4]):
  support_x=min(f['x']-.14 for f in feet if f['room_index']==idx and abs(f['z']-z)<1e-7)
  cube(prefix+'FloorCross_'+str(j),[min(x0-(3.65 if west else 0),support_x),15.98,z-.14],[x1+(0 if west else 3.65),16.3,z+.14])
 for x in [x0+.3,x1-.3]:cube(prefix+'Long_'+str(x),[x-.14,15.98,z0],[x+.14,16.3,z1])
 rooms.append({'allocation':a,'source_index':idx,'proposed_design_species':'Mantelids'if west else'Baelins','design_assignment_status':'ordinary architectural proposal, not recovered species/home assignment','species_ready':False,'profile_proposal':('garden_cocoon_folio'if not variant else'offset_quiet_care_retreat')if west else('aquatic_garden_bath'if not variant else'offset_aquatic_dry_gallery'),'parts':parts,'components':components,'floor_geometry':mapping(poly),'floor_y':16.5,'entry':{'origin':[doorx,16.5,cz],'yaw':yaw,'persistent_id':a['proposed_runtime_id']+':entry'},'approach_world':approach,'water_geometry':mapping(pool)if pool else None,'water_level_proposed':17.025 if pool else None,'lights':lights,'model_file':f'D04_PORT_FORWARD_HOME_{idx}_r001.glb','court_side':'west'if west else'east'})
parts=[];courts=[]
for side,(x0,x1)in [('west',(-62.6,-58.95)),('east',(-29.05,-25.4)),('commons',(-73,-70))]:
 z0,z1=(-423,-408.4)if side!='commons'else(-375.9,-364.1);poly=box(x0,z0,x1,z1);prefix='D04HC_'+side+'_' ;prism(prefix+'Floor',poly,16.26,16.5,category='court_floor');prism(prefix+'Roof',poly,20.46,20.66,role='ivory_enamel',category='roof')
 outside=x0 if side!='east'else x1;lo,hi=(outside,outside+.18)if side!='east'else(outside-.18,outside)
 cube(prefix+'PrivacyScreen',[lo,16.5,z0],[hi,18.45,z1],role='ivory_enamel',category='privacy_screen')
 cube(prefix+'GlassUpper',[lo,18.45,z0],[hi,20.46,z1],role='hospitality_glass',category='window')
 for j,z in enumerate([z0,z1]):cube(prefix+'End_'+str(j),[x0,16.5,z-.09],[x1,20.46,z+.09],role='ivory_enamel',category='shell')
 # Purposeful planted pockets, not random decoration; plants remain static
 # fictional garden assets and imply no life-support simulation.
 for j,z in enumerate([z0+1.5,(z0+z1)/2,z1-1.5]):
  px=outside+(1.05 if side!='east'else-1.05);bed=box(px-.45,z-.65,px+.45,z+.65).buffer(.2,quad_segs=3);prism(prefix+'Planter_'+str(j),bed,16.5,17.02,role='warm_stone',category='planter');prism(prefix+'Soil_'+str(j),bed.buffer(-.1),17.02,17.06,role='warm_walnut',category='planter')
  for k,(dx,dz,h)in enumerate([(-.18,-.26,.7),(.18,.15,1.05),(0,.38,.65)]):prism(prefix+f'LeafMass_{j}_{k}',box(px+dx-.22,z+dz-.27,px+dx+.22,z+dz+.27).buffer(.18,quad_segs=2),17.05,17.05+h,role='foliage',category='plant_detail');parts[-1]['runtime_collision']=False
 courts.append({'side':side,'geometry':mapping(poly),'floor_area_m2':poly.area,'public_access':False,'staff_horticultural_service_held':True,'outlook':'physical contained planted court; no hull window or occupied-volume view'})
 # Missing-only court support spans meet selected room floor cross beams or
 # original commons transfer members. No new imaginary lower slab is used.
 zs=[-422.6,-416.2,-415.2,-408.8]if side!='commons'else[-373.5,-367.5]
 if side=='commons':
  for j,z in enumerate(zs):cube(prefix+'Transfer_'+str(j),[x0,15.98,z-.12],[x1+.2,16.3,z+.12])
commonsparts=[]
for q in parts:commonsparts.append(q)
parts=[]
# Fuller enclosure and two sheltered activity edges within the original84m²
# commons bay. Preserve both registered benches, cabinet and staff route.
for side,z in [('North',-375.91),('South',-364.09)]:
 cube('D04Commons_'+side+'Dado',[-69.85,16.5,z-.085],[-63.15,17.6,z+.085],role='warm_walnut',category='shell')
 cube('D04Commons_'+side+'Glass',[-69.85,17.6,z-.085],[-63.15,19.8,z+.085],role='hospitality_glass',category='window')
 cube('D04Commons_'+side+'Head',[-69.85,19.8,z-.085],[-63.15,20.46,z+.085],role='ivory_enamel',category='shell')
cube('D04Commons_GardenGlass',[-69.94,17.8,-375.8],[-69.78,20.46,-364.2],role='hospitality_glass',category='window')
for j,(z0,z1)in enumerate([(-375.91,-372.6),(-367.2,-364.09)]):cube('D04Commons_EntryPier_'+str(j),[-63.20,16.5,z0],[-63.04,20.46,z1],role='ivory_enamel',category='shell')
for j,z in enumerate([-373.8,-366.2]):
 table=box(-66.75,z-.38,-65.25,z+.38).buffer(.18,quad_segs=3);prism('D04Commons_ActivityTop_'+str(j),table,17.18,17.28,role='warm_walnut',category='activity');cube('D04Commons_ActivityStem_'+str(j),[-66.1,16.5,z-.17],[-65.9,17.18,z+.17],category='activity')
commons_components=[{'catalogue_id':'AST-FUR-002','name':'CommonsNorthChair','position':[-64.6,16.5,-374.3],'yaw':-math.pi/2},{'catalogue_id':'AST-FUR-002','name':'CommonsSouthChair','position':[-64.6,16.5,-365.7],'yaw':-math.pi/2}]
commonsparts.extend(parts)
# Preserve all1000 envelope polygons; only the selected4 allocation interiors
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
for name in ['D04PF_UpperGuard_15','D04PF_UpperGuard_17']:
 for suffix in ['', '_Base','_Cap']:
  p=next(p for p in old['parts']if p['name']==name+suffix);removed.append({'name':p['name'],'preimage':p})
  z0=min(v[2]for v in p['verts']);z1=max(v[2]for v in p['verts']);ranges=[(z0,z1)]
  for center in [-412,-419.4]:
   low,high=center-1.82,center+1.82;new=[]
   for l,h in ranges:
    if h<=low or l>=high:new.append((l,h))
    else:
     if l<low:new.append((l,low))
     if h>high:new.append((high,h))
   ranges=new
  for j,(l,h)in enumerate(ranges):
   part=copy.deepcopy(p);part['name']='D04H_GuardSuccessor_'+name+suffix+'_'+str(j)
   for v in part['verts']:v[2]=l if abs(v[2]-z0)<1e-6 else h
   successor.append(part)
P={'schema':'astraea.d04_port_forward_homes_first.v1','base_commit':base,'house_id':old['house_id'],'commons_programme_key':old['commons_programme_key'],'all_twenty_allocations_unchanged':all_units,'rooms':rooms,'selected_source_indices':[880,892,904,916],'new_units':0,'new_rest_places':0,'proposed_rest_reservations_preserved':4,'species_ready_rooms':0,'sources':list(sources.values()),'source_pins':{p:sha(R/p)for p in inputs},'foundation_feet':feet,'commons_parts':commonsparts,'commons_components':commons_components,'courts':courts,'guard_preimages':removed,'guard_successor_parts':successor,'commons_frame_preimages':[p for p in old['parts']if p['name']in['D04PF_CommonsTransferWest_-373.5','D04PF_CommonsTransfer_-367.5','D04PF_BayLong_-69.7']],'connection_accepted':False,'open_room_entries':False,'limits':['Four scoped physical home proposals, not recovered identities/occupancy/species compatibility','All20 allocation polygons/15 single5double25proposedrests and six-neighborhood distinction remain unchanged','Aquatic water/bath geometry and quiet cocoons are physical architecture; biological parameters, acoustic attenuation, pose/rig/save/cleaner/stock operation held','Private gardens supported from actual D03 slab/piers and retained receiving frame; primary load/cantilever sizing held','Full20-room neighborhood/complete original commons, other5D04 neighborhoods, D17 rooms/private outlook and all eight groups remain construction','Existing public/staff connections and lift blankD04-D07 preserved; cart-safe service vertical remains unfinished','Ordinary Godot/CRT/hardware acceptance remains held']}
(W/'PLAN.json').write_text(json.dumps(P,indent=2)+'\n');print(json.dumps({'rooms':len(rooms),'source_pins':len(P['source_pins']),'new_feet':len(feet),'guard_preimages':len(removed),'court_floor_m2':sum(c['floor_area_m2']for c in courts)}))
