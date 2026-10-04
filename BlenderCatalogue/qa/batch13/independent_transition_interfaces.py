"""Actual transition source/native marker, support, cavity and mating-surface review."""
from pathlib import Path
import sys,json,hashlib,itertools,numpy as np
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch13';BASE=ROOT/'assets/botanical_transition'
sys.path.insert(0,str(ROOT/'qa/batch07'));from independent_geometry import Native,C
sys.path.insert(0,str(ROOT/'qa/batch08'));from independent_collision_geometry import Hull,nearest_distances,inside_mesh,segment_triangles
sys.path.insert(0,str(ROOT/'qa/batch12'));from independent_void_geometry import triangle_box_mask,hull_box_overlap
sys.path.insert(0,str(OUT));from independent_contact_graph import contact_graph,normal_witness
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
bind=lambda p:{'path':str(p.relative_to(ROOT)),'sha256':sha(p)}
mp=BASE/'AST-BOT-010.manifest.json';m=json.loads(mp.read_text());sp=BASE/m['source_blend'];gp=BASE/m['runtime_glb'];rp=OUT/'independent_source_AST-BOT-010.json';s=json.loads(rp.read_text());assert sha(sp)==s['sha256']==m['hashes']['blend_sha256'];assert sha(gp)==m['hashes']['glb_sha256'];so={o['name']:o for o in s['objects']};a=np.load(ROOT/s['geometry_cache']);tri=a['triangles'];labels=a['object_names'];roles=a['material_names'];native=Native(gp);nt=native.tris@C;nodes=native.g.doc['nodes'];ni={n.get('name'):i for i,n in enumerate(nodes)}
markers=[]
for mr in m['markers']:
 p=np.asarray(mr['source_m']);name=mr['name'];i=ni.get(name);world=native.world[i][:3,3]if i is not None else np.zeros(3);target=mr['physical_target'];physical=mr['kind'].startswith('physical')
 r={'name':name,'kind':mr['kind'],'physical_target':target,'source_world_m':np.asarray(so[name]['matrix_world'])[:3,3].tolist(),'native_world_m':world.tolist(),'source_marker_error_m':float(np.linalg.norm(np.asarray(so[name]['matrix_world'])[:3,3]-p)),'native_marker_present':i is not None,'native_marker_error_m':float(np.linalg.norm(world-C@p)),'declared_native_error_m':float(np.linalg.norm(np.asarray(mr['native_glb_m'])-C@p)),'wrong_axis_interpretation_error_m':float(np.linalg.norm(world-p))}
 if physical:
  part=tri[labels==target];assert len(part);role=so[target]['materials'][0];n=np.asarray(mr['physical_normal_source']);sel=native.tris[native.select(role=role)]
  r.update(distance_to_named_source_surface_m=float(nearest_distances([p],part)[0]),distance_to_native_surface_m=native.nearest(C@p,role=role)['distance_m'],source_outward_normal_witness=normal_witness(p,part,n),native_outward_normal_witness=normal_witness(C@p,sel,C@n))
  r['physical_surface_verified']=max(r['distance_to_named_source_surface_m'],r['distance_to_native_surface_m'])<.0002 and r['source_outward_normal_witness']['pass']and r['native_outward_normal_witness']['pass']
 r['pass']=i is not None and max(r['source_marker_error_m'],r['native_marker_error_m'],r['declared_native_error_m'])<1e-6 and r.get('physical_surface_verified',True);markers.append(r)
floor=[o['name']for o in s['objects']if o.get('min_xyz',[0,0,1])[2]<.00002 and o['type']=='MESH'];graph=contact_graph(tri,labels,floor)
cp=BASE/m['collision_file'];col=json.loads(cp.read_text());hulls=[Hull(x['points_source_m'],x)for x in col['solids']]
volumes=[];probes=[]
# Planting volumes contain soil deliberately. Their tests exclude only that stated medium.
boxes=[('lower_soil_structural_cavity',[.010,.160,.110],[.550,.870,.380],True),('upper_soil_structural_cavity',[.690,.160,.370],[1.670,.870,.780],True),('underseat_bay_left',[.275,-.410,.080],[.845,-.090,.320],False),('underseat_bay_right',[.955,-.410,.080],[1.525,-.090,.320],False),('upper_slab_internal_empty_bay',[.840,.230,.110],[1.510,.800,.325],False),('full_seated_above_ribbon',[.001,-.485,.471],[1.799,-.025,1.350],False),('front_approach',[.001,-1.690,0],[1.799,-.490,2.0],False),('standalone_rear_maintenance',[.001,1.080,0],[1.799,1.880,2.0],False)]
for name,lo,hi,exclude_soil in boxes:
 lo=np.array(lo);hi=np.array(hi);vl=lo+.0002;vh=hi-.0002;mask=roles!='ASTRAEA_botanical_soil' if exclude_soil else np.ones(len(tri),bool);nmask=native.materials!='ASTRAEA_botanical_soil'if exclude_soil else np.ones(len(nt),bool);t=tri[mask];nl=labels[mask];ntri=nt[nmask];sm=triangle_box_mask(t,vl,vh);nm=triangle_box_mask(ntri,vl,vh);contains=[]
 for part in np.unique(nl):
  if inside_mesh([(vl+vh)/2],t[nl==part])[0]:contains.append(str(part))
 overlaps=[h.record['name']for h in hulls if hull_box_overlap(h,vl,vh)['overlaps']]
 v={'name':name,'source_box_m':[lo.tolist(),hi.tolist()],'excludes_soil_medium_from_visual_test':exclude_soil,'source_intruding_parts':sorted(set(str(x)for x in nl[sm])),'source_intruding_triangles':int(sm.sum()),'native_intruding_triangles':int(nm.sum()),'midpoint_inside_named_solids':contains,'collision_overlaps':overlaps,'pass':not sm.any()and not nm.any()and not contains and not overlaps};volumes.append(v)
 for ax in range(3):
  others=[a for a in range(3)if a!=ax]
  for u,w in itertools.product([.08,.3,.5,.7,.92],repeat=2):
   p=lo+(hi-lo)*.01;q=hi-(hi-lo)*.01
   for a,f in zip(others,[u,w]):p[a]=q[a]=lo[a]+(hi[a]-lo[a])*f
   vb=bool(segment_triangles(p,q,t));nb=bool(segment_triangles(p,q,ntri));cb=any(h.segment(p,q)is not None for h in hulls);probes.append({'name':name,'segment_source_m':[p.tolist(),q.tolist()],'visual_blocked':vb,'native_blocked':nb,'proposal_blocked':cb,'expected_blocked':False,'pass':not vb and not nb and not cb})
