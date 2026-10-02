"""Read-only check against the immutable accepted Batch07 Git tree."""
import hashlib,json,subprocess
from pathlib import Path
BASE=Path(__file__).resolve().parents[1];CAT=BASE.parents[2];COMMIT='66dcaf10f105958c5cadb421d5aca15b054b98ed';files=[]
for family in('utility_pipework','utility_machines','utility_console'):
 folder=CAT/'assets'/family
 files+=list((folder/'source').glob('*.blend'))+list((folder/'exports').glob('*.glb'))+list((folder/'source').glob('*.py'))
files += [CAT/'standards'/f for f in('utility_ports.py','utility_port_spec.json','staff_materials.py')]
rows=[]
for path in sorted(files):
 rel=str(path.relative_to(CAT));old=subprocess.check_output(['git','show',COMMIT+':'+rel],cwd=CAT);oldhash=hashlib.sha256(old).hexdigest();nowhash=hashlib.sha256(path.read_bytes()).hexdigest();rows.append({'path':rel,'accepted_sha256':oldhash,'current_sha256':nowhash,'unchanged':oldhash==nowhash})
out={'accepted_commit':COMMIT,'scope':'Six original utility master Blender and GLB files, their original source generators and original port/spec/material helpers','results':rows,'all_unchanged':all(r['unchanged']for r in rows)};(BASE/'qa/original_preservation.json').write_text(json.dumps(out,indent=2)+'\n');print('ORIGINAL_UTILITY_PRESERVATION',out['all_unchanged']);assert out['all_unchanged']
