"""Read-only native source views and one compact-export import smoke check."""
import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1];OLD=P.parent;delivery=json.loads((P/'docs/TERMINAL_DELIVERY_R002.json').read_text());receipts=[]
for row in delivery['assemblies']:
 native=P/row['native'];before=hashlib.sha256(native.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(native));s=bpy.context.scene;sgn=-1 if 'Fore' in row['id'] else 1;z=sgn*517.5
 # Only exact retained D11 route triangles used as adjacent context.
 regions=json.loads((OLD/'dependencies/canonical_77a745/Game/data/generated/structural_meshes.json').read_text())['regions'];r=next(r for r in regions if r['id']=='D11_'+('fore' if sgn<0 else 'aft')+'_route');v=[];faces=[]
 for t in r['triangles']:i=len(v);v.extend((q[0],-q[1],r['floor_y']) for q in t);faces.append((i,i+1,i+2))
 me=bpy.data.meshes.new('QA retained D11 route');me.from_pydata(v,[],faces);o=bpy.data.objects.new(me.name,me);s.collection.objects.link(o);m=bpy.data.materials.new('QA route grey');m.diffuse_color=(.2,.22,.24,1);me.materials.append(m)
 s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True;s.render.resolution_x=1100;s.render.resolution_y=800;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.world=bpy.data.worlds.new('QA terminal daylight');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.60,.66,.75,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.6
 sun=bpy.data.objects.new('QA diagnostic sun',bpy.data.lights.new('QA diagnostic sun','SUN'));s.collection.objects.link(sun);sun.data.energy=2;sun.rotation_euler=(.6,-.3,-.5)
 c=bpy.data.objects.new('QA camera',bpy.data.cameras.new('QA camera'));s.collection.objects.link(c);s.camera=c
 for label,eye,target,lens,kind in [('route_door',(3,71.1,z),(6.8,71.05,z),24,'Camera supported by exact retained D11 route at eye1.6m; native closed-family door, no operating controller'),('roof_receiver',(10,71.1,z),(6.8,71,z),26,'Camera supported by newly owned roof bay at eye1.6m'),('stepped_external',(90,116,sgn*570),(10,81,sgn*522),38,'External architectural diagnostic; not a supported route')]:
  c.location=(eye[0],-eye[2],eye[1]);q=Vector((target[0],-target[2],target[1]));c.rotation_euler=(q-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=lens;s.render.filepath=str(P/'qa/views'/(row['id']+'_'+label+'.png'));bpy.ops.render.render(write_still=True);receipts.append({'image':Path(s.render.filepath).relative_to(P).as_posix(),'native':row['native'],'eye_world_xyz':eye,'target_world_xyz':target,'context':kind,'diagnostic_daylight':True})
 assert before==hashlib.sha256(native.read_bytes()).hexdigest()
# Both compact architectures and four previews must import in one fresh Blender scene.
bpy.ops.wm.read_factory_settings(use_empty=True);imports=[]
for row in delivery['assemblies']:
 for f in [row['export'],*[d['preview_export'] for d in row['doors']]]:
  before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(P/f));new=set(bpy.data.objects)-before;imports.append({'path':f,'new_mesh_objects':sum(o.type=='MESH' for o in new),'new_objects':len(new)})
assert all(r['new_mesh_objects']>0 for r in imports)
(P/'qa/source_view_receipt.json').write_text(json.dumps({'views':receipts,'import_smoke_checks':imports,'native_resaved':False,'blender_only':True,'engine_run':False,'final_art_accepted':False,'scope':'Six native source views using diagnostic daylight and actual placed downlights. Exact retained D11 route shown, wider room/ship geometry absent. Both compact architectures plus four previews imported in Blender. No controller, cart or whole-engine testing.'},indent=2)+'\n');print('TERMINAL_SOURCE_VIEWS',len(receipts),'IMPORTS',len(imports))
