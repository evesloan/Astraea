"""Replace uninformative frames from unchanged actual multi-level source files."""
import bpy,bmesh,pathlib,json,sys,hashlib,shutil,math
from mathutils import Vector
R=pathlib.Path(__file__).resolve().parent;sys.path.insert(0,str(R))
from source_paths import section
from premium_frame import PremiumFrame
unit=int(sys.argv[sys.argv.index('--')+1]);row,O,native,export=section(unit)
c=json.loads((O/'SECTION_CONTRACT.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(native)==c['native_sha256'] and sha(export)==c['export_sha256'];assert row['reservation']['tier'] in ['royalty','supreme']
frame=PremiumFrame(c['reservation']['proposed_floor_boundary']);history=O/'review_image_attempts';history.mkdir(exist_ok=True)
assert not (history/'CONTRACT_BEFORE_MULTILEVEL_VIEW.json').exists()
shutil.copy2(O/'SECTION_CONTRACT.json',history/'CONTRACT_BEFORE_MULTILEVEL_VIEW.json')
bpy.ops.wm.open_mainfile(filepath=str(native));scene=bpy.context.scene
def floor(name,poly,y):
 n=len(poly);me=bpy.data.meshes.new(name);me.from_pydata([(x,-z,h) for h in [y-.18,y] for x,z in poly],[],[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(j,(j+1)%n,(j+1)%n+n,j+n) for j in range(n)]);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.materials.append(bpy.data.materials['ASTRAEA_warm_stone']);ob=bpy.data.objects.new(name,me);scene.collection.objects.link(ob)
floor('PREVIEW_ROOT_LOWER_RECEIVER',frame.poly,102)
end=c['upper_floor_proposal']['local_v'][1]
for j,(u0,u1,v0,v1) in enumerate([(.30,4.65,12,14.85),(.30,.60,14.85,20.20),(4.20,4.65,14.85,20.20),(.30,4.65,20.20,end),(4.65,9.35,12,15.85),(4.65,4.80,15.85,19.82),(9.20,9.35,15.85,19.82),(4.65,9.35,19.82,end),(9.35,100,12,end)]):
 vs=sorted(set([v0,v1]+[(z-frame.start)/frame.vsign for x,z in frame.poly if v0<(z-frame.start)/frame.vsign<v1]));poly=[]
 for v in vs:
  u=min(u1,frame.depth(v)-.30);p=frame.world(u,v);poly.append([p[0],p[2]])
 for v in reversed(vs):
  p=frame.world(u0,v);poly.append([p[0],p[2]])
 floor('PREVIEW_ROOT_UPPER_'+str(j),poly,106.5)
bpy.ops.import_scene.gltf(filepath=str(R/'inputs/Game/assets/models/AST-RES-TIDAL_floor_winding_r002.glb'))
cam=bpy.data.objects.new('QA_EyeCamera',bpy.data.cameras.new('QA_EyeCamera'));scene.collection.objects.link(cam);scene.camera=cam;cam.data.lens=20;cam.data.clip_start=.05;cam.data.clip_end=100
positions=[]
if row['reservation']['tier']=='royalty':positions.append(('main_programme',frame.blender(11.4,8.1,1.65),frame.blender(15,10.2,1.0),102))
positions.append(('sleeping_second',frame.rigid(15.6,19.2,.45,-3.15,6.15),frame.rigid(15.6,19.2,0,.7,5.35),106.5))
scene.cycles.samples=4;scene.cycles.device='CPU';scene.cycles.use_denoising=True;scene.render.threads_mode='FIXED';scene.render.threads=2
for name,pos,target,y in positions:
 shutil.copy2(O/(name+'.png'),history/(name+'_unhelpful_frame.png'));cam.location=Vector(pos);cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(O/(name+'.png'));bpy.ops.render.render(write_still=True)
 view=next(x for x in c['source_views'] if x['name']==name);view.update(camera_world_xyz=[pos[0],pos[2],-pos[1]],target_world_xyz=[target[0],target[2],-target[1]],sha256=sha(O/(name+'.png')),height_above_local_floor=1.65,proposed_local_floor_y=y,scope='Actual unchanged saved source; normal eye with Root render-only receiver floor proposal')
c['review_view_rebuild']={'script':'review_multilevel_views.py','sha256':sha(pathlib.Path(__file__)),'native_and_export_bytes_unchanged':True}
assert sha(native)==c['native_sha256'] and sha(export)==c['export_sha256'];(O/'SECTION_CONTRACT.json').write_text(json.dumps(c,indent=2));print('MULTILEVEL SOURCE VIEWS REBUILT',unit)
