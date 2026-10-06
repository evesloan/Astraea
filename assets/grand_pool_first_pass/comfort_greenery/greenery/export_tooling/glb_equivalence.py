"""Read-only actual GLB attribute decoder and bijective triangle/corner matcher.

No Blender or authoring-module dependency. No nearest-surface approximation:
every source and exported triangle, material role, winding and UV/normal corner
must participate in a one-to-one match at the fixed source tolerance.
"""
import sys
sys.dont_write_bytecode=True
import json,struct,hashlib,itertools,math
from pathlib import Path
import numpy as np
POSITION_TOLERANCE=2e-6
UV_TOLERANCE=2e-6
NORMAL_TOLERANCE=2e-6

def decode(path):
    data=Path(path).read_bytes();magic,version,length=struct.unpack_from('<III',data);assert magic==0x46546c67 and version==2 and length==len(data);off=12;doc=None;binary=None
    while off<len(data):
        n,kind=struct.unpack_from('<II',data,off);assert off+8+n<=len(data);chunk=data[off+8:off+8+n];off+=8+n
        if kind==0x4e4f534a:assert doc is None;doc=json.loads(chunk)
        elif kind==0x004e4942:assert binary is None;binary=chunk
        else:raise AssertionError('Unexpected GLB chunk')
    assert doc is not None and binary is not None and len(doc.get('buffers',[]))==1;assert 'uri' not in doc['buffers'][0];assert doc['buffers'][0]['byteLength']<=len(binary);assert not doc.get('animations') and not doc.get('skins') and not doc.get('cameras');assert 'KHR_draco_mesh_compression' not in doc.get('extensionsUsed',[])
    def accessor(index):
        a=doc['accessors'][index];assert not a.get('sparse') and not a.get('normalized');bv=doc['bufferViews'][a['bufferView']];assert bv.get('buffer',0)==0;kind={5121:'B',5123:'H',5125:'I',5126:'f'}[a['componentType']];n={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']];fmt='<'+kind*n;size=struct.calcsize(fmt);stride=bv.get('byteStride',size);start=bv.get('byteOffset',0)+a.get('byteOffset',0);assert start+(a['count']-1)*stride+size<=bv.get('byteOffset',0)+bv['byteLength']<=len(binary);values=np.asarray([struct.unpack_from(fmt,binary,start+k*stride) for k in range(a['count'])],dtype=np.float64);assert np.isfinite(values).all();return values
    def transform(node):
        if 'matrix' in node:return np.asarray(node['matrix'],dtype=np.float64).reshape((4,4),order='F')
        x,y,z,w=node.get('rotation',[0,0,0,1]);r=np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]],float);m=np.eye(4);m[:3,:3]=r@np.diag(node.get('scale',[1,1,1]));m[:3,3]=node.get('translation',[0,0,0]);return m
    nodes=[];primitives=[];visited=set()
    def visit(index,parent):
        assert index not in visited,'Instanced or cyclic export node';visited.add(index);n=doc['nodes'][index];matrix=parent@transform(n);record=dict(index=index,name=n.get('name'),extras=n.get('extras',{}),matrix=matrix,mesh=n.get('mesh'));nodes.append(record)
        if 'mesh' in n:
            assert np.max(np.abs(matrix-np.eye(4)))<=POSITION_TOLERANCE,'Runtime mesh must have identity native transform';mesh=doc['meshes'][n['mesh']]
            for prim in mesh['primitives']:
                assert prim.get('mode',4)==4 and not prim.get('targets') and not prim.get('extensions');attrs=prim['attributes'];assert {'POSITION','NORMAL','TEXCOORD_0'}<=attrs.keys();assert set(attrs)=={'POSITION','NORMAL','TEXCOORD_0'},'Unexpected vertex attribute';p=accessor(attrs['POSITION']);normal=accessor(attrs['NORMAL']);uv=accessor(attrs['TEXCOORD_0']);assert len(p)==len(normal)==len(uv);ix=accessor(prim['indices']).astype(np.int64).ravel() if 'indices'in prim else np.arange(len(p));assert len(ix)%3==0 and ix.min()>=0 and ix.max()<len(p);ix=ix.reshape((-1,3));world=(matrix[:3,:3]@p.T).T+matrix[:3,3];norm=(np.linalg.inv(matrix[:3,:3]).T@normal.T).T;assert np.all(np.abs(np.linalg.norm(norm,axis=1)-1)<NORMAL_TOLERANCE);primitives.append(dict(node=record,material_index=prim['material'],positions=world[ix],normals=norm[ix],uvs=uv[ix],triangles=len(ix)))
        for child in n.get('children',[]):visit(child,matrix)
    scene=doc['scenes'][doc.get('scene',0)];assert len(scene['nodes'])==1,'Exactly one runtime root required'
    for n in scene['nodes']:visit(n,np.eye(4))
    assert len(visited)==len(doc['nodes']),'Unreferenced source/export nodes';images=[]
    for im in doc.get('images',[]):
        assert 'uri' not in im and im.get('mimeType')=='image/png';bv=doc['bufferViews'][im['bufferView']];start=bv.get('byteOffset',0);raw=binary[start:start+bv['byteLength']];assert raw.startswith(b'\x89PNG\r\n\x1a\n');images.append(dict(sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw)))
    return dict(doc=doc,nodes=nodes,primitives=primitives,images=images)

