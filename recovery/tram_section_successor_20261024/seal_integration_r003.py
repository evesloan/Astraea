#!/usr/bin/env python3
"""One bounded source review/seal; no engine, main edit, import or publication."""
from pathlib import Path
import hashlib,json,re
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];GAME=ROOT/'Game';OWN=GAME/'tram_section_successor_20261024'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    protected=json.loads(Path('/workspace/astraea-env/receipts/tram-section-4e547c4b-readback.json').read_text())
    assert protected['commit']=='4e547c4b21e16eeb621a3fe5b756618b12eb340b'and protected['independent_remote_readback']
    old=json.loads((HERE/'PACKAGE_MANIFEST.json').read_text())
    for rel,pin in old['files'].items():assert sha(ROOT/rel)==pin['sha256'],rel
    prerequisites={};checks=0
    def pin(path):
        assert path.is_file(),path
        prerequisites['res://'+str(path.relative_to(GAME))]=sha(path)
    def read(path):pin(path);return path.read_text()
    uri='res://scripts/tidal_arrival_finish_integration_20261024/ship.gd';chain=[]
    while uri.startswith('res://'):
        p=GAME/uri[6:];text=read(p);methods=re.findall(r'^func ([^(]+)',text,re.M)
        chain.append({'path':uri,'sha256':sha(p),'methods':methods})
        found=re.match(r'extends "([^"]+)"',text);uri=found.group(1)if found else''
    ancestors=[r for r in chain if '_ready'in r['methods']]
    assert [r['path']for r in ancestors]==['res://scripts/consolidated_construction_20261022/ship.gd','res://scripts/ship.gd'];checks+=1
    ready_source=GAME/'scripts/consolidated_construction_20261022/ship.gd';text=ready_source.read_text()
    ready=text[text.index('func _ready()'):text.index('\nfunc model(')]
    old_call='load("res://scripts/group4_integrated_receiving.gd")'
    assert ready.count(old_call)==2
    target='load("res://tram_section_successor_20261024/integration_r003.gd")'
    expected=ready.replace(old_call+'.before_budget(self)','if '+target+'.before_budget(self)==null:return').replace(old_call+'.after_budget(self)','if not '+target+'.after_budget(self):return')
    root_script=GAME/'scripts/tram_section_integration_20261024/ship_r003.gd';current=root_script.read_text()
    assert current[current.index('func _ready()'):].rstrip()==expected.rstrip();checks+=1
    assert expected.count('await _construction_step("group4_integrated_receiving.gd")')==2;checks+=1
    assert expected.index('.before_budget(self)')<expected.index('lighting_budget.configure(self,player)')<expected.index('.after_budget(self)');checks+=1
    hook=GAME/'scripts/court_completion_integration_20261022/ship.gd';assert 'elif label=="group4_integrated_receiving.gd"'in hook.read_text();checks+=1
    for rel in ['tram_section_successor_20261024/CONTRACTS.json','scripts/group4_integrated_receiving.gd','tests/group4_exact_pit_successor_guard.gd','data/architecture/group4_pit_receiving/EXACT_SOURCE_SUCCESSOR_PROOF.json','scripts/group4_tram_operating_controls.gd','scripts/group4_station_information.gd','scripts/startup_residency_20261020/received_sections_bootstrap.gd','night_garden_court_completion_20261022/lighting_budget.gd']:
        pin(GAME/rel)
    proof=json.loads((GAME/'data/architecture/group4_pit_receiving/EXACT_SOURCE_SUCCESSOR_PROOF.json').read_text())
    for pk,hk in [('before_path','before_sha256'),('patch_path','patch_sha256')]:
        p=GAME/proof[pk].removeprefix('res://');assert sha(p)==proof[hk];pin(p);checks+=1
    p=GAME/'data/generated/structural_meshes.json';assert sha(p)==proof['current_compiled_sha256'];pin(p);checks+=1
    configs=['GROUP4_COMPLETION_CANDIDATE','GROUP4_AFTMID_UPPER_SOURCE_CANDIDATE','GROUP4_BOARDING_SAFETY_CANDIDATE','GROUP4_TRAVEL_SOURCE_CANDIDATE','GROUP4_LOADED_CART_SOURCE_CANDIDATE','GROUP4_OPERATING_CONTROLS_SOURCE_CANDIDATE','GROUP4_STATION_INFORMATION_SOURCE_CANDIDATE']
    nested=[]
    for name in configs:
        p=GAME/'data/architecture'/f'{name}.json';pin(p);data=json.loads(p.read_text());assert data['active'];checks+=1
        if 'north_stop_adopted'in data:assert data['north_stop_adopted']and data['shared_pits_adopted'];checks+=1
        if 'terminal_active'in data:assert data['terminal_active'];checks+=1
        for uri,digest in data.get('original_runtime_pins',{}).items():
            path=GAME/uri.removeprefix('res://');assert sha(path)==digest,uri;pin(path);checks+=1;nested.append(uri)
        if 'file'in data and 'model_root'in data:
            path=GAME/data['model_root'].removeprefix('res://')/data['file'];assert sha(path)==data['sha256'];pin(path);checks+=1
    owned={'res://tram_section_successor_20261024/'+n:sha(OWN/n)for n in ['integration_r003.gd','check_installed_r003.gd']}
    contracts={'schema':'astraea.tram.integration.r003','protected_prerequisite':protected['commit'],'prerequisites':prerequisites,'owned':owned,'production_selected':False}
    output=OWN/'INTEGRATION_CONTRACTS_r003.json';assert not output.exists();output.write_text(json.dumps(contracts,indent=2)+'\n')
    scene=GAME/'scenes/ship_tram_section_candidate_r003_20261024.tscn'
    review={'status':'PASS_SOURCE_REVIEW_ONLY','checks':checks,'protected_readback':{k:protected[k]for k in ['commit','parent','independent_remote_readback','file_count','bytes','completed_utc']},'old_package_files_unchanged':len(old['files']),'selected_chain':chain,'ready_owners':[r['path']for r in ancestors],'intermediate_ready_override':False,'additive_successors_above_consolidated':len(chain)-2,'unchanged_labels_and_budget_order':True,'root_ready_diff':'Only two checked-call substitutions; every other original _ready byte retained','root_entry':{'scene':str(scene.relative_to(ROOT)),'scene_sha256':sha(scene),'script':str(root_script.relative_to(ROOT)),'script_sha256':sha(root_script)},'nested_pins_verified':nested,'engine_executed_by_helper':False,'installed_world_acceptance':'PENDING'}
    out=HERE/'SOURCE_REVIEW_r003.json';assert not out.exists();out.write_text(json.dumps(review,indent=2)+'\n')
    files=[OWN/'integration_r003.gd',OWN/'check_installed_r003.gd',OWN/'INTEGRATION_CONTRACTS_r003.json',HERE/'INTEGRATION_r003.md',HERE/'seal_integration_r003.py',out]
    manifest={'schema':'astraea.tram.integration.r003.handoff','files':{str(p.relative_to(ROOT)):{'bytes':p.stat().st_size,'sha256':sha(p)}for p in files},'root_owned_entry_excluded':review['root_entry'],'source_review':review['status'],'engine_validation':'PENDING','default_main_changed_by_helper':False}
    output=HERE/'PACKAGE_MANIFEST_r003.json';assert not output.exists();output.write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({'checks':checks,'unchanged_r002_files':len(old['files']),'chain':len(chain),'successors':len(chain)-2,'prerequisites':len(prerequisites),'files':len(files),'bytes':sum(p.stat().st_size for p in files),'manifest_sha256':sha(output),'critical_hashes':owned,'root_entry':review['root_entry']}))

if __name__=='__main__':main()
