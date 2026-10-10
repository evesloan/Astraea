from pathlib import Path
import json,numpy as np,hashlib
W=Path(__file__).resolve().parent;R=Path('/workspace/shared/Astraea_direct_recovery_20261008_hcozu5z4');P=json.loads((W/'D13_RECEIVING_PLAN.json').read_text());U={'W':W};exec((R/'BlenderCatalogue/assets/group4_tram_connections_20261009/boarding_north_005/glb_source_reader.py').read_text(),U);base=U['read'];U['read']=lambda p:(W/Path(p).name).read_bytes()if (W/Path(p).name).exists()else base(p)
def canonical(t):return tuple(sorted(tuple(np.round(p,5))for p in t))
orig=dict(U['triangles']('AST-RES-TIDAL_lift_fit_r003.glb'));patch=dict(U['triangles']('TidalD13ServiceGuardPatch.glb'));rows=[]
for n in P['named_guard_replacement_map']:
 q=orig[n];lo=q.min(axis=1);hi=q.max(axis=1);affected=np.zeros(len(q),bool)
 for c in P['guard_cut_boxes']:affected|=np.all(hi>=np.array(c['min'])-1e-7,axis=1)&np.all(lo<=np.array(c['max'])+1e-7,axis=1)
 uncut=q[~affected];newset={canonical(t)for t in patch[n]};missing=[canonical(t)for t in uncut if canonical(t)not in newset]
 # Exact float output tolerance1e-4m permits only coordinate quantization, no omitted unaffected triangle.
 for t in uncut:
  v=t.mean(axis=0);idx=np.argmin(np.linalg.norm(patch[n].mean(axis=1)-v,axis=1));x=np.array(sorted(map(tuple,t)));y=np.array(sorted(map(tuple,patch[n][idx])));assert np.max(abs(x-y))<1e-4,(n,t)
 rows.append({'batch':n,'original_triangles':len(q),'patch_triangles':len(patch[n]),'unaffected_original_triangles_screened':len(uncut),'all_unaffected_triangle_point_sets_retained_within_m':.0001,'round5_exact_matches':len(uncut)-len(missing)})
actual=dict(U['triangles']('AST-RES-TIDAL_D13_service_receiving_r001.glb'));assert len(actual)==73;assert all(np.isfinite(t).all()for t in actual.values())
assert set(actual)=={p['name']for p in P['retained_source_parts']+P['additive_parts']}
rec={'status':'PASS','guard_replacement_triangles':rows,'actual_receiving_meshes':len(actual),'actual_receiving_triangles':sum(len(t)for t in actual.values()),'source_originals_unchanged':all(hashlib.sha256((R/p).read_bytes()).hexdigest()==h for p,h in P['source_pins'].items()),'limits':'Bounded actual-source triangle preservation and recipe identities; live door/floor/collision acceptance checked separately.'};assert rec['source_originals_unchanged'];(W/'ACTUAL_EXPORT_CHECK.json').write_text(json.dumps(rec,indent=2)+'\n');print(json.dumps(rec))
