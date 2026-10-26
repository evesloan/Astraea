import bpy,json,pathlib,hashlib,ast
from mathutils import Vector,Matrix
R=pathlib.Path(__file__).resolve().parents[2];D=R/'Game/grand_arrivals_tram_20261026/r005';N=R/'BlenderCatalogue/assets/grand_arrivals_tram_20261026/r005'
source=R/'Game/assets/models/AST-CIR-005.glb';assert hashlib.sha256(source.read_bytes()).hexdigest()=='524b54ad6aac1e35f68e0090b655929479c045d541c3001468a3d5cbf860769a'
assert not (D/'PrimaryCoreEnclosure.glb').exists() and not (N/'PrimaryCoreEnclosure_r005.blend').exists()
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.ops.import_scene.gltf(filepath=str(source))
tree=ast.parse((R/'recovery/grand_arrivals_embarkation_20261026/author_core_enclosure_r003.py').read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='clip'],type_ignores=[]),'protected_polygon_clip','exec'))
def game(p):return Vector((p.x,p.z,-p.y))
def native(p):return Vector((p.x,-p.z,p.y))
changed=[]
for h in ['0.14','1.06']:
 name='CORE_ForeWingRail_04_1_'+h;o=bpy.data.objects[name];old=o.data;old.calc_loop_triangles();faces=[]
 for tri in old.loop_triangles:
  poly=[{'p':game(o.matrix_world@old.vertices[vi].co),'uv':old.uv_layers.active.data[li].uv.copy()} for vi,li in zip(tri.vertices,tri.loops)]
  p=clip(poly,0,7.6,True)
  for i in range(1,len(p)-1):
   if (p[i]['p']-p[0]['p']).cross(p[i+1]['p']-p[0]['p']).length>1e-8:faces.extend([p[0],p[i],p[i+1]])
 y=21+float(h);points=[Vector((7.6,y,-13.04)),Vector((7.6,y+.08,-13.04)),Vector((7.6,y+.08,-12.96)),Vector((7.6,y,-12.96))]
 for i in [0,2,1,0,3,2]:faces.append({'p':points[i],'uv':Vector((points[i].z,points[i].y))})
 mesh=bpy.data.meshes.new(name+'_GuardReturn');mesh.from_pydata([native(v['p']) for v in faces],[],[(i,i+1,i+2) for i in range(0,len(faces),3)]);mesh.update();mesh.materials.append(old.materials[0]);uv=mesh.uv_layers.new(name='PreservedSourceUV')
 for i,v in enumerate(faces):uv.data[i].uv=v['uv']
 o.data=mesh;o.matrix_world=Matrix.Identity(4);changed.append(name)
o=bpy.data.objects['CORE_ForeWingPost_04_1_4.12'];m=o.matrix_world.copy();m.translation.x-=.69;o.matrix_world=m;changed.append(o.name)
for image in bpy.data.images:
 if image.source=='FILE' and image.has_data:image.pack()
native_file=N/'PrimaryCoreEnclosure_r005.blend';runtime=D/'PrimaryCoreEnclosure.glb'
bpy.ops.wm.save_as_mainfile(filepath=str(native_file));bpy.ops.export_scene.gltf(filepath=str(runtime),export_format='GLB',export_yup=True,export_extras=True)
receipt={'selected':False,'source':source.relative_to(R).as_posix(),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'changed_objects':changed,'guard_post_x_before':4.12,'guard_post_x_after':3.43,'replacement_guard':'r005 PrimaryD05_WestGlassGuard and continuous cap; r004 fore guard joins north','preserved':'All other original meshes, lights/datums, source materials, shaft and stair geometry','holds':['Native/runtime and untouched-object verification','Original component sweep','Installed route and guest circulation'],'outputs':{p.relative_to(R).as_posix():{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [native_file,runtime]}}
(D/'ENCLOSURE_BUILD.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
