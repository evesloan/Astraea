"""Run reviewed exporters to fresh r002 outputs with process-local precise normals.
The originals, rejected exports, saved sources and verification tolerances stay unchanged.
"""
import sys,json,hashlib
from pathlib import Path
sys.dont_write_bytecode=True
S=Path(__file__).resolve().parent;G=Path('/workspace/scratch/375c2e438292/pool-comfort-greenery/greenery');sys.path.insert(0,str(G))
from precise_normal_export import precise_normals
C=Path('/workspace/shared/astraea-catalogue-continuation-20261002/assets/grand_pool_first_pass');E=C/'finish_envelope';M=C/'comfort_greenery/media'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
config=json.loads((S/'EXPORT_R002_INPUTS.json').read_text());report=S/'COMPONENT_EXPORT_R002_RECEIPT.json';assert not report.exists()
completed=[]
with precise_normals() as precision:
 for task in config['tasks']:
  source_script=Path(task['script']);assert sha(source_script)==task['script_sha256'];text=source_script.read_text()
  for old,new in task['literal_replacements']:
   assert text.count(old)==1,(source_script,old);text=text.replace(old,new)
  for p,h in task['preserved'].items():assert sha(Path(p))==h
  for p in task['new_outputs']:assert not Path(p).exists()
  sys.argv=[str(source_script),'--']+task['args'];sys.path.insert(0,str(source_script.parent))
  try:exec(compile(text,str(source_script),'exec'),{'__name__':'__main__','__file__':str(source_script)})
  except SystemExit as e:assert e.code in (None,0)
  for p,h in task['preserved'].items():assert sha(Path(p))==h
  completed.append({'component':task['component'],'outputs':{p:sha(Path(p))for p in task['new_outputs']},'preserved':task['preserved']})
report.write_text(json.dumps({'status':'EXPORTED_R002_PENDING_UNCHANGED_EQUIVALENCE','normal_precision_fix':precision,'input_manifest_sha256':sha(S/'EXPORT_R002_INPUTS.json'),'results':completed},indent=2)+'\n');print('Three new derivative exports created; old exports and all source bytes preserved.')
