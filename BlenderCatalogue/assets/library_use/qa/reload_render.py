"""Actual source reload and imported-GLB QA. Renderer setup is not game content."""
from pathlib import Path
import bpy,json,sys,math,hashlib
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT.parents[1];QA=ROOT/'qa';QA.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(BASE/'standards'))
from qa_frame import frame_report
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def audit():
 pts=[];tris=0;count=0;issues=[];dg=bpy.context.evaluated_depsgraph_get()
 for ob in bpy.context.scene.objects:
  if ob.type!='MESH':continue
  count+=1;eo=ob.evaluated_get(dg);me=eo.to_mesh();me.calc_loop_triangles();tris+=len(me.loop_triangles);pts += [tuple(ob.matrix_world@v.co) for v in me.vertices]
  if not me.uv_layers.active:issues.append(ob.name+':no UV')
  if ob.matrix_world.determinant()<=0:issues.append(ob.name+':negative transform')
  eo.to_mesh_clear()
 lo=[min(v[i] for v in pts) for i in range(3)];hi=[max(v[i] for v in pts) for i in range(3)]
 return {'bounds_min_source_m':lo,'bounds_max_source_m':hi,'dimensions_source_m':[hi[i]-lo[i] for i in range(3)],'triangles':tris,'mesh_count':count,'packed_image_count':sum(bool(i.packed_file) for i in bpy.data.images),'issues':issues}
def point(ob,p):ob.rotation_euler=(Vector(p)-ob.location).to_track_quat('-Z','Y').to_euler()
def solid(name,color):
 m=bpy.data.materials.new(name);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Roughness'].default_value=.85;return m

def setup():
 s=bpy.context.scene;s.render.engine='BLENDER_EEVEE_NEXT';s.eevee.taa_render_samples=64;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.threads_mode='FIXED';s.render.threads=4
 bpy.ops.mesh.primitive_plane_add(size=200);ob=bpy.context.object;ob.name='QA_ONLY_neutral_floor';ob.data.materials.append(solid('QA_floor',(.20,.225,.24)))
 s.world=bpy.data.worlds.new('QA_ONLY_neutral_world');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.42,.46,.50,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.65
 for name,loc,power,size in [('key',(-3,-4,5),520,4),('fill',(3,-1,3),220,3),('rim',(0,3,4),330,3)]:
  bpy.ops.object.light_add(type='AREA',location=loc);ob=bpy.context.object;ob.name='QA_ONLY_'+name;ob.data.energy=power;ob.data.size=size;point(ob,(0,0,.7))
 bpy.ops.object.camera_add();s.camera=bpy.context.object;s.camera.name='QA_ONLY_camera';s.camera.data.lens=50;s.camera.data.clip_start=.02;s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';return s.camera

def imported(cid,z=0):
 bpy.ops.wm.read_factory_settings(use_empty=True);path=ROOT/'exports'/(cid+'.glb');bpy.ops.import_scene.gltf(filepath=str(path))
 for ob in bpy.context.scene.objects:
  if ob.parent is None:ob.location.z+=z
 return path
images=[]
def render(cid,filename,cam,position,target,lens=50,res=(640,360),context=None):
 if wanted and filename not in wanted:return
 s=bpy.context.scene;cam.location=position;point(cam,target);cam.data.lens=lens;s.render.resolution_x=res[0];s.render.resolution_y=res[1];s.render.filepath=str(QA/(filename+'.png'))
 objects=[o for o in s.objects if o.type=='MESH' and not o.name.startswith('QA_ONLY')]
 framing=None;proxy=None
 if filename.endswith('_640') or 'screen_controls_detail' in filename:
  if 'actual_use' in filename or 'screen_controls_detail' in filename:
   points=[o.matrix_world@v.co for o in objects for v in o.data.vertices if (o.matrix_world@v.co).z>.920]
   lo=Vector([min(v[i] for v in points) for i in range(3)]);hi=Vector([max(v[i] for v in points) for i in range(3)])
   bpy.ops.mesh.primitive_cube_add(size=1,location=(lo+hi)/2);proxy=bpy.context.object;proxy.name='QA_ONLY_preflight_display_and_controls';proxy.dimensions=hi-lo;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);objects=[proxy]
  framing=frame_report(s,cam,objects,margin=.10)
  while not framing['passes'] and cam.data.lens>20:
   cam.data.lens*=.96;framing=frame_report(s,cam,objects,margin=.10)
  assert framing['passes'],(filename,framing)
  framing['measured_scope']='All actual imported component bounds' if proxy is None else 'Actual exported display/control vertices above Z0.920 m; intended close use view'
  if proxy:bpy.data.objects.remove(proxy,do_unlink=True)
 lens=cam.data.lens
 if '--preflight' not in args:bpy.ops.render.render(write_still=True)
 mf=json.loads((ROOT/(cid+'.manifest.json')).read_text());images.append({'file':filename+'.png','catalogue_id':cid,'source_sha256':sha(ROOT/mf['source']),'export_sha256':sha(ROOT/mf['export']),'unlabelled_image_sha256':sha(QA/(filename+'.png')) if '--preflight' not in args else None,'frame_preflight':framing,'camera_source_position_m':list(position),'camera_target_source_m':list(target),'camera_rotation_euler_radians':list(cam.rotation_euler),'lens_mm':lens,'sensor_width_mm':cam.data.sensor_width,'resolution_px':list(res),'camera_height_m':position[2],'component_placement_translation_m':[0,0,.754] if cid=='AST-LIB-008' else [0,0,0],'context':context or 'QA floor and area lights only','scope':'Actual final imported GLB component inspection; not original-room or engine evidence','engine':'Blender 4.3.2 EEVEE Next','samples':64})

