from pathlib import Path
import json,copy,math
R=Path('/workspace/shared/Astraea_direct_recovery_20261008_hcozu5z4');B=R/'BlenderCatalogue/assets/tidal_aquatic_double_20261009';O=R/'BlenderCatalogue/assets/tidal_quiet_doubles_20261009';(O/'source').mkdir(parents=True,exist_ok=True);base=json.load(open(B/'units/394/PLAN.json'));rows=[q for q in json.load(open(R/'BlenderCatalogue/assets/residential_production_batch/inputs/PROPOSED_FULL_1000_PRODUCTION_ROWS.json'))['records']if q['house']=='port_forward_upper_house'and q['deck']=='D15'and q['historical_class']=='specialty_unsplit'and q['proposed_rest_place_count']==2];assert len(rows)==10;old=json.load(open(R/'BlenderCatalogue/assets/tidal_low_nest_singles_20261009/BATCH_PLAN.json'));cuts=copy.deepcopy(old['entry_cuts_including_retained_102']);units=[]
for row in rows:
 idx=row['source_envelope_index'];mirror=row['allocation_x'][0]<-45;dz=sum(row['allocation_z'])/2+490
 def point(v):return [(-88-v[0])if mirror else v[0],v[1]+4.5,v[2]+dz]
 p=copy.deepcopy(base);p['allocation']=row;p['composition_variant']='paired_quiet_cocoons_west_garden'if mirror else'paired_quiet_cocoons_east_garden';p['status']='new_quiet_cocoon_double_candidate'
 for q in p['parts']:
  q['name']=q['name'].replace('TA394',f'TQD{idx}');q['verts']=[point(v)for v in q['verts']]
  if mirror:q['faces']=[list(reversed(f))for f in q['faces']]
 p['components']=[{'catalogue_id':'AST-RST-QC-001','name':'QuietCocoonSupport'+str(i+1),'world_origin':point([x,88.5,-488.75]),'godot_yaw':0,'rest_slot_id':row['proposed_rest_slot_ids'][i]}for i,x in enumerate([-36.6,-32.3])]
 for d in p['doors']:
  d['world_origin']=point(d['world_origin']);d['identity']=row['proposed_runtime_id']+(':entry'if d['name']=='EntryDoor'else':wash')
  if mirror and d['name']=='EntryDoor':d['godot_yaw']=math.pi/2
 for q in p['source_fixtures']:
  q['origin']=point(q['origin'])
  if mirror and q['catalogue_id']=='AST-SAN-001':q['yaw']=0
 for q in p['lights']:q['position']=point(q['position']);q['name']=q['name'].replace('TA394',f'TQD{idx}')
 a=point(p['guard_opening_world']['min']);b=point(p['guard_opening_world']['max']);p['guard_opening_world']={'min':[min(a[i],b[i])for i in range(3)],'max':[max(a[i],b[i])for i in range(3)]};cuts.append(p['guard_opening_world'])
 p['limits']=['Two existing proposed rest reservations; no new guest unit or species assignment','Quiet cocoon construction profile, not biological/pose/acoustic acceptance','Environmental service controls, final in-engine/CRT review and full cart traversal remain open']
 u=O/'units'/str(idx);(u/'source').mkdir(parents=True,exist_ok=True);(u/'PLAN.json').write_text(json.dumps(p,indent=2)+'\n');units.append({'source_index':idx,'runtime_id':row['proposed_runtime_id'],'plan':str((u/'PLAN.json').relative_to(O))})
plan={'schema':'astraea.tidal_quiet_doubles.v1','source_house_sha256':old['source_house_sha256'],'rooms':units,'entry_cuts_including_retained_102':cuts,'limits':p['limits']};(O/'BATCH_PLAN.json').write_text(json.dumps(plan,indent=2)+'\n');(O/'source/prepare.py').write_text(Path(__file__).read_text());(O/'source/build.py').write_text((B/'source/build.py').read_text());s=(B/'source/cut_frontage.py').read_text().replace('TidalAquaticDoubleFrontagePatch','TidalQuietDoublesFrontagePatch');(O/'source/cut_frontage.py').write_text(s);s=(B/'source/assemble_review.py').read_text().replace('aquatic_rest_cradle_20261009/AST-RST-AQ-001.glb','quiet_cocoon_support_20261009/AST-RST-QC-001.glb').replace('TidalAquaticAssembly','TidalQuietDoubleAssembly').replace('(-38.5,491.0,floor+1.62)','(-38.5 if right else -49.5,-center+1.0,floor+1.62)');(O/'source/assemble_review.py').write_text(s);print('Prepared ten paired quiet-cocoon source interiors')
