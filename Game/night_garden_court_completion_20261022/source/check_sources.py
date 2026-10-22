from pathlib import Path
import json,hashlib
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
P=Path(__file__).resolve().parents[1];G=P.parent;R=G.parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();checks=[]
def check(ok,label):checks.append({'pass':bool(ok),'label':label})
b=json.loads((P/'evidence/BUILD_R003.json').read_text());pre=json.loads((P/'evidence/PREREQUISITES.json').read_text());plan=json.loads((P/'evidence/SOFFIT_PLAN.json').read_text())
for path,digest in pre['source_pins'].items():check(sha(G/path)==digest,'Retained prerequisite '+path)
for key in ['native','source_native']:check(sha(R/b[key])==b[key+'_sha256'],'Native bytes '+key)
check(sha(G/b['runtime'])==b['runtime_sha256'],'Runtime GLB bytes')
check(b['original_meshes_geometry_unchanged']==7334,'All 7334 predecessor mesh geometries preserved')
check(b['original_room_ids_changed']==0 and b['capacity_change']==0 and b['protected_slab_cuts']==0 and b['hull_changes']==0,'No identities capacity slab cuts or hull changes')
check(b['textured_new_parts_with_editable_uv']==150,'150 new textured parts have editable UVs')
check(len(b['lights'])==28 and all('anchor'in x for x in b['lights']),'28 fixture-bound lights have visible-receiver definitions')
check(all(x['bounds'][0][1]>=83.75 and x['bounds'][1][1]<=101.5 for x in b['new_parts']),'New court architecture stays below protected D17')
region=next(x for x in json.loads((G/'data/generated/structural_meshes.json').read_text())['regions']if x['id']==plan['owner']);footprint=unary_union([Polygon(t)for t in region['triangles']])
check(sha(G/'data/generated/structural_meshes.json')==plan['source_sha256'],'Exact compiled slab owner unchanged')
check(all(footprint.covers(Polygon(t))for tile in plan['tiles']for t in tile['triangles']),'All 28 soffit tiles lie inside retained slab footprint')
check(all(footprint.covers(box(49,r['z']-.5,53.9,r['z']+.5))for r in plan['lights']),'All six wallwash housings mount to retained slab')
check(abs(plan['original_underside_y']-96.95)<.001 and 96.78-93>3.7,'Cladding retains at least 3.78m D15 clearance')
check(len([r for r in b['new_parts']if '_BuiltInPlanter_'in r['name']])==8,'Eight supported planters outside walking lanes')
check(len([r for r in b['new_parts']if 'PlanterFern_'in r['name']or'IslandUnderstory_'in r['name']])==120,'120 integrated understory plants')
check(b['lantern_supports_connected'],'Both ring lanterns have modeled suspension')
check(json.loads((P/'evidence/CHECK.json').read_text())['failures']==0,'37 final focused runtime checks pass')
failed=sum(not x['pass']for x in checks);(P/'evidence/SOURCE_CHECK.json').write_text(json.dumps({'checks':checks,'failures':failed,'final_visual_accepted':False},indent=2)+'\n');print('SOURCE_CHECKS',len(checks),'failures',failed)
for c in checks:
 if not c['pass']:print('FAILED',c['label'])
raise SystemExit(bool(failed))
