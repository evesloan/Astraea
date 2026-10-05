from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];C=R.parents[1];D=json.loads((R/'source/section_contract.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(C/'assets/lower_hull_body/source/AST-HUL-001.blend'));hull=bpy.data.objects['HUL_LowerBand_00'];tree=BVHTree.FromObject(hull,bpy.context.evaluated_depsgraph_get());faces={};samples=[]
for s in D['seated_footings']:
 face=hull.data.polygons[s['witnesses'][0]['face_index']];normal=face.normal;origin=hull.data.vertices[face.vertices[0]].co
 assert normal.z>.9
 # Exact retained surface plane is checked over the entire rectangular contact footprint.
 maximum_plane_error=0.;maximum_ray_error=0.
 q=s['corners_world'];x0=q[0][0];width=q[1][0]-x0;z0=min(v[2] for v in q);depth=max(v[2] for v in q)-z0;slope=(q[1][1]-q[0][1])/width
 assert abs(width-.8)<1e-6 and abs(depth-1.2)<1e-6
 for i in range(9):
  for j in range(9):
   x=x0+i*width/8;z=z0+j*depth/8;y=q[0][1]+(x-x0)*slope
   p=Vector((x,-z,y));maximum_plane_error=max(maximum_plane_error,abs((p-origin).dot(normal)))
   hit,n,fi,d=tree.ray_cast(Vector((x,-z,4)),Vector((0,0,-1)),12);assert hit is not None;assert fi==face.index;maximum_ray_error=max(maximum_ray_error,abs(hit.z-y))
 assert maximum_plane_error<1e-5 and maximum_ray_error<1e-5
 assert min(s['top_y']-v[1]for v in q)>.34
 samples.append({'centre_xz':[s['x'],s['z']],'same_actual_hull_polygon':face.index,'grid_rays':81,'maximum_plane_error_m':maximum_plane_error,'maximum_ray_error_m':maximum_ray_error,'minimum_positive_wedge_thickness_m':min(s['top_y']-v[1]for v in q),'footprint_contact_area_xz_m2':.96})
assert sha(C/'assets/lower_hull_body/source/AST-HUL-001.blend')==D['source_inputs']['catalogue/assets/lower_hull_body/source/AST-HUL-001.blend']
assert sha(C/'assets/lower_hull_body/exports/AST-HUL-001.glb')==D['source_inputs']['catalogue/assets/lower_hull_body/exports/AST-HUL-001.glb']
phys=json.loads((R/'qa/parent_outer_support_census.json').read_text());diffs=[]
for s in D['seated_footings']:
 row=next(a for a in phys['candidate_support_columns'] if abs(a['xz'][0]-s['x'])<1e-4 and abs(a['xz'][1]-s['z'])<1e-4)
 for a in row['base_rays']:
  xyz=a['position'];b=min(s['witnesses'],key=lambda v:abs(v['point_world'][0]-xyz[0])+abs(v['point_world'][2]-xyz[2]));diffs.append(abs(xyz[1]-b['point_world'][1]))
assert len(diffs)==10 and max(diffs)<.001
runtime_delta={'maximum_absolute_y_m':max(diffs),'scope':'Previously measured retained-hull runtime rays versus new source seats; new footing runtime not imported'}
(R/'qa/seated_contact_verification.json').write_text(json.dumps({'pass':True,'scope':'Two exact source-plane seats; no whole-house structural or engine acceptance','hull_source_unchanged':True,'hull_export_unchanged':True,'source_seats':samples,'runtime_census_difference':runtime_delta},indent=2)+'\n');print(samples)

ledger=json.loads((R/'qa/source_join_ledger.json').read_text())
for i,s in enumerate(samples):
 entry=next(a for a in ledger['contacts'] if a['part']==f'D17_SeatedHullFooting_{i}')
 entry['contact']=f"Source polygon{s['same_actual_hull_polygon']};0.96m² XZ footprint; see seated_contact_verification.json"
 entry['centre_xz']=s['centre_xz'];entry['minimum_positive_wedge_thickness_m']=s['minimum_positive_wedge_thickness_m']
(R/'qa/source_join_ledger.json').write_text(json.dumps(ledger,indent=2)+'\n')
