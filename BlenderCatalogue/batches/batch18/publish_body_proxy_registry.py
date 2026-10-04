"""Publish explicit per-component body-role choices without changing prior registries."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[2]
def load(p):return json.loads((ROOT/p).read_text())
def binding(p):return {'path':p,'sha256':hashlib.sha256((ROOT/p).read_bytes()).hexdigest()}
review='qa/batch18/independent_final_review.json';assert load(review)['passed']
registry={'schema':'astraea_optional_body_proxy_registry_v1','status':'Optional body-role candidates; no installation or runtime cost acceptance','policy':'Use detailed geometry and physical markers for exact surface/mechanism/service/interaction targets. The display compound has a disclosed shallow cosmetic-setback approximation; useful display/storage openings remain open. Other selections retain original solids with explicit small-detail omissions.','assets':[],'game_adoptions':0}
for n in range(1,5):
 aid=f'AST-RTL-{n:03d}';family='retail_display' if n<3 else 'retail_work';precise_path=f'assets/{family}/collision_proposals.json';data=load(precise_path)
 if n<3:
  precise=data['assets'][aid];candidate_path=f'assets/{family}/actor_proxies/body_collision_subset.json';candidate=load(candidate_path)['assets'][aid]
  detailed_count=len(precise['shapes']);count=len(candidate['shapes']);selector=f'/assets/{aid}';derivation='Compound authored convex body geometry with explicitly bounded cosmetic setback fill' if n==1 else 'Original convex solids with ornamental strip omitted'
  limits={'maximum_declared_outward_approximation_m':max(row.get('max_outward_approximation_m',0)for row in candidate['shapes']),'omitted_detail':candidate['omitted_detail'],'useful_voids_must_remain_open':candidate['useful_voids_must_remain_open']}
 else:
  precise=data[aid];candidate_path=precise_path;candidate=precise['optional_body_candidate'];detailed_count=len(precise['precise_reference']);count=len(candidate['retained_shape_names']);selector=f'/{aid}/optional_body_candidate';derivation='Literal selection of original detailed solid profiles';limits={'fine_detail_distance':candidate['fine_detail_distance'],'new_enclosing_hulls':candidate['new_enclosing_hulls']}
 assert 0<count<=detailed_count
 registry['assets'].append({'catalogue_id':aid,'detailed_shape_count':detailed_count,'body_shape_count':count,'derivation':derivation,'candidate_source':binding(candidate_path),'candidate_json_pointer':selector,'precision_reference':binding(precise_path),'independent_review':binding(review),'declared_limits':limits,'engine_adoption':False})
p=ROOT/'batches/batch18/body_proxy_candidates.json';p.write_text(json.dumps(registry,indent=2)+'\n');b=binding(str(p.relative_to(ROOT)))
p=ROOT/'catalogue_manifest.json';j=json.loads(p.read_text());j['additional_optional_body_proxy_registries']=[row for row in j.get('additional_optional_body_proxy_registries',[]) if row['path']!=b['path']]+[b];p.write_text(json.dumps(j,indent=2)+'\n')
p=ROOT/'batches/batch18/manifest.json';j=json.loads(p.read_text());j['optional_body_proxy_registry']=b;p.write_text(json.dumps(j,indent=2)+'\n')
print('Published four explicit retail body-role choices; previous registries preserved')
