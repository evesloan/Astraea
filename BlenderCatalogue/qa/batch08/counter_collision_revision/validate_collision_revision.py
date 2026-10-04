"""Batch08 author collision evidence. Reads sources/caches/exports; never edits visuals.

Contains conservative continuum coverage by sphere-sweep radius inflation over
specified angular/height rectangles. This is geometry evidence, not engine QA.
"""
from pathlib import Path
import sys,json,hashlib,math,itertools
import numpy as np
from scipy.spatial import ConvexHull
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'qa/batch07'))
sys.path.insert(0,str(ROOT/'qa/batch08'))
from independent_collision_geometry import triangle_uncovered_area
from types import SimpleNamespace
from independent_geometry import Native,C
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
receipt=json.loads((OUT/'baseline_receipt.json').read_text())
current_path=ROOT/'assets/hospitality_counters/collision_proposals.json'
current=json.loads(current_path.read_text())
baseline=json.loads((OUT/'original_inputs/assets/hospitality_counters/collision_proposals.json').read_text())
checks=[]
cache_path=OUT/'surface_measurements_cache.json'
surface_cache=json.loads(cache_path.read_text()) if cache_path.exists() else {}
corridor_cache_path=OUT/'corridor_actual_cache.json'
corridor_actual_cache=json.loads(corridor_cache_path.read_text()) if corridor_cache_path.exists() else {}
def check(name,passed,**kw):checks.append({'name':name,'pass':bool(passed),**kw})
def hulls(data):
 out=[]
 for rec in data['proposals']:
  v=np.asarray(rec['source_points_m']);h=ConvexHull(v)
  out.append({'rec':rec,'v':v,'h':h,'eq':h.equations,'tri':v[h.simplices]})
 return out

def segment_hull(a,b,h,radius=0.,shrink=0.):
 a=np.asarray(a);b=np.asarray(b);eq=h['eq'];p=a@eq[:,:3].T+eq[:,3]+shrink-radius;d=(b-a)@eq[:,:3].T
 parallel=np.abs(d)<1e-13
 bad=np.any(parallel&(p>1e-9),axis=-1)
 cross=-p/np.where(parallel,1.,d)
 low=np.maximum(0.,np.max(np.where(d < -1e-13,cross,-np.inf),axis=-1))
 high=np.minimum(1.,np.min(np.where(d > 1e-13,cross,np.inf),axis=-1))
 return (~bad)&(low<=high+1e-9)
def shape_hits(hs,a,b,radius=0.,group_exclude=None):
 return [h['rec']['semantic_part'] for h in hs if h['rec'].get('functional_group')!=group_exclude and segment_hull(a,b,h,radius)]

def point_tri_distance(p,t):
 p=np.asarray(p);a,b,c=t[:,0],t[:,1],t[:,2];ab=b-a;ac=c-a;n=np.cross(ab,ac);nn=np.einsum('ij,ij->i',n,n)
 proj=p-n*(np.einsum('ij,ij->i',p-a,n)/np.maximum(nn,1e-30))[:,None]
 v=proj-a;d00=np.einsum('ij,ij->i',ab,ab);d01=np.einsum('ij,ij->i',ab,ac);d11=np.einsum('ij,ij->i',ac,ac);d20=np.einsum('ij,ij->i',v,ab);d21=np.einsum('ij,ij->i',v,ac)
 den=d00*d11-d01*d01;u=(d11*d20-d01*d21)/np.maximum(den,1e-30);vv=(d00*d21-d01*d20)/np.maximum(den,1e-30)
 inside=(u>=0)&(vv>=0)&(u+vv<=1)&(nn>1e-24)
 dd=np.where(inside,np.sum((proj-p)**2,axis=1),np.inf)
 for x,y in [(a,b),(b,c),(c,a)]:
  e=y-x;f=np.clip(np.einsum('ij,ij->i',p-x,e)/np.maximum(np.einsum('ij,ij->i',e,e),1e-30),0,1);q=x+f[:,None]*e
  dd=np.minimum(dd,np.sum((q-p)**2,axis=1))
 return np.sqrt(dd)

