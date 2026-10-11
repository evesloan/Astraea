from pathlib import Path
import json,copy,hashlib,math,ast,subprocess
from shapely.geometry import box,Polygon,shape,mapping
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
from shapely import constrained_delaunay_triangles
W=Path(__file__).resolve().parent;R=W.parents[2];read=lambda f:json.load(open(R/f));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();canon=lambda a:hashlib.sha256(json.dumps(a,sort_keys=True,separators=(',',':')).encode()).hexdigest()
source_path='Game/data/architecture/D04_STARBOARD_AFT_NEIGHBORHOOD.json';S=read(source_path);CO=read('Game/data/architecture/D04_STARBOARD_FULL_COMMONS.json');cross='BlenderCatalogue/assets/residential_hotels/central_room_families_20261007_r001/residential-neighborhood-audit-20261007/ALL_1000_NEIGHBORHOOD_CROSSWALK.json';units=[a for a in read(cross)['records']if a['house']=='starboard_central_lower_habitat_house'];assert len(units)==20 and sum(a['proposed_rest_place_count']for a in units)==25
transform=lambda v:[v[0]+40,v[1],v[2]-370]
def geom(g):
 if g is None:return None
 def walk(v):return[v[0]+40,v[1]-370]if isinstance(v[0],(int,float))else[walk(a)for a in v]
 return{**g,'coordinates':walk(g['coordinates'])}
def part(p,prefix,oldprefix=''):
 a=copy.deepcopy(p);a['name']=prefix+p['name'].removeprefix(oldprefix);a['verts']=[transform(v)for v in p['verts']];a.pop('actual_foundation_preimage',None)
 lo=[min(v[i]for v in a['verts'])for i in range(3)];hi=[max(v[i]for v in a['verts'])for i in range(3)]
 if a['category']=='frame'and hi[0]-lo[0]<.5 and hi[2]-lo[2]<.5 and lo[1]<16 and hi[1]>16:
  for v in a['verts']:
   if v[1]==lo[1]:v[1]=12
 return a
rooms=[];mapping_records=[]
for u in units:
 template=next(r for r in S['rooms']if all(abs(u['allocation_x'][i]-(r['allocation']['allocation_x'][i]+40))<1e-7 and abs(u['allocation_z'][i]-(r['allocation']['allocation_z'][i]-370))<1e-7 for i in [0,1]));assert template['allocation']['proposed_rest_place_count']==u['proposed_rest_place_count'];r=copy.deepcopy(template);idx=u['source_envelope_index'];r.update(allocation=u,source_index=idx,model_file=f'D04_STARBOARD_CENTRAL_HOME_{idx}_r001.glb',source_template={'source_index':template['source_index'],'source_sha256':canon(template),'rigid_translation_xyz':[40,0,-370]},species_ready=False);r['parts']=[part(a,f'SC{idx}_',f'SA{template["source_index"]}_')for a in template['parts']]
 for k in ['model_sha256','mesh_count','collision_policy','care_access_geometry_verified']:r.pop(k,None)
 slots=dict(zip(template['allocation']['proposed_rest_slot_ids'],u['proposed_rest_slot_ids']))
 for b in r['components']:
  b['position']=transform(b['position'])
  if 'rest_slot_id'in b:b['rest_slot_id']=slots[b['rest_slot_id']]
 for k in ['approach_world','outlook_world','care_station_world']:
  if k in r:r[k]=transform(r[k])
 for k in ['entry_to_care_waypoints','rest_approach_waypoints']:
  if k in r:r[k]=[transform(v)for v in r[k]]
 for k in ['floor_geometry','water_geometry']:r[k]=geom(r[k])
 r['entry']['origin']=transform(r['entry']['origin']);r['entry']['persistent_id']=u['proposed_runtime_id']+':entry'
 for a in r['lights']:a['name']=f'SC{idx}_'+a['name'].split('_',1)[1];a['at']=transform(a['at'])
 for a in r.get('rest_approach_worlds',[]):a['position']=transform(a['position']);a['rest_slot_id']=slots[a['rest_slot_id']]
 assert shape(r['floor_geometry']).difference(box(u['allocation_x'][0],u['allocation_z'][0],u['allocation_x'][1],u['allocation_z'][1])).area<1e-7
 rooms.append(r);mapping_records.append({'target_index':idx,'compatible_source_template_index':template['source_index'],'rests':u['proposed_rest_place_count'],'rigid_translation_xyz':[40,0,-370]})
