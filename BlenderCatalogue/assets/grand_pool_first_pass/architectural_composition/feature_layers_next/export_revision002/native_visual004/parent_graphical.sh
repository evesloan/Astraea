#!/usr/bin/env bash
# Parent only, after theater and all other Game work release the slot.
# This wrapper records existing authority; it does not grant permission.
set -euo pipefail
if [[ $# -ne 1 || -z "$1" ]]; then
  printf '%s\n' 'Usage: bash parent_graphical.sh "actual parent release message or receipt"' >&2
  exit 2
fi
if [[ -z "${DISPLAY:-}" && -z "${WAYLAND_DISPLAY:-}" ]]; then
  printf '%s\n' 'Run only in the existing approved parent graphical terminal.' >&2
  exit 2
fi
HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
export PYTHONDONTWRITEBYTECODE=1
python "$HERE/run_trial.py" --freeze --parent-released-engineering-theater --release-reference "$1"
python "$HERE/run_trial.py" --run --parent-approved-game-slot
