"""Final imported-GLB component-only evidence. Preflight does not render.
blender -b -t 2 --python qa/render_imported.py -- --preflight
blender -b -t 4 --python qa/render_imported.py -- --views silhouette,standing,joint,fixture
"""
import bpy,math,json,hashlib,sys,importlib.util
from pathlib import Path
from mathutils import Vector,Matrix
BASE=Path(__file__).resolve().parents[1];CAT=BASE.parents[1]
spec=importlib.util.spec_from_file_location('qa_frame',CAT/'standards/qa_frame.py');q=importlib.util.module_from_spec(spec);spec.loader.exec_module(q)
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else[]
preflight='--preflight' in args
views=args[args.index('--views')+1].split(',') if '--views' in args else['silhouette','standing','joint','fixture','service_bay']

def aim(ob,target):ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler()
def import_glb(path):
    old=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(path));return[o for o in bpy.data.objects if o not in old and o.type=='MESH']
def material(name,col,rough=.8):
    m=bpy.data.materials.new(name);m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*col,1);m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=rough;return m

def stage():
    sc=bpy.context.scene;sc.render.engine='BLENDER_EEVEE_NEXT';sc.eevee.taa_render_samples=48;sc.cycles.use_denoising=False;sc.render.threads_mode='FIXED';sc.render.threads=4
    sc.render.resolution_percentage=100;sc.view_settings.view_transform='AgX';sc.view_settings.look='AgX - Medium High Contrast';sc.view_settings.exposure=-1.3;sc.world=bpy.data.worlds.new('QA_ONLY_neutral_world');sc.world.use_nodes=True
    sc.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.23,.28,.32,1);sc.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.6
    bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.006));bpy.context.object.name='QA_ONLY_floor';bpy.context.object.data.materials.append(material('QA_ONLY_floor',(.20,.23,.24)))
    for name,loc,power,size in [('key',(-2,-4,6.6),1300,5),('fill',(3,-1,2.8),900,4),('rim',(0,4,5.5),1300,3),('under',(-1,-1,1),300,3)]:
        data=bpy.data.lights.new('QA_ONLY_'+name,'AREA');ob=bpy.data.objects.new(data.name,data);bpy.context.collection.objects.link(ob);ob.location=loc;data.energy=power;data.shape='DISK';data.size=size;aim(ob,(0,.3,2.95))
    data=bpy.data.cameras.new('QA_ONLY_camera');ob=bpy.data.objects.new(data.name,data);bpy.context.collection.objects.link(ob);sc.camera=ob;data.clip_start=.01;data.clip_end=250
    return ob

