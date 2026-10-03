"""Publish the independently reviewed optional body subset without changing asset rows."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
rp=R/'qa/batch16/independent_actor_proxy_final_receipt.json';review=json.loads(rp.read_text());assert review['passed']
side=R/'assets/auditorium_use/actor_proxies/body_collision_subset.json';assert sha(side)==review['new_optional_sidecar']['sha256']
registry={'schema':'astraea_optional_body_proxy_registry_v1','status':'Optional explicit body-only candidates; no installation or engine acceptance','policy':'The normalized catalogue index and detailed collision references remain unchanged. Opt into these subsets only for a suitable body role; retain detailed geometry and physical markers for fine mechanism/service/interaction targets. Do not use them as general-purpose precision contact replacements.','sidecar':{'path':str(side.relative_to(R)),'sha256':sha(side)},'independent_addendum':{'path':str(rp.relative_to(R)),'sha256':sha(rp)},'assets':review['assets'],'game_adoptions':0}
p=R/'standards/body_proxy_candidates.json';p.write_text(json.dumps(registry,indent=2)+'\n')
for rel in ['catalogue_manifest.json','batches/batch16/manifest.json']:
 p=R/rel;j=json.loads(p.read_text());j['optional_body_proxy_registry']={'path':'standards/body_proxy_candidates.json','sha256':sha(R/'standards/body_proxy_candidates.json'),'scope':'Explicit coarse body-only selection; precise/detailed mechanism and interaction references remain available'};add=str(rp.relative_to(R))
 if add not in j.setdefault('readiness_addenda',[]):j['readiness_addenda'].append(add)
 p.write_text(json.dumps(j,indent=2)+'\n')
print('Optional body registry published; normalized asset rows untouched')
