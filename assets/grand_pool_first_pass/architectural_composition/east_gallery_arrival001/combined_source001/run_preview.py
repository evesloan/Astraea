"""Two bounded source-context pictures. No saved scene, export or Game writes."""
from pathlib import Path
import os, sys, json, hashlib, subprocess, datetime, time
S = Path(__file__).resolve().parent
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
now = lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()
pins = json.loads((S/'PREVIEW_PINS.json').read_text())
for path, digest in pins['sha256'].items():
    assert sha(path) == digest, path
assert not (S/'source_preview001').exists() and not (S/'qa/PREVIEW_JOB.json').exists()
assert json.loads((S/'qa/INDEPENDENT_REOPEN.json').read_text())['status'] == 'PASS_EXACT_COMPOSED_SOURCE_REOPEN'
result = {'status': 'RUNNING', 'started_utc': now(), 'scope': 'Two early composed source views. Uninstalled candidate; native lighting and first-pass acceptance remain pending.'}
receipt = S/'qa/PREVIEW_JOB.json'
def save(): receipt.write_text(json.dumps(result, indent=2)+'\n')
env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', OMP_NUM_THREADS='2', OPENBLAS_NUM_THREADS='2', MKL_NUM_THREADS='2', NUMEXPR_NUM_THREADS='2', BLIS_NUM_THREADS='2')
command = ['/usr/bin/blender', '--background', '--factory-startup', '--disable-autoexec', '--threads', '2', '--python-exit-code', '1', '--python', str(S/'render_source.py')]
result['command'] = command
save()
print('POOL SOURCE PREVIEW START', result['started_utc'], flush=True)
try:
    start = time.monotonic()
    with (S/'qa/preview001.log').open('x') as handle:
        run = subprocess.run(command, env=env, stdout=handle, stderr=subprocess.STDOUT, timeout=1200)
    result.update(exit_code=run.returncode, elapsed_s=time.monotonic()-start, finished_utc=now(), log_sha256=sha(S/'qa/preview001.log'))
    assert run.returncode == 0, 'Source preview failed; preserve outputs'
    for path, digest in pins['sha256'].items(): assert sha(path) == digest, path
    report = json.loads((S/'source_preview001/PREVIEW_REPORT.json').read_text())
    assert len(report['renders']) == 2 and report['all_source_inputs_unchanged']
    result.update(status='TWO_SOURCE_CONTEXT_VIEWS_READY_FOR_PIXEL_REVIEW', all_pinned_inputs_unchanged=True, report_sha256=sha(S/'source_preview001/PREVIEW_REPORT.json'))
    save()
except BaseException as exc:
    result.update(status='FAILED_PRESERVE_OUTPUTS', finished_utc=now(), error=repr(exc))
    save()
    raise
print(result['status'], flush=True)
