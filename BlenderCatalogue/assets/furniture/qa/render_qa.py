"""Independent .blend reload and bounded Blender component inspection renders."""
import bpy,math,json,sys,hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parent.parent
QA=ROOT/'qa'

def mat(name,color,rough=.72):
 m=bpy.data.materials.new(name);m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough
 return m

def point(ob,p):ob.rotation_euler=(Vector(p)-ob.location).to_track_quat('-Z','Y').to_euler()

def studio():
 s=bpy.context.scene;s.render.engine='BLENDER_EEVEE_NEXT';s.cycles.samples=24;s.cycles.use_denoising=False;s.cycles.device='CPU'
 s.eevee.taa_render_samples=32
 s.render.threads_mode='FIXED';s.render.threads=4;s.render.resolution_percentage=100
 s.world=bpy.data.worlds.new('QA neutral daylight');s.world.use_nodes=True
 s.world.node_tree.nodes['Background'].inputs[0].default_value=(.42,.44,.47,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.45
 bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.002));bpy.context.object.name='QA_ONLY_neutral_floor';bpy.context.object.data.materials.append(mat('QA_floor',(.19,.205,.22)))
 for name,loc,power,size in [('QA_key',(-3,-4,5.8),700,5),('QA_fill',(4,-1,3.4),420,4),('QA_rim',(-1,4,4),500,3)]:
  bpy.ops.object.light_add(type='AREA',location=loc);l=bpy.context.object;l.name=name;l.data.energy=power;l.data.shape='DISK';l.data.size=size;point(l,(0,0,.5))
 bpy.ops.object.camera_add();cam=bpy.context.object;cam.name='QA_ONLY_camera';cam.data.lens=52;s.camera=cam
 s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast'
 s.render.image_settings.file_format='PNG';s.render.film_transparent=False
 return cam

def render(cam,path,loc,target,res=(640,360),lens=52):
 s=bpy.context.scene;cam.location=loc;point(cam,target);cam.data.lens=lens
 s.render.resolution_x=res[0];s.render.resolution_y=res[1];s.render.filepath=str(QA/path)
 bpy.ops.render.render(write_still=True)

def proxy(x,y):
 m=mat('QA_scale_proxy_neutral',(.30,.32,.34))
 def sphere(name,loc,scale):
  bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,radius=1,location=(loc[0]+x,loc[1]+y,loc[2]));o=bpy.context.object;o.name='QA_SCALE_PROXY_'+name;o.scale=scale;o.data.materials.append(m)
 def limb(name,a,b,r):
  aa=Vector((a[0]+x,a[1]+y,a[2]));bb=Vector((b[0]+x,b[1]+y,b[2]));mid=(aa+bb)/2
  bpy.ops.mesh.primitive_cone_add(vertices=12,radius1=r,radius2=r*.8,depth=(bb-aa).length,location=mid);o=bpy.context.object;o.name='QA_SCALE_PROXY_'+name;o.rotation_euler=(bb-aa).to_track_quat('Z','Y').to_euler();o.data.materials.append(m)
 sphere('head',(0,0,1.628),(.092,.10,.122));sphere('torso',(0,0,1.25),(.20,.105,.24));sphere('pelvis',(0,0,.965),(.15,.11,.15))
 for side in [-1,1]:
  limb('upper_leg',(side*.105,0,.96),(side*.115,.01,.54),.072);limb('shin',(side*.115,.01,.54),(side*.12,0,.075),.049)
  sphere('foot',(side*.12,-.065,.045),(.063,.135,.045));limb('upper_arm',(side*.18,0,1.40),(side*.23,0,1.11),.041);limb('forearm',(side*.23,0,1.11),(side*.255,-.025,.86),.032);sphere('hand',(side*.255,-.025,.825),(.036,.026,.065))

def check_source():
 objects=[o for o in bpy.context.scene.objects if o.type in {'MESH','CURVE'}];dg=bpy.context.evaluated_depsgraph_get();ps=[];bad=[];triangle=0
 for ob in objects:
  if abs(ob.matrix_world.determinant())<1e-9:bad.append(ob.name+':singular_transform')
  eo=ob.evaluated_get(dg);me=eo.to_mesh();me.calc_loop_triangles();triangle+=len(me.loop_triangles)
  for v in me.vertices:
   p=ob.matrix_world@v.co;ps.append(tuple(p))
   if not all(math.isfinite(v) for v in p):bad.append(ob.name+':nonfinite')
  eo.to_mesh_clear()
 lo=[min(p[i] for p in ps) for i in range(3)];hi=[max(p[i] for p in ps) for i in range(3)]
 return {'reloaded_source':True,'source_blend_sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'min_m':lo,'max_m':hi,'dimensions_m':[hi[i]-lo[i] for i in range(3)],'triangles':triangle,'issues':bad,'floor_contact_abs_m':abs(lo[2]),'packed_images':[{ 'name':i.name,'packed':bool(i.packed_file),'size':list(i.size),'packed_sha256':hashlib.sha256(i.packed_file.data).hexdigest() if i.packed_file else None} for i in bpy.data.images if i.source=='FILE'],'qa_scope':'Blender asset only; neutral studio and body-scale proxy are QA helpers, never exported, no Godot or rig claim'}

args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
minimal='--minimal' in args;audit_only='--audit-only' in args
args=[a for a in args if a not in ['--minimal','--audit-only']]
ids=args if args else ['001','002','003'];reports={}
for n in ids:
 blend=next(ROOT.glob('AST-FUR-'+n+'_*.blend'));bpy.ops.wm.open_mainfile(filepath=str(blend));reports[n]=check_source()
 (QA/(n+'_reload_audit.json')).write_text(json.dumps(reports[n],indent=2))
 if audit_only:continue
 cam=studio()
 if n=='001':
  render(cam,n+'_three_quarter_640.png',(3.65,-4.8,2.45),(0,0,.46))
  render(cam,n+'_detail_1280.png',(3.05,-3.65,2.02),(0,-.015,.47),(1280,720),55)
  if minimal:continue
  proxy(-1.68,.22);render(cam,n+'_standing_context_640.png',(3.7,-6.2,1.66),(-.42,0,.85),lens=50)
  render(cam,n+'_seated_context_640.png',(3.3,-5.45,1.19),(-.30,0,.76),lens=48)
 elif n=='002':
  render(cam,n+'_three_quarter_640.png',(2.25,-3.25,1.96),(0,0,.47),lens=55)
  if minimal:continue
  render(cam,n+'_detail_1280.png',(2.08,-3.12,1.85),(0,0,.49),(1280,720),53)
  proxy(-.94,.17);render(cam,n+'_standing_context_640.png',(2.42,-4.75,1.66),(-.35,0,.87),lens=45)
  render(cam,n+'_seated_context_640.png',(2.3,-4.1,1.19),(-.29,0,.81),lens=42)
 else:
  render(cam,n+'_three_quarter_640.png',(1.85,-2.7,1.79),(0,0,.31),lens=56)
  if minimal:continue
  render(cam,n+'_detail_1280.png',(1.58,-2.48,1.63),(0,0,.33),(1280,720),60)
  proxy(-.94,.23);render(cam,n+'_standing_context_640.png',(2.2,-4.75,1.66),(-.30,0,.83),lens=44)
  render(cam,n+'_seated_context_640.png',(2.1,-4.1,1.19),(-.30,0,.77),lens=42)
 (QA/(n+'_reload_audit.json')).write_text(json.dumps(reports[n],indent=2))
print('QA_RELOAD_RENDER_COMPLETE',json.dumps(reports))
