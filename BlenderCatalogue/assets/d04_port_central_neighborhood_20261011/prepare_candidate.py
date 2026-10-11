from pathlib import Path
import json,copy,hashlib,math,ast,subprocess
from shapely.geometry import box,Polygon,shape,mapping
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
from shapely import constrained_delaunay_triangles
W=Path(__file__).resolve().parent;R=W.parents[2];read=lambda f:json.load(open(R/f));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();canon=lambda a:hashlib.sha256(json.dumps(a,sort_keys=True,separators=(',',':')).encode()).hexdigest()
paths=[f'Game/data/architecture/D04_PORT_FORWARD_HOMES_{a}.json'for a in ['FIRST','SECOND','THIRD','FOURTH','FIFTH']];contracts=list(map(read,paths));CO=read('Game/data/architecture/D04_STARBOARD_FULL_COMMONS.json');cross='BlenderCatalogue/assets/residential_hotels/central_room_families_20261007_r001/residential-neighborhood-audit-20261007/ALL_1000_NEIGHBORHOOD_CROSSWALK.json';units=[a for a in read(cross)['records']if a['house']=='port_central_lower_habitat_house'];original=sum((p['rooms']for p in contracts),[]);assert len(units)==20 and sum(a['proposed_rest_place_count']for a in units)==25
transform=lambda v:[v[0]-40,v[1],v[2]+370]
def geom(g):
 if g is None:return None
 def walk(v):return[v[0]-40,v[1]+370]if isinstance(v[0],(int,float))else[walk(a)for a in v]
 return{**g,'coordinates':walk(g['coordinates'])}
def part(p,prefix):
 a=copy.deepcopy(p);a['name']=prefix+p['name'];a['verts']=[transform(v)for v in p['verts']];a.pop('actual_foundation_preimage',None);return a
rooms=[];mapping_records=[]
for u in units:
 template=next(r for r in original if all(abs(u['allocation_x'][i]-(r['allocation']['allocation_x'][i]-40))<1e-7 and abs(u['allocation_z'][i]-(r['allocation']['allocation_z'][i]+370))<1e-7 for i in [0,1]));assert template['allocation']['proposed_rest_place_count']==u['proposed_rest_place_count'];r=copy.deepcopy(template);idx=u['source_envelope_index'];r.update(allocation=u,source_index=idx,model_file=f'D04_PORT_CENTRAL_HOME_{idx}_r001.glb',source_template={'source_index':template['source_index'],'source_sha256':canon(template),'rigid_translation_xyz':[-40,0,370]},species_ready=False);r['parts']=[part(a,f'PC{idx}_')for a in template['parts']]
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
 for a in r['lights']:a['name']=f'PC{idx}_'+a['name'];a['at']=transform(a['at'])
 for a in r.get('rest_approach_worlds',[]):a['position']=transform(a['position']);a['rest_slot_id']=slots[a['rest_slot_id']]
 assert shape(r['floor_geometry']).difference(box(u['allocation_x'][0],u['allocation_z'][0],u['allocation_x'][1],u['allocation_z'][1])).area<1e-7
 rooms.append(r);mapping_records.append({'target_index':idx,'compatible_original_template_index':template['source_index'],'rests':u['proposed_rest_place_count'],'proper_rigid_translation_xyz':[-40,0,370]})
removed={a['name']for p in contracts for k in ['guard_preimages','commons_frame_preimages','frame_joint_preimages']for a in p.get(k,[])}
courtparts=[part(a,'PCK_')for p in contracts for a in p['commons_parts']+p['guard_successor_parts']if a['name']not in removed and 'commons'not in a['name'].lower()];courts=[{**a,'geometry':geom(a['geometry'])}for p in contracts for a in p['courts']if a['side']!='commons'];assert len(courts)==10
successors=[]
for q in courtparts:
 if q['name']=='PCK_D04H4_D04NR_EastGuard_0_Successor_0':
  for i,(z0,z1)in enumerate([(4,30.3),(33.7,40.22000000000003)]):
   a=copy.deepcopy(q);a['name']=q['name']+'_CentralBranch_'+str(i)
   for v in a['verts']:v[2]=z0 if v[2]==4 else z1
   successors.append(a)
 else:successors.append(q)
