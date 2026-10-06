"""Bounded two-thread Blender source review; images are not runtime evidence."""
from pathlib import Path
import argparse,sys,json,hashlib,math
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--revision',default='r002');p.add_argument('--addresses',nargs='*');p.add_argument('--plan',default='NEIGHBORHOOD_PLAN.json');a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
plan=json.loads((ROOT/a.plan).read_text());addresses=a.addresses or plan['representative_sample_addresses']
for address in addresses:
    dest=ROOT/'outputs'/a.revision/address;source=dest/'assembly.blend';before=hashlib.sha256(source.read_bytes()).hexdigest()
    bpy.ops.wm.open_mainfile(filepath=str(source));scene=bpy.context.scene
    scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=False
    scene.render.resolution_x=960;scene.render.resolution_y=640;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='AgX'
    scene.render.threads_mode='FIXED';scene.render.threads=2
    world=bpy.data.worlds.new('SourceReviewNeutralWorld');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.13,.16,.18,1);world.node_tree.nodes['Background'].inputs[1].default_value=.25;scene.world=world
    # Neutral source-review lights expose the real authored shell and furniture.
    # They are deliberately not exported or claimed as production fixture lights.
    for j,(point,power,size) in enumerate([((0,3.9,2.8),360,3),((0,7.0,3.1),470,3),((0,11.8,3.35),260,2)]):
        d=bpy.data.lights.new('QA_area_'+str(j),'AREA');d.energy=power;d.shape='DISK';d.size=size;o=bpy.data.objects.new(d.name,d);bpy.context.collection.objects.link(o);o.location=point
    views=[('entry_eye',(0,1.9,1.65),(-.05,9.3,1.50),None),('plan_cutaway',(0,6.45,24),(0,6.45,0),22.0)]
    for name,point,target,ortho in views:
        hidden=[]
        if ortho:
            for o in scene.objects:
                if o.type=='MESH' and any(o.name.startswith(s) for s in ['SUI_Ceiling','SUI_BathCeiling','SUI_SleepingValance','SUI_GatheringFoldedFascia','SUI_RetreatVault_','SUI_CocoonAcousticPetal_','SUI_FamilySideBerthCanopy']):o.hide_render=True;hidden.append(o)
            d=bpy.data.lights.new('QA_cutaway','AREA');d.energy=900;d.size=9;o=bpy.data.objects.new(d.name,d);bpy.context.collection.objects.link(o);o.location=(0,6.5,10)
        d=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,d);bpy.context.collection.objects.link(o);o.location=point;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();d.lens=22
        if ortho:d.type='ORTHO';d.ortho_scale=ortho
        scene.camera=o;scene.render.filepath=str(dest/(name+'.png'));bpy.ops.render.render(write_still=True)
        for o in hidden:o.hide_render=False
    assert hashlib.sha256(source.read_bytes()).hexdigest()==before
    (dest/'VISUAL_SOURCE_RECEIPT.json').write_text(json.dumps({'source_sha256':before,'source_unchanged':True,'views':[v[0] for v in views],
      'render':'Blender Cycles 32 samples, no unavailable denoiser, neutral source-only review lights','runtime_evidence':False,
      'cutaway_hidden_parts':'Ceiling surfaces, sleeping fascia, cocoon canopy and retreat canopy only for top-down inspection; entry view hides nothing'},indent=2)+'\n')
    print('SOURCE_VISUAL_COMPLETE',address,flush=True)
