"""Eye-height QA of new natives with retained floor context and actual sources."""
import bpy,json,hashlib,math,sys
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1];D=P/'dependencies/canonical_77a745';quiet='--quiet' in sys.argv;plan=json.loads((P/'docs'/('QUIETER_GALLERY_PLACEMENT_AND_INTERFACES.json' if quiet else 'GALLERY_PLACEMENT_AND_INTERFACES.json')).read_text());floors=json.loads((D/'Game/data/generated/structural_meshes.json').read_text())['regions'];receipts=[]
for r in plan['rooms']:
 f=P/r['source'];before=hashlib.sha256(f.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(f),load_ui=False)
 row=next(q for q in floors if q['id']==r['retained_floor_owner']);ox,oy,oz=r['origin_world_xyz'];v=[];faces=[]
 # Exact pinned slab triangles as QA-only context, outside native/GLB.
 for t in row['triangles']:
  if max(q[0] for q in t)<40 or min(q[0] for q in t)>49 or max(q[1] for q in t)<-30 or min(q[1] for q in t)>-14:continue
  i=len(v);v.extend([(q[0]-ox,-(q[1]-oz),row['floor_y']-oy) for q in t]);faces.append((i,i+1,i+2))
 me=bpy.data.meshes.new('QA retained floor context');me.from_pydata(v,[],faces);o=bpy.data.objects.new(me.name,me);bpy.context.scene.collection.objects.link(o);me.materials.append(bpy.data.materials.get('G7_stone') or next(m for m in bpy.data.materials if 'stone' in m.name))
 s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=True;s.render.resolution_x=1100;s.render.resolution_y=750;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.filepath=str(P/f"qa/gallery_views/{r['deck']}_normal_eye.png")
 s.world=bpy.data.worlds.new('QA low ambient');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.50,.55,.62,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.65
 camera=bpy.data.objects.new('QA normal eye',bpy.data.cameras.new('QA normal eye'));s.collection.objects.link(camera);camera.location=(-1.4,-2.7,1.6);target=Vector((2.50,-3.0,1.05));camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.lens=21;s.camera=camera
 bpy.ops.render.render(write_still=True);assert before==hashlib.sha256(f.read_bytes()).hexdigest()
 receipts.append({'id':r['id'],'image':s.render.filepath,'eye_local_y_up_xyz':[-1.4,1.6,2.7],'native_sha256':before,'context':'Exact retained slab triangles only; eight production source lights remain in their natives, no temporary area fixtures. QA neutral ambient supplements actual sources for geometry readability; not a main-scene illumination claim. Wider retained ship absent.','source_lights':[(o.name,o.data.cutoff_distance) for o in s.objects if o.type=='LIGHT'],'production_native_resaved':False})
(P/'qa'/('quieter_gallery_source_view_receipt.json' if quiet else 'gallery_source_view_receipt.json')).write_text(json.dumps({'views':receipts,'final_art_accepted':False},indent=2)+'\n');print('GALLERY_SOURCE_VIEWS',len(receipts))
