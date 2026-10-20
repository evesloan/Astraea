"""New fitted Night Garden receiving, never a recovery of missing pilot work."""
from pathlib import Path
import json,hashlib,copy
G=Path(__file__).resolve().parents[2]; B=G.parent/'BlenderCatalogue';OUT=G/'data/architecture/night_garden_specialty_d15_20261020';OUT.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
schedule=B/'assets/residential_production_batch/inputs/PROPOSED_FULL_1000_PRODUCTION_ROWS.json'
assert sha(schedule)=='63f1094d063cfd62e776205d1e4bd3dea40833d203945a448e446fcdd82fc0b6'
rows=json.loads(schedule.read_text())['records'];targets=[r for r in rows if r['deck']=='D15' and r['house']=='starboard_central_upper_house'];assert len(targets)==30
source={}
for f in (G/'data/architecture').glob('STAR_ATLAS_SPECIALTY*.json'):
 for r in json.loads(f.read_text()).get('rooms',[]):
  if 'allocation' in r:source[r['allocation']['source_envelope_index']]=(f,r)
manifest=json.loads((B/'catalogue_manifest.json').read_text()) # inspect whole manifest; no new catalogue ID allocated
p={'schema':'astraea.night_garden_specialty_d15.v1','authorship':'NEW fitted construction using retained authored families, not recovered pilot exports','root_name':'NightGardenD15SpecialtyReceiving20261020','rooms':[],'preimage_pins':{},'new_units':0,'reserved_rest_count':40,'acceptance':{'structural_connection':'pending focused check','occupied_capacity':False,'species_environment':False,'private_admission':False,'final_visual':False,'whole_ship_regression':False},'limits':['No new authoritative addresses, beds, species assignments or operational environmental systems.','Exact reservation/rest anchors preserved. Original source GLBs and80 adopted Night Garden homes unchanged.','Water/glass/material overhaul and final architecture acceptance remain a later ship-wide phase.']}
for target in targets:
 i=target['source_envelope_index'];f,s=source[i-3];a=s['allocation'];assert a['allocation_x']==[-target['allocation_x'][1],-target['allocation_x'][0]] and a['allocation_z']==target['allocation_z'] and a['proposed_rest_place_count']==target['proposed_rest_place_count']
 src=G/'assets/models'/s['model_file'];assert sha(src)==s['model_sha256'];p['preimage_pins'][str(src.relative_to(G))]=sha(src)
 r={'allocation':target,'source_contract':str(f.relative_to(G)),'source_contract_sha256':sha(f),'source_model_file':s['model_file'],'source_model_sha256':s['model_sha256'],'model_file':f'NightGardenD15Specialty_{i}_r001.glb','source_profile':s['profile_proposal'],'doors':copy.deepcopy(s['doors']),'lights':copy.deepcopy(s['lights']),'rest_adjustments':[],'source_components':copy.deepcopy(s['components'])}
 for d in r['doors']:
  d['position'][0]*=-1;d['yaw']*=-1;d['persistent_id']=d['persistent_id'].replace(a['proposed_runtime_id'],target['proposed_runtime_id'])
 for light in r['lights']:light['position'][0]*=-1
 rests=[c for c in s['components'] if 'rest_slot_id' in c]
 assert len(rests)==target['proposed_rest_place_count']==len(target['historical_bed_anchor_markers'])
 for j,(c,anchor) in enumerate(zip(rests,target['historical_bed_anchor_markers'])):
  pos=c['position'];r['rest_adjustments'].append({'component_name':c['name'],'source_position':pos,'target_position':[anchor['x'],target['floor_y'],anchor['z']],'mirrored_delta':[anchor['x']+pos[0],0,anchor['z']-pos[2]],'slot_id':target['proposed_rest_slot_ids'][j],'catalogue_id':c['catalogue_id']})
 p['rooms'].append(r)
assert sum(r['allocation']['proposed_rest_place_count'] for r in p['rooms'])==40
for name in ['scripts/central_homes_adoption.gd','scripts/starboard_house_upper.gd','data/architecture/NIGHT_GARDEN_UNITS.json','assets/models/AST-COM-003.glb','data/generated/structural_meshes.json','data/generated/received_structural_meshes.json']:
 p['preimage_pins'][name]=sha(G/name)
(OUT/'PACKAGE.json').write_text(json.dumps(p,indent=2)+'\n')
print('Prepared30 new fitted rooms/40 immutable reserved rest slots. No production runtime mutation yet.')