courtparts=successors
parts=[];faces=[[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]];text=(R/'BlenderCatalogue/assets/d04_port_forward_receiving_20261010/prepare.py').read_text()
for n in ast.parse(text).body:
 if isinstance(n,ast.FunctionDef)and n.name in ['add','cube','prism','segment']:exec(compile(ast.get_source_segment(text,n),'<reviewed existing architectural helpers>','exec'))
single_prism=prism
def prism(name,g,*args,**kw):
 if g.geom_type=='MultiPolygon':
  for i,q in enumerate(g.geoms):single_prism(name+'_'+str(i),q,*args,**kw)
 else:single_prism(name,g,*args,**kw)
floor=Polygon([(-96,-8),(-91,-13),(-74,-13),(-69,-8),(-69,-3),(-63,-3),(-63,3),(-69,3),(-69,8),(-74,13),(-91,13),(-96,8)])
receiving=unary_union([box(-86.05,-75.4,-81.95,75.4),box(-84,-33.7,-50.8,-30.3),box(-84,30.3,-50.8,33.7),box(-63,-3,-50.8,3)]).difference(floor)
baseline=unary_union([Polygon(t)for a in read('Game/data/generated/structural_meshes.json')['regions']if a['floor_y']==16.5 for t in a['triangles']]);retained_overlap=receiving.intersection(baseline).area;receiving=receiving.difference(baseline)
prism('PC_ReceivingFloor',receiving,16.26,16.5);prism('PC_ReceivingRoof',receiving,20.4,20.64,role='ivory_enamel',category='roof')
for x in [-85.85,-82.15]:
 for i,z in enumerate([-75.1,-62,-49,-35.5,-22,22,35.5,49,62,75.1]):
  cube(f'PC_StreetBearing_{x}_{i}',[x-.12,12,z-.12],[x+.12,16.3,z+.12]);cube(f'PC_StreetRoofPier_{x}_{i}',[x-.12,16.5,z-.12],[x+.12,20.4,z+.12],'warm_walnut','roof_pier')
 for i,(z0,z1)in enumerate([(-75.4,-13),(13,75.4)]):cube(f'PC_StreetLong_{x}_{i}',[x-.12,15.98,z0],[x+.12,16.3,z1])
for j,z in enumerate([-33.55,-30.45,30.45,33.55,-2.82,2.82]):
 x0=-84 if abs(z)>10 else -63
 cube(f'PC_ArrivalBeam{j}',[x0,15.98,z-.12],[-51,16.3,z+.12]);cube(f'PC_ArrivalRoofBeam{j}',[x0,20.10,z-.12],[-51,20.4,z+.12])
 for i,x in enumerate([-77,-65,-55]if abs(z)>10 else[-61,-55]):cube(f'PC_ArrivalBearing{j}_{i}',[x-.12,12,z-.12],[x+.12,16.3,z+.12]);cube(f'PC_ArrivalRoofPier{j}_{i}',[x-.12,16.5,z-.12],[x+.12,20.4,z+.12],'warm_walnut','roof_pier')
for z in [-33.7,-30.3,30.3,33.7]:cube(f'PC_ArrivalGuard{z}',[-81.95,16.5,z-.04],[-51,17.68,z+.04],'hospitality_glass','guard')
for z in [-3,3]:cube(f'PC_CentralArrivalGuard{z}',[-63,16.5,z-.04],[-51,17.68,z+.04],'hospitality_glass','guard')
for z in [-75.4,75.4]:cube(f'PC_StreetEndGuard{z}',[-86.05,16.5,z-.04],[-81.95,17.68,z+.04],'hospitality_glass','guard')
lights=[]
def lamp(name,x,y,z,staff=False):
 cube(name+'_Housing',[x-.32,y-.30,z-.26],[x+.32,y,z+.26],'champagne_metal','fitting');cube(name+'_Lens',[x-.27,y-.33,z-.21],[x+.27,y-.30,z+.21],'opal_glow','light_fixture');lights.append({'name':name+'_Lens','at':[x,y-.35,z],'staff':staff})
