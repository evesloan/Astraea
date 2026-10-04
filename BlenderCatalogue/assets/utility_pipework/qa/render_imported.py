"""Render only re-imported final GLBs. EEVEE_NEXT; no denoiser.
Run -- --preflight before asking lead to reserve heavy render slot.
"""
import bpy,math,json,hashlib,sys,importlib.util
from pathlib import Path
from mathutils import Vector,Matrix
BASE=Path(__file__).resolve().parents[1];CAT=BASE.parents[1]
s=importlib.util.spec_from_file_location('qa_frame',CAT/'standards/qa_frame.py');q=importlib.util.module_from_spec(s);s.loader.exec_module(q)
PREFLIGHT='--preflight' in sys.argv
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
def mat(name,c):
    m=bpy.data.materials.new(name);m.diffuse_color=(*c,1);m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*c,1);m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.8;return m
def import_at(ident,offset,yaw=0):
    prior=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(BASE/'exports'/f'{ident}.glb'));allnew=[o for o in bpy.data.objects if o not in prior]
    trans=Matrix.Translation(Vector(offset))@Matrix.Rotation(math.radians(yaw),4,'Z')
    for o in allnew:
        if o.parent not in allnew:o.matrix_world=trans@o.matrix_world
    return [o for o in allnew if o.type=='MESH']
def stand(x,y,top,qa_material):
    for name,c,d in [('base',(x,y,.014),(.22,.25,.028)),('post',(x,y,top/2),(.045,.055,top)),('saddle',(x,y,top-.015),(.11,.16,.03))]:
        bpy.ops.mesh.primitive_cube_add(size=1,location=c);o=bpy.context.object;o.name='QA_ONLY_stand_'+name;o.scale=d;o.data.materials.append(qa_material)
        mod=o.modifiers.new('QA bevel','BEVEL');mod.width=.008;mod.segments=2
def stage():
    sc=bpy.context.scene;sc.render.engine='BLENDER_EEVEE_NEXT';sc.eevee.taa_render_samples=32;sc.cycles.use_denoising=False;sc.render.threads_mode='FIXED';sc.render.threads=2;sc.render.resolution_percentage=100
    sc.view_settings.view_transform='AgX';sc.view_settings.look='AgX - Medium High Contrast';sc.view_settings.exposure=-.7
    sc.world=bpy.data.worlds.new('QA_ONLY_world');sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.22,.27,.31,1);sc.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.6
    bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.003));bpy.context.object.name='QA_ONLY_floor';bpy.context.object.data.materials.append(mat('QA_ONLY_floor',(.19,.22,.24)))
    for name,pos,power,size in [('key',(-1.3,-3,4.5),1000,3.5),('fill',(3,-1,2.6),650,3),('rim',(.6,3,3.8),1100,3)]:
        data=bpy.data.lights.new('QA_ONLY_'+name,'AREA');ob=bpy.data.objects.new(data.name,data);bpy.context.collection.objects.link(ob);ob.location=pos;data.energy=power;data.shape='DISK';data.size=size;aim(ob,(.3,.2,.9))
    data=bpy.data.cameras.new('QA_ONLY_camera');ob=bpy.data.objects.new(data.name,data);bpy.context.collection.objects.link(ob);sc.camera=ob;data.clip_start=.01;data.clip_end=250;return ob
def main():
    evidence={'scope':'Re-imported GLB component inspection only; QA floor, stands, cameras and lights are absent from exports; no new room or engine implementation','engine':'BLENDER_EEVEE_NEXT','samples':32,'denoiser':False,'source_hashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((BASE/'exports').glob('*.glb'))},'views':{}}
    for code in('004','005','006','assembly'):
        bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);objects=[]
        if code=='assembly':
            for row in json.loads((BASE/'port_and_seam_api.json').read_text())['source_inspection_assembly']:objects+=import_at(row['id'],row['translation_m'],row['rotation_degrees'])
        else:objects=import_at('AST-ENG-'+code,(0,0,.8))
        cam=stage();sc=bpy.context.scene;sm=mat('QA_ONLY_stand',(.12,.15,.17))
        if code=='004':stand(.25,0,.699,sm);stand(.56,0,.699,sm)
        elif code=='005':stand(.22,.015,.698,sm);stand(.566,.44,.698,sm)
        elif code=='006':stand(.325,0,.636,sm)
        else:stand(-.4,0,.649,sm);stand(.50,.75,.586,sm)
        if code=='004':plans={'standing640':{'loc':(-.75,-1.75,1.65),'target':(.40,0,.81),'lens':52,'res':(640,360)},'bore_detail':{'loc':(-1,-.48,1.04),'target':(.11,0,.80),'ortho':.52,'res':(1024,768),'full':False}}
        elif code=='005':plans={'standing640':{'loc':(-1.15,-1.6,1.65),'target':(.3,.23,.81),'lens':49,'res':(640,360)},'bend_detail':{'loc':(-.63,-.63,1.75),'target':(.28,.23,.8),'ortho':1.48,'res':(1024,768)}}
        elif code=='006':plans={'standing640':{'loc':(-.8,-1.75,1.65),'target':(.325,0,.955),'lens':44,'res':(640,360)},'wheel_bonnet_detail':{'loc':(-.34,-.67,1.54),'target':(.325,0,1.095),'ortho':.83,'res':(1024,768),'full':False}}
        else:plans={'assembly':{'loc':(-2.2,-3.1,2.2),'target':(-.01,.36,.9),'lens':48,'res':(1280,960)},'joint_detail':{'loc':(-.40,-.45,1.05),'target':(0,0,.75),'ortho':.55,'res':(1024,768),'full':False}}
        for name,p in plans.items():
            cam.location=p['loc'];aim(cam,p['target']);cam.data.type='ORTHO' if'ortho'in p else'PERSP';cam.data.ortho_scale=p.get('ortho',2);cam.data.lens=p.get('lens',50);sc.render.resolution_x,sc.render.resolution_y=p['res'];bpy.context.view_layer.update()
            report=q.frame_report(sc,cam,objects,margin=.025)
            full=p.get('full',True)
            if full and not report['passes']:raise RuntimeError(f'{code}_{name} failed camera preflight {report}')
            filename=f'{code}_{name}.png';evidence['views'][filename]={'camera_blender_source_world':p,'frame_check':report,'full_extent_required':full,'asset_pose':'Open valve geometry where visible; wheel at zero rotation','path':'renders/'+filename}
            if not PREFLIGHT:sc.render.filepath=str(BASE/'renders'/filename);sc.render.image_settings.file_format='PNG';bpy.ops.render.render(write_still=True)
    (BASE/'qa'/('camera_preflight.json' if PREFLIGHT else'render_evidence.json')).write_text(json.dumps(evidence,indent=2)+'\n');print('PIPEWORK_PREFLIGHT_PASS' if PREFLIGHT else'PIPEWORK_RENDER_COMPLETE')
if __name__=='__main__':main()
