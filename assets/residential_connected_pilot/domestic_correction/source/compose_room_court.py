"""Compose corrected real suite sources with their authored court source.

Source-only views; never a replacement game scene or a simulated backdrop.
"""
from pathlib import Path
import bpy,json,math,sys,argparse,hashlib
from mathutils import Matrix,Vector
ROOT=Path(__file__).resolve().parents[1];BATCH=ROOT.parent
p=argparse.ArgumentParser();p.add_argument('--court-blend',required=True);p.add_argument('--revision',default='room_court_r001');p.add_argument('--view',default='through_window');args=p.parse_args(sys.argv[sys.argv.index('--')+1:])
court=Path(args.court_blend);assert court.is_file();OUT=ROOT/'outputs'/args.revision;OUT.mkdir(exist_ok=True)
source=OUT/'room_and_court.blend'
plan=json.loads((BATCH/'COURT_PILOT_PLAN.json').read_text());inputs={'court':{'path':str(court),'sha256':hashlib.sha256(court.read_bytes()).hexdigest()},'rooms':[]}
if not source.exists():
    bpy.ops.wm.open_mainfile(filepath=str(court))
    # Court owns its actual authored fixtures and source lights. Keep them.
    for cfg in plan['rooms']:
        path=BATCH/'outputs/court_domestic_r008'/cfg['address']/'assembly.blend';inputs['rooms'].append({'path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
        with bpy.data.libraries.load(str(path),link=False)as(fr,to):to.objects=list(fr.objects)
        loaded=[o for o in to.objects if o is not None and o.type in ['MESH','EMPTY','CURVE']]
        ox,oy,oz=cfg['source_origin_world_xyz'];T=Matrix.Translation((ox,-oz,oy))@Matrix.Rotation(cfg['source_yaw_godot'],4,'Z');mapping={}
        for ob in loaded:
            bpy.context.collection.objects.link(ob)
        bpy.context.view_layer.update()
        original_roots={ob:ob.matrix_world.copy() for ob in loaded if ob.parent is None}
        for ob in loaded:
            name=ob.name
            if ob.parent is None:ob.matrix_world=T@original_roots[ob]
            ob.name='U'+str(cfg['census_source_index'])+'__'+name;ob['suite_identity']=cfg['rebuild_identity'];mapping[name]=ob
        bpy.context.view_layer.update()
        for ob,original in original_roots.items():
            expected=T@original
            assert max(abs(ob.matrix_world[i][j]-expected[i][j])for i in range(4)for j in range(4))<.0001,'Composite root transform drift'
        for anchor in cfg['bed_anchors']:
            name='DATUM_bed_'+str(anchor['historical_anchor_index']);marker=next(ob for key,ob in mapping.items()if key==name or key.startswith(name+'.'))
            expected=Vector((anchor['world_xyz'][0],-anchor['world_xyz'][2],anchor['world_xyz'][1]))
            assert (marker.matrix_world.translation-expected).length<.0001,'Composite rest marker misplaced'
        for name,ob in mapping.items():
            if ob.type!='EMPTY' or 'light'not in name:continue
            if not(name.startswith('DATUM_')or name.startswith('SuiteKitchenette__DATUM_')):continue
            bedside='bed_light' in name;power=12 if bedside else (25 if 'bath' in name else (12 if 'task' in name else 95))
            data=bpy.data.lights.new('U'+str(cfg['census_source_index'])+'_Fixture_'+name,'POINT' if bedside else 'AREA');data.energy=power;data.color=(1.0,.86,.68)
            light=bpy.data.objects.new(data.name,data);bpy.context.collection.objects.link(light);light.location=ob.matrix_world.translation
            if bedside:data.shadow_soft_size=.05
            else:data.shape='RECTANGLE';data.size=.35;data.size_y=.22
            light['source_fixture_marker']=ob.name;light['scope']='Source-preview radiometric translation at actual modelled fixture; not Godot acceptance'
    bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(source))
    (OUT/'COMPOSITION_INPUTS.json').write_text(json.dumps({'source_inputs':inputs,'court_transform':'identity; globalBlenderX,-worldZ,worldY','room_transforms':[{k:c[k]for k in ['address','source_origin_world_xyz','source_yaw_godot','view_target_id']}for c in plan['rooms']],
     'root_transform_and_bed_position_checks_passed':True,'source_objects_evaluated_before_transform':True,
     'scope':'Source-only connected room and proposed authored garden; no Game adoption, structural certification or complete500-room view acceptance'},indent=2)+'\n')
else:bpy.ops.wm.open_mainfile(filepath=str(source))
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=False;scene.render.threads_mode='FIXED';scene.render.threads=2
scene.render.resolution_x=1100;scene.render.resolution_y=740;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='AgX';scene.view_settings.exposure=1.2
if not scene.world:scene.world=bpy.data.worlds.new('CourtSourceWorld')
scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.15,.17,.18,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.06
pilot=next(c for c in plan['rooms']if c['census_source_index']==205);ox,oy,oz=pilot['source_origin_world_xyz'];T=Matrix.Translation((ox,-oz,oy))@Matrix.Rotation(pilot['source_yaw_godot'],4,'Z')
views={'through_window':((-.05,8.08,1.58),(.1,18.5,.9),23),
 'window_approach':((.2,11.40,1.65),(0,24,-1.25),24),
 'entry_kitchen_bath':((.45,7.20,1.65),(.8,1.0,1.12),25),
 'bathroom_interior':((-2.15,3.52,1.60),(-2.0,.7,.88),23)}
assert args.view in views;pos,target,lens=views[args.view];pos=T@Vector(pos);target=T@Vector(target)
data=bpy.data.cameras.new('Review_'+args.view);camera=bpy.data.objects.new(data.name,data);bpy.context.collection.objects.link(camera);camera.location=pos;camera.rotation_euler=(target-pos).to_track_quat('-Z','Y').to_euler();data.lens=lens;scene.camera=camera
scene.render.filepath=str(OUT/(args.view+'.png'));bpy.ops.render.render(write_still=True)
(OUT/(args.view+'_receipt.json')).write_text(json.dumps({'view':args.view,'source_composition_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'source_camera_xyz':list(pos),'source_target_xyz':list(target),'source_only':True,'hidden_geometry':False,'actual_fixture_marker_lights':True,'no_invented_space_background':True,'proposed_court_not_installed':True},indent=2)+'\n')
print('CONNECTED_SUITE_COURT_VIEW_READY',scene.render.filepath,flush=True)
