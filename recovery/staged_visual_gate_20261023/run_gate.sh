#!/usr/bin/env bash
set -euo pipefail
source /workspace/astraea-env/activate.sh
package_dir="$(cd -- "$(dirname -- "$0")" && pwd)"
python "$package_dir/../staged_activation_successor_20261023/compose.py"
DISPLAY=:111 /opt/godot/4.6.3/Godot_v4.6.3-stable_linux.x86_64 --rendering-method gl_compatibility --rendering-driver opengl3 --audio-driver Dummy --path /workspace/Astraea-recovered-e6274e77-20261021/Game --script "$package_dir/visual_gate.gd" --quit-after 3000
