from pathlib import Path
import copy,json,hashlib,math,subprocess
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
W=Path(__file__).resolve().parent;R=W.parents[2];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();write=lambda p,v:p.write_text(json.dumps(v,indent=2)+'\n')
base='3799962d34d3a0b59620fc22aad0cb49497aa373';assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=R).decode().strip()==base
rows=json.load(open(R/'BlenderCatalogue/assets/residential_production_batch/inputs/PROPOSED_FULL_1000_PRODUCTION_ROWS.json'))['records'];S=json.load(open(R/'Game/data/architecture/CENTRAL_RESIDENTIAL_STREETS.json'));H=json.load(open(R/'Game/data/architecture/STAR_ATLAS_EIGHT_HABITATS.json'));rooms=[];pins={};parts=[];joins=[]
inputs=['BlenderCatalogue/assets/residential_production_batch/inputs/PROPOSED_FULL_1000_PRODUCTION_ROWS.json','BlenderCatalogue/catalogue_manifest.json','Game/data/architecture/CENTRAL_RESIDENTIAL_STREETS.json','Game/data/architecture/STAR_ATLAS_UNITS.json','Game/data/generated/structural_meshes.json','Game/data/generated/received_structural_meshes.json','Game/docs/master_source/MASTER_CURRENT_APPLICATION.json','Game/docs/master_source/MASTER_FULL_CONTENT_INDEX.json','BlenderCatalogue/references/intimate/image(20261002-000722).png','BlenderCatalogue/references/aquatic/image(20261001-035517).png']
for p in inputs:pins[p]=sha(R/p)
templates={503:json.load(open(R/'Game/data/architecture/STAR_ATLAS_SPECIALTY_SEVENTH.json')),443:json.load(open(R/'BlenderCatalogue/assets/star_atlas_low_rest_adaptation_20261010/RUNTIME_PLAN.json')),491:json.load(open(R/'BlenderCatalogue/assets/star_atlas_low_rest_adaptation_20261010/RUNTIME_PLAN.json'))}
sources={a['catalogue_id']:a for p in templates.values()for a in p['sources']}
for idx,sourceidx,profile in [(103,503,'screened_street_cocoon_folio'),(109,443,'quiet_cocoon_north_library'),(115,491,'quiet_cocoon_folio_gallery')]:
 row=next(r for r in rows if r['source_envelope_index']==idx);assert row['deck']=='D13'and row['proposed_rest_place_count']==1 and len(row['proposed_rest_slot_ids'])==1
 src=next(r for r in templates[sourceidx]['rooms']if r['allocation']['source_envelope_index']==sourceidx);room=copy.deepcopy(src);old=room['allocation'];delta=[sum(row['allocation_x'])/2-sum(old['allocation_x'])/2,row['floor_y']-old['floor_y'],sum(row['allocation_z'])/2-sum(old['allocation_z'])/2];move=lambda v:[v[i]+delta[i]for i in range(3)]
 pins['Game/assets/models/'+src['model_file']]=sha(R/'Game/assets/models'/src['model_file'])
 room['allocation']=row;room['profile_proposal']=profile;room['layout']=profile;room['model_file']=f'StarAtlasSpecialty_{idx}.glb';room['proposed_design_species']='Mantelids';room['species_ready']=False;room['orientation_yaw']=math.pi if idx==103 else 0
 room['parts']=[q for q in room['parts']if q['category']!='receiving']
 for q in room['parts']:q['name']=q['name'].replace(f'SA{sourceidx}_',f'SA{idx}_');q['verts']=[move(v)for v in q['verts']]
 for b in room['components']:
  b['position']=move(b['position'])
  if 'rest_slot_id'in b:b['rest_slot_id']=row['proposed_rest_slot_ids'][0]
 for d in room['doors']:d['position']=move(d['position']);d['persistent_id']=row['proposed_runtime_id']+(':'+d['name'].lower())
 for light in room['lights']:light['position']=move(light['position'])
 rest=next(b for b in room['components']if b['catalogue_id']=='AST-RST-QC-001')
 if sourceidx==503:
  for f in room['rest_fittings']:
   f['rest_slot_id']=row['proposed_rest_slot_ids'][0];f['binding']=rest;f['frame_origin']=move(f['frame_origin']);f['approach_world']=move(f['approach_world']);f['actual_reference_bottom_contacts_world']=[move(v)for v in f['actual_reference_bottom_contacts_world']]
 else:
  h=next(r for r in H['rooms']if r['source_envelope_index']==sourceidx);d=copy.deepcopy(h['privacy_door']);d.update(name='CocoonPrivacyDoor_01',position=move(d['position']),persistent_id=row['proposed_rest_slot_ids'][0]+':privacy',controller='cocoon_privacy_door.gd');room['doors'].append(d)
  room['rest_fittings']=[{'rest_slot_id':row['proposed_rest_slot_ids'][0],'binding':rest,'frame_origin':rest['position'],'yaw':rest['yaw'],'approach_world':move(h['approach_world']),'actual_reference_bottom_contacts_world':[move(v)for v in h['rest_contacts_world']],'privacy_door_name':d['name'],'environment_role':'Closed lined quiet cocoon; canonical body/rig, acoustics and molting operations held'}]
 for key in ['receiving_contacts','below_unit','previous_model_binding','historical_profile_proposal','design_adaptation']:room.pop(key,None)
 room['receiving_contacts']=[];room['window_view']='Actual shared D13 street-facing screened activity bay'if idx==103 else'Inner-bank internal outlook; retained geometry, final court composition acceptance held'
 room['operations_hold']=['canonical species/body/rig/pose','acoustic attenuation/molting/biology','privacy permission/stock/save','engineering load capacity/final runtime visuals'];rooms.append(room)
