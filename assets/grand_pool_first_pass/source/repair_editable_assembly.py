"""Repair cached-world-transform loss in the surviving source, without regeneration.
Original asset families and the initial failed assembly are opened read-only.
A corrected source is saved separately; raw mesh/UV/material identities are pinned.
"""
import bpy, hashlib, json, re
from pathlib import Path
from mathutils import Matrix
HERE=Path(__file__).resolve().parents[1];ROOT=HERE.parents[1]
c=json.loads((HERE/'source/placement_contract.json').read_text())
old=HERE/'source/grand_pool_first_pass_editable.blend'
out=HERE/'source/grand_pool_first_pass_editable_corrected.blend'
assert old.exists() and not out.exists(), 'Preserve surviving sources; never overwrite a corrected source'
old_hash=hashlib.sha256(old.read_bytes()).hexdigest()

def digest(data):return hashlib.sha256(json.dumps(data,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def mesh_digest(ob):
 if ob.type!='MESH':return None
 me=ob.data
 return digest(dict(vertices=[list(v.co) for v in me.vertices],polygons=[list(p.vertices) for p in me.polygons],material_indices=[p.material_index for p in me.polygons],uvs={uv.name:[list(x.uv) for x in uv.data] for uv in me.uv_layers}))
def materials(ob):
 return [re.sub(r'\.\d{3}$','',m.name) if m else None for m in ob.data.materials] if ob.type=='MESH' else []
def evaluated(ob,dg):
 if ob.type!='MESH':return None
 eo=ob.evaluated_get(dg);me=eo.to_mesh();result=dict(vertices=[list(eo.matrix_world@v.co) for v in me.vertices],polygons=[list(p.vertices) for p in me.polygons]);eo.to_mesh_clear();return result
# Read original files in their real scene, then evaluate dependency graph before
# recording world matrices. Unlinked library objects have stale identity caches.
original={}
for key,a in c['input_inventory'].items():
 for field,h in [('path','sha256'),('editable_source','editable_source_sha256')]:
  assert hashlib.sha256((ROOT/a[field]).read_bytes()).hexdigest()==a[h],a[field]
 bpy.ops.wm.open_mainfile(filepath=str(ROOT/a['editable_source']));bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
 original[key]={ob.name:dict(type=ob.type,matrix=[list(row) for row in ob.matrix_world],mesh_sha256=mesh_digest(ob),materials=materials(ob),evaluated=evaluated(ob,dg)) for ob in bpy.context.scene.objects if ob.type in {'MESH','EMPTY'}}
bpy.ops.wm.open_mainfile(filepath=str(old));bpy.context.view_layer.update();before={};records=[];mapping={}
for it in c['placements']:
 coll=bpy.data.collections[it['name']];source=original[it['asset']];matched=set()
 assert len(coll.objects)==len(source),(it['name'],len(coll.objects),len(source))
 for ob in coll.objects:
  name=ob.name.split('__',1)[1];row=source.get(name)
  # Existing Blender names may have been truncated, but a raw mesh fingerprint
  # and original name prefix must identify exactly one original object.
  if row is None:
   candidates=[(n,v) for n,v in source.items() if n.startswith(re.sub(r'\.\d{3}$','',name)) and v['type']==ob.type and v['mesh_sha256']==mesh_digest(ob)]
   assert len(candidates)==1,(it['name'],name,'ambiguous source identity',len(candidates));name,row=candidates[0]
  assert name not in matched and ob.type==row['type'];matched.add(name)
  assert mesh_digest(ob)==row['mesh_sha256'],(it['name'],name,'mesh or UV changed')
  assert materials(ob)==row['materials'],(it['name'],name,'material roles changed')
  before[ob.name]=(mesh_digest(ob),materials(ob));mapping[ob.name]=(it,name,row)
 assert matched==set(source)
# Preserve the existing object, mesh, UV, material and modifier data; repair only
# the world transform using the original source plus the approved placement.
for obname,(it,name,row) in mapping.items():
 ob=bpy.data.objects[obname];x,y,z=it['position_xyz'];root=Matrix.Translation((x,-z,y))@Matrix.Rotation(it['yaw_radians'],4,'Z');expected=root@Matrix(row['matrix']);prior=ob.matrix_world.copy()
 error=max(abs(prior[k][j]-expected[k][j]) for k in range(4) for j in range(4))
 ob.parent=None;ob.matrix_world=expected;ob['retained_object_name']=name
 records.append(dict(item=it['name'],object=ob.name,retained_object=name,previous_matrix_max_error=error,transform_repaired=error>1e-5))
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();geometry_checks=[]
for obname,(it,name,row) in mapping.items():
 ob=bpy.data.objects[obname];assert before[obname]==(mesh_digest(ob),materials(ob))
 if ob.type!='MESH':continue
 x,y,z=it['position_xyz'];root=Matrix.Translation((x,-z,y))@Matrix.Rotation(it['yaw_radians'],4,'Z');actual=evaluated(ob,dg);source=row['evaluated']
 assert actual['polygons']==source['polygons'],(obname,'evaluated topology changed')
 assert len(actual['vertices'])==len(source['vertices'])
 from mathutils import Vector
 error=max((Vector(a)-(root@Vector(b))).length for a,b in zip(actual['vertices'],source['vertices']))
 assert error<.0002,(obname,'evaluated geometry mismatch',error)
 geometry_checks.append(dict(object=obname,evaluated_vertices=len(actual['vertices']),max_source_world_error_m=error))
assert hashlib.sha256(old.read_bytes()).hexdigest()==old_hash
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(out))
report=dict(status='corrected_source_saved_pending_independent_QA',cause='Appended object matrix_world was cached as identity before scene linkage and dependency graph evaluation. Restored from freshly evaluated original sources; no tolerance increase or placement translation.',original_failed_source=str(old.relative_to(HERE)),original_failed_sha256=old_hash,corrected_source=str(out.relative_to(HERE)),corrected_sha256=hashlib.sha256(out.read_bytes()).hexdigest(),placements=len(c['placements']),objects_checked=len(records),transforms_repaired=sum(r['transform_repaired'] for r in records),meshes_checked=len(geometry_checks),max_evaluated_source_world_error_m=max(r['max_source_world_error_m'] for r in geometry_checks),raw_geometry_uv_material_roles_preserved=True,records=records,geometry_checks=geometry_checks)
(HERE/'qa/transform_repair_report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ['records','geometry_checks']},indent=2))
