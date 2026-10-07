"""Authenticate all279 predecessors before accepting exactly one Moss owner."""
import hashlib,json
from shapely.geometry import Polygon
from shapely.ops import unary_union
from theater_incremental_preservation import effective_shapes
PROOF_SHA='91b18afbf31ee9679b3162a6b01fd94ac458a1f9e60dae8128fb119ded52a472'

def preserve_moss_sanctuary_successor(root,layout,elevations,owned,outputs,preserve_movement,preserve_lounge,preserve_botanical,preserve_triage,preserve_welcome):
    p=root/'data/architecture/packages/moss_sanctuary/MOSS_COMPILER_PROOF.json'
    assert hashlib.sha256(p.read_bytes()).hexdigest()==PROOF_SHA,'Moss proof changed'
    proof=json.loads(p.read_text());assert proof['schema']==1
    assert hashlib.sha256((root/'data/design_contract.json').read_bytes()).hexdigest()==proof['contract_sha256']
    def retained(name):
        spec=proof['predecessors'][name];p=root/spec['retained_path'];assert hashlib.sha256(p.read_bytes()).hexdigest()==spec['sha256'];return json.loads(p.read_text())
    old=retained('data/spatial_layout.json');compiled=retained('data/generated/structural_meshes.json')
    assert compiled['source_checks']==retained('docs/LAYOUT_COMPILE_CHECKS.json')
    additions=proof['new_layout_records'];ids={r['id'] for r in additions}
    assert ids=={'D06_moss_sanctuary_receiving_floor'}
    assert layout['regions']==old['regions']+additions,'Exact predecessor layout/order and exactly one addition required'
    assert {k:v for k,v in layout.items() if k!='regions'}=={k:v for k,v in old.items() if k!='regions'}
    assert len({r['id'] for r in layout['regions']})==len(layout['regions'])
    prior_shapes=effective_shapes(old,elevations)
    assert all(prior_shapes[r['id']].equals(owned[r['id']]) for r in old['regions'])
    old_outputs=[r for r in outputs if r['id'] not in ids]
    projected=dict(layout);projected['regions']=old['regions'];prior_owned={k:v for k,v in owned.items() if k not in ids}
    preserved,welcome,triage,botanical,lounge,movement=preserve_movement(root,projected,elevations,prior_owned,old_outputs,preserve_lounge,preserve_botanical,preserve_triage,preserve_welcome)
    assert preserved==compiled['regions'],'All279 complete old records and order must remain exact'
    new_outputs=[r for r in outputs if r['id'] in ids]
    assert len(new_outputs)==1 and len(outputs)==len(preserved)+1 and len({r['id'] for r in outputs})==len(outputs)
    for spec,row,wanted in zip(additions,new_outputs,proof['new_expected_compiled_records']):
        expected=Polygon(spec['boundary'],spec.get('holes',[]))
        assert expected.is_valid and owned[row['id']].equals(expected)
        assert row==wanted,'Exact authenticated new compiler record required'
        assert row['deck']=='D06' and row['floor_y']==27 and row['thickness']==.24
        assert unary_union([Polygon(t) for t in row['triangles']]).equals(expected)
        for old_record in compiled['regions']:
            overlap=expected.intersection(prior_shapes[old_record['id']]).area
            if overlap>1e-8:
                slab_overlap=min(27,old_record['floor_y'])-max(26.76,old_record['floor_y']-old_record['thickness'])
                assert slab_overlap<1e-7,('Old slab conflict',old_record['id'])
    receipt={'proof_sha256':PROOF_SHA,'retained_layout_records':len(old['regions']),'retained_compiled_records':len(preserved),'retained_void_records':len(old['voids']),'new_owners':[r['id'] for r in additions],'new_area_m2':sum(r['structural_area_m2'] for r in new_outputs),'complete_old_records_preserved':True,'scope':'Exact structural preservation and source-foot support only; runtime and primary-deck bearing acceptance open'}
    return preserved+new_outputs,welcome,triage,botanical,lounge,movement,receipt
