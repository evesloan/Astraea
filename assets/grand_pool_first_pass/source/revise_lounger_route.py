"""Move seven existing lounger instances west by 0.5m; preserve original route."""
import bpy,json,hashlib,shutil
from pathlib import Path
HERE=Path(__file__).resolve().parents[1]
f=HERE/'source/grand_pool_first_pass_editable_corrected.blend';prior=HERE/'source/grand_pool_first_pass_transform_repaired_only.blend'
assert not prior.exists(),'Never overwrite retained pre-route-revision source'
assert hashlib.sha256(f.read_bytes()).hexdigest()=='5c2b0f758ea13709591de16fc0e710c62f3eaf80154b3f5f3f6ca53a84e4b31e'
shutil.copy2(f,prior);assert hashlib.sha256(prior.read_bytes()).hexdigest()==hashlib.sha256(f.read_bytes()).hexdigest()
c=json.loads((HERE/'source/placement_contract.json').read_text());assert not c['issues']
bpy.ops.wm.open_mainfile(filepath=str(f));bpy.context.view_layer.update();changed=[]
for it in c['placements']:
 if it['asset']!='lounger':continue
 assert it['position_xyz'][0]==-47.5
 coll=bpy.data.collections[it['name']]
 for ob in coll.objects:ob.location.x-=.5
 changed.append(it['name'])
assert len(changed)==7;bpy.context.view_layer.update();bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(f))
report=dict(status='source_shift_saved_pending_independent_QA',reason='Preserve the retained actual X-45.9 walking route with its 0.3m capsule; original 6cm visual clearance was insufficient',prior_source=str(prior.relative_to(HERE)),prior_sha256=hashlib.sha256(prior.read_bytes()).hexdigest(),corrected_source=str(f.relative_to(HERE)),corrected_sha256=hashlib.sha256(f.read_bytes()).hexdigest(),placements_changed=changed,translation_xyz=[-.5,0,0],unchanged='All other placement transforms, meshes, source materials, original inputs and live game')
(HERE/'qa/lounger_route_revision.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
