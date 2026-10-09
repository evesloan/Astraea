#!/usr/bin/env python3
"""Bounded derivative: correct downward horizontal tops of semantic floor parts.
Preserves original GLB; edits only triangle order and dedicated top normals.
No Blender, Godot, imports, or geometry regeneration.
"""
import collections, hashlib, json, math, os, pathlib, struct
import numpy as np
ROOT = pathlib.Path(__file__).resolve().parents[3]
SOURCE = ROOT/'BlenderCatalogue/assets/residential_hotels/aft_houses_20261007_r001/residential-neighborhood-courts-20261007/sunset_conservatory_house/outputs/house_r002/architecture.glb'
OUTPUT = ROOT/'Game/assets/models/SUNSET_ARCHITECTURE_r002.glb'
UNITS_SOURCE = SOURCE.parents[2]/'SUNSET_83_CURRENT_APPLICATION.json'
UNITS_SHA = '8d9ef2816b0168866302c575f5995efd08c631af0426507a2bea69434e4662c7'
EXPECTED = 'afaf5c7080207a21158eca5cdff5135f318f4abe320a397e344cdccb811aa330'
NATIVE = ROOT/'BlenderCatalogue/assets/residential_hotels/aft_houses_20261007_r001/residential-neighborhood-courts-20261007/sunset_conservatory_house/outputs/house_r002'
PLAN = NATIVE/'PLAN.json'
PLAN_SHA = '253b37fe1bf886a0e6c5bc3ca6d6c94427ee19ba6dbcc5aab25029b574c4a6e4'
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
tops_before=collections.Counter(); tops_after=collections.Counter(); plan_top_triangles=0
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
        # The retained PLAN is the orientation authority, not a blanket normal flip.
        source_vertices=np.asarray(source_part['verts'],dtype='<f4')
        source_top_faces=[]
        for face in source_part['faces']:
            polygon=source_vertices[face]
            if not np.all(np.abs(polygon[:,1]-top)<1e-5):continue
            assert np.cross(polygon[1]-polygon[0],polygon[2]-polygon[0])[1]>1e-7
            source_top_faces.append(set(face)); plan_top_triangles+=len(face)-2
        for index in np.flatnonzero(topface):
            assert any(set((ids[index]-start).tolist())<=face for face in source_top_faces)
        tops_before['upward']+=int(np.sum(topface & (cross[:,1]>1e-7)))
        tops_before['downward']+=int(np.sum(topface & (cross[:,1]<-1e-7)))
        assert not np.any(topface & (np.abs(cross[:,1])<=1e-7))
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
assert all_parts==35 and len(changes)==21 and sum(len(c['triangle_indices']) for c in changes)==98
assert tops_before=={'upward':293,'downward':98} and plan_top_triangles==391
# Independently reread the patched accessors to verify every solid floor top.
for node in g['nodes']:
    extra=node.get('extras',{})
    if extra.get('category')!='floor' or not extra.get('runtime_collision'):continue
    prim=g['meshes'][node['mesh']]['primitives'][0]
    verts,_,_=accessor(prim['attributes']['POSITION'],out)
    indices,_,_=accessor(prim['indices'],out);ids=indices.reshape(-1,3)
    tri=verts[ids];cross=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0])
    for part in extra['source_part_ranges']:
        start=part['vertex_start'];end=start+part['vertex_count']
        top=verts[start:end,1].max();bottom=verts[start:end,1].min()
        if top-bottom<1e-5:continue
        own=np.all((ids>=start)&(ids<end),axis=1)
        topface=own & np.all(np.abs(tri[:,:,1]-top)<1e-5,axis=1)
        tops_after['upward']+=int(np.sum(topface & (cross[:,1]>1e-7)))
        tops_after['downward']+=int(np.sum(topface & (cross[:,1]<-1e-7)))
assert tops_after=={'upward':391,'downward':0}
actual={i for i,(a,b) in enumerate(zip(raw,out)) if a!=b}
assert actual<=allowed and len(raw)==len(out)
# All mesh POSITION bytes and all non-index/non-normal bytes remain identical.
# Static exact ray witnesses across all 83 exterior approaches on repaired asset.
triangles=[]
for node in g['nodes']:
    if not node.get('extras',{}).get('runtime_collision'):continue
    for prim in g['meshes'][node['mesh']]['primitives']:
        v,_,_=accessor(prim['attributes']['POSITION'],out)
        ix,_,_=accessor(prim['indices'],out);triangles.extend(v[ix.reshape(-1,3)])
t=np.asarray(triangles);a=t[:,0];e1=t[:,1]-a;e2=t[:,2]-a
cross=np.cross(e1,e2);det=e1[:,0]*e2[:,2]-e1[:,2]*e2[:,0]
assert hashlib.sha256(UNITS_SOURCE.read_bytes()).hexdigest()==UNITS_SHA
units=json.loads(UNITS_SOURCE.read_text())['units']
assert len({u['rebuild_identity'] for u in units})==83
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
assert len(witness)==83
# Write only the derivative. Receiving/units manifest changes are owned by the integrator.
if OUTPUT.exists(): assert OUTPUT.read_bytes()==out,'Refusing to replace different surviving derivative'
else:
    temporary=OUTPUT.with_suffix('.glb.tmp');temporary.write_bytes(out);os.replace(temporary,OUTPUT)
sha=hashlib.sha256(out).hexdigest();assert hashlib.sha256(OUTPUT.read_bytes()).hexdigest()==sha
assert SOURCE.read_bytes()==raw
receipt={'status':'STATIC_PASS_RUNTIME_PENDING','source_file':str(SOURCE.relative_to(ROOT)),
 'source_sha256':EXPECTED,'plan_sha256':PLAN_SHA,'native_source_file':str((NATIVE/'architecture.glb').relative_to(ROOT)),'derivative_file':str(OUTPUT.relative_to(ROOT)),'derivative_sha256':sha,
 'policy':'Only downward horizontal maxY tops of solid runtime-collision floor source parts. No position/material/topology membership changes; no blanket double-sided collision.',
 'verified_floor_mesh_ranges':verified_ranges,'examined_floor_parts':all_parts,
 'changed_parts':len(changes),'changed_triangles':sum(len(c['triangle_indices']) for c in changes),
 'changed_normal_vertices':sum(len(c['normal_vertex_indices']) for c in changes),
 'units_source_file':str(UNITS_SOURCE.relative_to(ROOT)),'units_source_sha256':UNITS_SHA,
 'floor_top_triangles_before':dict(tops_before),'floor_top_triangles_after':dict(tops_after),
 'verified_upward_plan_top_triangles':plan_top_triangles,
 'changed_byte_count':len(actual),'changes':changes,'street_witness_count':len(witness),'street_witnesses':witness,
 'remaining_scope':'Runtime engine validation required. Sloped faces, flat sheets, walls and roofs excluded.'}
receipt_path=pathlib.Path(__file__).with_name('floor_winding_receipt.json')
receipt_path.write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({k:receipt[k] for k in ['status','derivative_sha256','verified_floor_mesh_ranges','examined_floor_parts','changed_parts','changed_triangles','changed_normal_vertices','street_witness_count']}))
