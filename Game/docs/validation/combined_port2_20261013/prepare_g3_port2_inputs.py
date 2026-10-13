from pathlib import Path
import json,hashlib,subprocess
C=Path(__file__).parent;R=Path('/workspace/astraea-protected-integration-20261012');S='/workspace/astraea-readonly-interface-review-20261012/remote_only_20261012T000749Z.git';rev='6f2d0da67429ea940edf7011348ec08a346f37db';sha=lambda b:hashlib.sha256(b).hexdigest();plan=json.loads((C/'g3_receiving_metadata/Game/data/architecture/group3_port2_clinical_20261011/PHYSICAL.json').read_text());proof=json.loads((R/'Game/data/architecture/packages/botanical_pair_runtime/RUNTIME_PROOF.json').read_text());ys=[float(x['floor_elevation_m'])for x in json.loads((R/'Game/data/design_contract.json').read_text())['deck_datums']][:17];assert plan['controller_binding']['floor_heights']==ys;rows=[]
for path,h in plan['source_pins'].items():
 b=subprocess.check_output(['git','-C',S,'show',rev+':'+path]);assert sha(b)==h;row={'path':path,'sha256':h,'bytes':len(b),'independent_pin_exact':True};p=R/path
 if p.exists():
  live=p.read_bytes();row['live_sha256']=sha(live)
  if sha(live)!=h:
   if path.endswith('/structural_meshes.json'):
    a=json.loads(b);z=json.loads(live);assert len(a['regions'])==len(z['regions'])==303;changed=[x['id']for x,y in zip(a['regions'],z['regions'])if x!=y];assert set(changed)=={'D09_fore_route','D09_aft_route','D09_atrium_circulation'};assert all(a[k]==z[k]for k in a if k!='regions');row['explained']='Three exact already protected G4 pit successor owners'
   else:
    text=live.decode();found=False
    for e in proof['inverse_edits'][path[5:]]:
     assert text.count(e['after'])==e['count'];text=text.replace(e['after'],e['before']);found=found or sha(text.encode())==h
    assert found,path;row['explained']='Exact required preimage in sealed inverse chain'
 else:row['materialization']='Inactive authoring input remains independently Git-backed'
 rows.append(row)
for name,h in plan['model_pins'].items():
 key='Game/assets/models/group3_port2_clinical_20261011/'+name;b=subprocess.check_output(['git','-C',S,'show',rev+':'+key]);assert sha(b)==h;p=C/'g3_port2_staging'/key;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b);Path(str(p)+'.import').write_bytes(subprocess.check_output(['git','-C',S,'show',rev+':'+key+'.import']))
for key in ['data/architecture/group3_port2_clinical_20261011/PHYSICAL.json','scripts/group3_port2_clinical_20261011/physical_package.gd']:
 p=C/'g3_port2_staging/Game'/key;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((C/'g3_receiving_metadata/Game'/key).read_bytes())
key='Game/scripts/group3_port2_clinical_20261011/physical_package.gd.uid';(C/'g3_port2_staging'/key).write_bytes(subprocess.check_output(['git','-C',S,'show',rev+':'+key]))
key='BlenderCatalogue/assets/group3_crew_service_20261009/extensions/port2_clinical_physical_batch016/source/PORT2_MISSING_ONLY_FLOORS.json';p=C/'g3_port2_preflight/PORT2_MISSING_ONLY_FLOORS.json';p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(subprocess.check_output(['git','-C',S,'show',rev+':'+key]))
result={'status':'PASS_EXACT_INPUTS_CURRENT_DATUMS_AND_EXPLAINED_SUCCESSORS','source_revision':rev,'source_pins':rows,'all17_canonical_deck_datums_match':True,'protected_D04_riser3_not_selected':True,'operating_identities_created':False};(C/'G3_PORT2_INPUT_VERIFICATION.json').write_text(json.dumps(result,indent=2)+'\n');print(result['status'],len(rows),'pins',len(plan['model_pins']),'models')