courts=[{**a,'geometry':geom(a['geometry'])}for a in S['courts']];assert len(courts)==10
courtparts=[part(a,'SCK_','SAK_')for a in S['assemblies']['CombinedStructure']if a['name'].startswith('SAK_')];guard_corrections=[];new=[]
for q in courtparts:
 lo=[min(v[i]for v in q['verts'])for i in range(3)];hi=[max(v[i]for v in q['verts'])for i in range(3)];cuts=[]
 if q['category']in ['guard','guard_successor']and hi[0]-lo[0]<.3 and hi[2]-lo[2]>1:
  x=(lo[0]+hi[0])/2
  if abs(x-81.95)<.2:cuts+=[(-33.7,-30.3),(30.3,33.7)]
  if abs(x-81.95)<.2 or abs(x-86.05)<.2:cuts+=[(-3,3)]
 spans=[(lo[2],hi[2])]
 for a,b in cuts:
  out=[]
  for z0,z1 in spans:
   if b<=z0 or a>=z1:out.append((z0,z1))
   else:
    if z0<a:out.append((z0,a))
    if b<z1:out.append((b,z1))
  spans=out
 if spans==[(lo[2],hi[2])]:new.append(q);continue
 successors=[]
 for i,(z0,z1)in enumerate(spans):
  a=copy.deepcopy(q);a['name']=q['name']+'_Join_'+str(i)
  for v in a['verts']:v[2]=z0 if v[2]==lo[2]else z1
  new.append(a);successors.append(a)
 guard_corrections.append({'exact_translated_preimage':q,'successors':successors,'cuts':cuts,'reason':'Open only owned guards at new supported public branches/lateral commons link; do not cut unbacked outer street edge.'})
courtparts=new
parts=[];faces=[[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]];text=(R/'BlenderCatalogue/assets/d04_port_forward_receiving_20261010/prepare.py').read_text()
for n in ast.parse(text).body:
 if isinstance(n,ast.FunctionDef)and n.name in ['add','cube','prism','segment']:exec(compile(ast.get_source_segment(text,n),'<reviewed existing architectural helpers>','exec'))
single_prism=prism
def prism(name,g,*args,**kw):
 if g.geom_type=='MultiPolygon':
  for i,q in enumerate(g.geoms):single_prism(name+'_'+str(i),q,*args,**kw)
 else:single_prism(name,g,*args,**kw)
west=Polygon([(63,-3),(66,-3),(66,-8),(70,-12),(79,-12),(81,-10),(81,10),(79,12),(70,12),(66,8),(66,3),(63,3)])
east=Polygon([(88,-9),(91,-12),(95,-9),(95,9),(91,12),(88,9)]);link=box(81,-3,88,3);floor=unary_union([west,east,link]);receiving=unary_union([box(81.95,-75.4,86.05,75.4),box(50.8,-33.7,84,-30.3),box(50.8,30.3,84,33.7),box(50.8,-3,63,3)]).difference(floor)
baseline=unary_union([Polygon(t)for a in read('Game/data/generated/structural_meshes.json')['regions']if a['floor_y']==16.5 for t in a['triangles']]);overlap=receiving.intersection(baseline).area;receiving=receiving.difference(baseline)
prism('SC_ReceivingFloor',receiving,16.26,16.5);prism('SC_ReceivingRoof',receiving,20.45,20.69,role='ivory_enamel',category='roof')
for x in [82.15,85.85]:
 for i,z in enumerate([-75.1,-62,-49,-35.5,-22,-8,8,22,35.5,49,62,75.1]):cube(f'SC_StreetBearing_{x}_{i}',[x-.12,12,z-.12],[x+.12,16.3,z+.12]);cube(f'SC_StreetRoofPier_{x}_{i}',[x-.12,16.5,z-.12],[x+.12,20.45,z+.12],'warm_walnut','roof_pier')
 for i,(z0,z1)in enumerate([(-75.4,-3),(3,75.4)]):cube(f'SC_StreetLong_{x}_{i}',[x-.12,15.98,z0],[x+.12,16.3,z1])
