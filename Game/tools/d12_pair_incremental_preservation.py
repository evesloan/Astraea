"""Fail-closed four-owner extension; all prior preservation checks remain active."""
import json,hashlib
from shapely.geometry import Polygon
from shapely.ops import unary_union
from theater_incremental_preservation import effective_shapes
PROOF_SHA='984551a7e10b65c27c5c1bd4f0e181fc6fa1da8f6a84fb6a34eabd2babe1f6e1'

def inputs(root):
 p=root/'data/architecture/packages/d12_pair_candidate/D12_PAIR_COMPILER_PROOF.json'
 assert hashlib.sha256(p.read_bytes()).hexdigest()==PROOF_SHA
 proof=json.loads(p.read_text())
 assert hashlib.sha256((root/'data/design_contract.json').read_bytes()).hexdigest()==proof['contract_sha256']
 old={}
 for key,row in proof['predecessors'].items():
  p=root/row['retained_path'];assert hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256'];old[key]=json.loads(p.read_text())
 assert old['data/generated/structural_meshes.json']['source_checks']==old['docs/LAYOUT_COMPILE_CHECKS.json']
 return proof,old

def prepare_projection(root,layout,elevations,owned,outputs):
 proof,old=inputs(root);base=old['data/spatial_layout.json'];add=proof['new_layout_records'];ids={r['id'] for r in add}
 assert len(ids)==4 and len({r['id'] for r in layout['regions']})==len(layout['regions'])
 assert layout['regions']==base['regions']+add
 assert {k:v for k,v in layout.items() if k!='regions'}=={k:v for k,v in base.items() if k!='regions'}
 original=effective_shapes(base,elevations)
 assert all(original[r['id']].equals(owned[r['id']]) for r in base['regions'])
 new=[r for r in outputs if r['id'] in ids];assert new==proof['new_expected_compiled_records']
 for row in new:
  assert row['floor_y']==78 and row['thickness']==.24
  expected=Polygon(next(r for r in add if r['id']==row['id'])['boundary'])
  assert owned[row['id']].equals(expected) and unary_union([Polygon(t) for t in row['triangles']]).equals(expected)
 return base,{k:v for k,v in owned.items() if k not in ids},[r for r in outputs if r['id'] not in ids],new

def finish_projection(root,prior,new):
 proof,old=inputs(root);assert prior==old['data/generated/structural_meshes.json']['regions'];assert len(prior)==296
 assert new==proof['new_expected_compiled_records']
 return prior+new,{'proof_sha256':PROOF_SHA,'retained_compiled_records':296,'new_owners':[r['id'] for r in new],'all_prior_records_exact':True,'new_area_m2':sum(r['structural_area_m2'] for r in new),'scope':'Static isolated compiler only; native/runtime gates pending'}
