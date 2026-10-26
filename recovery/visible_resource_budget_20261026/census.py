"""Bounded source census of dominant actual run006 owners; no engine/import/write to assets."""
import collections, hashlib, json, pathlib, struct
ROOT = pathlib.Path(__file__).resolve().parents[2]
owners = json.loads((ROOT/'recovery/received_visibility_cells_20261026/RESULT006.json').read_text())['last_owners']['rooms']
selected = [x for x in owners if x['parent']=='ApprovedGroup2Homes']
paths = [(x['room'], ROOT/'Game/assets/group2_completion'/f"{x['source_key']}.glb") for x in selected]
paths += [('CustodialDepotReceiving_WIP', ROOT/'Game/assets/models/SOL_D01_directory_10_remaining_r001.glb')]
all_geometry = {}; rows = []
for owner, path in paths:
    data=path.read_bytes(); size,kind=struct.unpack_from('<II',data,12); assert kind==0x4e4f534a
    d=json.loads(data[20:20+size]); length,kind=struct.unpack_from('<II',data,20+size); assert kind==0x004e4942
    binary=data[28+size:28+size+length]
    def acc(i):
        a=dict(d['accessors'][i]); v=d['bufferViews'][a.pop('bufferView')]; assert 'sparse' not in a
        start=v.get('byteOffset',0); b=binary[start:start+v['byteLength']]
        return [a,{k:w for k,w in v.items() if k not in ('buffer','byteOffset')},hashlib.sha256(b).hexdigest()]
    geometry={}; material_groups=set(); total=0
    for mesh in d['meshes']:
        primitives=[]; mats=[]; views=set()
        for p in mesh['primitives']:
            p=dict(p); mats.append(p.pop('material',None)); indices=list(p['attributes'].values())
            if 'indices' in p:indices.append(p['indices'])
            for i in indices:views.add(d['accessors'][i]['bufferView'])
            p['attributes']={k:acc(v) for k,v in p['attributes'].items()}
            if 'indices' in p:p['indices']=acc(p['indices'])
            assert 'targets' not in p
            primitives.append(p)
        payload=[primitives,{k:v for k,v in mesh.items() if k not in ('primitives','name')}]
        key=hashlib.sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest()
        cost=sum(d['bufferViews'][v]['byteLength'] for v in views);total+=cost
        geometry[key]=cost;all_geometry[key]=cost;material_groups.add((key,tuple(mats)))
    rows.append(dict(owner=owner,path=path.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(data).hexdigest(),file_bytes=len(data),mesh_definitions=len(d['meshes']),mesh_instances=sum('mesh' in n for n in d['nodes']),materials=len(d.get('materials',[])),geometry_groups=len(geometry),same_local_material_groups=len(material_groups),definition_buffer_bytes=total,unique_geometry_buffer_bytes=sum(geometry.values())))
result=dict(scope='Raw retained GLB exact accessor/layout census, not GPU memory, imported LOD, live resource ownership or FPS measurement. Material indices only comparable inside each file. Materials are not declared interchangeable.',source='run006 retained owner snapshot; production residency restored after that test',owners=rows,total_mesh_definitions=sum(r['mesh_definitions'] for r in rows),cross_file_geometry_groups=len(all_geometry),definition_buffer_bytes=sum(r['definition_buffer_bytes'] for r in rows),cross_file_geometry_buffer_bytes=sum(all_geometry.values()))
out=pathlib.Path(__file__).with_name('CENSUS.json');out.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
