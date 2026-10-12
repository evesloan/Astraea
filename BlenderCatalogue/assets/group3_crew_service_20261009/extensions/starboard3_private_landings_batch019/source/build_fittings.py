"""Unscaled original gate/cabin payloads in complete port2 source poses; no save keys."""
from pathlib import Path
import bpy,json,hashlib,math
from mathutils import Vector,Matrix
HERE=Path(__file__).resolve().parents[1];ROOT=HERE.parents[4]
p=json.load(open(HERE/'source/PRIVATE_LANDING_CONTRACT.json'))
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
for f,h in p['source_pins'].items():assert sha(ROOT/f)==h,f
asset='AST-STF-G3-046';catalogue=json.load(open(ROOT/'BlenderCatalogue/catalogue_manifest.json'))
assert not any(q['catalogue_id']==asset for q in catalogue['assets'])
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.context.preferences.filepaths.save_version=0
def pose(at,yaw):return Matrix.Translation(Vector((at[0],-at[2],at[1])))@Matrix.Rotation(yaw,4,'Z')
prototypes={}
for name,file in [('Service','AST-STF-008.glb'),('Gate','AST-DOR-003.glb'),('Cabin','AST-CIR-003_seventeen_stop.glb')]:
 before=set(bpy.context.scene.objects);bpy.ops.import_scene.gltf(filepath=str(ROOT/'Game/assets/models'/file));objects=sorted(set(bpy.context.scene.objects)-before,key=lambda o:o.name)
 for o in objects:o.name='PROTOTYPE_'+name+'_'+o.name
 prototypes[name]=objects
bindings=[];placements=[]
def instance(kind,name,at,yaw):
 originals=prototypes[kind];copies={o:o.copy()for o in originals};m=pose(at,yaw)
 for old,new in copies.items():
  bpy.context.collection.objects.link(new);new.name=name+'__'+old.name.split('PROTOTYPE_'+kind+'_',1)[1]
  new.parent=copies.get(old.parent);new.matrix_parent_inverse=old.matrix_parent_inverse.copy();new.matrix_basis=old.matrix_basis.copy()
  if old.parent not in copies:new.matrix_world=m@old.matrix_world
  new['source_fitting_role']=name;new['original_component']=kind;new['persistent_identity_assigned']=False
  if old.type=='MESH':
   assert new.data==old.data;bindings.append(dict(instance=new.name,component=kind,original_mesh_data_shared=True,
    vertices=len(old.data.vertices),polygons=len(old.data.polygons),UV_material_payload_unchanged=True,unscaled=True))
 placements.append(dict(name=name,component=kind,position=at,yaw=yaw,persistent_id=None))
for q in p['door_bindings']:instance('Service',q['name'],q['position'],q['yaw'])
for deck,y in zip(p['controller_binding']['stop_ids'],p['controller_binding']['floor_heights']):instance('Gate','Landing_'+deck,[23.08,y,-86],math.pi/2)
instance('Cabin','SourceCabinAtD03',[23.2,12,-86],-math.pi/2)
instance('Gate','SourceCabinGateAtD03',[23.32,12,-86],math.pi/2)
for group in prototypes.values():
 for o in group:bpy.data.objects.remove(o,do_unlink=True)
bpy.context.scene['catalogue_id']=asset;bpy.context.scene['persistent_keys_created']=0;bpy.context.scene['source_only_unbound_operating_fittings']=True
native=HERE/'source'/f'{asset}.blend';export=HERE/'exports'/f'{asset}.glb'
bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True)
bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',export_extras=True,export_yup=True,export_lights=False,export_cameras=False)
q=dict(status='PASS_RIGID_ORIGINAL_FITTINGS',source_sha256=sha(native),export_sha256=sha(export),mesh_bindings=len(bindings),placements=placements,
 original_vertices_UV_materials_and_scale_preserved=True,persistent_keys_created=0,bindings=bindings)
(HERE/'qa/FITTINGS_NATIVE_ASSEMBLY.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:q[k]for k in ['status','mesh_bindings','export_sha256','persistent_keys_created']}))
