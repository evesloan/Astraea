"""One bounded serial source build/reopen/fitting job. New scratch outputs only."""
from pathlib import Path
import os, sys, json, hashlib, subprocess, datetime, time
S = Path(__file__).resolve().parent
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
now = lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()
pins = json.loads((S/'JOB_PINS.json').read_text())
for path, digest in pins['sha256'].items():
    assert sha(path) == digest, path
assert not (S/'source').exists() and not (S/'qa/SOURCE_JOB.json').exists()
(S/'qa').mkdir(exist_ok=True)
receipt = S/'qa/SOURCE_JOB.json'
result = {'status': 'RUNNING', 'started_utc': now(), 'processes': [], 'scope': 'One complete source build, independent reopen, pure evaluated fitting. No export/render/Game/Catalogue mutation.'}
env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', OMP_NUM_THREADS='2', OPENBLAS_NUM_THREADS='2', MKL_NUM_THREADS='2', NUMEXPR_NUM_THREADS='2', BLIS_NUM_THREADS='2')

def save():
    receipt.write_text(json.dumps(result, indent=2)+'\n')

def run(label, command, timeout):
    record = {'label': label, 'command': command, 'started_utc': now(), 'timeout_s': timeout}
    result['processes'].append(record)
    save()
    print('POOL SOURCE START', label, record['started_utc'], flush=True)
    start = time.monotonic()
    with (S/'qa'/f'{label}.log').open('x') as log:
        completed = subprocess.run(command, env=env, stdout=log, stderr=subprocess.STDOUT, timeout=timeout)
    record.update(finished_utc=now(), elapsed_s=time.monotonic()-start, exit_code=completed.returncode, log_sha256=sha(S/'qa'/f'{label}.log'))
    save()
    print('POOL SOURCE END', label, completed.returncode, flush=True)
    assert completed.returncode == 0, f'{label} failed; retain log and source'

try:
    base = ['/usr/bin/blender', '--background', '--factory-startup', '--disable-autoexec', '--threads', '2', '--python-exit-code', '1', '--python']
    run('build001', base+[str(S/'build_composed.py')], 300)
    run('reopen001', base+[str(S/'reopen_composed.py')], 300)
    run('actual_core_fitting001', [sys.executable, str(S.parent/'source_blockin001/review_core.py'), '--plan', str(S/'qa/BUILD_EVALUATED_CORE.json'), '--output', str(S/'qa/ACTUAL_CORE_FITTING.json')], 300)
    run('actual_fitting001', [sys.executable, str(S/'check_actual_programme.py')], 300)
    for path, digest in pins['sha256'].items():
        assert sha(path) == digest, path
    result.update(status='PASS_COMPOSED_SOURCE_BUILD_REOPEN_AND_FIT', finished_utc=now(), inputs_unchanged=True, source_sha256=sha(S/'source/AST-AQU-016_east_gallery_composed.blend'), pending=['Early source pixels', 'Independent retention', 'Exports and native-world acceptance'])
    save()
except BaseException as exc:
    result.update(status='FAILED_PRESERVE_OUTPUTS', finished_utc=now(), error=repr(exc))
    save()
    raise
print(result['status'], flush=True)
