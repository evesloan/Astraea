"""Pinned, additive Group2 inventory. Does not edit a receiving registry."""
import collections, hashlib, json, pathlib
ROOT=pathlib.Path(__file__).resolve().parent
INPUT=ROOT/'inputs'
def read(p): return json.loads((INPUT/p).read_text(encoding='utf-8'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
proposal=read('Game/data/architecture/D17_LUXURY_HOUSES_PROPOSAL.json')
production=read('BlenderCatalogue/assets/residential_production_batch/inputs/PROPOSED_FULL_1000_PRODUCTION_ROWS.json')
runtime=read('Game/data/architecture/D17_CONNECTED_HOUSE_RUNTIME.json')
lookup={r['source_envelope_index']:r for r in production['records']}
assert len(lookup)==1000
records=[]
for r in proposal['replacements']:
    old=lookup[r['source_envelope_index']]
    assert old['proposed_family']==r['tier']
    assert old['candidate_layout']['proposed_floor_boundary']==r['proposed_floor_boundary']
    identity={k:old.get(k) for k in ['source_envelope_index','allocation_sha256','proposed_runtime_id','runtime_id_status','historical_persistent_id','historical_address','historical_class','historical_bed_anchor_markers','historical_door_marker_xz','proposed_rest_place_count','proposed_rest_slot_ids','rest_slot_id_status','existing_partial_construction']}
    record={'identity':identity,'reservation':r,'construction_status':'UNBUILT','installed_acceptance':False,'exclusive_scope':'Inside this existing-unit replacement reservation; root retains public commons, streets, floor compiler and controllers','new_guest_units':0,'species_assignment':None,'habitat_taxonomy_status':'Confirmed aquatic and quiet needs; final required taxonomy and tier mix remain open. No demographic quotas.'}
    if r['source_envelope_index']==790:
        record['protected_existing_geometry']={'asset':'AST-RES-006','lower_boundary':runtime['floor_regions'][3]['boundary'],'preserve_native_and_export':True,'entry':runtime['private_arrival'],'stair_lift_service':runtime['reservations'],'roof_policy':'Continuous retained lower roof has no hole. Any future upper connection needs an explicit bounded successor preserving retained originals and unaffected objects.'}
    record['D18_dependencies']=[x for x in proposal['historical_D18_overlap_dependencies'] if x['luxury_proposal_key']==r['proposal_key']]
    records.append(record)
counts=collections.Counter(r['reservation']['tier'] for r in records)
assert dict(counts)=={'deluxe':50,'premium':25,'royalty':5,'supreme':1}
assert len({x['identity']['source_envelope_index'] for x in records})==81
assert sum(x['identity']['proposed_rest_place_count'] for x in records)==400
safe_other=[x for x in production['records'] if x['source_envelope_index'] not in {r['identity']['source_envelope_index'] for r in records}]
assert len(safe_other)==919
data={'schema':'astraea.group2_luxury_source_inventory.v1','checkpoint':'77a745750169a8ee853e71785f82fd2862bdaba5','owner':'Eve','scope':'81 existing-unit luxury replacements; source proposals only, no registry/save/capacity migration','counts':dict(counts),'source_unit_total':1000,'unaffected_other_units':919,'maximum_proposed_luxury_rest_places':400,'actual_authored_rest_anchors':0,'passenger_admission_cap':2000,'physical_ship_rest_ledger':'Unreconciled; admission limit is not a physical-rest total','records':records,'protected_Group1_standard_D17_indices':proposal['retained_D17_standard_source_indices'],'private_handoff':'Owner-approved unique Group2 branch; publication not yet performed','source_hashes':{str(p.relative_to(INPUT)):sha(p) for p in [INPUT/'Game/data/architecture/D17_LUXURY_HOUSES_PROPOSAL.json',INPUT/'BlenderCatalogue/assets/residential_production_batch/inputs/PROPOSED_FULL_1000_PRODUCTION_ROWS.json',INPUT/'Game/data/architecture/D17_CONNECTED_HOUSE_RUNTIME.json']}}
(ROOT/'LUXURY_81_INVENTORY.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
print('Exact joined luxury inventory:',len(records),dict(counts),'400 maxima, 0 authored anchors; no new units.')
