from pathlib import Path
import json,sys,hashlib,numpy as np
R=Path(__file__).resolve().parent;G=Path('/workspace/shared/astraea-godot-production-20261003');C=Path('/workspace/shared/astraea-catalogue-continuation-20261002');P=C/'assets/grand_lantern_theater_section'
sys.path.insert(0,str(P/'source/firstpass_003/dependencies'));from geometry_review import glb,Query
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
data=json.loads((G/'data/architecture/THEATER_RUNTIME_STAGE001.json').read_text());static=glb(G/'assets/models'/data['static_file']);bridge=glb(G/'assets/models'/data['bridge_file']);moving=glb(G/'assets/models'/data['moving_file']);q=Query(static['meshes']+bridge['meshes'])
mechanisms=json.loads(Path('/workspace/scratch/375c2e438292/theater_resume/first_pass_plan/mechanism_package_compact.json').read_text());parts={r['name']:r for r in mechanisms['objects']}
source_anchor=np.array([-34.75,70.71,-130.8]);target_anchor=np.array([-34.,71.1,-128.82]);rotation=np.diag([-1.,1.,-1.]);new=[]
for name in ['THEATER_D11_MAIN_call_plate','THEATER_D11_MAIN_call_lens']:
 row=parts[name];v=(np.asarray(row['vertices_world'])-source_anchor)@rotation.T+target_anchor;tr=np.array([[v[f[0]],v[f[i]],v[f[i+1]]]for f in row['faces']for i in range(1,len(f)-1)]);lo=v.min(0);hi=v.max(0);hits=q.prism_hits([*lo,*hi],tolerance=.00001)
 new.append({'name':name.replace('MAIN_call','MAIN_exterior_call'),'retained_source_part':name,'vertices_world':v.tolist(),'faces':row['faces'],'uv_faces':row['uv_faces'],'material_ref':row['material_ref'],'bounds_native':[lo.tolist(),hi.tolist()],'unapproved_positive_volume_neighbor_hits':hits})
assert not any(p['unapproved_positive_volume_neighbor_hits']for p in new)
fixtures=[{'id':'interior','lens_source_part':'THEATER_D11_MAIN_call_lens','target':[-34.797,70.71,-130.8],'source_face':[-34.795,70.71,-130.8],'stance':[-35.9,69.5,-130.8],'outward':[-1,0,0]}, {'id':'exterior','lens_source_part':'THEATER_D11_MAIN_exterior_call_lens','target':[-33.953,71.1,-128.82],'source_face':[-33.955,71.1,-128.82],'stance':[-32.8,69.5,-128.05],'outward':[1,0,0]}]
regions=json.loads((G/'data/generated/structural_meshes.json').read_text())['regions']
def inside(p,t):
 p=np.array(p);t=np.array(t);v=[np.cross(t[(i+1)%3]-t[i],p-t[i])for i in range(3)];return min(v)>=-1e-8 or max(v)<=1e-8
for f in fixtures:
 eye=np.array(f['stance'])+[0,1.65,0];target=np.array(f['target']);hits=q.rays(eye,target);f['eye']=eye.tolist();f['ray_distance_m']=float(np.linalg.norm(target-eye));f['retained_geometry_blocks']=hits[:3];f['supported_footprint_samples']=[]
 for dx,dz in [(0,0),(.3,0),(-.3,0),(0,.3),(0,-.3)]:
  point=[f['stance'][0]+dx,f['stance'][2]+dz];owners=[r['id']for r in regions if abs(r['floor_y']-69.5)<.0001 and any(inside(point,t)for t in r['triangles'])];f['supported_footprint_samples'].append({'point_xz':point,'owners':owners})
 assert f['ray_distance_m']<2.5 and not hits and all(x['owners']for x in f['supported_footprint_samples'])
report={'status':'PASS_PURE_PROPOSED_CONTROL_SUPPORT_AND_REACH_SCREEN','source_ids':['THEATER_D11_MAIN_LEAF_LEFT','THEATER_D11_MAIN_LEAF_RIGHT'],'source_travel_m':2.65,'proposed_maximum_leaf_speed_m_s':1.0,'default_pose_fraction':1.0,'new_exterior_call':{'parts':new,'anchor_world':target_anchor.tolist(),'retained_original_anchor':source_anchor.tolist(),'rotation_native':rotation.tolist(),'exact_source_build_required':True},'controls':fixtures,'all_continuous_motion_contacts_and_native_interaction_pending':True,'scope':'Pure recipe/retained-GLB support and approach rays. Actual source reopen, import contact equivalence, real player/cart, pause and native open/closed review still required.','input_pins':{str(p):sha(p)for p in [G/'data/architecture/THEATER_RUNTIME_STAGE001.json',G/'data/generated/structural_meshes.json',G/'scripts/service_door.gd',G/'scripts/player.gd',G/'assets/models'/data['static_file'],G/'assets/models'/data['moving_file'],G/'assets/models'/data['bridge_file']]}}
out=R/'PURE_ENTRY_PLAN.json';assert not out.exists();out.write_text(json.dumps(report,indent=2)+'\n');print('PASS',sha(out),[(f['id'],round(f['ray_distance_m'],3))for f in fixtures])