def match_triangles(expected,actual):
    """Role-local bijection with cyclic winding, full corner UVs and normals."""
    ep=np.asarray(expected['positions'],np.float64);eu=np.asarray(expected['uvs'],np.float64);en=np.asarray(expected['normals'],np.float64);ap=np.asarray(actual['positions'],np.float64);au=np.asarray(actual['uvs'],np.float64);an=np.asarray(actual['normals'],np.float64);assert ep.shape==ap.shape and eu.shape==au.shape and en.shape==an.shape,'Triangle/corner cardinality differs'
    size=POSITION_TOLERANCE*2;bins={}
    for i,c in enumerate(ep.mean(axis=1)):bins.setdefault(tuple(np.floor(c/size).astype(np.int64)),[]).append(i)
    unmatched=set(range(len(ep)));maxp=maxu=maxn=0.0
    for ai,c in enumerate(ap.mean(axis=1)):
        key=np.floor(c/size).astype(np.int64);possible=[]
        for offset in itertools.product([-1,0,1],repeat=3):possible.extend(i for i in bins.get(tuple(key+offset),[]) if i in unmatched)
        match=None
        for ei in possible:
            for shift in range(3):
                q=np.roll(ap[ai],-shift,axis=0);pd=float(np.max(np.linalg.norm(ep[ei]-q,axis=1)))
                if pd>POSITION_TOLERANCE:continue
                ud=float(np.max(np.abs(eu[ei]-np.roll(au[ai],-shift,axis=0))));nd=float(np.max(np.linalg.norm(en[ei]-np.roll(an[ai],-shift,axis=0),axis=1)))
                if ud<=UV_TOLERANCE and nd<=NORMAL_TOLERANCE:match=(ei,pd,ud,nd);break
            if match is not None:break
        assert match is not None,'No matching source triangle with equal winding, material, UV and normals at exported triangle '+str(ai)
        ei,pd,ud,nd=match;unmatched.remove(ei);maxp=max(maxp,pd);maxu=max(maxu,ud);maxn=max(maxn,nd)
    assert not unmatched;return dict(triangles=len(ep),max_position_deviation_m=maxp,max_uv_deviation=maxu,max_normal_deviation=maxn)

def material_check(decoded,role,material_index,spec):
    doc=decoded['doc'];mat=doc['materials'][material_index];assert mat.get('extras',{}).get('astraea_material_role')==role;assert mat.get('extras',{}).get('alpha_contract')=='OPAQUE';assert mat.get('extras',{}).get('uv_contract')==spec['uv_contract'];pbr=mat.get('pbrMetallicRoughness',{});assert mat.get('alphaMode','OPAQUE')=='OPAQUE';assert bool(mat.get('doubleSided',False))==bool(spec['double_sided']);assert abs(pbr.get('metallicFactor',1)-spec['metallic'])<=1e-6;assert abs(pbr.get('roughnessFactor',1)-spec['roughness'])<=1e-6;assert np.max(np.abs(np.array(pbr.get('baseColorFactor',[1,1,1,1]))-[1,1,1,1]))<=1e-6;assert mat.get('emissiveFactor',[0,0,0])==[0,0,0];assert not mat.get('emissiveTexture') and not mat.get('normalTexture') and not mat.get('occlusionTexture');assert not pbr.get('metallicRoughnessTexture');assert not mat.get('extensions'),'Unexpected material extension'
    bt=pbr['baseColorTexture'];assert bt.get('texCoord',0)==0 and not bt.get('extensions');tex=doc['textures'][bt['index']];assert not tex.get('extensions');image=decoded['images'][tex['source']];assert image['sha256']==spec['sha256'],'Packed image byte mismatch for '+role
    if 'sampler'in tex:
        sampler=doc['samplers'][tex['sampler']];assert sampler.get('wrapS',10497)==10497 and sampler.get('wrapT',10497)==10497;assert sampler.get('magFilter',9729)==9729;assert sampler.get('minFilter',9987) in [9729,9987]
    return dict(material_role=role,material_name=mat.get('name'),material_index=material_index,packed_image_sha256=image['sha256'],packed_image_bytes=image['bytes'],alpha='OPAQUE',double_sided=spec['double_sided'])
