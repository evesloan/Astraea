"""Exact two-owner successor. Re-run the unchanged triage proof on its full predecessor."""
import hashlib,json
from shapely.geometry import Polygon
from shapely.ops import unary_union
from theater_incremental_preservation import effective_shapes
PROOF_SHA = '275e10007060fc9f24e744cf59e05f7e8b7b2039e5dcf4675921096f7f54e951'

def preserve_botanical_court_successor(root, layout, elevations, owned, outputs, preserve_triage, preserve_welcome):
    path=root/'data/architecture/packages/botanical_court/BOTANICAL_COURT_COMPILER_PROOF.json'
    assert hashlib.sha256(path.read_bytes()).hexdigest()==PROOF_SHA
    proof=json.loads(path.read_text())
    assert hashlib.sha256((root/'data/design_contract.json').read_bytes()).hexdigest()==proof['contract_sha256']
    def retained(name):
        spec=proof['predecessors'][name];p=root/spec['retained_path']
        assert hashlib.sha256(p.read_bytes()).hexdigest()==spec['sha256']
        return json.loads(p.read_text())
    old=retained('data/spatial_layout.json');compiled=retained('data/generated/structural_meshes.json')
    assert compiled['source_checks']==retained('docs/LAYOUT_COMPILE_CHECKS.json')
    additions=proof['new_layout_records'];ids={r['id'] for r in additions}
    assert len(ids)==2
    assert layout['regions']==old['regions']+additions, 'Exact prior layout/order or bounded additions changed'
    assert {k:v for k,v in layout.items() if k!='regions'}=={k:v for k,v in old.items() if k!='regions'}
    assert len({r['id'] for r in layout['regions']})==len(layout['regions'])
    prior_shapes=effective_shapes(old,elevations)
    assert all(prior_shapes[r['id']].equals(owned[r['id']]) for r in old['regions'])
    old_outputs=[r for r in outputs if r['id'] not in ids]
    projected=dict(layout);projected['regions']=old['regions']
    prior_owned={k:v for k,v in owned.items() if k not in ids}
    preserved,welcome_receipt,triage_receipt=preserve_triage(root,projected,elevations,prior_owned,old_outputs,preserve_welcome)
    assert preserved==compiled['regions'], 'Complete 273-owner predecessor must match, including order and metadata'
    new_outputs=[r for r in outputs if r['id'] in ids]
    assert len(new_outputs)==2 and len(outputs)==len(preserved)+2
    for spec,row in zip(additions,new_outputs):
        expected=Polygon(spec['boundary'])
        assert row['id']==spec['id'] and row['deck']=='D06' and row['floor_y']==27 and row['thickness']==.24
        assert expected.area==120 and owned[row['id']].equals(expected)
        assert unary_union([Polygon(t) for t in row['triangles']]).equals(expected)
        assert row['structural_area_m2']==120 and row['material_role']=='guest_floor'
    receipt={'proof_sha256':PROOF_SHA,'retained_layout_records':len(old['regions']),'retained_compiled_records':len(preserved),'retained_void_records':len(old['voids']),'new_owners':sorted(ids),'new_area_m2':240,'complete_old_records_preserved':True,'scope':'Structural source proof; engine and final room acceptance not run'}
    return preserved+new_outputs,welcome_receipt,triage_receipt,receipt