for i,z in enumerate([-72,-57,-42,-26,26,42,57,72]):lamp('PC_StreetLamp'+str(i),-84,20.4,z)
for i,(x,z)in enumerate([(-73,-32),(-57,-32),(-73,32),(-57,32),(-57,0)]):lamp('PC_ArrivalLamp'+str(i),x,20.4,z)
assemblies={'Receiving':parts+courtparts};parts=[]
prism('PCC_CommonsFloor',floor,16.26,16.5);prism('PCC_CommonsRoof',floor,20.4,20.64,role='ivory_enamel',category='roof');quiet=floor.intersection(box(-96,3,-89,13));prism('PCC_QuietLowCanopy',quiet,19.35,19.57,role='warm_walnut',category='roof');prism('PCC_ServiceLowCanopy',floor.intersection(box(-76,-13,-69,-3)),19.15,19.37,role='staff_panel',category='roof')
# Three authored thresholds: north/south home street and deep east atrium arrival.
for i,(a,b)in enumerate(zip(list(floor.exterior.coords),list(floor.exterior.coords)[1:])):
 segments=[(a,b)]
 if a[1]==b[1]and abs(a[1])==13:segments=[((-91,a[1]),(-86.05,a[1])),((-81.95,a[1]),(-74,a[1]))]
 if a[0]==b[0]==-63:continue
 for j,(a,b)in enumerate(segments):
  segment(f'PCC_PerimeterDado_{i}_{j}',[a[0],17.1,a[1]],[b[0],17.1,b[1]],1.2,.16,'warm_walnut','wall');segment(f'PCC_PerimeterGlass_{i}_{j}',[a[0],18.64,a[1]],[b[0],18.64,b[1]],1.88,.16,'hospitality_glass','window');segment(f'PCC_PerimeterHead_{i}_{j}',[a[0],19.99,a[1]],[b[0],19.99,b[1]],.82,.16,'ivory_enamel','wall')
for z in [-13,13]:cube(f'PCC_StreetPortalHead{z}',[-86.05,19.2,z-.12],[-81.95,20.4,z+.12],'ivory_enamel','portal')
cube('PCC_QuietScreen',[-89.12,16.5,3],[-88.96,18.65,5.0],'warm_walnut','privacy_screen');cube('PCC_QuietScreenBack',[-89.12,16.5,9],[-88.96,18.65,11.0],'warm_walnut','privacy_screen')
# Separate stock/closed-return compartments, both reached from the social floor.
for name,lo,hi in [('ServiceWest',[-76.0,16.5,-12],[-75.84,19.15,-3.4]),('ServiceEast',[-69.3,16.5,-8],[-69.14,19.15,-3.4]),('ServiceNorth',[-76,16.5,-12],[-74.4,19.15,-11.84]),('ServiceDivider',[-74.2,16.5,-11],[-74.04,19.15,-5]),('ReturnFrontL',[-75.84,16.5,-3.56],[-75.5,19.15,-3.4]),('ReturnFrontR',[-74.5,16.5,-3.56],[-74.2,19.15,-3.4]),('StockFrontL',[-74.04,16.5,-3.56],[-73.5,19.15,-3.4]),('StockFrontR',[-70.1,16.5,-3.56],[-69.3,19.15,-3.4]),('ReturnHead',[-75.5,18.8,-3.56],[-74.5,19.15,-3.4]),('StockHead',[-73.5,18.8,-3.56],[-70.1,19.15,-3.4])]:cube('PCC_'+name,lo,hi,'staff_panel','wall')
stock_transform=lambda v:[v[0]-142.2,v[1],v[2]+350.0]
for a in CO['parts']:
 if 'StockShelf'in a['name']:q=copy.deepcopy(a);q['name']='PCC_'+a['name'];q['verts']=[stock_transform(v)for v in a['verts']];parts.append(q)
for i,x in enumerate([-75,-73.8]):
 cube(f'PCC_ReturnBinFoot{i}',[x-.3,16.5,-9.7],[x+.3,16.62,-8.9],'warm_walnut','fitting');cube(f'PCC_ReturnBinShell{i}',[x-.27,16.62,-9.67],[x+.27,17.5,-8.93],'staff_panel','closed_return');cube(f'PCC_ReturnBinLid{i}',[x-.3,17.5,-9.7],[x+.3,17.6,-8.9],'champagne_metal','closed_return')
for i,z in enumerate([-6,0,6]):
 cube(f'PCC_PlantedPlinth{i}',[-95.5,16.5,z-.8],[-94.2,17.1,z+.8],'warm_walnut','planter');cube(f'PCC_PlantedSoil{i}',[-95.43,17.1,z-.73],[-94.27,17.16,z+.73],'warm_stone','plant_detail')
 for j,dy in enumerate([0,.55,1.1]):cube(f'PCC_LeafMass{i}_{j}',[-95.15-j*.08,17.16+dy,z-.5+j*.07],[-94.55+j*.08,17.71+dy,z+.5-j*.07],'foliage','plant_detail')
