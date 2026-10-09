from pathlib import Path
import sys,json,hashlib,shutil,copy,subprocess
O=Path(__file__).resolve().parent; S=O.parent; R=Path('/workspace/shared/Astraea_recovery_20261007_AXWr5x'); G=R/'Game'; I=O/'isolated/Game'
sys.path.insert(0,str(S/'botanical_receiving_court_build_20261007/python_deps'))
from shapely.geometry import Polygon
from shapely.geometry.polygon import orient
from shapely import constrained_delaunay_triangles
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2)+'\n')
pins={}
def pin(p):pins[str(p)]={'sha256':sha(p),'bytes':p.stat().st_size};return p
def read(p):return json.loads(pin(p).read_text())
layout=read(G/'data/spatial_layout.json'); old=read(G/'data/generated/structural_meshes.json');checks=read(G/'docs/LAYOUT_COMPILE_CHECKS.json');assert len(old['regions'])==296 and checks==old['source_checks']
candidates=read(S/'lounge_pair_floor_candidates_20261008/FLOOR_CANDIDATES.json')['additions'];cat=read(R/'BlenderCatalogue/catalogue_manifest.json');read(G/'data/programme_ledger.json')
for p in ['AGENTS.md','data/design_contract.json','scripts/ship.gd','scripts/crew_batch_receiving.gd','docs/WHOLE_SHIP_SECTION_COORDINATION.md','docs/master_source/MASTER_CURRENT_APPLICATION.json','docs/master_source/MASTER_FULL_CONTENT_INDEX.json']:pin(G/p)
for p in (G/'tools').glob('*.py'):pin(p)
for p in (G/'data/architecture/packages').rglob('*'):
 if p.is_file():pin(p)
for p in ['INDEPENDENT_LIBRARY_VERIFICATION.json']:read(S/'root_correction_checkpoints_20261008'/p)
add=[];new=[]
for c in candidates:
 suffix='room_floor' if 'room' in c['id'] else 'branch_floor';ident=c['programme_key']+'_'+suffix
 spec={'id':ident,'deck':'D12','boundary':c['boundary'],'thickness':.24,'status':'Construction-stage receiving floor; operational acceptance pending','material_role':'guest_floor'}
 assert ident not in {r['id'] for r in layout['regions']};add.append(spec);p=Polygon(spec['boundary']);assert p.is_valid
 for v in layout['voids']:
  if 'D12' in v['decks']:p=p.difference(Polygon(v['boundary']))
 for r in layout['regions']:
  if r['deck']=='D12' and r.get('offset_y',0)==0 and r.get('priority',0)>0:
   q=Polygon(r['boundary'],r.get('holes',[]))
   for v in layout['voids']:
    if 'D12' in v['decks'] and v['id'] not in r.get('void_exemptions',[]):q=q.difference(Polygon(v['boundary']))
   p=p.difference(q)
 new.append({'id':ident,'deck':'D12','floor_y':78,'thickness':.24,'triangles':[[list(v) for v in t.exterior.coords[:3]] for t in constrained_delaunay_triangles(p).geoms],'rings':[[list(v) for v in orient(p,sign=1).exterior.coords[:-1]]],'structural_area_m2':p.area,'render_chunks':[],'status':spec['status'],'material_role':'guest_floor'})
