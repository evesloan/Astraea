"""Bounded imported-GLB captures. --preflight imports ALL cameras without rendering.
Run only after cheap geometry/rebuild review and lead grants serialized heavy slot.
A copy of this exact script is frozen under qa/executed_scripts at launch.
"""
import bpy,json,hashlib,sys
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
BASE=Path(__file__).resolve().parents[1];OUT=BASE/'qa/renders';OUT.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
VIEWS=[('001_front_standing','AST-RTL-001.glb',(3.3,-7.1,1.60),(0,0,1.45),43,'ordinary standing-height imported whole component'),('001_entry_reveal_standing','AST-RTL-001.glb',(-4.9,-6.5,1.60),(-.10,0,1.45),43,'ordinary standing-height imported whole component, entry-facing side recess'),('002_front_standing','AST-RTL-002.glb',(2.5,-3.6,1.60),(0,0,.53),47,'ordinary standing-height imported whole component'),('002_stepped_surfaces_high','AST-RTL-002.glb',(-2.6,-3.1,2.7),(0,0,.53),47,'high three-quarter imported surface inspection, explicitly not an ordinary-height view')]
preflight='--preflight'in sys.argv
selected={x for x in sys.argv[sys.argv.index('--')+1:]if not x.startswith('--')}if '--'in sys.argv else set()
views=VIEWS if preflight or not selected else[v for v in VIEWS if v[0]in selected]
records=[];report=BASE/'qa/review_media_manifest.json';previous=[]if preflight or not report.exists()else json.loads(report.read_text())['views'];pending=[]
# Preflight is a complete no-render pass; ordinary runs also check every requested view before any render.
for label,file,pos,look,lens,kind in views:
 bpy.ops.wm.read_factory_settings(use_empty=True);src=BASE/'exports'/file;ident=file[:11];rec=json.loads((BASE/(ident+'.manifest.json')).read_text());inputs={str(src.relative_to(BASE)):sha(src),rec['source']:sha(BASE/rec['source']),'source/build_retail_display.py':sha(BASE/'source/build_retail_display.py')};bpy.ops.import_scene.gltf(filepath=str(src));bpy.context.view_layer.update();meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];vertices=[o.matrix_world@v.co for o in meshes for v in o.data.vertices]
 camdata=bpy.data.cameras.new('QA_CAMERA');cam=bpy.data.objects.new('QA_CAMERA',camdata);bpy.context.collection.objects.link(cam);cam.location=pos;cam.rotation_euler=(Vector(look)-cam.location).to_track_quat('-Z','Y').to_euler();camdata.lens=lens;sc=bpy.context.scene;sc.camera=cam;sc.render.resolution_x=640;sc.render.resolution_y=360;sc.render.resolution_percentage=100;bpy.context.view_layer.update();projected=[world_to_camera_view(sc,cam,p)for p in vertices];lo=[min(p[i]for p in projected)for i in range(3)];hi=[max(p[i]for p in projected)for i in range(3)];okay=min(lo[:2])>.035 and max(hi[:2])<.965 and lo[2]>0
 row={'view':label,'type':kind,'inputs_sha256':inputs,'camera_source_position_m':pos,'camera_target_source_m':look,'camera_lens_mm':lens,'pixel_dimensions':[640,360],'projected_min':lo,'projected_max':hi,'entire_visual_bounds_inside_frame':okay,'scope':'Actual imported GLB with neutral QA floor/lights only; no finished shop, host/ceiling/door, stock, body or game-renderer claim.'};records.append(row)
 if not okay:raise RuntimeError('All-camera preflight failed before any rendering: '+label+' '+str((lo,hi)))
 pending.append(row)
(BASE/'qa/all_camera_preflight.json').write_text(json.dumps({'script_sha256':sha(Path(__file__)),'rendered':False,'views':records,'all_passed':all(r['entire_visual_bounds_inside_frame']for r in records)},indent=2)+'\n')
if preflight:print('ALL_CAMERA_PREFLIGHT_PASSED',len(records));raise SystemExit(0)
for row in pending:
 label=row['view'];src=BASE/next(p for p in row['inputs_sha256']if p.endswith('.glb'));bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(src))
 floor=bpy.data.materials.new('QA_neutral_floor');floor.use_nodes=True;bs=floor.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.16,.185,.195,1);bs.inputs['Roughness'].default_value=.86;bpy.ops.mesh.primitive_plane_add(size=200);bpy.context.object.name='QA_FLOOR_NOT_GAME';bpy.context.object.data.materials.append(floor)
 sc=bpy.context.scene;world=bpy.data.worlds.new('QA_neutral_world');sc.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.18,.21,.24,1);world.node_tree.nodes['Background'].inputs[1].default_value=.60
 for name,pos,power,size in[('key',(-3,-4,6),1500,5),('fill',(4,1,4),1000,4),('rim',(-2,4,5),1150,3)]:
  data=bpy.data.lights.new('QA_'+name,'AREA');data.energy=power;data.shape='DISK';data.size=size;ob=bpy.data.objects.new('QA_'+name,data);bpy.context.collection.objects.link(ob);ob.location=pos;ob.rotation_euler=(Vector((0,0,1))-ob.location).to_track_quat('-Z','Y').to_euler()
 data=bpy.data.cameras.new('QA_CAMERA');cam=bpy.data.objects.new('QA_CAMERA',data);bpy.context.collection.objects.link(cam);cam.location=row['camera_source_position_m'];cam.rotation_euler=(Vector(row['camera_target_source_m'])-cam.location).to_track_quat('-Z','Y').to_euler();data.lens=row['camera_lens_mm'];sc.camera=cam;sc.render.engine='BLENDER_EEVEE_NEXT';sc.eevee.taa_render_samples=64;sc.render.resolution_x=640;sc.render.resolution_y=360;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.view_settings.view_transform='AgX';sc.render.filepath=str(OUT/(label+'.png'));bpy.ops.render.render(write_still=True)
 row['image']='qa/renders/'+label+'.png';row['image_sha256']=sha(OUT/(label+'.png'));row['inputs_unchanged_after_capture']=all(sha(BASE/p)==h for p,h in row['inputs_sha256'].items());row['executed_script_sha256']=sha(Path(__file__));previous=[r for r in previous if r['view']!=label]+[row];report.write_text(json.dumps({'schema':'retail_display_imported_captures_v1','views':previous},indent=2)+'\n');print('CAPTURE_SAVED',label)
print('IMPORTED_CAPTURE_COMPLETE',len(pending))