def cube(name,lo,hi,category):
 verts=[[x,y,z]for z in [lo[2],hi[2]]for y in [lo[1],hi[1]]for x in [lo[0],hi[0]]];parts.append({'name':name,'verts':verts,'faces':[[0,2,3,1],[4,5,7,6],[0,1,5,4],[2,6,7,3],[0,4,6,2],[1,3,7,5]],'category':category,'runtime_collision':True})
streetowners={r['id']:r for r in S['regions']};north=streetowners['D13_STAR_ATLAS_MISSING_STREET_0'];south=streetowners['D13_STAR_ATLAS_MISSING_STREET_3'];assert north['floor_y']==south['floor_y']==84 and north['thickness']==south['thickness']==.24
def joint(name,lo,hi,owner):
 assert unary_union([Polygon(t)for t in owner['triangles']]).buffer(1e-7).covers(box(lo[0],lo[2],hi[0],hi[2]));assert lo[1]==83.76 and hi[1]<=84
 joins.append({'name':name,'owner':owner['id'],'overlap_bounds':[lo,hi],'source_bottom':83.76,'floor_y':84,'source_thickness':.24,'basis':'Geometric overlap into exact retained D13 slab; engineering load/cantilever capacity held'})
for room in rooms:
 idx=room['allocation']['source_envelope_index'];row=room['allocation'];z=sum(row['allocation_z'])/2;xlo,xhi=row['allocation_x'];owner=north if idx==109 else south
 for n,v in enumerate([-3.1,0,3.1]):
  zz=z+v;cube(f'SA{idx}_FloorTransverse_{n}',[min(xlo,-85.9),83.55,zz-.10],[max(xhi,-82.1),83.78,zz+.10],'D13_room_floor_crossbeam')
  if idx==109:joint(parts[-1]['name'],[-85.9,83.76,zz-.1],[-82.1,83.78,zz+.1],north)
 for n,x in enumerate([xlo+.15,(xlo+xhi)/2,xhi-.15]):cube(f'SA{idx}_FloorLongitudinal_{n}',[x-.1,83.55,z-3.6],[x+.1,83.78,z+3.6],'D13_room_floor_longitudinal')
# South missing-only7.4m street; two full-width overlap plates tie its frame into the retained slab.
cube('SA_D13_NinthSouthStreetFloor',[-86.05,83.76,67.8],[-81.95,84,75.2],'D13_street_extension_floor')
for n,x in enumerate([-85.8,-82.2]):
 cube(f'SA_D13_NinthSouthLongitudinal_{n}',[x-.1,83.55,67.56],[x+.1,83.78,75.2],'D13_street_longitudinal');joint(parts[-1]['name'],[x-.1,83.76,67.56],[x+.1,83.78,67.8],south)
