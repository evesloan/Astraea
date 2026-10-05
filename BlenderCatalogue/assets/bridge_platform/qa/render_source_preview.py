"""Source-only diagnostic pixels. Unsaved parent planned floor and source-located lights are context.
No runtime adoption, sky replacement or final art acceptance implied.
"""
from pathlib import Path
import bpy,bmesh,json,math,hashlib,datetime,sys
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
R=Path(__file__).resolve().parents[1];C=R.parents[1];G=C.parent/'astraea-godot-production-20261003'
D=json.loads((R/'source/section_contract.json').read_text());source_hash=hashlib.sha256((R/'source/AST-CMD-003.blend').read_bytes()).hexdigest();capture_start=datetime.datetime.now(datetime.timezone.utc).isoformat();bpy.ops.wm.open_mainfile(filepath=str(R/'source/AST-CMD-003.blend'))
mat=bpy.data.materials.new('QA_ONLY_parent_floor');mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.21,.22,.23,1);bs.inputs['Roughness'].default_value=.88
# Exact planned compiler regions, with only old spine overlap excluded. No floor is saved in the deliverable.
polys=[('planned_bridge_port',[(-30,-172),(-4,-172),(-4,-118),(-36,-118),(-36,-160)]),('planned_bridge_starboard',[(4,-172),(30,-172),(36,-160),(36,-118),(4,-118)]),('planned_port_bypass',[(-48,-181),(-4,-181),(-4,-173),(-40,-173),(-40,-80),(-48,-80)])]
def floorpoly(name,poly,y=106.5,depth=.24):
 vs=[(x,-z,yy)for yy in[y-depth,y]for x,z in poly];n=len(poly);fs=[]
 for tri in tessellate_polygon([[Vector((x,-z,0))for x,z in poly]]):
  ids=[v if isinstance(v,int) else min(range(n),key=lambda i:(Vector((poly[i][0],-poly[i][1],0))-v).length)for v in tri];fs.extend([tuple(reversed(ids)),tuple(i+n for i in ids)])
 for i in range(n):j=(i+1)%n;fs.append((i,j,j+n,i+n))
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.materials.append(mat);o=bpy.data.objects.new('QA_ONLY_'+name,me);bpy.context.collection.objects.link(o)
for name,poly in polys:floorpoly(name,poly)
for name,poly in [('retained_spine',[(-4,-205),(4,-205),(4,-113),(-4,-113)]),('retained_fore_apron',[(-48,-80),(48,-80),(48,-74),(-48,-74)])]:floorpoly(name,poly)
# Current primary core source is context, not a rewritten stand-in. It remains untouched.
with bpy.data.libraries.load(str(C/'assets/primary_atrium_core/source/AST-CIR-005.blend'),link=False)as(src,dst):dst.objects=[n for n in src.objects if 'Cap' in n or 'Cover' in n]
for ob in dst.objects:
 if ob:bpy.context.collection.objects.link(ob)
for marker in D['light_markers']:
 x,y,z=marker['position'];data=bpy.data.lights.new(marker['name']+'_QA','AREA');data.energy=400;data.color=marker['suggested_color'];data.shape='DISK';data.size=1.2;ob=bpy.data.objects.new(data.name,data);bpy.context.collection.objects.link(ob);ob.location=(x,-z,y-.015)
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=20;scene.cycles.use_denoising=False;scene.render.threads_mode='FIXED';scene.render.threads=2;scene.render.resolution_x=840;scene.render.resolution_y=525;scene.render.resolution_percentage=100;scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.07,.10,.15,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.4;scene.view_settings.view_transform='AgX'
images=[]
def render(name,pos,target,lens=24):
 cam=bpy.data.cameras.new(name);ob=bpy.data.objects.new(name,cam);bpy.context.collection.objects.link(ob);ob.location=(pos[0],-pos[2],pos[1]);t=Vector((target[0],-target[2],target[1]));ob.rotation_euler=(t-ob.location).to_track_quat('-Z','Y').to_euler();cam.lens=lens;cam.clip_end=1600;scene.camera=ob;scene.render.filepath=str(R/'qa'/name);bpy.ops.render.render(write_still=True);images.append(name)
render('source_fore_gallery_junction.png',(0,108.2,-177),(-36,108.5,-177),24)
render('source_public_port_gallery.png',(-44,108.2,-171),(-44,108.7,-125),24)
render('source_port_window.png',(-43.2,108.2,-140),(-50,109,-128),24)
render('source_turn_to_spine.png',(-44,108.2,-176),(0,108.5,-177),24)
render('source_east_return_base.png',(0,107.7,-175),(4.1,106.8,-176.5),24)
# Exterior/construction keys are diagnostic only and never used for interior acceptance.
scene.world.node_tree.nodes['Background'].inputs[1].default_value=.8
l=bpy.data.lights.new('QA_ONLY_frame_key','AREA');l.energy=90000;l.size=70;ob=bpy.data.objects.new(l.name,l);bpy.context.collection.objects.link(ob);ob.location=(50,230,170);ob.rotation_euler=(Vector((0,130,95))-ob.location).to_track_quat('-Z','Y').to_euler()
render('source_bridge_frame_overview.png',(100,132,-220),(-5,101,-126),35)
render('source_bridge_front_left_view.png',(20,108.2,-134),(-43,110,-171),24)
render('source_guard_mouth_return.png',(7,108.2,-167),(4.05,107,-171.8),30)
for ob in bpy.context.scene.objects:
 if ob.type=='MESH'and ob.get('group')in['roof','enclosure','ceiling','glass','window_frame','fixture']:ob.hide_render=True
render('source_support_cutaway.png',(-93,124,-216),(-20,109,-137),39)
# Below-floor view shows the actual narrow supported grid and preserved D17 centreline headroom.
render('source_underfloor_spine.png',(0,104,-186),(0,104.8,-127),24)
assert source_hash==hashlib.sha256((R/'source/AST-CMD-003.blend').read_bytes()).hexdigest(),'Source changed during capture'
(R/'qa/source_preview_receipt.json').write_text(json.dumps({'source_sha256':source_hash,'capture_started_utc':capture_start,'source_unchanged_through_capture':True,'captured_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'engine':'Cycles CPU','threads':2,'samples':20,'denoised':False,'images':images,'context':'Unsaved exact planned parent floor polygons and retained floor context. Source fixture markers provide local lights. Exterior keys used only after four interior views. World background is neutral diagnostic and does not claim final celestial views.','limit':'Parent owns actual Godot floor/collision/sky and normal/effects-off visual acceptance'},indent=2)+'\n')
