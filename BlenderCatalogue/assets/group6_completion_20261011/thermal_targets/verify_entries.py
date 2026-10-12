"""Fresh reopen of exact source successors and affected current GLB fit."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path(__file__).resolve().parent;R=P.parents[3]
code=(P/'author_entries.py').read_text();exec(code[code.index('def digest'):code.index('provenance=')])
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def inside(p,ring):
 x,z=p;flag=False
 for a,b in zip(ring,ring[1:]+ring[:1]):
  if (a[1]>z)!=(b[1]>z) and x<(b[0]-a[0])*(z-a[1])/(b[1]-a[1])+a[0]:flag=not flag
 return flag
regions=json.loads((R/'Game/data/generated/received_structural_meshes.json').read_text())['regions'];results=[]
for spec in json.loads((P/'THERMAL_ENTRY_CONTRACT.json').read_text())['rooms']:
 key=spec['programme_key'];bpy.ops.wm.open_mainfile(filepath=str(R/spec['native']))
 for n,h in spec['original_meshes'].items():assert digest(bpy.data.objects[n])==h,n
 for n,h in spec['new_meshes'].items():assert digest(bpy.data.objects[n])==h,n
 for n,h in spec['original_packed_images'].items():assert hashlib.sha256(bpy.data.images[n].packed_file.data).hexdigest()==h,n
 contacts=[]
 floor_rings=[r['rings'][0] for r in regions if r['id'].startswith(key+'_')]
 for n in spec['new_meshes']:
  o=bpy.data.objects[n]
  if not ('dry_bridge' in n or '_post_' in n):continue
  vs=[o.matrix_world@v.co for v in o.data.vertices];low=min(v.z for v in vs)
  for v in vs:
   if abs(v.z-low)>.0001:continue
   p=[v.x,v.z,-v.y]
   if abs(low-44)<.001:ok=any(inside([p[0],p[2]],ring) for ring in floor_rings)
   else:
    ok=False
    for entry in spec['entries']:
     bed=bpy.data.objects[entry['original_bed_mesh']];verts=[bed.matrix_world@q.co for q in bed.data.vertices];bvh=BVHTree.FromPolygons(verts,[list(f.vertices) for f in bed.data.polygons]);hit=bvh.ray_cast(Vector((v.x,v.y,low+.02)),Vector((0,0,-1)),.04);ok=ok or (hit[0] is not None and abs(hit[0].z-low)<.001)
   contacts.append({'part':n,'xyz':p,'supported':ok});assert ok,(n,p)
 bpy.ops.object.select_all(action='DESELECT')
 for n in spec['new_meshes']:bpy.data.objects[n].select_set(True)
 repeat=Path('/workspace/group6-repeat-export')/Path(spec['new_export']).name;repeat.parent.mkdir(exist_ok=True)
 bpy.ops.export_scene.gltf(filepath=str(repeat),export_format='GLB',use_selection=True,export_extras=True,export_cameras=False,export_lights=False,export_materials='EXPORT');assert sha(repeat)==spec['new_export_sha256']
 # Current entrance successor is authoritative for runtime. Verify every scoped
 # changed/bed mesh in that exact export against the preserved reviewed source.
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(R/spec['current_room_runtime']))
 affected=[]
 for name,expected in spec['affected_original_bounds_xyz'].items():
  o=bpy.data.objects.get(name);assert o is not None,name
  vs=[o.matrix_world@v.co for v in o.data.vertices];a=[[min(v[j] for v in vs),max(v[j] for v in vs)] for j in range(3)];actual=[a[0],a[2],[-a[1][1],-a[1][0]]]
  assert max(abs(actual[j][k]-expected[j][k]) for j in range(3) for k in range(2))<.002,name;affected.append(name)
 results.append({'programme':key,'status':'PASS','native_sha256':spec['native_sha256'],'original_meshes_checked':len(spec['original_meshes']),'original_packed_images_checked':len(spec['original_packed_images']),'new_meshes_checked':len(spec['new_meshes']),'new_support_points':contacts,'exact_current_export_affected_meshes_checked':affected,'fresh_repeat_export_identical':True,'fresh_export_sha256':sha(repeat),'scope':'Original reviewed native semantics, current affected mesh bounds and actual original compiler/bed support only. Later entrance native absent; no replacement or whole-scene/final-art/gameplay acceptance.'})
(P/'SAVED_ENTRY_VERIFICATION.json').write_text(json.dumps({'status':'PASS','rooms':results},indent=2)+'\n');print('THERMAL SAVED NATIVE PASS',[(x['programme'],len(x['new_support_points'])) for x in results])
