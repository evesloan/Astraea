from pathlib import Path
import json,hashlib,shutil,struct
import numpy as np
R=Path(__file__).resolve().parent;P=R.parent;S=P/'closed_interface002';G=Path('/workspace/shared/Astraea_recovery_20261007_AXWr5x/Game');C=R/'candidate/Game';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda p:json.loads(p.read_text());dump=lambda p,x:p.write_text(json.dumps(x,indent=2)+'\n')
assert not C.exists(),'Keep each predecessor; use a new successor if rebuilding'
manifest=load(S/'PROPOSED_GAME_APPLY_MANIFEST.json')
for row in manifest['changes']:
 src=Path(row['candidate_file']);assert sha(src)==row['after_sha256']
 if row['before_sha256']:assert sha(G/row['path'])==row['before_sha256']
 else:assert not (G/row['path']).exists()
 dst=C/row['path'];dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
base=C/'data/architecture/packages/botanical_court';ret=base/'retained';guard_path='tests/medical_triage_successor_guard.gd';orig=(G/guard_path).read_text();shutil.copy2(G/guard_path,ret/'medical_triage_successor_guard.gd')
# Preserve this exact current consumer, including the applied pool/medical composition.
patches=[]
def edit(before,after):
 global orig
 assert orig.count(before)==1,(before,orig.count(before));patches.append({'before':before,'after':after,'count':1});orig=orig.replace(before,after)
edit('if relative != POOL_FINISH_HELPER: return FileAccess.get_file_as_string("res://"+relative)','if relative != POOL_FINISH_HELPER: return _botanical_current_text(relative)')
edit('\treturn FileAccess.get_sha256("res://"+relative)\nstatic func _ensure()', '\t_botanical_ensure()\n\tif relative in botanical_proof.projected_paths: return _botanical_current_text(relative).sha256_text()\n\treturn FileAccess.get_sha256("res://"+relative)\nstatic func _ensure()')
edit('static func _ensure() -> void:\n\tif checked: return','static func _ensure() -> void:\n\tif checked: return\n\t_botanical_ensure()')
edit('var restored := FileAccess.get_file_as_string("res://"+str(path))','var restored := _botanical_current_text("res://"+str(path))')
for p in ['data/spatial_layout.json','data/generated/structural_meshes.json','docs/LAYOUT_COMPILE_CHECKS.json']:
 edit('FileAccess.get_file_as_string("res://'+p+'")','_botanical_current_text("res://'+p+'")')
edit('return checked and value==current_compiled','return checked and (value==current_compiled or value==botanical_current_compiled)')
edit('\tif value!=current_compiled and value!=old_compiled:', '\tif value==botanical_current_compiled: value=current_compiled\n\tif value!=current_compiled and value!=old_compiled:')
edit('\tif floors.get_child_count()!=current_compiled.regions.size():','\tvar actual_owners: Array=_botanical_floor_children(floors)\n\tif actual_owners.size()!=current_compiled.regions.size():')
edit('\tfor owner in floors.get_children():','\tfor owner in actual_owners:')
# Decode export vertices/indices through full transforms; deduplicate identical points only.
name='AST-ATR-001_botanical_receiving_closed002.glb';b=(S/name).read_bytes();n=struct.unpack_from('<I',b,12)[0];d=json.loads(b[20:20+n]);blob=b[28+n:]
def accessor(i):
 a=d['accessors'][i];v=d['bufferViews'][a['bufferView']];dtype={5126:'<f4',5125:'<u4',5123:'<u2',5121:'u1'}[a['componentType']];size={'VEC3':3,'SCALAR':1}[a['type']];dt=np.dtype(dtype);return np.ndarray((a['count'],size),dtype=dtype,buffer=blob,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',size*dt.itemsize),dt.itemsize))
def local(o):
 if 'matrix' in o:return np.array(o['matrix']).reshape(4,4).T
 x,y,z,w=o.get('rotation',[0,0,0,1]);m=np.eye(4);m[:3,:3]=np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])@np.diag(o.get('scale',[1,1,1]));m[:3,3]=o.get('translation',[0,0,0]);return m