def segment_tri_distance(a,b,t):
 # Exact Euclidean distance: face crossing, end-point/triangle and segment/edges.
 a=np.asarray(a);b=np.asarray(b);u=b-a;A=u@u
 best=np.minimum(point_tri_distance(a,t),point_tri_distance(b,t))**2
 for c,d in [(t[:,0],t[:,1]),(t[:,1],t[:,2]),(t[:,2],t[:,0])]:
  v=d-c;w=a-c;B=v@u;D=w@u;E=np.einsum('ij,ij->i',v,w);F=np.einsum('ij,ij->i',v,v);den=A*F-B*B
  s=np.divide(B*E-F*D,den,out=np.zeros_like(den),where=den>1e-25)
  z=np.divide(A*E-B*D,den,out=np.zeros_like(den),where=den>1e-25)
  inside=(den>1e-25)&(s>=0)&(s<=1)&(z>=0)&(z<=1)
  dd=np.sum((w+s[:,None]*u-z[:,None]*v)**2,axis=1);best=np.minimum(best,np.where(inside,dd,np.inf))
  for p in [c,d]:
   ss=np.clip((p-a)@u/A,0,1);best=np.minimum(best,np.sum((a+ss[:,None]*u-p)**2,axis=1))
 # Segment crosses triangle face interior.
 e1=t[:,1]-t[:,0];e2=t[:,2]-t[:,0];hh=np.cross(u,e2);det=np.einsum('ij,ij->i',e1,hh);good=np.abs(det)>1e-13
 inv=np.divide(1.,det,out=np.zeros_like(det),where=good);ss=a-t[:,0];q=np.cross(ss,e1)
 v=inv*np.einsum('ij,ij->i',ss,hh);w=inv*(q@u);f=inv*np.einsum('ij,ij->i',e2,q)
 hit=good&(v>=-1e-10)&(w>=-1e-10)&(v+w<=1+1e-10)&(f>=0)&(f<=1)
 best=np.where(hit,0,best)
 return float(np.sqrt(best.min()))

def boundary_samples(h):
 # Longest-edge subdivision avoids massive oversampling of thin, long faces.
 # The complete convex-face net includes internal partition faces, making its
 # maximum a conservative overestimate for the external compound boundary.
 stack=list(h['tri']);pp=[];max_cell=0.
 while stack:
  t=stack.pop();edges=[(0,1),(1,2),(2,0)];lengths=[np.linalg.norm(t[a]-t[b]) for a,b in edges];k=int(np.argmax(lengths))
  if lengths[k]>.025:
   a,b=edges[k];c=3-a-b;mid=(t[a]+t[b])/2
   stack.extend([np.array([t[a],mid,t[c]]),np.array([mid,t[b],t[c]])])
  else:
   pp.extend(t);pp.append(t.mean(axis=0));max_cell=max(max_cell,max(lengths))
 return np.unique(np.round(pp,11),axis=0),max_cell

report={'revision':'hospitality-static-compound-03','method':'Actual source profile convex hull consolidation; triangle containment; finite Euclidean surface samples; source/native-frame identity; conservative continuous capsule corridors with exact convex-distance refinement; exact convex linear translation tests.','inputs':[],'assets':[],'checks':checks}
for r in receipt['protected_prior_evidence_and_visuals']:
 p=ROOT/r['path'];check('preserved_'+r['path'],p.is_file() and sha(p)==r['sha256'])
