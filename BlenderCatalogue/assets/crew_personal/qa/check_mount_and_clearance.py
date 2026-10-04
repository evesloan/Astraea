"""Read actual sibling/source geometry; never edit receiver. Frame is relative QA only."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
BASE=Path(__file__).resolve().parents[1];CAT=BASE.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
 bpy.ops.wm.open_mainfile(filepath=str(p));bpy.context.view_layer.update();out={};dg=bpy.context.evaluated_depsgraph_get()
 for o in bpy.context.scene.objects:
  if o.type!='MESH':continue
  e=o.evaluated_get(dg);m=e.to_mesh();vs=[o.matrix_world@v.co for v in m.vertices];ps=[list(q.vertices)for q in m.polygons];out[o.name]={'vs':vs,'tree':BVHTree.FromPolygons(vs,ps)};e.to_mesh_clear()
 return out
rp=CAT/'assets/crew_rest/source/AST-CRW-001.blend';mp=BASE/'source/AST-CRW-004.blend';r=read(rp);m=read(mp);offset=Vector((-.26,2.14,.88));contract=json.loads((BASE/'mount_contract.json').read_text());head=r['001_flat_headboard']['tree'];contacts=[]
for w in contract['contact_witnesses']:
 p=Vector(w['module_source_m']);a=m['headboard_mount_backplate']['tree'].find_nearest(p);b=head.find_nearest(p+offset);contacts.append({'module_source_m':list(p),'frame_source_m':list(p+offset),'module_surface_distance_m':a[3],'frame_surface_distance_m':b[3],'normal_dot':a[1].dot(b[1]),'passes':a[3]<1e-6 and b[3]<1e-6 and a[1].dot(b[1])<-.999})
allpts=[v+offset for q in m.values()for v in q['vs']];lo=[min(v[k]for v in allpts)for k in range(3)];hi=[max(v[k]for v in allpts)for k in range(3)];checks=[]
for name in['001_shaped_single_mattress','001_shaped_head_pillow','001_draped_folded_blanket']:
 vs=r[name]['vs'];rl=[min(v[k]for v in vs)for k in range(3)];rh=[max(v[k]for v in vs)for k in range(3)];gaps=[max(rl[k]-hi[k],lo[k]-rh[k])for k in range(3)];checks.append({'receiver_part':name,'actual_bounds_source':{'min':rl,'max':rh},'full_module_axis_separations_m':gaps,'passes':max(gaps)>0})
restlo=[-.40,.30,.565];resthi=[.40,1.52,1.10];restgaps=[max(restlo[k]-hi[k],lo[k]-resthi[k])for k in range(3)]
shelfpts=[v+offset for v in m['clipped_personal_shelf']['vs']];pillowtop=max(v.z for v in r['001_shaped_head_pillow']['vs']);shelflow=min(v.z for v in shelfpts)
row={'scope':'Actual evaluated sources in agreed relative frame mounting. Complete AABBs prove disjointness where one axis has positive gap; no body/head movement or structural-load certification. Central use prism declared by receiver author and deliberately retained.','source_hashes':{'AST-CRW-001':sha(rp),'AST-CRW-004':sha(mp)},'complete_module_bounds_in_frame':{'min':lo,'max':hi},'physical_mount_checks':contacts,'bedding_full_module_separation':checks,'central_rest_use_prism':{'min_source_m':restlo,'max_source_m':resthi,'separation_by_axis_m':restgaps,'passes':max(restgaps)>0},'shelf_to_pillow_vertical_gap_m':shelflow-pillowtop,'all_passed':all(x['passes']for x in contacts+checks)and max(restgaps)>0};(BASE/'qa/mount_and_clearance_checks.json').write_text(json.dumps(row,indent=2)+'\n');print(json.dumps(row,indent=2))
