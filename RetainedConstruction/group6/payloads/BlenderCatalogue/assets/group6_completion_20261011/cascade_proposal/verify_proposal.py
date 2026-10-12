"""Fresh native/repeat export, original shoulder supports and shared-stream fit."""
import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path(__file__).resolve().parent;R=P.parents[3];p=json.loads((P/'CONTRACT.json').read_text())
code=(P.parent/'author_completion.py').read_text();exec(code[code.index('def digest(o):'):code.index('before={')])
bpy.ops.wm.open_mainfile(filepath=str(R/p['native']));S=bpy.context.scene
for group in ['source_context_mesh_hashes','registered_reference_mesh_hashes','new_mesh_hashes']:
 for n,h in p[group].items():assert digest(bpy.data.objects[n])==h,n
for n,h in p['packed_context_images'].items():assert hashlib.sha256(bpy.data.images[n].packed_file.data).hexdigest()==h,n
def world(o):return [o.matrix_world@v.co for v in o.data.vertices]
def bounds(o):
 pts=world(o);return [[min(v[i] for v in pts),max(v[i] for v in pts)] for i in range(3)]
old={n:bounds(bpy.data.objects[n]) for n in p['source_context_mesh_hashes'] if not bpy.data.objects[n].get('group6_exchange_excluded') and bpy.data.objects[n].get('kind') not in ['water_visual','tube_static_visual','fixture_lens','plant_static','compiler_floor_proposal','runtime_service_gate_reference']}
pairs=0
for n in p['new_mesh_hashes']:
 o=bpy.data.objects[n];b=bounds(o)
 for name,a in old.items():
  pairs+=1;assert not all(min(a[i][1],b[i][1])-max(a[i][0],b[i][0])>.003 for i in range(3)),(n,'overlaps original',name)
shoulder=bpy.data.objects['AQD__cascade_maintenance_shoulder'];tree=BVHTree.FromPolygons(world(shoulder),[list(f.vertices) for f in shoulder.data.polygons]);foot=bpy.data.objects['G6_CASCADE__cabinet_foot'];low=min(v.z for v in world(foot));support=[]
for v in world(foot):
 if abs(v.z-low)>.0001:continue
 hit=tree.ray_cast(v+Vector((0,0,.02)),Vector((0,0,-1)),.04);ok=hit[0] is not None and abs(hit[0].z-low)<.001;support.append({'xyz':[v.x,v.z,-v.y],'supported':ok});assert ok
hood=bpy.data.objects['AQD__cascade_acoustic_hood'];tree=BVHTree.FromPolygons(world(hood),[list(f.vertices) for f in hood.data.polygons]);hit=tree.ray_cast(Vector((21.9,-215.1,46.529)),Vector((0,0,1)),.015);assert hit[0] is not None and abs(hit[0].z-46.53)<.001
bpy.ops.object.select_all(action='DESELECT')
for n in p['new_mesh_hashes']:bpy.data.objects[n].select_set(True)
repeat=Path('/workspace/group6-repeat-export/Group6CascadeInterfaceProposal_r002.glb');bpy.ops.export_scene.gltf(filepath=str(repeat),export_format='GLB',use_selection=True,export_extras=True,export_cameras=False,export_lights=False,export_materials='EXPORT');assert hashlib.sha256(repeat.read_bytes()).hexdigest()==p['export_sha256']
result={'status':'PASS','source_context_meshes_preserved':len(p['source_context_mesh_hashes']),'registered_cascade_reference_meshes_preserved':len(p['registered_reference_mesh_hashes']),'packed_context_images_preserved':len(p['packed_context_images']),'new_meshes_verified':len(p['new_mesh_hashes']),'original_solid_pairs_checked':pairs,'actual_original_shoulder_foot_points':support,'actual_original_hood_mount_contact':True,'fresh_repeat_export_identical':True,'export_sha256':p['export_sha256'],'scope':'Inactive local-console source fit only. Existing Group6 shoulder/hood and registered receiver/spine context preserved. Original-player access, mechanical controls, onward branch clearance/connection and shared-owner adoption separate.'}
(P/'SAVED_NATIVE_VERIFICATION.json').write_text(json.dumps(result,indent=2)+'\n');print('CASCADE PROPOSAL SAVED NATIVE PASS')
