"""Project an authenticated additive successor through every existing proof."""
import hashlib,json
from shapely.geometry import Polygon

def project_received_predecessor(root,layout,owned,outputs):
    proof=json.loads((root/'data/architecture/packages/received_sections/PREDECESSOR.json').read_text())
    def retained(key):
        spec=proof['predecessors'][key];p=root/spec['retained_path']
        assert hashlib.sha256(p.read_bytes()).hexdigest()==spec['sha256'],('Preimage changed',key)
        return json.loads(p.read_text())
    old=retained('data/spatial_layout.json');compiled=retained('data/generated/structural_meshes.json')
    assert compiled['source_checks']==retained('docs/LAYOUT_COMPILE_CHECKS.json')
    additions=proof['new_layout_records'];ids={r['id'] for r in additions}
    assert len(ids)==len(additions)
    assert layout['regions']==old['regions']+additions
    assert {k:v for k,v in layout.items() if k!='regions'}=={k:v for k,v in old.items() if k!='regions'}
    assert not ids.intersection(r['id'] for r in old['regions'])
    prior_owned={k:v for k,v in owned.items() if k not in ids}
    new_outputs=[r for r in outputs if r['id'] in ids]
    assert len(new_outputs)==len(ids)
    for spec in additions:
        shape=Polygon(spec['boundary'],spec.get('holes',[]))
        assert shape.is_valid and shape.equals(owned[spec['id']])
    return old,prior_owned,[r for r in outputs if r['id'] not in ids],new_outputs,compiled,proof

def merge_received_successor(preserved,new_outputs,compiled,proof):
    assert preserved==compiled['regions'], 'Every complete baseline compiler record must remain exact'
    assert [r['id'] for r in new_outputs]==[r['id'] for r in proof['new_layout_records']]
    receipt={'baseline_main':proof['baseline_main'],'retained_complete_compiled_records':len(preserved),
             'all_baseline_records_exact':True,'new_owners':[r['id'] for r in new_outputs],
             'new_area_m2':sum(r['structural_area_m2'] for r in new_outputs),'scope':proof['scope']}
    return preserved+new_outputs,receipt
