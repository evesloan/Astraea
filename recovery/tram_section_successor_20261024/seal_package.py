#!/usr/bin/env python3
"""Seal exact additive candidate bytes; never edits a global source manifest."""
from pathlib import Path
import hashlib,json,re,sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];GAME=ROOT/'Game';OWN=GAME/'tram_section_successor_20261024'

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    prerequisites={}
    def pin(path):
        path=path.resolve()
        if not path.is_file():raise FileNotFoundError(path)
        if not path.is_relative_to(GAME):return
        uri='res://'+str(path.relative_to(GAME))
        if uri in prerequisites:return
        prerequisites[uri]=digest(path)
        if path.suffix in ['.gd','.tscn','.json']:
            for found in re.findall(r'res://[A-Za-z0-9_./-]+\.(?:gd|tscn|json|glb|gdshader)',path.read_text()):
                child=GAME/found.removeprefix('res://')
                if child.is_file()and not child.is_relative_to(OWN):pin(child)
    for name in ['group4_completion','group4_aftmid_upper_successor','group4_boarding_safety','group4_boarding_bridge','group4_cart_restraint','group4_loaded_tram_actuator','group4_tram_source_actuator','group4_tram_operating_controls','group4_tram_control_button','group4_cart_handle_guard','group4_station_information','static_contact_cache','commons_lift','lift_gate']:
        pin(GAME/'scripts'/f'{name}.gd')
    configs=['GROUP4_COMPLETION_CANDIDATE','GROUP4_AFTMID_UPPER_SOURCE_CANDIDATE','GROUP4_BOARDING_SAFETY_CANDIDATE','GROUP4_TRAVEL_SOURCE_CANDIDATE','GROUP4_LOADED_CART_SOURCE_CANDIDATE','GROUP4_OPERATING_CONTROLS_SOURCE_CANDIDATE','GROUP4_STATION_INFORMATION_SOURCE_CANDIDATE']
    for name in configs:
        path=GAME/'data/architecture'/f'{name}.json';pin(path);data=json.loads(path.read_text())
        base=GAME/data.get('model_root','res://source_derivatives/group4_completion_20261011/').removeprefix('res://')
        for item in data.get('models',[])+data.get('exports',[]):pin(base/item['file'])
        if 'selected_model'in data:pin(base/data['selected_model'])
    report=json.loads((HERE/'SOURCE_GATE_FINAL.json').read_text())
    for relative in report['source_pins']:
        path=ROOT/relative
        if path.is_relative_to(GAME)and not path.is_relative_to(OWN):pin(path)
    selected=['assembly.gd','boarding.gd','bridge.gd','motor.gd','installed_gate.gd','check_controller.gd','section_r002.glb','section_plan_r002.json','POSE_KNOTS_r002.json','bridge.glb','NEIGHBORS.json']
    owned={'res://'+str((OWN/name).relative_to(GAME)):digest(OWN/name)for name in selected}
    contracts={'schema':'astraea.tram.section.20261024.r002','status':'UNADOPTED_SOURCE_CANDIDATE','baseline_protected':'c2d7383311d3f52574a150c56bac6a9b6e3a0c3e','prerequisites':dict(sorted(prerequisites.items())),'owned':owned,'not_authorized_by_this_file':['production boarding','motion','joint admission'],'scope':'Exact successor dependencies, not replacement of global SOURCE_CONTRACTS'}
    out=OWN/'CONTRACTS.json';assert not out.exists();out.write_text(json.dumps(contracts,indent=2)+'\n')
    files={}
    for base in [HERE,OWN]:
        for path in sorted(base.rglob('*')):
            if path.is_file()and path.name!='PACKAGE_MANIFEST.json'and'__pycache__'not in path.parts:
                files[str(path.relative_to(ROOT))]={'bytes':path.stat().st_size,'sha256':digest(path)}
    result=HERE/'PACKAGE_MANIFEST.json';assert not result.exists();result.write_text(json.dumps({'schema':'astraea.tram.section.additive.handoff','selected_runtime_namespace':'Game/tram_section_successor_20261024','selected_geometry':'geometry_r002','source_gate':report['status'],'engine_executed_by_helper':False,'native_generated_by_helper':False,'production_selected':False,'files':files},indent=2)+'\n')
    print(json.dumps({'files':len(files),'bytes':sum(x['bytes']for x in files.values()),'runtime_prerequisites':len(prerequisites),'selected_owned':len(owned),'manifest_sha256':digest(result)}))

if __name__=='__main__':main()
