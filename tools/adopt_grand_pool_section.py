"""Adopt a pinned source section without replacing retained asset files.
Default is read-only preflight; --apply writes only the explicit candidate paths.
Independent remote retention is verified by the coordinating parent before apply.
"""
from pathlib import Path
import hashlib,json,sys,shutil
ROOT=Path(__file__).resolve().parents[1]
SOURCE=Path('/workspace/shared/astraea-catalogue-continuation-20261002/assets/grand_pool_orchard_section')
RETAINED_SOURCE_COMMIT='c333b25c21131f811902438e16712c01771cc611'
PINS={
 'exports/AST-AQU-016.glb':'95a72a20bd0ed653bb10622ff025b1003386020063587828b29efe5e8e40a481',
 'exports/AST-CIR-005_forward_pool_market.glb':'538f8c6d1a3a075b48cdd63a8cb375c83b07f8100987e193b2efbfd39d134667',
 'exports/AST-STF-009_pool_market.glb':'5e1995b9e0114e8a4f28d9cd5d9c00efbb44ff2fb504d8a965eba613b0e7467a',
 'source/connected_contract.json':'7173bdd7e5213059dcc48b74d596b2589ab805dea5d839ce1e8dda6044b458dd',
 'DELIVERY_HASHES.json':'31de4cd03eae0707338532f2126d8b532ef56487d53d1ff5b0a0a2cdcfe7cf6f'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def canonical(v):return json.dumps(v,sort_keys=True,separators=(',',':'))
for name,digest in PINS.items():assert sha(SOURCE/name)==digest,name
receipt=json.loads((SOURCE/'DELIVERY_HASHES.json').read_text())
for name,digest in receipt['files'].items():assert sha(SOURCE/name)==digest,name
for name in ['source_export_verification.json','source_contact_graph.json','plan_route_verification.json','lift_source_sweeps.json']:
 assert json.loads((SOURCE/'qa'/name).read_text())['pass'],name
layout_path=ROOT/'data/spatial_layout.json';compiled_path=ROOT/'data/generated/structural_meshes.json'
assert sha(layout_path)=='f913b8a7fd7100762f7477bdb37400e003d45a2098824b7d2aaf95c98f0c5f52','Unexpected layout changes'
assert sha(compiled_path)=='29b063c3d039e8a183e057e0a4e2673842fc1d6064ab2f8e0bbd54dc1130bf89','Unexpected compiled-floor changes'
layout=json.loads(layout_path.read_text());old=json.loads(compiled_path.read_text());source=json.loads((SOURCE/'source/connected_contract.json').read_text())
assert len(old['regions'])==250 and len(source['floor_regions'])==8
priority=min(row.get('priority',0) for row in layout['regions'])-1
ids={row['id'] for row in layout['regions']};added=[]
for floor in source['floor_regions']:
 assert floor['id'] not in ids;ids.add(floor['id'])
 row={k:floor[k] for k in ['id','deck','offset_y','thickness','boundary','holes','material_role']}
 row.update(authoring_owner='grand_pool_orchard_section',priority=priority,render_cell_m=16,status='Connected pool-market candidate; runtime and final programme acceptance pending')
 added.append(row)
core_path=ROOT/'data/architecture/FORWARD_PUBLIC_CORE.json';core=json.loads(core_path.read_text())
assert core['enclosure_file']=='AST-CIR-005_forward_core.glb' and core['lateral_portal_decks']==['D01','D02']
new_models=[ROOT/'assets/models'/Path(name).name for name in PINS if name.startswith('exports/')]
contract_path=ROOT/'data/architecture/GRAND_POOL_SECTION_RUNTIME.json'
for path in new_models+[contract_path]:assert not path.exists(),f'Preserve existing candidate: {path}'
pre={'count':250,'source_sha256':sha(layout_path),'compiled_sha256':sha(compiled_path),'record_sha256':{r['id']:hashlib.sha256(canonical(r).encode()).hexdigest() for r in old['regions']}}
report={'retained_catalogue_commit':RETAINED_SOURCE_COMMIT,'source_pins':PINS,'adopted_priority':priority,'prior_compiled_count':250,'added_floor_ids':[r['id'] for r in added],'prior_layout_sha256':sha(layout_path),'prior_core_contract_sha256':sha(core_path),'scope':'Pinned candidate installation; old floor equality checked after compilation. Source QA is not runtime acceptance.','runtime_acceptance':'Pending'}
if '--apply' not in sys.argv:
 print(json.dumps(report,indent=2));raise SystemExit(0)
for name in PINS:
 if name.startswith('exports/'):shutil.copy2(SOURCE/name,ROOT/'assets/models'/Path(name).name)
shutil.copy2(SOURCE/'source/connected_contract.json',contract_path)
layout['regions'].extend(added);layout_path.write_text(json.dumps(layout,indent=2)+'\n')
core['enclosure_file']='AST-CIR-005_forward_pool_market.glb';core['lateral_portal_decks']=['D01','D02','D08','D09'];core_path.write_text(json.dumps(core,indent=2)+'\n')
(ROOT/'docs/GRAND_POOL_PRE_ADOPTION_MESHES.json').write_text(json.dumps(pre,indent=2)+'\n')
(ROOT/'docs/GRAND_POOL_ADOPTION.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'candidate_installed':True,'new_models':len(new_models),'new_floor_regions':len(added),'priority':priority,'runtime_acceptance':'Pending'}))
