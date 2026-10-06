"""Pure physical fitting checks over independently reopened source evidence."""
import sys, json, gzip, importlib.util
from pathlib import Path
sys.dont_write_bytecode = True
S = Path(__file__).resolve().parent
sys.path.insert(0, str(S.parent/'reference_programme001'))
from check_programme import run
assert json.loads((S/'qa/INDEPENDENT_REOPEN.json').read_text())['status'] == 'PASS_EXACT_COMPOSED_SOURCE_REOPEN'
with gzip.open(S/'qa/BUILD_EVALUATED_PROGRAMME.json.gz', 'rt') as handle:
    snapshot = json.load(handle)
actual_core = json.loads((S/'qa/BUILD_EVALUATED_CORE.json').read_text())
assert json.loads((S/'qa/ACTUAL_CORE_FITTING.json').read_text())['status'] == 'PASS_CORE_PURE_GEOMETRY'
result = run(snapshot, actual_core_plan=actual_core)
output = S/'qa/ACTUAL_PROGRAMME_FITTING.json'
assert not output.exists()
output.write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps({'status': result['status'], 'issues': result['issues']}), flush=True)
assert not result['issues'], 'Actual evaluated source fitting failed; preserve outputs'
