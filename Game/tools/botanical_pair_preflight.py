"""Fail early before full-world Godot startup when D06 runtime prerequisites are unmet.
An explicit --only import is a preparatory import, never a validation pass.
"""
from pathlib import Path
import hashlib,json,sys,re
RUNTIME_PROOF_REL='data/architecture/packages/botanical_pair_runtime/RUNTIME_PROOF.json'
RUNTIME_GUARD_REL='tests/botanical_pair_successor_guard.gd'
# Read the sealed guard pin; no duplicate literal that creates a proof hash cycle.

def blockers(root):
 root=Path(root);reasons=[];proofpath=root/RUNTIME_PROOF_REL
 guardpath=root/RUNTIME_GUARD_REL
 guard_text=guardpath.read_text() if guardpath.is_file() else ''
 pins=re.findall(r'const PROOF_SHA := "([0-9a-f]{64})"',guard_text)
 if len(pins)!=1:reasons.append('D06 runtime successor guard has no unique verified proof pin')
 if not proofpath.is_file():reasons.append('D06 runtime successor proof is missing')
 if reasons:return reasons
 if hashlib.sha256(proofpath.read_bytes()).hexdigest()!=pins[0]:return ['D06 runtime successor proof hash mismatch']
 proof=json.loads(proofpath.read_text())
 if guard_text.count(pins[0])!=1 or hashlib.sha256(guard_text.replace(pins[0],'<PROOF_SHA>').encode()).hexdigest()!=proof.get('normalized_guard_sha256'):return ['D06 normalized runtime guard source mismatch']
 if proof.get('schema')!=1 or proof.get('predecessor_compiled_owners')!=300 or proof.get('current_compiled_owners')!=303:return ['D06 successor scope is not exactly 300 plus 3 owners']
 for gate in ['source_delta_verified','import_identity_maps_verified','source_import_contact_parity_verified','exact_predecessor_projection_wiring_verified','botanical_access_fixture_successor_prepared','moss_port_state_successor_verified']:
  if proof.get(gate) is not True:reasons.append('Missing prerequisite: '+gate)
 for rel,row in proof.get('current_sha256',{}).items():
  p=root/rel
  if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=row:reasons.append('Unverified current file: '+rel)
 required={'scripts/botanical_pair_receiving.gd','tests/d12_pair_successor_guard.gd','tests/medical_triage_successor_guard.gd','tests/validate_botanical_receiving_access.gd','data/spatial_layout.json','data/generated/structural_meshes.json','docs/LAYOUT_COMPILE_CHECKS.json','scripts/ship.gd','data/architecture/botanical_pair/runtime_manifest.json','assets/models/AST-ATR-001_botanical_nursery_open001.glb.import','assets/models/AST-RCV-D06-CLOUD-LINK-001.glb.import'}
 for rel in sorted(required-set(proof.get('current_sha256',{}))):reasons.append('Required proof input absent: '+rel)
 manifest_path=root/'data/architecture/botanical_pair/runtime_manifest.json'
 if not manifest_path.is_file():reasons.append('D06 runtime manifest missing')
 else:
  manifest=json.loads(manifest_path.read_text())
  if manifest.get('activation_ready') is not True:reasons.append('D06 receiving activation prerequisites not complete')
 for name in ['AST-ATR-001_botanical_nursery_open001.glb','AST-RCV-D06-CLOUD-LINK-001.glb']:
  p=root/'assets/models'/(name+'.import')
  if not p.is_file():reasons.append('Missing asset-specific importer settings: '+name)
  elif 'meshes/force_disable_compression=true' not in p.read_text():reasons.append('Exact contact compression setting missing: '+name)
 return reasons

def enforce(root,argv):
 if '--only' in argv and argv.index('--only')+1<len(argv) and argv[argv.index('--only')+1]=='import':return
 reasons=blockers(root)
 if reasons:
  print(json.dumps({'status':'BLOCKED_BEFORE_ENGINE','scope':'Botanical pair successor preflight only; no Godot validation ran','blockers':reasons},indent=2))
  raise SystemExit(2)

if __name__=='__main__':enforce(Path(__file__).resolve().parents[1],sys.argv[1:])
