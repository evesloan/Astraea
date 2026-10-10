from pathlib import Path
import copy,json,hashlib,math,subprocess
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
W=Path(__file__).resolve().parent;R=W.parents[2];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();write=lambda p,v:p.write_text(json.dumps(v,indent=2)+'\n')
base='65ae79c645c99489f3f86598f0801b86c102e8b2';assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=R).decode().strip()==base
rows=json.load(open(R/'BlenderCatalogue/assets/residential_production_batch/inputs/PROPOSED_FULL_1000_PRODUCTION_ROWS.json'))['records'];S=json.load(open(R/'Game/data/architecture/CENTRAL_RESIDENTIAL_STREETS.json'));H=json.load(open(R/'Game/data/architecture/STAR_ATLAS_EIGHT_HABITATS.json'));rooms=[];pins={};parts=[];joins=[]
inputs=['BlenderCatalogue/assets/residential_production_batch/inputs/PROPOSED_FULL_1000_PRODUCTION_ROWS.json','BlenderCatalogue/catalogue_manifest.json','Game/data/architecture/CENTRAL_RESIDENTIAL_STREETS.json','Game/data/architecture/STAR_ATLAS_UNITS.json','Game/data/generated/structural_meshes.json','Game/data/generated/received_structural_meshes.json','Game/docs/master_source/MASTER_CURRENT_APPLICATION.json','Game/docs/master_source/MASTER_FULL_CONTENT_INDEX.json','BlenderCatalogue/references/intimate/image(20261002-000722).png','BlenderCatalogue/references/aquatic/image(20261001-035517).png']
for p in inputs:pins[p]=sha(R/p)
templates={133:json.load(open(R/'Game/data/architecture/STAR_ATLAS_SPECIALTY_TENTH.json')),139:json.load(open(R/'Game/data/architecture/STAR_ATLAS_SPECIALTY_TENTH.json')),449:json.load(open(R/'Game/data/architecture/STAR_ATLAS_SPECIALTY_SIXTH.json')),479:json.load(open(R/'Game/data/architecture/STAR_ATLAS_SPECIALTY_SIXTH.json')),509:json.load(open(R/'Game/data/architecture/STAR_ATLAS_SPECIALTY_THIRD.json')),563:json.load(open(R/'Game/data/architecture/STAR_ATLAS_SPECIALTY_FOURTH.json'))}
sources={a['catalogue_id']:a for p in templates.values()for a in p['sources']}
for idx,sourceidx,profile in [(365,133,'quiet_inner_north_library'),(371,139,'quiet_inner_south_folio'),(377,449,'quiet_outer_negative_end_gallery'),(383,479,'quiet_outer_positive_long_folio'),(389,509,'quiet_inner_offset_folio_retreat'),(395,563,'quiet_inner_staggered_pair_study')]:
 row=next(r for r in rows if r['source_envelope_index']==idx);assert row['deck']=='D14'and row['proposed_rest_place_count']==(2 if idx==395 else 1) and len(row['proposed_rest_slot_ids'])==row['proposed_rest_place_count']
 src=next(r for r in templates[sourceidx]['rooms']if r['allocation']['source_envelope_index']==sourceidx);room=copy.deepcopy(src);old=room['allocation'];assert old['proposed_rest_place_count']==row['proposed_rest_place_count'];slot_map=dict(zip(old['proposed_rest_slot_ids'],row['proposed_rest_slot_ids']));delta=[sum(row['allocation_x'])/2-sum(old['allocation_x'])/2,row['floor_y']-old['floor_y'],sum(row['allocation_z'])/2-sum(old['allocation_z'])/2];move=lambda v:[v[i]+delta[i]for i in range(3)]
 pins['Game/assets/models/'+src['model_file']]=sha(R/'Game/assets/models'/src['model_file'])
 room['allocation']=row;room['profile_proposal']=profile;room['layout']=profile;room['model_file']=f'StarAtlasSpecialty_{idx}.glb';room['proposed_design_species']='Mantelids';room['species_ready']=False;room['orientation_yaw']=math.pi if idx in [377,383] else 0;room['component_source_predecessor']={'model_file':src['model_file'],'source_index':sourceidx,'translation':delta}
 room['parts']=[q for q in room['parts']if q['category']!='receiving']
 for q in room['parts']:q['name']=q['name'].replace(f'SA{sourceidx}_',f'SA{idx}_');q['verts']=[move(v)for v in q['verts']]
 for b in room['components']:
  b['position']=move(b['position'])
  if 'rest_slot_id'in b:b['rest_slot_id']=slot_map[b['rest_slot_id']]
 for d in room['doors']:d['position']=move(d['position']);d['persistent_id']=row['proposed_runtime_id']+(':'+d['name'].lower())
 for light in room['lights']:light['position']=move(light['position'])
 rests={b['name']:b for b in room['components']if b['catalogue_id']=='AST-RST-QC-001'}
 for f in room['rest_fittings']:
  f['rest_slot_id']=slot_map[f['rest_slot_id']];f['binding']=rests[f['binding']['name']];f['frame_origin']=move(f['frame_origin']);f['approach_world']=move(f['approach_world']);f['actual_reference_bottom_contacts_world']=[move(v)for v in f['actual_reference_bottom_contacts_world']]
 assert not(R/'Game/assets/models'/room['model_file']).exists(),'New export destination must not replace another source'
 for key in ['receiving_contacts','below_unit','previous_model_binding','historical_profile_proposal','design_adaptation']:room.pop(key,None)
 room['receiving_contacts']=[];room['window_view']='Actual shared D14 street-facing screened activity bay'if idx in [377,383] else'Inner-bank internal outlook; retained geometry, final court composition acceptance held'
 room['operations_hold']=['canonical species/body/rig/pose','acoustic attenuation/molting/biology','privacy permission/stock/save','engineering load capacity/final runtime visuals'];rooms.append(room)
