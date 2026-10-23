#!/usr/bin/env bash
set -euo pipefail
source /workspace/astraea-env/activate.sh
package_dir="$(cd -- "$(dirname -- "$0")" && pwd)"
python "$package_dir/compose.py"
/opt/godot/4.6.3/Godot_v4.6.3-stable_linux.x86_64 --headless --quit-after 600 --path /workspace/Astraea-recovered-e6274e77-20261021/Game --script "$package_dir/connected_check.gd"
