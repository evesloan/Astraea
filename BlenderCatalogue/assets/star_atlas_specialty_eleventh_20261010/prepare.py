from pathlib import Path
import copy,json,hashlib,math,subprocess
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
W=Path(__file__).resolve().parent;R=W.parents[2];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();write=lambda p,v:p.write_text(json.dumps(v,indent=2)+'\n')
base='3679019699bb7a42f8602f965d7a105bf7e32775';assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=R).decode().strip()==base
rows=json.load(open(R/'BlenderCatalogue/assets/residential_production_batch/inputs/PROPOSED_FULL_1000_PRODUCTION_ROWS.json'))['records'];S=json.load(open(R/'Game/data/architecture/CENTRAL_RESIDENTIAL_STREETS.json'));H=json.load(open(R/'Game/data/architecture/STAR_ATLAS_EIGHT_HABITATS.json'));rooms=[];pins={};parts=[];joins=[]
inputs=['BlenderCatalogue/assets/residential_production_batch/inputs/PROPOSED_FULL_1000_PRODUCTION_ROWS.json','BlenderCatalogue/catalogue_manifest.json','Game/data/architecture/CENTRAL_RESIDENTIAL_STREETS.json','Game/data/architecture/STAR_ATLAS_UNITS.json','Game/data/generated/structural_meshes.json','Game/data/generated/received_structural_meshes.json','Game/docs/master_source/MASTER_CURRENT_APPLICATION.json','Game/docs/master_source/MASTER_FULL_CONTENT_INDEX.json','BlenderCatalogue/references/intimate/image(20261002-000722).png','BlenderCatalogue/references/aquatic/image(20261001-035517).png']
for p in inputs:pins[p]=sha(R/p)
templates={449:json.load(open(R/'Game/data/architecture/STAR_ATLAS_SPECIALTY_SIXTH.json')),407:json.load(open(R/'Game/data/architecture/STAR_ATLAS_SPECIALTY_FIFTH.json')),139:json.load(open(R/'Game/data/architecture/STAR_ATLAS_SPECIALTY_TENTH.json'))}
sources={a['catalogue_id']:a for p in templates.values()for a in p['sources']}
for idx,sourceidx,profile in [(145,449,'quiet_negative_end_gallery_cocoon'),(151,407,'quiet_positive_screened_gallery_cocoon'),(157,139,'quiet_inner_terminal_folio_cocoon')]:
 row=next(r for r in rows if r['source_envelope_index']==idx);assert row['deck']=='D13'and row['proposed_rest_place_count']==1 and len(row['proposed_rest_slot_ids'])==1
 src=next(r for r in templates[sourceidx]['rooms']if r['allocation']['source_envelope_index']==sourceidx);room=copy.deepcopy(src);old=room['allocation'];delta=[sum(row['allocation_x'])/2-sum(old['allocation_x'])/2,row['floor_y']-old['floor_y'],sum(row['allocation_z'])/2-sum(old['allocation_z'])/2];move=lambda v:[v[i]+delta[i]for i in range(3)]
 pins['Game/assets/models/'+src['model_file']]=sha(R/'Game/assets/models'/src['model_file'])
 room['allocation']=row;room['profile_proposal']=profile;room['layout']=profile;room['model_file']=f'StarAtlasSpecialty_{idx}.glb';room['proposed_design_species']='Mantelids';room['species_ready']=False;room['orientation_yaw']=math.pi if idx in [145,151] else 0;room['component_source_predecessor']={'model_file':src['model_file'],'source_index':sourceidx,'translation':delta}
 room['parts']=[q for q in room['parts']if q['category']!='receiving']
 for q in room['parts']:q['name']=q['name'].replace(f'SA{sourceidx}_',f'SA{idx}_');q['verts']=[move(v)for v in q['verts']]
 for b in room['components']:
  b['position']=move(b['position'])
  if 'rest_slot_id'in b:b['rest_slot_id']=row['proposed_rest_slot_ids'][0]
 for d in room['doors']:d['position']=move(d['position']);d['persistent_id']=row['proposed_runtime_id']+(':'+d['name'].lower())
 for light in room['lights']:light['position']=move(light['position'])
 rest=next(b for b in room['components']if b['catalogue_id']=='AST-RST-QC-001')
 for f in room['rest_fittings']:
  f['rest_slot_id']=row['proposed_rest_slot_ids'][0];f['binding']=rest;f['frame_origin']=move(f['frame_origin']);f['approach_world']=move(f['approach_world']);f['actual_reference_bottom_contacts_world']=[move(v)for v in f['actual_reference_bottom_contacts_world']]
 assert not(R/'Game/assets/models'/room['model_file']).exists(),'New export destination must not replace another source'
 for key in ['receiving_contacts','below_unit','previous_model_binding','historical_profile_proposal','design_adaptation']:room.pop(key,None)
 room['receiving_contacts']=[];room['window_view']='Actual shared D13 street-facing screened activity bay'if idx in [145,151] else'Inner-bank internal outlook; retained geometry, final court composition acceptance held'
 room['operations_hold']=['canonical species/body/rig/pose','acoustic attenuation/molting/biology','privacy permission/stock/save','engineering load capacity/final runtime visuals'];rooms.append(room)
