"""Source diagnostic pixels only, with unsaved planned floor and unchanged shared context."""
from pathlib import Path
import bpy,bmesh,json,math,hashlib,datetime
from mathutils import Vector
R=Path(__file__).resolve().parents[1];C=R.parents[1];D=json.loads((R/'source/section_contract.json').read_text());source=R/'source/AST-CMD-005.blend';sha=hashlib.sha256(source.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(source))
def append_source(path,offset=None):
 with bpy.data.libraries.load(str(path),link=False)as(src,dst):dst.objects=list(src.objects)
 for ob in dst.objects:
  if ob:
   bpy.context.collection.objects.link(ob)
   if offset and ob.parent is None:ob.location+=Vector(offset)
 return dst.objects
append_source(C/'assets/aft_command/source/AST-CMD-002.blend')
append_source(C/'assets/primary_atrium_core/source/AST-CIR-005_upper_link.blend',(0,-119,102))
# Four real shared door sources for context, closed. No leaves saved in005 or002.
doors=D['doors']+[d for d in json.loads((C/'assets/aft_command/source/section_contract.json').read_text())['doors']if d['name'].endswith('_exit')]
for door in doors:
 x,y,z=door['position'];append_source(C/'assets/staff_threshold/source/AST-STF-008.blend',(x,-z,y))
mat=bpy.data.materials.new('QA_ONLY_parent_planned_floor');mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.30,.28,.23,1);bs.inputs['Roughness'].default_value=.9
tris=json.loads((R/'qa/preview_floor_context.json').read_text())['triangles'];verts=[];faces=[]
for tri in tris:
 offset=len(verts);verts.extend((x,-z,106.5)for x,z in tri);faces.append(tuple(offset+i for i in range(3)))
me=bpy.data.meshes.new('QA_ONLY_parent_floor');me.from_pydata(verts,[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.materials.append(mat);ob=bpy.data.objects.new('QA_ONLY_parent_floor',me);bpy.context.collection.objects.link(ob)
for marker in D['light_markers']:
 x,y,z=marker['position'];data=bpy.data.lights.new(marker['name']+'_QA','AREA');data.energy=450;data.color=marker['suggested_color'];data.shape='DISK';data.size=1.2;ob=bpy.data.objects.new(data.name,data);bpy.context.collection.objects.link(ob);ob.location=(x,-z,y-.015)
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=16;scene.cycles.use_denoising=False;scene.render.threads_mode='FIXED';scene.render.threads=2;scene.render.resolution_x=840;scene.render.resolution_y=525;scene.render.resolution_percentage=100;scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.07,.10,.15,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.4;scene.view_settings.view_transform='AgX';images=[]
def render(name,pos,target,lens=24):
 cam=bpy.data.cameras.new(name);ob=bpy.data.objects.new(name,cam);bpy.context.collection.objects.link(ob);ob.location=(pos[0],-pos[2],pos[1]);t=Vector((target[0],-target[2],target[1]));ob.rotation_euler=(t-ob.location).to_track_quat('-Z','Y').to_euler();cam.lens=lens;cam.clip_end=1600;scene.camera=ob;scene.render.filepath=str(R/'qa'/name);bpy.ops.render.render(write_still=True);images.append(name)
render('source_receiving_to_fan.png',(0,108.1,140),(0,109,182),24)
render('source_public_wing_return.png',(16,108.1,148),(16,108.5,105),24)
render('source_service_turn.png',(27,108.1,104.2),(33,108.1,105.3),20)
render('source_closed_service_terminal.png',(26,108.1,148),(32,108.1,141.92),24)
render('source_onward_spine.png',(0,108.1,182),(0,107.6,202),24)
scene.world.node_tree.nodes['Background'].inputs[1].default_value=.8
l=bpy.data.lights.new('QA_ONLY_frame_key','AREA');l.energy=120000;l.size=70;ob=bpy.data.objects.new(l.name,l);bpy.context.collection.objects.link(ob);ob.location=(50,-165,170);ob.rotation_euler=(Vector((0,-145,110))-ob.location).to_track_quat('-Z','Y').to_euler()
render('source_platform_frame_overview.png',(86,155,222),(0,109,148),36)
render('source_seam_couplers.png',(45,122,100),(2,113,103),30)
render('source_old_wall_guard_junction.png',(39,110,108),(35.7,107.7,101.98),30)
for ob in bpy.context.scene.objects:
 if ob.name=='QA_ONLY_parent_floor':ob.hide_render=True
render('source_keel_bearing_chain.png',(165,100,300),(0,53,149),28)
assert sha==hashlib.sha256(source.read_bytes()).hexdigest()
(R/'qa/source_preview_receipt.json').write_text(json.dumps({'source_sha256':sha,'source_unchanged':True,'engine':'Cycles CPU','samples':16,'threads':2,'images':images,'captured_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'context':'Unsaved QA floor with exact existing core holes, actual old002 and upper-link source, four actual shared closed door sources and source-position local lights. No invented sky or hull view. Neutral diagnostic world only; no engine ambient setting changed.','limits':'Source diagnostic only. Parent owns actual floor ownership, runtime collision, physical loaded carts and normal/effects-off final visual review.'},indent=2)+'\n')
