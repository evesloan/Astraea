"""Reuse existing read-only Blender inspector; isolate new reports to batch03."""
from pathlib import Path
import hashlib,json,sys,runpy
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'qa/batch03'
files=[p for family in ['wall','overhead','workbay'] for p in (ROOT/'assets'/('staff_'+family)).rglob('*.blend')]
before={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
for family in ['wall','overhead','workbay']:
 sys.argv=['inspect_blend_independent.py','--',str(ROOT/'assets'/('staff_'+family)),str(OUT/('independent_'+family+'_blend_report.json'))]
 runpy.run_path(str(ROOT/'qa/inspect_blend_independent.py'),run_name='__main__')
after={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
(OUT/'independent_source_reload_stability.json').write_text(json.dumps({'before':before,'after':after,'unchanged':before==after,'scope':'Source file hashes around read-only load; any author change invalidates only affected source checks.'},indent=2)+'\n')
