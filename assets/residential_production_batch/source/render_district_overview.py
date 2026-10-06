"""One actual source district cutaway, from the generated mass-placement file."""
from pathlib import Path
import bpy,json,hashlib,math,os
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];revision=os.environ.get('ASTRAEA_PRODUCTION_REVISION','production_r005');folder=ROOT/'outputs'/revision/'sections';source=folder/'Astraea_500_regular_family_portable.blend'
before=hashlib.sha256(source.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(source));scene=bpy.context.scene
district='D16__starboard_central_upper_house'
for col in scene.collection.children:col.hide_render=col.name!=district
hidden=[]
for ob in bpy.data.objects:
    if ob.type=='MESH' and any(ob.name.startswith(s)for s in ['SUI_Ceiling','SUI_BathCeiling','SUI_SleepingValance','SUI_GatheringFoldedFascia','SUI_RetreatVault_','SUI_FamilySideBerthCanopy']):
        ob.hide_render=True;hidden.append(ob.name)
scene.render.engine='CYCLES';scene.cycles.samples=16;scene.cycles.use_denoising=False;scene.render.threads_mode='FIXED';scene.render.threads=2
scene.render.resolution_x=720;scene.render.resolution_y=1560;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='AgX'
world=bpy.data.worlds.new('QA_neutral_source_world');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.16,.19,.22,1);world.node_tree.nodes['Background'].inputs[1].default_value=.6;scene.world=world
d=bpy.data.lights.new('QA_district_sun','SUN');d.energy=2.5;d.angle=.25;o=bpy.data.objects.new(d.name,d);scene.collection.objects.link(o);o.rotation_euler=(.2,-.25,.4)
d=bpy.data.cameras.new('QA_district_overview');o=bpy.data.objects.new(d.name,d);scene.collection.objects.link(o);o.location=(84,3.7,350);o.rotation_euler=(0,0,0);d.type='ORTHO';d.ortho_scale=225;scene.camera=o
scene.render.filepath=str(folder/'D16_starboard_central_33_family_source_cutaway_full.png');bpy.ops.render.render(write_still=True)
assert hashlib.sha256(source.read_bytes()).hexdigest()==before
(folder/'DISTRICT_OVERVIEW_RECEIPT.json').write_text(json.dumps({'scope':'Actual33 family source instances in their D16 allocations. Source-only top-down cutaway; roofs/canopies hidden for inspection.',
 'district':district,'room_instances':33,'source_sha256':before,'source_unchanged':True,'source_file':str(source),'hidden_meshes':hidden,
 'not_shown_or_claimed':['No adopted Game rooms','No surrounding installed commons or street construction','No final light/view/collision acceptance'],'camera_source_xyz':[84,3.7,350],'camera_ortho_vertical_m':225},indent=2)+'\n')
print('DISTRICT_SOURCE_OVERVIEW_COMPLETE',scene.render.filepath,flush=True)
