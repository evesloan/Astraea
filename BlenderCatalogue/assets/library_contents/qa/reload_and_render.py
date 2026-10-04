"""Reload source, import actual GLB, compare, and render component-only proof."""
from pathlib import Path
import bpy,sys,json,math,hashlib
from mathutils import Vector
ROOT=Path(__file__).resolve().parent.parent;QA=ROOT/'qa'
def audit():
 ps=[];tri=0;issues=[];parts=[];dg=bpy.context.evaluated_depsgraph_get()
 for ob in bpy.context.scene.objects:
  if ob.type!='MESH':continue
  if ob.matrix_world.determinant()<=0:issues.append(ob.name+':nonpositive_transform')
  me=ob.evaluated_get(dg).to_mesh();me.calc_loop_triangles();tri+=len(me.loop_triangles)
  pts=[tuple(ob.matrix_world@v.co) for v in me.vertices];ps+=pts
  if not all(math.isfinite(q) for p in pts for q in p):issues.append(ob.name+':nonfinite')
  if not me.uv_layers.active:issues.append(ob.name+':missing_uv')
  parts.append(ob.name)
  ob.evaluated_get(dg).to_mesh_clear()
 lo=[min(p[i] for p in ps) for i in range(3)];hi=[max(p[i] for p in ps) for i in range(3)]
 return {'min_m':lo,'max_m':hi,'dimensions_m':[hi[i]-lo[i] for i in range(3)],'triangles':tri,'mesh_count':len(parts),'issues':issues,'packed_images':[{'name':i.name,'packed':bool(i.packed_file),'size':list(i.size)} for i in bpy.data.images if i.source=='FILE']}
def point(ob,p):ob.rotation_euler=(Vector(p)-ob.location).to_track_quat('-Z','Y').to_euler()
def material(name,col):
 m=bpy.data.materials.new(name);m.use_nodes=True;m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(*col,1);m.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.83;return m
def setup(z):
 s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.device='CPU';s.cycles.use_denoising=False;s.render.threads_mode='FIXED';s.render.threads=2;s.render.resolution_percentage=100
 for o in bpy.context.scene.objects:
  if o.parent is None:o.location.z+=z
 bpy.ops.mesh.primitive_cube_add(size=1,location=(0,0,z-.012));ob=bpy.context.object;ob.name='QA_ONLY_support_slab';ob.dimensions=(.88,.44,.024);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);ob.data.materials.append(material('QA_neutral_shelf',(.21,.225,.235)))
 bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,0));bpy.context.object.name='QA_ONLY_floor';bpy.context.object.data.materials.append(material('QA_floor',(.16,.175,.19)))
 s.world=bpy.data.worlds.new('QA neutral environment');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.38,.41,.45,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.6
 for name,loc,power,size in [('key',(-2,-3,4.5),420,3),('fill',(2,-.5,3),170,2),('rim',(0,3,4),280,2)]:
  bpy.ops.object.light_add(type='AREA',location=loc);l=bpy.context.object;l.name='QA_ONLY_'+name;l.data.energy=power;l.data.size=size;point(l,(0,0,z+.12))
 bpy.ops.object.camera_add();s.camera=bpy.context.object;s.camera.name='QA_ONLY_camera';s.camera.data.lens=52;s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.render.image_settings.file_format='PNG'
 return s.camera
def render(name,cam,loc,target,res=(640,360),lens=52):
 s=bpy.context.scene;cam.location=loc;point(cam,target);cam.data.lens=lens;s.render.resolution_x=res[0];s.render.resolution_y=res[1];s.render.filepath=str(QA/name);bpy.ops.render.render(write_still=True)
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
rendering='--render' in args
reports={}
for cid in ['006','007']:
 p=next(ROOT.glob('AST-LIB-'+cid+'_*.blend'));bpy.ops.wm.open_mainfile(filepath=str(p));source=audit();source['reloaded_source']=str(p.name);source['sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(p.with_suffix('.glb')));export=audit();export['actual_glb_import']=str(p.with_suffix('.glb').name)
 assert source['triangles']==export['triangles']
 assert max(abs(a-b) for a,b in zip(source['dimensions_m'],export['dimensions_m']))<1e-5
 assert not source['issues'] and not export['issues']
 reports[cid]={'source':source,'imported_glb':export,'paired_geometry_match':True,'scope':'Blender component evidence only; no game, room fit, actor contact, or runtime claim'}
 if rendering:
  z=1.06 if cid=='006' else .75;cam=setup(z)
  if cid=='006':
   render('006_imported_glb_standing_640.png',cam,(.79,-1.22,1.62),(-.03,0,1.18),lens=53)
   render('006_imported_glb_detail_1280.png',cam,(.51,-.91,1.55),(-.025,0,1.195),(1280,720),lens=60)
  else:
   render('007_imported_glb_seated_640.png',cam,(.58,-.91,1.19),(0,-.012,.789),lens=55)
   render('007_imported_glb_detail_1280.png',cam,(.29,-.45,1.24),(0,0,.786),(1280,720),lens=54)
(QA/'source_reload_import_audit.json').write_text(json.dumps(reports,indent=2));print('PAIRED_SOURCE_GLB_PASS',json.dumps(reports))
if rendering:
 for variant in ['reordered','short_flat']:
  bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(ROOT/('AST-LIB-006_upright_book_group_'+variant+'.glb')));cam=setup(1.06)
  render('006_'+variant+'_imported_glb_640.png',cam,(.79,-1.22,1.62),(-.03,0,1.18),lens=53)
