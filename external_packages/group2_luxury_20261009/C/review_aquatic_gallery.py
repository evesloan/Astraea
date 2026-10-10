"""One normal-height gallery view of both contained aquatic rest bays from the saved source.
Geometry files remain byte-identical. Run after build_deluxe_variant.py via
heavy.py before actual visual acceptance. Preserve the replaced image evidence.
"""
import bpy,pathlib,json,hashlib,sys,shutil,bmesh
from mathutils import Vector
R=pathlib.Path(__file__).resolve().parent;unit=int(sys.argv[sys.argv.index('--')+1]);O=R/'sections'/f'{unit}_deluxe';c=json.loads((O/'SECTION_CONTRACT.json').read_text());assert c['habitat_study']=='aquatic'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();native=O/f'{unit}_deluxe.blend';export=O/f'{unit}_deluxe.glb';assert sha(native)==c['native_sha256'] and sha(export)==c['export_sha256']
assert all(json.loads((O/f'{k}_VERIFICATION.json').read_text())['status']=='PASS' for k in ['NATIVE','EXPORT'])
history=O/'review_image_attempts';history.mkdir(exist_ok=True);assert not (history/'main_programme_salon_frame.png').exists()
shutil.copy2(O/'main_programme.png',history/'main_programme_salon_frame.png');shutil.copy2(O/'SECTION_CONTRACT.json',history/'CONTRACT_BEFORE_GALLERY_VIEW.json')
if (O/'QA_CONTACT_SHEET.png').exists():shutil.copy2(O/'QA_CONTACT_SHEET.png',history/'QA_CONTACT_SHEET_BEFORE_GALLERY_VIEW.png')
bpy.ops.wm.open_mainfile(filepath=str(native));scene=bpy.context.scene;f=c['local_frame']
def w(u,v,h):return [f['origin_xyz'][k]+u*f['u_axis'][k]+v*f['v_axis'][k]+h*f['h_axis'][k] for k in range(3)]
def xyz(p):return Vector((p[0],-p[2],p[1]))
poly=c['reservation']['proposed_floor_boundary'];n=len(poly);me=bpy.data.meshes.new('PREVIEW_COMPILER_FLOOR');me.from_pydata([(x,-z,h) for h in [101.82,102] for x,z in poly],[],[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(j,(j+1)%n,(j+1)%n+n,j+n) for j in range(n)]);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.materials.append(bpy.data.materials['ASTRAEA_warm_stone']);ob=bpy.data.objects.new('PREVIEW_COMPILER_FLOOR',me);scene.collection.objects.link(ob)
bpy.ops.import_scene.gltf(filepath=str(R/'inputs/Game/assets/models/AST-RES-TIDAL_floor_winding_r002.glb'))
cam=bpy.data.objects.new('QA_EyeLevelCamera',bpy.data.cameras.new('QA_EyeLevelCamera'));scene.collection.objects.link(cam);scene.camera=cam;cam.data.lens=20;cam.data.clip_start=.05;cam.data.clip_end=100;pos=w(10.65,8.10,1.65);target=w(10.35,2.25,.95);cam.location=xyz(pos);cam.rotation_euler=(xyz(target)-cam.location).to_track_quat('-Z','Y').to_euler();scene.cycles.samples=4;scene.cycles.device='CPU';scene.cycles.use_denoising=True;scene.render.threads_mode='FIXED';scene.render.threads=2;scene.render.filepath=str(O/'main_programme.png');bpy.ops.render.render(write_still=True)
view=next(x for x in c['source_views'] if x['name']=='main_programme');view.update(camera_world_xyz=pos,target_world_xyz=target,sha256=sha(O/'main_programme.png'),scope='Actual saved-source paired-basin aquatic gallery, normal1.65m eye level; source-only')
c['review_view_rebuild']={'script':'review_aquatic_gallery.py','sha256':sha(pathlib.Path(__file__)),'command':f'python heavy.py review_aquatic_gallery.py {unit}','native_and_export_bytes_unchanged':True}
assert sha(native)==c['native_sha256'] and sha(export)==c['export_sha256'];(O/'SECTION_CONTRACT.json').write_text(json.dumps(c,indent=2));print('AQUATIC GALLERY VIEW rebuilt from unchanged native/export',unit,flush=True)
