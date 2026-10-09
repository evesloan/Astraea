from pathlib import Path
import hashlib,json,struct,difflib
HERE=Path(__file__).resolve().parent
B=HERE.parent
G=Path('/workspace/shared/Astraea_recovery_20261007_AXWr5x/Game')
I=B.parent/'sol_batch_intake_20261008/A'
V=B/'shared_fixture_variant'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,v): (HERE/n).write_text(json.dumps(v,indent=2)+'\n')
def gltf(p):
 b=p.read_bytes(); return json.loads(b[20:20+struct.unpack_from('<I',b,12)[0]])
old=json.loads((G/'data/architecture/CENTRAL_CROWN_RUNTIME.json').read_text())
proposal=json.loads((V/'CENTRAL_CROWN_RUNTIME.proposed.json').read_text())
variant='AST-CMD-001_crown_fixture_relocation_20261008_r002.glb'
proposal['export_sha256']=sha(V/variant)
proposal['runtime_model_file']=variant
write('CENTRAL_CROWN_RUNTIME.proposed.json',proposal)
patch=json.loads((V/'RUNTIME_MANIFEST_PATCH.json').read_text())
restored=json.loads(json.dumps(proposal)); restored.pop('runtime_model_file');restored['export_sha256']=old['export_sha256']
for test,replace in zip(patch['json_patch'][::2],patch['json_patch'][1::2]):
 idx=int(test['path'].split('/')[2]);assert restored['light_markers'][idx]['position']==replace['value']; restored['light_markers'][idx]['position']=test['value']
assert restored==old
write('RUNTIME_CONTRACT_INVERSE_PROOF.json',{'inverse_restores_exact_parsed_original':True,'original_sha256':sha(G/'data/architecture/CENTRAL_CROWN_RUNTIME.json'),'candidate_sha256':sha(HERE/'CENTRAL_CROWN_RUNTIME.proposed.json'),'changes':patch['json_patch']+[{'op':'replace','path':'/export_sha256','value':proposal['export_sha256']},{'op':'add','path':'/runtime_model_file','value':variant}],'scope':'Exact semantic equality after inverse; original serialization bytes remain preserved on disk.'})
sections=[]
for p in sorted(B.glob('D18_directory_*')):
 c=json.loads((p/'contract.json').read_text());a=json.loads((p/'artifact_manifest.json').read_text());key=c['programme_key']; door=next(d for d in old['doors'] if d['name']==key+'_entry');qa=json.loads((p/'qa/validation.json').read_text())
 sections.append({'programme_key':key,'source_folder':p.name,'model_file':key+'.glb','root_name':'CrownInterior_'+key,'runtime_sha256':a['glb_sha256'],'native_sha256':a['native_sha256'],'archive_file':p.name+'_source_review.zip','archive_sha256':sha(I/(p.name+'_source_review.zip')),'position':[0,0,0],'rotation':[0,0,0],'scale':[1,1,1],'floor_y':c['floor_y'],'existing_floor_owners':['D18_fore_apron','D18_atrium_structural_cap'] if key.endswith('02') else ['D18_atrium_structural_cap'],'existing_door':door,'mesh_count':qa['checks']['actual_export_meshes'],'triangle_count':qa['checks']['triangles'],'source_paths_xz':c['paths'],'source_views':c['views'],'authored_fixture_preview':c['authored_fixture_preview'],'receiving_hold':'Source-only. Runtime route/cart/door, lighting, visual and operational acceptance pending.'})
manifest={'schema':1,'status':'ISOLATED CANDIDATE; NOT APPLIED; retention blocked','root_name':'CrownBatchInteriors_SourceOnly','common_model_file':variant,'common_runtime_sha256':proposal['export_sha256'],'sections':sections,'new_floor_regions':[],'new_doors':[],'new_lights':[],'new_catalogue_ids':[]}
write('runtime_manifest.proposed.json',manifest)
live=['scripts/central_command_crown.gd','scripts/ship.gd','scripts/service_door.gd','scripts/static_contact_cache.gd','scripts/player.gd','data/architecture/CENTRAL_CROWN_RUNTIME.json','data/spatial_layout.json','data/generated/structural_meshes.json','data/programme_ledger.json','assets/models/AST-CMD-001.glb','assets/models/AST-STF-008.glb','tests/validate_crown_structure.gd','tests/validate_crown_access.gd','tests/validate_crown_cart.gd','tests/validate_crown_windows.gd','tools/test_central_crown.py','scripts/crew_batch_receiving.gd']
pins={str(G/p):sha(G/p) for p in live if (G/p).exists()}
for p in [B/'RECEIVING_REPORT.md', B/'RECEIVING_AUDIT.json',B/'INDEPENDENT_CROWN_FIXTURE_R002_REVIEW_20261008.json',*V.glob('*r002.blend'), V/variant,V/'BATCH_SPLIT_PROOF.json',V/'RESULT.md',V/'RUNTIME_MANIFEST_PATCH.json']:
 pins[str(p)]=sha(p)