for n,z in enumerate([68.5,71.6,74.7]):cube(f'SA_D13_NinthSouthCrossmember_{n}',[-86.05,83.55,z-.1],[-81.95,83.78,z+.1],'D13_street_transverse')
for side,x in [('West',-86.05),('East',-81.95)]:
 for n,(a,b)in enumerate([(67.8,69.86),(73.34,75.2)]):cube(f'SA_D13_NinthSouth{side}Guard_{n}',[x-.035,84,a],[x+.035,85.1,b],'guard')
cube('SA_D13_NinthSouthTerminalGuard',[-86.05,84,75.165],[-81.95,85.1,75.235],'guard')
for n,(a,b)in enumerate([(-75.2,-73.34),(-69.86,-67.821)]):cube(f'SA_D13_NinthNorthEastGuard_{n}',[-81.985,84,a],[-81.915,85.1,b],'guard')
guards=[e for e in S['exposed_edge_guards']if e['id']in['D13_STAR_ATLAS_MISSING_STREET_0_Guard_6','D13_STAR_ATLAS_MISSING_STREET_3_Guard_23']];assert len(guards)==2
for room in rooms:
 rect=box(*[room['allocation']['allocation_x'][0],room['allocation']['allocation_z'][0],room['allocation']['allocation_x'][1],room['allocation']['allocation_z'][1]])
 for f in ['Game/data/generated/structural_meshes.json','Game/data/generated/received_structural_meshes.json','Game/data/architecture/CENTRAL_RESIDENTIAL_STREETS.json']:
  for owner in json.load(open(R/f))['regions']:
   if owner['floor_y']==84:assert unary_union([Polygon(t)for t in owner['triangles']]).intersection(rect).area<1e-6,(room['allocation']['source_envelope_index'],owner['id'])
Q={'schema':'astraea.star_atlas_specialty_ninth_receiving.v1','base_commit':base,'model_file':'StarAtlasSpecialtyNinthReceiving.glb','parts':parts,'source_pins':pins,'slab_joints':joins,'lower_structural_owners':[],'support_toes':[],'removed_source_guards':guards,'new_street_floor_area_m2':30.34,'new_street_overlap_m2':0,'new_piers':0,'engineering_load_capacity_accepted':False,'geometric_load_path':'Retained north D13 slab directly receives three room transverse overlaps; retained south D13 slab receives two longitudinal0.24m joins into7.4m missing-only street frame and the two rooms transverse/longitudinal network. No D12 floor exists below this ROI; primary engineering/load capacity held.'}
P={'schema':'astraea.star_atlas_specialty_ninth.v1','base_commit':base,'root_name':'StarAtlasSpecialtyNinthCandidates','sources':list(sources.values()),'preimage_pins':pins,'rooms':rooms,'selected_source_indices':[103,109,115],'retained_specialty_reservations':46,'physical_interior_batch':3,'new_units':0,'rest_reservations':3,'species_ready_rooms':0,'source_ids_unchanged':True,'limits':['33/46 specialty interiors now physical candidates;43rests;remaining7 D13 +6 D14','Engineering load/cantilever capacity, canonical bodies/rigs/pose, biological/privacy/stock/save operations and final ordinary Godot/CRT/hardware visuals held']}
write(W/'PLAN.json',P);write(W/'RECEIVING_PLAN.json',Q);write(W/'PREIMAGE_ALLOCATION_CHECK.json',{'status':'PASS','base_commit':base,'indices':[103,109,115],'capacities':{'103':1,'109':1,'115':1},'new_units':0,'new_rest_places':0,'ids_changed':0,'remaining_specialty_by_deck':{'D13':7,'D14':6},'dependency_choice':'Lowest remaining deck, first incomplete row at±71.6; exact retained D13 street slabs as geometric frame anchors; D12 support absent and engineering capacity held'});print('NINTH_PREPARED',len(rooms),len(parts),len(joins))