assert len(add)==4
proposed=copy.deepcopy(layout);proposed['regions']+=add
dump(O/'FLOOR_OWNER_ADDITIONS.json',add)
# Independent isolated copies, never symlinks to writable production files.
I.mkdir(parents=True,exist_ok=True)
shutil.copytree(G/'tools',I/'tools',dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__'))
shutil.copytree(G/'data',I/'data',dirs_exist_ok=True)
(I/'docs').mkdir(exist_ok=True)
(I/'assets/models').mkdir(parents=True,exist_ok=True)
pin(G/'assets/models/AST-CUL-005_static_003.glb')
shutil.copyfile(G/'assets/models/AST-CUL-005_static_003.glb',I/'assets/models/AST-CUL-005_static_003.glb')
base=I/'data/architecture/packages/d12_pair_candidate';base.mkdir(parents=True,exist_ok=True)
predecessors={}
for rel in ['data/spatial_layout.json','data/generated/structural_meshes.json','docs/LAYOUT_COMPILE_CHECKS.json']:
 target=base/'predecessors'/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(G/rel,target);predecessors[rel]={'retained_path':str(target.relative_to(I)),'sha256':sha(target)}
proof={'schema':1,'contract_sha256':sha(G/'data/design_contract.json'),'predecessors':predecessors,'new_layout_records':add,'new_expected_compiled_records':new,'scope':'Isolated D12 pair candidate only'}
dump(base/'D12_PAIR_COMPILER_PROOF.json',proof);dump(I/'data/spatial_layout.json',proposed)
p=I/'tools/compile_layout.py';s=p.read_text();start=s.index('outputs=canonicalize_crew_batch_predecessor_chunks');end=s.index("checks={'source_sha256'",start)
block=s[start:end]
# Existing preservation routines receive the exactly pinned 296-owner projection only.
block=block.replace('root,layout,elevations,owned,outputs','root,prior_layout,elevations,prior_owned,prior_outputs',1)
block=block.replace('outputs=canonicalize','prior_outputs=canonicalize',1)
block=block.replace('root,layout,elevations,owned,outputs','root,prior_layout,elevations,prior_owned,prior_outputs',1).replace('outputs,preservation=','prior_outputs,preservation=',1)
block=block.replace('root,layout,elevations,owned,outputs','root,prior_layout,elevations,prior_owned,prior_outputs',1).replace('outputs,medical_preservation','prior_outputs,medical_preservation',1)
intro='from d12_pair_incremental_preservation import prepare_projection, finish_projection\nprior_layout,prior_owned,prior_outputs,d12_new_outputs=prepare_projection(root,layout,elevations,owned,outputs)\n'
finish='outputs,d12_receipt=finish_projection(root,prior_outputs,d12_new_outputs)\n'
s=s[:start]+intro+block+finish+s[end:];s=s.replace("checks['crew_batch_additive_preservation']=crew_batch_preservation","checks['crew_batch_additive_preservation']=crew_batch_preservation\nchecks['d12_pair_additive_preservation']=d12_receipt")
p.write_text(s)
module='''"""Fail-closed four-owner extension; all prior preservation checks remain active."""
import json,hashlib
from shapely.geometry import Polygon
from shapely.ops import unary_union
from theater_incremental_preservation import effective_shapes
PROOF_SHA=PLACEHOLDER

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
'''.replace('PLACEHOLDER',repr(sha(base/'D12_PAIR_COMPILER_PROOF.json')))
(I/'tools/d12_pair_incremental_preservation.py').write_text(module)
# Full manifest exact-ID inspection, no registration/count changes.
ids=[r['catalogue_id'] for r in cat['assets']];assert len(ids)==len(set(ids));guard_id='AST-RCV-D12-PAIR-001';assert guard_id not in ids
dump(O/'CATALOGUE_ID_LOOKUP.json',{'complete_manifest_sha256':sha(R/'BlenderCatalogue/catalogue_manifest.json'),'all_ids':ids,'exact_proposed_id':guard_id,'matches':[r for r in cat['assets'] if r['catalogue_id']==guard_id],'registration_performed':False})
sections=[]
for key,title in [('D12_directory_07','Many worlds gallery'),('D12_directory_08','Reading nooks')]:
 folder=S/'lounge_entry_successors_20261008'/key
 for rel in ['source/section_entry_successor.blend','source/build_section.py','NATIVE_PROOF.json','NATIVE_ASSETS_PROOF.json','RUNTIME_PROOF.json','GEOMETRY_PROOF.json','EXTERIOR_COVERAGE_PROOF.json']:pin(folder/rel)
 glb=pin(folder/'exports'/f'{key}_entry_successor.glb')
 sections.append({'programme':key,'title':title,'root_name':key,'source_local_path':str(glb),'model_file':f'{key}_entry_successor.glb','runtime_sha256':sha(glb),'native_source':str(folder/'source/section_entry_successor.blend'),'transform':{'position':[0,0,0],'rotation':[0,0,0],'scale':[1,1,1]},'source_registry_mutation':False})
dump(O/'runtime_manifest.json',{'schema':1,'root_name':'D12PairReceivingCandidate','operational_acceptance':False,'sections':sections,'guard_asset':{'catalogue_id':guard_id,'model_file':guard_id+'.glb','status':'NOT GENERATED; runtime hash must be pinned after native/export validation'}})
dump(O/'INPUT_PINS.json',pins)
print('prepared',len(add),'additions; isolated compiler ready')