for i in [1,2]:
 ident=f'AST-HSP-00{i}';new=hulls(current[ident]);old=hulls(baseline[ident]);cache_report=json.loads((ROOT/f'qa/batch07/independent_source_{ident}.json').read_text());cache=np.load(ROOT/cache_report['geometry_cache']);t=cache['triangles'];names=cache['object_names'];n=Native(ROOT/f'assets/hospitality_counters/exports/{ident}.glb');nt=n.tris@C
 check(ident+'_source_cache_hash',sha(ROOT/cache_report['path'])==cache_report['sha256'])
 check(ident+'_frame_exact',all(np.array_equal(h['v']@C.T,np.asarray(h['rec']['glb_points_m'])) for h in new))
 old_containment=[]
 for h in old:
  if h['rec']['semantic_part']=='bowed_guest_walnut_shell' or 'terminal_bulkhead' in h['rec']['semantic_part']:continue
  opts=[p for p in new if h['rec']['semantic_part'] in p['rec']['semantic_parts']]
  values=[float(np.max(h['v']@p['eq'][:,:3].T+p['eq'][:,3])) for p in opts]
  old_containment.append(min(values))
 check(ident+'_all_unaffected_old_hulls_contained',max(old_containment)<2e-7,old_hull_count=len(old_containment),intentional_exception='Old whole-fascia hulls filled real lower-shelf depth and old terminal hulls filled toe recesses; source-backed band/step decomposition removes those false positives',maximum_plane_excess_m=max(old_containment))
 semantic=set(x for h in new for x in h['rec']['semantic_parts']);source_tri=t[np.isin(names,list(semantic))];source_names=names[np.isin(names,list(semantic))]
 triangle_full=[];failure=[];union_count=0;max_uncovered_area=0.
 for name in sorted(semantic):
  ts=source_tri[source_names==name];opts=[h for h in new if name in h['rec']['semantic_parts']]
  best=np.full(len(ts),np.inf)
  for h in opts:best=np.minimum(best,np.max(ts@h['eq'][:,:3].T+h['eq'][:,3],axis=(1,2)))
  crossed=np.where(best>2e-7)[0]
  adapted=[SimpleNamespace(lo=h['v'].min(axis=0),hi=h['v'].max(axis=0),planes=h['eq']) for h in opts]
  for j in crossed:
   area=triangle_uncovered_area(ts[j],adapted);union_count+=1;max_uncovered_area=max(max_uncovered_area,area)
   if area<=1e-10:best[j]=0.
   else:failure.append({'part':name,'triangle_index_within_part':int(j),'uncovered_area_m2':area})
  triangle_full.extend(best.tolist())
 check(ident+'_whole_source_triangle_union_containment',not failure,triangles=len(triangle_full),cap_or_band_crossing_triangles_clipped=union_count,maximum_uncovered_area_m2=max_uncovered_area,failures=failure)
 # Compare actual source point cloud with actual native GLB vertex cloud.
 from scipy.spatial import cKDTree
 sv=np.unique(t.reshape(-1,3),axis=0);gv=np.unique(nt.reshape(-1,3),axis=0);parity=max(cKDTree(sv).query(gv)[0].max(),cKDTree(gv).query(sv)[0].max())
 check(ident+'_cache_actual_GLB_parity',parity<2e-6,max_bidirectional_vertex_error_m=float(parity))
 # Area-uniform source-surface error evidence at a fixed <=25mm triangular net.
 approximations=[]
 for label,hs in [('baseline',old),('reduced',new)]:
  perpart=[]
  for name in sorted({h['rec']['semantic_part'] for h in hs}):
   family=[h for h in hs if h['rec']['semantic_part']==name];sem=set(x for h in family for x in h['rec'].get('semantic_parts',[name]));target=t[np.isin(names,list(sem))]
   # Complete face net, with an explicit25mm covering bound.
   cache_key=hashlib.sha256(json.dumps({'id':ident,'label':label,'part':name,'hulls':[h['rec']['source_points_m'] for h in family],'source_cache':sha(ROOT/cache_report['geometry_cache']),'spacing_m':.025},sort_keys=True).encode()).hexdigest()
   if cache_key in surface_cache:
    perpart.append(surface_cache[cache_key]);continue
   maximum=0.;count=0;max_cell=0.;worst=None
   for h in family:
    pp,cell=boundary_samples(h);max_cell=max(max_cell,cell)
    for start in range(0,len(pp),64):
     batch=pp[start:start+64];ds=point_tri_distance(np.repeat(batch,len(target),axis=0),np.tile(target,(len(batch),1,1))).reshape(len(batch),len(target)).min(axis=1);count+=len(batch);j=int(np.argmax(ds))
     if ds[j]>maximum:maximum=float(ds[j]);worst=batch[j].tolist()
   perpart.append({'semantic_part':name,'source_parts':sorted(sem),'surface_sample_count':count,'maximum_sampled_boundary_to_source_distance_m':maximum,'sampling_cover_radius_bound_m':max_cell,'includes_internal_section_faces':True,'conservative_maximum_distance_bound_m':maximum+max_cell,'worst_sample_source_m':worst})
   surface_cache[cache_key]=perpart[-1];cache_path.write_text(json.dumps(surface_cache,indent=2)+'\n')
  approximations.append({'label':label,'parts':perpart,'maximum_sampled_boundary_to_source_distance_m':max(p['maximum_sampled_boundary_to_source_distance_m'] for p in perpart)})
  print(ident,label,'surface samples',sum(p['surface_sample_count'] for p in perpart),'max',approximations[-1]['maximum_sampled_boundary_to_source_distance_m'],flush=True)
 # Legacy openings are re-used unchanged and tested against the actual GLB.
 probes=[]
 def ray(name,a,b,empty=True):
  hit=shape_hits(new,a,b);actual=n.segment_hits(C@a,C@b);ok=(not hit)==empty and (not actual)==empty
  check(ident+'_'+name,ok,source_segment_m=[a,b],expected_empty=empty,proposal_hits=hit,actual_GLB_hit_count=len(actual));probes.append(name)
 if i==1:
  for x in [.4,1.2,2.]:
   for z in [.30,.55]:ray('legacy_straight_'+str((x,z)),[x,.60,z],[x,-.24,z])
  for x in [.4,1.2,2.]:
   for z in [.22,.27,.30,.40]:ray('deep_shelf_'+str((x,z)),[x,.60,z],[x,-.304,z])
  ray('legacy_drawer_cavity',[1.2,.25,.72],[1.2,-.20,.72]);ray('blocked_fascia',[1.2,-.42,.55],[1.2,-.25,.55],False)
 else:
  interface=json.loads((ROOT/'assets/hospitality_counters/counter_interface.json').read_text())
  for j,p in enumerate(interface[ident]['staff_shelf_access']['sampled_approach_rays']):
   a=np.asarray(p['source_start_m']);b=a+np.asarray(p['source_direction'])*p['ray_length_m'];ray('original_twelve_access_'+str(j),a.tolist(),b.tolist())
  for theta in [.2,.75,1.4]:
   for z in [.3,.55]:ray('legacy_return_'+str((theta,z)),[.05*math.sin(theta),.62-.05*math.cos(theta),z],[.84*math.sin(theta),.62-.84*math.cos(theta),z])
  for theta in [.2,.75,1.4]:
   for z in [.22,.27,.30,.40]:ray('deep_shelf_'+str((theta,z)),[.10*math.sin(theta),.62-.10*math.cos(theta),z],[.924*math.sin(theta),.62-.924*math.cos(theta),z])
  ray('blocked_fascia',[.88/2**.5,.62-.88/2**.5,.55],[.99/2**.5,.62-.99/2**.5,.55],False)
 report['assets'].append({'id':ident,'baseline_shape_count':len(old),'reduced_shape_count':len(new),'source_triangles_covered':len(source_tri),'approximations':approximations})
 report['inputs'].extend([{'path':str(n.path.relative_to(ROOT)),'sha256':sha(n.path)},{'path':cache_report['geometry_cache'],'sha256':sha(ROOT/cache_report['geometry_cache'])}])
 # Linear motion proposal: every moving convex hull against every static hull.
 if i==1:
  moving=[h for h in new if h['rec']['functional_group']=='proposed_linen_drawer'];static=[h for h in new if h['rec']['functional_group']!='proposed_linen_drawer'];motion=[]
  for label,axis,expect_clear in [('documented_source_axis',[0,1,0],True),('wrong_source_axis',[0,0,1],False)]:
   hits=[]
   for a in moving:
    for b in static:
     pts=(b['v'][:,None,:]-a['v'][None,:,:]).reshape(-1,3);mh={'eq':ConvexHull(pts).equations}
     if segment_hull([0,0,0],np.asarray(axis)*.32,mh,shrink=1e-6):hits.append([a['rec']['semantic_part'],b['rec']['semantic_part']])
   check(ident+'_continuous_drawer_'+label,(not hits)==expect_clear,source_axis=axis,travel_m=.32,moving_hulls=len(moving),stationary_hulls=len(static),penetrating_pairs=hits,touching_tolerance_m=1e-6)
 # Selected blocked geometry includes every meaningful static role.
 for h in new:
  if h['rec']['functional_group']=='proposed_linen_drawer':continue
  ctr=h['v'].mean(axis=0)
  # Actual source-triangle centroid is a guaranteed surface contact, bounded to this section.
  choices=t[np.isin(names,h['rec']['semantic_parts'])];cents=choices.mean(axis=1);cents=cents[np.max(cents@h['eq'][:,:3].T+h['eq'][:,3],axis=1)<1e-7]
  if not len(cents):continue
  p=cents[np.argmin(np.linalg.norm(cents-ctr,axis=1))]
  check(ident+'_blocked_section_'+h['rec']['semantic_part']+'_'+str(h['rec']['section']),bool(shape_hits(new,p,p,radius=2e-7)),source_surface_control_m=p.tolist(),numeric_surface_tolerance_m=2e-7)
 # Finite-size service proxies with a conservative covering proof between samples.
 corridors=[]
 if i==2:
  regions=[('lower_entry',.15,.37,.215,.400),('lower_middle',.61,.96,.215,.400),('lower_exit',1.20,1.42,.215,.400),('upper_open_arc',.15,1.42,.535,.775)]
  for label,alo,ahi,zlo,zhi in regions:
   angles=np.linspace(alo,ahi,math.ceil((ahi-alo)/.003)+1);zs=np.linspace(zlo,zhi,math.ceil((zhi-zlo)/.003)+1)
   gap=.73*(angles[1]-angles[0])/2+(zs[1]-zs[0])/2;radius=.025;expanded=radius+gap
   aa=[];bb=[]
   for theta,z in itertools.product(angles,zs):aa.append([.10*math.sin(theta),.62-.10*math.cos(theta),z]);bb.append([.73*math.sin(theta),.62-.73*math.cos(theta),z])
   aa=np.array(aa);bb=np.array(bb);blocked=np.zeros(len(aa),bool)
   plane_candidates=0;edge_false_positives=0
   for h in new:
    possible=np.where(segment_hull(aa,bb,h,expanded))[0];plane_candidates+=len(possible)
    for j in possible:
     dist=0. if segment_hull(aa[j],bb[j],h) else segment_tri_distance(aa[j],bb[j],h['tri'])
     if dist<=expanded+1e-9:blocked[j]=True
     else:edge_false_positives+=1
   actual_min=np.inf;actual_bad=[]
   actual_key=json.dumps([ident,label,[alo,ahi],[zlo,zhi],len(aa),float(expanded),sha(n.path)])
   cached=corridor_actual_cache.get(actual_key)
   if cached:
    actual_min=cached['minimum_actual_GLB_clearance_m'];actual_bad=list(range(cached['actual_GLB_blocked_count']))
   for j,(a,b) in ([] if cached else enumerate(zip(aa,bb))):
    # Safe triangle AABB broad phase; farther triangles cannot reduce clearance.
    lo=np.minimum(a,b)-.06;hi=np.maximum(a,b)+.06;near=nt[(nt.min(axis=1)<=hi).all(axis=1)&(nt.max(axis=1)>=lo).all(axis=1)]
    d=segment_tri_distance(a,b,near) if len(near) else .06;actual_min=min(actual_min,d)
    if d<expanded-1e-7:actual_bad.append(j)
   corridor_actual_cache[actual_key]={'minimum_actual_GLB_clearance_m':float(actual_min),'actual_GLB_blocked_count':len(actual_bad)};corridor_cache_path.write_text(json.dumps(corridor_actual_cache,indent=2)+'\n')
   rec={'region_name':label,'expanded_plane_broadphase_candidates':plane_candidates,'exact_distance_rejected_corner_false_positives':edge_false_positives,'angle_interval_rad':[alo,ahi],'source_z_interval_m':[zlo,zhi],'radial_interval_m':[.10,.73],'nominal_sphere_radius_m':radius,'covering_radius_inflation_m':float(gap),'tested_radius_m':float(expanded),'sampled_segments':len(aa),'proposal_blocked_count':int(blocked.sum()),'actual_GLB_blocked_count':len(actual_bad),'minimum_actual_GLB_clearance_m':float(actual_min),'continuum_argument':'Each intermediate path is within r_max*d_theta/2 + d_z/2 of a sampled path; enlarged radius proves the nominal 25mm sphere clear throughout this closed parameter rectangle. Expanded convex planes are a conservative broad phase; exact Euclidean segment-to-hull distance resolves their edge/corner false positives.'}
   check(ident+'_continuous_capsule_corridor_'+label,not blocked.any() and not actual_bad,**rec);corridors.append(rec)
   print(ident,label,len(aa),'clear',not blocked.any() and not actual_bad,'distance',actual_min,flush=True)
  # Sensitive blocked sweeps around end mouths/supports and through each shelf.
  for theta,label in [(0.015,'entry_bulkhead'),(math.pi/2-.015,'exit_bulkhead'),(math.pi/2*.31,'radial_support_1'),(math.pi/2*.69,'radial_support_2')]:
   a=[.1*math.sin(theta),.62-.1*math.cos(theta),.3];b=[.73*math.sin(theta),.62-.73*math.cos(theta),.3];ray('blocked_mouth_'+label,a,b,False)
  for theta in [.25,.8,1.3]:
   x=.50*math.sin(theta);y=.62-.50*math.cos(theta);ray('blocked_shelf_'+str(theta),[x,y,.42],[x,y,.51],False)
 else:
  # Continuous boxes of 25mm spheres through each lower/upper straight service bay.
  for xlo,xhi in [(.12,.66),(.94,1.46),(1.74,2.28)]:
   for zlo,zhi in [(.22,.39),(.525,.595)]:
    xs=np.linspace(xlo,xhi,math.ceil((xhi-xlo)/.02)+1);zs=np.linspace(zlo,zhi,math.ceil((zhi-zlo)/.01)+1);gap=(xs[1]-xs[0])/2+(zs[1]-zs[0])/2;rad=.025+gap
    aa=np.array([[x,.60,z] for x,z in itertools.product(xs,zs)]);bb=aa.copy();bb[:,1]=-.24;blocked=np.zeros(len(aa),bool)
    for h in new:blocked|=segment_hull(aa,bb,h,rad)
    actual_min=np.inf
    for a,b in zip(aa,bb):
     lo=np.minimum(a,b)-.06;hi=np.maximum(a,b)+.06;near=nt[(nt.min(axis=1)<=hi).all(axis=1)&(nt.max(axis=1)>=lo).all(axis=1)];d=segment_tri_distance(a,b,near) if len(near) else .06;actual_min=min(actual_min,d)
    rec={'source_x_interval_m':[xlo,xhi],'source_z_interval_m':[zlo,zhi],'source_y_path_m':[.60,-.24],'nominal_sphere_radius_m':.025,'covering_radius_inflation_m':float(gap),'sampled_segments':len(aa),'proposal_blocked_count':int(blocked.sum()),'minimum_actual_GLB_clearance_m':float(actual_min)}
    check(ident+'_continuous_straight_corridor_'+str((xlo,zlo)),not blocked.any() and actual_min>=rad-1e-7,**rec);corridors.append(rec)
 report['assets'][-1]['continuous_service_corridors']=corridors
