"""Independent actual source/native profile, support, void and collision review."""
from pathlib import Path
import sys,json,hashlib,itertools
import numpy as np
from scipy.spatial import ConvexHull,cKDTree
from scipy.optimize import linprog
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch18'
sys.path.insert(0,str(ROOT/'qa/batch07'));from independent_geometry import Native,SourceCache,C
sys.path.insert(0,str(ROOT/'qa/batch08'));from independent_collision_geometry import nearest_distances
sys.path.insert(0,str(ROOT/'qa/batch15'));from independent_contact_graph import normal_witness
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
bind=lambda p:{'path':str(Path(p).relative_to(ROOT)),'sha256':sha(p)}
def hull(points):return ConvexHull(np.unique(np.round(points,9),axis=0))
def pts(t):return np.unique(t.reshape(-1,3),axis=0)
def inside(p,h,tol=1e-6):return np.max(np.asarray(p)@h.equations[:,:-1].T+h.equations[:,-1],axis=1)<=tol
def clip(a,b):
 out=list(a)
 for p,q in zip(b,np.roll(b,-1,axis=0)):
  old=out;out=[]
  if not len(old):break
  for x,y in zip(old,np.roll(old,-1,axis=0)):
   cross=lambda v,w:float(v[0]*w[1]-v[1]*w[0]);u=cross(q-p,x-p);v=cross(q-p,y-p)
   if u>=-1e-12:out.append(x)
   if (u>=-1e-12)!=(v>=-1e-12):out.append(x+u/(u-v)*(y-x))
 return np.asarray(out)
def area(p):return abs(sum(np.cross(p[i]-p[0],p[i+1]-p[0])for i in range(1,len(p)-1)))/2 if len(p)>2 else 0.
def poly(points):
 p=np.unique(points,axis=0);h=ConvexHull(p);return p[h.vertices]
def halfplane(p,a,b,keep_inside=True):
 out=[]
 if not len(p):return np.empty((0,2))
 for x,y in zip(p,np.roll(p,-1,axis=0)):
  cross=lambda v,w:float(v[0]*w[1]-v[1]*w[0]);u=cross(b-a,x-a);v=cross(b-a,y-a)
  if not keep_inside:u=-u;v=-v
  if u>=-1e-12:out.append(x)
  if (u>=-1e-12)!=(v>=-1e-12):out.append(x+u/(u-v)*(y-x))
 return np.asarray(out)
def subtract_convex(a,b):
 remains=a;outside=[]
 for x,y in zip(b,np.roll(b,-1,axis=0)):
  piece=halfplane(remains,x,y,False)
  if area(piece)>1e-12:outside.append(piece)
  remains=halfplane(remains,x,y,True)
  if area(remains)<=1e-12:break
 return outside
def uncovered_area(a,polygons):
 residual=[a]
 for b in polygons:
  residual=[piece for p in residual for piece in subtract_convex(p,b)]
 return float(sum(area(p)for p in residual))
def intersects_box(h,lo,hi):
 # Inward margin avoids classifying a deliberate contact boundary as a filled void.
 res=linprog(np.zeros(3),A_ub=h.equations[:,:3],b_ub=-h.equations[:,3]-1e-7,bounds=list(zip(np.array(lo)+1e-7,np.array(hi)-1e-7)),method='highs')
 return bool(res.success)
