from pathlib import Path
import json,struct,hashlib,copy
import numpy as np
R=Path(__file__).resolve().parent
BASE=Path('/workspace/shared/Astraea_recovery_20261007_AXWr5x')
ORIG=BASE/'Game/assets/models/AST-CIR-005_spine_core.glb'
OUT=R/'AST-CIR-005_aft_uniforms_d03.glb'
def sha(b):return hashlib.sha256(b).hexdigest()
def read(p):
 raw=p.read_bytes();ln=struct.unpack_from('<I',raw,12)[0];off=20+ln;bn,bt=struct.unpack_from('<II',raw,off);assert bt==0x004e4942
 return raw,json.loads(raw[20:off]),raw[off+8:off+8+bn],raw[:off+8]
def acc(d,b,i):
 a=d['accessors'][i];v=d['bufferViews'][a['bufferView']];assert 'sparse'not in a and v.get('buffer',0)==0
 dt={5123:'<u2',5125:'<u4',5126:'<f4'}[a['componentType']];nc={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']];size=np.dtype(dt).itemsize
 return np.ndarray((a['count'],nc),dtype=dt,buffer=b,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',nc*size),size)).copy()
raw,d,b,header=read(ORIG);original=copy.deepcopy(d);buf=bytearray(b);original_hash=sha(raw)
assert original_hash=='986fab07bb209f7d6d734b7c7d8ecde8fd9b26a53c07e21056da5b3671e0def2'
def add_array(a,typ,component):
 while len(buf)%4:buf.append(0)
 v=len(d['bufferViews']);d['bufferViews'].append({'buffer':0,'byteOffset':len(buf),'byteLength':a.nbytes});buf.extend(a.tobytes())
 entry={'bufferView':v,'componentType':component,'count':len(a),'type':typ}
 if typ=='VEC3':entry.update(min=a.min(axis=0).tolist(),max=a.max(axis=0).tolist())
 idx=len(d['accessors']);d['accessors'].append(entry);return idx
removed=[]
for mesh_id,lo,hi in [(0,[7.72,12,-13],[7.88,16.26,20]),(2,[7.635,12.12,-13],[7.685,12.78,20])]:
 p=d['meshes'][mesh_id]['primitives'][0];v=acc(d,b,p['attributes']['POSITION']);ids=acc(d,b,p['indices']).ravel().reshape(-1,3);t=v[ids]
 mask=((t>=np.array(lo)-1e-5)&(t<=np.array(hi)+1e-5)).all(axis=(1,2));assert mask.sum()==12
 selected=t[mask];actual_lo=selected.min(axis=(0,1));actual_hi=selected.max(axis=(0,1))
 # Target must be a closed axis-aligned cuboid surface, with all eight corners.
 unique=np.unique(selected.reshape(-1,3),axis=0);assert len(unique)==8
 assert all(any(np.allclose(tr[:,ax],bound,atol=1e-6,rtol=0) for ax in range(3) for bound in [actual_lo[ax],actual_hi[ax]]) for tr in selected)
 old_indices=p['indices'];p['indices']=add_array(ids[~mask].ravel().astype('<u4').reshape(-1,1),'SCALAR',5125)
 removed.append({'mesh':mesh_id,'original_indices_accessor':old_indices,'new_indices_accessor':p['indices'],'removed_triangle_ordinals':np.flatnonzero(mask).tolist(),'actual_bounds':[actual_lo.tolist(),actual_hi.tolist()],'retained_triangle_count':int((~mask).sum()),'removed_triangle_count':12})
rr,rd,rb,rh=read(R/'doorway_replacement_pieces.glb');added=[]
for node in rd['nodes']:
 if 'mesh'not in node:continue
 assert not any(k in node for k in ['translation','rotation','scale','matrix'])
 mesh=copy.deepcopy(rd['meshes'][node['mesh']]);assert len(mesh['primitives'])==1
 p=mesh['primitives'][0];pos=acc(rd,rb,p['attributes']['POSITION']);ind=acc(rd,rb,p['indices']).ravel();assert len(ind)==36 and len(np.unique(pos,axis=0))==8
 lo=pos.min(axis=0);hi=pos.max(axis=0);tris=pos[ind].reshape(-1,3,3)
 assert all(any(np.allclose(tr[:,ax],bound,atol=1e-6,rtol=0) for ax in range(3) for bound in [lo[ax],hi[ax]]) for tr in tris)
 signed_volume=np.sum(np.einsum('ij,ij->i',tris[:,0],np.cross(tris[:,1],tris[:,2])))/6
 assert abs(abs(signed_volume)-np.prod(hi-lo))<1e-4
 for k,i in list(p['attributes'].items()):
  a=rd['accessors'][i];p['attributes'][k]=add_array(acc(rd,rb,i),a['type'],a['componentType'])
 p['indices']=add_array(ind.astype('<u4').reshape(-1,1),'SCALAR',5125)
 matname=rd['materials'][p['material']]['name'];p['material']=next(i for i,m in enumerate(d['materials']) if m['name']==matname)
 ni=copy.deepcopy(node);ni['mesh']=len(d['meshes']);d['meshes'].append(mesh);idx=len(d['nodes']);d['nodes'].append(ni);d['scenes'][d.get('scene',0)]['nodes'].append(idx)
 added.append({'name':node['name'],'material':matname,'bounds':[lo.tolist(),hi.tolist()],'volume':float(abs(signed_volume))})
assert len(added)==5
# Exact axis-aligned volume partition proof: every cell induced by old/new box planes
# must equal old solid minus the sole portal void; this is independent of triangulation.
cell_counts=[]
for rem in removed:
 lo,hi=np.array(rem['actual_bounds']);mat='ivory_enamel'if rem['mesh']==0 else'warm_walnut';boxes=[np.array(q['bounds']) for q in added if q['material']==mat]
 assert all((bb[0]>=lo).all() and (bb[1]<=hi).all() for bb in boxes)
 planes=[sorted(set([lo[a],hi[a]]+[float(bb[z,a]) for bb in boxes for z in [0,1]])) for a in range(3)]
 cells=0
 for x0,x1 in zip(planes[0][:-1],planes[0][1:]):
  for y0,y1 in zip(planes[1][:-1],planes[1][1:]):
   for z0,z1 in zip(planes[2][:-1],planes[2][1:]):
    q=np.array([(x0+x1)/2,(y0+y1)/2,(z0+z1)/2]);inside=sum(bool(((q>bb[0])&(q<bb[1])).all()) for bb in boxes)
    void=(-2<q[2]<2 and 12<=q[1]<float(np.float32(14.65)))
    assert inside==(0 if void else 1);cells+=1
 cell_counts.append(cells)
while len(buf)%4:buf.append(0)
d['buffers'][0]['byteLength']=len(buf)
j=json.dumps(d,separators=(',',':')).encode();j+=b' '*((-len(j))%4)
out=struct.pack('<III',0x46546c67,2,12+8+len(j)+8+len(buf))+struct.pack('<II',len(j),0x4e4f534a)+j+struct.pack('<II',len(buf),0x004e4942)+buf
OUT.write_bytes(out)
(R/'inverse_original_header.bin').write_bytes(header)
# Reparse successor independently and verify inverse and unchanged primitives/accessors.
sraw,sd,sb,_=read(OUT);assert sb[:len(b)]==b
assert sha(header+sb[:len(b)])==original_hash
for m in range(len(original['meshes'])):
 op=original['meshes'][m]['primitives'][0];sp=sd['meshes'][m]['primitives'][0]
 for k,idx in op['attributes'].items():assert np.array_equal(acc(original,b,idx),acc(sd,sb,sp['attributes'][k]))
 oi=acc(original,b,op['indices']).ravel().reshape(-1,3);si=acc(sd,sb,sp['indices']).ravel().reshape(-1,3)
 target=next((r for r in removed if r['mesh']==m),None)
 if target:oi=np.delete(oi,target['removed_triangle_ordinals'],axis=0)
 assert np.array_equal(oi,si)
for key in ['materials','images','textures','samplers']:assert sd.get(key)==original.get(key)
assert sd['nodes'][:len(original['nodes'])]==original['nodes']
report={'status':'Isolated source/runtime candidate; engine and graphical acceptance pending','original_glb_path':str(ORIG),'original_glb_sha256':original_hash,'successor_glb_sha256':sha(out),'original_binary_length':len(b),'original_binary_prefix_unchanged':True,'inverse_hash_verified':True,'original_materials_images_textures_samplers_and_nodes_unchanged':True,'all_original_vertex_attributes_unchanged':True,'retained_index_sequences_exact':True,'removed':removed,'added':added,'solid_partition_cell_counts':cell_counts,'outside_aperture_volume_unchanged':True,'aperture_local_xyz':[[7.635,12,-2],[7.88,float(np.float32(14.65)),2]],'world_origin':[0,0,432],'clear_width':4,'clear_height_actual':float(np.float32(14.65))-12,'runtime_triangle_change':{'removed':24,'added':60,'net':36},'integration_gates':['No live adoption performed','Only AFT_PUBLIC_CORE enclosure_file may select this derivative','Require compiled floor and 0.2x4 supported bridge','No whole-batch contact deletion','Engine import, exact mesh-contact parity, player/cart sweeps and visual review outstanding']}
(R/'RUNTIME_PROOF.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
