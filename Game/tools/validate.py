"""Run bounded Godot checks; a printed PASS never overrides an engine/script error."""
import os, pathlib, subprocess, json, sys, threading, time
if "--help" in sys.argv or "-h" in sys.argv:
    print("Usage: python tools/validate.py [--only CHECK] [--realtime]")
    print("Default runs the full suite. --only runs one named check plus import.")
    print("Help does not start Godot or modify validation receipts.")
    sys.exit(0)
root=pathlib.Path(__file__).resolve().parents[1]
# Checks can emit receipts before the suite finishes, including on a fresh clone.
(root/'artifacts').mkdir(exist_ok=True)
state=root/'.godot'/'validation_state'
env=os.environ.copy()
for key,sub in [('XDG_CONFIG_HOME','config'),('XDG_DATA_HOME','data'),('XDG_CACHE_HOME','cache')]:
    p=state/sub;p.mkdir(parents=True,exist_ok=True);env[key]=str(p)
results=[]
realtime="--realtime" in sys.argv
mode="realtime" if realtime else "fixed60"
requested="full"
suite_started=time.perf_counter()
commands=[('bridge_platform_structure',['--script','res://tests/validate_bridge_platform_structure.gd']),('bridge_platform_routes',['--script','res://tests/validate_bridge_platform_routes.gd']),('bridge_platform_cart',['--script','res://tests/validate_bridge_platform_cart.gd']),('bridge_platform_windows',['--script','res://tests/validate_bridge_platform_windows.gd']),('aft_command_structure',['--script','res://tests/validate_aft_command_structure.gd']),('aft_command_cart',['--script','res://tests/validate_aft_command_cart.gd']),('aft_command_access',['--script','res://tests/validate_aft_command_access.gd']),('crown_windows',['--script','res://tests/validate_crown_windows.gd']),('crown_structure',['--script','res://tests/validate_crown_structure.gd']),('crown_cart',['--script','res://tests/validate_crown_cart.gd']),('crown_access',['--script','res://tests/validate_crown_access.gd']),('forward_staff_lift',['--script','res://tests/validate_forward_staff_lift.gd']),('forward_staff_boarding',['--script','res://tests/validate_forward_staff_boarding.gd']),('lower_staff_routes',['--script','res://tests/validate_lower_staff_routes.gd']),('upper_staff_routes',['--script','res://tests/validate_upper_staff_routes.gd']),('lower_staff_cart',['--script','res://tests/validate_lower_staff_cart.gd']),('staff_cart_turns',['--script','res://tests/validate_staff_cart_turns.gd']),('fore_midship_stairs',['--script','res://tests/validate_fore_midship_stairs.gd']),('fore_midship_lift',['--script','res://tests/validate_fore_midship_lift.gd']),('fore_midship_boarding',['--script','res://tests/validate_fore_midship_boarding.gd']),('aft_midship_stairs',['--script','res://tests/validate_aft_midship_stairs.gd']),('aft_midship_lift',['--script','res://tests/validate_aft_midship_lift.gd']),('aft_midship_boarding',['--script','res://tests/validate_aft_midship_boarding.gd']),('aft_stairs',['--script','res://tests/validate_aft_stairs.gd']),('aft_lift',['--script','res://tests/validate_aft_lift.gd']),('aft_boarding',['--script','res://tests/validate_aft_boarding.gd']),('forward_core_stairs',['--script','res://tests/validate_forward_core_stairs.gd']),('forward_core_lift',['--script','res://tests/validate_forward_core_lift.gd']),('forward_core_boarding',['--script','res://tests/validate_forward_core_boarding.gd']),('lower_hull',['--script','res://tests/validate_lower_hull.gd']),('aft_crown_stairs',['--script','res://tests/validate_aft_crown_stairs.gd']),('aft_crown_lift',['--script','res://tests/validate_aft_crown_lift.gd']),('aft_crown_boarding',['--script','res://tests/validate_aft_crown_boarding.gd']),('ship_backbone',['--script','res://tests/audit_ship_backbone.gd']),('primary_core_boarding',['--script','res://tests/validate_primary_core_boarding.gd']),('primary_core_stairs',['--script','res://tests/validate_primary_core_stairs.gd']),('primary_core_lift',['--script','res://tests/validate_primary_core_lift.gd']),('primary_lift_panel',['--script','res://tests/validate_primary_lift_panel.gd']),('orchard_foodhall',['--script','res://tests/validate_orchard_foodhall.gd']),('orchard_boarding',['--script','res://tests/validate_orchard_boarding.gd']),('orchard_exchange',['--script','res://tests/validate_orchard_exchange.gd']),('orchard_lift',['--script','res://tests/validate_orchard_lift.gd']),('thread_shell_cart',['--script','res://tests/validate_thread_shell_cart.gd']),('thread_shell',['--script','res://tests/validate_thread_shell.gd']),('starboard_quiet',['--script','res://tests/validate_starboard_quiet.gd']),('starboard_conversation',['--script','res://tests/validate_starboard_conversation.gd']),('starboard_cart_turns',['--script','res://tests/validate_starboard_cart_turns.gd']),('starboard_reading',['--script','res://tests/validate_starboard_reading.gd']),('starboard_house_clearance',['--script','res://tests/validate_starboard_house_clearance.gd']),('starboard_house_stairs',['--script','res://tests/validate_starboard_house_stairs.gd']),('starboard_house_lift',['--script','res://tests/validate_starboard_house_lift.gd']),('residential_wayfinding',['--script','res://tests/validate_residential_wayfinding.gd']),('vesper_boarding',['--script','res://tests/validate_vesper_boarding.gd']),('vesper_mezzanine',['--script','res://tests/validate_vesper_mezzanine.gd']),('vesper_lift',['--script','res://tests/validate_vesper_lift.gd']),('import',['--editor','--quit']),('baseline',['--script','res://tests/validate_baseline.gd']),('world',['--script','res://tests/validate_world.gd']),('stairs',['--script','res://tests/validate_stairs.gd']),('door',['--script','res://tests/validate_door.gd']),('contact_cache',['--script','res://tests/validate_contact_cache.gd']),('garden',['--script','res://tests/validate_garden.gd']),('salon',['--script','res://tests/validate_salon.gd']),('atrium_supports',['--script','res://tests/validate_atrium_supports.gd']),('salon_contents',['--script','res://tests/validate_salon_contents.gd']),('fixture_switch',['--script','res://tests/validate_fixture_switch.gd']),('garden_overlook',['--script','res://tests/validate_garden_overlook.gd']),('canopy_terrace',['--script','res://tests/validate_canopy_terrace.gd']),('residential_suite',['--script','res://tests/validate_residential_suite.gd']),('privacy_door',['--script','res://tests/validate_privacy_door.gd']),('guest_wash',['--script','res://tests/validate_guest_wash.gd']),('entry_door',['--script','res://tests/validate_entry_door.gd']),('twin_retreat',['--script','res://tests/validate_twin_retreat.gd']),('night_garden',['--script','res://tests/validate_night_garden.gd']),('cleaning_cart',['--script','res://tests/validate_cleaning_cart.gd']),('cart_clearance',['--script','res://tests/validate_cart_clearance.gd']),('lift_gate',['--script','res://tests/validate_lift_gate.gd']),('vertical_commons',['--script','res://tests/validate_vertical_commons.gd']),('commons_lift',['--script','res://tests/validate_commons_lift.gd']),('lift_boarding',['--script','res://tests/validate_lift_boarding.gd']),('commons_lighting',['--script','res://tests/validate_commons_lighting.gd']),('retail_curios',['--script','res://tests/validate_retail_curios.gd']),('arrivals_fusion',['--script','res://tests/validate_arrivals_fusion.gd']),('arrivals_lift',['--script','res://tests/validate_arrivals_lift.gd']),('star_atlas',['--script','res://tests/validate_star_atlas.gd']),('star_atlas_lift',['--script','res://tests/validate_star_atlas_lift.gd']),('aquatic_lift',['--script','res://tests/validate_aquatic_lift.gd']),('aquatic_access',['--script','res://tests/validate_aquatic_access.gd']),('living_gifts',['--script','res://tests/validate_living_gifts.gd']),('vesper_dining',['--script','res://tests/validate_vesper_dining.gd']),('vesper_watercourse',['--script','res://tests/validate_vesper_watercourse.gd']),('vesper_service',['--script','res://tests/validate_vesper_service.gd'])]
# New checks must not outrun the import barrier when their models are first added.
commands = [(name, ['--script', 'res://tests/validate_' + name + '.gd']) for name in ['upper_horizon_enclosure_structure','upper_horizon_enclosure_windows','aft_crown_platform_structure','aft_crown_platform_access','aft_crown_platform_cart','bridge_enclosure_structure','bridge_enclosure_windows','bridge_enclosure_access','bridge_enclosure_cart']] + commands
commands = [('d17_connected_access', ['--script', 'res://tests/validate_d17_connected_access.gd']), ('d17_connected_cart', ['--script', 'res://tests/validate_d17_connected_cart.gd'])] + commands
commands = [('lighting_budget', ['--script', 'res://tests/validate_lighting_budget.gd'])] + commands
commands = [('grand_pool_access', ['--script', 'res://tests/validate_grand_pool_access.gd'])] + commands
commands = [('grand_pool_service_cart', ['--script', 'res://tests/validate_grand_pool_service_cart.gd'])] + commands
commands += [('grand_pool_local_lift', ['--script', 'res://tests/validate_grand_pool_local_lift.gd']), ('forward_staff_extended_lift', ['--script', 'res://tests/validate_forward_staff_extended_lift.gd'])]
commands = [('secondary_engineering_access', ['--script', 'res://tests/validate_secondary_engineering_access.gd'])] + commands
commands = [('grand_pool_first_pass', ['--script', 'res://tests/validate_grand_pool_first_pass.gd'])] + commands
commands = [('secondary_engineering_essentials', ['--script', 'res://tests/validate_secondary_engineering_essentials.gd'])] + commands
commands = [('grand_pool_finish', ['--script', 'res://tests/validate_grand_pool_finish.gd'])] + commands
commands = [('secondary_engineering_cell', ['--script', 'res://tests/validate_secondary_engineering_cell.gd'])] + commands
commands = [(name, ['--script', 'res://tests/validate_' + name + '.gd']) for name in ['theater_structure','theater_access','theater_cart']] + commands
commands = [('grand_pool_architecture', ['--script', 'res://tests/validate_grand_pool_architecture.gd'])] + commands
commands = [('engineering_controls', ['--script', 'res://tests/validate_engineering_calibration.gd'])] + commands
commands.sort(key=lambda entry: entry[0] != 'import')
if '--only' in sys.argv:
    requested=sys.argv[sys.argv.index('--only')+1]
    commands=[entry for entry in commands if entry[0]==requested]
    assert commands, 'Unknown check'
    # Focused checks must not silently exercise stale imported Blender exports.
    # This is still a focused run, never a substitute for the full suite.
    if requested != 'import': commands.insert(0,('import',['--editor','--quit']))
