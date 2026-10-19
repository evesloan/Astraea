from pathlib import Path
import bpy,json,hashlib,struct
from mathutils import Matrix,Vector
D=Path(__file__).resolve().parent;R=Path('/workspace/Astraea');r=json.loads((D/'RECEIPT.json').read_text())
def geom(o):
 h=hashlib.sha256()
 for v in o.data.vertices:h.update(struct.pack('<3f',*v.co))
 for f in o.data.polygons:h.update(str(list(f.vertices)).encode())
 for l in o.data.uv_layers:
  for v in l.data:h.update(struct.pack('<2f',*v.uv))
 return h.hexdigest()
def sig(o):
 o.data.calc_loop_triangles();return sorted(tuple(sorted(tuple(round(float(c),4)for c in o.matrix_world@o.data.vertices[i].co)for i in t.vertices))for t in o.data.loop_triangles)
bpy.ops.wm.open_mainfile(filepath=str(R/'BlenderCatalogue/assets/quiet_d15_staff_receiving_20261016/QuietD15StaffReceiving_r001.blend'));prior={}
for o in bpy.data.objects:
 if o.type!='MESH':continue
 o.data=o.data.copy();o.data.transform(Matrix.Translation(Vector((0,0,4.5)))@Matrix.Diagonal((1,-1,1,1))@o.matrix_world);o.data.flip_normals();o.matrix_world=Matrix.Identity(4);prior[o.name]=(geom(o),o.matrix_world.copy())
bpy.ops.wm.open_mainfile(filepath=str(R/r['fixture_source_native']));source={q['source']:(geom(bpy.data.objects[q['source']]),bpy.data.objects[q['source']].matrix_world.copy())for q in r['rigid_clones']};images={hashlib.sha256(bytes(n.image.packed_file.data)).hexdigest()for name in source for m in bpy.data.objects[name].data.materials if m and m.use_nodes for n in m.node_tree.nodes if n.type=='TEX_IMAGE'and n.image and n.image.packed_file}
bpy.ops.wm.open_mainfile(filepath=str(D/'FamilyD16StaffReceiving_r001.blend'))
for name,(g,m)in prior.items():
 o=bpy.data.objects[name.replace('Q15_','F16_')];expected=m;assert geom(o)==g and max(abs(expected[i][j]-o.matrix_world[i][j])for i in range(4)for j in range(4))<.0001,(name,geom(o)==g,max(abs(expected[i][j]-o.matrix_world[i][j])for i in range(4)for j in range(4)))
for row in r['rigid_clones']:
 o=bpy.data.objects[row['name']];g,m=source[row['source']];assert geom(o)==g;assert abs(Matrix(row['rigid_matrix_blender']).determinant()-1)<.0001;expected=Matrix(row['rigid_matrix_blender'])@m;assert max(abs(expected[i][j]-o.matrix_world[i][j])for i in range(4)for j in range(4))<.0001
actual={hashlib.sha256(bytes(im.packed_file.data)).hexdigest()for im in bpy.data.images if im.packed_file};assert images<=actual
before={o.name:sig(o)for o in bpy.data.objects if o.type=='MESH'};assert len(before)==76
bpy.ops.export_scene.gltf(filepath='/workspace/family-d16-integration/FRESH.glb',export_format='GLB',use_selection=True,export_yup=True,export_extras=False);assert Path('/workspace/family-d16-integration/FRESH.glb').read_bytes()==(D/r['file']).read_bytes()
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.ops.import_scene.gltf(filepath=str(D/r['file']));after={o.name:sig(o)for o in bpy.data.objects if o.type=='MESH'};assert before==after
report={'status':'PASS','original44_architectural_meshes_verified_as_reflected_derivative':len(prior),'rigid_fixture_meshes':len(r['rigid_clones']),'source_image_payloads':len(images),'native_export_meshes':len(before),'fixed_geometry_rounding_m':.0001,'fresh_export_byte_identical':True,'runtime_or_visual_acceptance':False};(D/'NATIVE_VERIFICATION.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
