"""Register only the new family and two owned representations after revision-matching QA."""
from pathlib import Path
import json,hashlib,subprocess
R=Path(__file__).resolve().parents[1];C=R.parents[1];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
# A final UV audit was added while the same-revision main renders were running.
# Bounded one-time catch-up only when that stronger receipt is absent: the source builder corrects new staff ceiling UVs, never old pieces.
qpath=R/'qa/source_export_verification.json';prior=json.loads(qpath.read_text())
if not all(row.get('all_exported_UV_triangles_nondegenerate',False)for row in prior['roundtrips']):
 before=sha(R/'source/connected_contract.json')
 jobs=[('staff_uv_rebuild','source/build_source_derivatives.py',['--','--staff-only']),('verification','qa/verify_source.py',[]),('contacts','qa/check_contacts.py',[]),('lift_sweeps','qa/check_lift_source_sweeps.py',[])]
 for log,script,args in jobs:
  with (R/'qa'/(log+'.log')).open('w')as out:subprocess.run(['blender','-b','--python-exit-code','1','--python',str(R/script)]+args,stdout=out,stderr=subprocess.STDOUT,check=True)
 assert sha(R/'source/connected_contract.json')==before,'UV-only catch-up must preserve the validated geometry contract'
 with (R/'qa/plan_routes.log').open('w')as out:subprocess.run(['python',str(R/'qa/check_plan_routes.py')],stdout=out,stderr=subprocess.STDOUT,check=True)
D=json.loads((R/'source/connected_contract.json').read_text());Q=json.loads(qpath.read_text());assert Q['pass'] and Q['contract_sha256']==sha(R/'source/connected_contract.json')
views=json.loads((R/'qa/reference_source_visual_review.json').read_text());assert views['source_sha256']==sha(R/'source/AST-AQU-016.blend') and views['contract_sha256']==sha(R/'source/connected_contract.json')
for row in views['images']:assert sha(R/row['path'])==row['sha256']
for n in['source_contact_graph.json','plan_route_verification.json','lift_source_sweeps.json']:
 q=json.loads((R/'qa'/n).read_text());assert q['pass'],n
 for path,h in q['input_sha256'].items():assert sha(R/path)==h,(n,path)
for row in Q['roundtrips']:
 for kind,ext in[('source','blend'),('export','glb')]:assert sha(R/('source'if kind=='source'else'exports')/(row['asset']+'.'+ext))==row[kind+'_sha256']
status='Exact source/export, material, contact, source-route and lift-sweep QA pass; root runtime/in-ship acceptance pending'
for row in Q['roundtrips']:
 p=R/(row['asset']+'.manifest.json');m=json.loads(p.read_text());m['source_sha256']=row['source_sha256'];m['export_sha256']=row['export_sha256'];m['contract_sha256']=sha(R/'source/connected_contract.json');m['status']=status;m['handoff']='HANDOFF.md';m['verification']=['qa/source_export_verification.json','qa/source_contact_graph.json','qa/plan_route_verification.json','qa/lift_source_sweeps.json'];p.write_text(json.dumps(m,indent=2)+'\n')
cat_path=C/'catalogue_manifest.json';cat=json.loads(cat_path.read_text());base=json.loads((R/'source/catalogue_registration_baseline.json').read_text());fp=lambda x:hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
for a in cat['assets']:
 if a['catalogue_id']!='AST-AQU-016':assert fp(a)==base['asset_entry_sha256'][a['catalogue_id']],('Unowned existing asset entry changed',a['catalogue_id'])
for a in cat['derived_representations']:
 if a['id']not in['AST-CIR-005_forward_pool_market','AST-STF-009_pool_market']:assert fp(a)==base['derived_entry_sha256'][a['id']],a['id']
assert base['ownership']['AST-CIR-005']=='primary_atrium_core'and base['ownership']['AST-STF-009']=='lower_staff_network';assert 'AST-AQU-016'not in base['ownership']
m=json.loads((R/'AST-AQU-016.manifest.json').read_text());prefix='assets/grand_pool_orchard_section/'
entry={'catalogue_id':'AST-AQU-016','family':'grand_pool_orchard_section','name':m['name'],'source':prefix+m['source'],'export':prefix+m['export'],'manifest':prefix+'AST-AQU-016.manifest.json','source_sha256':m['source_sha256'],'export_sha256':m['export_sha256'],'evaluated_triangles':m['triangles'],'batch':'74','adopted_game_instances':0,'status':status}
prior=[a for a in cat['assets']if a['catalogue_id']=='AST-AQU-016'];assert len(prior)<=1 and all(a['family']=='grand_pool_orchard_section'for a in prior)
cat['assets']=[a for a in cat['assets']if a['catalogue_id']!='AST-AQU-016']+[entry];cat['unique_authored_asset_count']=len(cat['assets'])
for stem,parent in[('AST-CIR-005_forward_pool_market','AST-CIR-005'),('AST-STF-009_pool_market','AST-STF-009')]:
 m=json.loads((R/(stem+'.manifest.json')).read_text());entry={'id':stem,'parent_design_ids':[parent],'kind':'Bounded Grand Pool/Orchard existing-family source derivative; no new unique design','source':prefix+m['source'],'export':prefix+m['export'],'manifest':prefix+stem+'.manifest.json','source_sha256':m['source_sha256'],'export_sha256':m['export_sha256'],'new_unique_design_count':0,'evaluated_triangles':m['triangles'],'status':status};cat['derived_representations']=[a for a in cat['derived_representations']if a['id']!=stem]+[entry]
assert len({a['catalogue_id']for a in cat['assets']})==len(cat['assets']);assert len(cat['assets'])==base['asset_count']+1
cat_path.write_text(json.dumps(cat,indent=2)+'\n')
contact=json.loads((R/'qa/source_contact_graph.json').read_text());h=R/'HANDOFF.md';s=h.read_text().replace('548 exported semantic pieces',str(Q['roundtrips'][0]['editable_exported_meshes'])+' exported semantic pieces').replace('All 557 nodes',f"All {contact['rooted_nodes']} nodes");h.write_text(s)
# Generated caches and transient logs are not frozen delivery inputs.
files=[p for p in R.rglob('*')if p.is_file()and p.name!='DELIVERY_HASHES.json'and p.suffix not in['.log','.pyc']and'__pycache__'not in p.parts]
freeze={'status':'Frozen source stage; parent commit, independent retention and runtime adoption pending','source_root_commit_at_start':'51d431b4fbe197eb61397e1edb1fa04961eceef8','registered_new_id':'AST-AQU-016','derived_representations':['AST-CIR-005_forward_pool_market','AST-STF-009_pool_market'],'catalogue_registration_sha256':sha(cat_path),'files':{str(p.relative_to(R)):sha(p)for p in sorted(files)},'retained_input_hashes':D['preserved_catalogue_inputs']}
(R/'DELIVERY_HASHES.json').write_text(json.dumps(freeze,indent=2)+'\n');print(json.dumps({'status':status,'registered_count':len(cat['assets']),'rooted_nodes':contact['rooted_nodes'],'roundtrips':Q['roundtrips'],'contract_sha256':sha(R/'source/connected_contract.json')},indent=2))