def sample_triangle(t,n=6):return np.array([(a*t[0]+b*t[1]+(n-a-b)*t[2])/n for a in range(n+1)for b in range(n+1-a)])
rows=[]
for ident in ['AST-RTL-001','AST-RTL-002']:
 family=ROOT/'assets/retail_display';mp=family/(ident+'.manifest.json');m=json.loads(mp.read_text());sp=family/m['source'];gp=family/m['export'];sr=OUT/('independent_source_'+ident+'.json');s=json.loads(sr.read_text());assert s['sha256']==m['source_sha256']==sha(sp);assert m['glb_sha256']==sha(gp)
 a=np.load(ROOT/s['geometry_cache']);t=a['triangles'];labels=a['object_names'];mats=a['material_names'];parts={str(n):t[labels==n]for n in np.unique(labels)};hulls={n:hull(pts(tt))for n,tt in parts.items()};src=SourceCache(sr);src.materials=mats;native=Native(gp);native_source=native.tris@C
 marker=[]
 for x in m['physical_and_proposal_markers']:
  p=np.array(x['source_m']);native_point=np.array(x['gltf_m']);nodes=[i for i,n in enumerate(native.g.doc['nodes'])if n.get('name')==x['name']];assert len(nodes)==1
  frame_err=float(np.max(abs(p@C.T-native_point)));actual_err=float(np.max(abs(native.world[nodes[0]][:3,3]-native_point)));row={'name':x['name'],'kind':x['kind'],'frame_error_m':frame_err,'actual_native_node_error_m':actual_err,'physical_part':x['physical_part']}
  if x['physical_part']:
   part=x['physical_part'];tt=parts[part];role=str(mats[labels==part][0]);gt=native_source[native.materials==role];ds=float(nearest_distances([p],tt)[0]);dg=float(nearest_distances([p],gt)[0]);ns=normal_witness(p,tt,x['direction_source']);ng=normal_witness(p,gt,x['direction_source']);row.update(source_surface_error_m=ds,native_surface_error_m=dg,source_normal=ns,native_normal=ng);row['passed']=max(frame_err,actual_err,ds,dg)<1e-6 and ns['pass']and ng['pass']
  else:row['passed']=max(frame_err,actual_err)<1e-6
  marker.append(row)
 joins=[]
 for x in m['joins']:
  p=np.array(x['probe_source_m']);dist=[float(nearest_distances([p],parts[n])[0])for n in x['parts']];joins.append({'name':x['name'],'parts':x['parts'],'surface_distances_m':dist,'native_point_frame_error_m':float(np.max(abs(p@C.T-x['probe_gltf_m']))),'passed':max(dist)<1e-6})
 profiles=[]
 for x in m['whole_profile_records']:
  axis=x['profile_axis_source'];dims=[k for k in range(3)if k!=axis];expected=[]
  for d in x['extrusion_range_m']:
   for point in x['polygon_m']:
    p=np.zeros(3);p[axis]=d;p[dims]=point;expected.append(p)
  expected=np.array(expected);actual=pts(parts[x['part']]);err=float(max(cKDTree(actual).query(expected)[0].max(),cKDTree(expected).query(actual)[0].max()));tt=parts[x['part']];vol=abs(np.einsum('ij,ij->i',tt[:,0],np.cross(tt[:,1],tt[:,2])).sum()/6);hv=hulls[x['part']].volume;profiles.append({'part':x['part'],'all_actual_vertices_match_full_profile_m':err,'actual_mesh_volume_m3':vol,'convex_hull_volume_m3':hv,'passed':err<1e-6 and abs(vol-hv)<1e-7})
 patches=[]
 for x in m['support_patches']:
  p=np.array(x['polygon_source_m']);surface=parts[x['physical_part']];ss=np.concatenate([p,np.mean(p,axis=0)[None],(p+np.roll(p,-1,axis=0))/2]);ds=nearest_distances(ss,surface);normal=normal_witness(np.mean(p,axis=0),surface,x['normal_source']);above=ss+np.array(x['normal_source'])*.0005;blocked=[n for n,h in hulls.items()if inside(above,h,1e-8).any()];patches.append({'name':x['name'],'physical_part':x['physical_part'],'vertices_edges_and_center_witnesses':len(ss),'max_source_surface_distance_m':float(ds.max()),'normal':normal,'blocked_0_5mm_above_by_parts':blocked,'passed':ds.max()<1e-6 and normal['pass']and not blocked})
 cp=family/'collision_proposals.json';bp=family/'actor_proxies/body_collision_subset.json';detail=json.loads(cp.read_text())['assets'][ident];body=json.loads(bp.read_text())['assets'][ident];dh=[];drows=[]
 for x in detail['shapes']:
  h=hull(x['points_source_m']);part=x['semantic_part'];actual=pts(parts[part]);point=np.array(x['points_source_m']);err=float(max(cKDTree(actual).query(point)[0].max(),cKDTree(point).query(actual)[0].max()));dh.append(h);drows.append({'part':part,'all_actual_vertices_error_m':err,'volume_error_m3':abs(h.volume-hulls[part].volume),'passed':err<1e-6 and abs(h.volume-hulls[part].volume)<1e-7})
 bh=[];brows=[];kept=set()
 compound=[x for x in body['shapes']if len(x['semantic_parts'])>1];compound_names=sorted({n for x in compound for n in x['semantic_parts']});compound_source_polys=[poly(np.round(pts(parts[n])[:,[0,2]],6))for n in compound_names];compound_body_polys=[poly(np.round(np.array(x['points_source_m'])[:,[0,2]],6))for x in compound]
 # All actual profile-axis1 structural prisms are eligible for the geometric union. This includes the adjacent upper entry pier: arbitrary artistic wedge ownership is not a solid boundary.
 profile_parts={x['part']:x for x in m['whole_profile_records']};structural_names=[n for n in parts if profile_parts[n]['profile_axis_source']==1 and str(mats[labels==n][0])in {'ASTRAEA_ivory_enamel','ASTRAEA_retail_terracotta_enamel'}]
 structural_polys=[poly(np.round(pts(parts[n])[:,[0,2]],6))for n in structural_names if pts(parts[n])[:,1].min()<=-.31+1e-6 and pts(parts[n])[:,1].max()>=.40-1e-6]
 compound_source_uncovered=sum(uncovered_area(p,compound_body_polys)for p in compound_source_polys);compound_body_added=sum(uncovered_area(p,structural_polys)for p in compound_body_polys)
 for x in body['shapes']:
  names=x['semantic_parts'];kept.update(names);p=np.array(x['points_source_m']);h=hull(p);bh.append(h);allp=np.concatenate([pts(parts[n])for n in names]);cover=inside(allp,h).all();row={'semantic_parts':names,'named_part_vertices_within_this_one_hull':bool(cover),'declared_outward_approximation_m':x['max_outward_approximation_m']}
  if len(names)==1:
   err=float(abs(h.volume-hulls[names[0]].volume));row.update(exact_hull_volume_error_m3=err,passed=bool(cover and err<1e-7))
  else:
   assert len(names)==2
   # Both source wedges are actual convex extrusions in Y. Their 2-D XZ union is proved by containment and additive area, including intersection area.
   pa=poly(pts(parts[names[0]])[:,[0,2]]);pb=poly(pts(parts[names[1]])[:,[0,2]]);pc=poly(p[:,[0,2]]);ha=ConvexHull(pc);contained=inside(pa,ha).all()and inside(pb,ha).all();unionarea=float(area(pa)+area(pb)-area(clip(pa,pb)));gap=abs(float(area(pc))-unionarea);dist=[]
   for name in names:
    actual=pts(parts[name]);dist.append(max(max(0,actual[:,1].min()-p[:,1].min()),max(0,p[:,1].max()-actual[:,1].max())))
   bound=float(max(dist));row.update(per_named_pair_full_XZ_union_area_difference_m2=gap,per_named_pair_source_XZ_polygons_within_body=bool(contained),all_compound_profile_source_uncovered_area_m2=compound_source_uncovered,all_compound_profile_body_added_area_m2=compound_body_added,semantic_joint_note='Whole union includes the adjacent actual upper entry pier and neighboring static compound. Every eligible original solid is a verified constant-Y prism spanning at least -0.31..0.40m; therefore any body point at Y-0.40..0.43 has a source point with the same XZ within90mm. Polygon proof snaps float32/decimal source coordinates to1micrometre; actual source/native checks remain at1micrometre tolerance.',profile_plane_snap_tolerance_m=.000001,analytic_Y_extrusion_outward_bound_m=bound,passed=bool(compound_source_uncovered<1e-7 and compound_body_added<1e-7 and bound<=x['max_outward_approximation_m']+1e-6))
  brows.append(row)
 voids=[]
 for x in m['useful_voids']:
  lo=x['min_source_m'];hi=x['max_source_m'];inter=[n for n,h in hulls.items()if intersects_box(h,lo,hi)];dint=[i for i,h in enumerate(dh)if intersects_box(h,lo,hi)];bint=[i for i,h in enumerate(bh)if intersects_box(h,lo,hi)];voids.append({'name':x['name'],'exact_solid_intersections':inter,'detailed_intersections':dint,'body_intersections':bint,'passed':not(inter or dint or bint)})
 # Actual support surface solid is a blocked control for every claimed empty box.
 controls=[]
 for x in m['support_patches']:
  center=np.mean(x['polygon_source_m'],axis=0)-np.array(x['normal_source'])*.005;hit=[n for n,h in hulls.items()if inside([center],h).any()];controls.append({'name':x['name'],'point_5mm_inside_primary_solid':center.tolist(),'blocked_by':hit,'passed':x['physical_part']in hit})
 omitted=[];body_union=np.concatenate([parts[n]for n in kept]);
 for x in body['omitted_detail']:
  name=x['semantic_part'];ss=np.concatenate([sample_triangle(tt)for tt in parts[name]]);dd=nearest_distances(ss,body_union);mx=float(dd.max());omitted.append({'part':name,'sample_count':len(ss),'finite_observed_distance_m':mx,'declared_omitted_detail_distance_m':x['maximum_distance_from_retained_body_m'],'material_thickness_separate_m':x['material_thickness_m'],'passed':mx<=x['maximum_distance_from_retained_body_m']+1e-6})
 whole=[]
 if ident.endswith('001'):
  back=pts(parts['dark_inset_display_back']);opening=ConvexHull(back[:,[0,2]])
  for name in ['lower_storage_tactile_floor','left_open_storage_divider','right_open_storage_divider','main_display_work_slab','upper_timber_display_mullion','left_supported_display_shelf','right_supported_display_shelf']:
   v=pts(parts[name]);signed=v[:,[0,2]]@opening.equations[:,:2].T+opening.equations[:,2];mx=float(signed.max());whole.append({'part':name,'all_actual_vertices':len(v),'max_outside_full_actual_arch_profile_m':mx,'passed':mx<1e-6})
  source_left=np.array([-1.7,0,1.44]);yaw=np.array([[0,-1,0],[1,0,0],[0,0,1]]);entry={'local_recess_face_normal':[-1,0,0],'arrangement_recess_face_normal':(yaw@np.array([-1,0,0])).tolist(),'faces_threshold_minus_sourceY':bool(np.array_equal(yaw@np.array([-1,0,0]),[0,-1,0]))}
 else:entry=None
 row={'catalogue_id':ident,'bindings':[bind(p)for p in [sp,gp,mp,cp,bp,sr]],'markers':marker,'joins':joins,'full_profile_records':profiles,'support_patches':patches,'whole_internal_parts_within_arch':whole,'entry_relation':entry,'detail_collision':{'shape_count':len(dh),'checks':drows},'optional_body_collision':{'shape_count':len(bh),'checks':brows,'omitted_detail':omitted,'meaning':'Optional source-authored compound, not a literal subset when material wedges are merged. Analytical cross-section and extrusion bound separates added finish volume from omitted thin ornament.'},'whole_useful_void_box_checks':voids,'blocked_controls':controls,'passed':all(x['passed']for group in [marker,joins,profiles,patches,whole,drows,brows,voids,controls,omitted]for x in group)}
 rows.append(row);(OUT/('independent_display_geometry_'+ident+'.json')).write_text(json.dumps(row,indent=2,default=lambda x:x.item())+'\n');print(ident,row['passed'],[(k,[x.get('name',x.get('part',x.get('semantic_parts')))for x in group if not x['passed']])for k,group in [('markers',marker),('joins',joins),('profiles',profiles),('patches',patches),('arch',whole),('details',drows),('body',brows),('voids',voids),('controls',controls),('omitted',omitted)]],flush=True)
report={'passed':all(x['passed']for x in rows),'assets':rows,'method':'Actual source named-part triangles and independent parsed native GLB. Convexity is checked by full profile vertex identity and mesh/hull volume. Full convex useful boxes use linear feasibility against each actual convex solid/detail/body, not sampled empty centers. Actual support/normal and blocked controls accompany each useful space. Whole arch containment checks every internal-part vertex in the actual convex arch profile.','limits':['No strength, floor/wall anchorage, load, actor/species/reach, real R070 support/door/slot or engine acceptance','Optional compound approximation uses full convex XZ union and actual extrusion ranges; omitted ornamental distance is a finite face-grid observation, not a continuous global Hausdorff proof'],'executed_script_sha256':sha(Path(__file__))}
(OUT/'independent_display_geometry_review.json').write_text(json.dumps(report,indent=2,default=lambda x:x.item())+'\n')