import numpy as np
def cube(name,lo,hi,category):
 verts=[[x,y,z]for z in [lo[2],hi[2]]for y in [lo[1],hi[1]]for x in [lo[0],hi[0]]];parts.append({'name':name,'verts':verts,'faces':[[0,2,3,1],[4,5,7,6],[0,1,5,4],[2,6,7,3],[0,4,6,2],[1,3,7,5]],'category':category,'runtime_collision':True})
def beam(name,a,b,width,category):
 a=np.array(a);b=np.array(b);d=(b-a)/np.linalg.norm(b-a);u=np.array([1.,0,0]);v=np.cross(d,u);v/=np.linalg.norm(v);u=np.cross(v,d)
 verts=[(p+du*u*width/2+dv*v*width/2).tolist()for p in [a,b]for du,dv in [(-1,-1),(1,-1),(1,1),(-1,1)]];parts.append({'name':name,'verts':verts,'faces':[[0,3,2,1],[4,5,6,7],[0,1,5,4],[3,7,6,2],[0,4,7,3],[1,2,6,5]],'category':category,'runtime_collision':True});return parts[-1]
frame_joints=[];rakers=[];braces=[]
source_owners={sign:next(r for r in S['regions']if r['id']=='D14_STAR_ATLAS_MISSING_STREET_'+str(0 if sign<0 else 1))for sign in [-1,1]}
def joint(part,lo,hi,owner):
 assert owner['floor_y']==88.5 and owner['thickness']==.24 and lo[1]==88.26 and hi[1]==88.28
 assert unary_union([Polygon(t)for t in owner['triangles']]).buffer(1e-7).covers(box(lo[0],lo[2],hi[0],hi[2]))
 joins.append({'name':part['name'],'owner':owner['id'],'overlap_bounds':[lo,hi],'source_bottom':88.26,'floor_y':88.5,'source_thickness':.24,'basis':'Exact contained overlap into verified retained D14 source street slab; primary engineering/load/cantilever capacity held'})
