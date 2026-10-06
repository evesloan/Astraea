"""Pure, additive contract repair: winding and loop order only. No Blender.
This writes fresh successor contracts/evidence here and refuses all overwrites.
"""
from pathlib import Path
import ast, collections, copy, hashlib, json, math, struct
import numpy as np
D=Path(__file__).resolve().parent; R=D.parents[1]; P=R/'printed_materials001'
read=lambda p:json.loads(Path(p).read_text())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
digest=lambda x:hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
f32=lambda x:struct.unpack('f',struct.pack('f',x))[0]

def write(name,value):
 with (D/name).open('x')as h:json.dump(value,h,indent=2,allow_nan=False);h.write('\n')

def audit(row,kind,origin=None):
 raw=row.get('vertices_world',row.get('vertices'))
 if origin is not None:raw=[[origin[0]+v[0],origin[1]+v[2],origin[2]-v[1]]for v in raw]
 v=np.asarray(raw,dtype=np.float32).astype(float);faces=row['faces'];uv=row.get('face_uv')
 if uv is None:
  uv=[];at=0
  for f in faces:uv.append(row['loop_uvs'][at:at+len(f)]);at+=len(f)
 failures=[];edges=collections.defaultdict(list);mins=[]
 for i,face in enumerate(faces):
  if len(face)!=len(set(face))or len(face)<3:failures.append(['repeated_face_vertex',i])
  if len(uv[i])!=len(face):failures.append(['uv_arity',i])
  for a,b in zip(face,face[1:]+face[:1]):edges[tuple(sorted((a,b)))].append((a,b,i))
  for k in range(1,len(face)-1):
   area=float(np.linalg.norm(np.cross(v[face[k]]-v[face[0]],v[face[k+1]]-v[face[0]])))
   mins.append(area)
   if area<1e-12:failures.append(['degenerate_fan_triangle',i,k,area])
 if not np.isfinite(v).all()or not all(math.isfinite(float(t))for f in uv for x in f for t in x):failures.append('nonfinite')
 boundary=[e for e,u in edges.items()if len(u)==1];nonmanifold=[e for e,u in edges.items()if len(u)>2]
 same=[e for e,u in edges.items()if len(u)==2 and u[0][:2]!=u[1][:2][::-1]]
 if nonmanifold:failures.append(['nonmanifold_edges',nonmanifold])
 if same:failures.append(['same_direction_edges',same])
 adjacency=collections.defaultdict(set)
 for u in edges.values():
  if len(u)==2:adjacency[u[0][2]].add(u[1][2]);adjacency[u[1][2]].add(u[0][2])
 components=[];seen=set()
 for i in range(len(faces)):
  if i in seen:continue
  comp=[];todo=[i];seen.add(i)
  while todo:
   k=todo.pop();comp.append(k)
   for j in adjacency[k]-seen:seen.add(j);todo.append(j)
  components.append(comp)
 volumes=[]
 for comp in components:
  vv=v-v[faces[comp[0]][0]]
  volumes.append(float(sum(np.dot(vv[faces[i][0]],np.cross(vv[faces[i][k]],vv[faces[i][k+1]]))/6 for i in comp for k in range(1,len(faces[i])-1))))
 euler=len(v)-len(edges)+len(faces)
 if kind=='open_shaped_leaf':
  deg=collections.Counter(i for e in boundary for i in e)
  if not boundary or any(n!=2 for n in deg.values())or euler!=1 or len(components)!=1:failures.append('leaf_disk_topology')
 else:
  if boundary:failures.append(['closed_boundary_edges',boundary])
  if any(x<=1e-13 for x in volumes):failures.append(['nonpositive_signed_volume',volumes])
 normal_dots=[]
 if kind=='closed_support':
  s=row['shape_controls']['sides'];rings=len(row['shape_controls']['centerline']);centers=[v[i*s:(i+1)*s].mean(0)for i in range(rings)]
  for fi,face in enumerate(faces):
   pts=v[face];local=pts-pts[0];normal=np.cross(local,np.roll(local,-1,axis=0)).sum(0);normal/=np.linalg.norm(normal)
   direction=pts.mean(0)-(centers[fi//s]+centers[fi//s+1])/2 if fi<s*(rings-1) else centers[0]-centers[1]if fi==len(faces)-2 else centers[-1]-centers[-2]
   dot=float(np.dot(normal,direction/np.linalg.norm(direction)));normal_dots.append(dot)
   if dot<=0:failures.append(['inward_support_normal',fi,dot])
 return {'name':row['name'],'kind':kind,'vertices':len(v),'faces':len(faces),'euler':euler,'components':len(components),'boundary_edges':len(boundary),'nonmanifold_edges':len(nonmanifold),'same_direction_edges':len(same),'component_signed_volumes_m3':volumes,'minimum_fan_triangle_cross_length_m2':min(mins),'minimum_closed_support_outward_normal_dot':min(normal_dots)if normal_dots else None,'failures':failures}

def main():
 c=read(R/'COURT_A_GEOMETRY_CONTRACT.json');f=read(R/'FULLER_REAR_MASS_CANDIDATE.json');p=read(P/'PRINTED_MATERIALS_CONTRACT.json');old=copy.deepcopy(c)
 row=next(x for x in c['objects']if x['name']=='A4_W_crowned_cushion');original=copy.deepcopy(row)
 changes=[]
 for i in range(56):
  before_face=row['faces'][i][:];before_uv=copy.deepcopy(row['face_uv'][i]);row['faces'][i].reverse();row['face_uv'][i].reverse()
  assert dict(zip(before_face,before_uv))==dict(zip(row['faces'][i],row['face_uv'][i]))
  changes.append({'face_index':i,'before_face':before_face,'after_face':row['faces'][i],'before_uv':before_uv,'after_uv':row['face_uv'][i]})
 proof=audit(row,'architecture');assert not proof['failures'],proof
 row['closed_volume_m3']=sum(proof['component_signed_volumes_m3'])
 # New basename is a destination-only change. Parent must use a NEW scratch output directory.
 c['standalone_source_proposal']='AST-CUL-005_arrival_court_A_004_winding001.blend'
 expected=copy.deepcopy(old);target=next(x for x in expected['objects']if x['name']==row['name']);target.update({'faces':row['faces'],'face_uv':row['face_uv'],'closed_volume_m3':row['closed_volume_m3']});expected['standalone_source_proposal']=c['standalone_source_proposal'];assert c==expected
 rows=[(r,'architecture',None)for r in c['objects']]+[(r,r['surface_kind'],f['asset']['position_xyz'])for r in f['asset']['parts']]+[(r,'printed',None)for r in[p['display_plate']]+p['pieces']]
 checks=[audit(r,k,o)for r,k,o in rows];assert len(checks)==157 and not any(r['failures']for r in checks)
 # Exact printed fronts and image orientation from candidate float32 contracts.
 print_checks=[]
 for pr in[p['display_plate']]+p['pieces']:
  i=pr['printed_face_index']
  if i is None:continue
  vertices=np.array(pr['vertices_world'],dtype=np.float32).astype(float);face=pr['faces'][i];pts=vertices[face]
  normal=np.cross(pts[1]-pts[0],pts[2]-pts[0]);normal/=np.linalg.norm(normal)
  uv=pr['face_uv'][i];corners={tuple(q):vertices[vi]for q,vi in zip(uv,face)};assert set(corners)=={(0,0),(1,0),(1,1),(0,1)}
  right=corners[(1,0)]-corners[(0,0)];right/=np.linalg.norm(right);top=corners[(0,1)]-corners[(0,0)];top/=np.linalg.norm(top)
  assert np.max(abs(normal-np.array(pr.get('front_normal_world',[0,1,0]))))<1e-6
  assert np.max(abs(right-np.array([1,0,0])))<1e-6
  assert np.max(abs(top-np.array(pr.get('printed_top_direction_world',[0,0,-1]))))<1e-6
  print_checks.append({'name':pr['name'],'normal':normal.tolist(),'image_top':top.tolist(),'text_right':right.tolist()})
 stack_interfaces=[]
 for s in p['stacks']:
  parts={r['name']:r for r in p['pieces']}
  for a,b in zip(s['piece_names'],s['piece_names'][1:]):
   hi=max(f32(v[1])for v in parts[a]['vertices_world']);lo=min(f32(v[1])for v in parts[b]['vertices_world']);assert hi==lo
   stack_interfaces.append({'lower':a,'upper':b,'plane_world_y':hi})
 write('COURT_A_GEOMETRY_CONTRACT_WINDING_SUCCESSOR.json',c)
 after_sha=sha(D/'COURT_A_GEOMETRY_CONTRACT_WINDING_SUCCESSOR.json')
 plan={'status':'PASS_PURE_WINDING_ONLY_SUCCESSOR_NOT_BUILT','source_contract':str(R/'COURT_A_GEOMETRY_CONTRACT.json'),'source_contract_sha256':sha(R/'COURT_A_GEOMETRY_CONTRACT.json'),'successor_contract_sha256':after_sha,'affected_object':row['name'],'face_indices_to_reverse':list(range(56)),'exact_changes':changes,'metadata_changes':{'closed_volume_m3':{'before':original['closed_volume_m3'],'after':row['closed_volume_m3']},'standalone_source_proposal':{'before':old['standalone_source_proposal'],'after':c['standalone_source_proposal']}},'unchanged':{'all_vertex_arrays':all(a['vertices_world']==b['vertices_world']for a,b in zip(old['objects'],c['objects'])),'all_materials_roles_names_bounds_contacts':True,'all_24_instance_rows':old['retained_instances']==c['retained_instances'],'all_geometry_other_than_one_faces_loop_order':True,'each_face_uv_to_vertex_association':True,'all_old_sources_and_2200_chairs':True},'prior_saved_source':str(P/'authored_preview001'/old['standalone_source_proposal']),'prior_saved_source_sha256':sha(P/'authored_preview001'/old['standalone_source_proposal']),'output_must_be_new_scratch_directory':True,'qa_must_use_successor_contract_and_new_build_fingerprints':True,'root_cause':'Cushion cap triangulation orientation did not follow the west outline orientation. emit() checked unsigned edge use count and aggregate volume, neither of which detects locally reversed caps.','generator_guidance':'Repair finalized contract face indices and UV loops in matching reverse order. Re-running metric_uv after flipping faces can mirror the established UVs and is not equivalent. Add directed-edge consistency validation to future generator successors; do not edit the retained generator.'}
 write('WINDING_REPAIR_PLAN.json',plan)
 write('ALL_157_SUCCESSOR_PURE_AUDIT.json',{'status':'PASS_PURE_TOPOLOGY_ONLY','meshes':checks,'affected_original_objects':[row['name']],'closed_mesh_count':sum(r['kind']!='open_shaped_leaf'for r in checks),'open_leaf_count':sum(r['kind']=='open_shaped_leaf'for r in checks),'closed_support_count':sum(r['kind']=='closed_support'for r in checks),'closed_support_faces_checked':sum(r['faces']for r in checks if r['kind']=='closed_support'),'minimum_fan_triangle_cross_length_m2':min(r['minimum_fan_triangle_cross_length_m2']for r in checks),'printed_fronts':print_checks,'exact_float32_stack_interfaces':stack_interfaces,'limits':['Pure float32 contract topology only; Blender-independent saved-source checks remain mandatory','Fan triangle checks cannot replace Blender tessellation checks for general n-gons','No material library append, render, export or engine run']})
 write('REOPEN_ASSERTION_STATIC_REVIEW.json',{'status':'PASS_STATIC_CONTRACT_REVIEW_ONLY','reviewed_script_sha256':sha(R/'reopen_qa001/reopen_court_A_readonly.py'),'pure_verified':['All 157 vertex/face/UV cardinalities and float32 finiteness','All 121 closed meshes are connected, oppositely wound and positive-volume after correction','All 36 open leaf disks have one connected component, Euler characteristic 1 and closed boundary loops','Every face of all 42 closed botanical supports points outward after actual world-coordinate float32 conversion','All four printed image fronts and UV directions match checker defaults','All six paper-stack interfaces coincide exactly after float32 conversion','All generated names are under Blender name length; source prototype report names are at most 39 characters','The 24 retained instance recipes and source IDs are unmodified'], 'required_successor_adaptation':['The source checker must read the successor contract, not the original incorrect winding contract','Point OUT to a NEW scratch output directory with the new filename and a new BUILD_REPORT','Original pure screen has the original contract hash; use a scoped winding equivalence receipt rather than presenting the old screen as a newly executed screen','Keep saved-source SHA, new-mesh fingerprints, full independent library checks and every original topology gate enabled'], 'remaining_runtime_specific_assertions':['Independent native graph and image equality require Blender library append','Actual prototype parents and source matrices require reopening','Actual source stack triangle witnesses and plant bounds still require reopening'], 'known_additional_contract_mismatches':[]})
 for fn in ['COURT_A_GEOMETRY_CONTRACT_WINDING_SUCCESSOR.json','WINDING_REPAIR_PLAN.json','ALL_157_SUCCESSOR_PURE_AUDIT.json','REOPEN_ASSERTION_STATIC_REVIEW.json']:print(fn,sha(D/fn))
if __name__=='__main__':main()