for j,z in enumerate([-33.55,-30.45,30.45,33.55,-2.82,2.82]):
 x1=84 if abs(z)>10 else 63
 cube(f'SC_ArrivalBeam{j}',[51,15.98,z-.12],[x1,16.3,z+.12]);cube(f'SC_ArrivalRoofBeam{j}',[51,20.15,z-.12],[x1,20.45,z+.12])
 for i,x in enumerate([55,65,77]if abs(z)>10 else[55,61]):cube(f'SC_ArrivalBearing{j}_{i}',[x-.12,12,z-.12],[x+.12,16.3,z+.12]);cube(f'SC_ArrivalRoofPier{j}_{i}',[x-.12,16.5,z-.12],[x+.12,20.45,z+.12],'warm_walnut','roof_pier')
for z in [-33.7,-30.3,30.3,33.7]:cube(f'SC_ArrivalGuard{z}',[51,16.5,z-.04],[81.95,17.68,z+.04],'hospitality_glass','guard')
for z in [-3,3]:cube(f'SC_CentralArrivalGuard{z}',[51,16.5,z-.04],[63,17.68,z+.04],'hospitality_glass','guard')
for z in [-75.4,75.4]:cube(f'SC_StreetEndGuard{z}',[81.95,16.5,z-.04],[86.05,17.68,z+.04],'hospitality_glass','guard')
lights=[]
def lamp(name,x,y,z,staff=False):
 cube(name+'_Housing',[x-.32,y-.30,z-.26],[x+.32,y,z+.26],'champagne_metal','fitting');cube(name+'_Lens',[x-.27,y-.33,z-.21],[x+.27,y-.30,z+.21],'opal_glow','light_fixture');lights.append({'name':name+'_Lens','at':[x,y-.35,z],'staff':staff})
for i,z in enumerate([-72,-57,-42,-26,-10,10,26,42,57,72]):lamp('SC_StreetLamp'+str(i),84,20.45,z)
for i,(x,z)in enumerate([(57,-32),(73,-32),(57,32),(73,32),(57,0)]):lamp('SC_ArrivalLamp'+str(i),x,20.45,z)
assemblies={'Receiving':parts+courtparts};parts=[]
prism('SCC_CommonsFloor',floor,16.26,16.5);prism('SCC_CommonsRoof',west.union(link),20.45,20.69,role='ivory_enamel',category='roof');prism('SCC_QuietLowRoof',east,19.25,19.49,role='warm_walnut',category='roof');prism('SCC_ServiceLowCanopy',west.intersection(box(66.7,-11,78.2,-3.5)),19.15,19.37,role='staff_panel',category='roof')
# The west social room and low east garden bay are connected across the home street, not a mirrored salon.
for label,g,height in [('West',west,20.45),('East',east,19.25)]:
 for i,(a,b)in enumerate(zip(list(g.exterior.coords),list(g.exterior.coords)[1:])):
  spans=[(a,b)]
  if a[0]==b[0]and a[0]in[63,81,88]:
   if a[0]==63:continue
   spans=[((a[0],min(a[1],b[1])),(a[0],-3)),((a[0],3),(a[0],max(a[1],b[1])))]
  for j,(a,b)in enumerate(spans):
   if abs(a[0]-b[0])+abs(a[1]-b[1])<1e-5:continue
   segment(f'SCC_{label}Dado{i}_{j}',[a[0],17.05,a[1]],[b[0],17.05,b[1]],1.1,.16,'warm_walnut','wall');glass_height=height-18.1;segment(f'SCC_{label}Glass{i}_{j}',[a[0],17.6+glass_height/2,a[1]],[b[0],17.6+glass_height/2,b[1]],glass_height,.16,'hospitality_glass','window');segment(f'SCC_{label}Head{i}_{j}',[a[0],height-.25,a[1]],[b[0],height-.25,b[1]],.5,.16,'ivory_enamel','wall')
