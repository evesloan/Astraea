from pathlib import Path
import json
R=Path(__file__).resolve().parent;C=R/'compiler_candidate';M=C/'tools/night_table_incremental_preservation.py'
text='''
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
            assert ga.equals(gb) and old_shapes[row['id']].covers(ga),('Chunk geometry changed',row['id'],ca['id'])
            assert abs(sum(q.area for q in pa)-ga.area)<1e-8 and abs(sum(q.area for q in pb)-gb.area)<1e-8
        if a!=b:changes.append(row['id'])
        row['render_chunks']=b
    (root/'docs/NIGHT_TABLE_CHUNK_CANONICALIZATION.json').write_text(json.dumps({'physically_identical_chunk_order_retained_for':changes,'all_old_owners_checked':len(prior),'geometry_changed':False},indent=2)+'\\n')
    return outputs
'''
M.write_text(M.read_text()+text)
p=C/'tools/compile_layout.py';s=p.read_text();before='from night_table_incremental_preservation import preserve_night_table_successor';after=before+', canonicalize_night_table_predecessor_chunks';assert s.count(before)==1;s=s.replace(before,after)
before2='outputs,preservation=preserve_prior_records(root,layout,elevations,owned,outputs)';after2='outputs=canonicalize_night_table_predecessor_chunks(root,layout,elevations,owned,outputs)\n'+before2;assert s.count(before2)==1;s=s.replace(before2,after2);p.write_text(s)
ctx=C/'data/architecture/packages/night_table/BUILD_CONTEXT.json';d=json.load(open(ctx));d['compiler_inverse_edits']=[{'before':before,'after':after,'count':1},{'before':before2,'after':after2,'count':1}]+d['compiler_inverse_edits'];ctx.write_text(json.dumps(d,indent=2)+'\n');print('Added exact per-chunk geometry preservation before older strict metadata checks')