for side,sign in [('North',-1),('South',1)]:
 owner=source_owners[sign];lo,hi=(-112.2,-104.8)if sign==-1 else(104.8,112.2)
 cube(f'SA_D14_Twelfth{side}StreetFloor',[-86.05,88.26,lo],[-81.95,88.5,hi],'D14_street_extension_floor')
 for n,x in enumerate([-85.8,-82.2]):
  a,b=(-112.2,-104.56)if sign==-1 else(104.56,112.2)
  cube(f'SA_D14_Twelfth{side}Longitudinal_{n}',[x-.1,88.05,a],[x+.1,88.28,b],'D14_street_longitudinal');ol,oh=(-104.8,-104.56)if sign==-1 else(104.56,104.8);joint(parts[-1],[x-.1,88.26,ol],[x+.1,88.28,oh],owner)
  az=sign*104.5;tz=sign*111.9
  cube(f'SA_D14_Twelfth{side}RakerAnchor_{n}',[x-.1,87.5,az-.1],[x+.1,88.28,az+.1],'D14_source_connected_raker_anchor');joint(parts[-1],[x-.1,88.26,az-.1],[x+.1,88.28,az+.1],owner)
  q=beam(f'SA_D14_Twelfth{side}Raker_{n}',[x,87.6,az],[x,88.14,tz],.18,'D14_under_street_diagonal_raker');rakers.append({'name':q['name'],'anchor_name':f'SA_D14_Twelfth{side}RakerAnchor_{n}','tip_member':f'SA_D14_Twelfth{side}Longitudinal_{n}','anchor_center':[x,87.6,az],'tip_center':[x,88.14,tz],'category':'Geometric source-slab-connected raker/truss; primary engineering capacity held'})
 cube(f'SA_D14_Twelfth{side}RakerLowerCrossTie',[-85.9,87.52,sign*104.5-.1],[-82.1,87.68,sign*104.5+.1],'D14_raker_anchor_cross_tie')
 for n,z in enumerate([sign*d for d in [105.5,108.6,111.7]]):cube(f'SA_D14_Twelfth{side}Crossmember_{n}',[-86.05,88.05,z-.1],[-81.95,88.28,z+.1],'D14_street_transverse')
 for bank,x in [('West',-86.05),('East',-81.95)]:
  intervals=[(104.8,106.86),(110.34,112.2)]if sign==1 else[(-112.2,-110.34),(-106.86,-104.8)]
  for n,(a,b)in enumerate(intervals):cube(f'SA_D14_Twelfth{side}{bank}Guard_{n}',[x-.035,88.5,a],[x+.035,89.6,b],'guard')
 end=sign*112.2;cube(f'SA_D14_Twelfth{side}TerminalGuard',[-86.05,88.5,end-.035],[-81.95,89.6,end+.035],'guard')
 intervals=[(-104.8,-102.94),(-99.46,-97.421)]if sign<0 else[(97.421,99.46),(102.94,104.8)]
 for n,(a,b)in enumerate(intervals):cube(f'SA_D14_Twelfth{side}ExistingEastFrontGuard_{n}',[-81.985,88.5,a],[-81.915,89.6,b],'guard')
for room in rooms:
 a=room['allocation'];idx=a['source_envelope_index'];z=sum(a['allocation_z'])/2;xlo,xhi=a['allocation_x']
 for n,v in enumerate([-3.1,0,3.1]):
  cube(f'SA{idx}_FloorTransverse_{n}',[min(xlo,-85.9),88.05,z+v-.1],[max(xhi,-82.1),88.28,z+v+.1],'D14_room_floor_crossbeam')
  if idx in [365,371]:joint(parts[-1],[-85.9,88.26,z+v-.1],[-82.1,88.28,z+v+.1],source_owners[-1 if z<0 else 1])
 for n,x in enumerate([xlo+.15,(xlo+xhi)/2,xhi-.15]):cube(f'SA{idx}_FloorLongitudinal_{n}',[x-.1,88.05,z-3.6],[x+.1,88.28,z+3.6],'D14_room_floor_longitudinal')
 q=beam(f'SA{idx}_UnderFloorPlanBrace',[xlo+.15,88.14,z-3.1],[xhi-.15,88.14,z+3.1],.12,'D14_under_floor_plan_brace');braces.append({'name':q['name'],'start':[xlo+.15,88.14,z-3.1],'end':[xhi-.15,88.14,z+3.1],'basis':'Exact floor joist intersection plan brace; engineering capacity held'})
