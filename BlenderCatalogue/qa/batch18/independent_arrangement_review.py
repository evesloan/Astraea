"""Read-only actual imported geometry placement/support screen for R070 source proposal."""
from pathlib import Path
import json,hashlib,sys,itertools
import numpy as np
from scipy.spatial import ConvexHull
from scipy.optimize import linprog
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch18'
sys.path.insert(0,str(ROOT/'qa/batch07'));from independent_geometry import Native,C
sys.path.insert(0,str(ROOT/'qa/batch08'));from independent_collision_geometry import nearest_distances
sys.path.insert(0,str(ROOT/'qa/batch15'));from independent_contact_graph import normal_witness
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();bind=lambda p:{'path':str(p.relative_to(ROOT)),'sha256':sha(p)}
pp=OUT/'assembly/plan.json';p=json.loads(pp.read_text());bykey={x['key']:x for x in p['items']};native={};geometry={};manifests={};rot={};bindings=[];bounds=[]
S=np.array([[0,-1,0],[0,0,1],[-1,0,0]])
for x in p['items']:
 k=x['key'];a=np.deg2rad(x['source_z_rotation_deg']);r=np.array([[np.cos(a),-np.sin(a),0],[np.sin(a),np.cos(a),0],[0,0,1]]);rot[k]=r
 gp=ROOT/x['variants']['closed'];n=Native(gp);tt=(n.tris@C)@r.T+np.array(x['source_origin_m']);native[k]=tt;lo=tt.min((0,1));hi=tt.max((0,1));ship=tt@S.T+np.array([78,52.5,236]);bounds.append({'key':k,'actual_source_bounds_m':[lo.tolist(),hi.tolist()],'actual_ship_bounds_m':[ship.min((0,1)).tolist(),ship.max((0,1)).tolist()],'proper_source_rotation_determinant':float(np.linalg.det(r)),'inside_historical_outer_allocation':bool(lo[0]>=-6-1e-6 and hi[0]<=6+1e-6 and lo[1]>=-1e-6 and hi[1]<=12+1e-6)})
 mp=ROOT/x['manifest_path'];m=json.loads(mp.read_text());manifests[k]=m;sp=ROOT/x['source_path'];assert m['source_sha256']==sha(sp)and m['glb_sha256']==sha(gp)
 sr=OUT/('independent_source_'+x['asset_id']+'.json');s=json.loads(sr.read_text());assert s['sha256']==sha(sp);g=np.load(ROOT/s['geometry_cache']);geometry[k]={str(name):(g['triangles'][g['object_names']==name]@r.T+np.array(x['source_origin_m']))for name in np.unique(g['object_names'])}
 bindings.extend([bind(gp),bind(mp),bind(sp),bind(sr)])
empty=[]
for region in p['proposed_empty_regions']:
 lo=np.array(region['min_source_m']);hi=np.array(region['max_source_m'])
 for k,tt in native.items():
  a=tt.min((0,1));b=tt.max((0,1));overlap=np.minimum(b,hi)-np.maximum(a,lo);empty.append({'region':region['id'],'key':k,'actual_geometry_bbox_overlap_xyz_m':overlap.tolist(),'passed':bool(np.min(overlap)<=1e-6),'method':'A separated actual-vertex bounding box proves no surface/solid in the test region. Touching boundary within1micrometre is permitted; no bounding overlap establishes a physical contact.'})
