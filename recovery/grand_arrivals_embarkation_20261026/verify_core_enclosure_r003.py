import bpy,json,pathlib,hashlib,collections
from mathutils import Vector
R=pathlib.Path(__file__).resolve().parents[2];D=R/'Game/grand_arrivals_tram_20261026/r003'
b=json.loads((D/'BUILD.json').read_text())
for p,row in b['outputs'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==row['sha256']
def snapshot():
 out={}
 for o in bpy.data.objects:
  if o.type!='MESH':continue
  o.data.calc_loop_triangles();assert o.data.uv_layers.active
  tris=[]
  for t in o.data.loop_triangles:
   v=[]
   for vi,li in zip(t.vertices,t.loops):
    p=o.matrix_world@o.data.vertices[vi].co;u=o.data.uv_layers.active.data[li].uv
    v.append(tuple(round(x,4) for x in (*p,*u)))
   tris.append(tuple(sorted(v)))
  out[o.name]={'triangles':collections.Counter(tris),'materials':[m.name.split('.')[0] for m in o.data.materials]}
 return out
def clear():
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.wm.open_mainfile(filepath=str(next(R/p for p in b['outputs'] if p.endswith('.blend'))));native=snapshot()
clear();bpy.ops.import_scene.gltf(filepath=str(D/'ForeMidCoreEnclosure.glb'));runtime=snapshot()
assert native==runtime,'Native/runtime geometry, UV or material divergence'
clear();bpy.ops.import_scene.gltf(filepath=str(R/b['source']));original=snapshot()
preserved=0
for name,row in original.items():
 assert runtime[name]['materials']==row['materials']
 for tri,n in row['triangles'].items():
  points=[Vector((v[0],v[2],-v[1])) for v in tri]
  fixture=all(5.278<=p.x<=5.922 and 11.538<=p.y<=11.762 and -.282<=p.z<=.282 for p in points)
  role=row['materials'][0]
  intersects=any(c['role']==role and all(max(p[i] for p in points)>=c['lo'][i]-.001 and min(p[i] for p in points)<=c['hi'][i]+.001 for i in range(3)) for c in b['cut_volumes_local'])
  if not fixture and not intersects:
   assert runtime[name]['triangles'][tri]>=n,(name,tri)
   preserved+=n
receipt={'passed':True,'native_runtime_objects':len(native),'native_runtime_triangle_uv_material_equality_0_1mm':True,'outside_original_triangles_preserved':preserved,'source_sha256':b['source_sha256'],'scope':'Geometry/UV/material identity outside scoped openings; not installed or visual acceptance'}
(D/'NATIVE_RUNTIME_CHECK.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
