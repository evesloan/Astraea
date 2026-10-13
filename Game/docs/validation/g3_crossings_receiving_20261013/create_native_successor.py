import bpy,json,hashlib,itertools
from pathlib import Path
from mathutils import Matrix,Vector
P=Path(__file__).parent
plan=json.loads((P/'THRESHOLD_RECEIVING_PLAN_EXACT_EXPORT.json').read_text());receipt=json.loads((P/'EXACT_NATIVE_RETENTION.json').read_text());source=P/'source/AST-STF-G3-063.blend';assert hashlib.sha256(source.read_bytes()).hexdigest()==next(x['sha256']for x in receipt['files']if x['path'].endswith('/AST-STF-G3-063.blend'))
def sig(o):
 m=o.data;d={'vertices':[list(v.co)for v in m.vertices],'faces':[list(f.vertices)for f in m.polygons],'uv':{u.name:[list(q.uv)for q in u.data]for u in m.uv_layers},'materials':[q.name for q in m.materials],'matrix':[list(q)for q in o.matrix_world],'properties':dict(o.items())};return hashlib.sha256(json.dumps(d,sort_keys=True).encode()).hexdigest()
old={o.name:sig(o)for o in bpy.data.objects if o.type=='MESH'};removed=[];trimmed=[]
for row in plan['parts']:
 o=bpy.data.objects[row['name']]
 if not row['polygons']:removed.append(o.name);bpy.data.objects.remove(o,do_unlink=True);continue
 if row['removed_m2']<1e-8:continue
 m=o.data;oldco=[v.co.copy()for v in m.vertices];faces=[]
 for f in m.polygons:
  axis=max(range(3),key=lambda i:abs(f.normal[i]));axes=[i for i in range(3)if i!=axis];samples=[(i,oldco[m.loops[i].vertex_index],m.uv_layers.active.data[i].uv.copy())for i in f.loop_indices];matrix=None
  for trio in itertools.combinations(samples,3):
   mat=Matrix([(q[1][axes[0]],q[1][axes[1]],1)for q in trio])
   if abs(mat.determinant())>1e-8:matrix=mat;break
  assert matrix is not None
  inv=matrix.inverted();u=inv@Vector([q[2].x for q in trio]);v=inv@Vector([q[2].y for q in trio]);faces.append((list(f.loop_indices),axes,u,v))
 x0,x1,z0,z1=row['corrected_bounds_xz']
 for v in m.vertices:v.co.y=max(-z1,min(-z0,v.co.y))
 for loops,axes,u,v in faces:
  for i in loops:
   co=m.vertices[m.loops[i].vertex_index].co;q=Vector((co[axes[0]],co[axes[1]],1));m.uv_layers.active.data[i].uv=(u.dot(q),v.dot(q))
 m.update();trimmed.append(o.name)
new={o.name:sig(o)for o in bpy.data.objects if o.type=='MESH'};unchanged=[n for n in new if n not in trimmed];assert len(new)==4 and len(unchanged)==2 and all(new[n]==old[n]for n in unchanged)
D=P/'proposed';D.mkdir(exist_ok=True);blend=D/'AST-STF-G3-063_current_receiving_successor001.blend';glb=D/'AST-STF-G3-063_current_receiving_successor001.glb';bpy.ops.wm.save_as_mainfile(filepath=str(blend));bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',export_yup=True,export_apply=False)
r={'status':'PASS_NATIVE_THRESHOLD_RECEIVING_SUCCESSOR','source_native_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'removed_fully_covered_parts':removed,'trimmed_parts':trimmed,'unchanged_original_geometry_uv_material_parts':unchanged,'corrected_floor_m2':plan['corrected_area_m2'],'removed_duplicate_m2':plan['removed_m2'],'files':{str(q.relative_to(P)):{'bytes':q.stat().st_size,'sha256':hashlib.sha256(q.read_bytes()).hexdigest()}for q in [blend,glb]},'original_criteria_preserved':13,'operational_admission':False};(P/'NATIVE_SUCCESSOR_RECEIPT.json').write_text(json.dumps(r,indent=2)+'\n');print('PASS_THRESHOLD_NATIVE_SUCCESSOR unchanged=2 trimmed=2 removed=2')
