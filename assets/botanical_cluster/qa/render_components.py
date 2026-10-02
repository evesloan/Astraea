"""Bounded component-only Eevee captures, exact source/export hashes and camera frame evidence."""
import bpy,json,hashlib,math,importlib.util
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parents[1];CAT=BASE.parents[1]
spec=importlib.util.spec_from_file_location('frame',CAT/'standards/qa_frame.py');f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def point(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
def mat(name,color,rough=1):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(*color,1);b.inputs['Roughness'].default_value=rough;return m
views={
 'AST-BOT-007':{'cam':(4.1,-6.4,2.35),'aim':(0,.08,1.35),'ortho':5.4,'floor':-.012,'description':'Full specimen/crown inspection at camera Z2.35m; slightly downward toward mid-crown. Not an ordinary standing eye-height view'},
 'AST-BOT-008':{'cam':(1.65,-2.4,1.03),'aim':(0,.38,-.13),'ortho':2.6,'floor':-.615,'description':'High three-quarter view exposes root-to-arch-to-unequal-tail chain; isolated below-soil drop visible'},
 'AST-BOT-009':{'cam':(2.4,-4.2,1.18),'aim':(0,0,.54),'ortho':2.7,'floor':-.012,'description':'Upright flowering bank full silhouette; lens elevated near flower tops, not a host outlook'}
}
rows=[]
for ident in views:
 rec=json.loads((BASE/(ident+'.manifest.json')).read_text());src=BASE/rec['source'];export=BASE/rec['export'];cfg=views[ident]
 for mode in(('source','imported')if ident=='AST-BOT-009'else('imported',)):
  if mode=='source':bpy.ops.wm.open_mainfile(filepath=str(src))
  else:
   bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(export))
  objects=[o for o in bpy.context.scene.objects if o.type=='MESH'];scene=bpy.context.scene;scene.render.engine='BLENDER_EEVEE_NEXT';scene.eevee.taa_render_samples=48;scene.render.resolution_x=640;scene.render.resolution_y=360;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False;scene.world=bpy.data.worlds.new('QA neutral sky');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.20,.24,.22,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.55;scene.view_settings.view_transform='AgX'
  bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,cfg['floor']));floor=bpy.context.object;floor.name='QA_ONLY_STUDIO_FLOOR';floor.data.materials.append(mat('QA neutral warm floor',(.24,.25,.235)))
  for name,pos,power,size in [('key',(-3,-4,6),1000,5),('fill',(4,-1,4),700,4),('rim',(1,4,5),1100,3)]:
   data=bpy.data.lights.new('QA_'+name,'AREA');data.energy=power;data.shape='DISK';data.size=size;o=bpy.data.objects.new('QA_'+name,data);scene.collection.objects.link(o);o.location=pos;point(o,(0,0,.9))
  data=bpy.data.cameras.new('QA camera');cam=bpy.data.objects.new('QA camera',data);scene.collection.objects.link(cam);cam.location=cfg['cam'];point(cam,cfg['aim']);data.type='ORTHO';data.ortho_scale=cfg['ortho'];data.clip_end=100;scene.camera=cam
  frame=f.assert_full_frame(scene,cam,objects,margin=.025);path=BASE/'qa'/f'{ident}_{mode}_640.png';scene.render.filepath=str(path);before=(sha(src),sha(export));bpy.ops.render.render(write_still=True);after=(sha(src),sha(export));assert before==after
  rows.append({'catalogue_id':ident,'mode':mode,'image':str(path.relative_to(BASE)),'image_sha256':sha(path),'source_sha256':before[0],'glb_sha256':before[1],'hashes_unchanged_during_capture':before==after,'camera_source_position_m':list(cam.location),'camera_rotation_euler':list(cam.rotation_euler),'aim_source_m':cfg['aim'],'camera_type':'ORTHO','ortho_scale':data.ortho_scale,'resolution':[640,360],'render_samples':48,'frame':frame,'description':cfg['description'],'scope':'Blender Eevee component inspection; no engine, host or performance claim'})
  (BASE/'qa/render_evidence.json').write_text(json.dumps({'views':rows,'final_hashes_frozen':True},indent=2)+'\n')
print('RENDERED',len(rows))
