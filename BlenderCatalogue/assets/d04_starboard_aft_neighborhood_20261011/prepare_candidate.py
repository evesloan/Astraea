from pathlib import Path
import json,copy,hashlib,math,ast,subprocess
from shapely.geometry import box,Polygon,shape,mapping,Point
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
from shapely import constrained_delaunay_triangles
W=Path(__file__).resolve().parent;R=W.parents[2];read=lambda f:json.load(open(R/f));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();canon=lambda a:hashlib.sha256(json.dumps(a,sort_keys=True,separators=(',',':')).encode()).hexdigest()
paths=[f'Game/data/architecture/D04_PORT_FORWARD_HOMES_{a}.json'for a in ['FIRST','SECOND','THIRD','FOURTH','FIFTH']];contracts=list(map(read,paths));CO=read('Game/data/architecture/D04_STARBOARD_FULL_COMMONS.json');cross='BlenderCatalogue/assets/residential_hotels/central_room_families_20261007_r001/residential-neighborhood-audit-20261007/ALL_1000_NEIGHBORHOOD_CROSSWALK.json';aft=[a for a in read(cross)['records']if a['house']=='starboard_aft_lower_habitat_house'];original=sum((p['rooms']for p in contracts),[]);assert len(aft)==20 and sum(a['proposed_rest_place_count']for a in aft)==25
transform=lambda v,d=0:[-v[0],v[1],-v[2]+d]
def geom(g,d=0):
 if g is None:return None
 def walk(v):return[-v[0],-v[1]+d]if isinstance(v[0],(int,float))else[walk(a)for a in v]
 return{**g,'coordinates':walk(g['coordinates'])}
def part(p,prefix,d=0):
 a=copy.deepcopy(p);a['name']=prefix+p['name'];a['verts']=[transform(v,d)for v in p['verts']];a.pop('actual_foundation_preimage',None);return a
rooms=[];mapping_records=[]
for u in aft:
 exact=next(r for r in original if u['allocation_x']==[-r['allocation']['allocation_x'][1],-r['allocation']['allocation_x'][0]]and u['allocation_z']==[-r['allocation']['allocation_z'][1],-r['allocation']['allocation_z'][0]])
 template=exact
 if u['proposed_rest_place_count']!=exact['allocation']['proposed_rest_place_count']:template=next(r for r in original if r['source_index']=={970:964,964:970}[exact['source_index']])
 assert template['allocation']['proposed_rest_place_count']==u['proposed_rest_place_count'];d=sum(u['allocation_z'])/2+sum(template['allocation']['allocation_z'])/2;r=copy.deepcopy(template);idx=u['source_envelope_index'];r.update(allocation=u,source_index=idx,model_file=f'D04_STARBOARD_AFT_HOME_{idx}_r001.glb',source_template={'source_index':template['source_index'],'source_sha256':canon(template),'proper_rotation_y_pi':True,'translation_z':d},species_ready=False,court_side={'east':'west','west':'east'}[template['court_side']]);r['parts']=[part(a,f'SA{idx}_',d)for a in template['parts']]
 if template is not exact:
  r['parts']=[part(a,f'SA{idx}_',d)for a in template['parts']if not(a['category']=='frame'and min(v[1]for v in a['verts'])<16.5)]+[part(a,f'SA{idx}_SF_',0)for a in exact['parts']if a['category']=='frame'and min(v[1]for v in a['verts'])<16.5];r['source_template']['structural_grid_template_index']=exact['source_index']
 for k in ['model_sha256','mesh_count','collision_policy','care_access_geometry_verified']:r.pop(k,None)
 slots=dict(zip(template['allocation']['proposed_rest_slot_ids'],u['proposed_rest_slot_ids']))
 for b in r['components']:
  b['position']=transform(b['position'],d);b['yaw']+=math.pi
  if 'rest_slot_id'in b:b['rest_slot_id']=slots[b['rest_slot_id']]
 for k in ['approach_world','outlook_world','care_station_world']:
  if k in r:r[k]=transform(r[k],d)
 for k in ['entry_to_care_waypoints','rest_approach_waypoints']:
  if k in r:r[k]=[transform(v,d)for v in r[k]]
 for k in ['floor_geometry','water_geometry']:r[k]=geom(r[k],d)
 r['entry']['origin']=transform(r['entry']['origin'],d);r['entry']['yaw']+=math.pi;r['entry']['persistent_id']=u['proposed_runtime_id']+':entry'
 for a in r['lights']:a['name']=f'SA{idx}_'+a['name'];a['at']=transform(a['at'],d)
 for a in r.get('rest_approach_worlds',[]):a['position']=transform(a['position'],d);a['rest_slot_id']=slots[a['rest_slot_id']]
 assert shape(r['floor_geometry']).difference(box(u['allocation_x'][0],u['allocation_z'][0],u['allocation_x'][1],u['allocation_z'][1])).area<1e-7
 rooms.append(r);mapping_records.append({'target_index':idx,'rotated_envelope_source_index':exact['source_index'],'actual_fitting_template_index':template['source_index'],'rests':u['proposed_rest_place_count'],'translation_z':d})
