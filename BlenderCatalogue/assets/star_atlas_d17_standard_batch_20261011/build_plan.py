from pathlib import Path
import json,hashlib,subprocess,copy,math
from shapely.geometry import Polygon,box,shape,mapping
from shapely.ops import unary_union,triangulate
from shapely.affinity import scale
R=Path('/workspace/astraea-recovered-532087b9-20261010T083844Z');W=Path(__file__).resolve().parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();old=json.load(open(R/'Game/data/architecture/STAR_ATLAS_D17_RECEIVING_FIRST.json'));base_room=json.load(open(R/'Game/data/architecture/STAR_ATLAS_D17_STANDARD823.json'));allocations=json.load(open(W/'NINE_EXACT_ALLOCATIONS.json'));parts=[];source_native='BlenderCatalogue/assets/star_atlas_d17_receiving_first_20261010/StarAtlasD17ReceivingFirst.blend'
def finish(q,material='D17R_FloorLong_0'):
 # Historical prism plans repeat coincident points per face;index-weld exact coordinates without changing geometry.
 unique=[];indices={};remap={}
 for i,v in enumerate(q['verts']):
  key=tuple(v)
  if key not in indices:indices[key]=len(unique);unique.append(v)
  remap[i]=indices[key]
 q['verts']=unique;q['faces']=[[remap[i]for i in face]for face in q['faces']]
 q['material_native']=source_native;q['material_source']=material;q['expected_bounds']=[[min(v[i]for v in q['verts'])for i in range(3)],[max(v[i]for v in q['verts'])for i in range(3)]];parts.append(q)
def cube(name,low,high,role='champagne_metal',category='frame',material='D17R_FloorLong_0'):
 x,y,z=low;X,Y,Z=high;finish({'name':name,'verts':[[x,y,z],[X,y,z],[X,y,Z],[x,y,Z],[x,Y,z],[X,Y,z],[X,Y,Z],[x,Y,Z]],'faces':[[3,2,1,0],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]],'role':role,'category':category,'runtime_collision':True},material)
def prism(name,poly,y0,y1,role='champagne_metal',category='floor',material='D17R_ReceivedFloor'):
 for i,t in enumerate(triangulate(poly)):
  if not poly.covers(t.representative_point()):continue
  for j,g in enumerate([t.intersection(poly)]):
   if g.geom_type!='Polygon' or g.area<1e-8:continue
   ring=list(g.exterior.coords)[:-1];n=len(ring);vs=[[x,y0,z]for x,z in ring]+[[x,y1,z]for x,z in ring];faces=[list(reversed(range(n))),list(range(n,2*n))]+[[k,(k+1)%n,(k+1)%n+n,k+n]for k in range(n)];finish({'name':f'{name}_{i:03d}_{j}','verts':vs,'faces':faces,'role':role,'category':category,'runtime_collision':True},material)
def guard(name,a,b):
 x,z=a;X,Z=b;dx=X-x;dz=Z-z;l=math.hypot(dx,dz);u=-dz/l*.04;v=dx/l*.04;p=Polygon([(x+u,z+v),(X+u,Z+v),(X-u,Z-v),(x-u,z-v)]);prism(name+'_Base',p,102,102.08,category='guard_base',material='D17R_GuardEnd_Base');prism(name,p,102.08,103.12,role='hospitality_glass',category='guard',material='D17R_GuardEnd');prism(name+'_Cap',p.buffer(.015,join_style=2),103.12,103.18,category='guard',material='D17R_GuardEnd_Cap')
# Reuse the proven fore receiving geometry by exact reflection, with actual lower source-bearing stations.
skip=('D17R_ReceivedRoof','D17R_ReceivedFloor','D17R_GuardInnerFore','D17R_GuardInnerAft','D17R_HeldRoom823','D17R_GuardEnd','D17R_GuardOuter','D17R_LightHousing','D17R_LightLens')
for original in old['parts']:
 if original['name'].startswith(skip):continue
 q=copy.deepcopy(original);q['name']='SAB_North_'+original['name'];q['verts']=[[x,y,-z]for x,y,z in original['verts']];q['faces']=[list(reversed(f))for f in q['faces']]
 if original['name'].startswith('D17R_D16Pier_'):
  zshift=-2.0;q['verts']=[[x,y,z+zshift]for x,y,z in q['verts']]
 finish(q,original['name'])
