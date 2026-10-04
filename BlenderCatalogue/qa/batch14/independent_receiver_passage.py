"""Complete bounded capsule passage through actual receiver, independent of towel mechanics."""
from pathlib import Path
import sys,json,hashlib,numpy as np
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch14';sys.path.insert(0,str(OUT));from independent_collision_adapters import expand
from independent_capsule_geometry import segment_triangle_distance
sys.path.insert(0,str(ROOT/'qa/batch07'));from independent_geometry import Native,C
from independent_collision_geometry import inside_mesh
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();bind=lambda p:{'path':str(p.relative_to(ROOT)),'sha256':sha(p)}
mp=ROOT/'assets/aquatic_towel_use/AST-AQU-008.manifest.json';m=json.loads(mp.read_text());sp=mp.parent/m['source'];gp=mp.parent/m['export'];cp=mp.parent/'AST-AQU-008.collision_proposal.json';rp=OUT/'independent_source_AST-AQU-008.json';s=json.loads(rp.read_text());assert sha(sp)==s['sha256'];a=np.load(ROOT/s['geometry_cache']);tri=a['triangles'];labels=a['object_names'];n=Native(gp);nt=n.tris@C;col=json.loads(cp.read_text());hulls=[h for r in col['shapes']for h in expand(r)]
route=np.array([[0,-.35,.96],[0,-.20,.97],[0,-.03,.825],[0,.125,.635],[0,.16,.47],[0,.16,.30]]);radius=.025;rows=[]
for p,q in zip(route,route[1:]):
 ds=segment_triangle_distance(p,q,tri);dn=segment_triangle_distance(p,q,nt);dc=min(0. if h.segment(p,q)is not None else segment_triangle_distance(p,q,h.tris)for h in hulls);inside=[str(part)for part in np.unique(labels)if inside_mesh([p,q],tri[labels==part]).any()]
 rows.append({'segment_source_m':[p.tolist(),q.tolist()],'capsule_radius_m':radius,'minimum_source_surface_distance_m':ds,'minimum_native_surface_distance_m':dn,'minimum_collision_surface_distance_m':dc,'endpoints_inside_named_parts':inside,'pass':min(ds,dn,dc)>=radius-1e-6 and not inside})
negative=segment_triangle_distance([0,-.19,.60],[0,-.19,.90],tri)<radius
r={'passed':all(x['pass']for x in rows)and negative,'bindings':{k:bind(p)for k,p in [('source',sp),('export',gp),('manifest',mp),('collision',cp),('source_audit',rp)]},'route_source_m':route.tolist(),'capsule_radius_m':radius,'segments':rows,'obstructed_floor_negative_control_detected':negative,'method':'Minimum distance between every complete finite segment and every source/native triangle, using exact intersection, endpoint-to-face and segment-to-edge distances. Conservative polygon/cylinder collision surfaces are checked separately. The union of radius25mm capsules is a complete bounded geometric passage, not finite point or pose sampling.','limits':['A50mm-diameter geometric passage does not certify compressible towels, hands, species, cleaning or gameplay.','The route ends inside the closed bin. With the bin removed, containment is deliberately unavailable.','Endpoint-in-solid checks reject a segment that starts wholly inside a named solid.'],'executed_script_sha256':sha(Path(__file__))}
(OUT/'independent_receiver_passage.json').write_text(json.dumps(r,indent=2)+'\n');print('PASSAGE',r['passed'],[(x['minimum_source_surface_distance_m'],x['minimum_collision_surface_distance_m'])for x in rows],flush=True)