# Reuse the checked private-court kit and resolved guards; no inherited common-room or receiving plan.
removed={a['name']for p in contracts for k in ['guard_preimages','commons_frame_preimages','frame_joint_preimages']for a in p.get(k,[])}
courtparts=[part(a,'SAK_')for p in contracts for a in p['commons_parts']+p['guard_successor_parts']if a['name']not in removed and 'commons'not in a['name'].lower()]
courts=[{**a,'side':{'east':'west','west':'east'}[a['side']],'geometry':geom(a['geometry'])}for p in contracts for a in p['courts']if a['side']!='commons'];assert len(courts)==10
parts=[];faces=[[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]];text=(R/'BlenderCatalogue/assets/d04_port_forward_receiving_20261010/prepare.py').read_text()
for n in ast.parse(text).body:
 if isinstance(n,ast.FunctionDef)and n.name in ['add','cube','prism','segment']:exec(compile(ast.get_source_segment(text,n),'<reviewed existing architectural helpers>','exec'))
receiving=unary_union([box(41.95,294.6,46.05,445.4),box(4,403.5,41.95,406.9),box(46.05,367.2,63,372.6)]);existing=read('Game/data/generated/structural_meshes.json');baseline=unary_union([Polygon(t)for a in existing['regions']if a['floor_y']==16.5 for t in a['triangles']]);receiving=receiving.difference(baseline)
prism('SA_ReceivingFloor',receiving,16.26,16.5);prism('SA_ReceivingRoof',receiving,20.48,20.70,role='ivory_enamel',category='roof')
# Small original-frame bays carry the continuous street and single south public branch.
for x in [42.15,45.85]:
 cube(f'SA_StreetLong_{x}',[x-.12,15.98,294.6],[x+.12,16.3,445.4])
 for i,z in enumerate([294.8,309.5,324.3,334,345,357,367.8,380,392,403.8,415.7,430.5,445.1]):
  cube(f'SA_StreetBearing_{x}_{i}',[x-.12,12,z-.12],[x+.12,16.3,z+.12]);cube(f'SA_StreetRoofPier_{x}_{i}',[x-.12,16.5,z-.12],[x+.12,20.48,z+.12],'warm_walnut','roof_pier')
for z in [403.65,406.75]:
 cube(f'SA_PublicArrivalBeam_{z}',[4,15.98,z-.12],[44,16.3,z+.12])
 for i,x in enumerate([8.5,20,32]):cube(f'SA_PublicArrivalBearing_{z}_{i}',[x-.12,12,z-.12],[x+.12,16.3,z+.12])
for z in [367.35,372.45]:
 cube(f'SA_CommonsLinkBeam_{z}',[44,15.98,z-.12],[63,16.3,z+.12])
 for i,x in enumerate([50,56,62.6]):cube(f'SA_CommonsLinkBearing_{z}_{i}',[x-.12,12,z-.12],[x+.12,16.3,z+.12])
