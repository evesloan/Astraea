#!/usr/bin/env python3
"""Verify exact source box and preserved failure provenance; no engine."""
from pathlib import Path
import hashlib,itertools,json,sys
import numpy as np
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];GAME=ROOT/'Game';OWN=GAME/'tram_passenger_successor_20261024'
sys.path.insert(0,str(ROOT/'recovery/tram_section_successor_20261023'))
import triangle_gate as tg

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    retention=json.loads(Path('/workspace/astraea-env/receipts/tram-integrated-913609a1-readback.json').read_text())
    assert retention['commit']=='913609a143d191b5fde3348cc3350280f8b9694c'and retention['independent_remote_readback']
    vehicle=GAME/'source_derivatives/group4_boarding_safety_20261011/AST-TRM-G4-024_powered_portal_body_r001.glb'
    floor=[x for x in tg.glb(vehicle)if x['name']=='V2__Tram_Floor'];assert len(floor)==1
    floor=floor[0];points=np.unique(floor['points'],axis=0);lo=points.min(axis=0);hi=points.max(axis=0)
    corners=np.array(list(itertools.product(*zip(lo,hi))))
    assert len(points)==8 and len(floor['triangles'])==12
    assert {tuple(x)for x in points}=={tuple(x)for x in corners}
    for triangle in floor['triangles']:
        assert any(np.all(triangle[:,axis]==value)for axis in range(3)for value in [lo[axis],hi[axis]])
    volume=abs(np.einsum('ij,ij->i',floor['triangles'][:,0],np.cross(floor['triangles'][:,1],floor['triangles'][:,2])).sum()/6)
    assert abs(volume-float(np.prod(hi-lo)))<1e-10
    evidence=GAME/'docs/validation/tram_boarding_interlock_20261013/TRAM_CART_JOINT_CONCRETE_BLOCKER.json'
    diagnostic=GAME/'docs/validation/tram_boarding_interlock_20261013/diagnose_tram_cart_contacts.gd'
    failure=json.loads(evidence.read_text());assert not failure['joint_exists_during_failure']and failure['first_upward_impulse_frame']==5
    assert 'cart.global_transform=vehicle.global_transform' in diagnostic.read_text()
    proof={'schema':'astraea.tram.original_caster.exact_primitive.r001','status':'PASS_SOURCE_GEOMETRY_ONLY','protected_commit':retention['commit'],'vehicle_source':'res://'+str(vehicle.relative_to(GAME)),'vehicle_sha256':sha(vehicle),'floor_name':'V2__Tram_Floor','floor_min':lo.tolist(),'floor_max':hi.tolist(),'vertices':8,'triangles':12,'volume_m3':volume,'exact_box_corner_set':True,'history':failure,'historical_live_setup_relocation_in_source':True,'historical_evidence_sha256':sha(evidence),'historical_diagnostic_sha256':sha(diagnostic),'confirmed_solver_cause':False,'runtime_fix_verified':False,'source_geometry_or_actors_modified':False}
    dest=OWN/'SOURCE_PROOF.json';assert not dest.exists();dest.write_text(json.dumps(proof,indent=2)+'\n')
    old_contract=GAME/'tram_section_successor_20261024/CONTRACTS.json';old=json.loads(old_contract.read_text())
    prerequisites={**old['prerequisites'],**old['owned']};prerequisites['res://tram_section_successor_20261024/CONTRACTS.json']=sha(old_contract)
    extra=['scripts/cleaning_cart.gd','scripts/cleaning_bottle.gd','scripts/player.gd','scripts/physics_tether.gd','scripts/cart_handle.gd','scripts/lighting_budget.gd','scripts/group4_cart_restraint.gd','scripts/group4_tram_operating_controls.gd','scripts/group4_station_information.gd','data/architecture/cleaning_cart_contacts.json','assets/models/AST-HSK-005.glb']
    for name in extra:prerequisites['res://'+name]=sha(GAME/name)
    for uri,expected in prerequisites.items():assert sha(GAME/uri[6:])==expected,uri
    owned={'res://tram_passenger_successor_20261024/'+p.name:sha(p)for p in [OWN/'floor_contact.gd',OWN/'check_carry.gd',dest]}
    path=OWN/'CONTRACTS.json';assert not path.exists();path.write_text(json.dumps({'schema':'astraea.tram.original_source_carry.r001','prerequisites':prerequisites,'owned':owned,'production_selected':False,'baseline_first_required':True},indent=2)+'\n')
    files=[p for base in [HERE,OWN]for p in base.iterdir()if p.is_file()and p.name!='PACKAGE_MANIFEST.json']
    manifest={'files':{str(p.relative_to(ROOT)):{'bytes':p.stat().st_size,'sha256':sha(p)}for p in files},'engine_run':False,'default_main_or_prior_source_changed':False,'physical_acceptance':'PENDING_MATCHED_BASELINE_FIRST'}
    path=HERE/'PACKAGE_MANIFEST.json';assert not path.exists();path.write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({'files':len(files),'bytes':sum(p.stat().st_size for p in files),'prerequisites':len(prerequisites),'exact_floor_corners':len(points),'manifest_sha256':sha(path),'script_hashes':owned}))

if __name__=='__main__':main()