def main():
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    api=json.loads((BASE/'mounting_api.json').read_text());objects=[];instances={}
    for row in api['inspection_assembly']:
        m=Matrix.Translation(Vector(row['translation_m']))@Matrix.Rotation(math.radians(row['rotation_z_degrees']),4,'Z');group=import_glb(BASE/'exports'/f"{row['id']}.glb")
        for ob in group:ob.matrix_world=m@ob.matrix_world;ob.name=row['instance']+'__'+ob.name
        objects+=group;instances[row['instance']]=group
    own_objects=list(objects);context_objects=[];context_files={};context_placements=[];context_bounds={}
    context_rows=[
      ('wall_corner','staff_wall/AST-STF-002.glb',(-1.5,2.6,0),0),
      ('back_wall_A','staff_wall/AST-STF-001.glb',(-1.2,2.6,0),0),
      ('back_wall_B','staff_wall/AST-STF-001.glb',(0,2.6,0),0),
      ('back_terminal','staff_wall/AST-STF-003.glb',(1.2,2.6,0),0),
      ('side_wall_A','staff_wall/AST-STF-001.glb',(-1.5,1.1,0),90),
      ('side_wall_B','staff_wall/AST-STF-001.glb',(-1.5,-.1,0),90),
      ('closed_cabinet','staff_workbay/AST-STF-007_supply_work_cabinet.glb',(0,2.15,0),0)]
    for label,relative,loc,yaw in context_rows:
        path=BASE.parent/relative;group=import_glb(path);m=Matrix.Translation(Vector(loc))@Matrix.Rotation(math.radians(yaw),4,'Z')
        for ob in group:ob.matrix_world=m@ob.matrix_world;ob.name='QA_CONTEXT_'+label+'__'+ob.name
        bpy.context.view_layer.update()
        points=[ob.matrix_world@Vector(c) for ob in group for c in ob.bound_box]
        context_bounds[label]={'min_m':[min(v[k] for v in points) for k in range(3)],'max_m':[max(v[k] for v in points) for k in range(3)]}
        context_objects+=group;context_files[relative]=hashlib.sha256(path.read_bytes()).hexdigest();context_placements.append({'instance':label,'glb':relative,'translation_m':list(loc),'rotation_z_degrees':yaw,'pose':'closed exported default' if label=='closed_cabinet' else'fixed component'})
    cam=stage();sc=bpy.context.scene
    bpy.ops.mesh.primitive_plane_add(size=1,location=(-.35,.175,.0008));aisle=bpy.context.object;aisle.name='QA_ONLY_clear_aisle_floor_marker';aisle.scale=(1.8,2.65,1);aisle.data.materials.append(material('QA_ONLY_aisle_marker',(.11,.20,.23)));context_aids=[aisle]
    # A narrow wire outline declares the sample mounting plane without inventing a room ceiling.
    datum_mat=material('QA_ONLY_mounting_datum',(.23,.30,.31))
    for label,loc,dims in [('datum_front',(-.10,-1.10,3.304),(2.70,.012,.008)),('datum_back',(-.10,2.18,3.304),(2.70,.012,.008)),('datum_left',(-1.45,.54,3.304),(.012,3.28,.008)),('datum_right',(1.25,.54,3.304),(.012,3.28,.008))]:
        bpy.ops.mesh.primitive_cube_add(size=1,location=loc);ob=bpy.context.object;ob.name='QA_ONLY_'+label;ob.scale=dims;ob.data.materials.append(datum_mat);context_aids.append(ob)
    objects+=context_objects

    plans={
      'service_bay':{'location':(3.8,-5.8,1.65),'target':(-.1,.82,1.65),'res':(1280,960),'lens':45,'full':True,'caption':'Standing component arrangement | 1.8 m marked example aisle; closed cabinet clear of it'},
      'silhouette':{'location':(3.25,-4.5,5.8),'target':(-.04,.42,3.06),'res':(1280,960),'ortho':3.90,'full':True,'caption':'Full silhouette | joined run + 90 degree turn + run; separate guarded fixture'},
      'standing':{'location':(1.65,-3.8,1.65),'target':(-.04,.35,2.87),'res':(640,360),'lens':38,'full':False,'caption':'Camera at 1.65 m | mounting datum 3.30 m; lowest guard 2.6925 m'},
      'joint':{'location':(-.42,-.90,3.86),'target':(-.005,.015,2.96),'res':(1280,960),'ortho':.93,'full':False,'caption':'Entry seam detail | 2 mm rail gap; exterior splice collars + hollow conduit sleeves'},
      'fixture':{'location':(-1.50,-1.98,2.32),'target':(-.60,-.73,2.93),'res':(1280,960),'ortho':1.50,'full':True,'caption':'Fixture underside | formed housing, lens, reflector, guard and two ceiling drops'}}
    evidence={'scope':'Blender imported GLB component inspection only. No ship room, gameplay, real route headroom, physical load or electrical-function claim. All scene lights are QA aids and absent from export.','source_hashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((BASE/'exports').glob('*.glb'))},'mounting_datum_world_z_m':3.3,'minimum_hanging_geometry_world_z_m':api['clearance_example']['lowest_fixture_world_z_m'],'fixture_light_function':'None; opal material is non-emissive','qa_exposure_stops':-1.3,'context_glb_hashes':context_files,'context_placements':context_placements,'context_measured_world_bounds':context_bounds,'service_bay_clearances':{'cabinet_back_to_wall_bumper_m':.02,'cabinet_front_to_marked_aisle_m':.295,'side_wall_to_marked_aisle_m':.13,'aisle_min_world_m':[-1.25,-1.15,0],'aisle_max_world_m':[.55,1.5,2.65],'aisle_width_m':1.8,'aisle_length_m':2.65,'lowest_overhead_to_prism_top_m':.0425000429,'mounting_datum_outline_bottom_world_z_m':3.3,'scope':'QA-only component arrangement and open clearance prism; no complete room, ship route, cabinet-open access or cart turning acceptance'},'views':{}}
    clear=evidence['service_bay_clearances'];clear['cabinet_back_to_wall_bumper_m']=context_bounds['back_wall_A']['min_m'][1]-context_bounds['closed_cabinet']['max_m'][1];clear['cabinet_front_to_marked_aisle_m']=context_bounds['closed_cabinet']['min_m'][1]-1.5;clear['side_wall_to_marked_aisle_m']=-1.25-context_bounds['side_wall_A']['max_m'][0]
    clear['bounds_clear_of_aisle_prism']=all(any(b['max_m'][k]<=clear['aisle_min_world_m'][k] or b['min_m'][k]>=clear['aisle_max_world_m'][k] for k in range(3)) for b in context_bounds.values())
    if not clear['bounds_clear_of_aisle_prism'] or min(clear['cabinet_back_to_wall_bumper_m'],clear['cabinet_front_to_marked_aisle_m'],clear['side_wall_to_marked_aisle_m'])<0:raise RuntimeError('Shared arrangement failed measured clearance')
    for name in views:
        plan=plans[name]
        for ob in own_objects:ob.hide_render=(name=='fixture' and ob not in instances['adjacent_fixture'])
        for ob in context_objects+context_aids:ob.hide_render=name!='service_bay'
        cam.location=plan['location'];aim(cam,plan['target']);cam.data.type='ORTHO' if'ortho'in plan else'PERSP';cam.data.ortho_scale=plan.get('ortho',3);cam.data.lens=plan.get('lens',48);sc.render.resolution_x,sc.render.resolution_y=plan['res']
        component=[o for o in objects if not o.hide_render];frame=q.frame_report(sc,cam,component,margin=.035)
        if plan['full'] and not frame['passes']:raise RuntimeError(name+' framing failed '+str(frame))
        evidence['views'][name]={'camera':plan,'framing':frame,'full_component_silhouette_required':plan['full'],'cropping':'None permitted' if plan['full'] else'Close/eye-height crop allowed; see full silhouette for complete extent'}
        if not preflight:
            sc.render.filepath=str(BASE/'qa'/f'{name}_raw.png');sc.render.image_settings.file_format='PNG';bpy.ops.render.render(write_still=True)
    filename='camera_preflight.json' if preflight else'render_evidence.json';(BASE/'qa'/filename).write_text(json.dumps(evidence,indent=2)+'\n');print('PREFLIGHT_PASS' if preflight else'RENDER_COMPLETE',views)
if __name__=='__main__':main()
