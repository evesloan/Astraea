import bpy,json,pathlib,hashlib,ast
from mathutils import Vector,Matrix
R=pathlib.Path(__file__).resolve().parents[2];D=R/'Game/grand_arrivals_tram_20261026/r007';N=R/'BlenderCatalogue/assets/grand_arrivals_tram_20261026/r007'
source=R/'Game/assets/models/AST-CIR-005_forward_breakroom_d03.glb';assert hashlib.sha256(source.read_bytes()).hexdigest()=='dd79daa1dc24e5524cebf6ba32778eee9f1b39ef6ad02fbd4e07336d3a0191de'
assert not (D/'ForwardGroundEnclosure.glb').exists() and not (N/'ForwardGroundEnclosure_r007.blend').exists()
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.ops.import_scene.gltf(filepath=str(source))
tree=ast.parse((R/'recovery/grand_arrivals_embarkation_20261026/author_core_enclosure_r003.py').read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='clip'],type_ignores=[]),'protected_polygon_clip','exec'))
def game(p):return Vector((p.x,p.z,-p.y))
def native(p):return Vector((p.x,-p.z,p.y))
changed=[]
for end,h in [(end,h) for end in ['Fore','Rear'] for h in ['0.14','1.06']]:
 name='CORE_'+end+'WingRail_00_1_'+h;o=bpy.data.objects[name];old=o.data;old.calc_loop_triangles();faces=[]
 for tri in old.loop_triangles:
  poly=[{'p':game(o.matrix_world@old.vertices[vi].co),'uv':old.uv_layers.active.data[li].uv.copy()} for vi,li in zip(tri.vertices,tri.loops)]
  p=clip(poly,0,7.6,True)
  for i in range(1,len(p)-1):
   if (p[i]['p']-p[0]['p']).cross(p[i+1]['p']-p[0]['p']).length>1e-8:faces.extend([p[0],p[i],p[i+1]])
 y=float(h);z=-13 if end=='Fore' else 20;points=[Vector((7.6,y,z-.04)),Vector((7.6,y+.08,z-.04)),Vector((7.6,y+.08,z+.04)),Vector((7.6,y,z+.04))]
 for i in [0,2,1,0,3,2]:faces.append({'p':points[i],'uv':Vector((points[i].z,points[i].y))})
 mesh=bpy.data.meshes.new(name+'_GuardReturn');mesh.from_pydata([native(v['p']) for v in faces],[],[(i,i+1,i+2) for i in range(0,len(faces),3)]);mesh.update();mesh.materials.append(old.materials[0]);uv=mesh.uv_layers.new(name='PreservedSourceUV')
 for i,v in enumerate(faces):uv.data[i].uv=v['uv']
 o.data=mesh;o.matrix_world=Matrix.Identity(4);changed.append(name)
for end in ['Fore','Rear']:
 o=bpy.data.objects['CORE_'+end+'WingPost_00_1_4.12'];m=o.matrix_world.copy();m.translation.x-=.69;o.matrix_world=m;changed.append(o.name)
materials={m.name.split('.')[0]:m for m in bpy.data.materials};new=[]
existing=set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath=str(R/'Game/assets/models/AST-ARR-002.glb'))
materials['ArrivalsArchitecturalGlass']=next(m for m in bpy.data.materials if m.name=='ArrivalsArchitecturalGlass')
for imported in set(bpy.data.objects)-existing:bpy.data.objects.remove(imported,do_unlink=True)
def box(name,lo,hi,role):
 x,y,z=lo;X,Y,Z=hi;vs=[[x,y,z],[X,y,z],[x,Y,z],[X,Y,z],[x,y,Z],[X,y,Z],[x,Y,Z],[X,Y,Z]];fs=[[0,2,3,1],[4,5,7,6],[0,1,5,4],[2,6,7,3],[0,4,6,2],[1,3,7,5]]
 m=bpy.data.meshes.new(name);m.from_pydata([native(Vector(p)) for p in vs],[],fs);m.update();m.materials.append(materials[role]);u=m.uv_layers.new(name='MetreUV')
 for f in m.polygons:
  ax=max(range(3),key=lambda i:abs(f.normal[i]));axes=[i for i in range(3) if i!=ax]
  for li in f.loop_indices:
   p=m.vertices[m.loops[li].vertex_index].co;u.data[li].uv=(p[axes[0]],p[axes[1]])
 obj=bpy.data.objects.new(name,m);bpy.context.collection.objects.link(obj);new.append(name)
for name,lo,hi in [('North',-13,-2),('South',2,20)]:
 box('FORWARD_Ground_'+name+'Glass',[3.405,.16,lo],[3.44,1.28,hi],'ArrivalsArchitecturalGlass')
 box('FORWARD_Ground_'+name+'Cap',[3.37,1.28,lo],[3.47,1.36,hi],'champagne_metal')
 for i,z in enumerate([lo,hi]):box('FORWARD_Ground_'+name+'Post_'+str(i),[3.35,0,z-.04],[3.49,1.36,z+.04],'champagne_metal')
for image in bpy.data.images:
 if image.source=='FILE' and image.has_data:image.pack()
native_file=N/'ForwardGroundEnclosure_r007.blend';runtime=D/'ForwardGroundEnclosure.glb'
bpy.ops.wm.save_as_mainfile(filepath=str(native_file));bpy.ops.export_scene.gltf(filepath=str(runtime),export_format='GLB',export_yup=True,export_extras=True)
receipt={'selected':False,'source':source.relative_to(R).as_posix(),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'changed_objects':changed,'added_objects':new,'crossing_world_z':[-434,-430],'crossing_interlock_admitted':False,'guard_post_x_before':4.12,'guard_post_x_after':3.43,'replacement_guard':'Ground guards keep original 4m room-threshold crossing; no departure admission without crossing occupancy/interlock proof','preserved':'All other original meshes, lights/datums, source materials, shaft and stair geometry','holds':['Native/runtime and untouched-object verification','Original component sweep','Installed route and guest circulation'],'outputs':{p.relative_to(R).as_posix():{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [native_file,runtime]}}
(D/'ENCLOSURE_BUILD.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
