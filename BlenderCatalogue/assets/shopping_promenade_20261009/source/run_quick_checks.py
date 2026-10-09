from pathlib import Path
import subprocess,json,datetime
P=Path(__file__).resolve().parents[1];G='C:/Users/cered/Dolphin/AstraeaTools/godot.exe';receipt=[]
for name,args in [('import',['--headless','--editor','--path',str(P/'preview'),'--import']),('stationary_construction_checks',['--headless','--path',str(P/'preview'),'--script','res://quick_checks.gd'])]:
 r=subprocess.run([G,*args],capture_output=True,text=True);(P/'qa'/('godot_'+name+'.log')).write_text(r.stdout+r.stderr,encoding='utf-8');errors=[l for l in (r.stdout+r.stderr).splitlines() if 'ERROR:' in l or 'SCRIPT ERROR:' in l];receipt.append({'phase':name,'exit_code':r.returncode,'errors':errors,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()});print(name,r.returncode,'errors',len(errors),flush=True)
 if r.returncode or errors:break
(P/'qa/godot_execution_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');assert all(r['exit_code']==0 and not r['errors'] for r in receipt)
