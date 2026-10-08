from pathlib import Path
import sys,json,copy,hashlib
R=Path(__file__).resolve().parent;C=R/'compiler_candidate'
sys.path.insert(0,str(C/'tools'))
from crew_batch_incremental_preservation import canonicalize_crew_batch_predecessor_chunks as check
from theater_incremental_preservation import effective_shapes
layout=json.loads((C/'data/spatial_layout.json').read_text());compiled=json.loads((C/'data/generated/structural_meshes.json').read_text());contract=json.loads((C/'data/design_contract.json').read_text())
elev={r['deck_id']:r['floor_elevation_m'] for r in contract['deck_datums']};owned=effective_shapes(layout,elev)
rows=compiled['regions'];results=[]
def rejected(name,l,o):
 try:check(C,l,elev,owned,o)
 except AssertionError as e:results.append({'test':name,'rejected':True,'reason':str(e)});return
 raise AssertionError('Invalid candidate accepted: '+name)
l=copy.deepcopy(layout);l['regions'][0]['priority']=l['regions'][0].get('priority',0)+1;rejected('changed predecessor input',l,copy.deepcopy(rows))
o=copy.deepcopy(rows);r=next(r for r in o if r['render_chunks'] and r['render_chunks'][0]['triangles']);r['render_chunks'][0]['triangles'][0][0][0]+=.25;rejected('changed predecessor chunk vertex',layout,o)
o=copy.deepcopy(rows);r=next(r for r in o if r['render_chunks'] and r['render_chunks'][0]['triangles']);r['render_chunks'][0]['triangles'].append(copy.deepcopy(r['render_chunks'][0]['triangles'][0]));rejected('duplicate overlapping predecessor triangle',layout,o)
check(C,layout,elev,owned,copy.deepcopy(rows));results.append({'test':'unchanged valid candidate','accepted':True})
(R/'NEGATIVE_CONTROLS.json').write_text(json.dumps({'results':results,'scope':'Chunk canonicalization preservation gate; no live edits'},indent=2)+'\n');print(json.dumps(results))