for i,(x,z)in enumerate([(-92,-7),(-92,7),(-87,-10),(-87,10),(-78,-10),(-78,10),(-70,-6),(-70,6)]):
 cube(f'PCC_UpperBearing{i}',[x-.14,12,z-.14],[x+.14,16.3,z+.14]);cube(f'PCC_UpperRoofPier{i}',[x-.14,16.5,z-.14],[x+.14,20.4,z+.14],'warm_walnut','roof_pier')
for i,z in enumerate([-6,6]):cube(f'PCC_UpperTransfer{i}',[-94,15.98,z-.14],[-69.5,16.3,z+.14]);cube(f'PCC_RoofTransfer{i}',[-94,20.08,z-.14],[-69.5,20.4,z+.14],'warm_walnut','frame')
for i,x in enumerate([-92,-87,-78,-70]):cube(f'PCC_UpperLong{i}',[x-.14,15.98,-11],[x+.14,16.3,11])
for i,(x,y,z,staff)in enumerate([(-78.3,20.4,0,False),(-86.5,20.4,0,False),(-92,19.35,7,False),(-92,20.4,-6,False),(-74.5,19.15,-6,True),(-71,19.15,-6,True),(-65,20.4,0,False)]):lamp('PCC_Lamp'+str(i),x,y,z,staff)
for q in parts:
 if q['name'].startswith('PCC_ReturnBin')and q['name'].endswith('1'):
  for v in q['verts']:v[0]-=1.2;v[2]+=1.9
assemblies['CO']=parts;bindings={'CO':[]};byname={a['name']:a for a in CO['rigid_bindings']}
def bind(name,position,yaw):q=copy.deepcopy(byname[name]);q.update(position=position,yaw=yaw);bindings['CO'].append(q)
bind('SharedActivityTable',[-78.3,16.5,0],0)
for i,(x,z,yaw)in enumerate([(-79,-1.55,0),(-77.6,-1.55,0),(-79,1.55,math.pi),(-77.6,1.55,math.pi)]):bind('ActivityChair'+str(i),[x,16.5,z],yaw)
bind('QuietChair0',[-92,16.5,5.25],0);bind('QuietChair1',[-92,16.5,8.75],math.pi);bind('QuietActivityTable',[-92,16.5,7],math.pi/2);bind('GardenEdgeBenchSouth',[-90.4,16.5,-6],math.pi/2);bind('GardenEdgeBenchNorth',[-87,16.5,8],math.pi)
for name in ['CleanStockCabinet']+[f'FixedStockBottle{i}'for i in range(4)]:q=copy.deepcopy(byname[name]);q['position']=stock_transform(q['position']);bindings['CO'].append(q)
for r in rooms:
 for q in r['parts']:
  if q['name']in['PC929_D04H928_Pier_3','PC929_D04H928_Pier_4']:
   for v in q['verts']:v[0]-=.2
for q in assemblies['CO']:
 if q['name']in ['PCC_UpperRoofPier1','PCC_UpperRoofPier6']:
  dx,dz=(-2,1)if q['name'].endswith('1')else(0,1.6)
  for v in q['verts']:v[0]+=dx;v[2]+=dz
allparts=[a for rows in assemblies.values()for a in rows]+[a for r in rooms for a in r['parts']];feet=[]
for a in allparts:
 lo=[min(v[i]for v in a['verts'])for i in range(3)];hi=[max(v[i]for v in a['verts'])for i in range(3)]
 if a['category']=='frame'and hi[0]-lo[0]<.5 and hi[2]-lo[2]<.5 and lo[1]<=12.001 and hi[1]>11.79:feet.append({'x':(lo[0]+hi[0])/2,'z':(lo[2]+hi[2])/2,'top_y':hi[1],'original_min_y':lo[1],'part_name':a['name'],'width_x':hi[0]-lo[0],'width_z':hi[2]-lo[2]})
