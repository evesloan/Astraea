"""Run bounded Godot checks; a printed PASS never overrides an engine/script error."""
import os, pathlib, subprocess, json, sys, threading
root=pathlib.Path(__file__).resolve().parents[1]
state=root/'.godot'/'validation_state'
env=os.environ.copy()
for key,sub in [('XDG_CONFIG_HOME','config'),('XDG_DATA_HOME','data'),('XDG_CACHE_HOME','cache')]:
    p=state/sub;p.mkdir(parents=True,exist_ok=True);env[key]=str(p)
results=[]
commands=[('import',['--editor','--quit']),('baseline',['--script','res://tests/validate_baseline.gd']),('world',['--script','res://tests/validate_world.gd']),('stairs',['--script','res://tests/validate_stairs.gd']),('door',['--script','res://tests/validate_door.gd']),('contact_cache',['--script','res://tests/validate_contact_cache.gd']),('garden',['--script','res://tests/validate_garden.gd']),('salon',['--script','res://tests/validate_salon.gd']),('atrium_supports',['--script','res://tests/validate_atrium_supports.gd']),('salon_contents',['--script','res://tests/validate_salon_contents.gd']),('fixture_switch',['--script','res://tests/validate_fixture_switch.gd']),('garden_overlook',['--script','res://tests/validate_garden_overlook.gd']),('canopy_terrace',['--script','res://tests/validate_canopy_terrace.gd']),('residential_suite',['--script','res://tests/validate_residential_suite.gd']),('privacy_door',['--script','res://tests/validate_privacy_door.gd']),('guest_wash',['--script','res://tests/validate_guest_wash.gd']),('entry_door',['--script','res://tests/validate_entry_door.gd']),('twin_retreat',['--script','res://tests/validate_twin_retreat.gd']),('night_garden',['--script','res://tests/validate_night_garden.gd'])]
if '--only' in sys.argv:
    requested=sys.argv[sys.argv.index('--only')+1]
    commands=[entry for entry in commands if entry[0]==requested]
    assert commands, 'Unknown check'
    # Focused checks must not silently exercise stale imported Blender exports.
    # This is still a focused run, never a substitute for the full suite.
    if requested != 'import': commands.insert(0,('import',['--editor','--quit']))
for label,args in commands:
    process=subprocess.Popen(['godot','--headless','--path',str(root),'--quit-after','2400',*args],env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
    timeout=threading.Timer(90,process.kill);timeout.daemon=True;timeout.start()
    lines=[];errors=[]
    for line in process.stdout:
        lines.append(line);print(line,end='',flush=True)
        if 'ERROR:' in line or 'Assertion failed' in line or 'Parse Error' in line:
            errors.append(line.strip())
            if process.poll() is None: process.terminate()
    process.wait();timeout.cancel();output=''.join(lines)
    passed=process.returncode==0 and not errors and (label=='import' or 'PASS:' in output)
    results.append({'check':label,'passed':passed,'exit_code':process.returncode,'errors':errors})
    if not passed: break
(root/'artifacts').mkdir(exist_ok=True)
(root/'artifacts'/'validation.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps(results))
sys.exit(0 if len(results)==len(commands) and all(x['passed'] for x in results) else 1)