for label,args in commands:
    frame_budget='50000' if label in ['primary_core_stairs','forward_core_stairs','fore_midship_stairs','aft_midship_stairs','aft_stairs'] else '30000' if label in ['fore_midship_lift','fore_midship_boarding','aft_midship_lift','aft_midship_boarding','aft_lift','aft_boarding','primary_core_lift','primary_core_boarding','forward_core_lift','forward_core_boarding','aft_crown_stairs','aft_crown_lift','aft_crown_boarding'] else '12000' if label in ['star_atlas','starboard_house_lift','starboard_house_stairs','starboard_cart_turns','thread_shell','thread_shell_cart','orchard_exchange','orchard_lift','orchard_foodhall'] else '4800' if label in ['arrivals_fusion','star_atlas_lift','aquatic_lift','living_gifts','vesper_dining','vesper_watercourse','vesper_service','vesper_mezzanine','residential_wayfinding'] else '2400'
    # Lower staff routes exceed 500m at the unchanged3.1m/s walking speed.
    # Include all three stops and loaded return turns without premature quit-after.
    if label in ['forward_staff_lift','forward_staff_boarding','lower_staff_routes','upper_staff_routes','staff_cart_turns']:frame_budget='20000'
    if label in ['crown_access','crown_cart','aft_command_access','aft_command_cart','bridge_platform_routes','bridge_platform_cart']:frame_budget='30000'
    # Full closed-door bypass round-trip plus bridge thresholds:1937.4m at1m/s.
    if label == 'bridge_enclosure_cart': frame_budget='180000'
    if label == 'bridge_enclosure_access': frame_budget='70000'
    # New aft circuit uses physical staff turns and four thresholds at unchanged speeds.
    if label == 'aft_crown_platform_cart': frame_budget='100000'
    if label == 'aft_crown_platform_access': frame_budget='60000'
    if label == 'd17_connected_access': frame_budget='12000'
    if label == 'd17_connected_cart': frame_budget='24000'
    if label == 'grand_pool_access': frame_budget='30000'
    if label == 'grand_pool_first_pass': frame_budget='32000'
    if label == 'grand_pool_finish': frame_budget='32000'
    if label == 'grand_pool_architecture': frame_budget='12000'
    if label == 'secondary_engineering_cell': frame_budget='30000'
    if label == 'engineering_controls': frame_budget='40000'
    if label == 'secondary_engineering_access': frame_budget='16000'
    if label == 'secondary_engineering_essentials': frame_budget='12000'
    if label == 'grand_pool_service_cart': frame_budget='60000'
    if label == 'forward_staff_extended_lift': frame_budget='12000'
    if label == 'theater_structure': frame_budget='2400'
    if label == 'theater_access': frame_budget='12000'
    if label == 'theater_cart': frame_budget='24000'
    # Fixed60 advances the same60Hz simulation without wall-clock waiting.
    # Import and graphical review retain their separate original workflows.
    clock_args=[] if realtime or label=='import' else ['--fixed-fps','60']
    started=time.perf_counter()
    process=subprocess.Popen(['godot','--headless','--path',str(root),'--quit-after',frame_budget,*clock_args,*args],env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
    timeout=threading.Timer(1200 if label=='engineering_controls' else 600 if label=='theater_cart' else 240 if label in ['theater_structure','theater_access'] else 600 if label=='secondary_engineering_cell' else 1000 if label=='grand_pool_service_cart' else 240 if label in ['d17_connected_cart','grand_pool_access','grand_pool_first_pass','grand_pool_finish','grand_pool_architecture'] else 600 if label=='aft_crown_platform_cart' else 300 if label=='aft_crown_platform_access' else 900 if label=='bridge_enclosure_cart' else 240 if label=='bridge_enclosure_access' else 180 if label in ["star_atlas","bridge_platform_cart","forward_staff_extended_lift","secondary_engineering_access","secondary_engineering_essentials","secondary_engineering_cell"] else 90,process.kill);timeout.daemon=True;timeout.start()
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