parents={c:i for i,o in enumerate(d['nodes']) for c in o.get('children',[])}
def world(i):return (world(parents[i]) if i in parents else np.eye(4))@local(d['nodes'][i])
objects={}
for i,node in enumerate(d['nodes']):
 if 'mesh' not in node:continue
 vertices=[];triangles=[];keys={}
 for prim in d['meshes'][node['mesh']]['primitives']:
  vs=accessor(prim['attributes']['POSITION']).astype(float);vs=(world(i)@np.c_[vs,np.ones(len(vs))].T).T[:,:3];indices=accessor(prim['indices']).reshape(-1,3);mapping=[]
  for v in vs:
   key=tuple(float(x) for x in v)
   if key not in keys:keys[key]=len(vertices);vertices.append(list(key))
   mapping.append(keys[key])
  triangles.extend([[mapping[int(k)] for k in triangle] for triangle in indices])
 objects[node['name']]={'vertices_world':vertices,'triangles':triangles}
geometry_path=base/'BOTANICAL_GUARD_EXPORT_GEOMETRY.json';dump(geometry_path,{'source_export_sha256':sha(S/name),'objects':objects})
recovery=load(S/'EXACT_PREDECESSOR_RECOVERY.json');projected=[p['live_path'] for p in recovery['pins']];pred={x['live_path']:{'retained_path':x['retained_path'],'sha256':x['expected_predecessor_sha256']} for x in recovery['pins']};pred[guard_path]={'retained_path':str((ret/'medical_triage_successor_guard.gd').relative_to(C)),'sha256':sha(G/guard_path)}
current={row['path']:sha(C/row['path']) for row in manifest['changes']}
current[str(geometry_path.relative_to(C))]=sha(geometry_path)
for p in ['scripts/structural_floor_builder.gd','scripts/static_contact_cache.gd','tests/grand_pool_finish_successor.gd','tests/grand_pool_feature_builder_successor.gd','tests/medical_successor_guard.gd','docs/MEDICAL_TRIAGE_ADDITIVE_SUCCESSOR.json','docs/MEDICAL_ADDITIVE_SUCCESSOR.json','data/design_contract.json']:
 current[p]=sha(G/p)
block=(R/'integration_block.gd.txt').read_text();proof={'schema':1,'scope':'Exact two botanical floors and closed interim guard addition; retain complete existing pool/medical proof chain','projected_paths':projected,'current_sha256':current,'predecessors':pred,'added_owner_ids':[x['id'] for x in load(C/'data/spatial_layout.json')['regions'][-2:]],'added_layout_records':load(C/'data/spatial_layout.json')['regions'][-2:],'added_compiled_records':load(C/'data/generated/structural_meshes.json')['regions'][-2:],'compile_summary':load(C/'docs/LAYOUT_COMPILE_CHECKS.json'),'guard_root':'BotanicalCourtReceivingClosedInterim','guard_file':name,'guard_geometry_path':str(geometry_path.relative_to(C)),'consumer_inverse_edits':list(reversed(patches)),'integration_block_normalized_sha256':hashlib.sha256(block.encode()).hexdigest(),'exact_inverse_edits':{'tools/compile_layout.py':list(reversed(recovery['compiler_inverse_edits'])),'scripts/ship.gd':[recovery['ship_inverse_edit']]}}
p=base/'BOTANICAL_RUNTIME_PROOF.json';dump(p,proof);block=block.replace('<PROOF_SHA>',sha(p),1)
patched=orig+block
(C/'tests').mkdir();(C/guard_path).write_text(patched)
# Verify complete byte recovery before delivery.
restore=patched[:-len(block)]
for patch in reversed(patches):assert restore.count(patch['after'])==1;restore=restore.replace(patch['after'],patch['before'])
assert restore==(G/guard_path).read_text()
dump(R/'INTEGRATION_PATCHES.json',{'source_before_sha256':sha(G/guard_path),'source_after_sha256':sha(C/guard_path),'outside_edits':patches,'inline_section_normalized_sha256':proof['integration_block_normalized_sha256'],'proof_sha256':sha(p),'all_original_consumer_bytes_recovered':True})
# Current read-only baseline, including newer proof composition inputs.
files=[p for sub in ['scripts','tests','tools','data'] for p in (G/sub).rglob('*') if p.is_file() and '__pycache__' not in p.parts]
dump(R/'CURRENT_SOURCE_HASHES_BEFORE.json',{str(p.relative_to(G)):sha(p) for p in files})
print(json.dumps({'proof_sha256':sha(p),'integrated_guard_sha256':sha(C/guard_path),'guard_export_meshes':len(objects),'original_consumer_recovered':True,'baseline_files':len(files)}))
