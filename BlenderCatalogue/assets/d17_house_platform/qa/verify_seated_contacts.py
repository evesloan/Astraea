from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];C=R.parents[1];D=json.loads((R/'source/section_contract.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(C/'assets/lower_hull_body/source/AST-HUL-001.blend'));hull=bpy.data.objects['HUL_LowerBand_00'];tree=BVHTree.FromObject(hull,bpy.context.evaluated_depsgraph_get());faces={};samples=[]
for s in D['seated_footings']:
 owner=s['source_owner'].split('/')[-1];assert owner in ['HUL_LowerBand_00','HUL_LowerBand_03'];hull=bpy.data.objects[owner];tree=BVHTree.FromObject(hull,bpy.context.evaluated_depsgraph_get())
 face=hull.data.polygons[s['witnesses'][0]['face_index']];normal=face.normal;origin=hull.data.vertices[face.vertices[0]].co
 assert normal.z>(.9 if owner=='HUL_LowerBand_00' else .4)
 # Exact retained surface plane is checked over the entire rectangular contact footprint.
 maximum_plane_error=0.;maximum_ray_error=0.
 q=s['corners_world'];x0=q[0][0];width=q[1][0]-x0;z0=min(v[2] for v in q);depth=max(v[2] for v in q)-z0;slope=(q[1][1]-q[0][1])/width
 assert abs(width-.8)<1e-6 and abs(depth-1.2)<1e-6
 for i in range(9):
  for j in range(9):
   x=x0+i*width/8;z=z0+j*depth/8;y=q[0][1]+(x-x0)*slope
   p=Vector((x,-z,y));maximum_plane_error=max(maximum_plane_error,abs((p-origin).dot(normal)))
   hit,n,fi,d=tree.ray_cast(Vector((x,-z,20)),Vector((0,0,-1)),30);assert hit is not None;assert fi==face.index;maximum_ray_error=max(maximum_ray_error,abs(hit.z-y))
 assert maximum_plane_error<1e-5 and maximum_ray_error<1e-5
 assert min(s['top_y']-v[1]for v in q)>.34
 samples.append({'centre_xz':[s['x'],s['z']],'hull_owner':owner,'same_actual_hull_polygon':face.index,'grid_rays':81,'maximum_plane_error_m':maximum_plane_error,'maximum_ray_error_m':maximum_ray_error,'minimum_positive_wedge_thickness_m':min(s['top_y']-v[1]for v in q),'footprint_contact_area_xz_m2':.96})
assert sha(C/'assets/lower_hull_body/source/AST-HUL-001.blend')==D['source_inputs']['catalogue/assets/lower_hull_body/source/AST-HUL-001.blend']
assert sha(C/'assets/lower_hull_body/exports/AST-HUL-001.glb')==D['source_inputs']['catalogue/assets/lower_hull_body/exports/AST-HUL-001.glb']
source_only_complete=True
phys=json.loads((R/'qa/parent_outer_support_census.json').read_text());phys['candidate_support_columns']+=json.loads((R/'qa/parent_original_support_census.json').read_text())['candidate_support_columns'];phys['candidate_support_columns']+=json.loads((R/'qa/d17_royalty_remaining_support_census.json').read_text())['candidate_support_columns'];diffs=[];rows=[]
for s in D['seated_footings']:
 row=next(a for a in phys['candidate_support_columns'] if abs(a['xz'][0]-s['x'])<1e-4 and abs(a['xz'][1]-s['z'])<1e-4)
 local_diffs=[]
 for a in row['base_rays']:
  xyz=a['position'];b=min(s['witnesses'],key=lambda v:abs(v['point_world'][0]-xyz[0])+abs(v['point_world'][2]-xyz[2]));diffs.append(abs(xyz[1]-b['point_world'][1]));local_diffs.append(abs(xyz[1]-b['point_world'][1]))
 rows.append({'centre_xz':[s['x'],s['z']],'hull_owner':s['source_owner'],'max_y_difference_m':max(local_diffs),'strict_1mm_comparison_pass':max(local_diffs)<.001})
 if s['source_owner'].endswith('HUL_LowerBand_00'):assert max(local_diffs)<.001
assert len(diffs)==5*len(D['seated_footings'])
comparison_pass=max(diffs)<.001
runtime_delta={'strict_1mm_comparison_pass':comparison_pass,'per_seat':rows,'maximum_absolute_y_m':max(diffs),'scope':'Previously measured retained-hull runtime rays versus new source seats; new footing runtime not imported'}
(R/'qa/seated_contact_verification.json').write_text(json.dumps({'pass':comparison_pass,'source_plane_seats_pass':True,'runtime_adoption_hold':not comparison_pass,'scope':'Exact source-plane seats separately verified; strict retained-runtime comparison remains failed where reported','hull_source_unchanged':True,'hull_export_unchanged':True,'source_seats':samples,'runtime_census_difference':runtime_delta},indent=2)+'\n');print(samples)

ledger=json.loads((R/'qa/source_join_ledger.json').read_text())
for i,s in enumerate(samples):
 entry=next((a for a in ledger['contacts'] if a['part']==f'D17_SeatedHullFooting_{i}'),None)
 if entry is None:
  entry={'part':f'D17_SeatedHullFooting_{i}','root':'AST-HUL-001/'+s['hull_owner']};ledger['contacts'].append(entry)
 entry['contact']=f"Source polygon{s['same_actual_hull_polygon']};0.96m² XZ footprint; see seated_contact_verification.json"
 entry['centre_xz']=s['centre_xz'];entry['minimum_positive_wedge_thickness_m']=s['minimum_positive_wedge_thickness_m']
(R/'qa/source_join_ledger.json').write_text(json.dumps(ledger,indent=2)+'\n')

assert comparison_pass, 'Strict source-to-retained-runtime1mm comparison failed for band03. See explicit per-seat receipt and decoded-mesh audit; do not claim engine adoption.'
