#!/usr/bin/env bash
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
mode="${1:?baseline or candidate}"
script="${2:-connected_check.gd}"
python "$here/prepare_fixture.py" --mode "$mode"
export ASTRAEA_FIXTURE_MAP="$here/evidence/$mode-source-map.json"
export ASTRAEA_FIXTURE_OVERLAY="$here/evidence/$mode-overlay.pck"
export ASTRAEA_FIXTURE_BASE_PACK="${ASTRAEA_FIXTURE_BASE_PACK:-$here/../library/latest/extracted/Astraea-e3af0334.pck}"
export ASTRAEA_ROOM_PREWARM=0
export XDG_DATA_HOME="$here/focused-project/xdg/data"
export XDG_CACHE_HOME="$here/focused-project/xdg/cache"
export XDG_CONFIG_HOME="$here/focused-project/xdg/config"
mkdir -p "$XDG_DATA_HOME" "$XDG_CACHE_HOME" "$XDG_CONFIG_HOME"
# Exact full pack hash was verified by acquisition; the maps verify all mounted
# fixture bytes again. No --main-pack, editor, import, export, or production main.
exec godot --headless --audio-driver Dummy --quit-after 16000 --path "$here/focused-project" --script "$here/$script"