# True floor edges only; household openings use the resolved kit guards above.
for z in [403.5,406.9]:cube(f'SA_PublicArrivalGuard_{z}',[4,16.5,z-.04],[41.95,17.68,z+.04],'hospitality_glass','guard')
for z in [367.2,372.6]:cube(f'SA_CommonsLinkGuard_{z}',[46.05,16.5,z-.04],[62.92,17.68,z+.04],'hospitality_glass','guard')
cube('SA_NorthStreetEndGuard',[41.95,16.5,294.56],[46.05,17.68,294.64],'hospitality_glass','guard');cube('SA_SouthStreetEndGuard',[41.95,16.5,445.36],[46.05,17.68,445.44],'hospitality_glass','guard')
lights=[]
def lamp(name,x,y,z,staff=False):
 cube(name+'_Housing',[x-.32,y-.30,z-.26],[x+.32,y,z+.26],'champagne_metal','fitting');cube(name+'_Lens',[x-.27,y-.33,z-.21],[x+.27,y-.30,z+.21],'opal_glow','light_fixture');lights.append({'name':name+'_Lens','at':[x,y-.35,z],'staff':staff})
for i,z in enumerate([298.4,313.2,328,344,359,374,389,405.2,419.4,434.2,442]):lamp('SA_StreetLamp'+str(i),44,20.48,z)
for i,x in enumerate([10,22,34]):lamp('SA_PublicArrivalLamp'+str(i),x,20.48,405.2)
assemblies={'Receiving':parts+courtparts};parts=[]
# Authored asymmetric twin-bay commons: stepped reading volume, low screened quiet bay, separate service edge.
main=Polygon([(70,360.2),(73,357.8),(82.4,357.8),(85,360.4),(85,378.8),(82,381.8),(72.6,381.8),(70,379.2)]);service=box(63,356.2,71.4,367.2);entry=box(63,367.2,73,372.2);floor=unary_union([main,service,entry]);roof=floor.union(box(63,367.2,71.4,383.4));quiet=main.intersection(box(76.8,357.8,85,363.1));staff=unary_union([box(4,379,60,383.4),box(60,367.8,69.4,383.4)]);stair_void=box(63.2,372.2,69.2,382.9)
prism('SAC_CommonsFloor',floor,16.26,16.5);prism('SAC_CommonsRoof',roof,20.48,20.7,role='ivory_enamel',category='roof');prism('SAC_QuietLowCanopy',quiet,19.3,19.55,role='warm_walnut',category='roof');prism('SAC_ServiceLowCeiling',box(63.2,356.4,71.2,364.8),19.05,19.3,role='staff_panel',category='roof');prism('SAC_LowerSharedFloor',staff,11.76,12,role='warm_stone',category='staff_floor');prism('SAC_LowerSharedRoof',staff.difference(stair_void),15.2,15.4,role='staff_panel',category='staff_roof')
# Main perimeter follows the chamfered useful floor rather than a rectangular reservation box.
for i,(a,b)in enumerate(zip(list(main.exterior.coords),list(main.exterior.coords)[1:])):
 # West arrival is open between Z367.2 and372.2; other edges carry substantial enclosure and a screened outlook.
 if a[0]==b[0]==70:
  for j,(z0,z1)in enumerate([(360.2,367.2),(372.2,379.2)]):cube(f'SAC_WestWall_{j}',[69.88,16.5,z0],[70,20.48,z1],'ivory_enamel','wall')
 else:
  segment(f'SAC_PerimeterDado_{i}',[a[0],17.1,a[1]],[b[0],17.1,b[1]],.16,1.2,'warm_walnut','wall');segment(f'SAC_PerimeterGlass_{i}',[a[0],18.45,a[1]],[b[0],18.45,b[1]],.16,1.5,'hospitality_glass','window');segment(f'SAC_PerimeterHead_{i}',[a[0],20.065,a[1]],[b[0],20.065,b[1]],.16,.83,'ivory_enamel','wall')
