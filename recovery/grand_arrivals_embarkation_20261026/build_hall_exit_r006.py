import bpy,json,pathlib,hashlib,ast
from mathutils import Vector,Matrix
R=pathlib.Path(__file__).resolve().parents[2];D=R/'Game/grand_arrivals_tram_20261026/r006';N=R/'BlenderCatalogue/assets/grand_arrivals_tram_20261026/r006'
source=R/'Game/assets/models/AST-ARR-002.glb';assert hashlib.sha256(source.read_bytes()).hexdigest()=='938a20eae3eec4a164e8822368b6776d534216bb6f438153e10aa60aa67f1d9e'
assert not (D/'ArrivalsHallExit.glb').exists()
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.ops.import_scene.gltf(filepath=str(source))
tree=ast.parse((R/'recovery/grand_arrivals_embarkation_20261026/author_core_enclosure_r003.py').read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['clip','subtract']],type_ignores=[]),'protected_clip','exec'))
def game(p):return Vector((p.x,p.z,-p.y))
def native(p):return Vector((p.x,-p.z,p.y))
o=bpy.data.objects['ARR_EastEnclosure_-465.85'];old=o.data;old.calc_loop_triangles();flat=[];changed=0
for t in old.loop_triangles:
 p=[{'p':game(o.matrix_world@old.vertices[vi].co),'uv':old.uv_layers.active.data[li].uv.copy()} for vi,li in zip(t.vertices,t.loops)]
 pieces,cut=subtract(p,[22.5,-.01,-30.8],[23.2,4.4,-24.8]);changed+=int(cut)
 for q in pieces:
  for i in range(1,len(q)-1):
   if (q[i]['p']-q[0]['p']).cross(q[i+1]['p']-q[0]['p']).length>1e-8:flat.extend([q[0],q[i],q[i+1]])
assert changed>0
mesh=bpy.data.meshes.new(o.name+'_SupportedExit');mesh.from_pydata([native(v['p']) for v in flat],[],[(i,i+1,i+2) for i in range(0,len(flat),3)]);mesh.update();mesh.materials.append(old.materials[0]);uv=mesh.uv_layers.new(name='OriginalWallUV')
for i,v in enumerate(flat):uv.data[i].uv=v['uv']
o.data=mesh;o.matrix_world=Matrix.Identity(4)
materials={m.name.split('.')[0]:m for m in bpy.data.materials};new=[]
def box(name,lo,hi,role):
 x,y,z=lo;X,Y,Z=hi;vs=[[x,y,z],[X,y,z],[x,Y,z],[X,Y,z],[x,y,Z],[X,y,Z],[x,Y,Z],[X,Y,Z]];fs=[[0,2,3,1],[4,5,7,6],[0,1,5,4],[2,6,7,3],[0,4,6,2],[1,3,7,5]]
 m=bpy.data.meshes.new(name);m.from_pydata([native(Vector(p)) for p in vs],[],fs);m.update();m.materials.append(materials[role]);u=m.uv_layers.new(name='MetreUV')
 for f in m.polygons:
  ax=max(range(3),key=lambda i:abs(f.normal[i]));axes=[i for i in range(3) if i!=ax]
  for li in f.loop_indices:
   p=m.vertices[m.loops[li].vertex_index].co;u.data[li].uv=(p[axes[0]],p[axes[1]])
 obj=bpy.data.objects.new(name,m);bpy.context.collection.objects.link(obj);new.append(name)
for side,z in [('North',-30.96),('South',-24.64)]:box('ARR_RailExit_'+side+'Jamb',[22.55,0,z-.16],[23,4.9,z+.16],'warm_walnut')
box('ARR_RailExit_ReceivedHeader',[22.55,4.4,-31.12],[23,4.9,-24.48],'warm_walnut')
box('ARR_RailExit_HeaderReveal',[22.50,4.4,-30.8],[23.03,4.47,-24.8],'champagne_metal')
for image in bpy.data.images:
 if image.source=='FILE' and image.has_data:image.pack()
nf=N/'ArrivalsHallExit_r006.blend';gf=D/'ArrivalsHallExit.glb'
bpy.ops.wm.save_as_mainfile(filepath=str(nf));bpy.ops.export_scene.gltf(filepath=str(gf),export_format='GLB',export_extras=True,export_yup=True)
out={'selected':False,'source':source.relative_to(R).as_posix(),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'changed_objects':[o.name],'added_objects':new,'opening_world_xz':[-8.25,-462.8,-8.05,-456.8],'clear_height_m':4.4,'preserved':'Original D03 cap, exhibits, stair court, lift, reception and baggage/service separation; no new light','holds':['Untouched-object/native-runtime verification','Complete original vehicle curve and station threshold sweep','Actual guest/boarding/loaded operation and visual acceptance'],'outputs':{p.relative_to(R).as_posix():{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [nf,gf]}}
(D/'HALL_BUILD.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
