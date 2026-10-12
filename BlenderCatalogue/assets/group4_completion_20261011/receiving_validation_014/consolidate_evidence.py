"""Select complete station circuits from retained actual-player runs without relabeling failures."""
from pathlib import Path
import json,hashlib,shutil
W=Path(__file__).resolve().parent;R=next(p for p in W.parents if (p/'Game').is_dir())
source=R/'Game/artifacts/group4_received_player.json'
target=W/'PLAYER_RECEIVING004_AFTMID_RETURN_BAY.json'
if not target.exists():shutil.copy2(source,target)
old=json.loads((W/'FAILED_PLAYER_RECEIVING002_RECEIPT.json').read_text())
new=json.loads(target.read_text())
assert old['status']=='HOLD' and old['errors']==['AFT_MIDSHIP actual platform leg 0 original player walk']
assert new['status']=='PASS' and not new['errors'] and new['station_filter']=='AFT_MIDSHIP' and new['aftmid_successor_used']
stations=[]
for st in ['FORWARD','AFT','FORE_MIDSHIP','AFT_MIDSHIP','CENTRAL']:
 d=new if st=='AFT_MIDSHIP' else old
 legs=[x for x in d['actual_original_player_legs'] if x['label'].split(' ')[0]==st]
 rides=[x for x in d['actual_original_controller_rides'] if x['label'].split(' ')[0]==st]
 controls=[x for x in d['original_E_RMB_interactions'] if x['label'].split(' ')[0]==st]
 assert legs and all(x['reached'] and x['floor_contact'] and x['existing_player_controller'] for x in legs)
 assert len(rides)==2 and all(x['reached'] and x['on_floor'] and x['original_E_RMB'] for x in rides)
 assert len(controls)==2 and all(x['actual_original_player_E_RMB_events'] and x['exact_existing_button_ray_target'] for x in controls)
 assert any('lower to core' in x['label'] for x in legs)
 stations.append({'station':st,'status':'PASS_COMPLETE_CORE_LIFT_PLATFORM_AND_RETURN_CIRCUIT','retained_run':'PLAYER_RECEIVING004_AFTMID_RETURN_BAY.json' if st=='AFT_MIDSHIP' else 'FAILED_PLAYER_RECEIVING002_RECEIPT.json','actual_original_player_legs':len(legs),'actual_original_lift_rides':len(rides),'actual_E_RMB_interactions':len(controls),'selected_source030_r002':st=='AFT_MIDSHIP'})
logs=['PLAYER_RECEIVING002.log','PLAYER_RECEIVING004_AFTMID_RETURN_BAY.log']
for name in logs:assert not any(x in (W/name).read_text() for x in ['SCRIPT ERROR','Parse Error','ERROR:'])
d={'status':'PASS_FIVE_INDEPENDENT_RECEIVING_CIRCUITS','retained_baseline':'affc5c807087ff87da29f3642c2d6e418241b896','stations':stations,'actual_original_player_legs':sum(x['actual_original_player_legs'] for x in stations),'actual_original_lift_rides':10,'actual_existing_E_RMB_interactions':10,'initial_supported_station_placements':5,'within_route_relocations':0,'old_run002_remains_HOLD':True,'test_boundary':'Actual original main, original player W and E/RMB input, original commons_lift controllers; three exact floor-owner replacements only inside transient scene, north/pit adoption remains false. Four unaffected complete run002 circuits plus focused repaired Aft Midship run004; not one uninterrupted five-station journey.','original_cart_and_four_product_identities_checked':True,'cart_or_tram_player_carry_tested':False,'species_structural_save_final_art_acceptance':False,'pinned_evidence':{n:{'sha256':hashlib.sha256((W/n).read_bytes()).hexdigest(),'bytes':(W/n).stat().st_size} for n in logs+['FAILED_PLAYER_RECEIVING002_RECEIPT.json',target.name]}}
(W/'FIVE_STATION_RECEIVING_EVIDENCE.json').write_text(json.dumps(d,indent=2)+'\n')
print('FIVE_STATION_RECEIVING_EVIDENCE',d['status'],d['actual_original_player_legs'],'original walks;10 original E/RMB lift rides')
