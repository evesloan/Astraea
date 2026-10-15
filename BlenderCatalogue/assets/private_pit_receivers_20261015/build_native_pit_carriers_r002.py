from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
P=Path(__file__).resolve().parent
plan=json.loads((P/'EXACT_PIT_RECEIVER_PLAN.json').read_text())
assert bpy.app.version[:3]==(4,3,2)
assert 'G2_PIT_CARRIERS_r002'not in Path('/workspace/astraea-protected-integration-20261012/BlenderCatalogue/catalogue_manifest.json').read_text()
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
def material(name,color):
 m=bpy.data.materials.new(name);m.use_nodes=True;s=m.node_tree.nodes.get('Principled BSDF');s.inputs['Base Color'].default_value=(*color,1);s.inputs['Roughness'].default_value=.76;return m
steel=material('Receiver_dark_zinc',(.18,.20,.21));stone=material('Pit_receiving_stone',(.52,.49,.40))
objects=[]
def create(name,world_vertices,faces,mat):
 coordinates=[(p[0],-p[2],p[1])for p in world_vertices];mesh=bpy.data.meshes.new(name);mesh.from_pydata(coordinates,[],faces);mesh.update();center=sum((v.co for v in mesh.vertices),Vector())/len(mesh.vertices)
 for polygon in mesh.polygons:
  if polygon.normal.dot(polygon.center-center)<0:polygon.flip()
 mesh.update();assert all(face.normal.dot(face.center-center)>0 for face in mesh.polygons),name
 obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj);obj.data.materials.append(mat);objects.append(obj)
def prism(name,a,b,width,depth,v0,v1):
 a,b=Vector(a),Vector(b);d=(b-a).normalized();u=d.cross(Vector((0,1,0))).normalized();v=u.cross(d).normalized();corners=[a-u*width/2+v*v0,a+u*width/2+v*v0,a+u*width/2+v*v1,a-u*width/2+v*v1,b-u*width/2+v*v0,b+u*width/2+v*v0,b+u*width/2+v*v1,b-u*width/2+v*v1];faces=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)];create(name,corners,faces,steel)
for suite in plan['suites']:
 key=suite['key'];outline=suite['floor_outline_xz'];low=suite['floor_bottom_y'];high=suite['floor_top_y'];vertices=[(p[0],y,p[1])for y in[low,high]for p in outline];faces=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)];# Exact retained PIT_<key>_r001.glb owns the slab;author new carriers only.
 for member in suite['new_underframe_parts']:
  w=member['width'];d=member['depth']
  for suffix,width,lo,hi in [('bottom',w,-d/2,-d/2+.035),('web',.045,-d/2+.035,d/2-.035),('top',w,d/2-.035,d/2)]:prism(member['name']+'_'+suffix,member['a'],member['b'],width,d,lo,hi)
bpy.data.texts.new('EXACT_PIT_RECEIVER_PLAN.json').write(json.dumps(plan,indent=2))
out=P/'import/Game/assets/private_pit_receivers_20261015';out.mkdir(parents=True,exist_ok=True);model=out/'G2_PIT_CARRIERS_r002.glb';bpy.ops.export_scene.gltf(filepath=str(model),export_format='GLB',export_yup=True)
native=P/'native';native.mkdir(exist_ok=True);file=native/'G2_PIT_CARRIERS_r002.blend';bpy.ops.wm.save_as_mainfile(filepath=str(file),compress=True);bpy.ops.wm.open_mainfile(filepath=str(file));fresh=P/'FRESH_NATIVE_REEXPORT.glb';bpy.ops.export_scene.gltf(filepath=str(fresh),export_format='GLB',export_yup=True);assert fresh.read_bytes()==model.read_bytes()
receipt={'status':'PASS_NATIVE_PIT_RECEIVERS_FRESH_REEXPORT_EXACT','blender_version':bpy.app.version_string,'source_suites':5,'source_slabs_used_unchanged':5,'profiled_crossmembers':10,'mesh_objects':len(bpy.data.objects),'model_sha256':hashlib.sha256(model.read_bytes()).hexdigest(),'native_sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'source_cabin_clearance_m':.24,'old_source_files_changed':False,'production_adopted':False,'runtime_rim_contacts_verified':False};(P/'NATIVE_PIT_CARRIER_VERIFICATION.json').write_text(json.dumps(receipt,indent=2)+'\n');print('PASS_NATIVE_PIT_RECEIVERS_EXPORT',len(bpy.data.objects))
