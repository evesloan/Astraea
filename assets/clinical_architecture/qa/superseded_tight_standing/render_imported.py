"""Serialized, exact-hash-bound imported-GLB inspection views. Call only with lead render slot."""
import bpy,sys,json,hashlib,math
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
VIEWS={
 '001_closed_standing_640':('AST-MED-001',False,(3.7,-5.1,1.62),(.0,.10,1.20),48,640,360),
 '001_open_standing_640':('AST-MED-001',True,(3.7,-5.1,1.62),(.0,.10,1.20),48,640,360),
 '001_track_and_grip_detail_1280':('AST-MED-001',False,(2.4,-2.8,2.48),(.65,.09,1.94),65,1280,720),
 '002_standing_640':('AST-MED-002',False,(2.65,-3.5,1.62),(0,.02,.91),52,640,360),
 '002_basin_supply_detail_1280':('AST-MED-002',False,(1.45,-2.0,2.20),(-.05,.03,1.06),57,1280,720),
 '002_rear_service_detail_1280':('AST-MED-002',False,(-1.8,2.7,1.15),(-.12,.21,.69),55,1280,720),
}
args=sys.argv[sys.argv.index('--')+1:]if '--'in sys.argv else list(VIEWS)
record_path=BASE/'qa/render_evidence.json';records=json.loads(record_path.read_text())if record_path.exists()else {'scope':'Blender imported GLB inspection only; ordinary and detail cameras explicitly separated, no game renderer/host validation','views':{}}
for name in args:
 ident,isopen,eye,target,lens,w,h=VIEWS[name];source=BASE/'source'/f'{ident}.blend';export=BASE/'exports'/(ident+('__open'if isopen else'')+'.glb');before={'source':sha(source),'glb':sha(export),'render_script':sha(Path(__file__))}
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(export));scene=bpy.context.scene
 # Imported component coordinates are restored by the GLB importer to Blender Z-up.
 scene.render.engine='BLENDER_EEVEE_NEXT';scene.render.resolution_x=w;scene.render.resolution_y=h;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
 scene.world=bpy.data.worlds.new('Neutral inspection world');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.22,.25,.26,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.45
 bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.013));floor=bpy.context.object;floor.name='QA_only_neutral_floor';m=bpy.data.materials.new('QA floor');m.diffuse_color=(.19,.215,.225,1);m.use_nodes=True;m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.19,.215,.225,1);m.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.95;floor.data.materials.append(m)
 for nm,loc,energy,size in [('key',(-3,-4,6),1150,5),('fill',(4,-1,4),700,4),('rear',(0,3,5),900,3)]:
  dat=bpy.data.lights.new('QA_'+nm,'AREA');dat.energy=energy;dat.shape='DISK';dat.size=size;ob=bpy.data.objects.new(dat.name,dat);scene.collection.objects.link(ob);ob.location=loc;ob.rotation_euler=(Vector((0,0,1))-ob.location).to_track_quat('-Z','Y').to_euler()
 dat=bpy.data.cameras.new('QA_camera');cam=bpy.data.objects.new('QA_camera',dat);scene.collection.objects.link(cam);cam.location=eye;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();dat.lens=lens;scene.camera=cam
 scene.view_settings.view_transform='AgX';scene.render.filepath=str(BASE/'qa'/f'{name}.png');bpy.ops.render.render(write_still=True)
 after={'source':sha(source),'glb':sha(export),'render_script':sha(Path(__file__))};assert before==after
 records['views'][name]={'catalogue_id':ident,'state':'open'if isopen else'closed','image':f'qa/{name}.png','image_sha256':sha(BASE/'qa'/f'{name}.png'),'source':str(source.relative_to(BASE)),'export':str(export.relative_to(BASE)),'hashes_before':before,'hashes_after':after,'camera_source_frame':{'eye':eye,'target':target,'lens_mm':lens,'resolution':[w,h]},'inspection_type':'ordinary standing proposed eye height 1.62m'if 'standing'in name else'explicit higher or rear detail view','source_unchanged':True}
 record_path.write_text(json.dumps(records,indent=2)+'\n')
 print('RENDERED',name)
