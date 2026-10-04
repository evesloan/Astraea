"""Read source .blend files without save/render; records editable semantic geometry."""
from pathlib import Path
import hashlib,json,sys,runpy
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch04'
folders=['botanical_canopy','botanical_understory','botanical_planter']
files=[p for f in folders for p in (ROOT/'assets'/f).rglob('*.blend')]
before={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
for family in folders:
 sys.argv=['inspect_blend_independent.py','--',str(ROOT/'assets'/family),str(OUT/('independent_'+family+'_blend_report.json'))]
 runpy.run_path(str(ROOT/'qa/inspect_blend_independent.py'),run_name='__main__')
after={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
(OUT/'independent_source_reload_stability.json').write_text(json.dumps({'before':before,'after':after,'unchanged':before==after,'scope':'Source file hashes around read-only load; author changes invalidate only affected source checks.'},indent=2)+'\n')
