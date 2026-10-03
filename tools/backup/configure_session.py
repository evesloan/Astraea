"""Recreate non-secret backup session settings after a verified source restore."""
from pathlib import Path
import argparse,json
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--workspace',required=True,type=Path,help='Actual conversation-scoped workspace for new archives/state')
p.add_argument('--upload-helper',required=True,type=Path,help='Fresh official Library upload helper, unchanged')
p.add_argument('--projects-parent',type=Path,default=Path(__file__).resolve().parents[3])
a=p.parse_args();assert a.upload_helper.is_file(),'Obtain the current supported helper first'
policy=json.loads(Path(__file__).with_name('retained_baselines.json').read_text());projects=[]
for source in policy['projects']:
    entry=dict(source);name=entry.pop('directory_name');root=(a.projects_parent/name).resolve()
    assert (root/'.git').is_dir(),'Restore and verify project history first: '+str(root)
    entry['root']=str(root);projects.append(entry)
workspace=a.workspace.resolve();runtime=workspace/'astraea-backup-runtime';runtime.mkdir(parents=True,exist_ok=True)
config=runtime/'config.json'
if config.exists():raise SystemExit('Existing session config preserved; inspect it rather than overwrite it')
settings={k:policy[k] for k in ['schema','wip_interval_seconds','poll_seconds','part_limit_bytes']}
settings.update(state=str(runtime/'state.json'),output=str(workspace/'astraea-auto-backups'),upload_helper=str(a.upload_helper.resolve()),projects=projects)
config.write_text(json.dumps(settings,indent=2)+'\n');print(config)