for z in [-3,3]:cube(f'SCC_LateralLinkGuard{z}',[81,16.5,z-.04],[88,17.66,z+.04],'hospitality_glass','guard')
# No guard crosses the north/south home street at the link edge.
for q in list(parts):
 if q['name'].startswith('SCC_LateralLinkGuard'):
  parts.remove(q)
  for j,(x0,x1)in enumerate([(81,81.95),(86.05,88)]):cube(q['name']+'_'+str(j),[x0,16.5,q['verts'][0][2]],[x1,17.66,q['verts'][4][2]],'hospitality_glass','guard')
for name,lo,hi in [('StockWest',[66.7,16.5,-9],[66.86,19.15,-3.5]),('ServiceDivider',[72.2,16.5,-10.2],[72.36,19.15,-3.5]),('ReturnEast',[78.04,16.5,-10.2],[78.2,19.15,-3.5]),('ServiceNorth',[69.4,16.5,-10.4],[78.2,19.15,-10.2]),('StockFrontL',[66.86,16.5,-3.66],[68,19.15,-3.5]),('StockFrontR',[71.5,16.5,-3.66],[72.2,19.15,-3.5]),('ReturnFrontL',[72.36,16.5,-3.66],[74,19.15,-3.5]),('ReturnFrontR',[76.5,16.5,-3.66],[78.2,19.15,-3.5]),('StockHead',[68,18.8,-3.66],[71.5,19.15,-3.5]),('ReturnHead',[74,18.8,-3.66],[76.5,19.15,-3.5])]:cube('SCC_'+name,lo,hi,'staff_panel','wall')
stock=lambda v:[v[0]-1.2,v[1],v[2]+351]
for a in CO['parts']:
 if 'StockShelf'in a['name']:q=copy.deepcopy(a);q['name']='SCC_'+a['name'];q['verts']=[stock(v)for v in a['verts']];parts.append(q)
for i,x in enumerate([74,75.4]):
 cube(f'SCC_ReturnBinFoot{i}',[x-.3,16.5,-8.3],[x+.3,16.62,-7.5],'warm_walnut','fitting');cube(f'SCC_ReturnBinShell{i}',[x-.27,16.62,-8.27],[x+.27,17.5,-7.53],'staff_panel','closed_return');cube(f'SCC_ReturnBinLid{i}',[x-.3,17.5,-8.3],[x+.3,17.6,-7.5],'champagne_metal','closed_return')
for i,z in enumerate([-6,0,6]):
 cube(f'SCC_PlantedPlinth{i}',[94,16.5,z-.8],[94.8,17.1,z+.8],'warm_walnut','planter');cube(f'SCC_PlantedSoil{i}',[94.07,17.1,z-.73],[94.73,17.16,z+.73],'warm_stone','plant_detail')
 for j,dy in enumerate([0,.55,1.1]):cube(f'SCC_LeafMass{i}_{j}',[94.15-j*.03,17.16+dy,z-.5+j*.07],[94.65+j*.03,17.71+dy,z+.5-j*.07],'foliage','plant_detail')
