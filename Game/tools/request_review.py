"""Queue the fixed current-project graphical review atomically; no arbitrary command payloads."""
from pathlib import Path
import argparse,json,re,os,subprocess
parser=argparse.ArgumentParser();parser.add_argument('name');parser.add_argument('--profile',action='store_true');parser.add_argument('--view-group',choices=['all','aft_crown_platform','upper_horizon_enclosure'],default='all');args=parser.parse_args()
assert re.fullmatch('[A-Za-z0-9_-]+',args.name),'Use a simple unique review name'
root=Path(__file__).resolve().parents[1];queue=Path('/workspace/shared/astraea-review-queue');assert queue.is_dir(),'Cloud graphical runner must already be started'
assert not any(queue.glob('*.request')), 'A graphical review is already queued or running'
assert not any(queue.glob(args.name+'.*')),'Do not overwrite or repeat an existing review'
# Refresh imported resources before admitting a graphical job. A current GLB on
# disk alone does not mean an already imported scene uses those bytes.
state=root/'.godot'/'validation_state';env=os.environ.copy()
for key,sub in [('XDG_CONFIG_HOME','config'),('XDG_DATA_HOME','data'),('XDG_CACHE_HOME','cache')]:
    folder=state/sub;folder.mkdir(parents=True,exist_ok=True);env[key]=str(folder)
refresh=subprocess.run(['godot','--headless','--path',str(root),'--editor','--quit'],env=env,capture_output=True,text=True,timeout=90)
output=refresh.stdout+refresh.stderr
(root/'artifacts').mkdir(exist_ok=True)
(root/'artifacts'/('review_import_'+args.name+'.log')).write_text(output)
assert refresh.returncode==0 and 'ERROR:' not in output and 'Parse Error' not in output,'Review import failed; no graphical job queued'
(root/'artifacts/capture_view_group.txt').write_text(args.view_group+'\n')
if args.profile:(root/'artifacts/profile_architecture.request').write_text('paired static views\n')
temporary=queue/(args.name+'.tmp');temporary.write_text(json.dumps({'kind':'capture_current_ship'}));destination=queue/(args.name+'.request');temporary.replace(destination);print(destination)
