"""Read-only verification of optional body subset plus finite and conservative omission distances.
No source/export/manifest/collision/image is written. Outputs stay in actor_proxies.
"""
from pathlib import Path
import json,hashlib,itertools,math
import numpy as np
from scipy.spatial import ConvexHull
HERE=Path(__file__).resolve().parent;BASE=HERE.parent
C=np.array([[1.,0,0],[0,0,1],[0,-1,0]])
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def hull(v):
 v=np.asarray(v,float);h=ConvexHull(v);return {'v':v,'eq':h.equations,'tri':v[h.simplices],'volume':h.volume}
def triangle_distances(points,tri):
 # Exact Euclidean closest-triangle distance using face projection and all three edge segments.
 p=points[:,None,:];a=tri[None,:,0,:];e0=tri[:,1]-tri[:,0];e1=tri[:,2]-tri[:,0];n=np.cross(e0,e1);n/=np.linalg.norm(n,axis=1)[:,None]
 signed=np.sum((p-a)*n[None,:,:],axis=2);q=p-signed[:,:,None]*n[None,:,:];v=q-a;d00=np.sum(e0*e0,axis=1);d01=np.sum(e0*e1,axis=1);d11=np.sum(e1*e1,axis=1);d20=np.sum(v*e0[None,:,:],axis=2);d21=np.sum(v*e1[None,:,:],axis=2);den=d00*d11-d01*d01
 b=(d11*d20-d01*d21)/den;d=(d00*d21-d01*d20)/den;inside=(b>=-1e-10)&(d>=-1e-10)&(b+d<=1+1e-10);best=np.where(inside,signed*signed,np.inf)
 for i,j in((0,1),(1,2),(2,0)):
  aa=tri[:,i];ee=tri[:,j]-aa;tt=np.clip(np.sum((p-aa[None,:,:])*ee[None,:,:],axis=2)/np.sum(ee*ee,axis=1),0,1);delta=p-(aa[None,:,:]+tt[:,:,None]*ee[None,:,:]);best=np.minimum(best,np.sum(delta*delta,axis=2))
 return np.sqrt(np.maximum(0,best.min(axis=1)))
def distances(points,shapes):
 inside=np.zeros(len(points),bool)
 for h in shapes:inside |= np.max(points@h['eq'][:,:3].T+h['eq'][:,3],axis=1)<=1e-10
 result=triangle_distances(points,np.concatenate([h['tri']for h in shapes]));result[inside]=0;return result
def matrix(m,frac):
 T=np.eye(4)
 if m['kind']=='translation':T[:3,3]=np.array(m['axis_source'])*m['travel']*frac
 else:
  a=math.radians(m['travel']*frac);c,s=math.cos(a),math.sin(a);R=np.array([[1,0,0],[0,c,-s],[0,s,c]]);p=np.array(m['pivot_source_m']);T[:3,:3]=R;T[:3,3]=p-R@p
 return T
def transform(v,owner,motions,state):
 if owner not in motions:return np.asarray(v)
 T=matrix(motions[owner],state[owner]);return np.asarray(v)@T[:3,:3].T+T[:3,3]
