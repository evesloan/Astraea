"""Actual reused fixture bounds, paired surface/normal mounts, and finite intrusion screen."""
from pathlib import Path
import sys,json,hashlib,itertools,numpy as np
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch11'
sys.path.insert(0,str(ROOT/'qa/batch07'));from independent_geometry import Native,C
sys.path.insert(0,str(ROOT/'qa/batch08'));from independent_collision_geometry import inside_mesh,nearest_distances
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
bind=lambda p:{'path':str(p.relative_to(ROOT)),'sha256':sha(p)}
def readcache(ident):
 p=OUT/('independent_source_'+ident+'.json');r=json.loads(p.read_text());assert sha(ROOT/r['path'])==r['sha256'];g=np.load(ROOT/r['geometry_cache']);return r,g['triangles'],g['object_names']
def checknormal(p,t,n):
 # All near-face centroid projection normals are candidate physical normals; use exact triangle distances.
 ds=np.asarray([nearest_distances([p],x[None])[0]for x in t]);v=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);v/=np.maximum(np.linalg.norm(v,axis=1),1e-30)[:,None];near=ds<=.0002
 return {'distance_m':float(ds.min()),'normal_cosine':float(np.max(v[near]@n)) if near.any()else None,'pass':bool(near.any() and np.max(v[near]@n)>.999)}
configs=[]
gp=ROOT/'assets/landing_guest/qa_context_placements.json';g=json.loads(gp.read_text())['AST-LND-001']['fixture'];configs.append(('AST-LND-001',g['catalogue_id'],ROOT/g['path_from_catalogue_root'],np.asarray(g['source_local_transform_4x4']),g['mount_witnesses'],gp))
sp=ROOT/'assets/landing_service/interface_api.json';s=json.loads(sp.read_text())['assets']['AST-LND-003']['fixture_context'];w=[{'fixture_part':'fixture_mount_'+str(i+1)+'_ceiling_plate','fixture_local_source_m':x['fixture_local_point_m'],'fixture_normal_source':s['fixture_top_normal_source'],'receiver_part':x['receiver_object'],'receiver_source_m':x['receiver_source_point_m'],'receiver_normal_source':s['receiver_surface_normal_source']}for i,x in enumerate(s['paired_mount_witnesses'])];configs.append(('AST-LND-003',s['asset_id'],(sp.parent/s['existing_export']).resolve(),np.asarray(s['matrix_source_local']),w,sp))
rows=[]
for comp,fid,fp,T,witnesses,meta in configs:
 cr,ct,cn=readcache(comp);fr,ft,fn=readcache(fid);ng=Native(fp);native_local=ng.tris@C;verts=native_local.reshape(-1,3);moved=verts@T[:3,:3].T+T[:3,3];lo=moved.min(axis=0);hi=moved.max(axis=0);target_lo=np.asarray(cr['bounds_min_m']);target_hi=np.asarray(cr['bounds_max_m']);w=[]
 for x in witnesses:
  p=np.asarray(x['fixture_local_source_m']);q=np.asarray(x['receiver_source_m']);world=T[:3,:3]@p+T[:3,3];nf=np.linalg.inv(T[:3,:3]).T@x['fixture_normal_source'];nr=np.asarray(x['receiver_normal_source']);fst=ft[fn==x['fixture_part']];rst=ct[cn==x['receiver_part']];fs=checknormal(p,fst,x['fixture_normal_source']);rs=checknormal(q,rst,nr)
  w.append({**x,'actual_transformed_fixture_point_source_m':world.tolist(),'paired_point_gap_m':float(np.linalg.norm(world-q)),'opposing_normal_cosine':float(nf@nr),'fixture_actual_surface':fs,'receiver_actual_surface':rs,'pass':np.linalg.norm(world-q)<.0002 and nf@nr<-.999 and fs['pass'] and rs['pass']})
 samples=np.unique(np.round(np.concatenate([native_local.reshape(-1,3),native_local.mean(axis=1),(native_local[:,0]+native_local[:,1])/2,(native_local[:,1]+native_local[:,2])/2,(native_local[:,2]+native_local[:,0])/2]),9),axis=0)@T[:3,:3].T+T[:3,3]
 intrusions=[]
 for part in np.unique(cn):
  t=ct[cn==part];a=t.reshape(-1,3).min(axis=0);b=t.reshape(-1,3).max(axis=0);candidate=samples[((samples>a+.0002)&(samples<b-.0002)).all(axis=1)]
  if not len(candidate):continue
  inside=inside_mesh(candidate,t);pts=candidate[inside]
  if len(pts):
   ds=nearest_distances(pts,t);pts=pts[ds>.0002];ds=ds[ds>.0002]
   if len(pts):intrusions.append({'component_part':str(part),'sample_count':len(pts),'max_sample_inside_depth_m':float(ds.max()),'example_source_m':pts[int(np.argmax(ds))].tolist()})
 row={'component':comp,'reused_fixture':fid,'bindings':{'component_source':bind(ROOT/cr['path']),'fixture_source':bind(ROOT/fr['path']),'fixture_export':bind(fp),'placement_metadata':bind(meta)},'matrix_source_local':T.tolist(),'actual_native_fixture_source_bounds_m':{'min':lo.tolist(),'max':hi.tolist()},'within_component_source_envelope':bool(np.all(lo>=target_lo-1e-6) and np.all(hi<=target_hi+1e-6)),'paired_mount_witnesses':w,'fixture_surface_sample_count':len(samples),'finite_fixture_surface_intrusions_into_component':intrusions,'counted_as_new_design':False,'copied_into_production':False,'pass':all(x['pass']for x in w) and not intrusions and bool(np.all(lo>=target_lo-1e-6) and np.all(hi<=target_hi+1e-6))};rows.append(row);print(comp,json.dumps({k:row[k]for k in ['pass','actual_native_fixture_source_bounds_m','within_component_source_envelope','finite_fixture_surface_intrusions_into_component']}))
r={'passed':all(x['pass']for x in rows),'executed_script_sha256':sha(Path(__file__)),'assets':rows,'limits':'Actual finite triangle-surface/normal mount witnesses and finite fixture surface intrusion samples. This is not structural load, continuous mechanical sweep, wiring, illumination, headroom, host room or actor/cart acceptance.'};(OUT/'independent_fixture_review.json').write_text(json.dumps(r,indent=2)+'\n')
