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
(R/'qa/seated_contact_verification.json').write_text(json.dumps({'pass':True,'scope':'Two exact source-plane seats; no whole-house structural or engine acceptance','hull_source_unchanged':True,'hull_export_unchanged':True,'source_seats':samples,'runtime_census_difference':'Parent physics witnesses are approximately0.00027m above the editable hull surface; this source seat is not a claim of final engine contact acceptance.'},indent=2)+'\n');print(samples)
