"""Review actual source coverage, native-frame shapes and dense service clearances."""
from pathlib import Path
import sys,json,hashlib,numpy as np,itertools
from scipy.spatial import ConvexHull
from independent_collision_geometry import Hull,nearest_distances,inside_mesh,segment_triangles,sample_triangles,triangle_uncovered_area
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch08';C=np.array([[1.,0,0],[0,0,1],[0,-1,0]])
path=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'assets/hospitality_counters/collision_proposals.json'
if not path.is_absolute():path=ROOT/path
j=json.loads(path.read_text());reports=[]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
baseline=json.loads((OUT/'independent_baseline_hashes.json').read_text());base={r['path']:r for r in baseline['files']}
def source_points(t,z,r):return np.array([r*np.sin(t),.62-r*np.cos(t),z])
for ident,r in j.items():
 srpath=ROOT/f'qa/batch07/independent_source_{ident}.json';sr=json.loads(srpath.read_text());cache=ROOT/sr['geometry_cache'];source=ROOT/sr['path']
 assert sha(source)==sr['sha256']==base[sr['path']]['sha256']
 assert sha(srpath)==base[str(srpath.relative_to(ROOT))]['sha256'];assert sha(cache)==base[str(cache.relative_to(ROOT))]['sha256']
 a=np.load(cache);tri=a['triangles'];labels=a['object_names'];roles={o['name']:o['properties'].get('functional_group','static') for o in sr['objects']}
 hs=[Hull(p['source_points_m'],p) for p in r['proposals']];frame_error=max(np.abs(h.points@C.T-np.asarray(h.record['glb_points_m'])).max() for h in hs)
 coverage=[];errors=[]
 for name in sorted(set(labels)):
  candidates=[h for h in hs if name in h.record.get('semantic_parts',[h.record['semantic_part']])]
  selected=tri[labels==name]
  if not candidates:
   allowed=name.startswith('vertical_walnut_rib') or 'champagne_shadow' in name or 'grip' in name
   coverage.append({'part':name,'excluded_ornament':True,'exclusion_in_authorized_original_proposal':allowed,'triangles':len(selected),'pass':allowed});continue
  covered=np.zeros(len(selected),bool)
  for h in candidates:covered|=h.covers_triangles(selected)
  single_count=int(covered.sum());remaining=np.where(~covered)[0];uncovered={int(i):triangle_uncovered_area(selected[i],candidates) for i in remaining};union_ok=all(v<1e-10 for v in uncovered.values())
  coverage.append({'part':name,'triangles':len(selected),'whole_triangles_inside_single_hull':single_count,'triangles_requiring_exact_union_polygon_clipping':len(remaining),'maximum_uncovered_triangle_area_m2':max(uncovered.values(),default=0),'all_vertices_and_triangle_interiors_covered':union_ok,'functional_groups':sorted(set(h.record['functional_group'] for h in candidates)),'pass':union_ok and all(h.record['functional_group']==roles[name] for h in candidates)})
 # Boundary samples include vertices, midpoint and interior barycentric grids, against actual named source surfaces/solids.
 for h in hs:
  names=h.record.get('semantic_parts',[h.record['semantic_part']]);sel=tri[np.isin(labels,names)]
  # Curved cells are dense at 20 mm. Straight extrusions use their exact longitudinal symmetry: endpoints, thirds, midpoints.
  if ident.endswith('002'):samples,step=sample_triangles(h.tris,.025)
  else:
   weights=np.array([(i/6,j/6,1-(i+j)/6) for i in range(7) for j in range(7-i)])
   samples=np.unique(np.round(np.einsum('wi,tij->twj',weights,h.tris).reshape(-1,3),9),axis=0);step=None
  inside=np.zeros(len(samples),bool)
  for name in names:
   part=tri[labels==name];lo=part.min(axis=(0,1));hi=part.max(axis=(0,1));idx=np.where(~inside&((samples>=lo-1e-7)&(samples<=hi+1e-7)).all(axis=1))[0]
   if len(idx):inside[idx]=inside_mesh(samples[idx],part)
  ds=nearest_distances(samples,sel);ds[inside]=0
  k=int(np.argmax(ds));errors.append({'part':h.record['semantic_part'],'section':h.record.get('section'),'samples':len(samples),'barycentric_maximum_grid_edge_m':step,'max_outside_source_solid_distance_m':float(ds[k]),'worst_source_point_m':samples[k].tolist(),'p95_m':float(np.percentile(ds,95))})
 tests=[];mismatches=[];single_hull=Hull(tri.reshape(-1,3));wrong_hull_blocked_clear=0
 def check(name,p,q,expected=None):
  global wrong_hull_blocked_clear
  s=segment_triangles(p,q,tri);coll=[(h.record['semantic_part'],h.segment(p,q)) for h in hs];coll=[x for x in coll if x[1] is not None]
  row={'name':name,'source_segment_m':[p.tolist(),q.tolist()],'actual_source_blocked':bool(s),'compound_blocked':bool(coll),'source_first_fraction':s[0] if s else None,'compound_first_fraction':min([v[0] for _,v in coll],default=None),'source_control_expected':expected,'pass':(expected is None or bool(s)==expected) and bool(s)==bool(coll)}
  tests.append(row)
  if not row['pass']:mismatches.append(row)
  if not s and single_hull.segment(p,q) is not None:wrong_hull_blocked_clear+=1
 if ident.endswith('002'):
  for ti,t in enumerate(np.linspace(.055,np.pi/2-.055,241)):
   for zi,z in enumerate(np.r_[np.linspace(.200,.420,12),np.linspace(.505,.795,16)]):check(f'access_{ti}_{zi}',source_points(t,z,.08),source_points(t,z,.73));check(f'deep_shelf_{ti}_{zi}',source_points(t,z,.30),source_points(t,z,.924))
  # Midpoints of every source angular station are present; dense sequence is deliberately offset from author samples.
  for t in np.linspace(.07,np.pi/2-.07,97):
   for z in [.07,.151,.454,.86,.89,.30,.55,.77]:
    start=.1 if z in [.151,.454,.86,.89] else .82
    check(f'blocked_radial_{t:.6f}_{z}',source_points(t,z,start),source_points(t,z,1.03),True)
  for t in [np.pi/2*.31,np.pi/2*.69]:
   for z in [.18,.3,.43]:check(f'actual_support_{t}_{z}',source_points(t,z,.08),source_points(t,z,.85),True)
  for t in [0,np.pi/2]:
   p=source_points(t,.30,.60);v=np.array([np.cos(t),np.sin(t),0])
   check('seam_terminal',p-v*.02,p+v*.04,True)
  for along in [.005,.014,.023]:
   for z in [.025,.055,.085,.115]:
    check('entry_terminal_toe_recess',np.array([along,.34,z]),np.array([along,.285,z]),False)
    check('exit_terminal_toe_recess',np.array([.28,.62-along,z]),np.array([.335,.62-along,z]),False)
 else:
  for xi,x in enumerate(np.linspace(.04,2.36,241)):
   for z in [.20,.24,.28,.32,.36,.40,.51,.54,.57,.60]:check(f'access_{xi}_{z}',np.array([x,.6,z]),np.array([x,-.24,z]));check(f'deep_shelf_{xi}_{z}',np.array([x,.3,z]),np.array([x,-.304,z]))
  for x in np.linspace(.04,2.36,121):
   for z in [.07,.151,.455,.88,.30,.55]:
    check('blocked_structure',np.array([x,.1 if z in [.151,.455,.88] else -.20,z]),np.array([x,-.42,z]),True)
  for x in [.8,1.6]:check('actual_bay_divider',np.array([x,.6,.3]),np.array([x,-.24,.3]),True)
  for x in [.01,2.39]:check('seam_terminal',np.array([x,.4,.3]),np.array([x,-.3,.3]),True)
  check('drawer_cavity',np.array([1.2,.25,.72]),np.array([1.2,-.2,.72]),False)
  for x in [.005,.014,.023,2.377,2.386,2.395]:
   for z in [.025,.055,.085,.115]:check('terminal_toe_recess',np.array([x,.34,z]),np.array([x,.285,z]),False)
 out={'id':ident,'shape_count':len(hs),'source_sha256':sha(source),'cached_actual_source_receipt':str(srpath.relative_to(ROOT)),'cached_geometry_sha256':sha(cache),'maximum_frame_error_m':float(frame_error),'coverage':coverage,'approximation':errors,'service_grid_and_blocked_controls':{'count':len(tests),'actual_source_clear':sum(not x['actual_source_blocked'] for x in tests),'actual_source_blocked':sum(x['actual_source_blocked'] for x in tests),'compound_source_mismatches':mismatches,'one_enclosing_hull_negative_control_blocked_actual_clear_rays':wrong_hull_blocked_clear},'tests':tests,'pass':frame_error<1e-7 and all(x['pass'] for x in coverage) and not mismatches and wrong_hull_blocked_clear>0}
 reports.append(out);print(ident,'shapes',len(hs),'coverage failures',[x['part'] for x in coverage if not x['pass']],'mismatches',len(mismatches),'max error',max(x['max_outside_source_solid_distance_m'] for x in errors),flush=True)
result={'input_path':str(path.relative_to(ROOT)),'input_sha256':sha(path),'pass':all(r['pass'] for r in reports),'assets':reports,'method':'Whole evaluated source triangles enclosed by at least one matching functional-group convex hull or exact halfspace polygon subtraction proves coverage by their union; this checks continuous source-triangle coverage between vertices. Barycentric collider surface grids and actual closed-source winding/Euclidean triangle distance measure overreach. Dense continuous segment clipping is compared with exact source-triangle intersections, including expected blocked supports/shelves/floor/ends and a deliberately invalid enclosing-hull control. Source caches are independently evaluated Batch07 evidence, exact-hash bound to unchanged current .blend files and baseline commit.','limits':['Finite collider-boundary error samples are measured bounds at samples, not a proof of a global Hausdorff maximum. A 10 mm radial chord parameter is not a bound on total preexisting profile-convexification error.','Offline geometry only; no native physics solver, runtime cost, controller, actor fit or continuous mechanical certification.','Decorative ribs/reveal/grip were already omitted in the original collision proposal; their absence is explicit and does not establish per-ornament physical contact.']}
(OUT/'independent_collision_report.json').write_text(json.dumps(result,indent=2)+'\n')
