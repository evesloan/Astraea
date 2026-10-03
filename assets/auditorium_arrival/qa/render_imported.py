"""Four ordinary-height imported 640x360 inspections; QA-only stage, not host geometry."""
from pathlib import Path
import bpy,json,hashlib,sys,math
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
B=Path(__file__).resolve().parents[1];Q=B/'qa';M={x['catalogue_id']:x for x in json.loads((B/'manifest.json').read_text())['assets']}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
VIEWS=[('001_public_standing','AST-CUL-001','closed',(2.6,-4.9,1.60),(0,0,1.13),40),('001_service_access_standing','AST-CUL-001','access',(-2.7,4.8,1.60),(0,.1,1.14),40),('002_public_standing','AST-CUL-002','closed',(2.1,-3.0,1.55),(0,0,.50),44),('002_staff_access_standing','AST-CUL-002','access',(-1.9,3.25,1.55),(0,.15,.57),44)]
onlyid=sys.argv[sys.argv.index('--asset')+1]if '--asset'in sys.argv else None
records=[];pre=[];only=sys.argv[sys.argv.index('--view')+1]if '--view'in sys.argv else None;preflight='--preflight'in sys.argv
for name,ident,state,eye,target,lens in VIEWS:
 if only and name!=only:continue
 if onlyid and ident!=onlyid:continue
 bpy.ops.wm.read_factory_settings(use_empty=True);sc=bpy.context.scene;r=M[ident];src=B/r['source'];exp=B/(r['export']if state=='closed'else r['state_derivatives'][0]['export']);before={'source_sha256':sha(src),'export_sha256':sha(exp),'generator_sha256':sha(B/'source/build_auditorium_arrival.py')}
 bpy.ops.import_scene.gltf(filepath=str(exp));objects=[o for o in sc.objects if o.type=='MESH'];points=[o.matrix_world@v.co for o in objects for v in o.data.vertices]
 # Separate QA floor and studio lights, never saved into component source or export.
 bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.003));floor=bpy.context.object;floor.name='QA_floor';mat=bpy.data.materials.new('QA_floor_warmgrey');mat.diffuse_color=(.16,.17,.19,1);mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.16,.17,.19,1);bs.inputs['Roughness'].default_value=.78;floor.data.materials.append(mat)
 world=bpy.data.worlds.new('QA_world');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.18,.20,.25,1);world.node_tree.nodes['Background'].inputs[1].default_value=.32;sc.world=world
 for nm,pos,power,size in [('key',(-3,-4,5),700,4),('rear_fill',(3,3,4),600,3),('top',(-1,1,5),400,3)]:
  ld=bpy.data.lights.new('QA_'+nm,'AREA');ld.energy=power;ld.shape='DISK';ld.size=size;o=bpy.data.objects.new('QA_'+nm,ld);sc.collection.objects.link(o);o.location=pos;o.rotation_euler=(Vector((0,0,1))-o.location).to_track_quat('-Z','Y').to_euler()
 cd=bpy.data.cameras.new('QA_camera');cam=bpy.data.objects.new('QA_camera',cd);sc.collection.objects.link(cam);cam.location=eye;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cd.lens=lens;sc.camera=cam
 sc.render.engine='BLENDER_EEVEE_NEXT';sc.eevee.taa_render_samples=64;sc.render.resolution_x=640;sc.render.resolution_y=360;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.view_settings.view_transform='AgX';sc.view_settings.look='AgX - Medium High Contrast';bpy.context.view_layer.update()
 xy=[world_to_camera_view(sc,cam,p)for p in points];bounds={'min':[min(p[i]for p in xy)for i in range(3)],'max':[max(p[i]for p in xy)for i in range(3)]};fit=all(0.04<min(p[i]for p in xy)and max(p[i]for p in xy)<.96 for i in range(2))and min(p.z for p in xy)>0
 row={'view':name,'catalogue_id':ident,'state':state,'export':str(exp.relative_to(B)),'image':str((Q/(name+'.png')).relative_to(B)),'camera':{'source_eye_m':eye,'target_source_m':target,'lens_mm':lens,'sensor_width_mm':cd.sensor_width,'matrix_world':[list(v)for v in cam.matrix_world],'resolution_px':[640,360],'role':'ordinary standing-height imported component inspection; no body rig'},'projected_component_bounds_01':bounds,'whole_component_framing_passed':fit,'before':before,'renderer':'Blender4.3.2 EEVEE64samples; studio QA aid only'};pre.append(row)
 if not preflight:
  assert fit,(name,bounds);sc.render.filepath=str(Q/(name+'.png'));bpy.ops.render.render(write_still=True);row['image_sha256']=sha(Q/(name+'.png'));row['after']={'source_sha256':sha(src),'export_sha256':sha(exp),'generator_sha256':sha(B/'source/build_auditorium_arrival.py')};row['source_export_unchanged']=row['before']==row['after'];records.append(row)
(Q/('camera_preflight.json'if preflight else 'render_evidence_002_r08.json'if onlyid else 'render_evidence.json')).write_text(json.dumps({'views':pre if preflight else records},indent=2));print('PREFLIGHT'if preflight else 'RENDERED',[(x['view'],x['whole_component_framing_passed'])for x in pre])
