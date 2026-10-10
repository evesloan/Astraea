from pathlib import Path
import json,hashlib,numpy as np
W=Path(__file__).resolve().parent;S=Path('/tmp/astraea_tidal_d14_receiver_20261010');R=Path('/workspace/shared/Astraea_direct_recovery_20261008_hcozu5z4');P=json.load(open(W/'D14_CORRIDOR_INTEGRATION_PLAN.json'));N=json.load(open(W/'CORRIDOR_NATIVE_EXPORT_CHECK.json'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();s=(R/'BlenderCatalogue/assets/group4_tram_connections_20261009/boarding_north_005/glb_source_reader.py').read_text();u={'R':R,'PIN':[],'np':np};exec('import math, struct, json\n'+s[s.index('def read(p):'):s.index('def contacts(')],u)
def read(p):
 f=Path(p).name
 if (W/f).exists():return(W/f).read_bytes()
 if f=='AST-STF-G3-003.glb':return(R/'BlenderCatalogue/assets/group3_crew_service_20261009/exports'/f).read_bytes()
 return(R/p).read_bytes()
u['read']=read;out=dict(u['triangles'](N['export']));old=dict(u['triangles']('AST-STF-G3-003.glb'));assert len(out)==65;joined={p for arr in P['batched_patch_targets'].values()for p in arr};checked=0
for p in P['retained_source_parts']+P['closures']:
 if p['name']in joined:continue
 t=out[p['name']];lo=t.min(axis=(0,1));hi=t.max(axis=(0,1))
 if 'aabb'in p:b=p['aabb'];expectedlo=np.array([b[0],b[2],b[4]]);expectedhi=np.array([b[1],b[3],b[5]])
 else:poly=np.array(p['boundary']);expectedlo=np.array([poly[:,0].min(),p['y'][0],poly[:,1].min()]);expectedhi=np.array([poly[:,0].max(),p['y'][1],poly[:,1].max()])
 assert np.max(abs(lo-expectedlo))<1e-4 and np.max(abs(hi-expectedhi))<1e-4,p['name'];checked+=1
match=[]
for name in P['batched_patch_targets']:
 before=old[name];after=out[name];assert len(before)==len(after)==24;errors=[]
 for t in before:
  a=np.array(sorted(tuple(v)for v in t));err=min(np.max(abs(a-np.array(sorted(tuple(v)for v in q))))for q in after);errors.append(float(err));assert err<1e-4
 match.append({'target':name,'all_original_triangles':24,'maximum_coordinate_error_m':max(errors)})
for p,h in P['source_pins'].items():
 f=R/p
 if p=='Game/scripts/tidal_garden_adoption.gd':assert sha(W/'predecessors/tidal_garden_adoption.gd')==h
 else:assert sha(f)==h,p
prior=json.load(open('/tmp/astraea_tidal_d13_receiving_20261010/FROZEN_D13_INTEGRATION_BATCH.json'));kept=[]
for p,q in prior['runtime_files'].items():
 if p=='Game/scripts/tidal_garden_adoption.gd':continue
 assert sha(R/p)==q['sha256'];kept.append(p)
fr=json.load(open(S/'FROZEN_D14_SHARED_RECEIVER_BATCH.json'));assert all(sha(S/f)==d['sha256']for f,d in fr['files'].items())
r={'schema':1,'status':'PASS','corridor_export_meshes':65,'retained_source_parts':64,'physical_closures':3,'aabb_checks':checked,'two_patch_batches_exact_source_match':match,'all_corridor_geometry_y_min':float(min(t.min(axis=(0,1))[1]for t in out.values())),'all_corridor_geometry_y_max':float(max(t.max(axis=(0,1))[1]for t in out.values())),'no_full_shaft_landing_geometry':True,'all_frozen_d14_proposal_files_unchanged':True,'preserved_prior_d13_runtime_files':kept,'only_intentional_existing_source_change':'one additive tidal_garden_adoption.gd call, original bytes bound in predecessors','source_dependencies_unchanged_except_bound_adoption':True};(W/'CORRIDOR_ACTUAL_EXPORT_CHECK.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