base=json.loads((BASE/'collision_proposals.json').read_text());sub=json.loads((HERE/'body_collision_subset.json').read_text());api=json.loads((BASE/'marker_api.json').read_text());source=json.loads((BASE/'qa/evaluated_source_geometry.json').read_text());geo=json.loads((BASE/'qa/geometry_checks.json').read_text());rows=[]
for ident,entry in sub['assets'].items():
 old=base[ident];allby={s['name']:s for s in old['shapes']};kept=entry['shapes'];omitted=[allby[r['base_shape_id']]for r in entry['omitted_shapes']];kh={s['name']:hull(s['points_source_m'])for s in kept};oh={s['name']:hull(s['points_source_m'])for s in omitted};motions={m['root']:m for m in old['motion_records']};retained_parts={p:s for s in kept for p in s['covered_parts']};source_parts={p['name']:p for p in source[ident]['parts']};rec=json.loads((BASE/f'{ident}.manifest.json').read_text());primary=[];fine_markers=[]
 for m in api[ident]:
  if not m['physical_part']:continue
  if m['physical_part']not in retained_parts:
   assert 'hinge'in m['kind']or'bearing'in m['kind'];fine_markers.append({'name':m['name'],'kind':m['kind'],'part':m['physical_part'],'still_available_in_unchanged_detailed_marker_api':True});continue
  sh=retained_parts[m['physical_part']];h=kh[sh['name']];p=np.array(m['source_m']);values=h['eq'][:,:3]@p+h['eq'][:,3];active=h['eq'][np.abs(values)<2e-6];dot=float(np.max(active[:,:3]@m['direction_source']))if 'direction_source'in m and len(active)else 1.;owner=sh['parent_root']==m['parent_root'];native=np.linalg.norm(C@p-m['gltf_m'])<1e-6
  primary.append({'name':m['name'],'kind':m['kind'],'part':m['physical_part'],'retained_shape_id':sh['name'],'parent_root':sh['parent_root'],'source_surface_signed_distance_m':float(np.max(values)),'normal_dot':dot,'source_native_marker_position_match':bool(native),'all_pose_surface_preservation':'The same complete physical convex profile, marker parent and transform are retained; rigid rotation/translation preserves the contact and normal.','passes':bool(abs(np.max(values))<2e-6 and dot>.999 and owner and native)})
 assert len(primary)==(7 if ident=='AST-CUL-003'else 9)
 subsets=all(allby[s['name']]==s for s in kept);native_shapes=all(np.max(np.abs(np.array(s['points_source_m'])@C.T-np.array(s['points_gltf_m'])))<1e-7 for s in kept)
 inherited=next(r for r in geo['assets']if r['catalogue_id']==ident);voids=[]
 for v in entry['preserve_voids']:
  detailed=next(q for q in old['preserve_voids']if q['name']==v['name']);prior=next(q for q in inherited['whole_volume_void_checks']if q['name']==v['name']);voids.append({'name':v['name'],'state_scope':v['state'],'exact_original_void_record':v==detailed,'accepted_detailed_full_volume_test_passed':prior['passes'],'source_hash_matches_accepted_geometry':inherited['source_sha256']==rec['source_sha256'],'subset_proof_for_all_identical_poses':'Retained convex profiles and owners are unchanged; their posed union is a strict subset of the detailed posed union, so the subset cannot newly intersect this void. Inherits exactly the original state/relative-motion scope, not anatomy or host acceptance.','passes':bool(v==detailed and prior['passes']and subsets and inherited['source_sha256']==rec['source_sha256'])})
 if ident=='AST-CUL-003':states=[{'PAN_HINGE_X':i/12}for i in range(13)]
 else:states=[{'LIGHT_AIM_X':i/4,'REAR_COVER_REMOVE':j/2}for i,j in itertools.product(range(5),range(3))]
 samples={};maxima={}
 for s in omitted:
  h=oh[s['name']];samples[s['name']]=np.concatenate((h['v'],h['tri'].mean(axis=1)));maxima[s['name']]={'distance_m':0.,'state':None,'sample_source_m':None,'sample_index':None}
 for state in states:
  posed=[hull(transform(s['points_source_m'],s['parent_root'],motions,state))for s in kept]
  for s in omitted:
   pts=transform(samples[s['name']],s['parent_root'],motions,state);d=distances(pts,posed);ix=int(np.argmax(d));value=float(d[ix])
   if maxima[s['name']]['state']is None or value>maxima[s['name']]['distance_m']:maxima[s['name']]={'distance_m':value,'state':state.copy(),'sample_source_m':pts[ix].tolist(),'sample_index':ix,'sample_kind':'authored_vertex'if ix<len(oh[s['name']]['v'])else'convex_facet_centroid'}
 omissions=[]
 for s in omitted:
  h=oh[s['name']];same=[k for k in kept if k['parent_root']==s['parent_root']];bounds=[]
  for k in same:
   d=distances(h['v'],[kh[k['name']]]);bounds.append((float(d.max()),k['name']))
  best,chosen=min(bounds);part=s['covered_parts'][0];dimensions=(h['v'].max(0)-h['v'].min(0)).tolist();row={'base_shape_id':s['name'],'covered_parts':s['covered_parts'],'material_roles':[source_parts[p]['material_role']for p in s['covered_parts']],'parent_root':s['parent_root'],'movement_group':s['movement_group'],'visual_geometry_basis':'This detailed convex proposal was independently checked as exact to its frozen visual semantic solid; no geometric inflation or omission in the base set.','source_aabb_dimensions_m':dimensions,'dimension_note':'Dimensions are not distance-to-proxy or material thickness; radial wall/shell thickness is not inferred from an AABB.','finite_samples_per_pose':len(samples[s['name']]),'finite_pose_count':len(states),'measured_finite_max_distance_to_retained_union':maxima[s['name']],'continuous_conservative_omission_bound':{'reference_retained_shape_id':chosen,'same_owner':s['parent_root'],'max_omitted_vertex_distance_to_reference_convex_shape_m':best,'numeric_allowance_m':.000002,'all_point_all_owner_pose_upper_bound_m':best+.000002,'proof':'Distance to one closed convex retained set is convex: for every point in the omitted convex hull, distance is at most the maximum distance of its vertices. Both shapes have identical rigid movement ownership, so that bound is invariant throughout every allowed owner pose, including simultaneous independent other-root motions. The retained union contains the reference shape and can only reduce this distance. This is a conservative distance bound, not a measured maximum over the union.'},'reason':next(r['reason']for r in entry['omitted_shapes']if r['base_shape_id']==s['name']),'passes':maxima[s['name']]['distance_m']<=best+.000002};omissions.append(row)
 access=rec.get('details',{}).get('access_reservations',[]);retained_access=[]
 for a in access:retained_access.append({'name':a['name'],'base_record':a,'all_cover_and_pull_shapes_preserved':all(n in retained_parts for n in('removable_rear_service_cover','rear_cover_pull_bridge','rear_pull_left_return','rear_pull_right_return')),'meaning':'Occupied handling-sweep reservation remains occupied by the same complete cover/pull assembly; it is not relabelled an empty void.'})
 rows.append({'catalogue_id':ident,'detailed_count':len(old['shapes']),'body_count':len(kept),'omitted_count':len(omitted),'unchanged_shape_subset':subsets,'native_basis_and_points_unchanged':bool(native_shapes),'base_motion_records_unchanged':entry['base_motion_records']==old['motion_records'],'all_primary_surface_markers_retained':primary,'fine_mechanism_markers_not_replaced_by_body_proxy':fine_markers,'preserved_use_approach_voids':voids,'preserved_access_reservations':retained_access,'finite_omission_pose_grid_fractions':states,'omissions':omissions,'finite_union_max_m':max(r['measured_finite_max_distance_to_retained_union']['distance_m']for r in omissions),'continuous_same_owner_conservative_max_m':max(r['continuous_conservative_omission_bound']['all_point_all_owner_pose_upper_bound_m']for r in omissions),'passes':subsets and bool(native_shapes)and all(x['passes']for x in primary+voids+omissions)and all(x['all_cover_and_pull_shapes_preserved']for x in retained_access)})