# Complete longitudinal street frames beyond the proven first receiving modules.
for bank,lo,hi in [('Fore',-68,-39.04),('Aft',39.04,68)]:
 for side,x in enumerate([-62.75,-60.25]):
  cube(f'SAB_{bank}_FloorLong{side}',[x-.16,101.48,lo],[x+.16,101.8,hi])
  cube(f'SAB_{bank}_TrussUpper{side}',[x-.16,105.98,lo],[x+.16,106.26,hi])
  cube(f'SAB_{bank}_TrussLower{side}',[x-.16,104.8,lo],[x+.16,105.04,hi])
  for j,z in enumerate([-68,-60.8,-53.6,-46.4,-39.2]if bank=='Fore'else[39.2,46.4,53.6,60.8,68]):
   if bank=='Aft'and j==0:continue # Original retained end post and hanger already receive this lap joint.
   cube(f'SAB_{bank}_TrussPost{side}_{j}',[x-.12,104.8,z-.10],[x+.12,106.26,z+.10])
   # Keep hangers outside the contained three-and-a-half metre entry receivers.
   cube(f'SAB_{bank}_Hanger{side}_{j}',[x-.10,101.48,z-.10],[x+.10,104.92,z+.10])
# Lower street bearings are actual compiler slabs,not room skins or hypothetical missing piers.
feet=[]
for i,z in enumerate([-67.8,-60.6,-53.4,-46.2,-39.0,-32.2,39.4,46.6,53.8,61.0,67.8]):
 name=f'SAB_OutboardPier{i:02d}';cube(name,[-85.98,97.5,z-.16],[-85.66,101.80,z+.16],category='source_bearing_pier');feet.append({'name':name,'at':[-85.82,97.5,z],'half_width':.16,'source_owner':'D16_STAR_ATLAS_MISSING_STREET_0'if z<0 else'D16_STAR_ATLAS_MISSING_STREET_1'})
 cube(f'SAB_CrossGirder{i:02d}',[-85.98,101.56,z-.12],[-60.09,101.80,z+.12])
for bank,lo,hi in [('Fore',-68,-32),('Aft',39.2,68)]:
 for j,x in enumerate([-85.82,-75.79,-71.5,-67.5]):cube(f'SAB_{bank}_RoomLong{j}',[x-.12,101.56,lo],[x+.12,101.80,hi])
# Missing-only street plates;native source owns these surfaces,not duplicate compiler floors.
existing=[]
for f in ['structural_meshes.json','received_structural_meshes.json']:
 existing += [Polygon(t)for q in json.load(open(R/'Game/data/generated'/f))['regions']if abs(q['floor_y']-102)<1e-6 for t in q['triangles']]
upper=json.load(open(R/'Game/data/architecture/STAR_ATLAS_UPPER_COMMONS.json'));existing += [shape(q['desired_geometry'])for q in upper['floors']if q['deck']==17];existing += [shape(old['floor_geometry']),box(-75.95,32,-63.05,39.2)];existing=unary_union(existing)
fore=unary_union([scale(shape(old['floor_geometry']),xfact=1,yfact=-1,origin=(0,0)),box(-63,-68,-60,-39.2)]).difference(existing);aft=box(-63,39.2,-60,68).difference(existing)
for label,g in [('Fore',fore),('Aft',aft)]:
 assert g.intersection(existing).area<1e-7
 for i,poly in enumerate([g]if g.geom_type=='Polygon'else list(g.geoms)):
  prism(f'SAB_{label}_StreetFloor{i}',poly,101.78,102,role='ivory_enamel',category='floor');prism(f'SAB_{label}_StreetRoof{i}',poly,106.26,106.5,role='ivory_enamel',category='roof',material='D17R_ReceivedRoof')
 guard(f'SAB_{label}_OuterGuard',[-60.06,-14.06 if label=='Fore'else 39.14],[-60.06,-67.94 if label=='Fore'else 67.94]);guard(f'SAB_{label}_EndGuard',[-62.94,-67.94 if label=='Fore'else 67.94],[-60.06,-67.94 if label=='Fore'else 67.94])