import numpy as np
def cube(name,lo,hi,category):
 verts=[[x,y,z]for z in [lo[2],hi[2]]for y in [lo[1],hi[1]]for x in [lo[0],hi[0]]];parts.append({'name':name,'verts':verts,'faces':[[0,2,3,1],[4,5,7,6],[0,1,5,4],[2,6,7,3],[0,4,6,2],[1,3,7,5]],'category':category,'runtime_collision':True})
def beam(name,a,b,width,category):
 a=np.array(a);b=np.array(b);d=(b-a)/np.linalg.norm(b-a);u=np.array([1.,0,0]);v=np.cross(d,u);v/=np.linalg.norm(v);u=np.cross(v,d)
 verts=[(p+du*u*width/2+dv*v*width/2).tolist()for p in [a,b]for du,dv in [(-1,-1),(1,-1),(1,1),(-1,1)]];parts.append({'name':name,'verts':verts,'faces':[[0,3,2,1],[4,5,6,7],[0,1,5,4],[3,7,6,2],[0,4,7,3],[1,2,6,5]],'category':category,'runtime_collision':True});return parts[-1]
old=json.load(open(R/'Game/data/architecture/STAR_ATLAS_SPECIALTY_TENTH.json'))['receiving'];pins['Game/assets/models/'+old['model_file']]=sha(R/'Game/assets/models'/old['model_file']);frame_joints=[];rakers=[];braces=[]
def old_part(name):return next(p for p in old['parts']if p['name']==name)
def frame_joint(part,prior,lo,hi):
 bounds=np.array(prior['verts']);assert np.all(np.array(lo)>=bounds.min(0)-1e-8)and np.all(np.array(hi)<=bounds.max(0)+1e-8)
 frame_joints.append({'name':part['name'],'existing_mesh':prior['name'],'existing_model':old['model_file'],'overlap_bounds':[lo,hi],'basis':'Exact contained overlap into preceding D13 tenth frame; chain returns to actual retained D13 slab. Primary engineering/load/cantilever capacity held'})
for side,sign in [('North',-1),('South',1)]:
 lo,hi=(-90,-82.6)if sign==-1 else(82.6,90)
 cube(f'SA_D13_Eleventh{side}StreetFloor',[-86.05,83.76,lo],[-81.95,84,hi],'D13_street_extension_floor')
 for n,x in enumerate([-85.8,-82.2]):
  a,b=(-90,-82.36)if sign==-1 else(82.36,90)
  cube(f'SA_D13_Eleventh{side}Longitudinal_{n}',[x-.1,83.55,a],[x+.1,83.78,b],'D13_street_longitudinal');prior=old_part(f'SA_D13_Tenth{side}Longitudinal_{n}')
  ol,oh=(-82.6,-82.36)if sign==-1 else(82.36,82.6);frame_joint(parts[-1],prior,[x-.1,83.55,ol],[x+.1,83.78,oh])
  az=sign*82.3;tz=sign*89.7
  cube(f'SA_D13_Eleventh{side}RakerAnchor_{n}',[x-.1,83.,az-.1],[x+.1,83.78,az+.1],'D13_source_connected_raker_anchor');frame_joint(parts[-1],prior,[x-.1,83.55,az-.1],[x+.1,83.78,az+.1])
  q=beam(f'SA_D13_Eleventh{side}Raker_{n}',[x,83.1,az],[x,83.64,tz],.18,'D13_under_street_diagonal_raker');rakers.append({'name':q['name'],'anchor_name':f'SA_D13_Eleventh{side}RakerAnchor_{n}','tip_member':f'SA_D13_Eleventh{side}Longitudinal_{n}','anchor_center':[x,83.1,az],'tip_center':[x,83.64,tz],'category':'Geometric raker/truss; primary engineering capacity held'})
 cube(f'SA_D13_Eleventh{side}RakerLowerCrossTie',[-85.9,83.02,sign*82.3-.1],[-82.1,83.18,sign*82.3+.1],'D13_raker_anchor_cross_tie')
 for n,z in enumerate([sign*d for d in [83.3,86.4,89.5]]):cube(f'SA_D13_Eleventh{side}Crossmember_{n}',[-86.05,83.55,z-.1],[-81.95,83.78,z+.1],'D13_street_transverse')
 for bank,x in [('West',-86.05),('East',-81.95)]:
  intervals=[(82.6,84.66),(88.14,90)]if sign==1 else[(-90,-88.14),(-84.66,-82.6)]
  if sign==1 and bank=='East':intervals=[(82.6,90)] # No eastern reservation opposite151: continuous real boundary.
  for n,(a,b)in enumerate(intervals):cube(f'SA_D13_Eleventh{side}{bank}Guard_{n}',[x-.035,84,a],[x+.035,85.1,b],'guard')
 end=sign*90;cube(f'SA_D13_Eleventh{side}TerminalGuard',[-86.05,84,end-.035],[-81.95,85.1,end+.035],'guard')
