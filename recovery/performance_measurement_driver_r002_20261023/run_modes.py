"""Plan by default. --execute is reserved for a separately authorized laptop run."""
import argparse, hashlib, json, math, os, subprocess
from pathlib import Path
MODES = [('no_occlusion_no_batch', '0', '0'), ('existing_occlusion_no_batch', '0', '1'), ('batch_without_occlusion', '1', '0'), ('batch_with_existing_occlusion', '1', '1')]

def require(condition, message):
    if not condition:
        raise ValueError(message)

def validate(s):
    for name, count in [('expected_actor_position', 3), ('internal_resolution', 2), ('expected_window_size', 2), ('headings_degrees', 4)]:
        require(isinstance(s[name], list) and len(s[name]) == count, name)
        require(all((isinstance(x, (int, float)) and (not isinstance(x, bool)) and math.isfinite(x) for x in s[name])), name)
    for name in ['camera_pitch_degrees', 'camera_fov', 'actor_tolerance_m', 'warmup_seconds', 'sample_seconds', 'startup_timeout_seconds', 'arm_timeout_seconds']:
        require(isinstance(s[name], (int, float)) and (not isinstance(s[name], bool)) and math.isfinite(s[name]), name)
    require(1 <= s['warmup_seconds'] <= 60 and 1 <= s['sample_seconds'] <= 60, 'Invalid measurement prerequisite')
    require(all((1 <= s[k] <= 600 for k in ['startup_timeout_seconds', 'arm_timeout_seconds'])) and 0 < s['actor_tolerance_m'] <= 0.2, 'Invalid measurement prerequisite')
    require(isinstance(s['expected_source_manifest_sha256'], str) and len(s['expected_source_manifest_sha256']) == 64 and all((c in '0123456789abcdef' for c in s['expected_source_manifest_sha256'])), 'Invalid measurement prerequisite')
    require(isinstance(s['effects_enabled'], bool), 'Invalid measurement prerequisite')
    require(20 <= s['camera_fov'] <= 120 and all((1 <= x <= 3840 and int(x) == x for x in s['internal_resolution'])), 'Invalid measurement prerequisite')

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--godot', type=Path, required=True)
    p.add_argument('--project', type=Path, required=True)
    p.add_argument('--scenario', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--execute', action='store_true')
    a = p.parse_args()
    s = json.loads(a.scenario.read_text())
    validate(s)
    require(isinstance(s['effects_enabled'], bool), 'Invalid measurement prerequisite')
    base = Path(__file__).resolve().parent
    project = a.project.resolve()
    out = a.output.resolve()
    scenario = a.scenario.resolve()
    require(not out.exists(), 'Use a new isolated result directory')
    plan = {'launch_requested': a.execute, 'operator_starts_each_existing_menu': True, 'fresh_process_per_mode': True, 'scenario': s, 'modes': [{'name': name, 'batch': batch, 'occlusion': occ} for name, batch, occ in MODES], 'production_writes': False, 'binary_requirement': 'Official Godot editor: --path/--script required; never use restricted release EXE', 'source_manifest_sha256': s['expected_source_manifest_sha256']}
    if not a.execute:
        print(json.dumps(plan, indent=2))
        return
    require(a.godot.is_file() and (project / 'project.godot').is_file(), 'Invalid measurement prerequisite')
    version = subprocess.check_output([str(a.godot.resolve()), '--version'], text=True).strip()
    require('.official.' in version, 'Use the retained official editor for all four modes')
    manifest = project / 'scripts/runtime_contracts_20261022/SOURCE_CONTRACTS.json'
    require(hashlib.sha256(manifest.read_bytes()).hexdigest() == s['expected_source_manifest_sha256'], 'Repaired source boundary differs')
    plan['engine_version'] = version
    plan['measurement_binary'] = 'official editor; not release EXE'
    plan['source_manifest_sha256'] = s['expected_source_manifest_sha256']
    require((project / 'd04_surface_cells_20261023/bootstrap.tscn').is_file(), 'Candidate not installed; this driver will not install it')
    pins = json.loads((base / 'CANDIDATE_PINS.json').read_text())
    for rel, h in pins.items():
        require(hashlib.sha256((project / rel).read_bytes()).hexdigest() == h, 'Candidate mismatch: ' + rel)
    out.mkdir(parents=True, exist_ok=False)
    (out / 'PLAN.json').write_text(json.dumps(plan, indent=2))
    timeout = s['startup_timeout_seconds'] + s['arm_timeout_seconds'] + 4 * (s['warmup_seconds'] + s['sample_seconds']) + 30
    for name, batch, occ in MODES:
        result = out / (name + '.json')
        log = out / (name + '.log')
        env = os.environ.copy()
        env.update(ASTRAEA_D04_SURFACE_CELLS=batch, ASTRAEA_OCCLUSION=occ, ASTRAEA_MEASUREMENT_MODE=name)
        cmd = [str(a.godot.resolve()), '--path', str(project), '--script', str(base / 'sampler.gd'), '--', str(scenario), str(result)]
        print('Mode ' + name + ': start menu, arrange verified pose/settings, then create ' + str(result) + '.arm', flush=True)
        with log.open('x', encoding='utf-8') as stream:
            child = subprocess.Popen(cmd, env=env, stdout=stream, stderr=subprocess.STDOUT)
            try:
                code = child.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                child.terminate()
                try:
                    child.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    child.kill()
                    child.wait()
                raise RuntimeError('Timed out; stopped only this driver-owned process: ' + name)
        require(code == 0 and result.is_file(), 'Mode failed; subsequent modes not launched: ' + name)
        require('SCRIPT ERROR:' not in log.read_text(encoding='utf-8', errors='replace') and '\nERROR:' not in log.read_text(encoding='utf-8', errors='replace'), 'Godot errors logged; subsequent modes stopped: ' + name)
        require(json.loads(result.read_text())['status'] == 'CAPTURED', 'Incomplete capture: ' + name)
    print(json.dumps({'status': 'CAPTURED', 'directory': str(out), 'modes': 4, 'performance_accepted': False}))
if __name__ == '__main__':
    main()
