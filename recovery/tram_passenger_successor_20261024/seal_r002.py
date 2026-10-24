#!/usr/bin/env python3
"""Seal/verify one initialization successor. No engine or source modifications."""
from pathlib import Path
import hashlib,json,sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
GAME=ROOT/'Game'
OWN=GAME/'tram_passenger_successor_20261024'

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def save_new(path,value):
    with path.open('x') as file:file.write(json.dumps(value,indent=2)+'\n')

def invariant_checks():
    first=json.loads((HERE/'PACKAGE_MANIFEST.json').read_text())
    for path,row in first['files'].items():assert sha(ROOT/path)==row['sha256'],path
    original=(GAME/'scripts/group4_boarding_safety.gd').read_text()
    old=original.split('static func create_candidate_vehicle(',1)[1].split('static func build(parent:',1)[0]
    new=(OWN/'vehicle_initial_pose_r002.gd').read_text()
    suffix=' var visual:Node3D=(load(MODELS+item.file) as PackedScene).instantiate();body.add_child(visual)'
    assert old[old.index(suffix):]==new[new.index(suffix):]
    assert new.index('body.transform=initial_pose')<new.index('parent.add_child(body)')
    old_assembly=(GAME/'tram_section_successor_20261024/assembly.gd').read_text()
    new_assembly=(OWN/'assembly_initial_pose_r002.gd').read_text()
    start='\tvar body:AnimatableBody3D=load("res://scripts/group4_boarding_safety.gd")'
    end='\tbody.set_meta("group4_initial_source_cursor"'
    a=old_assembly.index(start);b=old_assembly.index(end,a)
    x=new_assembly.index('\tvar initial_pose:=Transform3D(');y=new_assembly.index(end,x)
    assert old_assembly[:a]==new_assembly[:x] and old_assembly[b:]==new_assembly[y:]
    old_check=(OWN/'check_carry.gd').read_text();new_check=(OWN/'check_carry_r002.gd').read_text()
    for first_line,last_line in [('func stock_preserved()', 'func continuous('),('func travel(', 'func run()'),('\t# These are the only actor pose assignments:','\nfunc finish()')]:
        left=old_check[old_check.index(first_line):old_check.index(last_line)]
        right=new_check[new_check.index(first_line):new_check.index(last_line)]
        left=left.replace('res://tram_section_successor_20261024/assembly.gd','res://tram_passenger_successor_20261024/assembly_initial_pose_r002.gd')
        assert left==right,first_line
    return sha(HERE/'PACKAGE_MANIFEST.json')

def main():
    first_manifest=invariant_checks()
    if '--verify' in sys.argv:
        manifest=json.loads((HERE/'PACKAGE_MANIFEST_r002.json').read_text())
        for name,row in manifest['files'].items():
            p=ROOT/name;assert sha(p)==row['sha256'] and p.stat().st_size==row['bytes'],name
        contracts=json.loads((OWN/'CONTRACTS_r002.json').read_text())
        for bucket in ['prerequisites','owned']:
            for name,digest in contracts[bucket].items():assert sha(GAME/name[6:])==digest,name
        print(json.dumps({'status':'PASS_SOURCE_ONLY','files':len(manifest['files']),'prerequisites':len(contracts['prerequisites']),'engine_run':False,'manifest_sha256':sha(HERE/'PACKAGE_MANIFEST_r002.json')}));return
    evidence=HERE/'evidence_r001';evidence.mkdir(exist_ok=False)
    evidence_hashes={}
    for mode in ['baseline','primitive']:
        for extension in ['json','log']:
            source=Path('/tmp')/('astraea-original-carry-'+mode+'.'+extension)
            target=evidence/source.name
            with target.open('xb') as file:file.write(source.read_bytes())
            assert sha(target)==sha(source)
            evidence_hashes[str(target.relative_to(ROOT))]=sha(target)
    baseline=json.loads((evidence/'astraea-original-carry-baseline.json').read_text())
    primitive=json.loads((evidence/'astraea-original-carry-primitive.json').read_text())
    assert baseline['failures']==1 and baseline['motion_frames']==0
    assert primitive['primitive']['changed_contacts']==0 and primitive['samples']==[]
    section=json.loads((GAME/'tram_section_successor_20261024/section_plan_r002.json').read_text())
    pose=section['central']['new_pose'];xyz=[pose[1],56.1,pose[2]]
    measured=[float(x) for x in baseline['samples'][0]['vehicle_velocity'].strip('()').split(',')]
    predicted=[x*60 for x in xyz]
    assert max(abs(a-b)for a,b in zip(measured,predicted))<.001
    proof={'schema':'astraea.tram.initial_pose.r002','status':'PASS_SOURCE_ONLY','baseline_source_commit':'913609a143d191b5fde3348cc3350280f8b9694c','first_fixture_manifest_sha256':first_manifest,'original_contact_construction_suffix_byte_identical':True,'assembly_changes_only_initial_factory_call':True,'original_actor_stock_settling_clamp_joint_motion_gate_blocks_unchanged':True,'initial_pose_xyz':xyz,'predicted_origin_displacement_velocity_60hz':predicted,'baseline_reported_first_velocity':measured,'baseline_cart_upward_failure_m_s':baseline['maximum_upward_speed_m_s'],'baseline_failure_frame':baseline['samples'][-1]['frame'],'baseline_joint_exists':baseline['samples'][-1]['joint_exists'],'primitive_changed_contacts':0,'primitive_executed_physics':False,'evidence':evidence_hashes,'initialization_correction_runtime_tested':False,'caster_cause_proven':False,'production_admitted':False}
    save_new(OWN/'SOURCE_PROOF_r002.json',proof)
    first_contract=json.loads((OWN/'CONTRACTS.json').read_text())
    prerequisites={**first_contract['prerequisites'],**first_contract['owned'],'res://tram_passenger_successor_20261024/CONTRACTS.json':sha(OWN/'CONTRACTS.json')}
    for name,digest in prerequisites.items():assert sha(GAME/name[6:])==digest,name
    owned={str('res://'+str(path.relative_to(GAME))):sha(path)for path in [OWN/'vehicle_initial_pose_r002.gd',OWN/'assembly_initial_pose_r002.gd',OWN/'check_carry_r002.gd',OWN/'SOURCE_PROOF_r002.json']}
    save_new(OWN/'CONTRACTS_r002.json',{'schema':'astraea.tram.initial_pose.r002','prerequisites':prerequisites,'owned':owned,'production_selected':False,'primitive_selected':False})
    paths=[OWN/name for name in ['vehicle_initial_pose_r002.gd','assembly_initial_pose_r002.gd','check_carry_r002.gd','SOURCE_PROOF_r002.json','CONTRACTS_r002.json']]+[HERE/'README_r002.md',HERE/'seal_r002.py']+list(evidence.iterdir())
    manifest={'files':{str(p.relative_to(ROOT)):{'bytes':p.stat().st_size,'sha256':sha(p)}for p in paths},'first_fixture_unchanged':True,'main_unchanged':True,'engine_run_by_helper':False,'r002_runtime_status':'PENDING_ROOT_ONLY_BOUNDED_CHECK'}
    save_new(HERE/'PACKAGE_MANIFEST_r002.json',manifest)
    print(json.dumps({'status':'SEALED_SOURCE_ONLY','files':len(paths),'bytes':sum(p.stat().st_size for p in paths),'prerequisites':len(prerequisites),'manifest_sha256':sha(HERE/'PACKAGE_MANIFEST_r002.json'),'scripts':owned}))

if __name__=='__main__':main()
