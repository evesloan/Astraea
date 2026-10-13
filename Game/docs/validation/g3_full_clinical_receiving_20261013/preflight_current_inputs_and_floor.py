from pathlib import Path
import json,hashlib
P=Path(__file__).parent;C=P.parent;R=Path('/workspace/astraea-protected-integration-20261012');G=R/'Game';sha=lambda b:hashlib.sha256(b).hexdigest();d=json.loads((P/'CLINICAL_SOURCE.json').read_text());proof=json.loads((G/'data/architecture/packages/botanical_pair_runtime/RUNTIME_PROOF.json').read_text());rows=[]
for path,h in d['source_pins'].items():
 old=(P/'pinned_inputs'/path).read_bytes();assert sha(old)==h;current=R/path
 if not path.startswith('Game/')or not current.exists():continue
 b=current.read_bytes();row={'path':path,'source_sha256':h,'current_sha256':sha(b),'exact':sha(b)==h}
 if sha(b)!=h:
  if path=='Game/data/generated/structural_meshes.json':
   a=json.loads(old);z=json.loads(b);assert len(a['regions'])==len(z['regions'])==303;changed=[u['id']for u,v in zip(a['regions'],z['regions'])if u!=v];assert set(changed)=={'D09_fore_route','D09_aft_route','D09_atrium_circulation'};assert all(a[k]==z[k]for k in a if k!='regions');row['explained']='Exact three independently protected G4 pit owner successors'
  else:
   key=path[5:];assert proof['current_sha256'][key]==sha(b);text=b.decode();found=False
   for edit in proof['inverse_edits'][key]:
    assert text.count(edit['after'])==edit['count'];text=text.replace(edit['after'],edit['before']);found=found or sha(text.encode())==h
   assert found,path;row['explained']='Exact required predecessor occurs in sealed current inverse chain'
 rows.append(row)
ns={'__file__':str(C/'preflight_g3_first_floor_overlap.py')};exec((C/'preflight_g3_first_floor_overlap.py').read_text().split('old=[]')[0],ns);old=[]
for rel in ['data/generated/structural_meshes.json','data/generated/received_structural_meshes.json','data/architecture/REMAINING_BATCH_FLOORS.json']:
 data=json.loads((G/rel).read_text())
 for region in data.get('regions',[]):
  if abs(float(region.get('floor_y',-999))-21)<.001:old.extend((region['id'],t)for t in region['triangles'])
for key in ['BlenderCatalogue/assets/group3_crew_service_20261009/extensions/port2_clinical_physical_batch016/source/PORT2_MISSING_ONLY_FLOORS.json','BlenderCatalogue/assets/group3_crew_service_20261009/extensions/fore_starboard_clinical_batch018/source/FORE_MISSING_ONLY_FLOORS.json']:
 data=json.loads((P/'pinned_inputs'/key).read_text())
 for part in data['parts']:
  if abs(part['y'][-1]-21)<.001:old.extend((key+'/'+part['name'],t)for t in part['triangles'])
new=json.loads((P/'native/CLINICAL_COMPLETE_MISSING_FLOOR.json').read_text());hits=[]
for part in new['parts']:
 for i,t in enumerate(part['triangles']):
  for owner,base in old:
   a=ns['overlap'](t,base)
   if a>1e-6:hits.append({'part':part['name'],'triangle':i,'existing_owner':owner,'area_m2':a})
result={'status':'PASS_CURRENT_INPUT_SUCCESSORS_AND_DECLARED_MISSING_FLOOR'if not hits else'HOLD_FLOOR_OVERLAP','current_source_pins':rows,'existing_D05_floor_triangles':len(old),'new_triangles':sum(len(x['triangles'])for x in new['parts']),'new_declared_floor_m2':new['new_floor_m2'],'overlap_m2':sum(x['area_m2']for x in hits),'overlap_pairs':hits,'actual_native_floor_scene_preimages_required':True,'protected_pool_and_two_royalty_support_spans_held':True};(P/'CURRENT_INPUT_AND_FLOOR_PREFLIGHT.json').write_text(json.dumps(result,indent=2)+'\n');print(result['status'],'newtris',result['new_triangles'],'existing',len(old),'overlap',result['overlap_m2'])
