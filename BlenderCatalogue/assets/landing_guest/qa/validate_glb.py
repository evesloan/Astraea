"""Independent glTF binary inspection: no Blender imports."""
import json, struct, math, hashlib,io
from pathlib import Path
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
CAT=ROOT.parents[1]
COMP={5120:('b',1),5121:('B',1),5122:('h',2),5123:('H',2),5125:('I',4),5126:('f',4)}
WIDTH={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}

def read(path):
    raw=path.read_bytes();magic,version,total=struct.unpack_from('<4sII',raw)
    assert magic==b'glTF' and version==2 and total==len(raw)
    n,k=struct.unpack_from('<II',raw,12);doc=json.loads(raw[20:20+n]);off=20+n
    bn,bk=struct.unpack_from('<II',raw,off);blob=raw[off+8:off+8+bn]
    assert bk==0x004e4942
    return doc,blob

def accessor(doc,blob,idx):
    a=doc['accessors'][idx];v=doc['bufferViews'][a['bufferView']];code,size=COMP[a['componentType']];w=WIDTH[a['type']]
    offset=v.get('byteOffset',0)+a.get('byteOffset',0);stride=v.get('byteStride',w*size)
    return np.array([struct.unpack_from('<'+code*w,blob,offset+i*stride) for i in range(a['count'])])

def matrix(node):
    if 'matrix' in node:return np.array(node['matrix']).reshape(4,4).T
    x,y,z,w=node.get('rotation',[0,0,0,1]);rot=np.array([[1-2*y*y-2*z*z,2*x*y-2*z*w,2*x*z+2*y*w],[2*x*y+2*z*w,1-2*x*x-2*z*z,2*y*z-2*x*w],[2*x*z-2*y*w,2*y*z+2*x*w,1-2*x*x-2*y*y]])
    m=np.eye(4);m[:3,:3]=rot@np.diag(node.get('scale',[1,1,1]));m[:3,3]=node.get('translation',[0,0,0]);return m

def validate(path):
    doc,blob=read(path);points=[];tris=0;minarea=1e8;badn=0;roles=set();textures=set();badverts=0;node_determinants=[];negative_winding=0;collapsed_uv_area=0;collapsed_uv_triangles=0;texture_matches={}
    def walk(idx,parent):
        nonlocal tris,minarea,badn,badverts,negative_winding,collapsed_uv_area,collapsed_uv_triangles
        node=doc['nodes'][idx];m=parent@matrix(node);node_determinants.append(float(np.linalg.det(m[:3,:3])))
        if 'mesh' in node:
            for p in doc['meshes'][node['mesh']]['primitives']:
                v=accessor(doc,blob,p['attributes']['POSITION']);n=accessor(doc,blob,p['attributes']['NORMAL']);uv=accessor(doc,blob,p['attributes']['TEXCOORD_0']);i=accessor(doc,blob,p['indices']).reshape(-1,3)
                assert np.isfinite(v).all() and np.isfinite(n).all() and np.isfinite(uv).all()
                assert i.max()<len(v) and i.min()>=0
                t=v[i];cross=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);area=np.linalg.norm(cross,axis=1)*.5
                minarea=min(minarea,float(area.min()));tris+=len(i);badn+=int((np.abs(np.linalg.norm(n,axis=1)-1)>.005).sum())
                tuv=uv[i];aa=tuv[:,1]-tuv[:,0];bb=tuv[:,2]-tuv[:,0];uarea=np.abs(aa[:,0]*bb[:,1]-aa[:,1]*bb[:,0])*.5;collapsed=uarea<1e-12
                collapsed_uv_area+=float(area[collapsed].sum());collapsed_uv_triangles+=int(collapsed.sum())
                nn=n[i].mean(axis=1);negative_winding+=int(((cross*nn).sum(axis=1)<-1e-10).sum())
                points.extend((m@np.column_stack([v,np.ones(len(v))]).T).T[:,:3])
                mat=doc['materials'][p['material']];roles.add(mat['name']);tex=mat.get('pbrMetallicRoughness',{}).get('baseColorTexture');assert tex is not None
                ti=doc['textures'][tex['index']]['source'];im=doc['images'][ti];assert 'bufferView' in im;assert im['mimeType']=='image/png';textures.add(ti)
                bv=doc['bufferViews'][im['bufferView']];start=bv.get('byteOffset',0);embedded=Image.open(io.BytesIO(blob[start:start+bv['byteLength']])).convert('RGBA');role=mat['name'].replace('ASTRAEA_','');source_path=ROOT/'textures/guest_arrival_original.png' if role=='guest_arrival_original' else CAT/'materials'/(role+'.png');source=Image.open(source_path).convert('RGBA');texture_matches[role]=embedded.size==source.size and embedded.tobytes()==source.tobytes()
        for child in node.get('children',[]):walk(child,m)
    for idx in doc['scenes'][doc.get('scene',0)]['nodes']:walk(idx,np.eye(4))
    a=np.array(points);lo=a.min(0);hi=a.max(0)
    return {'file':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'triangle_count':tris,'bounds_gltf_y_up':{'min':lo.tolist(),'max':hi.tolist(),'dimensions':(hi-lo).tolist()},'finite_geometry':True,'uv_present_and_finite':True,'minimum_triangle_area_m2':minarea,'zero_area_triangles':bool(minarea==0),'non_unit_normals':badn,'triangles_opposed_to_vertex_normals':negative_winding,'collapsed_uv_surface_area_m2':collapsed_uv_area,'collapsed_uv_triangles':collapsed_uv_triangles,'material_roles':sorted(roles),'embedded_png_texture_count':len(textures),'embedded_texture_matches_shared_pixels':texture_matches,'runtime_mesh_count':len(doc['meshes']),'runtime_primitive_count':sum(len(x['primitives']) for x in doc['meshes']),'node_transform_determinants':node_determinants,'passed':minarea>1e-12 and badn==0 and negative_winding==0 and collapsed_uv_triangles==0 and all(texture_matches.values()) and all(d>0 for d in node_determinants)}

records=[validate(p) for p in sorted((ROOT/'exports').glob('*.glb'))]
out={'inspector':'Independent Python standard GLB chunk and accessor parser, numpy transforms; no Blender APIs','results':records,'all_passed':all(r['passed'] for r in records)}
(ROOT/'qa/glb_validation.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
