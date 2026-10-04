"""Actual GLB component inspection. Existing plants are disclosed QA-only context.
No runtime shader, room layout acceptance, player-fit or operational door claim.
"""
import bpy,math,json,hashlib,sys,importlib.util
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parents[1];CAT=BASE.parents[1]
s=importlib.util.spec_from_file_location('qa_frame',CAT/'standards/qa_frame.py');q=importlib.util.module_from_spec(s);s.loader.exec_module(q)
PREFLIGHT='--preflight'in sys.argv;ONLY=sys.argv[sys.argv.index('--only')+1]if'--only'in sys.argv else None
plans={
'004_standing_640':{'id':'AST-SAL-004','location':[3.9,-6.2,1.65],'target':[0,.74,.70],'res':[640,360],'lens':44,'full':True,'plants':True,'purpose':'Standing1.65m: useful low open seat and supported planted edge; existing botanical components are QA context'},
'004_junction_detail_1280':{'id':'AST-SAL-004','location':[3.4,-3.7,2.8],'target':[.18,.8,.51],'res':[1280,960],'ortho':3.10,'full':False,'plants':True,'purpose':'Close construction of supported seat, planting wall/cap, shaped rising end and actual soil contacts'},
'005_standing_640':{'id':'AST-SAL-005','location':[3.0,-4.8,1.65],'target':[0,.24,.58],'res':[640,360],'lens':46,'full':True,'purpose':'Standing1.65m: substantial continuous top, floor support and explicitly EMPTY infill fields; incomplete guard component'},
'005_profile_detail_1280':{'id':'AST-SAL-005','location':[2.8,-2.3,1.95],'target':[.79,.24,.79],'res':[1280,960],'ortho':1.70,'full':False,'purpose':'Portal-end physical plate, continuous top/wood contact and genuine infill recess; absence of panel is intentional'},
'006_guest_standing_640':{'id':'AST-SAL-006','location':[3.8,-5.4,1.65],'target':[0,.60,1.17],'res':[640,360],'lens':44,'full':True,'purpose':'Standing1.65m guest side: recessed vertical fields, tactile ledge and visible turned service return'},
'006_service_standing_640':{'id':'AST-SAL-006','location':[-4.6,6.9,1.65],'target':[0,.60,1.17],'res':[640,360],'lens':43,'full':True,'purpose':'Standing1.65m service side: useful reachable open shelves, supports, fixed corner and real open approach'},
}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def aim(ob,p):ob.rotation_euler=(Vector(p)-ob.location).to_track_quat('-Z','Y').to_euler()
def mat(name,c):
 m=bpy.data.materials.new(name);m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*c,1);m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.82;return m
def stage():
 sc=bpy.context.scene;sc.render.engine='BLENDER_EEVEE_NEXT';sc.eevee.taa_render_samples=48;sc.render.threads_mode='FIXED';sc.render.threads=3;sc.render.resolution_percentage=100;sc.view_settings.view_transform='AgX';sc.view_settings.look='AgX - Medium High Contrast';sc.view_settings.exposure=-.2
 sc.world=bpy.data.worlds.new('QA_ONLY_neutral_world');sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.27,.29,.30,1);sc.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.55
 bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.004));bpy.context.object.name='QA_ONLY_floor';bpy.context.object.data.materials.append(mat('QA_ONLY_neutral_floor',(.28,.29,.30)))
 for name,loc,power,size in [('key',(-3,-4,6),1400,4),('fill',(4,-1,4),900,3),('rear',(-2,4,5),1200,4)]:
  data=bpy.data.lights.new('QA_ONLY_'+name,'AREA');ob=bpy.data.objects.new(data.name,data);bpy.context.collection.objects.link(ob);ob.location=loc;data.energy=power;data.shape='DISK';data.size=size;aim(ob,(0,.6,.9))
 data=bpy.data.cameras.new('QA_ONLY_camera');ob=bpy.data.objects.new(data.name,data);bpy.context.collection.objects.link(ob);sc.camera=ob;data.clip_start=.01;data.clip_end=250;return ob
report={'scope':'Actual native GLBs imported into neutral Blender component QA. New adjustable components only; no recovered host, completed guard, real door dimensions, runtime shader, engine lighting or installed-room acceptance.','views':{}}
if ONLY and(BASE/'qa/render_evidence.json').exists()and not PREFLIGHT:report['views']=json.loads((BASE/'qa/render_evidence.json').read_text())['views']
for name,p in plans.items():
 if ONLY and ONLY not in(name,p['id']):continue
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 path=BASE/'exports'/f"{p['id']}.glb";bpy.ops.import_scene.gltf(filepath=str(path));asset=list(bpy.context.scene.objects);context=[]
 if p.get('plants'):
  for ident,pos in [('AST-BOT-002',[.43,1.18,.62]),('AST-BOT-003',[-.84,1.18,.62])]:
   before=set(bpy.context.scene.objects);cp=CAT/'assets/botanical_understory/exports'/f'{ident}.glb';bpy.ops.import_scene.gltf(filepath=str(cp));obs=[o for o in bpy.context.scene.objects if o not in before]
   for ob in obs:
    if ob.parent is None:ob.location=pos;ob['QA_ONLY_existing_context']=ident
   asset.extend(obs);context.append({'catalogue_id':ident,'path_from_catalogue_root':str(cp.relative_to(CAT)),'sha256':sha(cp),'placement_source_m':pos,'root_contact_z_m':.62,'new_asset':False,'production_source_dependency':False})
 bpy.context.view_layer.update();obs=[o for o in asset if o.type=='MESH'];cam=stage();sc=bpy.context.scene;cam.location=p['location'];aim(cam,p['target']);cam.data.type='ORTHO'if'ortho'in p else'PERSP';cam.data.ortho_scale=p.get('ortho',3);cam.data.lens=p.get('lens',44);sc.render.resolution_x,sc.render.resolution_y=p['res'];fr=q.frame_report(sc,cam,obs,margin=.045)
 if p['full']and not fr['passes']:raise RuntimeError(name+' framing failed '+str(fr))
 report['views'][name]={'camera':p,'framing':fr,'intentional_detail_crop':not p['full'],'source_sha256_at_capture':sha(BASE/'source'/f"{p['id']}.blend"),'glb_sha256':sha(path),'context':context}
 if not PREFLIGHT:sc.render.filepath=str(BASE/'qa'/f'{name}.png');sc.render.image_settings.file_format='PNG';bpy.ops.render.render(write_still=True)
(BASE/'qa'/('camera_preflight.json'if PREFLIGHT else'render_evidence.json')).write_text(json.dumps(report,indent=2)+'\n');print('PREFLIGHT_PASS'if PREFLIGHT else'RENDER_PASS')
