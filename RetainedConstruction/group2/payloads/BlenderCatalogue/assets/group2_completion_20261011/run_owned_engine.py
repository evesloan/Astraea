"""One bounded Godot process; stop this owned child on real engine/script error."""
import datetime, json, os, pathlib, subprocess, sys, time
args = sys.argv[1:]
qa, script, log = pathlib.Path(args[0]), args[1], pathlib.Path(args[2])
live = subprocess.run(['ps', '-C', 'godot,blender', '-o', 'pid=,args='], capture_output=True, text=True)
assert not live.stdout.strip(), 'Another heavy process is active; do not launch a duplicate'
env = os.environ.copy()
env.update(XDG_CONFIG_HOME='/workspace/astraea-env/config', XDG_CACHE_HOME='/workspace/astraea-env/cache', XDG_DATA_HOME='/workspace/astraea-env/data')
start = time.monotonic()
command = ['godot', '--headless', '--path', str(qa), '--fixed-fps', '60', '--script', script]
assert not log.exists(), 'Preserve earlier logs'
with log.open('w') as out:
    process = subprocess.Popen(command, stdout=out, stderr=subprocess.STDOUT, env=env)
    pid = process.pid
    reason = None
    while process.poll() is None:
        content = log.read_text(errors='replace')
        if 'SCRIPT ERROR:' in content or '\nERROR:' in content:
            reason = 'Owned engine stopped after engine/script error; no acceptance'
            process.terminate()
            break
        if time.monotonic() - start > 1200:
            reason = 'Owned engine reached1200s bound; no acceptance'
            process.terminate()
            break
        time.sleep(.25)
    try:
        code = process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        process.kill()
        code = process.wait()
    content = log.read_text(errors='replace')
    passed = code == 0 and reason is None and 'SCRIPT ERROR:' not in content and '\nERROR:' not in content
receipt = {'pid': pid, 'exit': code, 'pass': passed, 'reason': reason, 'script': script,
           'qa_project': str(qa), 'mode': 'fixed60 scoped fixture; not gameplayFPS',
           'finished_utc': datetime.datetime.now(datetime.timezone.utc).isoformat()}
log.with_suffix('.PROCESS.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps(receipt))
sys.exit(0 if passed else 1)
