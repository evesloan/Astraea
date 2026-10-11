from pathlib import Path
import json,hashlib,numpy as np
from shapely.geometry import Polygon,Point
from shapely.ops import unary_union
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.load(open(W/'RUNTIME_PLAN.json'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();reader=R/'BlenderCatalogue/assets/forward_staff_shaft_interfaces_20261010/source_geometry.py';ns={'__file__':str(reader)};exec(reader.read_text(),ns);T=ns['triangles'];rows=[]
for spec,parts in [(P['structure'],P['parts']),(P['court_candidate_model'],P['gate_revision_parts'])]:
 export={n:t for n,t in T(spec['model_file'])}
 for q in parts:
  v=np.array(q['verts']);t=export[q['name']].reshape(-1,3);error=max(np.max(abs(t.min(0)-v.min(0))),np.max(abs(t.max(0)-v.max(0))));assert error<.00004,q['name'];rows.append({'name':q['name'],'bound_error_m':float(error)})
stair={n:t for n,t in T(P['stair']['model'])};active={n:t for n,t in T(P['structure']['model_file'])};rigid=[]
for n,t in stair.items():
 key='D04SA_Stair__'+n
 if key not in active:continue
 expected=t.reshape(-1,3)+np.array(P['stair']['origin']);actual=active[key].reshape(-1,3);error=max(np.max(abs(expected.min(0)-actual.min(0))),np.max(abs(expected.max(0)-actual.max(0))));assert error<.00004,key;rigid.append({'name':key,'bound_error_m':float(error)})
assert len(rigid)==80,len(rigid)
regions=json.load(open(R/'Game/data/generated/structural_meshes.json'))['regions'];byid={r['id']:r for r in regions};contacts=[]
for x,z,owner in [(-55.4,-449.65,'D03_port_forward_staff_floor_0'),(-53.8,-449.65,'D03_protected_crew_cover'),(-55.4,-446.35,'D03_port_forward_staff_floor_0'),(-53.8,-446.35,'D03_protected_crew_cover'),(-29.3,-447.3,'D03_protected_crew_cover'),(-27.2,-447.3,'D03_protected_crew_cover'),(-29.3,-445.4,'D03_protected_crew_cover'),(-27.2,-445.4,'D03_protected_crew_cover')]:
 r=byid[owner];floor=unary_union([Polygon(t)for t in r['triangles']]);assert floor.covers(Point(x,z));contacts.append({'at':[x,12,z],'owner':owner,'floor_y':r['floor_y'],'thickness':r['thickness']})
for f,h in P['source_pins'].items():assert sha(R/f)==h,f
for record in P['native_export_records']:assert sha(W/record['native'])==record['native_sha256']and sha(W/record['export'])==record['export_sha256']and record['fresh_native_repeat_identical']
(W/'SOURCE_GEOMETRY_CHECK.json').write_text(json.dumps({'status':'PASS','owned_meshes_verified':len(rows),'meshes':rows,'original_rigid_stair_meshes':rigid,'source_floor_contacts':contacts,'protected_source_pins':len(P['source_pins']),'staff_lane_and_lower_stance_new_floor_m2':0,'production_active':False,'primary_load_accepted':False},indent=2)+'\n');print('STAFF_COURT_SOURCE_PASS',len(rows),len(rigid),len(contacts))
