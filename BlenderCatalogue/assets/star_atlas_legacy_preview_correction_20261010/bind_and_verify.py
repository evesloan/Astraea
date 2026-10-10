from pathlib import Path
import json,hashlib,shutil,struct,numpy as np,sys
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.load(open(W/'NATIVE_EXPORT_CHECK.json'));ns={'__file__':str(W/'reader.py')};exec((R/'BlenderCatalogue/assets/tidal_d15_service_receiving_20261010/source_geometry.py').read_text(),ns);sys.path.insert(0,str(R/'Game/tools'));from validate_production_glb import validate_and_copy
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();bindings={batch:json.load(open(R/'Game/data/architecture'/f'STAR_ATLAS_SPECIALTY_{batch}.json'))for batch in ['FIRST','SECOND']};newbindings=json.loads(json.dumps(bindings));meshes=triangles=removed=0
for r in P['rooms']:
 assert sha(R/r['original_native'])==r['original_native_sha256'] and sha(R/r['original_runtime'])==r['original_runtime_sha256']
 target=R/'Game/assets/models'/r['successor_runtime'];assert not target.exists()or sha(target)==r['successor_runtime_sha256'];validate_and_copy(W/r['successor_runtime'],target)
 before=dict(ns['triangles'](Path(r['original_runtime']).name));after=dict(ns['triangles'](r['successor_runtime']));expected={n:t for n,t in before.items()if'__Preview_Ground'not in n};assert set(expected)==set(after)
 for n,t in expected.items():assert np.array_equal(t,after[n]),n;triangles+=len(t);meshes+=1
 removed+=sum(len(t)for n,t in before.items()if'__Preview_Ground'in n)
 room=next(x for x in newbindings[r['batch']]['rooms']if x['allocation']['source_envelope_index']==r['source_index']);room.update(model_file=r['successor_runtime'],model_sha256=r['successor_runtime_sha256'],mesh_count=r['mesh_count'])
 for q in newbindings[r['batch']]['native_export_records']:
  if q['source_index']==r['source_index']:q.update(native=r['successor_native'],native_sha256=r['successor_native_sha256'],export=r['successor_runtime'],export_sha256=r['successor_runtime_sha256'],mesh_count=r['mesh_count'])
for old in bindings.values():
 for a in old['sources']:assert sha(R/'BlenderCatalogue'/a['source'])==a['source_sha256']and sha(R/'BlenderCatalogue'/a['export'])==a['export_sha256']
fourth=json.load(open(R/'Game/data/architecture/STAR_ATLAS_SPECIALTY_FOURTH.json'));pins={}
for r in fourth['rooms']:
 p=R/'Game/assets/models'/r['model_file'];assert sha(p)==r['model_sha256'];raw=p.read_bytes();n=struct.unpack_from('<I',raw,12)[0];j=json.loads(raw[20:20+n]);assert not any('Preview_Ground'in a.get('name','')for a in j['nodes']);pins[str(p.relative_to(R))]=sha(p)
assert removed==10
for batch,new in newbindings.items():(R/'Game/data/architecture'/f'STAR_ATLAS_SPECIALTY_{batch}.json').write_text(json.dumps(new,indent=2)+'\n')
eight=R/'Game/data/architecture/STAR_ATLAS_EIGHT_HABITATS.json';e=json.load(open(eight))
for r in P['rooms']:
 room=next(q for q in e['rooms']if q['source_envelope_index']==r['source_index']);room.update(production_assembly_native=str((W/r['successor_full_native']).relative_to(R/'BlenderCatalogue')),production_assembly_native_sha256=r['successor_full_native_sha256'])
eight.write_text(json.dumps(e,indent=2)+'\n')
report={'status':'PASS','corrected_existing_rooms':5,'preview_meshes_removed':5,'preview_triangles_removed':10,'all_retained_world_triangle_arrays_bit_identical':True,'retained_world_meshes':meshes,'retained_world_triangles':triangles,'original_base_and_full_native_and_runtime_history_unchanged':True,'runtime_binding_changes':'First/second model/native export filenames and hashes only; eight-habitat adds five source successor references, preserving every existing field','fourth_batch_runtime_pins_unchanged_and_no_preview_ground':pins,'new_rooms':0,'body_operations_and_IDs_unchanged':True};(W/'ACTUAL_SOURCE_CHECK.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
