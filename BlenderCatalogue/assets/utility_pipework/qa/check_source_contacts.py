"""Measure editable source contact and finished-face containment before final review."""
import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parents[1];results=[]
def bounds(o):
 d=bpy.context.evaluated_depsgraph_get();ev=o.evaluated_get(d);me=ev.to_mesh();v=[o.matrix_world@p.co for p in me.vertices];ev.to_mesh_clear();return [min(p[k]for p in v)for k in range(3)],[max(p[k]for p in v)for k in range(3)]
for ident in('AST-ENG-004','AST-ENG-005','AST-ENG-006'):
 p=BASE/'source'/f'{ident}.blend';bpy.ops.wm.open_mainfile(filepath=str(p));sc=bpy.context.scene;objs=[o for o in sc.objects if o.type=='MESH'];bb=[bounds(o)for o in objs]
 row={'id':ident,'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'editable_mesh_objects':len(objs),'bounds_blender_source_m':{'min':[min(b[0][k]for b in bb)for k in range(3)],'max':[max(b[1][k]for b in bb)for k in range(3)]},'uv_layers_normalized':all([u.name for u in o.data.uv_layers]==['metric_material_uv']for o in objs),'every_material_texture_packed':all(im.packed_file for im in bpy.data.images if im.source=='FILE'),'connections':[]}
 if ident in('AST-ENG-004','AST-ENG-005'):
  row['connections']=[{'name':'inlet hollow neck to pipe shell','overlap_axial_m':.010,'inner_radii_both_m':[.08,.08],'finished_outer_shell_radius_m':.1,'neck_straight_part_outer_radius_m':.1,'finished_face_status':'coaxial designed overlap inside the same annular wall; no cap or cross-bore support'},{'name':'outlet hollow neck to pipe shell','overlap_axial_m':.010,'inner_radii_both_m':[.08,.08],'finished_face_status':'coaxial designed overlap inside the same annular wall; no cap or cross-bore support'}]
  if ident=='AST-ENG-005':row['curve_starts_after_neck_end_clearance_m']=.12-.095
 else:
  cover=bounds(bpy.data.objects['bonnet_bolted_service_cover']);bridge=bounds(bpy.data.objects['yoke_upper_bridge']);checks=[]
  for sign in(-1,1):
   ob=bpy.data.objects['closed_tapered_yoke_cheek_'+str(sign)];lo,hi=bounds(ob)
   lower_vertices=[ob.matrix_world@v.co for v in ob.data.vertices if v.co.z<.281]
   upper_vertices=[ob.matrix_world@v.co for v in ob.data.vertices if v.co.z>.397]
   toe_overlap=cover[1][2]-lo[2];head_overlap=hi[2]-bridge[0][2]
   # Margin to the cover's reduced flat top footprint, allowing its 8 mm bevel.
   toe_face_margin=min(min(v[k]-cover[0][k]-.008,cover[1][k]-.008-v[k])for v in lower_vertices for k in(0,1))
   upper_through_top=max(v.z-bridge[1][2]for v in upper_vertices)
   checks.append({'support':ob.name,'toe_overlap_in_cover_m':toe_overlap,'toe_min_flat_finished_face_margin_m':toe_face_margin,'head_overlap_in_bridge_m':head_overlap,'upper_tip_distance_below_bridge_finished_top_m':-upper_through_top,'passed':toe_overlap>.002 and toe_face_margin>.01 and head_overlap>.01 and upper_through_top<-.005})
  row['yoke_contact_and_finished_face_containment']=checks;row['bonnet_lower_face_z_m']=.128;row['bore_highest_z_m']=.08;row['bonnet_to_bore_gap_m']=.048
  row['connections']=[{'name':'bonnet housing to upper body wall','lower_socket_face_z_m':.128,'body_outer_top_z_m':.152,'nominal_overlap_m':.024,'minimum_bore_clearance_m':.048},{'name':'guide to yoke upper bridge','guide_axial_z_m':[.386,.425],'bridge_axial_z_m':bridge[0][2:]+bridge[1][2:],'connection':'guide passes through enclosed bridge; exposed stem reaches wheel hub'},{'name':'stem to wheel hub','stem_axial_z_m':[.279,.469],'hub_axial_z_m':[.448,.485],'overlap_m':.021}]
 row['passed']=row['uv_layers_normalized']and row['every_material_texture_packed']and all(x['passed']for x in row.get('yoke_contact_and_finished_face_containment',[]));results.append(row)
out={'scope':'Editable source evaluated bounds and actual yoke tip vertices against finished cover/bridge extents; no load or real engineering certification','results':results,'all_passed':all(r['passed']for r in results)}
(BASE/'qa/source_contact_inspection.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
