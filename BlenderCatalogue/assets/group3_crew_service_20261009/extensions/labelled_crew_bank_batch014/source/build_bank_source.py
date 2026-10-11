"""Immutable original component payloads, rigidly assembled in sixteen exact atlas envelopes."""
from pathlib import Path
import json,hashlib,math,bpy,sys
from mathutils import Vector,Matrix
HERE=Path(__file__).resolve().parents[1];ROOT=HERE.parents[4]
spec=json.load(open(HERE/'source/LABELLED_BANK_CONTRACT.json'));template=json.load(open(ROOT/spec['template_spec_path']))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
catalogue=json.load(open(ROOT/'BlenderCatalogue/catalogue_manifest.json'))
assert not any(q['catalogue_id']=='AST-CRW-G3-002'for q in catalogue['assets'])
for f,h in spec['source_pins'].items():assert sha(ROOT/f)==h,f
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.context.preferences.filepaths.save_version=0
def gv(p):return Vector((p[0],-p[2],p[1]))
def matrix(position,yaw):return Matrix.Translation(gv(position))@Matrix.Rotation(yaw,4,'Z')
paths={'Shell':ROOT/spec['native_shell_path']}
for dep in template['dependencies']:paths[Path(dep['path']).stem]=ROOT/dep['path']
prototypes={}
for name,path in paths.items():
 before=set(bpy.context.scene.objects);bpy.ops.import_scene.gltf(filepath=str(path));objects=sorted(set(bpy.context.scene.objects)-before,key=lambda o:o.name)
 prototypes[name]=objects
 for o in objects:o.hide_render=True;o.name='PROTOTYPE_'+name+'_'+o.name
created=[];bindings=[]
def copy_component(component,pose,prefix):
 original=prototypes[component];copies={o:o.copy()for o in original}
 for old,new in copies.items():
  bpy.context.collection.objects.link(new);new.name=prefix+'__'+old.name.split('PROTOTYPE_'+component+'_',1)[1]
  new.hide_render=False;new.parent=copies.get(old.parent)
  # Keep descendant transforms local. Applying a world pose to every child while
  # assigning its copied parent can apply that parent pose twice in the export.
  new.matrix_parent_inverse=old.matrix_parent_inverse.copy()
  new.matrix_basis=old.matrix_basis.copy()
  if old.parent not in copies:new.matrix_world=pose@old.matrix_world
  new['reference_room_id']=prefix.split('__')[0];new['original_component']=component;new['construction_wip']=True
  created.append(new)
  if old.type=='MESH':
   assert new.data==old.data
   bindings.append(dict(instance=new.name,original_component=component,shared_original_mesh_data=True,
    local_vertices=len(old.data.vertices),local_polygons=len(old.data.polygons),uv_layers=len(old.data.uv_layers),rigid_transform_only=True))
for home in spec['instances']:
 rid=home['reference_room_id'];room=matrix(home['position'],home['yaw'])
 copy_component('Shell',room,rid+'__Shell')
 for bed in template['beds']:
  prefix=rid+'__Rest'+bed['local_place'];pos=bed['position'];yaw=bed['yaw']
  copy_component('AST-CRW-001',room@matrix(pos,yaw),prefix+'__Frame')
  copy_component('AST-CRW-002',room@matrix(bed['curtain_position'],bed['curtain_yaw']),prefix+'__Curtain')
  t=[-.26,.88,-2.14];c=math.cos(yaw);s=math.sin(yaw)
  mounted=[pos[0]+c*t[0]+s*t[2],pos[1]+t[1],pos[2]-s*t[0]+c*t[2]]
  copy_component('AST-CRW-004',room@matrix(mounted,yaw),prefix+'__Reading')
 for i,storage in enumerate(template['storage']):copy_component('AST-CRW-003',room@matrix(storage['position'],storage['yaw']),rid+'__Storage'+str(i))
for objects in prototypes.values():
 for o in objects:bpy.data.objects.remove(o,do_unlink=True)
bpy.context.scene['catalogue_id']='AST-CRW-G3-002';bpy.context.scene['registered_berth_keys_created']=0
bpy.context.scene['physical_unassigned_rest_surfaces']=32;bpy.context.scene['C036_migration_applied']=False
native=HERE/'source/AST-CRW-G3-002.blend';export=HERE/'exports/AST-CRW-G3-002.glb'
bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True)
bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',export_extras=True,export_yup=True,export_lights=False,export_cameras=False)
report=dict(status='PASS_RIGID_NATIVE_ASSEMBLY',native_sha256=sha(native),export_sha256=sha(export),
 labelled_rooms=16,physical_unassigned_rest_surfaces=32,registered_berths_added=0,mesh_bindings=len(bindings),
 every_component_local_mesh_and_UV_material_payload_unchanged=True,bindings=bindings,
 scope='Exact labelled physical source assembly. No restored berth/save identity, demographic/species assignment or complete 400-berth acceptance.')
(HERE/'qa/NATIVE_ASSEMBLY.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:report[k]for k in ['status','labelled_rooms','physical_unassigned_rest_surfaces','mesh_bindings','export_sha256']}))
