"""Read actual glTF transforms and triangle payloads without import side effects."""
import json,struct,numpy as np
def triangles(path):
    raw=path.read_bytes();assert raw[:4]==b'glTF' and len(raw)==struct.unpack_from('<I',raw,8)[0]
    size=struct.unpack_from('<I',raw,12)[0];d=json.loads(raw[20:20+size]);b=raw[28+size:]
    def accessor(i):
        a=d['accessors'][i];v=d['bufferViews'][a['bufferView']]
        dt={5121:'u1',5123:'<u2',5125:'<u4',5126:'<f4'}[a['componentType']];width={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']]
        item=np.dtype(dt).itemsize
        return np.ndarray((a['count'],width),dtype=dt,buffer=b,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',item*width),item)).copy()
    def pose(n):
        if 'matrix' in n:return np.array(n['matrix']).reshape(4,4).T
        x,y,z,w=n.get('rotation',[0,0,0,1]);m=np.eye(4)
        m[:3,:3]=np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])@np.diag(n.get('scale',[1,1,1]))
        m[:3,3]=n.get('translation',[0,0,0]);return m
    def walk(i,parent):
        n=d['nodes'][i];m=parent@pose(n)
        if 'mesh' in n:
            for p in d['meshes'][n['mesh']]['primitives']:
                v=accessor(p['attributes']['POSITION']).astype(float);v=(np.column_stack([v,np.ones(len(v))])@m.T)[:,:3]
                idx=accessor(p['indices']).reshape(-1) if 'indices' in p else np.arange(len(v))
                yield n.get('name','mesh'),v[idx.reshape(-1,3)],n.get('extras',{})
        for c in n.get('children',[]):yield from walk(c,m)
    for i in d['scenes'][d.get('scene',0)]['nodes']:yield from walk(i,np.eye(4))
