"""UNRUN adapter: append the standalone court to a new review scene only.
Never rebuilds/re-exports the theater or chairs. Default mode prints the plan.
"""
from pathlib import Path
import sys,json,hashlib
R=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text())

def compose():
 gate=read(R/'PARENT_SOURCE_BUILD_GATE.json')
 assert gate['parent_authorized_scratch_source_job'] and gate['source_job_slot_granted']
 c=read(R/'COURT_A_GEOMETRY_CONTRACT.json');base=Path(c['base_source'])
 build=read(R/'authored_preview001/BUILD_REPORT.json');source=Path(build['source'])
 reopen=read(R/'authored_preview001/REOPEN_REPORT.json')
 assert reopen['status']=='PASS_SOURCE_ONLY' and reopen['source_sha256']==sha(source)==build['sha256']
 assert sha(base)==c['base_source_sha256']
 output=R/'authored_preview001/AST-CUL-005_court_A_composed_review_004.blend'
 report=R/'authored_preview001/COMPOSITION_REPORT.json'
 assert not output.exists() and not report.exists()
 import bpy
 sys.path.insert(0,str(base.parents[2]/'firstpass_001'))
 # Explicit retained helper path, not a new whole-room generator.
 sys.path.insert(0,'/workspace/shared/astraea-catalogue-continuation-20261002/assets/grand_lantern_theater_section/source/firstpass_001')
 from firstpass_common import baseline_snapshot,compare_subset
 bpy.ops.wm.open_mainfile(filepath=str(base))
 before=baseline_snapshot(bpy)
 chair_ids=sorted(o.name for o in bpy.context.scene.objects if o.get('existing_family')=='AST-CUL-003')
 assert len(chair_ids)==2200
 with bpy.data.libraries.load(str(source),link=False)as(src,dst):
  assert'A4_COMPLETED_COURT'in src.collections;dst.collections=['A4_COMPLETED_COURT']
 addition=dst.collections[0];bpy.context.scene.collection.children.link(addition)
 errors=compare_subset(before,baseline_snapshot(bpy));assert not errors,errors[:10]
 assert chair_ids==sorted(o.name for o in bpy.context.scene.objects if o.get('existing_family')=='AST-CUL-003')
 bpy.context.preferences.filepaths.save_version=0
 bpy.ops.wm.save_as_mainfile(filepath=str(output),compress=True)
 assert sha(base)==c['base_source_sha256'] and sha(source)==build['sha256']
 report.write_text(json.dumps({'status':'SCRATCH_COMPOSITION_ONLY_VISUAL_REVIEW_PENDING','source':str(output),'sha256':sha(output),'base_source_sha256':sha(base),'standalone_source_sha256':sha(source),'preserved_chairs':len(chair_ids),'old_snapshot_exact':not errors,'existing_lights_cameras_exposure_unchanged':True,'exported_or_installed':False},indent=2)+'\n')

if __name__=='__main__':
 if'--compose'in sys.argv:compose()
 else:print('UNRUN: append A4_COMPLETED_COURT only after parent-coordinated build and independent source reopen; save a new scratch review .blend. No GLB export or Game changes.')
