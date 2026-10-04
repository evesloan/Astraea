"""Whole convex volumes, useful void positive controls and actual native GLB correspondence."""
from pathlib import Path
import json,itertools,hashlib,importlib.util
import numpy as np
from scipy.spatial import ConvexHull,cKDTree
from scipy.optimize import linprog
BASE=Path(__file__).resolve().parents[1];CAT=BASE.parents[1]
spec=importlib.util.spec_from_file_location('native_reader',CAT/'qa/inspect_glb_independent.py');reader=importlib.util.module_from_spec(spec);spec.loader.exec_module(reader)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def hull(v):
 v=np.asarray(v);h=ConvexHull(v);return {'v':v,'eq':h.equations,'lo':v.min(0),'hi':v.max(0)}
def box(lo,hi):return hull(list(itertools.product(*zip(lo,hi))))
def overlap(a,b,tol=3e-6):
 if np.any(np.minimum(a['hi'],b['hi'])-np.maximum(a['lo'],b['lo'])<=tol):return False,0
 eq=np.concatenate((a['eq'],b['eq']));r=linprog([0,0,0,-1],A_ub=np.column_stack((eq[:,:3],np.ones(len(eq)))),b_ub=-eq[:,3],bounds=[(None,None)]*4,method='highs');rad=float(r.x[3])if r.success else -1;return rad>tol,rad
def native_meshes(g):
 meshes=[];markers={};d=g.doc
 def visit(i,parent):
  n=d['nodes'][i];w=parent@g.matrix(n)
  if 'mesh'in n:
   for p in d['meshes'][n['mesh']]['primitives']:
    pos=g.accessor(p['attributes']['POSITION']);pts=(np.column_stack((pos,np.ones(len(pos))))@w.T)[:,:3];role=d['materials'][p['material']]['name'].replace('ASTRAEA_','');meshes.append((role,pts))
  else:markers[n.get('name','')]=w[:3,3]
  for c in n.get('children',[]):visit(c,w)
 for i in d['scenes'][d.get('scene',0)]['nodes']:visit(i,np.eye(4))
 return meshes,markers
source=json.loads((BASE/'qa/evaluated_source_geometry.json').read_text());body=json.loads((BASE/'actor_proxies/body_collision_subset.json').read_text())['assets'];rows=[]
for ident,data in source.items():
 rec=json.loads((BASE/f'{ident}.manifest.json').read_text());hs={p['name']:hull(p['vertices'])for p in data['parts']};bh=[hull(p['points_source_m'])for p in body[ident]['shapes']];voids=[]
 for v in data['voids']:
  vh=box(v['min_source_m'],v['max_source_m']);hits=[n for n,h in hs.items()if overlap(vh,h)[0]];bodyhits=[i for i,h in enumerate(bh)if overlap(vh,h)[0]];lo=np.array(v['min_source_m']);hi=np.array(v['max_source_m']);mid=(lo+hi)/2;r=np.minimum((hi-lo)/5,.01);blocked=overlap(vh,box(mid-r,mid+r))[0];voids.append({'name':v['name'],'detailed_solid_intrusions':hits,'optional_body_intrusions':bodyhits,'inserted_block_positive_control_detected':blocked,'passes':not hits and not bodyhits and blocked})
 intersections=[]
 for (n,a),(m,b)in itertools.combinations(hs.items(),2):
  hit,r=overlap(a,b)
  if hit:intersections.append({'parts':[n,m],'maximum_insphere_radius_m':r})
 arch=[]
 if ident.endswith('001'):
  profile=rec['details']['terracotta_opening_profile_source_xz_m'];full=hull([[x,y,z]for y in(-.309,.309)for x,z in profile]);shell=[n for n in hs if n.startswith(('pale_rising','recessed_terracotta','entry_pylon'))];hits=[n for n in shell if overlap(full,hs[n])[0]];bodyhits=[i for i,r in enumerate(body[ident]['shapes'])if any(n.startswith(('pale_rising','recessed_terracotta','entry_pylon'))for n in r['semantic_parts'])and overlap(full,bh[i])[0]];arch.append({'name':'entire_inner_arch_vs_every_surround_part','whole_profile_intrusions':hits,'optional_body_whole_profile_intrusions':bodyhits,'passes':not hits and not bodyhits})
 g=reader.GLB(BASE/rec['export']);check=g.inspect();native,marks=native_meshes(g);corr=[]
 for role in set(p['material_role']for p in data['parts']):
  src=np.concatenate([np.array(p['vertices'])for p in data['parts']if p['material_role']==role]);expected=src[:,[0,2,1]];expected[:,2]*=-1;actual=np.concatenate([p for r,p in native if r==role]);err=max(float(cKDTree(actual).query(expected)[0].max()),float(cKDTree(expected).query(actual)[0].max()));wrong=float(cKDTree(actual).query(src)[0].max());corr.append({'material_role':role,'bidirectional_native_vertex_error_m':err,'wrong_axis_control_max_error_m':wrong,'passes':err<3e-6 and wrong>.1})
 markerrows=[]
 for m in rec['physical_and_proposal_markers']:
  err=float(np.linalg.norm(marks[m['name']]-m['gltf_m']));markerrows.append({'name':m['name'],'actual_node_native_position_error_m':err,'passes':err<3e-6})
 envelope=np.concatenate([p for _,p in native]);bounds_ok=np.max(np.abs(envelope.min(0)-rec['bounds_gltf_y_up']['min_m']))<3e-6 and np.max(np.abs(envelope.max(0)-rec['bounds_gltf_y_up']['max_m']))<3e-6
 r={'catalogue_id':ident,'source_sha256':sha(BASE/rec['source']),'export_sha256':sha(BASE/rec['export']),'whole_volume_voids':voids,'whole_arch_profile':arch,'unexpected_solid_intersections':intersections,'native_role_correspondence':corr,'actual_native_markers':markerrows,'native_bounds_match':bool(bounds_ok),'native_mesh_issues':check['issues'],'detail_shape_count':len(hs),'optional_body_shape_count':len(bh),'all_passed':bool(all(x['passes']for x in voids+arch+corr+markerrows)and not intersections and bounds_ok and not check['issues'])};rows.append(r);print(ident,r['all_passed'],'void failures',[x['name']for x in voids if not x['passes']],'intersections',intersections)
(BASE/'qa/geometry_checks.json').write_text(json.dumps({'assets':rows,'all_passed':all(r['all_passed']for r in rows)},indent=2)+'\n')
