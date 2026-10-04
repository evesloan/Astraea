"""Matched640 actual imported GLB comparison. Run -- --preflight first.
Small controlled -4/0/+4deg camera orbit checks repeated-scale silhouette and
shading/alias stability; this is not native runtime/temporal performance QA.
"""
import bpy,bmesh,math,json,sys,hashlib,importlib.util
from pathlib import Path
from mathutils import Vector,Matrix
BASE=Path(__file__).resolve().parents[1];CAT=BASE.parents[2];PREFLIGHT='--preflight'in sys.argv
s=importlib.util.spec_from_file_location('qa_frame',CAT/'standards/qa_frame.py');qa=importlib.util.module_from_spec(s);s.loader.exec_module(qa)
FILES={'near':'utility_flange_near_comparison.glb','baseline':'utility_flange_exact_profile_baseline.glb','economical':'utility_flange_economical.glb'}
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
def imported(filename,T=None):
 before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(BASE/'exports'/filename));new=[o for o in bpy.data.objects if o not in before]
 if T is not None:
  for o in new:
   if o.parent not in new:o.matrix_world=T@o.matrix_world
 return [o for o in new if o.type=='MESH']
def context_links():
 # Preserve actual exported link triangles from the economical context,
 # deleting all flange polygons. Same actual links appear in all variants.
 obs=imported('utility_flange_repeated_context.glb');keep=[]
 stations=[.8*i+x for i in range(5)for x in(.085,.715)]
 for o in obs:
  bm=bmesh.new();bm.from_mesh(o.data);remove=[]
  for face in bm.faces:
   if not all(any(abs((o.matrix_world@v.co).y-s)<1e-6 for s in stations)for v in face.verts):remove.append(face)
  bmesh.ops.delete(bm,geom=remove,context='FACES');bm.to_mesh(o.data);bm.free()
  if len(o.data.polygons):keep.append(o)
  else:bpy.data.objects.remove(o,do_unlink=True)
 return keep

def mat(name,c):
 m=bpy.data.materials.new(name);m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*c,1);m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.85;return m

def stage():
 sc=bpy.context.scene;sc.render.engine='BLENDER_EEVEE_NEXT';sc.eevee.taa_render_samples=64;sc.cycles.use_denoising=False;sc.render.threads_mode='FIXED';sc.render.threads=2;sc.render.resolution_percentage=100;sc.render.resolution_x=640;sc.render.resolution_y=360;sc.view_settings.view_transform='AgX';sc.view_settings.look='AgX - Medium High Contrast';sc.view_settings.exposure=-.55
 sc.world=bpy.data.worlds.new('QA_ONLY_world');sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.22,.27,.31,1);sc.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.55
 bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,0));bpy.context.object.name='QA_ONLY_floor';bpy.context.object.data.materials.append(mat('QA_ONLY_floor',(.15,.18,.20)))
 for name,loc,energy,size in[('key',(-2,-3,5),1100,3.5),('fill',(3,-1,3),750,3),('rim',(1,5,4),1250,3)]:
  data=bpy.data.lights.new('QA_ONLY_'+name,'AREA');o=bpy.data.objects.new(data.name,data);bpy.context.collection.objects.link(o);o.location=loc;data.energy=energy;data.shape='DISK';data.size=size;aim(o,(0,1,.7))
 data=bpy.data.cameras.new('QA_ONLY_camera');o=bpy.data.objects.new(data.name,data);bpy.context.collection.objects.link(o);sc.camera=o;data.clip_start=.005;data.clip_end=250;return o

def main():
 evidence={'scope':'Matched640 actual imported GLB comparison; no source rendered meshes, no engine scene or native frame-rate inference','engine':'BLENDER_EEVEE_NEXT','samples':64,'denoising':False,'render_frame':'Blender Z-up after standard native GLB import; input GLB basis is Y-up and source maps (x,y,z)->(x,z,-y); do not apply C again after Blender import','input_hashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in(BASE/'exports').glob('*.glb')},'views':{}}
 for distance in('near','repeated'):
  for variant in('near','baseline','economical'):
   bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
   if distance=='near':objects=imported(FILES[variant],Matrix.Translation((0,0,.75)));target=Vector((.025,0,.75));origin=Vector((-.64,-.60,1.05));lens=42
   else:
    if variant=='economical':objects=imported('utility_flange_repeated_context.glb')
    else:
     objects=[]
     for i in range(6):
      for yaw in(90,-90):objects+=imported(FILES[variant],Matrix.Translation((0,i*.8,.7))@Matrix.Rotation(math.radians(yaw),4,'Z'))
     objects+=context_links()
    target=Vector((0,2,.7));origin=Vector((-4,-1.6,2.3));lens=40
   cam=stage();sc=bpy.context.scene;cam.data.lens=lens
   for angle in([0]if variant=='baseline'else[-4,0,4]):
    cam.location=target+Matrix.Rotation(math.radians(angle),3,'Z')@(origin-target);aim(cam,target);bpy.context.view_layer.update();fr=qa.assert_full_frame(sc,cam,objects,margin=.025)
    name=f'{distance}_{variant}_{angle:+03d}deg_640.png';key=f'{distance}/{variant}/{angle}'
    evidence['views'][key]={'path':'renders/'+name,'camera_source_world_m':list(cam.location),'target_source_world_m':list(target),'camera_distance_to_target_m':(cam.location-target).length,'focal_length_mm':lens,'resolution':[640,360],'controlled_orbit_degrees':angle,'frame_check':fr,'full_extent_required':True,'actual_mesh_objects':len(objects),'context':'Standalone original/economical flange'if distance=='near'else'Six actual opposed mating pairs and identical five actual-exported hollow links; neutral floor is QA-only'}
    if not PREFLIGHT:sc.render.image_settings.file_format='PNG';sc.render.filepath=str(BASE/'renders'/name);bpy.ops.render.render(write_still=True)
 (BASE/'qa'/('camera_preflight.json'if PREFLIGHT else'render_evidence.json')).write_text(json.dumps(evidence,indent=2)+'\n');print('FLANGE_PREFLIGHT_PASS'if PREFLIGHT else'FLANGE_RENDER_COMPLETE')
if __name__=='__main__':main()