for i,(x,z,roof_y)in enumerate([(66.9,-4.8,20.45),(69.5,-9.8,20.45),(79.9,-7.5,20.45),(67.5,6.5,20.45),(72.5,10.2,20.45),(79.9,9,20.45),(89,-8,19.25),(93,9,19.25),(89,8.5,19.25)]):
 cube(f'SCC_UpperBearing{i}',[x-.14,12,z-.14],[x+.14,16.3,z+.14]);cube(f'SCC_UpperRoofPier{i}',[x-.14,16.5,z-.14],[x+.14,roof_y,z+.14],'warm_walnut','roof_pier')
for i,z in enumerate([-7,7]):cube(f'SCC_WestTransfer{i}',[67.5,15.98,z-.14],[80.5,16.3,z+.14]);cube(f'SCC_WestRoofTransfer{i}',[67.5,20.13,z-.14],[80.5,20.45,z+.14],'warm_walnut','frame')
for i,x in enumerate([69.5,79.9,89,93]):cube(f'SCC_FloorLong{i}',[x-.14,15.98,-10],[x+.14,16.3,10])
for i,(x,y,z,staff)in enumerate([(75.5,20.45,5.4,False),(74.5,20.45,0,False),(90,19.25,0,False),(91.5,19.25,5,False),(70,19.15,-6,True),(75,19.15,-6,True),(65,20.45,0,False)]):lamp('SCC_Lamp'+str(i),x,y,z,staff)
assemblies['CO']=parts;bindings={'CO':[]};byname={a['name']:a for a in CO['rigid_bindings']}
def bind(name,position,yaw):q=copy.deepcopy(byname[name]);q.update(position=position,yaw=yaw);bindings['CO'].append(q)
bind('SharedActivityTable',[76,16.5,5.4],math.pi/2)
for i,(x,z,yaw)in enumerate([(74.45,6.1,math.pi/2),(74.45,4.7,math.pi/2),(77.55,6.1,3*math.pi/2),(77.55,4.7,3*math.pi/2)]):bind('ActivityChair'+str(i),[x,16.5,z],yaw)
bind('QuietChair0',[91.5,16.5,3.25],0);bind('QuietChair1',[91.5,16.5,6.75],math.pi);bind('QuietActivityTable',[91.5,16.5,5],math.pi/2);bind('GardenEdgeBenchSouth',[91,16.5,-6],0);bind('GardenEdgeBenchNorth',[69.3,16.5,6.5],math.pi/2)
for name in ['CleanStockCabinet']+[f'FixedStockBottle{i}'for i in range(4)]:q=copy.deepcopy(byname[name]);q['position']=stock(q['position']);bindings['CO'].append(q)
for r in rooms:
 for q in r['parts']:
  if q['name']in ['SC938_D04H928_Pier_3','SC938_D04H928_Pier_4']:
   for v in q['verts']:v[0]+=.2
allparts=[a for rows in assemblies.values()for a in rows]+[a for r in rooms for a in r['parts']];feet=[]
for a in allparts:
 lo=[min(v[i]for v in a['verts'])for i in range(3)];hi=[max(v[i]for v in a['verts'])for i in range(3)]
 if a['category']=='frame'and hi[0]-lo[0]<.5 and hi[2]-lo[2]<.5 and lo[1]<=12.001 and hi[1]>11.79:feet.append({'x':(lo[0]+hi[0])/2,'z':(lo[2]+hi[2])/2,'top_y':hi[1],'original_min_y':lo[1],'part_name':a['name'],'width_x':hi[0]-lo[0],'width_z':hi[2]-lo[2]})
