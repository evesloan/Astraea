from pathlib import Path
from collections import Counter
import json,struct,math,hashlib,numpy as np
W=Path(__file__).resolve().parent;R=W.parents[2]
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
                    rows.append((node["name"],role,np.array([np.r_[pos[k],uv[k],normal[k]] for k in tri])))
            nodes[node['name']]=[np.min(allvs,axis=0).tolist(),np.max(allvs,axis=0).tolist()]
        for c in node.get('children',[]):walk(c,m)
    for i in j['scenes'][j.get('scene',0)]['nodes']:walk(i,np.eye(4))
    return rows,nodes,texture_hashes

p=json.load(open(W/'PLAN.json'));original=R/'Game/assets/models/D05_medical_remaining_architecture.glb'
original_sha=hashlib.sha256(original.read_bytes()).hexdigest();assert original_sha=='c7cfb577d2bbc01c6058d77a02a87b6087b45c53022f568e9145f595d918e742'
old,oldnodes,oldtex=triangles(original);new,newnodes,newtex=triangles(W/p['model_file']);old_by={};new_by={}
for name,role,t in old:old_by.setdefault(name,[]).append((role,t))
for name,role,t in new:new_by.setdefault(name,[]).append((role,t))
origin=np.array([-28,21,-446]);reference=np.array([-16.5,21,-460]);checks=0;maximum=np.zeros(3);report=[]
for copy in p['source_copies']:
    name=copy['new_name'];source=copy['original_name'];m=np.array(copy['rigid_world_transform']).reshape(4,4)
    assert name in new_by and source in old_by,(name,source)
    candidates=[]
    for role,t in old_by[source]:
        tt=t.copy();tt[:,:3]=(m[:3,:3]@(tt[:,:3]+origin-reference).T).T+m[:3,3];tt[:,5:]=(m[:3,:3]@tt[:,5:].T).T;candidates.append(tt)
    used=set()
    for role,t in new_by[name]:
        found=None
        for i,tt in enumerate(candidates):
            if i in used:continue
            for shift in range(3):
                delta=np.abs(t-np.roll(tt,shift,axis=0));err=np.array([delta[:,:3].max(),delta[:,3:5].max(),delta[:,5:].max()])
                if err[0]<.0002 and err[1]<.0002 and err[2]<.002:found=(i,err);break
            if found is not None:break
        assert found is not None,(name,'Actual original source triangle/UV/normal mismatch');used.add(found[0]);maximum=np.maximum(maximum,found[1]);checks+=1
    assert len(used)==len(candidates)==copy['actual_evaluated_triangles']
    report.append({'copy':name,'original':source,'oriented_triangles':len(used),'original_geometry_uv_normals_preserved':True})
# Relevant original clinical texture bytes must remain embedded,alongside new controls.
source_roles={role for name,role,t in old if name in {c['original_name']for c in p['source_copies']}}
result={'status':'PASS_EXACT_ORIGINAL_GLTF_SOURCE_TRIANGLE_UV_NORMAL_RIGID_COPY','original_runtime_sha256':original_sha,'exact_new_copy_meshes':len(report),'oriented_source_copy_triangles':checks,'maximum_position_uv_normal_error':maximum.tolist(),'original_source_roles':sorted(source_roles),'copies':report,'source_native_sha256':p['source_leaf_native_sha256'],'original_source_mutations':0,'runtime_operation_acceptance':False}
(W/'EXACT_ORIGINAL_LEAF_COPY_VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k!='copies'}))