# Quiet bay has a real sectional/threshold change; opening X79.2..83.5 leads to original seated cluster.
cube('SAC_QuietScreen',[73.2,16.5,362.96],[79.2,18.8,363.12],'warm_walnut','privacy_screen');cube('SAC_QuietPortalHead',[79.2,19.0,362.92],[83.5,19.3,363.18],'ivory_enamel','portal')
# Stock and closed-return cells are distinct, accessible apertures; cabinet and shelf are exact rigid source derivatives below.
for name,lo,hi in [('ServiceWest',[63,16.5,356.2],[63.16,20.48,367.2]),('ServiceNorth',[63,16.5,356.2],[71.4,20.48,356.38]),('ServiceEast',[71.24,16.5,356.2],[71.4,19.05,362.4]),('ServiceDivider',[66.4,16.5,356.38],[66.56,19.05,362.4]),('ReturnFrontL',[63.16,16.5,362.4],[63.5,19.05,362.58]),('ReturnFrontR',[65.4,16.5,362.4],[66.4,19.05,362.58]),('StockFrontL',[66.56,16.5,362.4],[67,19.05,362.58]),('StockFrontR',[69.8,16.5,362.4],[71.4,19.05,362.58]),('ReturnHead',[63.5,18.85,362.4],[65.4,19.05,362.58]),('StockHead',[67,18.85,362.4],[69.8,19.05,362.58])]:cube('SAC_'+name,lo,hi,'staff_panel','wall')
# Translate the intact stock shelf/bottles/cabinet module with proper180degree rotation, independently of the room plan.
stock_transform=lambda v:[138.4-v[0],v[1],-v[2]]
for a in CO['parts']:
 if 'StockShelf'in a['name']:
  q=copy.deepcopy(a);q['name']='SAC_'+a['name'];q['verts']=[stock_transform(v)for v in a['verts']];parts.append(q)
for i,x in enumerate([64.0,65.4]):
 cube(f'SAC_ReturnBinFoot{i}',[x-.32,16.5,357.5],[x+.32,16.62,358.35],'warm_walnut','fitting');cube(f'SAC_ReturnBinShell{i}',[x-.29,16.62,357.53],[x+.29,17.5,358.32],'staff_panel','closed_return');cube(f'SAC_ReturnBinLid{i}',[x-.32,17.5,357.5],[x+.32,17.6,358.35],'champagne_metal','closed_return')
# Purposeful planted outlook stays inside the floor; no exterior hull opening or borrowed occupied volume.
for i,z in enumerate([366.4,370.9,375.4]):
 cube(f'SAC_PlantedPlinth{i}',[83.2,16.5,z-.85],[84.4,17.1,z+.85],'warm_walnut','planter');cube(f'SAC_PlantedSoil{i}',[83.27,17.1,z-.78],[84.33,17.16,z+.78],'warm_stone','plant_detail')
 for j,dy in enumerate([0,.6,1.2]):cube(f'SAC_LeafMass{i}_{j}',[83.6-j*.08,17.16+dy,z-.52+j*.07],[84.0+j*.08,17.76+dy,z+.52-j*.07],'foliage','plant_detail')
# Original hull/floor bearing positions will be resolved in the actual source before export.
for x in [63.6,70.5,77.4,82.45]:
 for z in [356.7,363.5,369.9,375.5,383.4]:cube(f'SAC_UpperBearing_{x}_{z}',[x-.14,-3.2,z-.14],[x+.14,16.3,z+.14])
for z in [356.7,363.5,369.9,375.5,383.4]:cube(f'SAC_UpperTransfer_{z}',[63.2,15.98,z-.14],[84.7,16.3,z+.14])
for x in [63.6,70.5,77.4,82.45]:cube(f'SAC_UpperLong_{x}',[x-.14,15.98,356.2],[x+.14,16.3,383.4])
for x in [8.5,20,32,44,56,61.4]:
 for z in [379.25,383.15]:cube(f'SAC_LowerBearing_{x}_{z}',[x-.14,-3.2,z-.14],[x+.14,11.8,z+.14])
