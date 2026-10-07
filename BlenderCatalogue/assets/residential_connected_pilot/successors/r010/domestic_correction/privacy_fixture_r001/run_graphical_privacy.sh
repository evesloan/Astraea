#!/usr/bin/env bash
set -euo pipefail
P=/workspace/scratch/375c2e438292/residential-batch-neighborhood-20261006/domestic_correction/privacy_fixture_r001
export XDG_CONFIG_HOME="$P/runtime_config"
export XDG_DATA_HOME="$P/runtime_data"
export XDG_CACHE_HOME="$P/runtime_cache"
python - "$P" <<'PY'
from pathlib import Path
import json,hashlib,sys
p=Path(sys.argv[1]); manifest=json.loads((p/'GRAPHICAL_INPUT_PINS.json').read_text())
for r in manifest['files']:
 assert hashlib.sha256((p/r['path']).read_bytes()).hexdigest()==r['sha256'],r['path']
print('Exact graphical input pins verified')
PY
set +e
timeout 150s godot --path "$P" --rendering-method gl_compatibility --resolution 320x240 --max-fps 60 --script res://test_privacy.gd > "$P/results/graphical.log" 2>&1
RESULT=$?
set -e
printf '%s\n' "$RESULT" > "$P/results/graphical.exit"
tail -18 "$P/results/graphical.log"
exit "$RESULT"