rooms=[];fixtures=[]
for a in sorted(allocations,key=lambda q:min(z for x,z in q['candidate_layout']['proposed_floor_boundary'])):
 idx=a['source_envelope_index'];poly=Polygon(a['candidate_layout']['proposed_floor_boundary']);cz=(poly.bounds[1]+poly.bounds[3])/2;delta=cz-35.6
 rooms.append({'allocation':a,'source_model':base_room['room_model'],'source_model_sha256':base_room['room_model_sha256'],'translation':[0,0,delta],'center_z':cz,'source_native':'BlenderCatalogue/assets/star_atlas_d17_receiving_first_20261010/StarAtlasD17Standard823Recess.blend','source_native_sha256':base_room['source_pins']['BlenderCatalogue/assets/star_atlas_d17_receiving_first_20261010/StarAtlasD17Standard823Recess.blend'],'entry_origin':[-63.175,102,cz],'entry_yaw':base_room['room_preimage']['entry_yaw'],'bath_origin':[-65.95,102,cz+.7],'bath_yaw':math.pi,'source_floor_area_m2':92.88})
 for j,original in enumerate(base_room['fixture_instances']):
  q=copy.deepcopy(original);q['name']=f'SAB_{idx}_Lamp{j}';q['at'][2]+=delta;q['emitter'][2]+=delta;q['room_index']=idx;fixtures.append(q)
 for j,original in enumerate([q for q in base_room['parts']if q['category']=='fixture_mount']):
  q=copy.deepcopy(original);q['name']=f'SAB_{idx}_Mount{j}';q['verts']=[[x,y,z+delta]for x,y,z in q['verts']];finish(q,'D17R_FloorLong_0')
# Guard the receiving edge everywhere outside the exact individual entry receiver widths.
for bank,lo,hi in [('Fore',-67.94,-17.44),('Aft',39.2,67.94)]:
 gaps=[(r['center_z']-1.82,r['center_z']+1.82)for r in rooms if lo<r['center_z']<hi];at=lo
 for i,(a,b)in enumerate(sorted(gaps)+[(hi,hi)]):
  if a>at+.02:guard(f'SAB_{bank}_InnerGuard{i}',[-62.94,at],[-62.94,min(a,hi)])
  at=max(at,b)
# One lighting source per new street segment;housing geometry is physically received by the canopy.
street_lights=[]
for i,z in enumerate([-22,-35.6,-46,-57,-65,44,54,64]):
 cube(f'SAB_StreetLightHousing{i}',[-61.66,105.84,z-.16],[-61.34,106.28,z+.16],role='ivory_enamel',category='light_fixture',material='D17R_LightHousing_0');cube(f'SAB_StreetLightLens{i}',[-61.63,105.82,z-.13],[-61.37,105.84,z+.13],role='opal_glow',category='light_source',material='D17R_LightLens_0');street_lights.append({'name':f'SAB_StreetLightLens{i}','at':[-61.5,105.81,z],'energy':.9,'range':7})
