"""Apply the original strict independent keeper to exports_r002; no relaxation."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import json,datetime,traceback,importlib.util
from export_gate import read_gate,sha,source_unchanged,CAT
from verify_exported_sources import verify_one,runtime_fragment
def main():
    g,plan,qa,source_qa,package,candidate=read_gate();receipt=candidate/'qa/GLB_EQUIVALENCE_r002_all.json';fragment=candidate/'qa/GREENERY_RUNTIME_FRAGMENT_r002_all.json';assert not receipt.exists() and not fragment.exists();export_receipt=candidate/'qa/EXPORT_RECEIPT_r002_all.json';er=json.loads(export_receipt.read_text());assert er['normal_precision_fix']['normal_rounding_decimal_digits']==8;assert len(er['outputs'])==23
    for p,h in er['preserved_failed_exports'].items():assert sha(p)==h
    pins=json.loads((package/'INPUT_PINS.json').read_text());specs=pins['material_spec']['materials'];reader_path=CAT/'assets/grand_pool_first_pass/finish_envelope/stock/geometry.py';sp=importlib.util.spec_from_file_location('retained_geometry_reader',reader_path);reader=importlib.util.module_from_spec(sp);sp.loader.exec_module(reader);results=[]
    try:
        for original in plan['assets']:
            a=dict(original);a['export']='exports_r002/'+Path(original['export']).name;results.append(verify_one(a,source_qa[a['name']],g,package,candidate,specs,reader));print('GREENERY_R002_STRICT_EQUIVALENCE',a['name'],flush=True)
        for p,h in er['preserved_failed_exports'].items():assert sha(p)==h
        source_unchanged(g,qa);read_gate();report=dict(status='PASS_ACTUAL_GLB_SOURCE_EQUIVALENCE',revision='r002_export_normal_precision',asset_count=len(results),contract_sha256=g['contract_sha256'],export_receipt_sha256=sha(export_receipt),position_tolerance_m=2e-6,corner_uv_tolerance=2e-6,normal_tolerance=2e-6,keeper_relaxation=False,all_original_source_hashes_unchanged=True,all_first_exports_preserved=True,assets=results,engine_adoption_and_visual_review='NOT_RUN');receipt.write_text(json.dumps(report,indent=2)+'\n');fragment.write_text(json.dumps(runtime_fragment(plan,results,g),indent=2)+'\n')
    except Exception:
        stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ');failure=candidate/'qa'/('GLB_EQUIVALENCE_R002_FAILURE_'+stamp+'.json');failure.write_text(json.dumps(dict(status='FAILED_PRESERVE_ALL_OUTPUTS',verified_assets=results,traceback=traceback.format_exc()),indent=2)+'\n');raise
if __name__=='__main__':main()
