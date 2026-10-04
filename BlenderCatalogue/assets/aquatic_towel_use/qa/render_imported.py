"""Lead-serialized actual imported GLB evidence. No engine or room claim."""
from pathlib import Path
import bpy,sys,json,hashlib
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];CAT=ROOT.parents[1]
sys.path.insert(0,str(CAT/'standards'))
from qa_frame import frame_report
ARGS=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
PREFLIGHT='--preflight' in ARGS
VIEWS=ARGS[ARGS.index('--views')+1].split(',') if '--views' in ARGS else ['dry_standing','return_standing','return_withdrawn_rear','dry_shelf_detail','return_throat_detail']
def aim(ob,p):ob.rotation_euler=(Vector(p)-ob.location).to_track_quat('-Z','Y').to_euler()
def matte(name,col):
 m=bpy.data.materials.new(name);m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*col,1);m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.8;return m
def imported(asset):
 old=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(ROOT/'exports'/f'{asset}.glb'))
 return [o for o in bpy.data.objects if o not in old and o.type=='MESH']
bpy.ops.wm.read_factory_settings(use_empty=True);sc=bpy.context.scene;sc.render.engine='BLENDER_EEVEE_NEXT';sc.eevee.taa_render_samples=48;sc.cycles.use_denoising=False
sc.render.resolution_percentage=100;sc.view_settings.view_transform='AgX';sc.view_settings.look='AgX - Medium High Contrast';sc.view_settings.exposure=-.60
sc.world=bpy.data.worlds.new('QA_ONLY_world');sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.27,.30,.32,1);sc.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.55
groups={a:imported(a) for a in ('AST-AQU-007','AST-AQU-008','AST-AQU-008_withdrawn')}
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.003));bpy.context.object.name='QA_ONLY_floor';bpy.context.object.data.materials.append(matte('QA_ONLY_floor',(.18,.205,.214)))
for name,loc,power,size in [('key',(-3,-4,5),1100,4.5),('fill',(3,-1,3.5),650,4),('rim',(1,4,5),950,3)]:
 d=bpy.data.lights.new('QA_ONLY_'+name,'AREA');o=bpy.data.objects.new(d.name,d);bpy.context.collection.objects.link(o);o.location=loc;d.energy=power;d.size=size;aim(o,(0,0,.6))
d=bpy.data.cameras.new('QA_ONLY_camera');cam=bpy.data.objects.new(d.name,d);bpy.context.collection.objects.link(cam);sc.camera=cam;d.clip_start=.01;d.clip_end=250
plans={
 'dry_standing':{'asset':'AST-AQU-007','location':[1.66,-5.12,1.65],'target':[0,0,.91],'lens':48,'res':[640,360],'full':True,'caption':'1.65m camera; actual imported dry niche. Protected front retrieval and folded stock; no room claim'},
 'return_standing':{'asset':'AST-AQU-008','location':[1.83,-3.66,1.65],'target':[0,0,.61],'lens':48,'res':[640,360],'full':True,'caption':'1.65m camera; actual imported guarded return. Fixed hood and shaped receiving throat'},
 'return_withdrawn_rear':{'asset':'AST-AQU-008_withdrawn','location':[2.1,4.5,1.65],'target':[0,.50,.50],'lens':45,'res':[640,360],'full':True,'caption':'1.65m rear camera; complete0.92m bin withdrawal with four floor-contact wheels and real handle'},
 'dry_shelf_detail':{'asset':'AST-AQU-007','location':[1.3,-2.1,1.5],'target':[0,-.05,1.04],'lens':47,'res':[960,720],'full':False,'caption':'Detail crop; true shelves, folded woven forms, original stacked-cloth symbol and relief DRY marking'},
 'return_throat_detail':{'asset':'AST-AQU-008','location':[.95,-1.55,1.35],'target':[0,-.13,.89],'lens':52,'res':[960,720],'full':False,'caption':'Detail crop; down-turn receiving floor, guards and opaque baffle; no implemented laundry or physics'}
}
report={'scope':'Imported native GLB component inspection; lights, floor and cameras are QA only. Not host room or engine evidence.','source_hashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'source').glob('*.blend')},'export_hashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'exports').glob('*.glb')},'views':{}}
for name in VIEWS:
 p=plans[name]
 for group,obs in groups.items():
  for o in obs:o.hide_render=group!=p['asset']
 cam.location=p['location'];aim(cam,p['target']);d.type='PERSP';d.lens=p['lens'];sc.render.resolution_x,sc.render.resolution_y=p['res']
 frame=frame_report(sc,cam,groups[p['asset']],.045)
 if p['full'] and not frame['passes']:raise RuntimeError(name+' framing failed '+str(frame))
 report['views'][name]={'camera':p,'framing':frame,'full_component_silhouette_required':p['full']}
 if not PREFLIGHT:
  sc.render.filepath=str(ROOT/'qa'/f'{name}_raw.png');sc.render.image_settings.file_format='PNG';bpy.ops.render.render(write_still=True)
(ROOT/'qa'/('camera_preflight.json' if PREFLIGHT else 'render_evidence.json')).write_text(json.dumps(report,indent=2)+'\n')
print('PREFLIGHT_PASS' if PREFLIGHT else 'RENDER_COMPLETE',VIEWS)