supports=[];interpenetrations=[]
for x in p['items']:
 if 'support'not in x:continue
 k=x['key'];record=x['support'];parent=record['parent_key'];childpatch=next(z for z in manifests[k]['support_patches']if z['name']==record['child_patch']);parentpatch=next(z for z in manifests[parent]['support_patches']if z['name']==record['parent_patch']);child=np.array(childpatch['polygon_source_m'])@rot[k].T+np.array(x['source_origin_m']);patch=np.array(parentpatch['polygon_source_m'])@rot[parent].T+np.array(bykey[parent]['source_origin_m']);h=ConvexHull(patch[:,:2]);signed=child[:,:2]@h.equations[:,:2].T+h.equations[:,2];cn=rot[k]@childpatch['normal_source'];pn=rot[parent]@parentpatch['normal_source'];plane=float(np.max(abs((child-patch[0])@pn)));foot=geometry[k][childpatch['physical_part']];surface=geometry[parent][parentpatch['physical_part']];samples=np.concatenate([child,(child+np.roll(child,-1,axis=0))/2,child.mean(0)[None]]);dc=nearest_distances(samples,foot);dp=nearest_distances(samples,surface);footnormal=normal_witness(child.mean(0),foot,cn);parentnormal=normal_witness(child.mean(0),surface,pn);wrong=child+np.array([10,0,0]);bad=bool(np.any(wrong[:,:2]@h.equations[:,:2].T+h.equations[:,2]>1e-6));allfoot=foot.reshape(-1,3);bottom=allfoot[abs((allfoot-child[0])@pn)<1e-6];allactual=bool(np.max(bottom[:,:2]@h.equations[:,:2].T+h.equations[:,2])<1e-6)
 row={'child':k,'parent':parent,'actual_child_part':childpatch['physical_part'],'actual_parent_part':parentpatch['physical_part'],'whole_uninset_foot_polygon_inside_parent_patch':bool(signed.max()<1e-6),'every_actual_foot_bottom_vertex_within_patch':allactual,'whole_support_margin_m':float(-signed.max()),'matching_plane_error_m':plane,'opposed_normal_cosine':float(cn@pn),'exact_uninset_corners_edge_midpoints_center_count':len(samples),'max_actual_child_surface_error_m':float(dc.max()),'max_actual_parent_surface_error_m':float(dp.max()),'child_surface_normal':footnormal,'parent_surface_normal':parentnormal,'displaced_outside_negative_control_rejected':bad};row['passed']=row['whole_uninset_foot_polygon_inside_parent_patch']and allactual and plane<1e-6 and cn@pn<-.999999 and max(dc.max(),dp.max())<1e-6 and footnormal['pass']and parentnormal['pass']and bad;supports.append(row)
 # Exact source semantic solids correspond to the actual GLB; convex-part interiors must remain separate except intended boundary support.
 faults=[];candidate_count=0
 for an,at in geometry[k].items():
  av=at.reshape(-1,3);ah=ConvexHull(np.unique(av,axis=0));alo=av.min(0);ahi=av.max(0)
  for bn,bt in geometry[parent].items():
   bv=bt.reshape(-1,3);blo=bv.min(0);bhi=bv.max(0)
   if np.min(np.minimum(ahi,bhi)-np.maximum(alo,blo))<=1e-6:continue
   candidate_count+=1;bh=ConvexHull(np.unique(bv,axis=0));eq=np.concatenate([ah.equations,bh.equations]);result=linprog([0,0,0],A_ub=eq[:,:3],b_ub=-eq[:,3]-1e-6,bounds=[(None,None)]*3,method='highs')
   if result.success:faults.append({'child_part':an,'parent_part':bn,'strict_shared_interior_point_m':result.x.tolist()})
 interpenetrations.append({'child':k,'parent':parent,'nontrivial_solid_pair_candidates':candidate_count,'strict_interior_intersections':faults,'passed':not faults})
report={'passed':all(x['inside_historical_outer_allocation']for x in bounds)and all(x['passed']for group in [empty,supports,interpenetrations]for x in group),'bindings':[bind(pp),*list({x['path']:x for x in bindings}.values())],'actual_instance_bounds':bounds,'empty_region_tests':empty,'supported_repeated_containers':supports,'parent_child_whole_solid_interference':interpenetrations,'design_count':4,'instance_count':6,'source_to_ship_rotation_determinant':float(np.linalg.det(S)),'actual_host_or_slot_adoption':False,'limits':['Independent actual parsed GLB placement inside historical outer allocation only; exact source semantic meshes supply physical labels and have separately passed source/native checks.','All foot polygon corners and edge midpoints use exact uninset source coordinates here; nearest-triangle witnesses avoid BVH ray-start ambiguity. Whole polygon proof uses all uninset vertices and convexity.','Case bodies may overhang their bottom foot without losing support; this is geometric support only, not stability/load/friction proof.','Unknown R070 finished wall/door/pocket/head/ceiling/support/owner slots and actual cart/body/reach remain unresolved. All six empty regions are adjustable QA proposals, not mandated safe clearance.'],'executed_script_sha256':sha(Path(__file__))}
(OUT/'independent_arrangement_review.json').write_text(json.dumps(report,indent=2)+'\n');print('ARRANGEMENT',report['passed'],'bounds',len(bounds),'empty',len(empty),'supports',len(supports),'solid intersections',interpenetrations)