for room in rooms:
 a=room['allocation'];idx=a['source_envelope_index'];z=sum(a['allocation_z'])/2;xlo,xhi=a['allocation_x']
 for n,v in enumerate([-3.1,0,3.1]):cube(f'SA{idx}_FloorTransverse_{n}',[min(xlo,-85.9),83.55,z+v-.1],[max(xhi,-82.1),83.78,z+v+.1],'D13_room_floor_crossbeam')
 for n,x in enumerate([xlo+.15,(xlo+xhi)/2,xhi-.15]):cube(f'SA{idx}_FloorLongitudinal_{n}',[x-.1,83.55,z-3.6],[x+.1,83.78,z+3.6],'D13_room_floor_longitudinal')
 q=beam(f'SA{idx}_UnderFloorPlanBrace',[xlo+.15,83.64,z-3.1],[xhi-.15,83.64,z+3.1],.12,'D13_under_floor_plan_brace');braces.append({'name':q['name'],'start':[xlo+.15,83.64,z-3.1],'end':[xhi-.15,83.64,z+3.1],'basis':'Exact joist-crossing plan brace; no engineering capacity claim'})
for room in rooms:
 a=room['allocation'];rect=box(a['allocation_x'][0],a['allocation_z'][0],a['allocation_x'][1],a['allocation_z'][1])
 for f in ['Game/data/generated/structural_meshes.json','Game/data/generated/received_structural_meshes.json','Game/data/architecture/CENTRAL_RESIDENTIAL_STREETS.json']:
  for r in json.load(open(R/f))['regions']:
   if r['floor_y']==84:assert unary_union([Polygon(t)for t in r['triangles']]).intersection(rect).area<1e-6,(a['source_envelope_index'],r['id'])
Q={'schema':'astraea.star_atlas_specialty_eleventh_receiving.v1','base_commit':base,'model_file':'StarAtlasSpecialtyEleventhReceiving.glb','parts':parts,'source_pins':pins,'slab_joints':[],'existing_frame_joints':frame_joints,'rakers':rakers,'room_plan_braces':braces,'lower_structural_owners':[],'support_toes':[],'removed_source_guards':[],'removed_previous_guard_meshes':['SA_D13_TenthNorthTerminalGuard','SA_D13_TenthSouthTerminalGuard'],'previous_receiving_model':old['model_file'],'previous_receiving_model_sha256':sha(R/'Game/assets/models'/old['model_file']),'new_street_floor_area_m2':60.68,'new_street_overlap_m2':0,'new_piers':0,'engineering_load_capacity_accepted':False,'geometric_load_path':'Eight exact overlapping connections into retained tenth frame, whose actual slab/preceding-frame joints are independently verified in its retained checkpoint; paired rakers, cross-ties and three room plan braces. No D12 foundation; cumulative cantilever/primary load design remains open.'}
P={'schema':'astraea.star_atlas_specialty_eleventh.v1','base_commit':base,'root_name':'StarAtlasSpecialtyEleventhCandidates','sources':list(sources.values()),'preimage_pins':pins,'rooms':rooms,'selected_source_indices':[145,151,157],'retained_specialty_reservations':46,'physical_interior_batch':3,'new_units':0,'rest_reservations':3,'species_ready_rooms':0,'source_ids_unchanged':True,'limits':['40/46 physical specialty candidates with50reservedrests; D13 complete as physical proposals, remaining6 D14','Primary support/cantilever engineering, canonical bodies/rigs/pose, biology/acoustics/privacy/stock/save and final ordinary Godot/CRT/hardware visual acceptance held']}
write(W/'PLAN.json',P);write(W/'RECEIVING_PLAN.json',Q);write(W/'PREIMAGE_ALLOCATION_CHECK.json',{'status':'PASS','base_commit':base,'indices':[145,151,157],'capacities':{str(i):1 for i in [145,151,157]},'new_units':0,'new_rest_places':0,'ids_changed':0,'remaining_specialty_by_deck':{'D13':0,'D14':6},'dependency_choice':'Final three D13 singles in terminal row; retained tenth frame connections, no D12 foundation/primary engineering certification'});print('ELEVENTH_PREPARED',len(rooms),len(parts),len(frame_joints),len(rakers))