for s in sections:
 for p in [I/s['archive_file'],B/s['source_folder']/'contract.json',B/s['source_folder']/'artifact_manifest.json',B/s['source_folder']/'exports'/s['model_file']]:pins[str(p)]=sha(p)
write('INPUT_SHA256.json',pins)
source=(G/'scripts/central_command_crown.gd').read_text()
candidate=source.replace('ship.model(root,"AST-CMD-001.glb"','ship.model(root,str(data.runtime_model_file)')
candidate+='\t# Additive source receiving; no new floor, door or light owners.\n\tload("res://scripts/crown_batch_receiving.gd").build(root,ship)\n'
(HERE/'central_command_crown.proposed.gd').write_text(candidate)
(HERE/'central_command_crown.proposed.patch').write_text(''.join(difflib.unified_diff(source.splitlines(True),candidate.splitlines(True),fromfile='scripts/central_command_crown.gd',tofile='scripts/central_command_crown.gd')))
j=gltf(V/variant); cell=[n['name'] for n in j['nodes'] if 'mesh'in n and n.get('name','').startswith('CMD_CELL_')];fixtures=[n['name'] for n in j['nodes'] if 'mesh'in n and n.get('name','').startswith('CMD_FIXTURE_RELOC_')];retired=[n['name'] for n in j['nodes'] if 'mesh'not in n and n.get('name','').startswith('CMD_CELL_')]
assert len(cell)==631 and len(fixtures)==20 and len(retired)==3
write('COMMON_MESH_ROSTER.json',{'retained_cell_meshes':cell,'relocated_fixture_meshes':fixtures,'retired_mesh_bindings_nodes_preserved':retired,'total_active_meshes':651,'triangles':32724,'maximum_extent_m':13.639999985694885,'unchanged_extent_gate_m':16.001})
t=(G/'tests/validate_crown_structure.gd').read_text();n=t.replace('res://assets/models/AST-CMD-001.glb','res://assets/models/'+variant).replace(old['export_sha256'],proposal['export_sha256'])
needle='\tcheck(meshes.size() == 634, "Expected 634 source/export-verified architecture batches")'
replacement='''\tcheck(meshes.size() == 631, "Expected 631 retained active CMD_CELL batches")
\tvar relocated := shell.find_children("CMD_FIXTURE_RELOC_*", "MeshInstance3D", true, false)
\tcheck(relocated.size() == 20, "Expected 20 independently reviewed relocated fixture batches")
\tmeshes.append_array(relocated)
\tcheck(meshes.size() == 651, "Expected all 651 active common meshes")
\tcheck(shell.find_children("*", "MeshInstance3D", true, false).size() == 651, "No active common mesh omitted")
\tvar roster: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/crown_batch/COMMON_MESH_ROSTER.json"))
\tfor expected in roster.retained_cell_meshes + roster.relocated_fixture_meshes:
\t\tcheck(shell.find_child(str(expected),true,false) is MeshInstance3D, "Missing exact active mesh identity: " + str(expected))
\tfor expected in roster.retired_mesh_bindings_nodes_preserved:
\t\tvar historic := shell.find_child(str(expected),true,false)
\t\tcheck(historic != null and not historic is MeshInstance3D, "Retired mesh binding must remain a non-mesh identity: " + str(expected))'''
assert needle in n;n=n.replace(needle,replacement)
needle2='\t\tvar bounds: AABB = mesh.global_transform * mesh.get_aabb()'; replacement2=needle2+'\n\t\tcheck(maxf(bounds.size.x,maxf(bounds.size.y,bounds.size.z)) < 16.001, "Unchanged spatial batch extent gate: " + str(mesh.name))'
n=n.replace(needle2,replacement2)
assert n.replace(replacement,needle).replace(replacement2,needle2).replace('res://assets/models/'+variant,'res://assets/models/AST-CMD-001.glb').replace(proposal['export_sha256'],old['export_sha256'])==t
(HERE/'validate_crown_structure.proposed.gd').write_text(n)
write('TEST_SUCCESSOR_INVERSE_PROOF.json',{'all_other_original_test_text_identical':True,'original_sha256':sha(G/'tests/validate_crown_structure.gd'),'successor_sha256':sha(HERE/'validate_crown_structure.proposed.gd'),'changes':['Asset filename and exact SHA pin','631 retained plus 20 relocated batches; all-mesh count and exact roster','Three historic node identities with retired mesh binding','Explicit unchanged <16.001 metre extent gate'],'retained_assertions':'All original triangle, keel, roof, piers, ties, protected covers, 170 openings, fixture/light and signage assertions remain verbatim.'})
print('Prepared isolated manifests and successors; no live writes.')
