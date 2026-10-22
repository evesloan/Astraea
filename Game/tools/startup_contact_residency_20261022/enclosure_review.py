"""Read actual scene-node transforms from all 88 retained G7 models and two base hulls.
This is a geometric obstruction survey, not pressure or residential design acceptance.
"""
from pathlib import Path
import hashlib, json, struct
import numpy as np

G = Path(__file__).resolve().parents[2]
OUT = G / 'docs/validation/startup_contact_residency_20261022'
rows = json.loads((G/'data/architecture/GROUP7_COMPLETION.json').read_text())['models']
rows += json.loads((G/'data/consolidated_all_eight_20261013/G7_ADDITIONAL.json').read_text())['models']
rows += [{'file':f'AST-HUL-00{i}.glb'} for i in (1,2)]
rooms = json.loads((G/'data/architecture/night_garden_specialty_d15_20261020/PACKAGE_R003.json').read_text())['rooms']
rooms = [r['allocation'] for r in rooms if r['allocation']['allocation_x'][0] > 84]
results = {int(r['source_envelope_index']):[] for r in rooms}
pins, intersecting = {}, []

def matrix(n):
    if 'matrix' in n: return np.array(n['matrix']).reshape(4,4).T
    x,y,z,w = n.get('rotation',[0,0,0,1])
    q = np.array([[1-2*y*y-2*z*z,2*x*y-2*z*w,2*x*z+2*y*w],
                  [2*x*y+2*z*w,1-2*x*x-2*z*z,2*y*z-2*x*w],
                  [2*x*z-2*y*w,2*y*z+2*x*w,1-2*x*x-2*y*y]])
    m = np.eye(4); m[:3,:3] = q @ np.diag(n.get('scale',[1,1,1])); m[:3,3]=n.get('translation',[0,0,0])
    return m

for row in rows:
    path=G/'assets/models'/row['file']; data=path.read_bytes()
    digest=hashlib.sha256(data).hexdigest(); pins[row['file']]=digest
    if 'sha256' in row: assert digest == row['sha256']
    assert data[:4]==b'glTF'
    length,kind=struct.unpack_from('<II',data,12); assert kind==0x4E4F534A
    d=json.loads(data[20:20+length]); start=20+length
    binary=data[start+8:]
    def accessor(i):
        a=d['accessors'][i]; v=d['bufferViews'][a['bufferView']]
        assert not a.get('sparse')
        dtype=np.dtype({5126:'<f4',5125:'<u4',5123:'<u2',5121:'u1'}[a['componentType']])
        count={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']]
        return np.ndarray((a['count'],count),dtype=dtype,buffer=binary,
            offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',dtype.itemsize*count),dtype.itemsize))
    def visit(i,parent):
        n=d['nodes'][i]; transform=parent@matrix(n)
        if 'mesh' in n:
            for p in d['meshes'][n['mesh']]['primitives']:
                assert p.get('mode',4)==4
                points=accessor(p['attributes']['POSITION'])
                points=points@transform[:3,:3].T+transform[:3,3]
                lo,hi=points.min(0),points.max(0)
                if hi[0]<98.9 or hi[1]<93 or lo[1]>97.5 or hi[2]<-98 or lo[2]>98: continue
                triangles=points[accessor(p['indices']).ravel()] if 'indices' in p else points
                triangles=triangles.reshape(-1,3,3)
                mat=d.get('materials',[])[p['material']] if 'material' in p else {}
                alpha=mat.get('alphaMode','OPAQUE'); name=n.get('name',str(i))
                intersecting.append({'file':row['file'],'node':name,'min':lo.tolist(),'max':hi.tolist(),'alpha_mode':alpha})
                # Nine rays through the intended broad opening, not a single center witness.
                for r in rooms:
                    room=int(r['source_envelope_index']); z=sum(r['allocation_z'])/2
                    for y in [94.2,95.1,96.1]:
                        for offset in [-2.1,0,2.1]:
                            yz=np.array([y,z+offset]); a=triangles[:,0,1:]; b=triangles[:,1,1:]-a; c=triangles[:,2,1:]-a
                            det=b[:,0]*c[:,1]-b[:,1]*c[:,0]; valid=np.abs(det)>1e-10
                            u=np.zeros(len(det)); v=u.copy(); delta=yz-a
                            u[valid]=(delta[valid,0]*c[valid,1]-delta[valid,1]*c[valid,0])/det[valid]
                            v[valid]=(b[valid,0]*delta[valid,1]-b[valid,1]*delta[valid,0])/det[valid]
                            hit=valid&(u>=-1e-7)&(v>=-1e-7)&(u+v<=1+1e-7)
                            xs=triangles[:,0,0]+u*(triangles[:,1,0]-triangles[:,0,0])+v*(triangles[:,2,0]-triangles[:,0,0])
                            xs=xs[hit & (xs>=98.95)]
                            if len(xs): results[room].append({'file':row['file'],'node':name,'alpha_mode':alpha,'y':y,'z':round(z+offset,4),'x':sorted(set(np.round(xs,5).tolist()))})
        for child in n.get('children',[]): visit(child,transform)
    for i in d['scenes'][d.get('scene',0)]['nodes']: visit(i,np.eye(4))

summary=[]
for room,hits in results.items():
    opaque=[h for h in hits if h['alpha_mode']=='OPAQUE']
    summary.append({'room':room,'opaque_ray_count':len({(h['y'],h['z']) for h in opaque}),
        'ray_count':9,'hit_files':sorted({h['file'] for h in hits}),
        'opaque_nodes':sorted({h['node'] for h in opaque})})
receipt={'scope':'90 retained installed enclosure models, full scene transforms, nine horizontal frontage rays per outer suite; no pressure/design acceptance',
    'models':len(rows),'pins':pins,'intersecting_meshes':intersecting,'summary':summary,'hits':results,
    'source_changed':False,'visual_acceptance':False,'other_district_obstructions_not_certified':True}
(OUT/'ENCLOSURE_REVIEW.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({'models':len(rows),'intersecting_meshes':len(intersecting),'summary':summary},indent=2))
