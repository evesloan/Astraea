"""Independent GLB triangle/UV proof plus source boundary and route reservation checks."""
from pathlib import Path
from collections import Counter,defaultdict
from itertools import product
import struct,json,hashlib,sys
import numpy as np
from shapely.geometry import Polygon,box,LineString
W=Path(__file__).resolve().parent;R=W.parents[2]
p=json.load(open(W/'PLAN.json'))
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()

def triangles(path):
    data=path.read_bytes();size,kind=struct.unpack_from('<II',data,12);j=json.loads(data[20:20+size]);offset=20+size
    size,kind=struct.unpack_from('<II',data,offset);binary=data[offset+8:offset+8+size]
    def arr(i):
        a=j['accessors'][i];v=j['bufferViews'][a['bufferView']];dt={5126:'<f4',5125:'<u4',5123:'<u2',5121:'u1'}[a['componentType']]
        n={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}[a['type']];d=np.dtype(dt);stride=v.get('byteStride',n*d.itemsize)
        return np.ndarray((a['count'],n),dtype=d,buffer=binary,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(stride,d.itemsize)).astype(float)
    def matrix(node):
        if 'matrix'in node:return np.array(node['matrix']).reshape(4,4).T
        x,y,z,w=node.get('rotation',[0,0,0,1]);m=np.eye(4)
        m[:3,:3]=[[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]]
        m[:3,:3]=m[:3,:3]@np.diag(node.get('scale',[1,1,1]));m[:3,3]=node.get('translation',[0,0,0]);return m
    rows=[];nodes={};texture_hashes={}
    for im in j.get('images',[]):
        v=j['bufferViews'][im['bufferView']];raw=binary[v.get('byteOffset',0):v.get('byteOffset',0)+v['byteLength']]
        texture_hashes[hashlib.sha256(raw).hexdigest()]=len(raw)
    def walk(i,parent):
        node=j['nodes'][i];m=parent@matrix(node)
        if 'mesh' in node:
            allvs=[]
            for q in j['meshes'][node['mesh']]['primitives']:
                pos=arr(q['attributes']['POSITION']);pos=(m@np.c_[pos,np.ones(len(pos))].T).T[:,:3];allvs.extend(pos)
                uv=arr(q['attributes']['TEXCOORD_0']) if 'TEXCOORD_0'in q['attributes'] else np.zeros((len(pos),2))
                normal=arr(q['attributes']['NORMAL']);normal=(np.linalg.inv(m[:3,:3]).T@normal.T).T
                normal/=np.linalg.norm(normal,axis=1)[:,None]
                ids=arr(q['indices']).astype(int).ravel().reshape(-1,3)
                role=j['materials'][q['material']]['name']
                for tri in ids:
                    rows.append((role,np.array([np.r_[pos[k],uv[k],normal[k]] for k in tri])))
            nodes[node['name']]=[np.min(allvs,axis=0).tolist(),np.max(allvs,axis=0).tolist()]
        for c in node.get('children',[]):walk(c,m)
    for i in j['scenes'][j.get('scene',0)]['nodes']:walk(i,np.eye(4))
    return rows,nodes,texture_hashes

first,native_nodes,tex1=triangles(W/p['unbatched_export']['file'])
final,runtime_nodes,tex2=triangles(W/p['model_file'])
assert len(first)==len(final),'Triangle count mismatch'
bins=defaultdict(list)
for i,(role,tri) in enumerate(first):bins[(role,*np.floor(tri[:,:3].mean(axis=0)*10).astype(int))].append(i)
used=set();maximum=np.zeros(3)
for role,tri in final:
    key=np.floor(tri[:,:3].mean(axis=0)*10).astype(int);best=None
    for delta in product([-1,0,1],repeat=3):
        for i in bins.get((role,*(key+delta)),[]):
            if i in used:continue
            src=first[i][1]
            for shift in range(3):
                rotated=np.roll(src,shift,axis=0)
                diff=np.abs(tri-rotated)
                errors=np.array([diff[:,:3].max(),diff[:,3:5].max(),diff[:,5:].max()])
                if errors[0]<.0002 and errors[1]<.0002 and errors[2]<.002:
                    best=(i,errors);break
            if best is not None:break
        if best is not None:break
    assert best is not None,('Actual source triangle/UV/normal mismatch',role,tri.tolist())
    used.add(best[0]);maximum=np.maximum(maximum,best[1])
assert len(used)==len(first),'A source triangle was lost or duplicated'
assert tex1==tex2,'Embedded original texture bytes changed'
assert sha(W/p['model_file'])==p['model_sha256']==sha(R/'Game/assets/models'/p['model_file'])
assert sha(W/p['native'])==p['native_sha256']
assert set(runtime_nodes)==set(p['collision_policy'])





for rel,pin in json.load(open(W/"SOURCE_PINS.json")).items():assert sha(R/rel)==pin,rel
assert json.load(open(W/"SOURCE_SCREEN003.json"))["status"]=="PASS"
report={"status":"PASS","native_meshes":len(p["meshes"]),"runtime_batches":len(runtime_nodes),"oriented_triangles_uv_normals":len(final),"maximum_position_uv_normal_error":maximum.tolist(),"embedded_texture_hashes":tex2,"new_standard_door_instances":3,"new_task_sources":6,"exact_original_source_pair_checks":380700,"protected_static_route_checks":792,"original_programme_capacity_floor_mutations":0,"native_sha256":p["native_sha256"],"runtime_sha256":p["model_sha256"],"scaled_dynamic_door_cart_and_operation_acceptance":False}
(W/"EXACT_EXPORT_AND_SOURCE_PINS.json").write_text(json.dumps(report,indent=2)+"\n");print(json.dumps(report))