for name,p,q in [('seat',[.5,-.25,.4],[.5,-.25,.49]),('upper_slab',[1.1,.5,.32],[1.1,.5,.38]),('riser',[.54,.5,.65],[.70,.5,.65]),('terminal',[1.66,.5,.65],[1.82,.5,.65]),('rear_retaining',[1.1,.85,.6],[1.1,1.03,.6]),('floor_shoe',[.9,-.1,-.02],[.9,-.1,.02])]:
 vb=bool(segment_triangles(p,q,tri));nb=bool(segment_triangles(p,q,nt));cb=any(h.segment(p,q)is not None for h in hulls);probes.append({'name':name,'segment_source_m':[p,q],'visual_blocked':vb,'native_blocked':nb,'proposal_blocked':cb,'expected_blocked':True,'pass':vb and nb and cb})
wrong=Hull(tri.reshape(-1,3));negative=sum(not x['expected_blocked']and wrong.segment(*x['segment_source_m'])is not None for x in probes)
# Direct native GLB mating-face witnesses: existing end translated -2.4m, new start +0.
prior=Native(ROOT/'assets/botanical_planter/AST-BOT-004.glb');pt=prior.tris@C;pt[:,:,0]-=2.4;seams=[]
for name,p,role in [('front_wall',[.001,.08,.2],'warm_stone'),('rear_wall',[.001,.93,.2],'warm_stone'),('seat',[.001,-.24,.445],'warm_walnut'),('front_coping',[.001,.08,.42],'ivory_enamel'),('rear_coping',[.001,.94,.42],'ivory_enamel'),('soil',[.001,.5,.25],'botanical_soil')]:
 p=np.array(p);q=p.copy();q[0]=-.001;ta=pt[np.array([role in x for x in prior.materials])];tb=nt[np.array([role in x for x in native.materials])];da=float(nearest_distances([q],ta)[0]);db=float(nearest_distances([p],tb)[0]);an=normal_witness(q,ta,[1,0,0]);bn=normal_witness(p,tb,[-1,0,0]);seams.append({'name':name,'prior_end_source_m':q.tolist(),'transition_start_source_m':p.tolist(),'nominal_gap_m':.002,'actual_prior_surface_error_m':da,'actual_new_surface_error_m':db,'opposed_prior_normal':an,'opposed_new_normal':bn,'pass':max(da,db)<.0002 and an['pass']and bn['pass']})
result={'passed':all(x['pass']for x in markers+volumes+probes+seams)and graph['passed']and negative>0,'bindings':{k:bind(p)for k,p in [('source',sp),('export',gp),('manifest',mp),('collision',cp),('source_audit',rp)]},'markers':markers,'contact_graph':graph,'collision_shape_count':len(hulls),'empty_or_medium_filled_volume_checks':volumes,'clear_and_blocked_probes':probes,'actual_native_mating_faces':seams,'whole_asset_hull_negative_controls':negative,'wrong_axis_negative_control_count':sum(x['wrong_axis_interpretation_error_m']>.001 for x in markers),'limits':['Soil-filled cavities are not visually empty. Tests exclude only soil medium and preserve actual retaining/floor geometry.','Standalone rear approach applies before adding the separately measured trailing plant. The final assembled strip must be tested independently.','Exact triangle/box intersection and convex feasibility prove stated inset boxes for these static components; finite rays are supplementary, not continuous actor fit.','All geometric support connectivity and seam witnesses are component-level only. No structural loads, host adoption, plant care or species claims.'],'executed_script_sha256':sha(Path(__file__))}
(OUT/'independent_botanical_transition_interfaces.json').write_text(json.dumps(result,indent=2)+'\n')
print('passed',result['passed'],'markers',len(markers),'failed',[x['name']for x in markers if not x['pass']],'isolated',graph['isolated_parts'],'void failures',[(x['name'],x['source_intruding_parts'],x['collision_overlaps'])for x in volumes if not x['pass']],'probe failures',[x['name']for x in probes if not x['pass']],'seam failures',[x['name']for x in seams if not x['pass']])
