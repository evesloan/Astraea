"""Read-only source proof execution and adversarial fixtures. Never a Godot substitute."""
from pathlib import Path
import json,hashlib,re,copy,collections,sys
R=Path(__file__).resolve().parent;C=R/'candidate/Game';G=Path('/workspace/shared/Astraea_recovery_20261007_AXWr5x/Game')
sha=lambda b:hashlib.sha256(b).hexdigest();encode=lambda o:(json.dumps(o,indent=2)+'\n').encode()
PROOF='data/architecture/packages/botanical_court/BOTANICAL_RUNTIME_PROOF.json';GUARD='tests/medical_triage_successor_guard.gd'
def reader(overrides=None):
 overrides=overrides or {}
 def read(p):return overrides[p] if p in overrides else ((C/p).read_bytes() if (C/p).exists() else (G/p).read_bytes())
 return read

def check_records(proof,layout,compiled,summary,pre):
 for new,old,adds in [(layout,json.loads(pre['data/spatial_layout.json']),proof['added_layout_records']),(compiled,json.loads(pre['data/generated/structural_meshes.json']),proof['added_compiled_records'])]:
  assert new['regions']==old['regions']+adds,'Complete old records/order plus exactly two additions'
  assert len({r['id'] for r in new['regions']})==len(new['regions']),'Duplicate owner'
 assert {k:v for k,v in layout.items() if k!='regions'}=={k:v for k,v in json.loads(pre['data/spatial_layout.json']).items() if k!='regions'},'Globals/voids changed'
 assert summary==compiled['source_checks']==proof['compile_summary'],'Summary/current checks mismatch'
 assert len(compiled['regions'])==275
 for r in proof['added_compiled_records']:assert r['deck']=='D06' and r['floor_y']==27 and r['thickness']==.24 and r['structural_area_m2']==120

def authenticate(overrides=None):
 read=reader(overrides);source=read(GUARD).decode();ph=re.search(r'const BOTANICAL_PROOF_SHA := "([a-f0-9]{64})"',source).group(1);assert sha(read(PROOF))==ph,'Proof digest';proof=json.loads(read(PROOF))
 for p,h in proof['current_sha256'].items():assert sha(read(p))==h,'Current input '+p
 pre={}
 for p,spec in proof['predecessors'].items():assert sha(read(spec['retained_path']))==spec['sha256'],'Predecessor '+p;pre[p]=read(spec['retained_path']).decode()
 begin='# BOTANICAL_EXACT_SECTION_BEGIN\n';end='# BOTANICAL_EXACT_SECTION_END\n';assert source.count(begin)==source.count(end)==1;start=source.index(begin);finish=source.index(end)+len(end);block=source[start:finish];assert block.count(ph)==1;assert sha(block.replace(ph,'<PROOF_SHA>').encode())==proof['integration_block_normalized_sha256'],'Integrated logic changed'
 restored=source[:start]+source[finish:]
 for e in proof['consumer_inverse_edits']:assert restored.count(e['after'])==e['count'];restored=restored.replace(e['after'],e['before'])
 assert restored==pre[GUARD],'Original consumer bytes changed'
 for p,edits in proof['exact_inverse_edits'].items():
  restored=read(p).decode()
  for e in edits:assert restored.count(e['after'])==e['count'];restored=restored.replace(e['after'],e['before'])
  assert restored==pre[p],'Compiler/ship inverse'
 layout=json.loads(read('data/spatial_layout.json'));compiled=json.loads(read('data/generated/structural_meshes.json'));summary=json.loads(read('docs/LAYOUT_COMPILE_CHECKS.json'));check_records(proof,layout,compiled,summary,pre)
 return proof,pre,read

