from pathlib import Path
import collections, hashlib, json, shutil, struct
base=Path(__file__).parent
repo=base.parent/'Astraea-construction-6c52b7a8'
src=base/'tram-selected-operation-002'
dst=repo/'recovery/tram_passenger_successor_20261024/laptop_selected_operation_002'
dst.mkdir(exist_ok=False)
files={}
for p in sorted(src.iterdir()):
    if not p.is_file(): continue
    data=p.read_bytes()
    (dst/p.name).write_bytes(data)
    files[p.name]={'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
out=(src/'stdout.log').read_text(encoding='utf-8',errors='replace').splitlines()
err=(src/'stderr.log').read_text(encoding='utf-8',errors='replace').splitlines()
samples=[json.loads(s.split('TRAM_ROUTE_SAMPLE ',1)[1]) for s in out if s.startswith('TRAM_ROUTE_SAMPLE ')]
loads=[json.loads(s.split('GROUP2_MESH_LOAD ',1)[1]) for s in out if s.startswith('GROUP2_MESH_LOAD ')]
errors=collections.Counter(s for s in err if s.startswith(('ERROR:','SCRIPT ERROR:')))
inventory=[]
for key in dict.fromkeys(r['key'] for r in loads):
    p=repo/f'Game/assets/group2_completion/{key}.glb'
    with p.open('rb') as f:
        header=f.read(20)
        length,kind=struct.unpack_from('<II',header,12)
        assert kind==0x4e4f534a
        j=json.loads(f.read(length))
    inventory.append({'key':key,'bytes':p.stat().st_size,'nodes':len(j.get('nodes',[])),'meshes':len(j.get('meshes',[])),'materials':len(j.get('materials',[])),'textures':len(j.get('textures',[])),'primitives':sum(len(m['primitives']) for m in j.get('meshes',[]))})
receipt={'revision':'7182a3676a245a9c3a860881f7f54dd59e081ba5','files':files,'result_json_present':(src/'result.json').exists(),'errors':dict(errors),'route_samples':samples,'group2_loads':loads,'source_glb_inventory':inventory,'chronology_limit':'stdout and stderr are separately buffered. Last printed load before the first error cannot be assigned conclusively without a shared timestamp. Generic RID allocator path does not identify its owner. Resource count is all Resources, not a per-owner RID count.','acceptance':'Safety-stopped during movement; no completed return or median/p95 result. Not OOM, not a native-crash claim, no route/playability/performance acceptance.'}
(dst/'EVIDENCE.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'destination':str(dst),'errors':dict(errors),'sample_count':len(samples),'first_sample':samples[0] if samples else None,'last_sample':samples[-1] if samples else None,'last_loads':loads[-10:],'inventory_last':inventory[-10:]},indent=2))
