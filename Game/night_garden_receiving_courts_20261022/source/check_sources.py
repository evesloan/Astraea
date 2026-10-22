import json,hashlib
from pathlib import Path
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
P=Path(__file__).resolve().parents[1];G=P.parent;R=G.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
b=json.loads((P/'evidence/BUILD_R003.json').read_text());pre=json.loads((P/'evidence/PREREQUISITES.json').read_text());checks=[]
def check(ok,label):
 checks.append({'pass':bool(ok),'label':label})
 if not ok:print('FAILED',label)
for path,digest in pre['source_pins'].items():check(sha(R/path)==digest,'Immutable prerequisite '+path)
check(sha(R/b['native'])==b['native_sha256'],'Native successor bytes')
check(sha(G/b['runtime'])==b['runtime_sha256'],'Runtime successor bytes')
check(len(pre['neighbor_bounds'])==36,'36 existing neighbors included in context contract')
check(min(x['min'][0]for x in pre['neighbor_bounds'])>69.04,'Existing neighbor western bound')
check(not pre['retained_context_mesh_intersections'],'No relevant Group7 bounds in new court band')
regions=json.loads((G/'data/generated/structural_meshes.json').read_text())['regions']+json.loads((G/'data/architecture/CENTRAL_RESIDENTIAL_STREETS.json').read_text())['regions']
old=unary_union([Polygon(t)for a in regions if abs(a['floor_y']-84)<.01 for t in a['triangles']]);new=unary_union([Polygon(t)for t in pre['base_triangles_xz']])
check(new.intersection(old).area<1e-6,'No duplicate protected D13 floor area')
check(abs(pre['existing_base_area_preserved_m2']-151.884)<.001,'Existing window terrace preserved')
for y in [93,97.5]:
 old=unary_union([Polygon(t)for a in regions if abs(a['floor_y']-y)<.01 for t in a['triangles']])
 for sign in [-1,1]:
  zz=sorted([sign*35,sign*90.3]);check(box(55,zz[0],57.2,zz[1]).intersection(old).area<1e-6,'Missing-only gallery '+str(y)+' / '+str(sign))
check(all(x['bounds'][0][1]>=83.75 and x['bounds'][1][1]<=101.5 for x in b['objects']),'All new solids below protected D17')
check(all(x['bounds'][1][0]<=68.751 for x in b['objects'] if 'Bridge'not in x['name']),'Court geometry clear of installed room envelope')
check(b['new_ids']==0 and b['capacity_change']==0 and b['protected_slab_cuts']==0,'No IDs capacity or protected slab cuts')
check(len(b['lights'])==14,'14 fixture-bound sources; existing budget remains authoritative')
check(sum('Canopy' in x['name']for x in b['objects'])>0,'Native original canopy assembly retained')
e=json.loads((P/'evidence/ENTRANCES.json').read_text())
check(sha(R/e['source_native'])==e['source_native_sha256'],'Original avenue native preserved')
check(sha(R/e['native'])==e['native_sha256'],'Bounded entrance native bytes')
check(sha(G/e['runtime'])==e['runtime_sha256'],'Bounded entrance runtime bytes')
check(e['unchanged_source_meshes']==244 and len(e['changed_source_meshes'])==4 and e['floor_cuts']==0 and e['hull_cuts']==0,'Four public façade parts only; 244 source meshes and all floors preserved')
failures=sum(not x['pass']for x in checks)
(P/'evidence/SOURCE_CHECK.json').write_text(json.dumps({'checks':checks,'failures':failures,'visual_accepted':False},indent=2)+'\n')
print('SOURCE_CHECKS',len(checks),'failures',failures)
raise SystemExit(bool(failures))
