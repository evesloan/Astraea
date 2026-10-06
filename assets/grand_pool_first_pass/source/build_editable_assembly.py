"""Parent-scheduled Blender source assembly. Correct linkage before world-matrix capture.
Appends original editable retained objects; produces only NEW package outputs.
No original library mutation, registry entry, floor duplication or gameplay.
"""
import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Matrix
HERE=Path(__file__).resolve().parents[1];ROOT=HERE.parents[1]
c=json.loads((HERE/'source/placement_contract.json').read_text())
assert not c['issues'],'Fail closed: unresolved envelope/floor issues'
for a in c['input_inventory'].values():
 for key,h in [('path','sha256'),('editable_source','editable_source_sha256')]:
  assert hashlib.sha256((ROOT/a[key]).read_bytes()).hexdigest()==a[h],a[key]
# Fresh empty NEW scene only. Parent must schedule process, retention and adoption separately.
bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
for it in c['placements']:
 asset=c['input_inventory'][it['asset']];source=ROOT/asset['editable_source']
 with bpy.data.libraries.load(str(source),link=False) as (src,dst):dst.objects=src.objects
 coll=bpy.data.collections.new(it['name']);scene.collection.children.link(coll)
 x,y,z=it['position_xyz'];root=Matrix.Translation((x,-z,y))@Matrix.Rotation(it['yaw_radians'],4,'Z')
 appended=[]
 # Link the full retained hierarchy first. Unlinked matrix_world is a stale
 # cache and was identity for transformed parts in the interrupted assembly.
 for ob in dst.objects:
  if ob is not None and ob.type in {'MESH','EMPTY'}:coll.objects.link(ob)
 bpy.context.view_layer.update()
 frozen_world={ob:ob.matrix_world.copy() for ob in dst.objects if ob is not None}
 for ob in dst.objects:
  if ob is None:continue
  if ob.type not in {'MESH','EMPTY'}:continue
  old=frozen_world[ob];ob['retained_object_name']=ob.name;ob.parent=None;ob.matrix_world=root@old
  ob.name=it['name']+'__'+ob.name;ob['retained_source']=asset['editable_source'];ob['retained_source_sha256']=asset['editable_source_sha256'];ob['programme_scope']=str(c['programme_ids']);ob['placement_support']=it['support'];ob['collision_contract']='visual_only_pending_parent_compound_contacts'
  appended.append(ob)
 # Appended editable mesh families retain their existing material and texture roles.
 # No compiler floor solids, proxy crowds, lamps, water or runtime controllers are created.
assert all(o.type in {'MESH','EMPTY'} for o in scene.objects)
bpy.ops.file.pack_all()
out=HERE/'source/grand_pool_first_pass_editable.blend';assert not out.exists(),'Do not overwrite a surviving assembly source'
bpy.ops.wm.save_as_mainfile(filepath=str(out))
# Export is deliberately a separate allocation gate after parent source review.
print('Saved NEW editable source only:',out)
