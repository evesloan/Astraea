import json,pathlib,hashlib,collections
R=pathlib.Path('/workspace/Astraea');W=pathlib.Path('/workspace/full-requirement-reconciliation-20261019');f=W/'CURRENT_FILE_BINDING_TRACE.json';d=json.load(open(f));homes=json.load(open(R/'Game/data/received_homes_20261015/HOMES.json'));by={str(q['key']):q for q in homes['homes']};counts=collections.Counter()
for q in d['rows']:
 p=q['source_path'];name=pathlib.Path(p).name
 if q['current_script_or_contract_mentions']:status='CURRENT_SCRIPT_OR_CONTRACT_REFERENCE'
 elif '/group2_completion/'in p and pathlib.Path(name).stem.isdigit():
  key=pathlib.Path(name).stem;r=by[key];assert r['selected_for_first_source_home_package']and r['source_sha256']==q['source_sha256'];status='REGISTERED_DEFERRED_HOME_EXACT_SOURCE';q['dynamic_binding']={'registry':'Game/data/received_homes_20261015/HOMES.json','source_key':key,'loader':'Game/scripts/received_homes_20261015/package.gd','root_name':'Group2Home_'+key,'expected_mesh_nodes':r['mesh_nodes'],'current_asset_sha256':hashlib.sha256((R/'Game/assets/group2_completion'/name).read_bytes()).hexdigest()};assert q['dynamic_binding']['current_asset_sha256']==q['source_sha256']
 elif 'PERIMETER_'in name:
  status='REGISTERED_DEFERRED_PRIVATE_HOME_PERIMETER';q['dynamic_binding']={'loader':'Game/scripts/received_homes_20261015/source_dispatch.gd','source_loader':'Game/scripts/group2_pit_perimeters/package.gd','current_contract':'Game/data/group2_pit_perimeters/PLAN_r003.json'}
 elif 'thread_stock_repair_r002'in name:
  status='PREDECESSOR_OF_INSTALLED_THREAD_R005';q['successor_contract']='Game/data/architecture/group5/THREAD_STOCK_REPAIR.json'
 elif 'AquaticCompletion_'in name:
  status='PREDECESSOR_OF_INSTALLED_AQUATIC_R019';q['successor_contract']='Game/data/architecture/group6_completion/FIT_CONTRACT.json'
 elif 'Group6ThermalEntries_'in name:
  status='PREDECESSOR_OF_INSTALLED_THERMAL_ENTRY_R003';q['successor_contract']='Game/data/architecture/group6_completion/THERMAL_SUPPORT_CONTRACT.json'
 else:raise AssertionError(p)
 q['reviewed_disposition']=status;counts[status]+=1
 if 'successor_contract'in q:assert(R/q['successor_contract']).exists();q['successor_contract_sha256']=hashlib.sha256((R/q['successor_contract']).read_bytes()).hexdigest()
d['reviewed_counts']=dict(counts);f.write_text(json.dumps(d,indent=2)+'\n');print(counts)
