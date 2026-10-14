from pathlib import Path
import json,hashlib
C=Path(__file__).parent;R=Path('/workspace/astraea-protected-integration-20261012');G=R/'Game';P=C/'consolidated_all_eight_20261013';P.mkdir(exist_ok=True)
v=json.loads((C/'PORTCENTRAL_ADJUNCT_CARE_REMOTE_VERIFICATION.json').read_text());assert v['publication_status']=='VERIFIED'and v['changed_file_readbacks']==140
maps={}
for i in range(2,9):
 q=R/f'RetainedConstruction/group{i}/SOURCE_MAP.json';maps[i]=json.loads(q.read_text())
def source(group,path):
 row=next(x for x in maps[group]['files']if x['source_path']==path);q=R/row['storage_path'];assert q.is_file()and q.stat().st_size==row['bytes']and hashlib.sha256(q.read_bytes()).hexdigest()==row['sha256'],path
 return json.loads(q.read_text())
floor=source(2,'Game/data/group2_completion/FLOOR_INTERFACE.json');rooms=[]
for row in maps[2]['files']:
 p=row['source_path']
 if p.startswith('Game/data/group2_completion/contracts/')and p.endswith('.json'):
  key=Path(p).stem
  if not key.isdigit():continue
  d=source(2,p);entry=next(x for x in d['markers']if x['name']=='DATUM_entry');rooms.append({'key':key,'entry':entry['world_xyz'],'contract_sha256':row['sha256'],'identity':d['identity'],'reservation':d['reservation'],'floor_owner':d['floor_owner']})
assert len(rooms)==80
g7=json.loads((G/'data/architecture/GROUP7_COMPLETION.json').read_text());assert len(g7['models'])==69
for row in g7['models']:assert hashlib.sha256((G/'assets/models'/row['file']).read_bytes()).hexdigest()==row['sha256']
plan={'base_commit':v['published_commit'],'groups':json.loads((R/'CONSOLIDATED_CONSTRUCTION_INVENTORY.json').read_text())['groups'],'G2_floor_rows':floor['rows'],'G2_proposed_floor_area_m2':floor['missing_m2'],'G2_homes':rooms,'G2_private_vertical':source(2,'Game/data/group2_private_vertical/INTERFACES.json'),'G2_wet':source(2,'Game/data/group2_vip_pavilions/KITS_r003.json'),'G7_selected_models':g7['models'],'G7_remaining_models_held':19,'new_tram_or_primary_structural_design_selected':False,'original_sources_or_runtime_ids_changed':False};(P/'CONSOLIDATED_PLAN.json').write_text(json.dumps(plan,indent=2)+'\n');print('COMBINED_PLAN',len(rooms),'homes',len(floor['rows']),'floor regions','G7',len(g7['models']),'existing selected models;all8groups accounted')
