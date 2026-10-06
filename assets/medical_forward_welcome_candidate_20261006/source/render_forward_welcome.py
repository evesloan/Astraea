"""Render the authored .blend, never save it. QA-only floor and source-bound lights."""
from pathlib import Path
import bpy, json, hashlib, math, sys, runpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['001']
RUN=args[0];wanted=args[1:] or ['waiting_entry','diagnostic_support','admission_connection']
manifest=json.loads((ROOT/'qa'/f'SOURCE_MANIFEST_{RUN}.json').read_text())
source=Path(manifest['source']);sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();before=sha(source)
bpy.ops.wm.open_mainfile(filepath=str(source));scene=bpy.context.scene
if int(RUN)>=3:runpy.run_path(str(ROOT/'source/check_loaded_source_fit.py'))
scene.render.engine='BLENDER_EEVEE_NEXT';scene.render.resolution_x=1280;scene.render.resolution_y=720;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
scene.render.threads_mode='FIXED';scene.render.threads=2
scene.world=bpy.data.worlds.new('Source-only low ambient');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.19,.22,.24,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.15
scene.view_settings.view_transform='AgX';scene.view_settings.exposure=.65
floor_mat=bpy.data.materials.get('warm_stone')
for name,x0,x1,y0,y1 in [('rooms',-14,14,-4,4),('admission',14,20,-17,4)]:
    bpy.ops.mesh.primitive_cube_add(size=1,location=((x0+x1)/2,(y0+y1)/2,-.06));ob=bpy.context.object;ob.name='QA_ONLY_compiler_floor_'+name;ob.dimensions=(x1-x0,y1-y0,.12);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);ob.data.materials.append(floor_mat)
    uv=ob.data.uv_layers.active
    for face in ob.data.polygons:
        for li in face.loop_indices:
            p=ob.data.vertices[ob.data.loops[li].vertex_index].co;uv.data[li].uv=(p.x/2,p.y/2)
for f in manifest['fixture_sources']:
    data=bpy.data.lights.new('QA_Light_from_'+f['name'],'AREA');data.energy=f['energy'];data.shape='DISK';data.size=f['size'];data.color=(1,.90,.75) if 'SUPPORT' not in f['name'] else (.86,.96,1)
    ob=bpy.data.objects.new(data.name,data);scene.collection.objects.link(ob);ob.location=f['source_exit'];ob.rotation_euler=(Vector(f['aim'])-ob.location).to_track_quat('-Z','Y').to_euler()
views={
    'waiting_entry':((13.25,0,1.65),(5.2,.8,1.5),20),
    'diagnostic_support':((-1.15,-2.55,1.65),(-8.2,1.25,1.55),20),
    'admission_connection':((18.5,-14,1.65),(16.65,-1,1.7),22),
}
records=[]
for name in wanted:
    eye,target,lens=views[name];data=bpy.data.cameras.new('QA_'+name);cam=bpy.data.objects.new(data.name,data);scene.collection.objects.link(cam);cam.location=eye;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();data.lens=lens;scene.camera=cam
    destination=ROOT/'renders'/f'{RUN}_{name}_source_only.png';assert not destination.exists(),'Preserve previous views';scene.render.filepath=str(destination);bpy.ops.render.render(write_still=True)
    records.append({'name':name,'path':str(destination),'sha256':sha(destination),'camera_source_eye':eye,'camera_source_target':target,'lens_mm':lens,'standing_eye_m':1.65,'source_only':True,'qa_floor_not_in_source':True,'illumination':'Every local light is bound to a named modeled lens/sconce in SOURCE_MANIFEST; no directional sun or unmodeled fill.'})
    (ROOT/'qa'/f'RENDER_RECEIPT_{RUN}_{wanted[0]}.json').write_text(json.dumps({'source':str(source),'source_before':before,'source_after':sha(source),'unchanged':sha(source)==before,'views':records,'limits':'Blender source inspection, no Godot, runtime collision, CRT or target-GPU acceptance.'},indent=2)+'\n')
    print('VIEW_READY',destination,flush=True)
assert sha(source)==before
