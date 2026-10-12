"""Preserve every failed criterion; distinguish source holds from bounded tests."""
from pathlib import Path
import json,hashlib
HERE=Path(__file__).resolve().parents[1];ROOT=HERE.parents[4]
raw=ROOT/'Game/artifacts/group3_d03_streets_20261011/streets.json';r=json.load(open(raw));p=json.load(open(HERE/'source/REMAINING_STREETS_CONTRACT.json'))
allowed={'D04SC_LowerServiceWall_1','D04SC_LowerServiceWall_7','SAC_LowerScreen_3','SAC_LowerScreen_5','PACO_D04SC_LowerServiceWall_1','PACO_D04SC_LowerServiceWall_7'}
assert r['status']=='HOLD_UNEXPECTED' # Exact retained engine receipt, never rewritten.
assert len(r['walks'])==38 and all(w['reached']and w['floor_contact']for w in r['walks'])
assert r['actual_door_motion_samples']==40 and r['route_position_velocity_writes']==0
for file,h in r['source_model_pins'].items():assert hashlib.sha256((ROOT/'Game/assets/models/group3_d03_streets_20261011'/file).read_bytes()).hexdigest()==h
assert len(r['preserved_block_witnesses'])==11
for witness in r['preserved_block_witnesses']:
 assert witness['colliders']
 for path in witness['colliders']:assert '/Districts/'in path and any('/'+name+'/'in path for name in allowed),path
floors=[];workers=[]
for error in r['errors']:
 if error.startswith('worker_'):workers.append(error)
 elif error.startswith('floor_exact_held_'):
  assert error.replace('floor_','worker_',1)in r['errors'];floors.append(error)
 else:raise AssertionError('Unexpected non-interface failure: '+error)
assert len(workers)==11 and len(floors)==2
q=dict(status='HOLD_PRESERVED_D04_CROSSINGS',kind='Derived scope readiness; not a replacement engine result',raw_engine_status=r['status'],raw_receipt_sha256=hashlib.sha256(raw.read_bytes()).hexdigest(),actual_main_checks=r['checks'],bounded_normal_W_walks_passed=38,actual_door_motion_samples_without_fixed_contacts=40,disclosed_independent_actor_setups=r['independent_actor_setup_placements'],intra_route_position_or_velocity_writes=0,route_floor_worker_probes=r['whole_network_worker_floor_probes'],failed_worker_criteria_preserved=workers,failed_floor_criteria_at_closed_source_wall_positions_preserved=floors,exact_original_source_wall_owners=sorted(allowed),held_crossing_zones=p['held_main_crossings'],current_composite_unrelated_live_cells_preserved=r['current_composite_unrelated_live_cells_retained'],no_other_failed_physics_criteria=True,continuous_staff_network_accepted=False,full_group_accepted=False,aggregation_fix='Future test aggregation records failed exact-wall floor witnesses as interface holds. Criteria remain false; raw tested receipt and tested script retained. Latest script parse-checked, full physics not repeated for aggregation-only change.')
(HERE/'qa/CLASSIFIED_SCOPE_READINESS.json').write_text(json.dumps(q,indent=2)+'\n');(ROOT/'Game/artifacts/group3_d03_streets_20261011/classified_readiness.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q))