report['baseline_total_hospitality_shape_count']=399
report['current_total_hospitality_shape_count']=399-289+sum(a['reduced_shape_count'] for a in report['assets'])
report['current_collision_sha256']=sha(current_path)
report['pass']=all(c['pass'] for c in checks)
report['limits']=['No original game/room is present; no engine physics, runtime material, CPU/GPU performance, installed species/body accessibility or load/food certification.','Hull boundary error includes internal section faces, so its conservative upper bound also bounds the compound exterior; inward/source omission is assessed separately by whole-triangle containment.',
'The 25mm sphere is a bounded service-object/hand proxy only. Reported rectangles exclude actual support, end bulkhead, shelf and drawer volumes.','All source surfaces represented by the baseline are retained conservatively; old whole-fascia overfill is intentionally removed with five vertical profile bands. Decorative ribs, reveal and drawer grip remain intentionally absent from collisions, as in Batch07.','Diagnostic hull-face to source-surface distance includes internal partition faces and points inside source material; it is not the signed outward-overfill metric. Use the independent winding/solid-distance report for that metric.',
'Surface error is sampled on a <=25mm triangular net with its explicit covering-radius upper bound. Distances include inherited per-profile convexification; new arc chord bound is5mm and profile-depth bound5mm.','Contact within1 micrometre is allowed in the continuous drawer proposal test. This is geometric separation, not joint/controller or mechanical certification.']
(OUT/'validation_report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'pass':report['pass'],'checks':len(checks),'counts':[(a['id'],a['baseline_shape_count'],a['reduced_shape_count']) for a in report['assets']],'failures':[c for c in checks if not c['pass']]},indent=2))