for z in [379.25,383.15]:cube(f'SAC_LowerTransfer_{z}',[4,11.48,z-.14],[69.4,11.8,z+.14])
for i,(a,b)in enumerate(zip(list(staff.exterior.coords),list(staff.exterior.coords)[1:])):
 if a[0]==b[0]==4:continue
 segment(f'SAC_LowerScreen_{i}',[a[0],13.6,a[1]],[b[0],13.6,b[1]],.12,3.2,'staff_panel','wall')
# Floor-supported roof piers flank the activity and quiet thresholds.
for i,(x,z)in enumerate([(70.7,365.5),(70.7,374.8),(80.1,365.5),(80.1,378.5)]):cube(f'SAC_ReadingRoofPier{i}',[x-.16,16.5,z-.16],[x+.16,20.48,z+.16],'warm_walnut','roof_pier')
for i,(x,y,z)in enumerate([(74.2,20.48,370),(80.3,20.48,374.5),(80.5,19.3,359.8),(64.5,19.05,360),(68.4,19.05,360),(66,20.48,369.5),(22,15.2,381.2),(44,15.2,381.2),(61.6,15.2,371.3)]):lamp('SAC_Lamp'+str(i),x,y,z,y<16)
assemblies['CO']=parts
bindings={'CO':[]};byname={a['name']:a for a in CO['rigid_bindings']}
def bind(name,position,yaw):
 q=copy.deepcopy(byname[name]);q.update(position=position,yaw=yaw);bindings['CO'].append(q)
bind('SharedActivityTable',[77.3,16.5,372],math.pi/2)
for i,(x,z,yaw)in enumerate([(75.75,372.7,math.pi/2),(75.75,371.3,math.pi/2),(78.85,372.7,3*math.pi/2),(78.85,371.3,3*math.pi/2)]):bind('ActivityChair'+str(i),[x,16.5,z],yaw)
bind('QuietChair0',[78.75,16.5,359.8],math.pi/2);bind('QuietChair1',[82.25,16.5,359.8],-math.pi/2);bind('QuietActivityTable',[80.5,16.5,359.8],0);bind('GardenEdgeBenchSouth',[81.9,16.5,377.3],math.pi/2);bind('GardenEdgeBenchNorth',[72.4,16.5,378.5],0)
for name in ['CleanStockCabinet']+[f'FixedStockBottle{i}'for i in range(4)]:q=copy.deepcopy(byname[name]);q['position']=stock_transform(q['position']);q['yaw']+=math.pi;bindings['CO'].append(q)
bind('StaffStair450',[69.2,12,372.3],math.pi)
# The same original H450 native is rotated rigidly; only its declared simplified walking planes are transformed.
walking=[[[132.4-v[0],v[1],-v[2]]for v in quad]for quad in CO['walking_contacts']];names=['SAC_'+a.removeprefix('D04SC_')for a in CO['stair_detailed_contact_replacements']]
for a in assemblies['CO']:
 if a['name']=='SAC_UpperBearing_77.4_356.7':
  a['verts']=[[v[0]-.2,v[1],v[2]]for v in a['verts']]
allparts=[a for rows in assemblies.values()for a in rows]+[a for r in rooms for a in r['parts']];feet=[]
for a in allparts:
 lo=[min(v[i]for v in a['verts'])for i in range(3)];hi=[max(v[i]for v in a['verts'])for i in range(3)]
 if a['category']=='frame'and hi[0]-lo[0]<.5 and hi[2]-lo[2]<.5 and lo[1]<=12.001 and hi[1]>11.79:feet.append({'x':(lo[0]+hi[0])/2,'z':(lo[2]+hi[2])/2,'top_y':hi[1],'original_min_y':lo[1],'part_name':a['name'],'width_x':hi[0]-lo[0],'width_z':hi[2]-lo[2]})
