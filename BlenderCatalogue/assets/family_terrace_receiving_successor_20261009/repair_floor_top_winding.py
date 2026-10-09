#!/usr/bin/env python3
"""Bounded derivative: correct downward horizontal tops of semantic floor parts.
Preserves original GLB; edits only triangle order and dedicated top normals.
No Blender, Godot, imports, or geometry regeneration.
"""
import collections, hashlib, json, math, os, pathlib, struct
import numpy as np
ROOT = pathlib.Path(__file__).resolve().parents[3]
SOURCE = ROOT/'Game/assets/models/FAMILY_TERRACE_ARCHITECTURE_r001.glb'
OUTPUT = SOURCE.with_name('FAMILY_TERRACE_ARCHITECTURE_r002.glb')
MANIFEST = ROOT/'Game/data/architecture/FAMILY_TERRACE_RECEIVING.json'
EXPECTED = '1d1f2462e4cb916b8a98c7e547616f5e36bc207e6cae222e786c367146850a09'
NATIVE = ROOT/'BlenderCatalogue/assets/residential_hotels/aft_houses_20261007_r001/residential-neighborhood-courts-20261007/family_terrace_house/outputs/house_r001'
PLAN = NATIVE/'PLAN.json'
PLAN_SHA = '227f25c59826687b0571d884d04a5674b3f46bd351ecab79476d86c892df798f'
assert hashlib.sha256(PLAN.read_bytes()).hexdigest() == PLAN_SHA
plan = json.loads(PLAN.read_text())
plan_parts = {p['name']:p for p in plan['parts']}
assert len(plan_parts) == len(plan['parts'])
raw = SOURCE.read_bytes()
assert (NATIVE/'architecture.glb').read_bytes() == raw
assert hashlib.sha256(raw).hexdigest() == EXPECTED
out = bytearray(raw)
json_len = struct.unpack_from('<I', raw, 12)[0]
g = json.loads(raw[20:20+json_len]); bin_offset = 28+json_len
assert struct.unpack_from('<I',raw,24+json_len)[0] == 0x004e4942

def accessor(i, data=raw):
    a = g['accessors'][i]; bv = g['bufferViews'][a['bufferView']]
    assert 'sparse' not in a and bv.get('buffer',0)==0
    dt = {5126:'<f4',5125:'<u4',5123:'<u2'}[a['componentType']]
    width = {'VEC3':3,'SCALAR':1}[a['type']]
    size = np.dtype(dt).itemsize
    assert bv.get('byteStride',size*width)==size*width
    off = bin_offset+bv.get('byteOffset',0)+a.get('byteOffset',0)
    return np.frombuffer(data,dtype=dt,count=a['count']*width,offset=off).reshape(-1,width),off,size

changes=[]; all_parts=0; verified_ranges=0; allowed=set()
for node in g['nodes']:
    extra=node.get('extras',{})
    if extra.get('category')!='floor' or not extra.get('runtime_collision'):continue
    assert not any(k in node for k in ('matrix','translation','rotation','scale'))
    mesh=g['meshes'][node['mesh']]; assert len(mesh['primitives'])==1
    prim=mesh['primitives'][0];assert prim.get('mode',4)==4
    verts,_,_=accessor(prim['attributes']['POSITION'])
    normals,normoff,_=accessor(prim['attributes']['NORMAL'])
    indices,ixoff,ixsize=accessor(prim['indices']); ids=indices.reshape(-1,3)
    assert len(normals)==len(verts)
    ranges=extra['source_part_ranges']; ownership=np.full(len(verts),-1,dtype=int)
    for pi,part in enumerate(ranges):
        start=part['vertex_start'];end=start+part['vertex_count']
        assert start>=0 and end<=len(verts) and np.all(ownership[start:end]==-1)
        ownership[start:end]=pi
    assert np.all(ownership>=0)
    assert np.all(ownership[ids]==ownership[ids[:,0]][:,None]), 'Cross-part triangles'
    verified_ranges+=1
    tri=verts[ids];cross=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0])
    for pi,part in enumerate(ranges):
        all_parts+=1;start=part['vertex_start'];end=start+part['vertex_count']
        source_part = plan_parts[part['source_part_id']]
        assert source_part['category'] == 'floor'
        assert np.array_equal(np.asarray(source_part['verts'],dtype='<f4'),verts[start:end])
        assert extra['source_plan_sha256'] == PLAN_SHA
        top=float(verts[start:end,1].max()); bottom=float(verts[start:end,1].min())
        if top-bottom<1e-5:continue # Flat sheets have no distinguishable solid top.
        own=ownership[ids[:,0]]==pi
        topface=own & np.all(np.abs(tri[:,:,1]-top)<1e-5,axis=1)
        bad=topface & (cross[:,1]<-1e-7)
        ti=np.flatnonzero(bad)
        if not len(ti):continue
        vi=np.unique(ids[ti])
        # Dedicated normals only: touching sides/slopes must not be changed.
        touching=np.any(np.isin(ids,vi),axis=1)
        assert np.all(topface[touching]), f'Non-dedicated top normals: {part}'
        assert np.all(normals[vi,1] < -0.99), (part['source_part_id'], 'unexpected non-downward top normals')
        for index in ti:
            off=ixoff+int(index)*3*ixsize
            packed=ids[index,[0,2,1]].astype(indices.dtype).tobytes()
            out[off:off+3*ixsize]=packed;allowed.update(range(off,off+3*ixsize))
        for vertex in vi:
            off=normoff+int(vertex)*12
            out[off:off+12]=struct.pack('<fff',0.,1.,0.);allowed.update(range(off,off+12))
        changes.append({'mesh':node['name'],'part':part['source_part_id'],'top_y':top,
                        'triangle_indices':ti.tolist(),'normal_vertex_indices':vi.tolist()})
