"""One medical owner; preserve all current271 complete predecessor records."""
import hashlib,json
from shapely.geometry import Polygon
from shapely.ops import unary_union
from theater_incremental_preservation import effective_shapes
PROOF_SHA = "d635118faf4b48d27fc24f83fb09f6119910b363722c04d936faabfdfc549ba3"
PROOF_PATH = "data/architecture/packages/medical/MEDICAL_COMPILER_PROOF.json"
OWNER = "D05_forward_waiting_support_floor"

def preserve_medical_predecessor(root,layout,elevations,owned,outputs):
    proof_path=root/PROOF_PATH
    assert hashlib.sha256(proof_path.read_bytes()).hexdigest()==PROOF_SHA,"Medical compiler proof changed"
    proof=json.loads(proof_path.read_text())
    def retained(name):
        spec=proof['predecessors'][name];p=root/spec['retained_path']
        assert hashlib.sha256(p.read_bytes()).hexdigest()==spec['sha256'],name
        return json.loads(p.read_text())
    old_layout=retained('data/spatial_layout.json')
    old_compiled=retained('data/generated/structural_meshes.json')
    assert len(old_layout['regions'])==285 and len(old_compiled['regions'])==271 and len(old_layout['voids'])==28
    assert len(layout['regions'])==286 and len(outputs)==272
    assert {k:v for k,v in layout.items() if k!='regions'}=={k:v for k,v in old_layout.items() if k!='regions'}
    assert [r for r in layout['regions'] if r['id']!=OWNER]==old_layout['regions'],"Complete old layout/order changed"
    assert [r for r in layout['regions'] if r['id']==OWNER]==[proof['new_layout_record']]
    assert len({r['id'] for r in layout['regions']})==286
    assert len({r['id'] for r in outputs})==272
    old_by_id={r['id']:r for r in old_compiled['regions']}
    assert {r['id'] for r in outputs}==set(old_by_id)|{OWNER},"Exactly one medical compiled addition required"
    prior_shapes=effective_shapes(old_layout,elevations)
    old_input_ids={r['id'] for r in old_layout['regions']}
    for ident in old_input_ids:
        assert prior_shapes[ident].equals(owned[ident]),('Changed old effective shape',ident)
    reordered=[]
    for row in outputs:
        if row['id']==OWNER: continue
        prior=old_by_id[row['id']]
        assert set(row)==set(prior),row['id']
        for key in prior:
            if key not in ('triangles','rings','structural_area_m2'):
                assert row[key]==prior[key],('Changed metadata',row['id'],key)
        before=unary_union([Polygon(t) for t in prior['triangles']])
        after=unary_union([Polygon(t) for t in row['triangles']])
        assert before.equals(after) and before.equals(prior_shapes[row['id']]),row['id']
        assert abs(prior['structural_area_m2']-row['structural_area_m2'])<=1e-9,row['id']
        if row!=prior: reordered.append(row['id'])
    new=next(r for r in outputs if r['id']==OWNER)
    assert new['deck']=='D05' and new['floor_y']==21 and new['thickness']==.24
    assert abs(new['structural_area_m2']-350.72)<1e-8
    expected=Polygon(proof['new_layout_record']['boundary'])
    assert expected.equals(owned[OWNER])
    assert unary_union([Polygon(t) for t in new['triangles']]).equals(expected)
    for ident,shape in owned.items():
        if ident!=OWNER and abs(elevations[next(r['deck'] for r in layout['regions'] if r['id']==ident)]+next(r.get('offset_y',0) for r in layout['regions'] if r['id']==ident)-21)<1e-6:
            assert shape.intersection(expected).area<1e-7,('Medical coplanar overlap',ident)
    preserved=[old_by_id.get(r['id'],r) for r in outputs]
    assert [r for r in preserved if r['id']!=OWNER]==old_compiled['regions'],"Current271 record/order preservation failed"
    return preserved,{'proof_sha256':PROOF_SHA,'retained_layout_records':285,'retained_compiled_records':271,'retained_void_records':28,'new_owner':OWNER,'new_area_m2':350.72,'equivalent_triangulation_reorders_restored':reordered,'scope':'Exact structural preservation only; runtime access and visual acceptance remain separate'}
