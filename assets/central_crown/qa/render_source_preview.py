"""Source diagnostic views only. Floors and shared moving doors are temporary review context."""
from pathlib import Path
import bpy,json,math,hashlib,datetime
from mathutils import Vector
R=Path(__file__).resolve().parents[1];C=R.parents[1];D=json.loads((R/'source/section_contract.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(R/'source/AST-CMD-001.blend'))
m=bpy.data.materials.new('QA_ONLY_existing_floor');m.diffuse_color=(.21,.25,.25,1);m.use_nodes=True;m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.21,.25,.25,1);m.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.9
G=C.parent/'astraea-godot-production-20261003'
for region in json.loads((G/'data/generated/structural_meshes.json').read_text())['regions']:
 if region['id']not in['D18_fore_apron','D18_aft_apron','D18_atrium_structural_cap','D18_starboard_house_cover']:continue
 verts=[];faces=[]
 for tri in region['triangles']:
  base=len(verts);verts.extend((x,-z,region['floor_y'])for x,z in tri);faces.append(tuple(range(base,base+3)))
 me=bpy.data.meshes.new('QA_ONLY_'+region['id']);me.from_pydata(verts,[],faces);me.materials.append(m);o=bpy.data.objects.new(me.name,me);bpy.context.collection.objects.link(o)
# Shared doors imported for review only, never saved/exported as crown geometry.
for door in D['doors']:
 before=set(bpy.context.scene.objects);bpy.ops.import_scene.gltf(filepath=str(C/'assets/staff_threshold/exports/AST-STF-008.glb'));new=set(bpy.context.scene.objects)-before;root=bpy.data.objects.new('QA_ONLY_door_'+door['name'],None);bpy.context.collection.objects.link(root)
 for o in new:
  if o.parent not in new:o.parent=root
 x,y,z=door['position'];root.location=(x,-z,y);root.rotation_euler.z=door['yaw']
for mark in D['light_markers']:
 x,y,z=mark['position'];data=bpy.data.lights.new(mark['name'],'AREA');data.energy=250;data.color=(1,.84,.68)if mark.get('programme_key')=='D18_directory_05'else(.78,.88,1);data.shape='DISK';data.size=1.2;obj=bpy.data.objects.new(mark['name']+'_QA_LIGHT',data);bpy.context.collection.objects.link(obj);obj.location=(x,-z,y-.01)
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=False;scene.render.threads_mode='FIXED';scene.render.threads=2;scene.render.resolution_x=720;scene.render.resolution_y=450;scene.render.resolution_percentage=100;scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.18,.22,.28,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.4;scene.view_settings.view_transform='AgX'
def render(name,pos,target,lens=25):
 cam=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,cam);bpy.context.collection.objects.link(o);o.location=(pos[0],-pos[2],pos[1]);t=Vector((target[0],-target[2],target[1]));o.rotation_euler=(t-o.location).to_track_quat('-Z','Y').to_euler();cam.lens=lens;cam.clip_end=1200;scene.camera=o;scene.render.filepath=str(R/'qa'/name);bpy.ops.render.render(write_still=True)
render('source_navigation_window.png',(19,108.2,-59),(35.2,109.1,-44),23)
render('source_screened_threshold.png',(7.4,108.2,-60),(10,108.1,-51.8),24)
render('source_north_public_belt.png',(-40,108.2,-77),(35,108.4,-75.5),24)
render('source_public_gallery.png',(1.6,108.2,-75),(0,108.8,-25),24)
# Fitted frame external diagnostic. World illumination is only a preview setting.
scene.world.node_tree.nodes['Background'].inputs[1].default_value=.75
render('source_roof_and_spines.png',(114,150,162),(0,57,0),34)

(R/'qa/source_preview_receipt.json').write_text(json.dumps({'source_sha256':hashlib.sha256((R/'source/AST-CMD-001.blend').read_bytes()).hexdigest(),'captured_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'engine':'Cycles CPU','threads':2,'samples':32,'denoised':False,'purpose':'Source-only construction diagnostics; temporary floor and shared doors excluded from export','images':['source_navigation_window.png','source_screened_threshold.png','source_north_public_belt.png','source_public_gallery.png','source_roof_and_spines.png']},indent=2)+'\n')
