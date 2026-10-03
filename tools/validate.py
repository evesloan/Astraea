"""Run bounded Godot checks; a printed PASS never overrides an engine/script error."""
import os, pathlib, subprocess, json, sys
root=pathlib.Path(__file__).resolve().parents[1]
state=root/'.godot'/'validation_state'
env=os.environ.copy()
for key,sub in [('XDG_CONFIG_HOME','config'),('XDG_DATA_HOME','data'),('XDG_CACHE_HOME','cache')]:
    p=state/sub;p.mkdir(parents=True,exist_ok=True);env[key]=str(p)
results=[]
commands=[('import',['--editor','--quit']),('baseline',['--script','res://tests/validate_baseline.gd']),('world',['--script','res://tests/validate_world.gd']),('stairs',['--script','res://tests/validate_stairs.gd'])]
for label,args in commands:
    process=subprocess.run(['godot','--headless','--path',str(root),'--quit-after','2400',*args],env=env,capture_output=True,text=True,timeout=90)
    output=process.stdout+process.stderr
    errors=[line for line in output.splitlines() if 'ERROR:' in line or 'Assertion failed' in line or 'Parse Error' in line]
    passed=process.returncode==0 and not errors and (label=='import' or 'PASS:' in output)
    results.append({'check':label,'passed':passed,'exit_code':process.returncode,'errors':errors})
    print(output)
    if not passed: break
(root/'artifacts').mkdir(exist_ok=True)
(root/'artifacts'/'validation.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps(results))
sys.exit(0 if len(results)==4 and all(x['passed'] for x in results) else 1)
