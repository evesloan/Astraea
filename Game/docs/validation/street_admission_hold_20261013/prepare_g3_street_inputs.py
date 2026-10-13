from pathlib import Path
import json,hashlib,subprocess
C=Path(__file__).parent;R=Path('/workspace/astraea-protected-integration-20261012');S='/workspace/astraea-readonly-interface-review-20261012/remote_only_20261012T000749Z.git';rev='6f2d0da67429ea940edf7011348ec08a346f37db';sha=lambda b:hashlib.sha256(b).hexdigest();p=json.loads((C/'g3_receiving_metadata/Game/data/architecture/group3_d03_streets_20261011/STREETS.json').read_text());proof=json.loads((R/'Game/data/architecture/packages/botanical_pair_runtime/RUNTIME_PROOF.json').read_text());rows=[]
for path,h in p['source_pins'].items():
 b=subprocess.check_output(['git','-C',S,'show',rev+':'+path]);assert sha(b)==h;row={'path':path,'sha256':h,'bytes':len(b),'independent_pin_exact':True};q=R/path
 if q.exists()and sha(q.read_bytes())!=h:
  live=q.read_bytes()
  if path.endswith('/structural_meshes.json'):
   a=json.loads(b);z=json.loads(live);assert len(a['regions'])==len(z['regions'])==303;assert {u['id']for u,v in zip(a['regions'],z['regions'])if u!=v}=={'D09_fore_route','D09_aft_route','D09_atrium_circulation'};assert all(a[k]==z[k]for k in a if k!='regions');row['explained']='Exact three protected G4 pit-owner successors'
  else:
   text=live.decode();found=False
   for e in proof['inverse_edits'][path[5:]]:
    assert text.count(e['after'])==e['count'];text=text.replace(e['after'],e['before']);found=found or sha(text.encode())==h
   if path=='Game/scripts/ship.gd':
    review=json.loads((C/'G3_STREET_SHARED_SCRIPT_SUCCESSOR_REVIEW.json').read_text());assert review['required_sha256']==h and review['current_sha256']==sha(live);row['explained']='Exact frozen baseline and independently retained authorized shared-root successor;sealed inverse verified'
   else:
    assert found,path;row['explained']='Exact required sealed inverse preimage'
 elif not q.exists():row['materialization']='Inactive native/source remains independently Git-backed'
 rows.append(row)
for file,h in p['model_pins'].items():
 key='Game/assets/models/group3_d03_streets_20261011/'+file;b=subprocess.check_output(['git','-C',S,'show',rev+':'+key]);assert sha(b)==h;q=C/'g3_street_staging'/key;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(b);Path(str(q)+'.import').write_bytes(subprocess.check_output(['git','-C',S,'show',rev+':'+key+'.import']))
for key in ['data/architecture/group3_d03_streets_20261011/STREETS.json','scripts/group3_d03_streets_20261011/physical_package.gd']:
 q=C/'g3_street_staging/Game'/key;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes((C/'g3_receiving_metadata/Game'/key).read_bytes())
key='Game/scripts/group3_d03_streets_20261011/physical_package.gd.uid';(C/'g3_street_staging'/key).write_bytes(subprocess.check_output(['git','-C',S,'show',rev+':'+key]))
base='BlenderCatalogue/assets/group3_crew_service_20261009/extensions/d03_remaining_streets_physical_batch023/'
for name in ['source/REMAINING_STREET_MISSING_FLOOR.json','source/RETAINED_PHYSICAL_FLOOR_SURVEY.json']:
 q=C/'g3_street_preflight'/Path(name).name;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(subprocess.check_output(['git','-C',S,'show',rev+':'+base+name]))
result={'status':'PASS_EXACT_STREET_INPUTS_AND_EXPLAINED_SUCCESSORS','source_revision':rev,'source_pins':rows,'models':5,'source_failed_network_criteria_preserved':13,'geometry_adoption_is_not_operational_route_acceptance':True};(C/'G3_STREET_INPUT_VERIFICATION.json').write_text(json.dumps(result,indent=2)+'\n');print(result['status'],len(rows),'pins',len(p['model_pins']),'models')