def verify_predecessor_chain(proof,pre,read):
 def botanical(p):return pre[p] if p in proof['projected_paths'] else read(p).decode()
 finish=json.loads(read('docs/GRAND_POOL_CONNECTED_FINISH_SUCCESSOR.json'))
 for p,h in finish['required_new_files'].items():assert sha(read(p))==h,p
 for p,row in finish['files'].items():assert sha(read(p))==row['after_sha256'],p
 pool_path='tests/grand_pool_feature_builder_successor.gd';row=finish['files'][pool_path];text=read(pool_path).decode()
 for e in reversed(row['inverse']):
  start=e['after_start'];assert text[start:start+len(e['after'])]==e['after'];text=text[:start]+e['before']+text[start+len(e['after']):]
 assert sha(text.encode())==row['before_sha256']
 def composed(p):return text if p==pool_path else botanical(p)
 triage=json.loads(read('docs/MEDICAL_TRIAGE_ADDITIVE_SUCCESSOR.json'));old={}
 for p,h in triage['postimage_sha256'].items():
  data=composed(p).encode() if p in proof['projected_paths'] or p==pool_path else read(p)
  assert sha(data)==h,('Retained triage pin',p)
 for p,spec in triage['predecessors'].items():assert sha(read(spec['retained_path']))==spec['sha256'];old[p]=read(spec['retained_path']).decode()
 for p,edits in triage['exact_patch_reversals'].items():
  restored=composed(p)
  for e in reversed(edits):assert restored.count(e['after'])==e['count'];restored=restored.replace(e['after'],e['before'])
  assert restored==old[p],('Triage inverse',p)
 def triage_text(p):return old[p] if p in old else composed(p)
 # Execute current medical consumer's exact D11 input mapping after triage/pool projection.
 medsrc=read('tests/medical_successor_guard.gd').decode();d11=json.loads(medsrc.split('const D11_ENTRY_MEDICAL_INPUTS := ',1)[1].split('\n\nstatic func _d11_entry_medical_text',1)[0])
 def medical_input(p):
  s=triage_text(p)
  if p not in d11:return s
  spec=d11[p]
  if sha(s.encode())==spec['preimage_sha256']:return s
  assert sha(s.encode())==spec['candidate_sha256'],('D11 candidate',p)
  for e in reversed(spec['reversals']):assert s.count(e['after'])==e['count'];s=s.replace(e['after'],e['before'])
  assert sha(s.encode())==spec['preimage_sha256'];return s
 med=json.loads(read('docs/MEDICAL_ADDITIVE_SUCCESSOR.json'));medold={}
 for p,h in med['postimage_sha256'].items():
  if p in old or p in proof['projected_paths'] or p==pool_path or p in d11:data=medical_input(p).encode()
  else:data=read(p)
  assert sha(data)==h,('Retained medical pin',p)
 for p,spec in med['predecessors'].items():assert sha(read(spec['retained_path']))==spec['sha256'];medold[p]=read(spec['retained_path']).decode()
 for p,edits in med['exact_patch_reversals'].items():
  s=medical_input(p)
  for e in reversed(edits):assert s.count(e['after'])==e['count'];s=s.replace(e['after'],e['before'])
  assert sha(s.encode())==med['predecessors'][p]['sha256'],('Medical inverse',p)
 assert len(json.loads(old['data/generated/structural_meshes.json'])['regions'])==272
 assert len(json.loads(medold['data/generated/structural_meshes.json'])['regions'])==271
 return {'pool_finish_current_inputs':len(finish['required_new_files'])+len(finish['files']),'triage_postimage_pins':len(triage['postimage_sha256']),'triage_exact_inverse_files':len(triage['exact_patch_reversals']),'medical_postimage_pins':len(med['postimage_sha256']),'medical_exact_inverse_files':len(med['exact_patch_reversals']),'complete_compiled_projection_counts':[275,273,272,271]}

