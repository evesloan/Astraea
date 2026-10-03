"""Queue the fixed current-project graphical review atomically; no arbitrary command payloads."""
from pathlib import Path
import argparse,json,re
parser=argparse.ArgumentParser();parser.add_argument('name');parser.add_argument('--profile',action='store_true');args=parser.parse_args()
assert re.fullmatch('[A-Za-z0-9_-]+',args.name),'Use a simple unique review name'
root=Path(__file__).resolve().parents[1];queue=Path('/workspace/shared/astraea-review-queue');assert queue.is_dir(),'Cloud graphical runner must already be started'
assert not any(queue.glob(args.name+'.*')),'Do not overwrite or repeat an existing review'
if args.profile:(root/'artifacts/profile_architecture.request').write_text('paired static views\n')
temporary=queue/(args.name+'.tmp');temporary.write_text(json.dumps({'kind':'capture_current_ship'}));destination=queue/(args.name+'.request');temporary.replace(destination);print(destination)
