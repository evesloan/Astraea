"""Run bounded Godot checks; a printed PASS never overrides an engine/script error."""
import os, pathlib, subprocess, json, sys, threading, time
root=pathlib.Path(__file__).resolve().parents[1]
state=root/'.godot'/'validation_state'
env=os.environ.copy()
for key,sub in [('XDG_CONFIG_HOME','config'),('XDG_DATA_HOME','data'),('XDG_CACHE_HOME','cache')]:
    p=state/sub;p.mkdir(parents=True,exist_ok=True);env[key]=str(p)
results=[]
realtime="--realtime" in sys.argv
mode="realtime" if realtime else "fixed60"
requested="full"
suite_started=time.perf_counter()
commands=[('orchard_boarding',['--script','res://tests/validate_orchard_boarding.gd']),('orchard_exchange',['--script','res://tests/validate_orchard_exchange.gd']),('orchard_lift',['--script','res://tests/validate_orchard_lift.gd']),('thread_shell_cart',['--script','res://tests/validate_thread_shell_cart.gd']),('thread_shell',['--script','res://tests/validate_thread_shell.gd']),('starboard_quiet',['--script','res://tests/validate_starboard_quiet.gd']),('starboard_conversation',['--script','res://tests/validate_starboard_conversation.gd']),('starboard_cart_turns',['--script','res://tests/validate_starboard_cart_turns.gd']),('starboard_reading',['--script','res://tests/validate_starboard_reading.gd']),('starboard_house_clearance',['--script','res://tests/validate_starboard_house_clearance.gd']),('starboard_house_stairs',['--script','res://tests/validate_starboard_house_stairs.gd']),('starboard_house_lift',['--script','res://tests/validate_starboard_house_lift.gd']),('residential_wayfinding',['--script','res://tests/validate_residential_wayfinding.gd']),('vesper_boarding',['--script','res://tests/validate_vesper_boarding.gd']),('vesper_mezzanine',['--script','res://tests/validate_vesper_mezzanine.gd']),('vesper_lift',['--script','res://tests/validate_vesper_lift.gd']),('import',['--editor','--quit']),('baseline',['--script','res://tests/validate_baseline.gd']),('world',['--script','res://tests/validate_world.gd']),('stairs',['--script','res://tests/validate_stairs.gd']),('door',['--script','res://tests/validate_door.gd']),('contact_cache',['--script','res://tests/validate_contact_cache.gd']),('garden',['--script','res://tests/validate_garden.gd']),('salon',['--script','res://tests/validate_salon.gd']),('atrium_supports',['--script','res://tests/validate_atrium_supports.gd']),('salon_contents',['--script','res://tests/validate_salon_contents.gd']),('fixture_switch',['--script','res://tests/validate_fixture_switch.gd']),('garden_overlook',['--script','res://tests/validate_garden_overlook.gd']),('canopy_terrace',['--script','res://tests/validate_canopy_terrace.gd']),('residential_suite',['--script','res://tests/validate_residential_suite.gd']),('privacy_door',['--script','res://tests/validate_privacy_door.gd']),('guest_wash',['--script','res://tests/validate_guest_wash.gd']),('entry_door',['--script','res://tests/validate_entry_door.gd']),('twin_retreat',['--script','res://tests/validate_twin_retreat.gd']),('night_garden',['--script','res://tests/validate_night_garden.gd']),('cleaning_cart',['--script','res://tests/validate_cleaning_cart.gd']),('cart_clearance',['--script','res://tests/validate_cart_clearance.gd']),('lift_gate',['--script','res://tests/validate_lift_gate.gd']),('vertical_commons',['--script','res://tests/validate_vertical_commons.gd']),('commons_lift',['--script','res://tests/validate_commons_lift.gd']),('lift_boarding',['--script','res://tests/validate_lift_boarding.gd']),('commons_lighting',['--script','res://tests/validate_commons_lighting.gd']),('retail_curios',['--script','res://tests/validate_retail_curios.gd']),('arrivals_fusion',['--script','res://tests/validate_arrivals_fusion.gd']),('arrivals_lift',['--script','res://tests/validate_arrivals_lift.gd']),('star_atlas',['--script','res://tests/validate_star_atlas.gd']),('star_atlas_lift',['--script','res://tests/validate_star_atlas_lift.gd']),('aquatic_lift',['--script','res://tests/validate_aquatic_lift.gd']),('aquatic_access',['--script','res://tests/validate_aquatic_access.gd']),('living_gifts',['--script','res://tests/validate_living_gifts.gd']),('vesper_dining',['--script','res://tests/validate_vesper_dining.gd']),('vesper_watercourse',['--script','res://tests/validate_vesper_watercourse.gd']),('vesper_service',['--script','res://tests/validate_vesper_service.gd'])]
# New checks must not outrun the import barrier when their models are first added.
commands.sort(key=lambda entry: entry[0] != 'import')
if '--only' in sys.argv:
    requested=sys.argv[sys.argv.index('--only')+1]
    commands=[entry for entry in commands if entry[0]==requested]
    assert commands, 'Unknown check'
    # Focused checks must not silently exercise stale imported Blender exports.
    # This is still a focused run, never a substitute for the full suite.
    if requested != 'import': commands.insert(0,('import',['--editor','--quit']))
for label,args in commands:
    frame_budget='12000' if label in ['star_atlas','starboard_house_lift','starboard_house_stairs','starboard_cart_turns','thread_shell','thread_shell_cart','orchard_exchange','orchard_lift'] else '4800' if label in ['arrivals_fusion','star_atlas_lift','aquatic_lift','living_gifts','vesper_dining','vesper_watercourse','vesper_service','vesper_mezzanine','residential_wayfinding'] else '2400'
    # Fixed60 advances the same60Hz simulation without wall-clock waiting.
    # Import and graphical review retain their separate original workflows.
    clock_args=[] if realtime or label=='import' else ['--fixed-fps','60']
    started=time.perf_counter()
    process=subprocess.Popen(['godot','--headless','--path',str(root),'--quit-after',frame_budget,*clock_args,*args],env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
    timeout=threading.Timer(180 if label=="star_atlas" else 90,process.kill);timeout.daemon=True;timeout.start()
    lines=[];errors=[]
    for line in process.stdout:
        lines.append(line);print(line,end='',flush=True)
        if 'ERROR:' in line or 'Assertion failed' in line or 'Parse Error' in line:
            errors.append(line.strip())
            if process.poll() is None: process.terminate()
    process.wait();timeout.cancel();output=''.join(lines)
    passed=process.returncode==0 and not errors and (label=='import' or 'PASS:' in output)
    results.append({'check':label,'passed':passed,'exit_code':process.returncode,'errors':errors,'wall_seconds':round(time.perf_counter()-started,4),'clock_mode':mode if label!='import' else 'editor'})
    if not passed: break
(root/'artifacts').mkdir(exist_ok=True)
(root/'artifacts'/'validation.json').write_text(json.dumps(results,indent=2)+'\n')
(root/'artifacts'/('validation_'+requested+'_'+mode+'.json')).write_text(json.dumps({'checks':results,'wall_seconds':round(time.perf_counter()-suite_started,4),'clock_mode':mode,'scope':'Simulation/assertion execution; not rendering performance, real-input latency or target-platform acceptance'},indent=2)+'\n')
print(json.dumps({"checks":len(results),"passed":sum(x["passed"]for x in results),"clock_mode":mode,"wall_seconds":round(time.perf_counter()-suite_started,4),"failed":[x for x in results if not x["passed"]]}))
sys.exit(0 if len(results)==len(commands) and all(x['passed'] for x in results) else 1)
