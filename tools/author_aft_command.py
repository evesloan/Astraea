"""Adopt reviewed aft command assets and only their missing floor, preserving old owners."""
from pathlib import Path
import argparse, copy, hashlib, json, shutil
from shapely.geometry import Polygon, box
from shapely.ops import unary_union
R=Path(__file__).resolve().parents[1]
C=Path('/workspace/shared/astraea-catalogue-continuation-20261002')
OWNER='aft_command_extension'
EXPECTED={'D18_directory_08','D18_directory_10'}

def write(path,value):
    path.write_text(json.dumps(value,indent=2)+'\n')

def floor_extension(layout):
    result=copy.deepcopy(layout)
    result['regions']=[r for r in result['regions'] if r.get('authoring_owner')!=OWNER]
    existing=[Polygon(r['boundary'],r.get('holes',[])) for r in result['regions'] if r['deck']=='D18']
    substrate=unary_union(existing)
    target=box(-36,80,36,102)
    missing=target.difference(substrate)
    assert abs(missing.area-1408)<1e-6, 'Existing substrate changed; re-coordinate before adoption'
    expected=unary_union([box(-36,80,-4,102),box(4,80,36,102)])
    assert missing.symmetric_difference(expected).area<1e-6
    for side,p in [('port',box(-36,80,-4,102)),('starboard',box(4,80,36,102))]:
        assert p.intersection(substrate).area<1e-6
        assert all(p.intersection(Polygon(v['boundary'])).area<1e-6 for v in result['voids'] if 'D18' in v.get('decks',[]))
        result['regions'].append({'id':'D18_aft_command_'+side+'_floor','authoring_owner':OWNER,'deck':'D18','boundary':[list(q) for q in p.exterior.coords[:-1]],'holes':[],'priority':80,'thickness':.24,'material_role':'guest_floor','status':'Aft command platform; supported-source and runtime acceptance recorded separately'})
    assert unary_union(existing).intersection(missing).area<1e-6
    return result

def reviewed(family,identity,expected_sha):
    source=C/'assets'/family/'exports'/(identity+'.glb')
    assert hashlib.sha256(source.read_bytes()).hexdigest()==expected_sha,'Reviewed export hash changed: '+identity
    data=json.loads((source.parent.parent/'source/section_contract.json').read_text())
    assert data['catalogue_id']==identity
    manifest=json.loads((C/'catalogue_manifest.json').read_text())
    matches=[entry for entry in manifest['assets'] if entry['catalogue_id']==identity]
    assert len(matches)==1,'Catalogue identity must be unique: '+identity
    assert matches[0]['family']==family and matches[0]['export_sha256']==expected_sha
    data['export_sha256']=expected_sha
    data['runtime_status']='Integrated source pending focused, aggregate and visual acceptance'
    return source,data

def author(central_sha,aft_sha):
    central_source,central=reviewed('central_crown','AST-CMD-001',central_sha)
    aft_source,aft=reviewed('aft_command','AST-CMD-002',aft_sha)
    assert {p['programme_key'] for p in central['programmes']}=={f'D18_directory_{i:02}' for i in range(2,8)}
    assert {p['programme_key'] for p in aft['programmes']}==EXPECTED
    for p in aft['programmes']:
        wanted=box(-36,66,-10,102) if p['programme_key']=='D18_directory_08' else box(10,66,36,102)
        assert Polygon(p['boundary']).symmetric_difference(wanted).area<1e-6
    layout=floor_extension(json.loads((R/'data/spatial_layout.json').read_text()))
    ledger=json.loads((R/'data/programme_ledger.json').read_text())
    assert len(ledger['destinations'])==161
    for p in aft['programmes']:
        row=next(r for r in ledger['destinations'] if r['programme_key']==p['programme_key'])
        row.update(current_geometry_owner='scripts/aft_command_crown.gd',current_boundary_xz=p['boundary'],current_boundary_authority='data/architecture/AFT_COMMAND_RUNTIME.json',current_status='Unfurnished aft command shell; operational systems and acceptance pending')
    # All validation precedes writes. This is adoption, never workspace restoration.
    write(R/'data/spatial_layout.json',layout)
    write(R/'data/programme_ledger.json',ledger)
    for data,name,source,identity in [(central,'CENTRAL_CROWN_RUNTIME',central_source,'AST-CMD-001'),(aft,'AFT_COMMAND_RUNTIME',aft_source,'AST-CMD-002')]:
        write(R/'data/architecture'/(name+'.json'),data)
        shutil.copyfile(source,R/'assets/models'/(identity+'.glb'))
    print(json.dumps({'new_floor_m2':1408,'programmes':sorted(EXPECTED),'guest_units_change':0,'acceptance_pending':True}))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--central-sha',required=True);parser.add_argument('--aft-sha',required=True)
    args=parser.parse_args();author(args.central_sha,args.aft_sha)
