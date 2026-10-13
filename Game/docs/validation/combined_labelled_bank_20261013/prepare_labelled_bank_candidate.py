from pathlib import Path
import json,hashlib,zipfile,datetime
C=Path(__file__).parent;S=C/'g3_first_receiving_staging/Game';I=C/'g3_first_import';sha=lambda b:hashlib.sha256(b).hexdigest()
p=json.loads((S/'data/architecture/group3_completion_20261011/LABELLED_BANK.json').read_text());writes={};stems=[Path(f).stem for f in p['model_pins']]
for f,h in p['model_pins'].items():
 k='assets/models/group3_completion_20261011/'+f;assert sha((S/k).read_bytes())==h;writes[k]=(S/k).read_bytes();writes[k+'.import']=(I/(k+'.import')).read_bytes()
for q in (I/'assets/models/group3_completion_20261011').iterdir():
 if q.is_file()and q.suffix in ['.png','.import']and any(q.name.startswith(x+'_')for x in stems):writes[str(q.relative_to(I))]=q.read_bytes()
for q in (I/'.godot/imported').iterdir():
 if q.is_file()and any(q.name.startswith(x)for x in stems):writes[str(q.relative_to(I))]=q.read_bytes()
key='scripts/group3_completion_20261011/labelled_bank.gd';original=(S/key).read_text();code=original
anchor=' var n:=Node3D.new();n.name="Group3LabelledCrewBank";ship.get_node("ShipSpace").add_child(n)'
assert code.count(anchor)==1
pre=' for f in p.model_pins:\n  assert(FileAccess.get_sha256("res://assets/models/group3_completion_20261011/"+f)==p.model_pins[f])\n'
code=code.replace(anchor,pre+anchor)
code=code.replace('load("res://scripts/service_door.gd").new()','load("res://scripts/group3_completion_20261011/bank_entry_gate.gd").new()')
code=code.replace('n.set_meta("C036_migration_applied",false)','n.set_meta("C036_migration_applied",false);n.set_meta("authoritative_identity_mapping",false);n.set_meta("private_entry_admitted",false);n.set_meta("default_main_adoption",false)')
writes[key]=code.encode();writes['data/architecture/group3_completion_20261011/LABELLED_BANK.json']=(S/'data/architecture/group3_completion_20261011/LABELLED_BANK.json').read_bytes()
# Consumer-specific orientation: native bank street is local negative Z on both opposing gates.
writes['scripts/group3_completion_20261011/bank_entry_gate.gd']=b'''extends "res://scripts/service_door.gd"
# Preserve native doors and inside egress. No external admission without owner permission.
var can_enter:Callable
var authorization_denied:=false
func interact(actor:CharacterBody3D)->void:
 if not desired_open and to_local(actor.global_position).z<=.25:
  if not can_enter.is_valid()or not can_enter.call(actor):
   authorization_denied=true;return
 authorization_denied=false;super.interact(actor)
func get_interaction_label()->String:
 if authorization_denied:return "Private entry authorization required"
 return super.get_interaction_label()
'''
with zipfile.ZipFile(C/'G3_LABELLED_BANK_CANDIDATE_OVERLAY.zip','w',zipfile.ZIP_DEFLATED,compresslevel=1)as z:
 for k,b in writes.items():z.writestr(k,b)
receipt={'status':'CANDIDATE_ONLY_ACTUAL_RECEIVING_PENDING','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_revision':'6f2d0da67429ea940edf7011348ec08a346f37db','source_script_preimage_sha256':sha(original.encode()),'consumer_script_sha256':sha(code.encode()),'native_model_pins_unchanged':p['model_pins'],'external_permission_unknown_refused':True,'inside_egress_preserved':True,'gate_orientation_evidence':'Both banks street atX87;leftgateX79/yaw-PI2 andrightgateX93/yawPI2 mapstreettolocalnegativeZ','new_registered_berths':0,'identity_save_population_migration_accepted':False,'portable_files':[k for k in writes if not k.startswith('.godot/')]};(C/'G3_LABELLED_BANK_CANDIDATE.json').write_text(json.dumps(receipt,indent=2)+'\n');print('candidate',len(writes),'files',len(p['model_pins']),'native models')
