"""Source-only construction diagnostics. Context floor and door objects are never saved/exported."""
from pathlib import Path
import bpy,json,math,hashlib,datetime
from mathutils import Vector
R=Path(__file__).resolve().parents[1];C=R.parents[1];G=C.parent/'astraea-godot-production-20261003'
D=json.loads((R/'source/section_contract.json').read_text());CD=json.loads((C/'assets/central_crown/source/section_contract.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(R/'source/AST-CMD-002.blend'))
with bpy.data.libraries.load(str(C/'assets/central_crown/source/AST-CMD-001.blend'),link=False) as (src,dst):dst.objects=src.objects
for o in dst.objects:
 if o:bpy.context.collection.objects.link(o)
mat=bpy.data.materials.new('QA_ONLY_compiled_floor');mat.use_nodes=True;mat.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.20,.24,.26,1);mat.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.9
regions=json.loads((G/'data/generated/structural_meshes.json').read_text())['regions'];context=[]
for region in regions:
 if region['deck']!='D18':continue
 if region['id']not in ['D18_aft_route','D18_aft_apron','D18_atrium_structural_cap','D18_starboard_house_cover']and'command'not in region['id']:continue
 verts=[];faces=[];top=region['floor_y'];bot=top-region['thickness']
 for tri in region['triangles']:
  n=len(verts);verts.extend((x,-z,y)for y in[bot,top]for x,z in tri);faces.extend([(n+2,n+1,n),(n+3,n+4,n+5)])
 for ring in region['rings']:
  for a,b in zip(ring,ring[1:]+ring[:1]):
   n=len(verts);verts.extend((x,-z,y)for y in[bot,top]for x,z in[a,b]);faces.append((n,n+1,n+3,n+2))
 me=bpy.data.meshes.new('QA_ONLY_'+region['id']);me.from_pydata(verts,[],faces);me.materials.append(mat);o=bpy.data.objects.new(me.name,me);bpy.context.collection.objects.link(o);context.append(region['id'])
# Planned parent-owned slab appears only if the compiled owner has not been introduced yet.
if not any('command' in name for name in context):
 for x in [-20,20]:
  bpy.ops.mesh.primitive_cube_add(size=1,location=(x,-91,106.38));o=bpy.context.object;o.name='QA_ONLY_planned_parent_floor';o.scale=(32,22,.24);o.data.materials.append(mat)
 context.append('temporary_plan_only_parent_floor')
for door in D['doors']+CD['doors']:
 before=set(bpy.context.scene.objects);bpy.ops.import_scene.gltf(filepath=str(C/'assets/staff_threshold/exports/AST-STF-008.glb'));new=set(bpy.context.scene.objects)-before;root=bpy.data.objects.new('QA_ONLY_door_'+door['name'],None);bpy.context.collection.objects.link(root)
 for o in new:
  if o.parent not in new:o.parent=root
 x,y,z=door['position'];root.location=(x,-z,y);root.rotation_euler.z=door['yaw']
for marker in D['light_markers']+CD['light_markers']:
 x,y,z=marker['position'];data=bpy.data.lights.new(marker['name']+'_QA','AREA');data.energy=270;data.color=(.78,.88,1);data.shape='DISK';data.size=1.2;o=bpy.data.objects.new(data.name,data);bpy.context.collection.objects.link(o);o.location=(x,-z,y-.01)
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=False;scene.render.threads_mode='FIXED';scene.render.threads=2;scene.render.resolution_x=840;scene.render.resolution_y=525;scene.render.resolution_percentage=100;scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.18,.22,.28,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.4;scene.view_settings.view_transform='AgX'
images=[]
def render(name,pos,target,lens=24):
 cam=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,cam);bpy.context.collection.objects.link(o);o.location=(pos[0],-pos[2],pos[1]);t=Vector((target[0],-target[2],target[1]));o.rotation_euler=(t-o.location).to_track_quat('-Z','Y').to_euler();cam.lens=lens;cam.clip_end=1600;scene.camera=o;scene.render.filepath=str(R/'qa'/name);bpy.ops.render.render(write_still=True);images.append(name)
render('source_public_cross_street.png',(-23,108.2,63),(12,108.4,64),24)
render('source_ship_status_entry.png',(-7.5,108.2,75),(-11,108.2,82),24)
render('source_emergency_shell.png',(15,108.2,72),(27,108.5,93),23)
scene.world.node_tree.nodes['Background'].inputs[1].default_value=.8
l=bpy.data.lights.new('QA_ONLY_external_key','AREA');l.energy=80000;l.size=80;o=bpy.data.objects.new(l.name,l);bpy.context.collection.objects.link(o);o.location=(55,-155,165);o.rotation_euler=(Vector((0,-86,75))-o.location).to_track_quat('-Z','Y').to_euler()
# Show actual under-floor transfer and keel-spine context. Old roofs remain fully present.
render('source_aft_support_frame.png',(88,133,153),(0,85,80),34)
# Unexported section clipping exposes roof/hanger/floor interfaces.
for o in bpy.context.scene.objects:
 if o.type=='MESH'and o.get('group')in['roof','shell','ceiling','fixture','threshold']and o.name.startswith('AFC'):o.hide_render=True
render('source_platform_support_cutaway.png',(67,126,135),(0,110,85),37)
(R/'qa/source_preview_receipt.json').write_text(json.dumps({'source_sha256':hashlib.sha256((R/'source/AST-CMD-002.blend').read_bytes()).hexdigest(),'central_source_sha256':hashlib.sha256((C/'assets/central_crown/source/AST-CMD-001.blend').read_bytes()).hexdigest(),'captured_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'engine':'Cycles CPU','threads':2,'samples':24,'denoised':False,'purpose':'Source-only diagnostics; temporary floor/doors/light context excluded from export. Final Godot first-person acceptance belongs to parent.','floor_context':context,'images':images},indent=2)+'\n')