sources={a['catalogue_id']:a for p in contracts+[CO]for a in p['sources']};pinpaths=paths+['Game/data/architecture/D04_STARBOARD_FULL_COMMONS.json',cross,'Game/data/reference/D04_guest_envelopes.json','Game/data/programme_ledger.json','Game/data/generated/structural_meshes.json','Game/data/generated/received_structural_meshes.json','Game/data/spatial_layout.json','Game/scripts/ship.gd','Game/scripts/player.gd','Game/scripts/guest_entry_door.gd','Game/scripts/aquatic_section.gd','Game/data/architecture/LOWER_STAFF_NETWORK.json','Game/data/architecture/PRIMARY_ATRIUM_CORE.json','Game/data/architecture/ATRIUM_GALLERY_RECEIVING.json','Game/data/architecture/crew_batch/D03_directory_05_NODE_NAME_MAP.json','Game/assets/models/D03_directory_05_runtime_names001.glb','BlenderCatalogue/catalogue_manifest.json','Game/docs/master_source/MASTER_FULL_CONTENT_INDEX.json','Game/docs/master_source/MASTER_CURRENT_APPLICATION.json']+['BlenderCatalogue/'+a['source']for a in sources.values()]
negative=box(-97,-14,-63,14).difference(floor)
P={'schema':'astraea.d04.port_central.neighborhood.v1','base_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),'house_id':'port_central_lower_habitat_house','commons_programme_key':'D04_directory_03','all_twenty_allocations_unchanged':units,'rooms':rooms,'assemblies':assemblies,'bindings':bindings,'sources':list(sources.values()),'lights':lights,'source_pins':{f:sha(R/f)for f in pinpaths},'courts':courts,'receiving_floor_geometry':mapping(receiving),'receiving_floor_m2':receiving.area,'commons_floor_geometry':mapping(floor),'commons_floor_m2':floor.area,'lower_staff_floor_m2':0.0,'existing_public_floor_retained_once_m2':retained_overlap,'negative_volume_zones':[{'purpose':'Chamfered corners preserve perimeter breathing room and original allocation margins; no new programme/exterior opening','geometry':mapping(negative),'floor_m2':negative.area}],'mapping_records':mapping_records,'support_candidates':feet,'walking_contacts':[],'stair_detailed_contact_replacements':[],'new_units':0,'new_rest_places':0,'active':False,'architectural_identity':{'title':'Port-central three-threshold atrium salon','plan':'Continuous north/south home street passes the quiet garden and distinct social table. Deep east atrium arrival; enclosed stock and returns east of the street. Chamfered outer social volume remains inside original reservation.','section':'Low western quiet canopy and cool low service ceiling contrast with tall social/arrival volume; substantial perimeter dado, visibly glazed middle and supported head.','compatible_kit_reuse':'Twenty exact fitting/allocation/rest matches use prior original port-forward profiles with rigid translation; no reflection/rescaling/rest template exchange. Private-court resolved kit translated; common room and receiving independently authored.'},'public_receiving_interface':{'proposed_atrium_join_points':[[-50.9,16.5,-32],[-50.9,16.5,0],[-50.9,16.5,32]],'actual_interfaces_verified':False},'local_staff_vertical_built':False,'limits':['Both central packages remain physical backlog until their own connected verification passes. Port-aft northern lateral portal and dedicated lower staff-network links/crossings/vertical service remain physical construction backlog.','Original D03 Training room ceiling is retained; no new local stair cut or dedicated staff approach is asserted. Commons practical service cells are accessed from D04 shared receiving.','Geometric source bearing continuity is not load sizing or hull/Training ceiling engineering acceptance.','No loaded cart/vertical or gameplay/privacy/occupancy/provider/save/biology acceptance.','Partial source diagnostic views are separate from ordinary-game/CRT/hardware and final art acceptance.'],'phase_evidence':{}}
assert len({a['name']for a in allparts})==len(allparts)
for u in units:assert receiving.intersection(box(u['allocation_x'][0],u['allocation_z'][0],u['allocation_x'][1],u['allocation_z'][1])).area<1e-7
(W/'CANDIDATE_PLAN.json').write_text(json.dumps(P,indent=2)+'\n');(W/'SUPPORT_CANDIDATES.json').write_text(json.dumps({'feet':feet},indent=2)+'\n');print({'rooms':20,'rests':25,'privatecourts':len(courts),'parts':len(allparts),'bearings':len(feet),'receiving_m2':receiving.area,'commons_m2':floor.area,'purposeful_negative_m2':negative.area})
