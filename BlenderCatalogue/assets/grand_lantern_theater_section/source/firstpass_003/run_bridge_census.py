"""Serial, read-only current-world census. Run only with Game slot owner clearance."""
from pathlib import Path
import json,hashlib,subprocess,time,os,datetime
R=Path(__file__).resolve().parent;G=Path('/workspace/shared/astraea-godot-production-20261003');P=Path('/workspace/shared/astraea-catalogue-continuation-20261002/assets/grand_lantern_theater_section')
script=R/'census_bridge_receivers.gd';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
run=R/'bridge_census_run001';assert not run.exists();run.mkdir();out=run/'retained_world_census.json';log=run/'godot.log';home=run/'xdg';home.mkdir()
paths=[p for p in G.rglob('*')if p.is_file()and not {'.git','.godot'}&set(p.relative_to(G).parts)]
before={str(p.relative_to(G)):sha(p)for p in paths};(run/'GAME_SOURCE_PINS.json').write_text(json.dumps(before,indent=2)+'\n')
command=['/usr/local/bin/godot','--headless','--path',str(G),'--log-file',str(run/'engine.log'),'--script',str(script),'--','--package',str(P),'--output',str(out)]
env=dict(os.environ,XDG_DATA_HOME=str(home),XDG_CONFIG_HOME=str(home),XDG_CACHE_HOME=str(home));start=time.time()
with log.open('x') as f:result=subprocess.run(command,stdout=f,stderr=subprocess.STDOUT,env=env,timeout=210)
after={str(p.relative_to(G)):sha(p)for p in G.rglob('*')if p.is_file()and not {'.git','.godot'}&set(p.relative_to(G).parts)}
changed=[k for k in sorted(set(before)|set(after))if before.get(k)!=after.get(k)]
receipt={'started_utc':datetime.datetime.fromtimestamp(start,datetime.timezone.utc).isoformat(),'finished_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'command':command,'exit_code':result.returncode,'elapsed_s':time.time()-start,'script_sha256':sha(script),'source_geometry_sha256':sha(P/'source/geometry.json'),'game_files_pinned':len(before),'game_source_changed':changed,'census_output':str(out)if out.exists() else None,'census_sha256':sha(out)if out.exists() else None,'log_sha256':sha(log),'scope':'Read-only actual main-scene census; candidates require exact classification; no floor/route/operation acceptance'}
(run/'run_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');assert not changed,changed
print(json.dumps(receipt,indent=2));raise SystemExit(result.returncode)
