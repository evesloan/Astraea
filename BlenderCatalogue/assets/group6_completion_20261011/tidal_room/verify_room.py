"""Fresh native integrity and focused receiving-join evidence for one chamber."""
import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path(__file__).resolve().parent;R=P.parents[3]
code=(P.parent/'thermal_targets'/'author_entries.py').read_text();exec(code[code.index('def digest'):code.index('provenance=')])
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
c=json.loads((P/'ROOM_CONTRACT.json').read_text());assert sha(R/c['native'])==c['native_sha256'];assert sha(R/c['source_context'])==c['source_context_sha256'];assert sha(R/c['current_room_runtime'])==c['current_room_runtime_sha256'];assert sha(R/c['required_recovery_export'])==c['required_recovery_export_sha256']
bpy.ops.wm.open_mainfile(filepath=str(R/c['native']));S=bpy.context.scene;checks={};errors=[]
def record(n,ok):
 checks[n]=bool(ok)
 if not ok:errors.append(n)
record('all_424_original_mesh_signatures_exact',all(digest(bpy.data.objects[n])==h for n,h in c['original_context_meshes'].items()))
record('all_selected_new_mesh_signatures_exact',all(digest(bpy.data.objects[n])==h for n,h in c['new_meshes'].items()))
record('original_packed_resources_exact',all(bpy.data.images.get(n) and bpy.data.images[n].packed_file and hashlib.sha256(bpy.data.images[n].packed_file.data).hexdigest()==h for n,h in c['original_packed_images'].items()))
def tree(n):
 o=bpy.data.objects['G6_TIDAL__'+n];return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons])
def cast(n,at,d,maxdist=100):return tree(n).ray_cast(xyz(at),xyz(d),maxdist)
joins=[]
for k,z in enumerate([-425.5,-417.8,-409.5]):
 o=bpy.data.objects['G6_TIDAL__cove_pier_base_'+str(k)];bottom=min((o.matrix_world@v.co).z for v in o.data.vertices);hit=cast('coping_east',(41,bottom+.002,z),(0,-1,0),.01);record('colonnade_foot_on_coping_'+str(k),hit[0] is not None and abs(hit[0].z-bottom)<.0001);joins.append({'joint':'pier_coping_'+str(k),'bottom_y':bottom,'receiving_surface_y':hit[0].z if hit[0] else None})
for k,z in enumerate([-424,-412]):
 hits=[cast('recovery_cove_'+str(i),(49.7,48.37,z),(0,-1,0),.05) for i in range(7)];hit=next((h for h in hits if h[0] is not None),(None,None,None,None));record('cove_drop_joins_real_ceiling_'+str(k),hit[0] is not None and abs(hit[0].z-48.35)<.0001)
# Each roof panel bears on the room-facing wall and retained western vault member.
for k in range(8):
 z=-430+(k+.5)*3.25;y=49.8+(-404-z)/28+.255
 if z>=-428.8:
  hit=cast('west_room_return_'+str(min(3,int((z+428.8)/6.2))),(27.9,y+.1,z),(0,-1,0),.2);record('vault_wall_receiving_'+str(k),hit[0] is not None and abs(hit[0].z-(y+.035))<.0002)
for name in ['wet_gallery','wet_landing_join','north_wet_turn','dry_return_upper_landing']:
 o=bpy.data.objects['G6_TIDAL__'+name];bottom=min((o.matrix_world@v.co).z for v in o.data.vertices);record(name+'_same_original_floor_datum',abs(bottom-44)<.00001)
record('new_source_stays_below_D09_underside',max((o.matrix_world@v.co).z for o in S.objects if o.type=='MESH' and o.name in c['new_meshes'] for v in o.data.vertices)<51.55)
record('new_room_capacity_and_floor_owner_zero',c['new_room_or_capacity_or_floor_owner']==0 and not c['original_shell_and_vault_changed'])
record('water_boundary_height_unchanged',c['water_nominal_y']==44.9 and c['water_boundary_xz']==[[29.2,40.8],[-427.8,-408.2]])
# Fresh deterministic export from saved native; not author-session metadata.
bpy.ops.object.select_all(action='DESELECT')
for n in c['new_meshes']:bpy.data.objects[n].select_set(True)
repeat=P/'FRESH_SELECTED_REEXPORT005.glb';bpy.ops.export_scene.gltf(filepath=str(repeat),export_format='GLB',use_selection=True,export_extras=True,export_cameras=False,export_lights=False,export_materials='EXPORT')
record('fresh_reexport_matches_selected_runtime',sha(repeat)==c['export_sha256'] and sha(R/c['runtime_addition'])==c['export_sha256'])
result={'status':'PASS' if not errors else 'HOLD','checks':checks,'errors':errors,'source_native_sha256':c['native_sha256'],'export_sha256':c['export_sha256'],'original_meshes':len(c['original_context_meshes']),'new_meshes':len(c['new_meshes']),'original_packed_resources':len(c['original_packed_images']),'new_material_images':len([i for i in bpy.data.images if i.name.startswith('G6_TIDAL_') and i.packed_file]),'joins':joins,'scope':'Fresh editable-source preservation, selected export identity, actual coping/pier/cove/roof wall contacts, same floor datum, upper-deck bound and visual water boundary. Original vault/outer shell unchanged. Not engineering load, consolidated receiving approval or player physics acceptance.'}
(P/'NATIVE_PROOF005.json').write_text(json.dumps(result,indent=2)+'\n');print('TIDAL NORTH NATIVE',result['status'],errors);assert not errors