assert all_parts==35 and len(changes)==18 and sum(len(c['triangle_indices']) for c in changes)==62
actual={i for i,(a,b) in enumerate(zip(raw,out)) if a!=b}
assert actual<=allowed and len(raw)==len(out)
# All mesh POSITION bytes and all non-index/non-normal bytes remain identical.
# Static exact ray witnesses across all 82 exterior approaches on repaired asset.
triangles=[]
for node in g['nodes']:
    if not node.get('extras',{}).get('runtime_collision'):continue
    for prim in g['meshes'][node['mesh']]['primitives']:
        v,_,_=accessor(prim['attributes']['POSITION'],out)
        ix,_,_=accessor(prim['indices'],out);triangles.extend(v[ix.reshape(-1,3)])
t=np.asarray(triangles);a=t[:,0];e1=t[:,1]-a;e2=t[:,2]-a
cross=np.cross(e1,e2);det=e1[:,0]*e2[:,2]-e1[:,2]*e2[:,0]
units=json.loads((ROOT/'Game/data/architecture/FAMILY_TERRACE_UNITS.json').read_text())['units']
witness=[]
for unit in units:
    origin=np.asarray(unit['source_origin_world_xyz']);yaw=unit['source_yaw_godot']
    point=origin+np.array([math.sin(yaw),0.,math.cos(yaw)]);d=point-a
    with np.errstate(divide='ignore',invalid='ignore'):
        u=(d[:,0]*e2[:,2]-d[:,2]*e2[:,0])/det
        v=(e1[:,0]*d[:,2]-e1[:,2]*d[:,0])/det
        y=a[:,1]+u*e1[:,1]+v*e2[:,1]
        hit=(abs(det)>1e-8)&(u>=-1e-6)&(v>=-1e-6)&(u+v<=1+1e-6)&(cross[:,1]>1e-7)&(abs(y-point[1])<.0001)
    assert np.any(hit),unit['rebuild_identity']
    witness.append({'room':unit['rebuild_identity'],'point':point.tolist(),'upward_top_hits':int(hit.sum())})
assert len(witness)==82
# Write derivative first, verify it, then atomically switch manifest binding.
if OUTPUT.exists(): assert OUTPUT.read_bytes()==out,'Refusing to replace different surviving derivative'
else:
    temporary=OUTPUT.with_suffix('.glb.tmp');temporary.write_bytes(out);os.replace(temporary,OUTPUT)
sha=hashlib.sha256(out).hexdigest();assert hashlib.sha256(OUTPUT.read_bytes()).hexdigest()==sha
assert SOURCE.read_bytes()==raw
manifest=json.loads(MANIFEST.read_text())
assert manifest['model_file'] in (SOURCE.name,OUTPUT.name)
manifest['model_file']=OUTPUT.name;manifest['source_sha256']=sha
manifest['floor_winding_successor']={'retained_model_file':SOURCE.name,'retained_sha256':EXPECTED,
 'receipt':'BlenderCatalogue/assets/family_terrace_receiving_successor_20261009/floor_winding_receipt.json'}
tmp=MANIFEST.with_suffix('.json.tmp');tmp.write_text(json.dumps(manifest,indent=2)+'\n');os.replace(tmp,MANIFEST)
receipt={'status':'STATIC_PASS_RUNTIME_PENDING','source_file':str(SOURCE.relative_to(ROOT)),
 'source_sha256':EXPECTED,'plan_sha256':PLAN_SHA,'native_source_file':str((NATIVE/'architecture.glb').relative_to(ROOT)),'derivative_file':str(OUTPUT.relative_to(ROOT)),'derivative_sha256':sha,
 'policy':'Only downward horizontal maxY tops of solid runtime-collision floor source parts. No position/material/topology membership changes; no blanket double-sided collision.',
 'verified_floor_mesh_ranges':verified_ranges,'examined_floor_parts':all_parts,
 'changed_parts':len(changes),'changed_triangles':sum(len(c['triangle_indices']) for c in changes),
 'changed_normal_vertices':sum(len(c['normal_vertex_indices']) for c in changes),
 'changed_byte_count':len(actual),'changes':changes,'street_witness_count':len(witness),'street_witnesses':witness,
 'remaining_scope':'Runtime engine validation required. Sloped faces, flat sheets, walls and roofs excluded.'}
receipt_path=pathlib.Path(__file__).with_name('floor_winding_receipt.json')
receipt_path.write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({k:receipt[k] for k in ['status','derivative_sha256','verified_floor_mesh_ranges','examined_floor_parts','changed_parts','changed_triangles','changed_normal_vertices','street_witness_count']}))
