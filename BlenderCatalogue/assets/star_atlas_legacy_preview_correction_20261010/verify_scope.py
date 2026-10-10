from pathlib import Path
import subprocess,json,hashlib
W=Path(__file__).resolve().parent;R=W.parents[2];base='f068815e31df16cf8fbc194de62ef7222436f383';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();show=lambda f:subprocess.check_output(['git','show',base+':'+f],cwd=R)
for batch in ['FIRST','SECOND']:
 f=f'Game/data/architecture/STAR_ATLAS_SPECIALTY_{batch}.json';a=json.loads(show(f));b=json.load(open(R/f))
 for p in [a,b]:
  for room in p['rooms']:
   for k in ['model_file','model_sha256','mesh_count']:room.pop(k)
  for v in p['native_export_records']:
   for k in ['native','native_sha256','export','export_sha256','mesh_count']:v.pop(k)
 assert a==b
f='Game/data/architecture/STAR_ATLAS_EIGHT_HABITATS.json';a=json.loads(show(f));b=json.load(open(R/f))
for room in b['rooms']:
 room.pop('production_assembly_native',None);room.pop('production_assembly_native_sha256',None)
assert a==b
for batch in ['THIRD','FOURTH']:
 f=f'Game/data/architecture/STAR_ATLAS_SPECIALTY_{batch}.json';assert (R/f).read_bytes()==show(f)
for r in json.load(open(W/'NATIVE_EXPORT_CHECK.json'))['rooms']:
 for k in ['original_native','original_runtime','original_full_native']:assert sha(R/r[k])==r[k+'_sha256']
 for k in ['successor_native','successor_full_native']:assert sha(W/r[k])==r[k+'_sha256']
# Every non-room active production model remains byte-identical to the parent.
import sys
sys.path.insert(0,str(R/'Game/tools'));from validate_production_glb import star_atlas_files
roomfiles=set()
for batch in ['FIRST','SECOND','THIRD','FOURTH']:
 roomfiles.update(q['model_file']for q in json.load(open(R/f'Game/data/architecture/STAR_ATLAS_SPECIALTY_{batch}.json'))['rooms'])
pins={}
for p in star_atlas_files(R/'Game'):
 if p.name not in roomfiles:
  rel=str(p.relative_to(R));assert p.read_bytes()==show(rel);pins[rel]=sha(p)
(W/'RECEIVING_NATIVE_CHECK.json').write_text(json.dumps({'status':'PASS','receiving_fitting_commons_models_unchanged':pins,'new_receiving_geometry':0},indent=2)+'\n')
p=W/'ACTUAL_SOURCE_CHECK.json';q=json.load(open(p));q.update(exact_metadata_scope_verified=True,all_other_room_metadata_unchanged=True,third_fourth_bindings_unchanged=True,original_base_full_native_runtime_hashes_unchanged=True,non_room_runtime_geometry_unchanged=pins);p.write_text(json.dumps(q,indent=2)+'\n');print('PASS precise metadata scope, original history hashes and all non-room production geometry')