def main():
 proof,pre,read=authenticate();chain=verify_predecessor_chain(proof,pre,read);tests=[]
 def reject(name,fn):
  try:fn()
  except (AssertionError,KeyError,ValueError,IndexError) as e:tests.append({'case':name,'rejected':True,'reason':str(e)[:200]});return
  raise AssertionError('Mutation accepted: '+name)
 paths={'modified_old_geometry':'data/generated/structural_meshes.json','missing_owner':'data/generated/structural_meshes.json','extra_unknown_owner':'data/generated/structural_meshes.json','duplicate_owner':'data/generated/structural_meshes.json','modified_new_geometry':'data/generated/structural_meshes.json','altered_void':'data/spatial_layout.json','guard_export_changed':'assets/models/'+proof['guard_file'],'compiler_changed':'tools/compile_layout.py','ship_extra_call':'scripts/ship.gd','old_consumer_assertion_removed':GUARD,'integrated_logic_modified':GUARD,'predecessor_changed':proof['predecessors']['data/spatial_layout.json']['retained_path'],'pool_helper_changed':'tests/grand_pool_feature_builder_successor.gd','summary_changed':'docs/LAYOUT_COMPILE_CHECKS.json'}
 for name,path in paths.items():
  b=read(path)
  if path.endswith('.json'):
   d=json.loads(b)
   if name=='modified_old_geometry':d['regions'][0]['triangles'][0][0][0]+=.05
   elif name=='missing_owner':d['regions'].pop(0)
   elif name=='extra_unknown_owner':r=copy.deepcopy(d['regions'][0]);r['id']='UNKNOWN';d['regions'].append(r)
   elif name=='duplicate_owner':d['regions'].append(copy.deepcopy(d['regions'][-1]))
   elif name=='modified_new_geometry':d['regions'][-1]['floor_y']+=.1
   elif name=='altered_void':d['voids'][0]['boundary'][0][0]+=.1
   else:d['tampered']=True
   b=encode(d)
  elif name=='old_consumer_assertion_removed':b=b.replace(b'assert(proof.schema==1 and proof.owner_id==OWNER)',b'assert(true)',1)
  elif name=='integrated_logic_modified':b=b.replace(b'assert(seen.size()==275 and retained.size()==273)',b'assert(true)',1)
  else:b+=b'\nTAMPER'
  reject(name,lambda p=path,v=b:authenticate({p:v}))
 # Independent structural mutations with signature checking intentionally out of the fixture,
 # proving record/cardinality invariants themselves reject additions and geometry changes.
 L=json.loads(read('data/spatial_layout.json'));K=json.loads(read('data/generated/structural_meshes.json'));S=json.loads(read('docs/LAYOUT_COMPILE_CHECKS.json'))
 for name in ['old_geometry','new_geometry','missing','extra','order','void','summary']:
  l,k,s=copy.deepcopy(L),copy.deepcopy(K),copy.deepcopy(S)
  if name=='old_geometry':k['regions'][0]['triangles'][0][0][0]+=.01
  elif name=='new_geometry':k['regions'][-1]['thickness']=.3
  elif name=='missing':k['regions'].pop(0)
  elif name=='extra':k['regions'].append(copy.deepcopy(k['regions'][-1]))
  elif name=='order':k['regions'][0],k['regions'][1]=k['regions'][1],k['regions'][0]
  elif name=='void':l['voids'][0]['boundary'][0][0]+=.1
  elif name=='summary':s['regions']+=1
  reject('structural_'+name,lambda l=l,k=k,s=s:check_records(proof,l,k,s,pre))
 # Roster model tests supplement, but never claim to execute the Godot geometry code.
 expected={r['id']:r for r in K['regions']}
 def roster(rows):
  assert len(rows)==275
  seen=set()
  for row in rows:
   assert row['id'] in expected and row['id'] not in seen;seen.add(row['id']);assert row==expected[row['id']]
  assert len(seen)==275
  result=[r for r in rows if r['id'] not in proof['added_owner_ids']];assert result==json.loads(pre['data/generated/structural_meshes.json'])['regions']
 roster(K['regions'])
 for name in ['unknown','missing','old_mutation','new_mutation']:
  rows=copy.deepcopy(K['regions'])
  if name=='unknown':rows[-1]['id']='UNKNOWN'
  elif name=='missing':rows.pop(5)
  elif name=='old_mutation':rows[0]['triangles'][0][0][0]+=.1
  else:rows[-1]['floor_y']+=.1
  reject('roster_model_'+name,lambda r=rows:roster(r))
 result={'status':'PASS: source proof and adversarial fixtures; Godot runtime assertions NOT EXECUTED','chain':chain,'adversarial_cases':tests,'adversarial_count':len(tests),'one_existing_consumer_extended':GUARD,'new_adapter_scripts':0,'unmodified_substantive_assertions':'Complete original consumer byte recovery verified; existing floor/contact/route scripts unchanged.','runtime_limits':['Syntax parse is separate from Godot type checking.','Full 275-owner live render/native collision checks and guard import/hierarchy checks are authored but unrun.','Current source-only roster model does not prove engine shape codec behavior, visual quality or actual traversal.']}
 (R/'SOURCE_TEST_RESULTS.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
