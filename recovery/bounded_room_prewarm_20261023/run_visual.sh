#!/usr/bin/env bash
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
: "${DISPLAY:?An approved private display must already be running}"
python "$here/prepare_fixture.py" --mode candidate
export ASTRAEA_FIXTURE_MAP="$here/evidence/candidate-source-map.json"
export ASTRAEA_FIXTURE_OVERLAY="$here/evidence/candidate-overlay.pck"
export ASTRAEA_FIXTURE_BASE_PACK="${ASTRAEA_FIXTURE_BASE_PACK:-$here/../library/latest/extracted/Astraea-e3af0334.pck}"
export ASTRAEA_VISUAL_OUTPUT="$here/evidence/visual"
export XDG_DATA_HOME="$here/focused-project/xdg/data"
export XDG_CACHE_HOME="$here/focused-project/xdg/cache"
export XDG_CONFIG_HOME="$here/focused-project/xdg/config"
mkdir -p "$ASTRAEA_VISUAL_OUTPUT" "$XDG_DATA_HOME" "$XDG_CACHE_HOME" "$XDG_CONFIG_HOME"
export LIBGL_ALWAYS_SOFTWARE=1
exec godot --rendering-method gl_compatibility --rendering-driver opengl3 --audio-driver Dummy --quit-after 16000 --path "$here/focused-project" --script "$here/visual_gate.gd"
