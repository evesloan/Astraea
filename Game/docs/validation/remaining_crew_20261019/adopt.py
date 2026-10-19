from pathlib import Path
import json,hashlib,re,shutil
R=Path('/workspace/Astraea');G=R/'Game';W=Path('/workspace/crew-bank-receiving-20261019');D=G/'docs/validation/remaining_crew_20261019';sha=lambda b:hashlib.sha256(b).hexdigest()
assert json.load(open(W/'CANDIDATE_RUNTIME.json'))['status']=='PASS_PHYSICAL_RECEIVING'
p=G/'data/architecture/packages/botanical_pair_runtime/RUNTIME_PROOF.json';proof=json.loads(p.read_text());guard=G/'tests/botanical_pair_successor_guard.gd';s=guard.read_text();h=re.search('const PROOF_SHA := "([0-9a-f]{64})"',s).group(1);assert sha(p.read_bytes())==h and sha(s.replace(h,'<PROOF_SHA>').encode())==proof['normalized_guard_sha256']
gaps=json.load(open(W/'PREEXISTING_GUARD_CHAIN_GAPS.json'))
for q in gaps:
 k=q['file'];assert proof['current_sha256'][k]==sha(q['before'].encode());assert(G/k).read_text()==q['after'];proof['inverse_edits'][k]=[{'before':q['before'],'after':q['after'],'count':1}]+proof['inverse_edits'][k];proof['current_sha256'][k]=sha(q['after'].encode())
ship=G/'scripts/ship.gd';old=ship.read_text();anchor='\tload("res://scripts/mineral_service_20261016/package.gd").build.call_deferred(self)\n';assert old.count(anchor)==1
new=old.replace(anchor,anchor+'\t# Retained anonymous crew source: physical receiving, zero new berth or room identities.\n\tload("res://scripts/group3_remaining_crew_20261019/package.gd").build.call_deferred(self)\n');k='scripts/ship.gd';proof['inverse_edits'][k]=[{'before':old,'after':new,'count':1}]+proof['inverse_edits'][k];proof['current_sha256'][k]=sha(new.encode())
for q in gaps:
 k=q['file'];t=new if k=='scripts/ship.gd' else (G/k).read_text()
 for e in proof['inverse_edits'][k]:assert t.count(e['after'])==e['count'];t=t.replace(e['after'],e['before'])
 assert sha(t.encode())==proof['predecessors'][k]['sha256'],k
pb=(json.dumps(proof,indent=2)+'\n').encode();ship.write_text(new);p.write_bytes(pb);guard.write_text(s.replace(h,sha(pb)))
shutil.copyfile(W/'PREEXISTING_GUARD_CHAIN_GAPS.json',D/'PREEXISTING_GUARD_CHAIN_GAPS.json')
f=G/'tests/validate_remaining_crew_20261019.gd';s=f.read_text();shutil.copyfile(f,D/'validate_candidate.gd.txt');s=s.replace('CANDIDATE_RUNTIME.json','INSTALLED_RUNTIME.json').replace('var old_lights:int=budget.sources.size()','var old_lights:int=budget.sources.size()-549').replace('var bank:Node3D=load("res://scripts/group3_remaining_crew_20261019/package.gd").build(ship);await frames(5)','var bank:Node3D=ship.get_node("ShipSpace/Group3RemainingCrewBank");await frames(5)');f.write_text(s)
print('ADOPTED; three historical proof gaps repaired with exact inverse hashes, normalized guard unchanged')
