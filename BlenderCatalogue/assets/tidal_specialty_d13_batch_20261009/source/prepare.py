from pathlib import Path
import json,math,copy,hashlib
O=Path(__file__).resolve().parents[1];R=O.parents[2];B=R/'BlenderCatalogue/assets/tidal_specialty_single_20261009';base=json.load(open(B/'PLAN.json'));rows=json.load(open(R/'BlenderCatalogue/assets/residential_production_batch/inputs/PROPOSED_FULL_1000_PRODUCTION_ROWS.json'))['records'];rows=[q for q in rows if q['house']=='port_forward_upper_house'and q['historical_class']=='specialty_unsplit'and q['deck']=='D13'];assert len(rows)==10
summary=[];cuts=[base['guard_opening_world']]
for k,row in enumerate(rows):
 if row['source_envelope_index']==102:continue
 idx=row['source_envelope_index'];mirror=row['allocation_x'][0]>-45;center=sum(row['allocation_z'])/2;dz=center+298.4;variant=k%3
 def point(v):return [(-88-v[0])if mirror else v[0],v[1],v[2]+dz]
 p=copy.deepcopy(base);p['allocation']=row;p['composition_variant']=['court_reading','central_cocoon','separate_activity'][variant];p['status']='new_authored_construction_candidate';p['reference_base_sha256']=hashlib.sha256((B/'PLAN.json').read_bytes()).hexdigest()
 if variant==1:p['component']['world_origin'][2]+=1.45
 if variant==2:
  for part in p['parts']:
   if 'Activity' in part['name']:
    for v in part['verts']:v[0]+=3.4;v[2]-=.7
 for part in p['parts']:
  part['name']=part['name'].replace('TQ102',f'TQ{idx}');part['verts']=[point(v)for v in part['verts']]
  if mirror:part['faces']=[list(reversed(f))for f in part['faces']]
 p['component']['world_origin']=point(p['component']['world_origin']);p['component']['godot_yaw']=math.pi/2 if mirror else-math.pi/2
 for door in p['doors']:
  door['world_origin']=point(door['world_origin']);door['identity']=row['proposed_runtime_id']+(':entry'if door['name']=='EntryDoor'else':wash')
  if mirror and door['name']=='EntryDoor':door['godot_yaw']=-math.pi/2
 for q in p['source_fixtures']:
  q['origin']=point(q['origin'])
  if mirror and q['catalogue_id']=='AST-SAN-001':q['yaw']=math.pi
 for q in p['lights']:q['position']=point(q['position']);q['name']=q['name'].replace('TQ102',f'TQ{idx}')
 a=point(base['guard_opening_world']['min']);b=point(base['guard_opening_world']['max']);p['guard_opening_world']={'min':[min(a[i],b[i])for i in range(3)],'max':[max(a[i],b[i])for i in range(3)]};cuts.append(p['guard_opening_world'])
 for part in p['parts']:
  assert all(row['allocation_x'][0]-.0001<=v[0]<=row['allocation_x'][1]+.0001 and row['allocation_z'][0]-.0001<=v[2]<=row['allocation_z'][1]+.0001 for v in part['verts'])
 u=O/'units'/str(idx);(u/'source').mkdir(parents=True,exist_ok=True);(u/'PLAN.json').write_text(json.dumps(p,indent=2)+'\n')
 summary.append({'source_index':idx,'runtime_id':row['proposed_runtime_id'],'plan':str((u/'PLAN.json').relative_to(O)),'variant':p['composition_variant'],'mirror':mirror,'new_guest_units':0,'reserved_rest_places':1})
plan={'schema':'astraea.tidal_specialty_d13_batch.v1','base_room_unchanged':102,'source_house_sha256':base['source_pins']['Game/assets/models/AST-RES-TIDAL_lift_fit_r003.glb'],'rooms':summary,'entry_cuts_including_retained_102':cuts,'limits':base['limits'],'status':'nine_new_compositions_prepared_not_installed'};(O/'BATCH_PLAN.json').write_text(json.dumps(plan,indent=2)+'\n');print('Prepared',len(summary),'room compositions',len(cuts),'bounded openings')