guard_ids=['D14_STAR_ATLAS_MISSING_STREET_0_Guard_53','D14_STAR_ATLAS_MISSING_STREET_0_Guard_54','D14_STAR_ATLAS_MISSING_STREET_1_Guard_77','D14_STAR_ATLAS_MISSING_STREET_1_Guard_78'];guards=[e for e in S['exposed_edge_guards']if e['id']in guard_ids];assert len(guards)==4
preimage=json.load(open(W/'PREIMAGE_ACTUAL_SUPPORT.json'));assert preimage['status']=='PASS'and preimage['source_slab_witnesses']==70 and not preimage['errors'];geometry=[]
for room in rooms:
 a=room['allocation'];rect=box(a['allocation_x'][0],a['allocation_z'][0],a['allocation_x'][1],a['allocation_z'][1]);hits=[]
 for f in ['Game/data/generated/structural_meshes.json','Game/data/generated/received_structural_meshes.json','Game/data/architecture/CENTRAL_RESIDENTIAL_STREETS.json']:
  for r in json.load(open(R/f))['regions']:
   if r['floor_y']in [84,88.5]:
    area=unary_union([Polygon(t)for t in r['triangles']]).intersection(rect).area;assert area<1e-6,(a['source_envelope_index'],r['id']);hits.append({'owner':r['id'],'floor_y':r['floor_y'],'area_in_room':area})
 geometry.append({'source_index':a['source_envelope_index'],'source_floor_intersections':hits,'D13_foundation_available':False})
Q={'schema':'astraea.star_atlas_specialty_twelfth_receiving.v1','base_commit':base,'model_file':'StarAtlasSpecialtyTwelfthReceiving.glb','parts':parts,'source_pins':pins,'slab_joints':joins,'existing_frame_joints':[],'rakers':rakers,'room_plan_braces':braces,'lower_structural_owners':[],'support_toes':[],'removed_source_guards':guards,'removed_previous_guard_meshes':[],'new_street_floor_area_m2':60.68,'new_street_overlap_m2':0,'new_piers':0,'engineering_load_capacity_accepted':False,'geometric_load_path':'Fourteen exact source-slab overlap volumes at actual retained D14 north/south street; six base-inner floor transverse joints plus eight terminal longitudinal/raker-anchor joints. Four rakers and six joist-crossing plan braces. No D13 foundation or culled room-skin support assumed; primary load design held.'}
P={'schema':'astraea.star_atlas_specialty_twelfth.v1','base_commit':base,'root_name':'StarAtlasSpecialtyTwelfthCandidates','sources':list(sources.values()),'preimage_pins':pins,'rooms':rooms,'selected_source_indices':[365,371,377,383,389,395],'retained_specialty_reservations':46,'physical_interior_batch':6,'new_units':0,'rest_reservations':7,'species_ready_rooms':0,'source_ids_unchanged':True,'limits':['46/46 retained Group1 specialty physical candidates with57reservedrests; five singles and one double preserved','Primary structural load/cantilever engineering, canonical bodies/rigs/poses, biology/acoustics/privacy/stock/save and final ordinary Godot/CRT/hardware visual acceptance held']}
write(W/'PLAN.json',P);write(W/'RECEIVING_PLAN.json',Q);write(W/'PREIMAGE_ALLOCATION_CHECK.json',{'status':'PASS','base_commit':base,'indices':[365,371,377,383,389,395],'capacities':{str(i):(2 if i==395 else 1)for i in [365,371,377,383,389,395]},'new_units':0,'new_rest_places':0,'ids_changed':0,'remaining_specialty_by_deck':{'D13':0,'D14':0},'source_support_before_edits':preimage['status'],'source_slab_witnesses_before_edits':70,'foundation_geometry':geometry,'dependency_choice':'Complete all six final D14 reservations using exact existing D14 slab contacts; no D13 foundation or culled room skins relied upon; primary engineering held'});print('TWELFTH_PREPARED',len(rooms),len(parts),len(joins),len(rakers))
