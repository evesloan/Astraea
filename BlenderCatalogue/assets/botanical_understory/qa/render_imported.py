"""Actual GLB render proof; no source geometry is used for the evidence.
Run with -- --preflight for lightweight framing only, or -- --views a,b.
"""
import bpy,math,json,hashlib,sys,importlib.util
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parents[1];CAT=BASE.parents[1]
spec=importlib.util.spec_from_file_location('qa_frame',CAT/'standards/qa_frame.py');qa=importlib.util.module_from_spec(spec);spec.loader.exec_module(qa)
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else[];preflight='--preflight' in args
views=args[args.index('--views')+1].split(',') if '--views' in args else['understory','rosette','standing_pair','leaf_flower_detail']

def aim(o,t):o.rotation_euler=(Vector(t)-o.location).to_track_quat('-Z','Y').to_euler()
def material(name,rgb):
    m=bpy.data.materials.new(name);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*rgb,1);bs.inputs['Roughness'].default_value=.83;return m

def stage():
    s=bpy.context.scene;s.render.engine='BLENDER_EEVEE_NEXT';s.eevee.taa_render_samples=40;s.cycles.use_denoising=False;s.render.resolution_percentage=100;s.render.threads_mode='FIXED';s.render.threads=4
    s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=-.4
    w=bpy.data.worlds.new('QA_ONLY_neutral_world');w.use_nodes=True;w.node_tree.nodes['Background'].inputs['Color'].default_value=(.28,.33,.35,1);w.node_tree.nodes['Background'].inputs['Strength'].default_value=.65;s.world=w
    bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.002));bpy.context.object.name='QA_ONLY_neutral_soil_datum';bpy.context.object.data.materials.append(material('QA_ONLY_neutral_ground',(.24,.255,.26)))
    for name,xyz,energy,size in [('key',(-3,-4,5),800,4),('fill',(4,-2,2.7),500,3.5),('rim',(1,3,4),950,3)]:
        d=bpy.data.lights.new('QA_ONLY_'+name,'AREA');o=bpy.data.objects.new(d.name,d);bpy.context.collection.objects.link(o);o.location=xyz;d.energy=energy;d.shape='DISK';d.size=size;aim(o,(0,0,.4))
    d=bpy.data.cameras.new('QA_ONLY_camera');o=bpy.data.objects.new(d.name,d);bpy.context.collection.objects.link(o);d.clip_start=.01;d.clip_end=250;s.camera=o;return o

bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
groups={}
for ident in ['AST-BOT-002','AST-BOT-003']:
    before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(BASE/'exports'/f'{ident}.glb'));groups[ident]=[o for o in bpy.data.objects if o not in before and o.type=='MESH']
cam=stage();sc=bpy.context.scene
plans={
 'understory':{'res':[640,360],'ids':['AST-BOT-002'],'location':[1.6,-2.3,1.45],'target':[0,0,.53],'ortho':2.55,'full':True,'caption':'AST-BOT-002 | 0.926 m above soil | 1,508 tris | opaque cupped leaves'},
 'rosette':{'res':[640,360],'ids':['AST-BOT-003'],'location':[.95,-1.4,.95],'target':[0,0,.15],'ortho':1.25,'full':True,'caption':'AST-BOT-003 | 0.338 m above soil | 1,520 tris | three restrained flowers'},
 'standing_pair':{'res':[640,360],'ids':['AST-BOT-002','AST-BOT-003'],'location':[2.35,-3.4,1.65],'target':[.15,0,.52],'lens':42,'full':True,'caption':'Standing camera 1.65 m | Shared soil datum Z0 | Original component comparison'},
 'leaf_flower_detail':{'res':[1280,960],'ids':['AST-BOT-002','AST-BOT-003'],'location':[1.8,-2.7,1.85],'target':[.15,0,.50],'ortho':2.65,'full':True,'caption':'Detail | Shaped cups, connected petioles, central crown and three flower stems'}}
evidence={'scope':'Blender component QA only; imported final GLBs, independent assets, no native game or ship room evidence','engine':'EEVEE_NEXT','denoising':False,'export_hashes':{i:hashlib.sha256((BASE/'exports'/f'{i}.glb').read_bytes()).hexdigest() for i in groups},'views':{}}
for name in views:
    plan=plans[name];objs=[]
    for ident,parts in groups.items():
        offset=Vector((-.37,0,0)) if ident=='AST-BOT-002' else Vector((.62,-.05,0))
        if len(plan['ids'])==1:offset=Vector((0,0,0))
        for ob in parts:
            ob.hide_render=ident not in plan['ids'];ob.location=offset
            if not ob.hide_render:objs.append(ob)
    cam.location=plan['location'];aim(cam,plan['target']);cam.data.type='ORTHO' if 'ortho' in plan else 'PERSP';cam.data.ortho_scale=plan.get('ortho',2);cam.data.lens=plan.get('lens',48);sc.render.resolution_x,sc.render.resolution_y=plan['res']
    print('PREFLIGHT',name,flush=True);framing=qa.assert_full_frame(sc,cam,objs,margin=.045)
    evidence['views'][name]={'camera':plan,'framing':framing,'imported_glb_objects':[o.name for o in objs]}
    if not preflight:
        sc.render.filepath=str(BASE/'qa'/f'{name}_raw.png');sc.render.image_settings.file_format='PNG';bpy.ops.render.render(write_still=True)
(BASE/'qa'/('camera_preflight.json' if preflight else 'render_evidence.json')).write_text(json.dumps(evidence,indent=2)+'\n')
print('PREFLIGHT_COMPLETE' if preflight else 'RENDER_COMPLETE',views)
