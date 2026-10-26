"""Select only after installed route, stationary boarding and circulation gates."""
from pathlib import Path
import json,hashlib,subprocess
R=Path(__file__).resolve().parents[2];G=R/'Game';D=G/'aquatic_tram_interior_20261026/integration';E=R.parent/'Astraea-resume-20261025'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()=='3a00b5308b58085381817f62d6a7f1c273867f59'
r=json.loads((E/'aquatic-receiving-check-034/result.json').read_text());assert r['status']=='PASS_INSTALLED_RESERVED_INTERVAL' and not r['hits'] and not r['component_sweep']['hits']
assert r['failures']==['Player enters original upper lift physically']
for check in ['Original player physically crosses bridge into car','Original player returns physically to station','Tram remained stationary throughout']:assert check in r['checks']
s=json.loads((E/'aquatic-receiving-check-051/summary.json').read_text());assert s['exit_code']==0 and not s['forced_stop']
c=json.loads((E/'aquatic-receiving-check-051/result.json').read_text());assert not c['failures']
for check in ['Original cabin carries standing actor to lower gallery','Actual stair terminates at station datum']:assert check in c['checks']
manifest=G/'scripts/runtime_contracts_20261022/SOURCE_CONTRACTS.json';prior=json.loads(manifest.read_text());old_sha=sha(manifest)
assert len(prior)==18039
for row in prior:
 p=G/row['path'].removeprefix('res://');assert p.stat().st_size==row['bytes'] and sha(p)==row['sha256'],row['path']
O=G/'orchard_tram_interior_20261025/integration';sources=[]
for name in ['bootstrap.gd','bootstrap.tscn','launcher.gd','launcher.tscn','check_selected_launcher.gd']:
 src=O/name;out=D/name;assert not out.exists();text=src.read_text(encoding='utf-8');text=text.replace('res://orchard_tram_interior_20261025/integration/','res://aquatic_tram_interior_20261026/integration/')
 if name=='check_selected_launcher.gd':text=text.replace('installed ship checks029/030/032 remain separate','installed aquatic checks034/051 remain separate')
 out.write_bytes(text.encode());sources.append({'source':src.relative_to(R).as_posix(),'source_sha256':sha(src),'output':out.relative_to(R).as_posix(),'output_sha256':sha(out)})
subprocess.run(['python',str(R/'recovery/aquatic_tram_interior_20261026/refresh_integration_contracts.py')],check=True)
owned=json.loads((D/'CONTRACTS.json').read_text())['owned'];required=set(owned)|{'res://aquatic_tram_interior_20261026/integration/CONTRACTS.json'}
existing={r['path']:r for r in prior};add=[]
for key in sorted(required):
 p=G/key.removeprefix('res://');row={'path':key,'sha256':sha(p),'bytes':p.stat().st_size}
 if key in existing:assert existing[key]==row
 else:add.append(row)
project=G/'project.godot';before=project.read_text(encoding='utf-8');old='res://orchard_tram_interior_20261025/integration/bootstrap.tscn';new='res://aquatic_tram_interior_20261026/integration/bootstrap.tscn';assert before.count(old)==1
manifest.write_bytes((json.dumps(prior+add,indent=2)+'\n').encode());project.write_bytes(before.replace(old,new).encode())
receipt={'status':'PHYSICAL_INTEGRATION_SELECTED_OPERATIONS_HELD','previous_main':old,'selected_main':new,'previous_manifest_sha256':old_sha,'previous_entries_unchanged':len(prior),'added_entries':add,'total_editor_contracts':len(prior+add),'manifest_sha256':sha(manifest),'launcher_source_copies':sources,'passed':['Installed full reservation and original vehicle/cart/door components034','Original stationary bridge/gate/player boarding/alighting034','Original occupied lift and physical circulation051'],'held':['Moving tram and loaded cart operation','Moving RID/resource stability','Hardware performance and60FPS target','Final1970s material/greenery/guest-space artistic completion','Remaining all-group operational boundaries','Matching Windows build'],'normal_start':'Original default player and CENTRAL tram; diagnostic station spawn only by explicit flag','visual_review':'Four actual034 images inspected. Interior grand-room participation demonstrated; surrounding dark broad surfaces and guest-space depth unfinished, not final architectural approval.'}
out=R/'recovery/aquatic_tram_interior_20261026/PHYSICAL_INTEGRATION.json';assert not out.exists();out.write_bytes((json.dumps(receipt,indent=2)+'\n').encode());print(json.dumps({'selected':new,'contracts':len(prior+add),'previous_unchanged':len(prior),'added':len(add)}))
