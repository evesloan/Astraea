from pathlib import Path
import bpy,json
from mathutils import Vector
root=Path(__file__).resolve().parents[1];(root/'qa').mkdir(exist_ok=True);records=[]
def bounds():
 deps=bpy.context.evaluated_depsgraph_get();v=[];tri=0
 for o in bpy.context.scene.objects:
  if o.type!='MESH':continue
  obj=o.evaluated_get(deps);m=obj.to_mesh();m.calc_loop_triangles();tri+=len(m.loop_triangles);v.extend(o.matrix_world@p.co for p in m.vertices);obj.to_mesh_clear()
 return {'min':[min(p[i]for p in v)for i in range(3)],'max':[max(p[i]for p in v)for i in range(3)],'triangles':tri}
for aid in ['AST-SLP-001','AST-SLP-002']:
 bpy.ops.wm.open_mainfile(filepath=str(root/'source'/(aid+'.blend')));before=bounds();assert abs(before['min'][2])<.001
 assert all(o.data.uv_layers for o in bpy.context.scene.objects if o.type=='MESH')
 names={o.name for o in bpy.context.scene.objects};assert 'DATUM_foot_approach' in names
 # Component-only original asset render; never evidence of a built guest room.
 s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=16;s.cycles.use_denoising=False;s.cycles.device='CPU';s.render.resolution_x=512;s.render.resolution_y=512;s.render.resolution_percentage=100
 s.world=bpy.data.worlds.new('InspectionWorld');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.38,.42,.48,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.35
 bpy.ops.object.camera_add(location=(3,-4,2.8));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,.6))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=4.0;s.camera=cam
 for loc,power,size in [((-3,-2,5),500,4),((3,1,4),250,3)]:
  bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((0,0,.5))-o.location).to_track_quat('-Z','Y').to_euler()
 s.render.filepath=str(root/'qa'/(aid+'_component.png'));bpy.ops.render.render(write_still=True)
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.ops.import_scene.gltf(filepath=str(root/'exports'/(aid+'.glb')));after=bounds()
 for key in ['min','max']:assert max(abs(a-b)for a,b in zip(before[key],after[key]))<.002,(aid,key,before,after)
 records.append({'id':aid,'source':before,'export':after,'roundtrip_bounds_match':True,'metric_uv_present':True,'floor_contact':True,'scope':'Geometry/material component QA; no fitted room, actor sleeping, species or final-art acceptance'})
(root/'qa/validation.json').write_text(json.dumps(records,indent=2)+'\n');print('GUEST_REST_ROUNDTRIP_PASS',records)
