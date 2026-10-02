"""Blender component compatibility inspection; never game/room evidence.

Combines the final evaluated exports without modifying any source asset.
The empty opening deliberately has no invented courtyard or exterior image.
"""
import bpy, math, json, hashlib, sys
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'qa/combined_components'
OUT.mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)

def bring(path, name, loc, angle=0):
 before=set(bpy.data.objects)
 bpy.ops.import_scene.gltf(filepath=str(path))
 obs=list(set(bpy.data.objects)-before)
 anchor=bpy.data.objects.new(name,None);bpy.context.collection.objects.link(anchor)
 for o in obs:
  if o.parent is None:o.parent=anchor
 anchor.location=loc;anchor.rotation_euler.z=angle
 bpy.context.view_layer.update()
 pts=[o.matrix_world@Vector(c) for o in obs if o.type=='MESH' for c in o.bound_box]
 lo=[min(p[i] for p in pts) for i in range(3)];hi=[max(p[i] for p in pts) for i in range(3)]
 return {'file':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'position_blender_m':loc,'rotation_z_rad':angle,'bounds_blender_m':{'min':lo,'max':hi}}

sources=[]
sources.append(bring(ROOT/'assets/view_reveal/exports/AST-VR-01-ASSEMBLY.glb','Reveal inspection assembly',(0,0,0)))
sources.append(bring(ROOT/'assets/furniture/AST-FUR-001_day_window_bench.glb','Window bench',(0,-.86,0)))
sources.append(bring(ROOT/'assets/furniture/AST-FUR-003_day_table.glb','Day table',(0,-2.12,0)))
sources.append(bring(ROOT/'assets/furniture/AST-FUR-002_day_reading_chair.glb','Reading chair',(1.20,-3.35,0),math.radians(155)))

pair_checks=[]
for i,a in enumerate(sources):
 for b in sources[i+1:]:
  aa=a['bounds_blender_m'];bb=b['bounds_blender_m'];overlap=[min(aa['max'][k],bb['max'][k])-max(aa['min'][k],bb['min'][k]) for k in range(3)]
  pair_checks.append({'a':a['file'],'b':b['file'],'aabb_overlap_m':overlap,'separate':any(x<=0 for x in overlap)})
assert all(x['separate'] for x in pair_checks), pair_checks
mat=bpy.data.materials.new('QA neutral floor');mat.diffuse_color=(.20,.22,.23,1);mat.use_nodes=True
bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.20,.22,.23,1);bs.inputs['Roughness'].default_value=.9
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.006));bpy.context.object.name='QA floor only';bpy.context.object.data.materials.append(mat)
scene=bpy.context.scene;scene.render.engine='BLENDER_EEVEE_NEXT'
if hasattr(scene, 'eevee') and hasattr(scene.eevee, 'taa_render_samples'): scene.eevee.taa_render_samples=128
scene.render.threads_mode='FIXED';scene.render.threads=4
scene.world.color=(.18,.18,.18)
scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast';scene.view_settings.exposure=0

def light(name,loc,energy,size,colour):
 data=bpy.data.lights.new(name,'AREA');data.energy=energy;data.shape='DISK';data.size=size;data.color=colour
 o=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,-1,1))-o.location).to_track_quat('-Z','Y').to_euler()
light('QA soft key',(-4,-5,6),1100,5,(1,.95,.87));light('QA neutral fill',(4,-2,4),650,4,(.90,.95,1));light('QA top return',(0,3,5),900,4,(1,1,1))
camdata=bpy.data.cameras.new('QA ordinary height');cam=bpy.data.objects.new('QA camera',camdata);bpy.context.collection.objects.link(cam);scene.camera=cam
camdata.lens=31;camdata.sensor_width=36;camdata.clip_start=.05;camdata.clip_end=300
views=[('standing_640',(3.5,-6.6,1.65),(0,-.8,1.35),640,360),('seated_640',(-2.0,-4.7,1.18),(0,-.75,1.35),640,360),('three_quarter_1280',(4.5,-7.5,3.3),(0,-1.0,1.20),1280,720)]
selected=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
for name,loc,target,w,h in views:
 if selected and name not in selected:continue
 camdata.lens=27 if name=='three_quarter_1280' else 31
 cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.resolution_x=w;scene.render.resolution_y=h;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.filepath=str(OUT/(name+'.png'));bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'component_arrangement.blend'))
(OUT/'evidence.json').write_text(json.dumps({'scope':'Blender component arrangement only. Empty opening, no room adoption, gameplay, physics, actual rig or runtime performance claim.','sources':sources,'component_bound_separation':pair_checks,'renderer':'Blender4.3.2 Eevee component renderer','views':[{'name':x[0],'eye_height_m':x[1][2],'resolution':x[3:],'lens_mm':27 if x[0]=='three_quarter_1280' else 31} for x in views],'rendered_in_this_run':selected or [x[0] for x in views],'fixture_note':'Inspection lights are not proposed ship fixtures. Layout is an inspection arrangement, not an approved room allocation.'},indent=2)+'\n')
