"""Fresh scoped recovery-fit verification, immutable context and source joints."""
import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path(__file__).resolve().parent;R=P.parents[3];ENTRY=P.parent/'thermal_targets';code=(ENTRY/'author_entries.py').read_text();exec(code[code.index('def digest'):code.index('provenance=')])
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def bounds(o):
 vs=[o.matrix_world@v.co for v in o.data.vertices];return [[min(v[k] for v in vs),max(v[k] for v in vs)] for k in range(3)]
def tree(o):return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[list(f.vertices) for f in o.data.polygons])
def inside(p,t):
 x,z=p;s=[(b[0]-a[0])*(z-a[1])-(b[1]-a[1])*(x-a[0]) for a,b in zip(t,t[1:]+t[:1])];return min(s)>=-1e-7 or max(s)<=1e-7
floors=json.loads((R/'Game/data/generated/received_structural_meshes.json').read_text())['regions'];results=[]
for spec in json.loads((P/'THERMAL_RECOVERY_CONTRACT.json').read_text())['rooms']:
 assert sha(R/spec['source_context'])==spec['source_context_sha256'];assert sha(R/spec['native'])==spec['native_sha256'];bpy.ops.wm.open_mainfile(filepath=str(R/spec['native']));key=spec['programme_key'];i=key[-2:];prefix='G6_REST_'+i+'__'
 for n,h in spec['original_context_meshes'].items():assert digest(bpy.data.objects[n])==h,n
 for n,h in spec['original_packed_images'].items():assert hashlib.sha256(bpy.data.images[n].packed_file.data).hexdigest()==h,n
 for n,h in spec['new_meshes'].items():assert digest(bpy.data.objects[n])==h,n
 if spec['corner_fixture_repair']:
  for old,new in spec['corner_fixture_repair']['original_source_parts_to_successors'].items():
   a=bpy.data.objects[old];b=bpy.data.objects[new];assert [list(v.co) for v in a.data.vertices]==[list(v.co) for v in b.data.vertices];assert [list(f.vertices) for f in a.data.polygons]==[list(f.vertices) for f in b.data.polygons];assert [m.name for m in a.data.materials]==[m.name for m in b.data.materials];assert [[list(q.uv) for q in u.data] for u in a.data.uv_layers]==[[list(q.uv) for q in u.data] for u in b.data.uv_layers];assert (b.matrix_world.translation-a.matrix_world.translation-Vector((2,-2,0))).length<.00001
 for f in spec['optional_existing_fixture_bindings']:
  a=bounds(bpy.data.objects[f['source_mesh']]);actual=[a[0],a[2],[-a[1][1],-a[1][0]]];assert max(abs(actual[k][j]-f['source_mesh_bounds_xyz'][k][j]) for k in range(3) for j in range(2))<.002;source=[sum(actual[0])/2,actual[1][0]-.025,sum(actual[2])/2];assert max(abs(source[k]-f['source_xyz'][k]) for k in range(3))<.0001
 old_bounds={n:bounds(bpy.data.objects[n]) for n in spec['original_context_meshes']};checks=0;feet=[];mounts=[]
 for n in spec['new_meshes']:
  o=bpy.data.objects[n];a=bounds(o)
  for old,b in old_bounds.items():
   if not all(min(a[k][1],b[k][1])-max(a[k][0],b[k][0])>.003 for k in range(3)):continue
   checks+=1;assert not tree(o).overlap(tree(bpy.data.objects[old])),('source collision',n,old)
  if '_foot_' in n or '_table_foot_' in n or n.endswith('corner_light2_post'):
   vs=[o.matrix_world@v.co for v in o.data.vertices];low=min(v.z for v in vs);assert abs(low-44)<.001
   for v in vs:
    if abs(v.z-low)>.0001:continue
    p=[v.x,v.z,-v.y];owners=[r['id'] for r in floors if r['id'].startswith(key+'_') and any(inside([p[0],p[2]],t) for t in r['triangles'])];assert owners,(n,p);feet.append({'part':n,'xyz':p,'existing_floor_owners':owners})
 for fitting in spec['new_task_fittings']:
  bits=fitting['id'].split('_recovery_')[1].split('_task_');j=bits[0];k=bits[1].split('_')[0];drop=bpy.data.objects[prefix+'bay_'+j+'_task_drop_'+k];tie=bpy.data.objects[prefix+'bay_'+j+'_task_cross_tie_'+k];a=bounds(drop);b=bounds(tie)
  p=Vector((drop.location.x,drop.location.y,a[2][1]));nearest=tree(tie).find_nearest(p);assert nearest[0] is not None and nearest[3]<.026,('drop tie joint',fitting['id'],nearest)
  # Both tie ends meet the actual different front/rear beam heights.
  for side in ['front','rear']:
   beam=bpy.data.objects[prefix+'bay_'+j+'_long_beam_'+side];assert tree(tie).overlap(tree(beam)),('tie beam joint',fitting['id'],side)
  mounts.append({'id':fitting['id'],'drop_cross_tie_and_both_beams_contact':True})
 # Exact existing fitting bounds and original bench bounds are compared with
 # the authoritative entry001 runtime, not a reconstructed entrance native.
 expected={b['existing_bench_mesh']:b['existing_bench_bounds_xyz'] for b in spec['bays']};expected.update({f['original_source_mesh']:f['original_source_mesh_bounds_xyz'] for f in spec['optional_existing_fixture_bindings']})
 bpy.ops.object.select_all(action='DESELECT')
 for n in spec['new_meshes']:bpy.data.objects[n].select_set(True)
 repeat=Path('/workspace/group6-repeat-export')/Path(spec['export']).name;bpy.ops.export_scene.gltf(filepath=str(repeat),export_format='GLB',use_selection=True,export_extras=True,export_cameras=False,export_lights=False,export_materials='EXPORT');assert sha(repeat)==spec['export_sha256']
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(R/spec['current_room_runtime']));assert sha(R/spec['current_room_runtime'])==spec['current_room_runtime_sha256']
 current=[]
 for n,b in expected.items():
  o=bpy.data.objects[n];a=bounds(o);actual=[a[0],a[2],[-a[1][1],-a[1][0]]];assert max(abs(actual[k][j]-b[k][j]) for k in range(3) for j in range(2))<.002,n;current.append(n)
 results.append({'programme_key':key,'status':'PASS','immutable_context_meshes_checked':len(spec['original_context_meshes']),'packed_context_images_checked':len(spec['original_packed_images']),'new_meshes_checked':len(spec['new_meshes']),'narrow_original_overlap_checks':checks,'ground_contacts':feet,'fitting_joints':mounts,'exact_current_runtime_original_bench_and_lens_bounds_checked':current,'repeat_export_byte_identical':True,'native_sha256':spec['native_sha256'],'export_sha256':spec['export_sha256'],'new_seats_rooms_floor_owners_or_capacity':0,'acoustic_dayrest_species_service_load_final_art_accepted':False})
(P/'SAVED_NATIVE_VERIFICATION.json').write_text(json.dumps({'status':'PASS','rooms':results},indent=2)+'\n');print('RECOVERY NATIVE PASS',[(r['programme_key'],len(r['ground_contacts']),len(r['fitting_joints']),r['narrow_original_overlap_checks']) for r in results])