source_paths=['Game/scripts/ship.gd','Game/scripts/lighting_budget.gd','Game/scripts/central_homes_adoption.gd','Game/scripts/star_atlas_d17_receiving_first.gd','Game/scripts/star_atlas_d17_standard823.gd','Game/data/architecture/STAR_ATLAS_D17_RECEIVING_FIRST.json','Game/data/architecture/STAR_ATLAS_D17_STANDARD823.json','Game/data/architecture/STAR_ATLAS_UPPER_COMMONS.json','Game/data/architecture/STAR_ATLAS_UNITS.json','Game/data/architecture/D17_LUXURY_HOUSES_PROPOSAL.json','Game/data/architecture/CENTRAL_RESIDENTIAL_STREETS.json','Game/data/generated/structural_meshes.json','Game/data/generated/received_structural_meshes.json','Game/data/architecture/botanical_pair/runtime_manifest.json','Game/data/architecture/ENGINEERING_CALIBRATION_DRAFT.json','Game/assets/models/STAR_ATLAS_D17_RECEIVING_FIRST_r001.glb','Game/assets/models/STAR_ATLAS_D17_STANDARD823_FRAME_r001.glb','Game/assets/models/'+base_room['room_model'],source_native,rooms[0]['source_native'],'BlenderCatalogue/assets/star_atlas_upper_commons_20261009/PLAN.json','BlenderCatalogue/assets/star_atlas_upper_commons_20261009/source/StarAtlasUpperCommons.blend','BlenderCatalogue/assets/hospitality_lantern/source/AST-LGT-001.blend','BlenderCatalogue/assets/residential_production_batch/inputs/PROPOSED_FULL_1000_PRODUCTION_ROWS.json','BlenderCatalogue/catalogue_manifest.json','Game/docs/master_source/MASTER_CURRENT_APPLICATION.json','Game/docs/master_source/MASTER_FULL_CONTENT_INDEX.json']
up=json.load(open(R/'BlenderCatalogue/assets/star_atlas_upper_commons_20261009/PLAN.json'));north_preimages=[q for q in up['parts']if q['name']in ['SA_D17_NorthWall_0','SA_D17_EastWall_0']];assert len(north_preimages)==2
P={'schema':'astraea.d17.standard_batch.v1','base_commit':subprocess.check_output(['git','-C',str(R),'rev-parse','HEAD'],text=True).strip(),'active':False,'parts':parts,'furniture':[],'fixture_instances':fixtures,'street_lights':street_lights,'rooms':rooms,'structure_file':'STAR_ATLAS_D17_STANDARD_BATCH_FRAME_r002.glb','source_pins':{f:sha(R/f)for f in source_paths},'protected_native_exports':{str(f.relative_to(R)):sha(f)for f in R.rglob('*')if f.is_file()and f.suffix in ['.blend','.glb']and'.godot'not in f.parts},'foundation_feet':feet,'north_foundation_feet':[{'name':'SAB_North_'+q['name'],'at':[q['x'],97.5,-q['z']-2],'half_width':.16,'source_owner':'D16_STAR_ATLAS_MISSING_STREET_0'}for q in old['piers']],'floor_geometry':{'Fore':mapping(fore),'Aft':mapping(aft)},'new_floor_m2':fore.area+aft.area,'source_room_floor_m2_to_install':9*92.88,'north_gateway':{'origin':[-65,102,-14.13],'yaw':math.pi,'persistent_id':'D17_port_central_fore_house_receiving_proposal'},'north_wall_preimages':north_preimages,'aft_end_guard_preimages':[q for q in old['parts']if q['name']in ['D17R_GuardEnd','D17R_GuardEnd_Base','D17R_GuardEnd_Cap']],'room_ids_and_eighteen_rest_ids_unchanged':True,'new_units':0,'new_rest_places':0,'physical_port_central_standard_proposals_after_batch':10,'all_retained_D17_standard_allocations':19,'other_nine_starboard_standard_proposals_outside_this_package':True,'seven_VIPs_Group2_owned':True,'limits':['Exact source bearings and source-connected geometry do not certify23m transverse or extended street frame load,buckling,hull or primary transfer capacity;Group7 review remains necessary','Outboard D16 street pier footprints preserve its central walking route;upper outboard house court has no new public floor/gallery across bedroom windows','Nine rigid source-kit physical proposals preserve all IDs/reservations;no additive unit/rest capacity,occupancy,save or species readiness','Seven port-central VIPs remain Group2-owned;their polygons and 81-luxury ledger unchanged;all19 D17 standard allocations remain retained','Whole-house/private gardens/environment,pressure/hull continuity,service/cart/loaded vertical and final Godot/CRT/hardware acceptance remain open'],'master_review':{'complete_chapters':[5,6,7,8],'reference_reopened':'BlenderCatalogue/references/intimate/image(20261002-000722).png'}}
P['upper_commons_model_sha256']=upper['model_sha256']
P['source_contact_allowlist']=['SA_LongBeam_-64_2_106_26','SA_CrossBeam_-12_7_106_26','SA_D17_NorthWall_0','SA_D17_EastWall_0','D17R_ReceivedFloor','D17R_FloorLong_0','D17R_FloorLong_1','D17R_Hanger_0_06','D17R_FloorCross_06','D17R_GuardOuter','D17R_GuardOuter_Base','D17R_GuardOuter_Cap','SA823_Transverse3']
(W/'PLAN.json').write_text(json.dumps(P,indent=2)+'\n');print(json.dumps({'parts':len(parts),'rooms':len(rooms),'original_room_runtime_meshes':9*405,'new_source_floor_m2':P['new_floor_m2'],'fixtures':len(fixtures),'lower_source_feet':len(feet)+4,'protected_assets':len(P['protected_native_exports'])}))
