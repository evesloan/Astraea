"""Actual GLB evidence, not editable source renders. Use --preflight first.
Lead serializes heavy EEVEE renders. All lights/floor/cameras are QA only.
"""
from pathlib import Path
import bpy,sys,json,hashlib,math
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[1];CAT=ROOT.parents[1]
sys.path.insert(0,str(CAT/'standards'))
from qa_frame import frame_report
ARGS=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
PREFLIGHT='--preflight' in ARGS
VIEWS=ARGS[ARGS.index('--views')+1].split(',') if '--views' in ARGS else ['family','standing','profile','table_detail','support_detail']

def aim(ob,p):ob.rotation_euler=(Vector(p)-ob.location).to_track_quat('-Z','Y').to_euler()
def material(name,col):
    m=bpy.data.materials.new(name);m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*col,1);m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.8;return m
def import_asset(asset,translation):
    old=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(ROOT/'exports'/f'{asset}.glb'))
    obs=[ob for ob in bpy.data.objects if ob not in old and ob.type=='MESH']
    for ob in obs:ob.matrix_world=Matrix.Translation(Vector(translation))@ob.matrix_world
    return obs

def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc=bpy.context.scene;sc.render.engine='BLENDER_EEVEE_NEXT';sc.eevee.taa_render_samples=48;sc.cycles.use_denoising=False;sc.render.threads_mode='FIXED';sc.render.threads=2
    sc.render.resolution_percentage=100;sc.view_settings.view_transform='AgX';sc.view_settings.look='AgX - Medium High Contrast';sc.view_settings.exposure=-.65
    sc.world=bpy.data.worlds.new('QA_ONLY_neutral_world');sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.27,.30,.32,1);sc.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.5
    groups={'lounger':import_asset('AST-AQU-001',(0,0,0)),'table':import_asset('AST-AQU-002',(.92,-.18,0))}
    bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.004));ob=bpy.context.object;ob.name='QA_ONLY_neutral_floor';ob.data.materials.append(material('QA_ONLY_neutral_floor',(.18,.205,.214)))
    for name,loc,power,size in [('key',(-3,-4,5.5),1000,4.5),('fill',(3,-1,3.5),650,4),('rim',(1,4,5),1000,3)]:
        data=bpy.data.lights.new('QA_ONLY_'+name,'AREA');ob=bpy.data.objects.new(data.name,data);bpy.context.collection.objects.link(ob);ob.location=loc;data.energy=power;data.size=size;aim(ob,(.2,0,.5))
    data=bpy.data.cameras.new('QA_ONLY_camera');cam=bpy.data.objects.new(data.name,data);bpy.context.collection.objects.link(cam);sc.camera=cam;data.clip_start=.01;data.clip_end=250
    plans={
      'family':{'location':(3.1,-4.2,2.9),'target':(.23,.0,.62),'ortho':3.80,'res':(640,360),'groups':['lounger','table'],'full':True,'caption':'Actual imported GLBs | sculpted drained lounger + low tray table'},
      'standing':{'location':(2.4,-3.5,1.65),'target':(.34,-.02,.43),'lens':43,'res':(640,360),'groups':['lounger','table'],'full':True,'caption':'1.65 m camera | clay contact strips, fitted rail/legs, four-point table support'},
      'profile':{'location':(3.8,-1.1,1.25),'target':(0,-.04,.47),'ortho':2.80,'res':(640,360),'groups':['lounger'],'full':True,'caption':'Lounger profile | continuous recline; open underside; four floor grips'},
      'table_detail':{'location':(1.72,-1.40,1.10),'target':(.92,-.18,.235),'ortho':1.20,'res':(960,720),'groups':['table'],'full':True,'caption':'Table detail | 8 mm drain slots, lowered teal channel and interrupted raised rim'},
      'support_detail':{'location':(1.25,-1.18,.84),'target':(.20,-.19,.365),'ortho':1.34,'res':(960,720),'groups':['lounger'],'full':False,'caption':'Lounger joint detail | intersecting rails, cross supports, legs and coated contact panels'}}
    report={'scope':'QA-only imported GLB component studio; not an installed room, game, water or physics test. Floor/lights/cameras absent from sources and exports.','export_hashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'exports').glob('*.glb')},'inspection_placements':[{'id':'AST-AQU-001','translation_m':[0,0,0]},{'id':'AST-AQU-002','translation_m':[.92,-.18,0]}],'views':{}}
    for name in VIEWS:
        p=plans[name]
        for key,obs in groups.items():
            for ob in obs:ob.hide_render=key not in p['groups']
        objects=[o for key in p['groups'] for o in groups[key]]
        cam.location=p['location'];aim(cam,p['target']);data.type='ORTHO' if 'ortho' in p else 'PERSP';data.ortho_scale=p.get('ortho',3);data.lens=p.get('lens',45);sc.render.resolution_x,sc.render.resolution_y=p['res']
        frame=frame_report(sc,cam,objects,.045)
        if p['full'] and not frame['passes']:raise ValueError(name+' framing failed '+str(frame))
        report['views'][name]={'camera':p,'framing':frame,'full_component_silhouette_required':p['full'],'crop':'Detail crop deliberately permitted' if not p['full'] else 'None permitted'}
        if not PREFLIGHT:
            sc.render.filepath=str(ROOT/'qa'/f'{name}_raw.png');sc.render.image_settings.file_format='PNG';bpy.ops.render.render(write_still=True)
    out='camera_preflight.json' if PREFLIGHT else 'render_evidence.json';(ROOT/'qa'/out).write_text(json.dumps(report,indent=2)+'\n');print('PREFLIGHT_PASS' if PREFLIGHT else 'RENDER_COMPLETE',VIEWS)
if __name__=='__main__':main()
