from pathlib import Path
import json,math,copy,hashlib
R=Path('/workspace/shared/Astraea_direct_recovery_20261008_hcozu5z4');O=R/'BlenderCatalogue/assets/tidal_aquatic_singles_20261009';(O/'source').mkdir(parents=True,exist_ok=True);B=R/'BlenderCatalogue/assets/tidal_specialty_single_20261009';base=json.load(open(B/'PLAN.json'));rows=json.load(open(R/'BlenderCatalogue/assets/residential_production_batch/inputs/PROPOSED_FULL_1000_PRODUCTION_ROWS.json'))['records'];rows=[q for q in rows if q['house']=='port_forward_upper_house'and q['historical_class']=='specialty_unsplit'and q['deck']=='D14'and q['proposed_rest_place_count']==1];assert len(rows)==5
summary=[];old=json.load(open(R/'BlenderCatalogue/assets/tidal_specialty_d13_batch_20261009/BATCH_PLAN.json'));cuts=copy.deepcopy(old['entry_cuts_including_retained_102'])
for row in rows:
 idx=row['source_envelope_index'];mirror=row['allocation_x'][0]>-45;center=sum(row['allocation_z'])/2;dz=center+298.4
 def point(v):return [(-88-v[0])if mirror else v[0],v[1]+4.5,v[2]+dz]
 p=copy.deepcopy(base);p['allocation']=row;p['composition_variant']='aquatic_single_east_garden'if mirror else'aquatic_single_west_garden';p['status']='new_aquatic_construction_candidate';p['reference_base_sha256']=hashlib.sha256((B/'PLAN.json').read_bytes()).hexdigest()
 if mirror:
  for part in p['parts']:
   if 'Activity' in part['name']:
    for v in part['verts']:v[0]+=5.3;v[2]-=.7
   if 'PrivacyScreen' in part['name']:
    for v in part['verts']:v[2]-=.9
 for part in p['parts']:
  part['name']=part['name'].replace('TQ102',f'TA{idx}');part['verts']=[point(v)for v in part['verts']]
  if mirror:part['faces']=[list(reversed(f))for f in part['faces']]
 p['components']=[{'catalogue_id':'AST-RST-AQ-001','name':'AquaticRestCradle','world_origin':point([-55.5,84,-297.3 if mirror else-299.85]),'godot_yaw':math.pi/2 if mirror else-math.pi/2,'rest_slot_id':row['proposed_rest_slot_ids'][0]}];p.pop('component')
 for door in p['doors']:
  door['world_origin']=point(door['world_origin']);door['identity']=row['proposed_runtime_id']+(':entry'if door['name']=='EntryDoor'else':wash')
  if mirror and door['name']=='EntryDoor':door['godot_yaw']=-math.pi/2
 for q in p['source_fixtures']:
  q['origin']=point(q['origin'])
  if mirror and q['catalogue_id']=='AST-SAN-001':q['yaw']=math.pi
 for q in p['lights']:q['position']=point(q['position']);q['name']=q['name'].replace('TQ102',f'TA{idx}')
 a=point(base['guard_opening_world']['min']);b=point(base['guard_opening_world']['max']);p['guard_opening_world']={'min':[min(a[i],b[i])for i in range(3)],'max':[max(a[i],b[i])for i in range(3)]};cuts.append(p['guard_opening_world'])
 p['limits']=['New aquatic-rest construction profile, no recovered species assignment or accepted biological fit','One retained proposed reservation per room; no extra guest units or physical places','Actual body/pose, water immersion simulation, plumbing, water chemistry/temperature and service controls remain open','Water/ripple meshes must have no solid collision; basin uses cavity-preserving triangle contact','Source composition review precedes adoption; final in-engine/CRT and full cart traversal remain open']
 for part in p['parts']:assert all(row['allocation_x'][0]-.0001<=v[0]<=row['allocation_x'][1]+.0001 and row['allocation_z'][0]-.0001<=v[2]<=row['allocation_z'][1]+.0001 for v in part['verts'])
 u=O/'units'/str(idx);(u/'source').mkdir(parents=True,exist_ok=True);(u/'PLAN.json').write_text(json.dumps(p,indent=2)+'\n');summary.append({'source_index':idx,'runtime_id':row['proposed_runtime_id'],'plan':str((u/'PLAN.json').relative_to(O)),'mirror':mirror,'reserved_rest_places':1})
plan={'schema':'astraea.tidal_aquatic_singles.v1','source_house_sha256':base['source_pins']['Game/assets/models/AST-RES-TIDAL_lift_fit_r003.glb'],'rooms':summary,'entry_cuts_including_retained_102':cuts,'retained_d13_units':10,'D14_double_reservation_remaining':394,'limits':p['limits'],'status':'five_new_aquatic_single_compositions_prepared_not_installed'};(O/'BATCH_PLAN.json').write_text(json.dumps(plan,indent=2)+'\n');(O/'source/prepare.py').write_text(Path(__file__).read_text());print('Prepared5aquatic single room shells, explicit pending double394')
# Reuse the owned shared shell builder; this does not run a competing publisher or Game import.
s=(R/'BlenderCatalogue/assets/tidal_specialty_d13_batch_20261009/source/build.py').read_text();(O/'source/build.py').write_text(s)
