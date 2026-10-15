from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector,Matrix
D=Path(__file__).resolve().parent;G=Path('/workspace/astraea-protected-integration-20261012/Game');src=G/'assets/models/AST-CIR-005_forward_breakroom_d03.glb';expected='dd79daa1dc24e5524cebf6ba32778eee9f1b39ef6ad02fbd4e07336d3a0191de';assert hashlib.sha256(src.read_bytes()).hexdigest()==expected;assert bpy.app.version[:3]==(4,3,2)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.ops.import_scene.gltf(filepath=str(src));bpy.context.preferences.filepaths.save_version=0
names=[f'CORE_{kind}_09_{side}'for side in[-1,1]for kind in['OuterWall','WallDado']];sources={name:bpy.data.objects[name]for name in names};donor=bpy.data.objects['CORE_LateralPortalLintel_01_-1'];made=[];rows=[]
def godot(p):return Vector((p.x,p.z,-p.y))
def blender(p):return Vector((p.x,-p.z,p.y))
def clip(poly,axis,plane,less):
 if not poly:return []
 out=[];s=poly[-1];ds=s['p'][axis]-plane
 for e in poly:
  de=e['p'][axis]-plane;ins=ds<=0 if less else ds>=0;ine=de<=0 if less else de>=0
  if ins!=ine:
   t=ds/(ds-de);out.append({k:s[k].lerp(e[k],t)for k in ['p','n','uv']})
  if ine:out.append(e)
  s=e;ds=de
 return out
def subtract(tri):
 pieces=[];inside=tri
 for axis,plane,less in[(0,-8.1,False),(0,8.1,True),(1,61.,False),(1,64.2,True),(2,-2.,False),(2,2.,True)]:
  outside=clip(inside,axis,plane,not less)
  if len(outside)>=3:pieces.append(outside)
  inside=clip(inside,axis,plane,less)
  if not inside:break
 return pieces
for name,obj in sources.items():
 obj.data.calc_loop_triangles();uvlayer=obj.data.uv_layers.active;triangles=[];pre=[]
 normal_matrix=obj.matrix_world.to_3x3().inverted().transposed()
 for tri in obj.data.loop_triangles:
  poly=[]
  for li,vi in zip(tri.loops,tri.vertices):
   p=godot(obj.matrix_world@obj.data.vertices[vi].co);n=godot(normal_matrix@obj.data.corner_normals[li].vector).normalized();uv=uvlayer.data[li].uv.copy()if uvlayer else Vector((0.,0.));poly.append({'p':p,'n':n,'uv':uv})
  pre.append(poly)
  for poly in subtract(poly):
   for i in range(1,len(poly)-1):triangles.append([poly[0],poly[i],poly[i+1]])
 # Close the newly exposed jambs and head using this exact wall's thickness and retained material.
 points=[v['p']for t in pre for v in t];lo=Vector(tuple(min(p[i]for p in points)for i in range(3)));hi=Vector(tuple(max(p[i]for p in points)for i in range(3)));ya=max(61.,lo.y);yb=min(64.2,hi.y)
 if yb>ya:
  for z,normal in[(-2.,Vector((0,0,1))),(2.,Vector((0,0,-1)))]:
   vs=[Vector((lo.x,ya,z)),Vector((hi.x,ya,z)),Vector((hi.x,yb,z)),Vector((lo.x,yb,z))]
   if (vs[1]-vs[0]).cross(vs[2]-vs[0]).dot(normal)<0:vs.reverse()
   for ids in[(0,1,2),(0,2,3)]:triangles.append([{'p':vs[i],'n':normal,'uv':Vector((vs[i].x,vs[i].y))}for i in ids])
  if lo.y<64.2<hi.y:
   vs=[Vector((lo.x,64.2,-2)),Vector((hi.x,64.2,-2)),Vector((hi.x,64.2,2)),Vector((lo.x,64.2,2))];normal=Vector((0,-1,0))
   if (vs[1]-vs[0]).cross(vs[2]-vs[0]).dot(normal)<0:vs.reverse()
   for ids in[(0,1,2),(0,2,3)]:triangles.append([{'p':vs[i],'n':normal,'uv':Vector((vs[i].x,vs[i].z))}for i in ids])
 flat=[v for t in triangles for v in t];mesh=bpy.data.meshes.new(name+'_D10_PUBLIC_PORTAL');mesh.from_pydata([blender(v['p'])for v in flat],[],[tuple(range(i,i+3))for i in range(0,len(flat),3)]);mesh.update();new=bpy.data.objects.new(name+'_D10_PUBLIC_PORTAL',mesh);bpy.context.collection.objects.link(new)
 for mat in obj.data.materials:mesh.materials.append(mat)
 uv=mesh.uv_layers.new(name='UVMap')
 for i,v in enumerate(flat):uv.data[i].uv=v['uv']
 for p in mesh.polygons:p.use_smooth=True
 mesh.normals_split_custom_set([blender(v['n']).normalized()for v in flat]);made.append(new);rows.append({'source_name':name,'replacement_name':new.name,'source_triangles':len(pre),'replacement_triangles':len(triangles),'input_bounds_local':[list(lo),list(hi)]})
for obj in list(bpy.data.objects):
 if obj not in made:bpy.data.objects.remove(obj,do_unlink=True)
for image in bpy.data.images:
 if image.source=='FILE'and not image.packed_file:image.pack()
bpy.data.texts.new('SOURCE_POLICY.txt').write('Two D10 public dining branches through four exact retained enclosure wall/dado meshes only. SourceSHA256 '+expected+'. Openings localZ-2..2,Y61..64.2 sit between unchanged lift shaft localZ-8.02..-3.98 and stair opening localZ4..14.7. Core floors,stairs,lift,primary columns,other walls andsourceGLB unchanged. New jamb/head reveals close wall thickness. Retained wall headers and explicit reveal faces frame both openings; no coincident duplicate lintel. No operating services,food orpressure/capacity claim.')
T=D/'import/Game/assets/dining_public_core_20261015';T.mkdir(parents=True,exist_ok=True);model=T/'FORWARD_D10_DINING_PUBLIC_BRANCHES_r001.glb';bpy.ops.export_scene.gltf(filepath=str(model),export_format='GLB',export_yup=True,export_extras=True);N=D/'native';N.mkdir(exist_ok=True);native=N/'FORWARD_D10_DINING_PUBLIC_BRANCHES_r001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True);bpy.ops.wm.open_mainfile(filepath=str(native));fresh=D/'FRESH_REEXPORT.glb';bpy.ops.export_scene.gltf(filepath=str(fresh),export_format='GLB',export_yup=True,export_extras=True);assert fresh.read_bytes()==model.read_bytes();assert hashlib.sha256(src.read_bytes()).hexdigest()==expected
receipt={'status':'NATIVE_FRESH_REEXPORT_EXACT_CANDIDATE_UNADOPTED','source_file':src.name,'source_sha256':expected,'native_sha256':hashlib.sha256(native.read_bytes()).hexdigest(),'model_sha256':hashlib.sha256(model.read_bytes()).hexdigest(),'walls':rows,'source_core_origin':[0,0,-432],'new_openings_world':{'floor_y':61,'clear_height':3.2,'z':[-434,-430]},'retained_shafts_floors_stairs_primary_supports_unchanged':True,'door_or_pressure_hygiene_capacity_admission':False};(D/'NATIVE_VERIFICATION.json').write_text(json.dumps(receipt,indent=2)+'\n');print('PASS_D10_PUBLIC_BRANCH_NATIVE_EXACT')
