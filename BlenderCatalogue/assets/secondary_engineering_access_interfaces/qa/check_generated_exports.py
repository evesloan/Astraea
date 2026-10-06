"""Actual generated GLB triangle acceptance; no engine/import/render work.
Execute only after parent-authorized source generation. Never creates acceptance from plans.
"""
from check_prepared_geometry import *

def check():
    names=['AST-CIR-005_forward_pool_market_engineering_access','AST-DOR-002_wide270','AST-ENG-008_receiving_shoulders'];receipts={}
    for stem in names:
        src=R/'source'/(stem+'.blend');exp=R/'exports'/(stem+'.glb');rec=json.loads((R/'qa'/(stem+'.preservation.json')).read_text())
        assert sha(src)==rec['source_sha256'];assert sha(exp)==rec['export_sha256'];receipts[stem]=rec
    for p,h in json.loads((R/'source/input_pins.json').read_text())['inputs'].items():assert sha(Path(p))==h,p
    core=glb(R/'exports'/(names[0]+'.glb'));door=glb(R/'exports'/(names[1]+'.glb'));section=glb(R/'exports'/(names[2]+'.glb'))
    for n,t in core:assert not clipped_triangle(t,[7.635,6,-1.8,7.88,8.7,1.8]),n
    source_section=glb(C/'assets/secondary_engineering_section/exports/AST-ENG-008.glb')
    old_names={n for n,_ in source_section};new_names={n for n,_ in section}
    assert new_names-old_names=={'SEC_VISITOR_RECEIVING_SHOULDER_N','SEC_VISITOR_RECEIVING_SHOULDER_S'}
    assert len(section)==3724;assert len(source_section)==3700
    canonical=lambda t:tuple(sorted(tuple(p) for p in t))
    from collections import Counter
    for n in old_names:assert Counter(canonical(t) for k,t in source_section if k==n)==Counter(canonical(t) for k,t in section if k==n),n
    static=[(n,t) for n,t in door if '@LEAF_' not in n];moving=[(n,t) for n,t in door if '@LEAF_' in n]
    assert {n.split('@')[-1] for n,_ in moving}=={'LEAF_LEFT','LEAF_RIGHT'}
    assert abs(max(p[1] for _,t in door for p in t)-2.86)<2e-6
    assert abs(min(p[1] for n,t in static if n=='ENTRY_Header' for p in t)-2.7)<2e-6
    for root in ['LEAF_LEFT','LEAF_RIGHT']:
        panels=[p for n,t in moving if n.startswith('ENTRY_MovingPanel_') and n.endswith('@'+root) for p in t]
        assert abs(max(p[0] for p in panels)-min(p[0] for p in panels)-1.18)<2e-6
        assert abs(max(p[1] for p in panels)-2.685)<2e-6;assert abs(min(p[1] for p in panels)-.035)<2e-6
    world=lambda t:[[8.8+p[2],6+p[1],-432-p[0]] for p in t]
    env_static=[t for _,t in section]+[[[p[0],p[1],p[2]-432] for p in t] for _,t in core]
    fractions=[0,.15,.5,.85,1]
    for f in fractions:
        posed=[(n,[[p[0]+(-1 if n.endswith('@LEAF_LEFT') else 1)*1.24*f,p[1],p[2]] for p in t]) for n,t in moving]
        for root in ['LEAF_LEFT','LEAF_RIGHT']:
            verts=[p for n,t in posed if n.endswith('@'+root) for p in t];bounds=[min(p[k] for p in verts) for k in range(3)]+[max(p[k] for p in verts) for k in range(3)]
            for n,t in static:assert not clipped_triangle(t,bounds),(f,root,n)
            wv=[p for n,t in posed if n.endswith('@'+root) for p in world(t)];wb=[min(p[k] for p in wv) for k in range(3)]+[max(p[k] for p in wv) for k in range(3)]
            for t in env_static:assert not clipped_triangle(t,wb),(f,root,'source wall/shoulder contact')
        if f==1:
            for n,t in static+posed:assert not clipped_triangle(t,[-1.2,0,-.055,1.2,2.7,.055]),n
            # Exact source prism: section/core + installed static fitting + open leaves.
            for t in env_static+[world(t) for _,t in static+posed]:assert not clipped_triangle(t,[7.8,6,-433.2,9.1,8.7,-430.8]),t
    result={'stage':'actual exported triangle geometry checks only; runtime/visual acceptance pending','fractions':fractions,'original_source_pins_unchanged':True,'section_original_triangles_preserved':3700,'shoulder_triangles_added':24,'core_prism_clear':True,'open_tall_prism_clear':True,'moving_static_source_contact_free':True,'source_export_hashes':{n:{k:r[k] for k in ['source_sha256','export_sha256']} for n,r in receipts.items()},'runtime_ready':False,'limits':['No Blender reload/render acceptance in this check','No runtime profile acceptance','No CharacterBody3D/RigidBody3D upper-band obstruction tests','No loaded-module traversal/full regression']}
    (R/'qa/generated_triangle_receipt.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':check()
