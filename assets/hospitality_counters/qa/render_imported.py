"""Imported final GLB component-only render evidence. Use --preflight first."""
import bpy,sys,json,hashlib,importlib.util,math
from pathlib import Path
from mathutils import Vector,Matrix
BASE=Path(__file__).resolve().parents[1];CAT=BASE.parents[1]
spec=importlib.util.spec_from_file_location('qa_frame',CAT/'standards/qa_frame.py');q=importlib.util.module_from_spec(spec);spec.loader.exec_module(q)
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else[];preflight='--preflight' in args;views=args[args.index('--views')+1].split(',') if '--views' in args else['guest','staff','standing','joint']
def aim(o,t):o.rotation_euler=(Vector(t)-o.location).to_track_quat('-Z','Y').to_euler()
def plain(name,color):
 m=bpy.data.materials.new(name);m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*color,1);m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.8;return m
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);component=[]
for ident,loc in [('AST-HSP-001',(0,0,0)),('AST-HSP-002',(2.4,0,0))]:
 old=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(BASE/'exports'/f'{ident}.glb'))
 for ob in [o for o in bpy.data.objects if o not in old]:
  if ob.parent is None:ob.location+=Vector(loc)
  if ob.type=='MESH':component.append(ob)
bpy.context.view_layer.update();sc=bpy.context.scene;sc.render.engine='BLENDER_EEVEE_NEXT';sc.eevee.taa_render_samples=64;sc.render.threads_mode='FIXED';sc.render.threads=4;sc.render.resolution_percentage=100;sc.view_settings.view_transform='AgX';sc.view_settings.look='AgX - Medium High Contrast';sc.view_settings.exposure=-.75
sc.world=bpy.data.worlds.new('QA_neutral_world');sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.28,.31,.34,1);sc.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.55
bpy.ops.mesh.primitive_plane_add(size=200,location=(1.5,0,-.003));floor=bpy.context.object;floor.name='QA_ONLY_neutral_floor';floor.data.materials.append(plain('QA_ONLY_floor',(.20,.22,.23)))
for name,loc,energy,size in [('key',(-1.2,-3.8,5),1250,4),('fill',(4,-1,2.5),750,3),('staff',(1,4,3),1200,4)]:
 d=bpy.data.lights.new('QA_ONLY_'+name,'AREA');o=bpy.data.objects.new(d.name,d);bpy.context.collection.objects.link(o);o.location=loc;d.energy=energy;d.size=size;aim(o,(1.5,0,.45))
d=bpy.data.cameras.new('QA_ONLY_camera');cam=bpy.data.objects.new(d.name,d);bpy.context.collection.objects.link(cam);sc.camera=cam;d.clip_start=.01;d.clip_end=200
plans={'guest':{'location':[4.6,-5.3,3.2],'target':[1.60,.10,.44],'ortho':4.35,'res':[1280,960],'full':True,'caption':'Imported GLB: pantry plus compatible curved return, neutral component inspection'},'staff':{'location':[-.60,4.6,2.7],'target':[1.60,.10,.44],'ortho':4.35,'res':[1280,960],'full':True,'caption':'Imported GLB: rear service bays, curved inner shelving and proposed drawer slid 0.32m'},'standing':{'location':[1.55,-4.60,1.65],'target':[1.55,.03,.48],'lens':38,'res':[640,360],'full':True,'caption':'Imported GLB: ordinary 1.65m standing eye height, neutral component-only view'},'joint':{'location':[3.3,-1.35,1.50],'target':[2.40,-.14,.61],'ortho':1.35,'res':[1280,960],'full':False,'caption':'Imported GLB: 2mm seam, continuous top/profile and closed terminal structure; purposeful close crop'}}
evidence={'scope':'Blender imported-GLB component evidence only, no game/room/physics/target-PC claim','source_hashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (BASE/'source').glob('AST-*.blend')},'glb_hashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (BASE/'exports').glob('*.glb')},'placements_source':[{'id':'AST-HSP-001','translation_m':[0,0,0],'yaw_degrees':0},{'id':'AST-HSP-002','translation_m':[2.4,0,0],'yaw_degrees':0}],'views':{}}
original={o.name:o.matrix_world.copy() for o in component}
for name in views:
 p=plans[name]
 for o in component:
  o.matrix_world=original[o.name]
  if name=='staff' and 'proposed_linen_drawer' in o.name:o.matrix_world=Matrix.Translation(Vector((0,.32,0)))@o.matrix_world
 cam.location=p['location'];aim(cam,p['target']);cam.data.type='ORTHO' if 'ortho'in p else'PERSP';cam.data.ortho_scale=p.get('ortho',4.35);cam.data.lens=p.get('lens',48);sc.render.resolution_x,sc.render.resolution_y=p['res'];bpy.context.view_layer.update();fr=q.frame_report(sc,cam,component,margin=.035)
 if p['full'] and not fr['passes']:raise RuntimeError(name+' framing fails '+str(fr))
 evidence['views'][name]={'camera':p,'framing':fr,'pose':'Proposed linear drawer +Y0.32m; remaining parts as exported' if name=='staff' else'Closed/default export pose','full_silhouette_required':p['full']}
 if not preflight:
  sc.render.image_settings.file_format='PNG';sc.render.filepath=str(BASE/'qa'/f'{name}_raw.png');bpy.ops.render.render(write_still=True)
(BASE/'qa'/('camera_preflight.json' if preflight else'render_evidence.json')).write_text(json.dumps(evidence,indent=2)+'\n');print('PREFLIGHT_PASS' if preflight else'RENDER_COMPLETE')
