from pathlib import Path
import json,hashlib,subprocess
W=Path(__file__).resolve().parent;R=W.parents[2];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()
assert head==json.load(open(str(R)+'-AFT-CROWN-SITTING-BAYS-AUTHORED-REMOTE_VERIFICATION.json'))['commit']
for suffix in ['REMOTE','LOCAL','CHAIN']:
 receipt=json.load(open(str(R)+'-AFT-CROWN-SITTING-BAYS-AUTHORED-'+suffix+'_VERIFICATION.json'));assert receipt['commit']==head and receipt['status'].startswith('PASS')
P=json.load(open(W/'PLAN.json'));assert not P['active']
assert sha(R/'Game/scripts/ship.gd')==P['source_pins']['Game/scripts/ship.gd']
assert P['sealed_receipt_sha256']==sha(R/'Game/artifacts/aft_crown_sitting_bays_geometry.json')
old=(R/'Game/scripts/ship.gd').read_bytes();pre=W/'INTEGRATION_PREIMAGE_ship.gd';assert not pre.exists();pre.write_bytes(old)
anchor=b'\tload("res://scripts/d04_starboard_aft_commons_enclosure.gd").build(self)\n';line=b'\tload("res://scripts/aft_crown_sitting_bays.gd").build(self)\n';assert old.count(anchor)==1 and line not in old
P['active']=True;P['independently_retained_inactive_geometry_commit']=head
for f in [W/'PLAN.json',W/'RUNTIME_PLAN.json',R/'Game/data/architecture/AFT_CROWN_SITTING_BAYS.json']:f.write_text(json.dumps(P,indent=2)+'\n')
(R/'Game/scripts/ship.gd').write_bytes(old.replace(anchor,anchor+line));assert (R/'Game/scripts/ship.gd').read_bytes().replace(line,b'')==old
(W/'INTEGRATION_RECEIPT.json').write_text(json.dumps({'inactive_geometry_commit':head,'source_ship_sha256':sha(pre),'source_geometry_seal_sha256':P['sealed_receipt_sha256'],'only_added_line':line.decode().strip(),'original_source_bytes_otherwise_unchanged':True,'active':True},indent=2)+'\n');print('Integrated exact one-line shared lower route after independent retention')
