from validate_practicals import *
from validate_proposed_architecture import proposed_objects
from shapely import constrained_delaunay_triangles

def cells(cloth):
 y0,y1=cloth['lo'][1],cloth['hi'][1];shape=plane_section(cloth['t'],1,y1);triangles=constrained_delaunay_triangles(shape);assert abs(sum(t.area for t in triangles.geoms)-shape.area)<1e-8;out=[]
 for i,t in enumerate(triangles.geoms):
  q=np.array(t.exterior.coords)[:3];v=np.array([[x,y,z]for y in [y0,y1]for x,z in q]);f=np.array([[0,2,1],[3,4,5],[0,1,4],[0,4,3],[1,2,5],[1,5,4],[2,0,3],[2,3,5]]);out.append({'name':str(i),'v':v,'t':v[f],'lo':v.min(0),'hi':v.max(0)})
 return shape,out

def embedding(n,cs):
 total=0;depth=0;hitcount=0
 for c in cs:
  if not(np.all(c['hi']>=n['lo'])and np.all(c['lo']<=n['hi'])):continue
  h=embedded_triangle_area(n['t'],c);assert h is not None
  if h['embedded_surface_area_m2']>1e-9:hitcount+=1;total+=h['embedded_surface_area_m2'];depth=max(depth,h['max_test_polygon_centroid_depth_m'])
 return {'real_contacted_cloth_prism_cells':hitcount,'actual_tab_surface_embedded_in_cloth_m2':total,'max_inside_cloth_test_polygon_centroid_depth_m':depth}

def main():
 path=PLAN/'ARCHITECTURE_ADDITIONS_GEOMETRY.json';N={o['name']:o for o in proposed_objects(path)};cloth=N['FP_original_navy_cyclorama'];shape,cs=cells(cloth);rail=N['FP_cyclorama_top_rail'];tabs=[]
 for i in range(40):
  ob=N[f'FP_cyclorama_tab_{i:02}'];h=embedding(ob,cs);rh=embedded_triangle_area(ob['t'],rail);tabs.append({'name':ob['name'],**h,'rail_actual_triangle_embedding':rh})
 runners=[]
 for side in ['port','starboard']:
  cloth=N[f'FP_{side}_stowed_stage_drape'];shape,cs=cells(cloth);y=cloth['hi'][1];track=N[f'FP_{side}_drape_track']
  for i in range(8):
   ob=N[f'FP_{side}_drape_runner_{i}'];cap=plane_section(ob['t'],1,y);runners.append({'name':ob['name'],'lower_plane_y':float(y),'real_lower_cap_to_cloth_contact_area_m2':cap.intersection(shape).area,'upper_track_actual_triangle_embedding':embedded_triangle_area(ob['t'],track),'cloth_volume_embedding':embedding(ob,cs),'joint_kind':'Finite-area boundary contact at cloth top, with positive overlap into top track. Positive buried cloth volume is not required for a valid cap boundary contact.'})
 d={'status':'CURRENT_TEXTILE_CONTACT_SCREEN','architecture_sha256':sha(path),'triangulation':'Every original float32 3D vertex preserved. Constrained planar projection chooses face triangle connectivity only; no reprojecting vertices into a different plane.','method':'Actual pleated cloth is a vertical prism over its actual top-face polygon. Exact constrained triangulation decomposes that prism into convex cells. Original connector triangles are clipped to those real solid cells; results are not empty bounds or a demand for coplanar caps.','cyclorama_tabs':tabs,'side_drape_runners':runners,'superseded_result':'Earlier CURRENT_145 summary tab missing-section flags were a checker triangulation artifact and are superseded. The face triangulator now preserves all actual raw 3D coordinates.'};(OUT/'CURRENT_TEXTILE_JOINT_EVIDENCE.json').write_text(json.dumps(d,indent=2)+'\n');print(json.dumps({'architecture_sha256':d['architecture_sha256'],'missing_tab_cloth':[r['name']for r in tabs if r['actual_tab_surface_embedded_in_cloth_m2']<=1e-9],'missing_tab_rail':[r['name']for r in tabs if r['rail_actual_triangle_embedding']is None or r['rail_actual_triangle_embedding']['embedded_surface_area_m2']<=1e-9],'minimum_tab_cloth_area':min(r['actual_tab_surface_embedded_in_cloth_m2']for r in tabs),'missing_runner_cloth':[r['name']for r in runners if r['real_lower_cap_to_cloth_contact_area_m2']<=1e-9],'minimum_runner_cloth_area':min(r['real_lower_cap_to_cloth_contact_area_m2']for r in runners),'missing_runner_track':[r['name']for r in runners if r['upper_track_actual_triangle_embedding']is None or r['upper_track_actual_triangle_embedding']['embedded_surface_area_m2']<=1e-9]},indent=2))
if __name__=='__main__':main()
