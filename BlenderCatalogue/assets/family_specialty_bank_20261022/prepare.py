from pathlib import Path
import json,hashlib,copy,math,collections,shutil
R=Path('/workspace/Astraea-recovered-e6274e77-20261021');G=R/'Game';P=G/'family_specialty_bank_20261022';N=R/'BlenderCatalogue/assets/family_specialty_bank_20261022';P.mkdir(exist_ok=False);N.mkdir(exist_ok=False);(P/'runtime').mkdir();(P/'evidence').mkdir();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ledger=next((R/'BlenderCatalogue/assets/residential_hotels/aft_houses_20261007_r001').rglob('ALL_1000_CURRENT_HOTEL_SOURCE_APPLICATION.json'));allunits=json.loads(ledger.read_text())['units'];targets=[x for x in allunits if x.get('house')=='starboard_aft_upper_house'and x.get('production_lane')=='specialty_family_design_and_fit'];sourcepath=G/'sunset_specialty_bank_20261022/PACKAGE_R002.json';source=json.loads(sourcepath.read_text());rows=[];pins={str(ledger.relative_to(R)):sha(ledger),str(sourcepath.relative_to(R)):sha(sourcepath)}
for target in targets:
 a=copy.deepcopy(target);a['floor_y']={13:84,14:88.5,15:93}[int(a['deck'][1:])]
 possible=[r for r in source['rooms']if r['allocation']['deck']==a['deck']and r['allocation']['proposed_rest_place_count']==a['proposed_rest_place_count']and abs(sum(r['allocation']['allocation_x'])+sum(a['allocation_x']))<.001 and abs((r['allocation']['allocation_z'][1]-r['allocation']['allocation_z'][0])-(a['allocation_z'][1]-a['allocation_z'][0]))<.001]
 assert possible,(a['source_envelope_index'],a['allocation_x']);s=min(possible,key=lambda r:abs(sum(r['allocation']['allocation_z'])-sum(a['allocation_z'])));dz=(sum(a['allocation_z'])+sum(s['allocation']['allocation_z']))/2
 def move(v):return [-v[0],v[1],-v[2]+dz]
 r=copy.deepcopy(s);oldid=s['allocation']['proposed_runtime_id'];newid=a['proposed_runtime_id'];r['allocation']=a
 for field in ['components','doors','lights']:
  for obj in r[field]:
   if 'position'in obj:obj['position']=move(obj['position'])
   if 'yaw'in obj:obj['yaw']+=math.pi
   for key in ['persistent_id','rest_slot_id']:
    if key in obj:obj[key]=obj[key].replace(oldid,newid)
 assert {c['rest_slot_id']for c in r['components']if 'rest_slot_id'in c}==set(a['proposed_rest_slot_ids'])
 idx=int(s['allocation']['source_envelope_index']);native=R/f'BlenderCatalogue/assets/sunset_specialty_bank_20261022/SunsetSpecialty_{idx}_r001.blend';assert native.exists();pins[str(native.relative_to(R))]=sha(native)
 r.update(source_room_model=s['model_file'],source_room_identity=oldid,source_native=str(native.relative_to(R)),source_native_sha256=sha(native),placement={'yaw':math.pi,'translation':[0,0,dz]},model_file=f'FamilySpecialty_{a["source_envelope_index"]}_r001.scn',window_view={'target':'retained Family Terrace court; receiving sightline validation pending','exterior_opening':False,'visual_accepted':False},receiving_contacts={'status':'HELD pending actual installed Family owners and controller connection'},species_ready=False)
 rows.append(r)
plan={'schema':'astraea.family.specialty.bank.v1','protected_parent':'40b62c1ee0b116a6e1e1d397fa8bf761c27f159a','rooms':rows,'pins':pins,'room_count':len(rows),'reserved_rests':sum(r['allocation']['proposed_rest_place_count']for r in rows),'new_capacity':0,'main_integrated':False,'status':'UNFINISHED prepared physical bank; receiving guards remain closed'}
assert len(rows)==47;assert shutil.disk_usage(R).free>500_000_000
(P/'PLAN.json').write_text(json.dumps(plan,indent=2)+'\n');shutil.copyfile(__file__,N/'prepare.py');print('FAMILY47',plan['reserved_rests'],'rests',len(pins),'source pins',len(set(r['source_native']for r in rows)),'native references')
