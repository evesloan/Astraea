"""Actual full-height source-only Supreme rest and care approach sweeps."""
import pathlib,json,sys,hashlib
R=pathlib.Path(__file__).resolve().parent;sys.path.insert(0,str(R))
from glb_tools import read_glb,projected_grid,route_check
from premium_frame import PremiumFrame
O=R/'sections/787_supreme';c=json.loads((O/'SECTION_CONTRACT.json').read_text());p=O/'787_supreme.glb';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert sha(p)==c['export_sha256'];f=PremiumFrame(c['reservation']['proposed_floor_boundary']);_,nodes=read_glb(p);polys,grid=projected_grid(nodes,102,2.25)
paths=[('habitat_spine_cart',[(4,9.2),(4,10.6),(7.7,10.6),(7.7,14.65),(11,14.65),(11,21.5),(10.4,21.5),(10.4,28.2)],.82),('quiet_rest_body',[(10.4,28.2),(7.3,28.2)],.38),('aquatic_rest_body',[(10.4,28.2),(15,28.2)],.38),('quiet_care_body',[(10.4,21.5),(2.7,21.5),(2.7,27.5)],.38),('aquatic_care_body',[(10.4,21.5),(19.7,21.5),(19.7,27.5)],.38)]
results=[]
for name,pts,radius in paths:
 world=[f.world(u,v) for u,v in pts];res=route_check(polys,grid,[(q[0],q[2]) for q in world],radius);res.update(name=name,world_xyz=world,height_m=2.25);results.append(res)
data={'status':'PASS' if all(x['passed'] for x in results) else 'FAIL','native_sha256':c['native_sha256'],'export_sha256':sha(p),'routes':results,'scope':'Actual exported triangles; proposed Root receiver omitted. No body/species/accessibility/runtime certification.'};out=O/'HABITAT_APPROACH_VERIFICATION.json';out.write_text(json.dumps(data,indent=2));print(data['status'],[(x['name'],x['passed'],x['min_actual_source_surface_distance_m']) for x in results]);assert data['status']=='PASS'
c['additional_source_files'][out.relative_to(R).as_posix()]=sha(out);c['additional_source_files'][pathlib.Path(__file__).name]=sha(pathlib.Path(__file__));(O/'SECTION_CONTRACT.json').write_text(json.dumps(c,indent=2))
