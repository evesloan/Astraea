"""Build an isolated two-band receiving candidate. Never writes the source project."""
from pathlib import Path
import json,hashlib,shutil
R=Path(__file__).resolve().parent
G=Path('/workspace/shared/Astraea_recovery_20261007_AXWr5x/Game')
C=R/'candidate/Game'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not C.exists(), 'Keep predecessor; use a new candidate directory if rebuilding'
(C/'tools').mkdir(parents=True);(C/'docs').mkdir();shutil.copytree(G/'data',C/'data')
for p in (G/'tools').glob('*.py'):shutil.copy2(p,C/'tools'/p.name)
base=C/'data/architecture/packages/botanical_court/retained';base.mkdir(parents=True)
pre={}
for f in ['data/spatial_layout.json','data/generated/structural_meshes.json','docs/LAYOUT_COMPILE_CHECKS.json']:
 t=base/Path(f).name;shutil.copy2(G/f,t);pre[f]={'sha256':sha(t),'retained_path':str(t.relative_to(C))}
layout=json.loads((G/'data/spatial_layout.json').read_text())
new=[]
for side,x0,x1 in [('port',-8,-4),('starboard',4,8)]:
 new.append({'id':f'D06_botanical_court_{side}_receiving_floor','authoring_owner':'botanical_court_receiving','deck':'D06','boundary':[[x0,-238],[x1,-238],[x1,-208],[x0,-208]],'thickness':0.24,'material_role':'guest_floor','status':'Bounded botanical receiving floor; room interiors, upper pavilion and runtime acceptance remain separate'})
assert not {r['id'] for r in new}&{r['id'] for r in layout['regions']}
layout['regions']+=new
(C/'data/spatial_layout.json').write_text(json.dumps(layout,indent=2)+'\n')
proof={'schema':1,'predecessors':pre,'new_layout_records':new,'contract_sha256':sha(G/'data/design_contract.json'),'scope':'Two receiving side-bands only. All predecessor inputs, meshes, voids and order exact.'}
p=C/'data/architecture/packages/botanical_court/BOTANICAL_COURT_COMPILER_PROOF.json';p.write_text(json.dumps(proof,indent=2)+'\n')
module='''"""Exact two-owner successor. Re-run the unchanged triage proof on its full predecessor."""
import hashlib,json
from shapely.geometry import Polygon
from shapely.ops import unary_union
from theater_incremental_preservation import effective_shapes
PROOF_SHA = PROOF_HASH

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
'''.replace('PROOF_HASH',repr(sha(p)))
(C/'tools/botanical_court_incremental_preservation.py').write_text(module)
p=C/'tools/compile_layout.py';s=p.read_text();s=s.replace('from medical_triage_incremental_preservation import preserve_medical_triage_successor','from medical_triage_incremental_preservation import preserve_medical_triage_successor\nfrom botanical_court_incremental_preservation import preserve_botanical_court_successor')
old='outputs,medical_preservation,triage_preservation=preserve_medical_triage_successor(root,layout,elevations,owned,outputs,preserve_medical_predecessor)'
assert s.count(old)==1
s=s.replace(old,'outputs,medical_preservation,triage_preservation,botanical_preservation=preserve_botanical_court_successor(root,layout,elevations,owned,outputs,preserve_medical_triage_successor,preserve_medical_predecessor)')
s=s.replace("checks['medical_triage_additive_preservation']=triage_preservation","checks['medical_triage_additive_preservation']=triage_preservation\nchecks['botanical_court_additive_preservation']=botanical_preservation")
p.write_text(s)
inputs=[p for sub in ['data','tools','scripts','tests'] for p in (G/sub).rglob('*') if p.is_file() and '__pycache__' not in p.parts]
(R/'SOURCE_INPUT_HASHES_BEFORE.json').write_text(json.dumps({str(p.relative_to(G)):sha(p) for p in inputs},indent=2)+'\n')
print(C)
