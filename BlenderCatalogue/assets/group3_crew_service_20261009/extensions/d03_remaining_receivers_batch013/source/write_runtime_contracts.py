"""Write complete group-local runtime contracts, including all actual source fixture datums."""
from pathlib import Path
import json,hashlib,shutil
HERE=Path(__file__).resolve().parents[1];ROOT=HERE.parents[4]
BANK=HERE.parent/'labelled_crew_bank_batch014'
def write(folder,source,target,fixture_specs=None):
 p=json.load(open(folder/'source'/source))
 p['model_pins']={f.name:hashlib.sha256(f.read_bytes()).hexdigest()for f in sorted((folder/'exports').glob('*.glb'))}
 if fixture_specs:
  p['fixtures']=[q for f in fixture_specs for q in json.load(open(folder/'source'/f))['fixtures']]
  assert len(p['fixtures'])==p['fixture_count']==33
 else:assert len(p['fixtures'])==48
 destination=ROOT/'Game/data/architecture/group3_completion_20261011'/target
 destination.write_text(json.dumps(p,indent=2)+'\n')
 for f in (folder/'exports').glob('*.glb'):shutil.copyfile(f,ROOT/'Game/assets/models/group3_completion_20261011'/f.name)
write(HERE,'PRECINCT_CONTRACT.json','D03_PRECINCT.json',[
 'TRAINING_RECEIVER.json','ADMINISTRATION_RECEIVER.json','UNIFORMS_RECEIVER.json',
 'UNIFORM_STREET_EXTENSION.json','SELECTED_STREET_PRECINCTS.json'])
write(BANK,'LABELLED_BANK_CONTRACT.json','LABELLED_BANK.json')
