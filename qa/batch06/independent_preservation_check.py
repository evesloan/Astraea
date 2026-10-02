"""Check frozen pre-Batch06 assets/materials against their actual git blob bytes."""
from pathlib import Path
import subprocess,hashlib,json
ROOT=Path(__file__).resolve().parents[2]
BASE='fc6ebb39c224b99a447eb83f969893bba9f1dd00'
ALLOWED={'BACKUP_LEDGER.json','README.md','catalogue_manifest.json','standards/source_package_groups.json','tools/source_family_packages.py','tools/package_small_delivery.py','tools/verify_catalogue_restore.py'}
paths=subprocess.check_output(['git','ls-tree','-r','--name-only',BASE],cwd=ROOT,text=True).splitlines()
changed=[];missing=[];checked=0;protected_count=0
for rel in paths:
    p=ROOT/rel;old=subprocess.check_output(['git','rev-parse',BASE+':'+rel],cwd=ROOT,text=True).strip()
    protected=rel.startswith(('assets/','materials/')) or rel in {'standards/materials.py','standards/staff_materials.py','standards/botanical_materials.py','standards/aquatic_materials.py','standards/COORDINATE_CONTRACT.md','standards/coordinate_compatibility.json'}
    protected_count+=protected
    if not p.exists():missing.append({'path':rel,'protected':protected});continue
    new=subprocess.check_output(['git','hash-object',str(p)],cwd=ROOT,text=True).strip();checked+=1
    if old!=new:changed.append({'path':rel,'protected':protected,'allowed_lead_bookkeeping':rel in ALLOWED,'baseline_blob':old,'current_blob':new})
out={'baseline_commit':BASE,'tracked_files_compared':checked,'frozen_asset_material_and_coordinate_files':protected_count,
     'allowed_lead_bookkeeping':sorted(ALLOWED),'changed_prior_files':changed,'missing_prior_files':missing,
     'no_frozen_changes':not missing and not any(c['protected'] for c in changed),
     'all_other_changes_authorized':all(c['allowed_lead_bookkeeping'] for c in changed),
     'scope':'Four lead-owned bookkeeping files and three explicitly authorized packaging-classification tools may evolve for this batch. Prior authored asset bytes, material bytes, and existing coordinate/material helpers remain frozen.'}
(ROOT/'qa/batch06/independent_preservation_report.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
