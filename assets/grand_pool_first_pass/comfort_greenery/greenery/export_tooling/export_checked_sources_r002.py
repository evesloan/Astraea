"""New exports_r002 only: source-faithful export-side normal precision fix."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import json,datetime,traceback
from export_gate import read_gate,sha,source_unchanged
from export_checked_sources import export_one
from precise_normal_export import precise_normals
def main():
    g,plan,qa,source_qa,package,candidate=read_gate();dest=candidate/'qa/EXPORT_RECEIPT_r002_all.json';assert not dest.exists();old={str(candidate/a['export']):sha(candidate/a['export']) for a in plan['assets']};assets=[]
    for original in plan['assets']:
        a=dict(original);a['export']='exports_r002/'+Path(original['export']).name;assert not (candidate/a['export']).exists(),'Preserve previous revision output';assets.append(a)
    completed=[];precision=None
    try:
        # Process-local variable, restored even on error; installed files,
        # source meshes, materials, geometry and verifier tolerances unchanged.
        with precise_normals() as precision:
            for a in assets:
                completed.append(export_one(a,g,source_qa[a['name']],package,candidate));print('GREENERY_R002_EXPORTED',a['name'],flush=True)
        for p,h in old.items():assert sha(p)==h,'Earlier failed export changed'
        source_unchanged(g,qa);read_gate();dest.write_text(json.dumps(dict(status='EXPORTED_R002_PENDING_UNCHANGED_INDEPENDENT_KEEPER',contract_sha256=g['contract_sha256'],normal_precision_fix=precision,fix_input_sha256=sha(Path(__file__).resolve().parent/'NORMAL_PRECISION_FIX_INPUTS.json'),preserved_failed_exports=old,outputs=completed,source_hashes_unchanged=True,source_rebuild=False),indent=2)+'\n')
    except Exception:
        stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ');failure=candidate/'qa'/('EXPORT_R002_FAILURE_'+stamp+'.json');failure.write_text(json.dumps(dict(status='FAILED_PRESERVE_ALL_OUTPUTS',completed=completed,normal_precision_fix=precision,preserved_failed_exports=old,traceback=traceback.format_exc()),indent=2)+'\n');raise
if __name__=='__main__':main()
