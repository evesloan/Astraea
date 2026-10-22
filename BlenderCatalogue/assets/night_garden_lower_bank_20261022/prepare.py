from pathlib import Path
import json,hashlib,copy,math,shutil
R=Path('/workspace/Astraea-recovered-e6274e77-20261021');G=R/'Game';P=G/'night_garden_lower_bank_20261022';N=R/'BlenderCatalogue/assets/night_garden_lower_bank_20261022';P.mkdir(exist_ok=True);N.mkdir(exist_ok=True);(P/'runtime').mkdir(exist_ok=True);(P/'evidence').mkdir(exist_ok=True);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ledger=next((R/'BlenderCatalogue/assets/residential_hotels/aft_houses_20261007_r001').rglob('ALL_1000_CURRENT_HOTEL_SOURCE_APPLICATION.json'));units=json.loads(ledger.read_text())['units'];targets=[q for q in units if q['house']=='starboard_central_upper_house' and q['production_lane']=='specialty_family_design_and_fit' and q['deck']in ['D13','D14']];sourcepath=G/'family_specialty_bank_20261022/PACKAGE_R002.json';source=json.loads(sourcepath.read_text());pins={str(ledger.relative_to(R)):sha(ledger),str(sourcepath.relative_to(R)):sha(sourcepath)};rows=[]
for a0 in targets:
 a=copy.deepcopy(a0);a['floor_y']={'D13':84,'D14':88.5}[a['deck']]
 possible=[q for q in source['rooms'] if q['allocation']['deck']==a['deck'] and q['allocation']['proposed_rest_place_count']==a['proposed_rest_place_count'] and abs(q['allocation']['allocation_x'][0]+40-a['allocation_x'][0])<.001 and abs((q['allocation']['allocation_z'][1]-q['allocation']['allocation_z'][0])-(a['allocation_z'][1]-a['allocation_z'][0]))<.001]
 assert possible,a['source_envelope_index'];s=min(possible,key=lambda q:abs((q['allocation']['allocation_z'][0]>0)-(a['allocation_z'][0]>0)));dz=(sum(a['allocation_z'])-sum(s['allocation']['allocation_z']))/2
 r=copy.deepcopy(s);oldid=s['allocation']['proposed_runtime_id'];newid=a['proposed_runtime_id'];r['allocation']=a
 for field in ['components','doors','lights']:
  for obj in r[field]:
   if 'position'in obj:obj['position']=[obj['position'][0]+40,obj['position'][1],obj['position'][2]+dz]
   for key in ['persistent_id','rest_slot_id']:
    if key in obj:obj[key]=obj[key].replace(oldid,newid)
 assert {c['rest_slot_id']for c in r['components']if 'rest_slot_id'in c}==set(a['proposed_rest_slot_ids'])
 r.update(source_room_model=s['model_file'],source_room_identity=oldid,runtime_translation=[40,0,dz],placement={'yaw':math.pi,'translation':[40,0,s['placement']['translation'][2]+dz]},model_file=f'NightGardenLower_{a["source_envelope_index"]}_r001.tscn',window_view={'target':'retained Night Garden inner court or legal outer frontage — exact current enclosure/neighbor checks pending','exterior_opening':False,'visual_accepted':False},receiving_contacts={'status':'HELD: actual existing receiving floor/support and guards must be verified before connection'},species_ready=False)
 # New allocation does not inherit another bank's historical receiving acceptance.
 r.pop('model_sha256',None);r.pop('full_path',None)
 pins[r['source_native']]=sha(R/r['source_native']);rows.append(r)
assert len(rows)==17
plan={'schema':'astraea.night_garden.lower17.v1','protected_parent':'ea6f59c404e500878cdccc60b60d82766c616a6a','rooms':rows,'pins':pins,'room_count':17,'reserved_rests':sum(r['allocation']['proposed_rest_place_count']for r in rows),'new_capacity':0,'main_integrated':False,'status':'UNFINISHED authored candidate; exact receiving/support/privacy/outlook gate pending; production guards unchanged'}
(P/'PLAN.json').write_text(json.dumps(plan,indent=2)+'\n');shutil.copyfile(__file__,N/'prepare.py');print(dict(rooms=17,rests=plan['reserved_rests'],native_sources=len(set(r['source_native']for r in rows)),free=shutil.disk_usage(R).free))
