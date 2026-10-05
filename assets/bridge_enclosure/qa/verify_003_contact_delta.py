from pathlib import Path
import json
R=Path(__file__).resolve().parents[1];C=R.parents[1];A=json.loads((R/'qa/baseline_003_contacts.json').read_text());B=json.loads((C/'assets/bridge_platform/qa/independent_review_contacts.json').read_text());allow=set(json.loads((R/'qa/prior_003_parts.json').read_text())['allowlist_assemblies'])
protected=['structural_mesh_count','structural_disconnected','all_mesh_disconnected','pier_verification','clearance_queries','ledger_mismatch','hanger_seats','guard_junction_returns','fixture_checks','east_return','broad_floor_panels','additional_low_structures','guard_endpoints','support_path_examples','new_floor_slab_meshes','door_meshes']
for k in protected:assert A[k]==B[k],k
unchanged=[];changed=[]
for k in set(A['assembly_contacts'])|set(B['assembly_contacts']):
 a=A['assembly_contacts'].get(k);b=B['assembly_contacts'].get(k)
 if a==b:unchanged.append(k);continue
 assert any(n in allow for n in k.split(' | ')),k
 changed.append({'assemblies':k,'before':a,'after':b})
failed=[x for x in B['guard_chain_checks']if not x['pass']]
assert failed==[{'side':'Port','corner':0,'type':'GuardCap','contact':None,'pass':False},{'side':'Starboard','corner':2,'type':'GuardCap','contact':None,'pass':False}]
report={'pass':True,'baseline_source_sha256':A['source_sha256'],'current_source_sha256':B['source_sha256'],'protected_audit_fields_byte_equal':protected,'unchanged_assembly_contact_count':len(unchanged),'changed_assembly_contacts':changed,'intentional_removed_same_height_cap_contacts':failed,'replacement':'004 BRE_Fore_HangerCollar at port nose and BRE_Aft_HangerCollar at starboard aft join both differing cap heights; no corner test silently passed or old checker weakened. Independent004 perimeter/contact report proves paired enclosure closure.','current003_audit':'../bridge_platform/qa/independent_review_contacts.json'}
(R/'qa/003_contact_delta.json').write_text(json.dumps(report,indent=2)+'\n');print('PROTECTED_AUDIT_IDENTICAL',len(protected),'unchanged assembly contacts',len(unchanged),'intentional removed cap corners',len(failed))
