"""Prepare bounded QA fixture from delivery exports; no full Game/test-copy build."""
from pathlib import Path
import json,shutil
P=Path(__file__).resolve().parents[1];Q=P/'preview';Q.mkdir(exist_ok=True)
plan=json.loads((P/'docs/PLACEMENT_AND_CONNECTORS.json').read_text())
(Q/'placement.json').write_text(json.dumps(plan)+'\n');(Q/'node_policy.json').write_bytes((P/'docs/RUNTIME_NODE_POLICY.json').read_bytes())
for f in (P/'exports').glob('*.glb'):
 t=Q/'exports'/f.name;t.parent.mkdir(exist_ok=True);shutil.copyfile(f,t)
(Q/'project.godot').write_text('; Bounded source-import and contact fixture only\nconfig_version=5\n[application]\nconfig/name="Shopping construction checks"\n[rendering]\nrenderer/rendering_method="gl_compatibility"\nrenderer/rendering_method.mobile="gl_compatibility"\n')
print('PREPARED_QA_EXPORTS',len(list((Q/'exports').glob('*.glb'))))
