"""Select the validated physical package; operating admission remains held."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[2];G=R/'Game';D=G/'orchard_tram_interior_20261025/integration'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
e=R.parent/'Astraea-resume-20261025'
for run in ['029','030','032']:
 s=json.loads((e/f'orchard-receiving-check-{run}/summary.json').read_text());assert s['exit_code']==0 and not s['forced_stop']
clear=json.loads((e/'orchard-receiving-check-029/result.json').read_text());assert clear['status']=='PASS_INSTALLED_RESERVED_INTERVAL' and not clear['hits'] and not clear['component_sweep']['hits']
boarding=json.loads((e/'orchard-receiving-check-030/result.json').read_text());assert not boarding['failures'] and len(boarding['checks'])==14
view=json.loads((e/'orchard-receiving-check-032/result.json').read_text());assert view['verified_arrival']
copies=[('scripts/group7_roof_connection_integration_20261025/bootstrap.gd','bootstrap.gd','res://scenes/launcher_group7_roof_connection_integrated_20261025.tscn','res://orchard_tram_interior_20261025/integration/launcher.tscn'),('scripts/group7_roof_connection_integration_20261025/launcher.gd','launcher.gd','res://scenes/main_group7_roof_connection_integrated_20261025.tscn','res://orchard_tram_interior_20261025/integration/main.tscn'),('scenes/bootstrap_group7_roof_connection_integrated_20261025.tscn','bootstrap.tscn','res://scripts/group7_roof_connection_integration_20261025/bootstrap.gd','res://orchard_tram_interior_20261025/integration/bootstrap.gd'),('scenes/launcher_group7_roof_connection_integrated_20261025.tscn','launcher.tscn','res://scripts/group7_roof_connection_integration_20261025/launcher.gd','res://orchard_tram_interior_20261025/integration/launcher.gd')]
for source,out,old,new in copies:
 s=(G/source).read_text(encoding='utf-8');assert s.count(old)==1;target=D/out;assert not target.exists();target.write_text(s.replace(old,new),encoding='utf-8')
 assert target.read_text(encoding='utf-8').replace(new,old)==s
project=G/'project.godot';before=project.read_text(encoding='utf-8');old='res://scenes/bootstrap_group7_roof_connection_integrated_20261025.tscn';new='res://orchard_tram_interior_20261025/integration/bootstrap.tscn';assert before.count(old)==1
manifest=G/'scripts/runtime_contracts_20261022/SOURCE_CONTRACTS.json';old_sha=sha(manifest);prior=json.loads(manifest.read_text());existing={x['path']:x for x in prior}
owned=json.loads((D/'CONTRACTS.json').read_text())['owned'];required=set(owned)
required.update('res://orchard_tram_interior_20261025/integration/'+p.name for p in D.iterdir() if p.suffix in ['.gd','.tscn','.json'])
required.update(['res://orchard_tram_interior_20261025/r007/OrchardReceiving_exact.glb','res://orchard_tram_interior_20261025/r007/FINAL.json'])
add=[]
for key in sorted(required):
 p=G/key.removeprefix('res://');row={'path':key,'sha256':sha(p),'bytes':p.stat().st_size}
 if key in existing:assert existing[key]==row,key
 else:add.append(row)
updated=prior+add;assert updated[:len(prior)]==prior
manifest.write_bytes((json.dumps(updated,indent=2)+'\n').encode());project.write_bytes(before.replace(old,new).encode())
receipt={'status':'PHYSICAL_INTEGRATION_SELECTED_OPERATIONS_HELD','previous_main':old,'selected_main':new,'previous_manifest_sha256':old_sha,'previous_entries_unchanged':len(prior),'added_entries':add,'total_editor_contracts':len(updated),'manifest_sha256':sha(manifest),'launcher_changes':'Only exact main/bootstrap resource paths; original menu, settings, readiness and export-contract mount logic unchanged','normal_start':'Original default player spawn and CENTRAL vehicle pose; diagnostic station spawn requires explicit CLI flag','passed':['Installed reserved clearance and original vehicle/cart component geometry029','Original stationary lift/player boarding/alighting030','Original end-glazing presentation correction031/032'],'held':['Actual loaded cart boarding','Ordinary travel and moving RID resource failure','Grand-space visual/artistic acceptance; side view constrained','Aquatic interior route','Remaining eight-group physical/operational gates','Measured hardware performance and matching Windows'],'visual_review':'Actual images inspected. Two restored warm fixtures and metre-scaled receiving surfaces improve station readability. End glazing now reveals route. Original portal framing/room surfaces constrain side view; no final architectural approval.'}
out=R/'recovery/orchard_tram_interior_20261025/PHYSICAL_INTEGRATION.json';assert not out.exists();out.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in receipt.items() if k!='added_entries'}))
