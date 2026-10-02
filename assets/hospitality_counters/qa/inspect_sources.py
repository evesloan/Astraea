"""Lightweight reload/contact checks on saved editable sources. No render."""
import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
BASE=Path(__file__).resolve().parents[1]
def geom(ob):
 dg=bpy.context.evaluated_depsgraph_get();e=ob.evaluated_get(dg);me=e.to_mesh();me.calc_loop_triangles();v=[ob.matrix_world@x.co for x in me.vertices];f=[list(t.vertices) for t in me.loop_triangles];e.to_mesh_clear();return v,f

def bounds(v):return {'min_m':[min(x[k] for x in v) for k in range(3)],'max_m':[max(x[k] for x in v) for k in range(3)]}
def near(ob,p):
 v,f=geom(ob);return BVHTree.FromPolygons(v,f,all_triangles=True).find_nearest(Vector(p))[3]
records=[]
for path in sorted((BASE/'source').glob('AST-*.blend')):
 bpy.ops.wm.open_mainfile(filepath=str(path));mesh={o.name:o for o in bpy.context.scene.objects if o.type=='MESH'};bb={n:bounds(geom(o)[0]) for n,o in mesh.items()};lo=[min(b['min_m'][k] for b in bb.values()) for k in range(3)];hi=[max(b['max_m'][k] for b in bb.values()) for k in range(3)];rec=json.loads((BASE/f'{path.stem}.manifest.json').read_text())
 checks={'bound_matches_manifest':all(abs(a-b)<1e-6 for a,b in zip(lo+hi,rec['bounds_blender_z_up']['min_m']+rec['bounds_blender_z_up']['max_m'])),'floor_contact_at_zero':abs(lo[2])<1e-7,'worktop_at_090':abs(hi[2]-.9)<1e-7,'identity_scale':all(max(abs(s-1) for s in o.scale)<1e-7 for o in mesh.values()),'semantic_uv_names':all(o.data.uv_layers.active.name=='metric_material_uv' for o in mesh.values()),'source_no_lights_cameras':not any(o.type in('LIGHT','CAMERA') for o in bpy.context.scene.objects),'packed_source_images':all(n.image.packed_file is not None for o in mesh.values() for m in o.data.materials for n in m.node_tree.nodes if n.type=='TEX_IMAGE')}
 measures={}
 for p in rec['physical_contacts']:
  d=near(mesh[p['surface']],p['source_m']);measures[p['name']+'_distance_m']=d;checks[p['name']+'_on_surface']=d<1e-6
 measures['base_shelf_to_front_plinth_gap_m']=bb['load_bearing_base_shelf']['min_m'][2]-bb['recessed_front_floor_plinth']['max_m'][2];checks['base_support_contact']=abs(measures['base_shelf_to_front_plinth_gap_m'])<1e-6
 measures['terminal_to_stone_gap_m']=bb['continuous_eased_stone_worktop']['min_m'][2]-bb['entry_closed_shaped_terminal_bulkhead']['max_m'][2];checks['top_supported_at_ends']=abs(measures['terminal_to_stone_gap_m'])<1e-6
 if path.stem=='AST-HSP-001':
  pan=bb['drawer_open_pan_bottom'];front=bb['drawer_ivory_front'];rail=bb['rear_top_support_rail'];runner=bb['fixed_drawer_runner_0.83'];measures['drawer_pan_to_runner_vertical_gap_m']=pan['min_m'][2]-runner['max_m'][2];measures['left_runner_under_pan_overlap_m']=runner['max_m'][0]-pan['min_m'][0];measures['drawer_front_to_upper_rail_vertical_clearance_m']=rail['min_m'][2]-front['max_m'][2];checks['runner_supports_drawer_pan']=abs(measures['drawer_pan_to_runner_vertical_gap_m'])<1e-6 and measures['left_runner_under_pan_overlap_m']>.006;checks['drawer_clears_upper_rail']=measures['drawer_front_to_upper_rail_vertical_clearance_m']>.002
  for key,x in [('left',.4),('centre',1.2),('right',2.0)]:
   shelf=mesh[key+'_open_service_shelf'] if key!='centre' else mesh['centre_lower_service_shelf'];measures[key+'_shelf_point_distance_m']=near(shelf,[x,0,.466]);checks[key+'_shelf_real_surface']=measures[key+'_shelf_point_distance_m']<1e-6
 else:
  measures['curved_shelf_to_radial_support_gap_m']=bb['curved_open_service_shelf']['min_m'][2]-bb['curved_shelf_radial_support_1']['max_m'][2];checks['curved_shelf_supported']=abs(measures['curved_shelf_to_radial_support_gap_m'])<1e-6
 records.append({'catalogue_id':path.stem,'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'checks':checks,'measurements':measures,'bounds':{'min_m':lo,'max_m':hi},'source_mesh_count':len(mesh),'retained_modifiers':sum(len(o.modifiers) for o in mesh.values()),'part_bounds':bb,'passed':all(checks.values())})
report={'method':'Reload each saved .blend and inspect evaluated source meshes; actual nearest triangles for support contacts','assets':records,'all_passed':all(r['passed'] for r in records)};(BASE/'qa/source_reload_checks.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps([{r['catalogue_id']:r['checks']} for r in records],indent=2));assert report['all_passed']
