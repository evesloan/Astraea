"""Wait explicitly for pinned Windows Godot, including GUI-binary headless child completion."""
from pathlib import Path
import subprocess,sys,json,shutil,struct
P=Path(__file__).resolve().parents[1]
exe=sys.argv[1] if len(sys.argv)>1 else r'C:\Users\cered\Dolphin\AstraeaTools\godot.exe'
V=P/'preview';(V/'models').mkdir(exist_ok=True)
for name in ['AQD_architecture.glb','AQD_floor_proposals.glb']:shutil.copyfile(P/'exports'/name,V/'models'/name)
shutil.copyfile(P/'docs/AQUATIC_CONSTRUCTION_PLAN.json',V/'plan.json');shutil.copyfile(P/'source/check_preview.gd',V/'check_preview.gd')
policy={}
for name in ['AQD_architecture.glb','AQD_floor_proposals.glb']:
 b=(P/'exports'/name).read_bytes();n=struct.unpack_from('<I',b,12)[0];d=json.loads(b[20:20+n])
 for q in d['nodes']:
  if 'mesh' in q:
   kind=q.get('extras',{}).get('kind');assert kind,q.get('name');policy[q['name']]=kind;policy[q['name'].replace('.','_')]=kind
(V/'collision_policy.json').write_text(json.dumps(policy,indent=2))
rows=[]
for phase,args in [('import',['--headless','--editor','--path',str(V),'--quit']),('quick_checks',['--headless','--path',str(V),'--script','res://check_preview.gd'])]:
 r=subprocess.run([exe,*args],capture_output=True,text=True,timeout=120)
 (P/'qa'/('godot_'+phase+'.log')).write_text(r.stdout+'\n'+r.stderr)
 rows.append({'phase':phase,'exit_code':r.returncode,'errors':[a for a in (r.stdout+r.stderr).splitlines() if 'ERROR:' in a or 'SCRIPT ERROR:' in a]})
 (P/'qa/godot_execution_receipt.json').write_text(json.dumps(rows,indent=2))
 print(phase,r.returncode,rows[-1]['errors'])
 assert r.returncode==0 and not rows[-1]['errors'],phase
