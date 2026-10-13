from pathlib import Path
import json,subprocess,hashlib,zipfile
P=Path(__file__).parent;R=Path('/workspace/astraea-protected-integration-20261012');G=R/'Game';T=P/'import/Game';T.mkdir(parents=True,exist_ok=True);d=json.loads((P/'PRIVATE.json').read_text());S='/workspace/astraea-readonly-interface-review-20261012/remote_only_20261012T000749Z.git';rev='6f2d0da67429ea940edf7011348ec08a346f37db';sha=lambda b:hashlib.sha256(b).hexdigest()
proof=json.loads((G/'data/architecture/packages/botanical_pair_runtime/RUNTIME_PROOF.json').read_text())
for row in json.loads((P/'CURRENT_PREFLIGHT.json').read_text())['source_pins']:
 if row['original_sha256']==row['current_sha256']:continue
 path=row['path'];a=json.loads((P/'pinned_inputs'/path).read_text());b=(R/path).read_bytes()
 if path.endswith('/structural_meshes.json'):
  z=json.loads(b);assert len(a['regions'])==len(z['regions'])==303;assert set(x['id']for x,y in zip(a['regions'],z['regions'])if x!=y)=={'D09_fore_route','D09_aft_route','D09_atrium_circulation'};assert all(a[k]==z[k]for k in a if k!='regions')
 else:
  key=path[5:];assert proof['current_sha256'][key]==sha(b);s=b.decode();found=False
  for e in proof['inverse_edits'][key]:assert s.count(e['after'])==e['count'];s=s.replace(e['after'],e['before']);found=found or sha(s.encode())==row['original_sha256']
  assert found,path
for name,h in d['model_pins'].items():
 src=P/'inputs/BlenderCatalogue/assets/group3_crew_service_20261009/extensions/starboard3_private_landings_batch019/exports'/name;assert sha(src.read_bytes())==h;q=T/'assets/models/group3_starboard3_private_20261011'/name;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(src.read_bytes())
original=(P/'physical_package.gd').read_text();(P/'OWNER_PACKAGE.gd.txt').write_text(original)
code=original.replace(' var p:Dictionary=', ' assert(resolved_identities.is_empty()and not staff_authorization.is_valid(),"Private operation requires separate authoritative admission")\n var p:Dictionary=',1)
code=code.replace(' var n:=Node3D.new();', ' for file in p.model_pins:\n  assert(FileAccess.get_sha256("res://assets/models/group3_starboard3_private_20261011/"+str(file))==str(p.model_pins[file]))\n  assert(load("res://assets/models/group3_starboard3_private_20261011/"+str(file)) is PackedScene)\n var n:=Node3D.new();',1)
code=code.replace('n.set_meta("clinical_operational_acceptance",false)','n.set_meta("clinical_operational_acceptance",false);n.set_meta("default_main_adoption",false);n.set_meta("operating_lift_or_private_gates",false)')
code=code.replace('l.shadow_enabled=true;l.set_meta','l.visible=false;l.shadow_enabled=false;l.set_meta')
for rel,b in {'scripts/group3_starboard3_private_20261011/physical_package.gd':code.encode(),'data/architecture/group3_starboard3_private_20261011/PRIVATE.json':(P/'PRIVATE.json').read_bytes()}.items():q=T/rel;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(b)
for name in ['physical_package.gd.uid']:
 b=subprocess.check_output(['git','-C',S,'show',rev+':Game/scripts/group3_starboard3_private_20261011/'+name]);(T/'scripts/group3_starboard3_private_20261011'/name).write_bytes(b)
(T/'project.godot').write_text('[application]\nconfig/name="Starboard3 exact source import"\n[rendering]\nrenderer/rendering_method="gl_compatibility"\nrenderer/rendering_method.mobile="gl_compatibility"\n')
print('PASS_PIN_SUCCESSORS_CANDIDATE_STAGED_NO_OPERATION')
