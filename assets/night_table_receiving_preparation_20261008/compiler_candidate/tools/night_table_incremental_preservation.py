"""Authenticate all282 predecessors before accepting exactly two Night Table owners."""
import hashlib,json
from shapely.geometry import Polygon
from shapely.ops import unary_union
from theater_incremental_preservation import effective_shapes
PROOF_SHA='5c87fd6f0baf918d2bedefe3143532db4c004d3f5553403c0b79d4531c8481c9'

def preserve_night_table_successor(root,layout,elevations,owned,outputs,preserve_sports,preserve_moss,preserve_movement,preserve_lounge,preserve_botanical,preserve_triage,preserve_welcome):
    p=root/'data/architecture/packages/night_table/NIGHT_TABLE_COMPILER_PROOF.json'
    assert hashlib.sha256(p.read_bytes()).hexdigest()==PROOF_SHA,'Night Table proof changed'
    proof=json.loads(p.read_text());assert proof['schema']==1
    assert hashlib.sha256((root/'data/design_contract.json').read_bytes()).hexdigest()==proof['contract_sha256']
    def retained(name):
        spec=proof['predecessors'][name];p=root/spec['retained_path'];assert hashlib.sha256(p.read_bytes()).hexdigest()==spec['sha256'];return json.loads(p.read_text())
    old=retained('data/spatial_layout.json');compiled=retained('data/generated/structural_meshes.json')
    assert compiled['source_checks']==retained('docs/LAYOUT_COMPILE_CHECKS.json')
    additions=proof['new_layout_records'];ids={r['id'] for r in additions}
    assert ids=={'D10_night_table_floor','D10_night_table_entry'}
    assert layout['regions']==old['regions']+additions,'Exact predecessor layout/order and exactly two addition required'
    assert {k:v for k,v in layout.items() if k!='regions'}=={k:v for k,v in old.items() if k!='regions'}
    assert len({r['id'] for r in layout['regions']})==len(layout['regions'])
    prior_shapes=effective_shapes(old,elevations)
    assert all(prior_shapes[r['id']].equals(owned[r['id']]) for r in old['regions'])
    old_outputs=[r for r in outputs if r['id'] not in ids]
    projected=dict(layout);projected['regions']=old['regions'];prior_owned={k:v for k,v in owned.items() if k not in ids}
    preserved,welcome,triage,botanical,lounge,movement,moss,sports=preserve_sports(root,projected,elevations,prior_owned,old_outputs,preserve_moss,preserve_movement,preserve_lounge,preserve_botanical,preserve_triage,preserve_welcome)
    assert preserved==compiled['regions'],'All282 complete old records and order must remain exact'
    new_outputs=[r for r in outputs if r['id'] in ids]
    assert len(new_outputs)==2 and len(outputs)==len(preserved)+2 and len({r['id'] for r in outputs})==len(outputs)
    for spec,row,wanted in zip(additions,new_outputs,proof['new_expected_compiled_records']):
        expected=Polygon(spec['boundary'],spec.get('holes',[]))
        assert expected.is_valid and owned[row['id']].equals(expected)
        assert row==wanted,'Exact authenticated new compiler record required'
        assert row['deck']=='D10' and row['floor_y']==61 and row['thickness']==.24
        assert unary_union([Polygon(t) for t in row['triangles']]).equals(expected)
        for old_record in compiled['regions']:
            overlap=expected.intersection(prior_shapes[old_record['id']]).area
            if overlap>1e-8:
                slab_overlap=min(61,old_record['floor_y'])-max(60.76,old_record['floor_y']-old_record['thickness'])
                assert slab_overlap<1e-7,('Old slab conflict',old_record['id'])
    receipt={'proof_sha256':PROOF_SHA,'retained_layout_records':len(old['regions']),'retained_compiled_records':len(preserved),'retained_void_records':len(old['voids']),'new_owners':[r['id'] for r in additions],'new_area_m2':sum(r['structural_area_m2'] for r in new_outputs),'complete_old_records_preserved':True,'scope':'Exact structural preservation and source-foot support only; runtime and primary-deck bearing acceptance open'}
    return preserved+new_outputs,welcome,triage,botanical,lounge,movement,moss,sports,receipt

def canonicalize_night_table_predecessor_chunks(root,layout,elevations,owned,outputs):
    """Retain exact old chunk ordering ONLY after equal per-chunk geometry proof."""
    p=root/'data/architecture/packages/night_table/NIGHT_TABLE_COMPILER_PROOF.json'
    assert hashlib.sha256(p.read_bytes()).hexdigest()==PROOF_SHA
    proof=json.loads(p.read_text())
    def retained(key):
        r=proof['predecessors'][key];f=root/r['retained_path']
        assert hashlib.sha256(f.read_bytes()).hexdigest()==r['sha256']
        return json.loads(f.read_text())
    old_layout=retained('data/spatial_layout.json');old=retained('data/generated/structural_meshes.json')
    assert layout['regions']==old_layout['regions']+proof['new_layout_records']
    old_shapes=effective_shapes(old_layout,elevations)
    prior={r['id']:r for r in old['regions']};changes=[]
    for row in outputs:
        if row['id'] not in prior:continue
        r=prior[row['id']]
        assert old_shapes[row['id']].equals(owned[row['id']])
        a=row['render_chunks'];b=r['render_chunks']
        assert [q['id']for q in a]==[q['id']for q in b]
        for ca,cb in zip(a,b):
            assert set(ca)==set(cb)=={'id','triangles'}
            pa=[Polygon(t)for t in ca['triangles']];pb=[Polygon(t)for t in cb['triangles']]
            assert all(q.is_valid and q.area>0 for q in pa+pb)
            ga=unary_union(pa);gb=unary_union(pb)
            if not ga.equals(gb):
                report={'owner':row['id'],'chunk':ca['id'],'equals':ga.equals(gb),'covered':old_shapes[row['id']].covers(ga),'symmetric_difference_area':ga.symmetric_difference(gb).area,'hausdorff_distance':ga.hausdorff_distance(gb),'outside_old_area':ga.difference(old_shapes[row['id']]).area,'candidate':ca,'prior':cb}
                (root/'docs/NIGHT_TABLE_CHUNK_DIAGNOSTIC.json').write_text(json.dumps(report,indent=2)+'\n')
                raise AssertionError(('Chunk geometry changed',row['id'],ca['id']))
            assert abs(sum(q.area for q in pa)-ga.area)<1e-8 and abs(sum(q.area for q in pb)-gb.area)<1e-8
        if a!=b:changes.append(row['id'])
        row['render_chunks']=b
    (root/'docs/NIGHT_TABLE_CHUNK_CANONICALIZATION.json').write_text(json.dumps({'physically_identical_chunk_order_retained_for':changes,'all_old_owners_checked':len(prior),'geometry_changed':False},indent=2)+'\n')
    return outputs