args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
wanted=set(next((a.split('=',1)[1] for a in args if a.startswith('--only=')), '').split(','))-{''}
if '--render' not in args:
 reports=[]
 for cid in ['AST-LIB-008','AST-LIB-009','AST-LIB-010']:
  mf=json.loads((ROOT/(cid+'.manifest.json')).read_text());p=ROOT/mf['source'];bpy.ops.wm.open_mainfile(filepath=str(p));source=audit();imported(cid);export=audit()
  assert source['triangles']==export['triangles']==mf['evaluated_triangles'];assert max(abs(a-b) for a,b in zip(source['dimensions_source_m'],export['dimensions_source_m']))<1e-5;assert not source['issues'] and not export['issues']
  reports.append({'catalogue_id':cid,'source_sha256':sha(p),'export_sha256':sha(ROOT/mf['export']),'source':source,'actual_imported_glb':export,'status':'PASS'})
 (QA/'source_reload_import_audit.json').write_text(json.dumps(reports,indent=2));print('RELOAD_PASS',[(r['catalogue_id'],r['source']['triangles']) for r in reports])
else:
 cid='AST-LIB-008';imported(cid,.754);cam=setup()
 bpy.ops.mesh.primitive_cube_add(size=1,location=(0,0,.727));ob=bpy.context.object;ob.name='QA_ONLY_receiver_support';ob.dimensions=(.84,.46,.054);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);ob.data.materials.append(solid('QA_support',(.26,.28,.29)))
 render(cid,'008_fixture_standing_640',cam,(.78,-1.32,1.65),(0,-.02,1.05),49)
 render(cid,'008_fixture_seated_640',cam,(.78,-1.32,1.19),(0,-.02,1.02),49)
 render(cid,'008_fixture_underhood_1280',cam,(.63,-.90,.99),(0,-.04,1.185),64,(1280,720))
 render(cid,'008_fixture_service_1280',cam,(.56,.98,1.43),(0,0,1.06),56,(1280,720))
 # Actual unchanged study-table GLB establishes receiver contact in visible context.
 bpy.data.objects.remove(bpy.data.objects['QA_ONLY_receiver_support'],do_unlink=True)
 p=BASE/'assets/library_study/AST-LIB-STUDY-01_open_shared_table.glb';bpy.ops.import_scene.gltf(filepath=str(p))
 render(cid,'008_existing_shared_table_context_640',cam,(1.85,-2.82,1.65),(0,0,.69),48,context={'reused_component':'AST-LIB-STUDY-01','glb_relative_to_catalogue':str(p.relative_to(BASE)),'sha256':sha(p),'change':'None; imported only as labelled QA context'})
 cid='AST-LIB-009';imported(cid);cam=setup()
 render(cid,'009_browser_standing_640',cam,(1.30,-2.29,1.65),(0,0,.65),37)
 render(cid,'009_browser_seated_640',cam,(.18,-2.28,1.19),(0,0,.65),32)
 render(cid,'009_browser_covers_detail_1280',cam,(.25,-1.48,1.34),(0,-.05,.90),59,(1280,720))
 cid='AST-LIB-010';imported(cid);cam=setup()
 render(cid,'010_terminal_standing_640',cam,(1.22,-2.40,1.65),(0,0,.71),35)
 render(cid,'010_terminal_actual_use_640',cam,(0,-.86,1.65),(0,-.02,1.172),30)
 render(cid,'010_terminal_screen_controls_detail_1280',cam,(.26,-1.02,1.54),(0,-.027,1.17),54,(1280,720))
 render(cid,'010_terminal_service_640',cam,(1.29,2.00,1.65),(0,0,.71),34)
 if wanted and (QA/'RENDER_MANIFEST.json').exists():
  prior=json.loads((QA/'RENDER_MANIFEST.json').read_text())['images'];new={r['file']:r for r in images};images=[new.pop(r['file'],r) for r in prior]+list(new.values())
 (QA/('FRAME_PREFLIGHT.json' if '--preflight' in args else 'RENDER_MANIFEST.json')).write_text(json.dumps({'scope':'BLENDER COMPONENT QA | actual imported GLB | no original game/room evidence','images':images},indent=2));print('RENDER_COMPLETE',len(images))
