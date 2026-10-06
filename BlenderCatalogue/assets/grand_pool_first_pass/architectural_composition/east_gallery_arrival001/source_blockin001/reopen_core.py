"""Fresh-process read-only source reopen, compared exactly to saved build evidence.
Import verify_core_subset() from a combined wrapper without running this script's
core-only whole-scene assertions. No source save/export/render occurs here.
"""
import bpy,json,hashlib,importlib.util
from pathlib import Path
S=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def load_module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

def verify_core_subset(scene,plan,built_plan,material_provenance):
    """Reusable core verification within a combined scene; no total counts."""
    helper=load_module('core_build_helpers_for_reopen',S/'build_core.py')
    checks=load_module('exact_source_roundtrip_checks',S/'source_roundtrip_checks.py')
    actual=helper.snapshot(scene,plan)
    names=[p['name']for p in plan['parts']]
    # First establish byte-value equality with evaluated build evidence. Source
    # plan comparisons cannot substitute for this saved/reopened source gate.
    saved_checks=checks.compare_reopened_parts(actual,built_plan['parts'],names)
    conversion_checks=checks.verify_core_plan_conversion(actual,plan['parts'])
    expected={p['name']:p for p in plan['parts']}
    for p in actual:
        ob=scene.objects[p['name']];r=expected[p['name']]
        assert not ob.modifiers and not ob.constraints and ob.parent is None
        assert len(ob.data.materials)==1 and len(ob.data.uv_layers)==1
        assert helper.mat_state(ob.data.materials[0])==material_provenance[p['material_role']]['material_state']
        assert ob['parent_design_id']=='AST-AQU-016'and not ob['new_floor_owner']
        assert json.loads(ob['support_json'])==r['support']
    return actual,saved_checks,conversion_checks

def main():
    out=S/'build001';receipt=json.loads((out/'qa/BUILD_RECEIPT.json').read_text())
    assert receipt['build_script_sha256']==sha(S/'build_core.py')
    assert receipt['roundtrip_helper_sha256']==sha(S/'source_roundtrip_checks.py')
    path=Path(receipt['source']);assert sha(path)==receipt['source_sha256']
    built_path=out/'qa/BUILD_EVALUATED_PLAN.json';assert sha(built_path)==receipt['evaluated_plan_sha256'];built=json.loads(built_path.read_text())
    plan=json.loads((S/'CORE_PLAN.json').read_text());assert sha(S/'CORE_PLAN.json')==receipt['plan_sha256']
    bpy.ops.wm.open_mainfile(filepath=str(path));scene=bpy.context.scene;scene.view_layers[0].update()
    actual,saved_checks,conversion_checks=verify_core_subset(scene,plan,built,receipt['material_provenance'])
    # These count assertions deliberately belong only to the standalone core
    # entry point. A combined wrapper owns its programme/object/marker counts.
    assert len([o for o in scene.objects if o.type=='MESH'])==len(plan['parts'])
    assert len([o for o in scene.objects if o.type=='EMPTY'])==5
    assert not [o for o in scene.objects if o.type=='LIGHT']
    assert sha(path)==receipt['source_sha256']
    for p,h in receipt['input_sha256'].items():assert sha(p)==h,p
    report_path=out/'qa/INDEPENDENT_REOPEN.json';assert not report_path.exists()
    actual_path=out/'qa/ACTUAL_CORE_PLAN.json';assert not actual_path.exists()
    actual_path.write_text(json.dumps(dict(plan,parts=actual,status='INDEPENDENTLY_REOPENED_CORE_SOURCE'),indent=2)+'\n')
    report=dict(status='PASS_INDEPENDENT_CORE_REOPEN',source=str(path),source_sha256=sha(path),source_unchanged=True,plan_sha256=receipt['plan_sha256'],built_evaluated_plan_sha256=sha(built_path),actual_plan_sha256=sha(actual_path),exact_saved_snapshot_checks=saved_checks,exact_source_conversion_checks=conversion_checks,geometry_contact_tolerance_changed=False,limitations=['Core only; no retained programme, source composition or native integration acceptance.','Run the same pure solid/contact/route review over this actual reopened plan.'])
    report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS_INDEPENDENT_CORE_REOPEN',len(actual),'exact saved snapshots and float32 source conversions; no source save/export/render')
if __name__=='__main__':main()
