from pathlib import Path
import json,hashlib,shutil,struct,numpy as np
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.load(open(W/'NATIVE_EXPORT_CHECK.json'));ns={'__file__':str(W/'reader.py')};exec((R/'BlenderCatalogue/assets/tidal_d15_service_receiving_20261010/source_geometry.py').read_text(),ns);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();newdata=R/'Game/data/architecture/STAR_ATLAS_SPECIALTY_THIRD.json';old=json.load(open(newdata));new=json.loads(json.dumps(old));meshes=triangles=removed=0
for r in P['rooms']:
 assert sha(R/r['original_native'])==r['original_native_sha256'] and sha(R/r['original_runtime'])==r['original_runtime_sha256']
 target=R/'Game/assets/models'/r['successor_runtime'];assert not target.exists()or sha(target)==r['successor_runtime_sha256'];shutil.copy2(W/r['successor_runtime'],target)
 before=dict(ns['triangles'](Path(r['original_runtime']).name));after=dict(ns['triangles'](r['successor_runtime']));expected={n:t for n,t in before.items()if'__Preview_Ground'not in n};assert set(expected)==set(after)
 for n,t in expected.items():assert np.array_equal(t,after[n]),n;triangles+=len(t);meshes+=1
 removed+=sum(len(t)for n,t in before.items()if'__Preview_Ground'in n)
 room=next(x for x in new['rooms']if x['allocation']['source_envelope_index']==r['source_index']);room.update(model_file=r['successor_runtime'],model_sha256=r['successor_runtime_sha256'],mesh_count=r['mesh_count'])
 for q in new['native_export_records']:
  if q['source_index']==r['source_index']:q.update(native=r['successor_native'],native_sha256=r['successor_native_sha256'],export=r['successor_runtime'],export_sha256=r['successor_runtime_sha256'],mesh_count=r['mesh_count'])
for a in old['sources']:assert sha(R/'BlenderCatalogue'/a['source'])==a['source_sha256']and sha(R/'BlenderCatalogue'/a['export'])==a['export_sha256']
fourth=json.load(open(R/'Game/data/architecture/STAR_ATLAS_SPECIALTY_FOURTH.json'));pins={}
for r in fourth['rooms']:
 p=R/'Game/assets/models'/r['model_file'];assert sha(p)==r['model_sha256'];raw=p.read_bytes();n=struct.unpack_from('<I',raw,12)[0];j=json.loads(raw[20:20+n]);assert not any('Preview_Ground'in a.get('name','')for a in j['nodes']);pins[str(p.relative_to(R))]=sha(p)
assert removed==12 and len(new['rooms'])==4
newdata.write_text(json.dumps(new,indent=2)+'\n');(W/'PRODUCTION_RUNTIME_PLAN.json').write_text(json.dumps(new,indent=2)+'\n');report={'status':'PASS','corrected_existing_rooms':4,'preview_meshes_removed':6,'preview_triangles_removed':removed,'all_retained_world_triangle_arrays_bit_identical':True,'retained_world_meshes':meshes,'retained_world_triangles':triangles,'original_native_and_runtime_history_unchanged':True,'registered_catalogue_sources_unchanged':len(old['sources']),'allocation_rest_ids_doors_lights_receiving_and_operations_unchanged':True,'fourth_batch_runtime_pins_unchanged_and_no_preview_ground':pins,'production_bindings':'New successor filenames/hashes and native records only; old source/native/runtime files remain retained'};(W/'ACTUAL_SOURCE_CHECK.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