# Positive controls for Euclidean omission distances: known one-centimetre separation and contained point.
unit=hull(list(itertools.product((0.,1.),repeat=3)));control=distances(np.array([[1.01,.5,.5],[.5,.5,.5]]),[unit]);controls={'one_cm_gap_distance_m':float(control[0]),'inside_distance_m':float(control[1]),'passes':bool(abs(control[0]-.01)<1e-10 and control[1]==0)}
inputs=[BASE/'collision_proposals.json',BASE/'marker_api.json',BASE/'qa/evaluated_source_geometry.json',BASE/'qa/geometry_checks.json',BASE/'AST-CUL-003.manifest.json',BASE/'AST-CUL-004.manifest.json',HERE/'body_collision_subset.json',Path(__file__)]
locked=json.loads((HERE/'base_byte_lock.json').read_text());lockrows=[{'path':r['path'],'unchanged':(BASE/r['path']).is_file()and sha(BASE/r['path'])==r['sha256']}for r in locked['files']]
out={'schema':'optional_body_subset_verification_v1','measurement':'Exact Euclidean point-to-retained-convex-union distances on original omitted vertices and every triangulated convex facet centroid at the stated finite poses. Separately proven conservative all-point/continuous-pose bounds use one retained convex shape with the same owner.','limits':['Finite union samples are not a global Hausdorff distance, uniform material thickness or an actor-fit guarantee.','Fine mechanism, pin and cable details stay visually present and are omitted from optional BODY collision only. Open service states expose those fine details.','Precise tools/interaction targeting and detailed mechanism checks must use unchanged detailed source/markers/profiles.','No engine adoption, dynamic load support, actual contact response, six-species fit, host routes or performance acceptance.'],'inputs':[{'path_from_family_root':str(p.relative_to(BASE)),'sha256':sha(p),'role':'generated base/QA evidence input'if'qa'in p.relative_to(BASE).parts else'current addendum or frozen production input'}for p in inputs],'assets':rows,'positive_controls':controls,'preexisting_files_checked':len(lockrows),'preexisting_file_checks':lockrows,'all_preexisting_bytes_preserved':all(r['unchanged']for r in lockrows),'all_passed':all(r['passes']for r in rows)and controls['passes']and all(r['unchanged']for r in lockrows)};(HERE/'body_subset_checks.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'all_passed':out['all_passed'],'preexisting_unchanged':out['all_preexisting_bytes_preserved'],'assets':[{'id':r['catalogue_id'],'count':r['body_count'],'finite_union_max_m':r['finite_union_max_m'],'continuous_bound_m':r['continuous_same_owner_conservative_max_m']}for r in rows]},indent=2))