sources={a['catalogue_id']:a for p in contracts+[CO]for a in p['sources']};pinpaths=paths+['Game/data/architecture/D04_STARBOARD_FULL_COMMONS.json',cross,'Game/data/reference/D04_guest_envelopes.json','Game/data/programme_ledger.json','Game/data/generated/structural_meshes.json','Game/data/spatial_layout.json','Game/scripts/ship.gd','Game/scripts/player.gd','Game/scripts/guest_entry_door.gd','Game/scripts/aquatic_section.gd','Game/data/architecture/LOWER_STAFF_NETWORK.json','Game/data/architecture/AFT_MIDSHIP_PUBLIC_CORE.json','Game/data/architecture/crew_batch/D03_directory_10_NODE_NAME_MAP.json','Game/assets/models/D03_directory_10_runtime_names001.glb','BlenderCatalogue/catalogue_manifest.json','Game/docs/master_source/MASTER_FULL_CONTENT_INDEX.json','Game/docs/master_source/MASTER_CURRENT_APPLICATION.json','BlenderCatalogue/assets/circulation_architecture/source/AST-CIR-001_H450.blend','BlenderCatalogue/assets/circulation_architecture/AST-CIR-001_H450.manifest.json']+['BlenderCatalogue/'+a['source']for a in sources.values()]
negative=box(63,356,97,384).difference(floor)
P={'schema':'astraea.d04.starboard_aft.neighborhood.v1','base_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),'house_id':'starboard_aft_lower_habitat_house','commons_programme_key':'D04_directory_06','all_twenty_allocations_unchanged':aft,'rooms':rooms,'assemblies':assemblies,'bindings':bindings,'sources':list(sources.values()),'lights':lights,'source_pins':{f:sha(R/f)for f in pinpaths},'courts':courts,'receiving_floor_geometry':mapping(receiving),'receiving_floor_m2':receiving.area,'commons_floor_geometry':mapping(floor),'commons_floor_m2':floor.area,'lower_staff_floor_geometry':mapping(staff),'lower_staff_floor_m2':staff.area,'negative_volume_zones':[{'purpose':'Original H450 stair/headroom, chamfered perimeter breathing room and protected hull volume; no additional programme or exterior opening','geometry':mapping(negative),'floor_m2':negative.area}],'mapping_records':mapping_records,'support_candidates':feet,'walking_contacts':walking,'stair_detailed_contact_replacements':names,'new_units':0,'new_rest_places':0,'active':False,'architectural_identity':{'title':'Starboard-aft twin-bay reading commons','plan':'Single south public branch; continuous street; chamfered central reading activity volume, low screened quiet pocket and independent practical stock/closed-return edge','section':'Rigid original H450 reversed across its width with proper180degree yaw; low quiet/service ceilings contrast with taller reading room','compatible_kit_reuse':'Unchanged original home profiles and private-court kit are reused deliberately. No inherited port-aft receiving or common-room plan.'},'public_receiving_interface':{'world_floor':[3.5,16.5,405.2],'north_core_sidewall_preserved_closed':True,'north_lateral_link_built':False},'limits':['Dedicated staff-network links and the port-aft northern lateral portal are physical construction backlog, not polish/gameplay. Local approach meets shared D03aft spine only.','Geometric source bearing continuity is not load sizing or hull/Uniforms floor engineering acceptance.','No loaded cart/vertical or gameplay/privacy/occupancy/provider/save/biology acceptance.','Source views are partial native diagnostics; ordinary-game/CRT/hardware and final art remain open.'],'phase_evidence':{}}
assert len({a['name']for a in allparts})==len(allparts)
for u in aft:assert receiving.intersection(box(*[u['allocation_x'][0],u['allocation_z'][0],u['allocation_x'][1],u['allocation_z'][1]])).area<1e-7
(W/'CANDIDATE_PLAN.json').write_text(json.dumps(P,indent=2)+'\n');(W/'SUPPORT_CANDIDATES.json').write_text(json.dumps({'feet':feet},indent=2)+'\n');print({'rooms':20,'rests':25,'privatecourts':len(courts),'parts':len(allparts),'support_candidates':len(feet),'receiving_m2':receiving.area,'commons_m2':floor.area,'lower_shared_m2':staff.area,'purposeful_negative_m2':negative.area})