sources={a['catalogue_id']:a for p in[S,CO]for a in p['sources']};pinpaths=[source_path,'Game/data/architecture/D04_STARBOARD_FULL_COMMONS.json',cross,'Game/data/reference/D04_guest_envelopes.json','Game/data/programme_ledger.json','Game/data/generated/structural_meshes.json','Game/data/generated/received_structural_meshes.json','Game/data/spatial_layout.json','Game/scripts/ship.gd','Game/scripts/player.gd','Game/scripts/guest_entry_door.gd','Game/scripts/aquatic_section.gd','Game/data/architecture/LOWER_STAFF_NETWORK.json','Game/data/architecture/PRIMARY_ATRIUM_CORE.json','Game/data/architecture/ATRIUM_GALLERY_RECEIVING.json','Game/data/architecture/crew_batch/D03_directory_06_NODE_NAME_MAP.json','Game/assets/models/D03_directory_06_runtime_names001.glb','BlenderCatalogue/catalogue_manifest.json','Game/docs/master_source/MASTER_FULL_CONTENT_INDEX.json','Game/docs/master_source/MASTER_CURRENT_APPLICATION.json']+['BlenderCatalogue/'+a['source']for a in sources.values()]
P={'schema':'astraea.d04.starboard_central.neighborhood.v1','base_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),'house_id':'starboard_central_lower_habitat_house','commons_programme_key':'D04_directory_04','all_twenty_allocations_unchanged':units,'rooms':rooms,'assemblies':assemblies,'bindings':bindings,'sources':list(sources.values()),'lights':lights,'source_pins':{f:sha(R/f)for f in pinpaths},'courts':courts,'receiving_floor_geometry':mapping(receiving),'receiving_floor_m2':receiving.area,'commons_floor_geometry':mapping(floor),'commons_floor_m2':floor.area,'lower_staff_floor_m2':0,'existing_public_floor_retained_once_m2':overlap,'negative_volume_zones':[{'purpose':'Keep useful open slots between two independently enclosed bays and the street, chamfered perimeter breathing room and allocation margins; no new programme or exterior opening','geometry':mapping(box(63,-14,97,14).difference(floor)),'floor_m2':952-floor.area}],'mapping_records':mapping_records,'support_candidates':feet,'walking_contacts':[],'stair_detailed_contact_replacements':[],'new_units':0,'new_rest_places':0,'active':False,'architectural_identity':{'title':'Starboard-central paired-bay garden commons','plan':'Tall western social bay and lower eastern quiet garden connected laterally across a continuous north/south home street, with three actual atrium approaches. Separate practical stock/returns sit in western service edge.','section':'Lower outboard garden roof19.25m and cool service canopy19.15m contrast with taller social roof20.45m; real glazed/dado/head enclosure and substantial lateral threshold.','compatible_kit_reuse':'Exact starboard-aft home/rest templates and resolved private courts translate[40,0,-370]; no new reflection/rescaling/capacity. Receiving and commons are independently authored, not port-central mirrors.'},'public_receiving_interface':{'proposed_atrium_join_points':[[50.9,16.5,-32],[50.9,16.5,0],[50.9,16.5,32]],'actual_interfaces_verified':False},'local_staff_vertical_built':False,'limits':['Starboard-central remains physical backlog until its exact connected gate passes. Northern port-aft portal, dedicated staff-network links and port-central service vertical remain physical construction backlog.','Original D03 Staff administration ceiling retained; no new local stair cut/dedicated staff approach claimed. Stock/returns use shared D04 receiving.','Source geometric bearing continuity does not establish engineering/load sizing.','No loaded cart/vertical or gameplay/privacy/occupancy/provider/save/biology acceptance.','Partial native visuals are separate from ordinary-game/CRT/hardware/final art acceptance.'],'phase_evidence':{}}
assert len({a['name']for a in allparts})==len(allparts)
(W/'CANDIDATE_PLAN.json').write_text(json.dumps(P,indent=2)+'\n');(W/'SUPPORT_CANDIDATES.json').write_text(json.dumps({'feet':feet},indent=2)+'\n');(W/'OWNED_GUARD_INTERFACE_INPUT.json').write_text(json.dumps(guard_corrections,indent=2)+'\n');print({'rooms':20,'rests':25,'courts':10,'bearings':len(feet),'receiving_m2':receiving.area,'commons_m2':floor.area,'purposeful_negative_m2':952-floor.area,'guard_aperture_preimages':len(guard_corrections)})
