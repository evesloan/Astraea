"""Fresh r006 geometry/preservation/receiving checks, not engineering acceptance."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path(__file__).resolve().parent;R=P.parents[3]
code=(P.parent/'thermal_targets'/'author_entries.py').read_text();exec(code[code.index('def digest'):code.index('provenance=')])
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
c=json.loads((P/'ROOM_CONTRACT.json').read_text());assert sha(R/c['native'])==c['native_sha256'];assert sha(R/c['source_context'])==c['source_context_sha256'];assert sha(P/'TidalNorthRoom_r005.blend')==c['prior_refinement_native_sha256']
bpy.ops.wm.open_mainfile(filepath=str(R/c['native']));S=bpy.context.scene;checks={};errors=[]
def record(n,v):
 checks[n]=bool(v)
 if not v:errors.append(n)
record('all_424_original_context_meshes_exact',all(digest(bpy.data.objects[n])==h for n,h in c['original_context_meshes'].items()))
record('authored_material_uv_is_primary',all(len(bpy.data.objects[n].data.uv_layers)==1 and bpy.data.objects[n].data.uv_layers[0].name=='UV0' and bpy.data.objects[n].data.uv_layers[0].active_render for n in c['new_meshes']))
record('all_selected_new_meshes_exact',all(digest(bpy.data.objects[n])==h for n,h in c['new_meshes'].items()))
record('all_original_packed_resources_exact',all(bpy.data.images.get(n) and bpy.data.images[n].packed_file and hashlib.sha256(bpy.data.images[n].packed_file.data).hexdigest()==h for n,h in c['original_packed_images'].items()))
cache={}
def tree(name):
 if not name.startswith(('G6_','D08_')):name='G6_TIDAL__'+name
 if name not in cache:
  o=bpy.data.objects[name];cache[name]=BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[list(f.vertices) for f in o.data.polygons])
 return cache[name]
def ray(name,p,d,dist):return tree(name).ray_cast(xyz(p),xyz(d),dist)
for k,z in enumerate([-433.5,-425.5,-417.8,-409.5]):
 base=49.8+(28-abs(z+432))/28+.255;beam='D08_directory_02__vault_rise1_'+('0' if z<-432 else '1');hit=ray(beam,(42,base-.8,z),(0,1,0),1.0)
 record('hanger_to_actual_retained_vault_'+str(k),hit[0] is not None and base-.48>=hit[0].z and base-.48-hit[0].z<.06)
 record('hanger_actual_cove_contact_'+str(k),bool(tree('cove_hanger_shoe_'+str(k)).overlap(tree('recovery_cove_'+str(int((z+437)/3.2))))))
for k,z in enumerate([-432,-412]):
 hits=[ray('recovery_cove_'+str(j),(49.7,48.37,z),(0,-1,0),.05) for j in range(10)]
 record('mounted_cove_receiver_'+str(k),any(h[0] is not None and abs(h[0].z-48.35)<.0001 for h in hits))
for k in range(2):
 for j in range(3):
  name='gallery_guard_spigot_'+str(k)+'_'+str(j);o=bpy.data.objects['G6_TIDAL__'+name];p=o.matrix_world.translation;game=(p.x,p.z+.1,-p.y);hit=ray('wet_gallery',game,(0,-1,0),.25)
  record(name+'_source_deck_contact',hit[0] is not None and abs(hit[0].z-44.9)<.0001)
# Header touches real roof; it remains above the unchanged transfer hardware.
record('foyer_roof_closes_to_actual_southern_exit',bool(tree('central_foyer_exit_spandrel').overlap(tree('vault_infill_8'))))
record('framed_threshold_meets_selected_roof',bool(tree('threshold_arch_spandrel').overlap(tree('vault_infill_0'))))
clashes=[]
for n in ['threshold_arch_spandrel','threshold_cove_return','threshold_west_jamb','threshold_east_jamb','central_foyer_exit_spandrel','central_cove_exit_head','central_exit_west_jamb']:
 for name in c['original_context_meshes']:
  if name.startswith('G6_SUPPORT_02__') and tree(n).overlap(tree(name)):clashes.append([n,name])
record('threshold_clear_of_retained_transfer_stations',not clashes)
record('piers_removed_above_unchanged_walkway',all(not bpy.data.objects.get('G6_TIDAL__cove_pier_'+str(k)) for k in range(3)))
record('central_pavilion_has_explicit_successor',any(n.startswith('G6_REST_02__bay_1_') for n in c['prior_recovery_runtime_exclusions']) and 'G6_TIDAL__central_seat_niche_crown' in c['new_meshes'])
record('new_source_below_protected_upper_deck',max((o.matrix_world@v.co).z for o in S.objects if o.type=='MESH' and o.name in c['new_meshes'] for v in o.data.vertices)<51.55)
# First-hit outward normals reject a source located inside an opaque closed mesh.
origin_clashes=[]
for f in c['fittings']:
 point=xyz(f['source_xyz'])
 for name,role in c['new_mesh_roles'].items():
  if role not in ['architecture','fixture_lens']:continue
  o=bpy.data.objects[name];vs=[o.matrix_world@v.co for v in o.data.vertices]
  if not all(min(v[k] for v in vs)<point[k]<max(v[k] for v in vs) for k in range(3)):continue
  direction=Vector((1,.371,.213)).normalized();hit=tree(name).ray_cast(point,direction,100)
  if hit[0] is not None and hit[1].dot(direction)>0:origin_clashes.append([f['id'],name])
record('all_eight_origins_outside_opaque_housings_and_stems',not origin_clashes)
record('no_new_room_capacity_floor_owner',c['new_room_or_capacity_or_floor_owner']==0 and not c['original_shell_and_vault_changed'])
bpy.ops.object.select_all(action='DESELECT')
for n in c['new_meshes']:bpy.data.objects[n].select_set(True)
p=P/'FRESH_SELECTED_REEXPORT008.glb';bpy.ops.export_scene.gltf(filepath=str(p),export_format='GLB',use_selection=True,export_extras=True,export_cameras=False,export_lights=False,export_materials='EXPORT')
record('fresh_saved_native_export_and_runtime_match',sha(p)==c['export_sha256']==sha(R/c['runtime_addition']))
out={'status':'PASS' if not errors else 'HOLD','checks':checks,'errors':errors,'original_context_meshes':len(c['original_context_meshes']),'new_meshes':len(c['new_meshes']),'source_native_sha256':c['native_sha256'],'export_sha256':c['export_sha256'],'threshold_transfer_clashes':clashes,'opaque_origin_clashes':origin_clashes,'scope':'Fresh native preservation/re-export, actual vault-hanger/cove/guard contacts, threshold roof joint/parked transfer clearance and source ceiling bound. No structural-load, occupied transfer, broad species or consolidated shared enclosure acceptance.'}
(P/'NATIVE_PROOF008.json').write_text(json.dumps(out,indent=2)+'\n');print('TIDAL REFINEMENT NATIVE',out['status'],errors);assert not errors
