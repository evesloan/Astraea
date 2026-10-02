"""Quantify finite collision simplification against actual named closed support meshes."""
from pathlib import Path
import json,sys,hashlib,numpy as np
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch13';BASE=ROOT/'assets/botanical_transition'
sys.path.insert(0,str(ROOT/'qa/batch08'));from independent_collision_geometry import Hull,sample_triangles,inside_mesh,nearest_distances,triangle_uncovered_area
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();rp=OUT/'independent_source_AST-BOT-010.json';s=json.loads(rp.read_text());assert sha(ROOT/s['path'])==s['sha256'];g=np.load(ROOT/s['geometry_cache']);tri=g['triangles'];labels=g['object_names'];part={str(n):tri[labels==n]for n in np.unique(labels)};cp=BASE/'collision_proposals.json';c=json.loads(cp.read_text());hulls=[Hull(x['points_source_m'],x)for x in c['solids']];rows=[];used=set()
for h in hulls:
 name=h.record['name']
 if name.startswith('front_rising_retaining_wall'):covered=['front_rising_retaining_wall']
 elif name.startswith('rear_'):covered=['rear_rising_retaining_wall']
 elif name=='seat_support_plate':covered=['timber_sitting_ribbon_'+str(i)for i in [1,2,3]]
 elif name.startswith('floor_to_seat_support_'):
  num=name.split('_')[-1];covered=['seat_load_bracket_'+num,'floor_contact_bracket_shoe_'+num]
 elif name in part:covered=[name]
 else:raise ValueError('Unclassified purpose '+name)
 used.update(covered);actual=np.concatenate([part[x]for x in covered]);pts,step=sample_triangles(h.tris,.035);inside=np.zeros(len(pts),bool)
 for p in covered:inside|=inside_mesh(pts,part[p])
 ext=pts[~inside];dist=nearest_distances(ext,actual)if len(ext)else np.array([0.]);j=int(dist.argmax());rows.append({'name':name,'covered_parts':covered,'sample_count':len(pts),'max_sample_grid_edge_m':step,'sampled_max_external_inflation_m':float(dist.max()),'worst_sample_source_m':ext[j].tolist()if len(ext)else None})
coverage=[]
for name in sorted(used):
 t=part[name];area=float(np.linalg.norm(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]),axis=1).sum()/2);uncovered=sum(triangle_uncovered_area(x,hulls)for x in t);pts,step=sample_triangles(t,.035);ins=np.any([h.inside(pts)for h in hulls],axis=0);ext=pts[~ins];under=float(nearest_distances(ext,np.concatenate([h.tris for h in hulls])).max())if len(ext)else 0.;coverage.append({'part':name,'actual_source_surface_area_m2':area,'uncovered_by_compound_area_m2':float(uncovered),'continuous_coverage_complete':uncovered<1e-7,'sampled_max_uncovered_surface_distance_m':under,'sample_count':len(pts),'max_sample_grid_edge_m':step,'pass':under<.002})
result={'passed':all(x['pass']for x in coverage),'source':s['path'],'source_sha256':s['sha256'],'collision':str(cp.relative_to(ROOT)),'collision_sha256':sha(cp),'shape_count':len(hulls),'profiles':rows,'continuous_structural_surface_coverage':coverage,'excluded_fine_finish_or_soil_parts':sorted(set(part)-used),'sampled_max_external_inflation_m':max(x['sampled_max_external_inflation_m']for x in rows),'executed_script_sha256':sha(Path(__file__)),'limits':'Thin profile gaps can produce nonzero uncovered surface area; that is disclosed separately, not called complete coverage. Geometric screening allows sampled underreach below2mm for these unadopted proposals; no continuous distance upper bound is established. Hull surfaces use finite barycentric samples with35mm maximum grid edge. External inflation maximum is sampled, not a continuous maximum certificate. Structural source-triangle union coverage uses continuous convex polygon clipping with0.2micrometre tolerance. Soil and fine finish layers are explicitly excluded; the proposal does not promise their contact behavior. Separate cavity/seat/maintenance probes test useful spaces. No engine physics or runtime performance claim.'}
(OUT/'independent_botanical_transition_collision_profile.json').write_text(json.dumps(result,indent=2)+'\n');print('PROFILE',result['passed'],'inflation',result['sampled_max_external_inflation_m'],'uncovered',[(x['part'],x['uncovered_by_compound_area_m2'])for x in coverage if not x['pass']],flush=True)
