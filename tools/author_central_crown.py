"""Integrate an explicitly verified six-programme crown kit without new floor slabs."""
from pathlib import Path
import argparse,hashlib,json,shutil
R=Path(__file__).resolve().parents[1]
C=Path('/workspace/shared/astraea-catalogue-continuation-20261002/assets/central_crown')
def write(path,value):path.write_text(json.dumps(value,indent=2)+'\n')
def author(expected_sha):
 source=C/'exports/AST-CMD-001.glb'
 assert hashlib.sha256(source.read_bytes()).hexdigest()==expected_sha,'Export differs from reviewed worker hash'
 data=json.loads((C/'source/section_contract.json').read_text())
 assert data['catalogue_id']=='AST-CMD-001'
 expected={f'D18_directory_{i:02}' for i in range(2,8)}
 assert {p['programme_key'] for p in data['programmes']}==expected
 assert data['public_fore_cross_street']['z']==[-80,-74]
 assert all(min(z for x,z in p['boundary'])>=-74 for p in data['programmes'])
 data['runtime_status']='Integrated construction awaiting runtime and visual acceptance'
 data['export_sha256']=expected_sha
 write(R/'data/architecture/CENTRAL_CROWN_RUNTIME.json',data)
 shutil.copyfile(source,R/'assets/models/AST-CMD-001.glb')
 ledger=json.loads((R/'data/programme_ledger.json').read_text())
 for p in data['programmes']:
  row=next(r for r in ledger['destinations'] if r['programme_key']==p['programme_key'])
  row['current_geometry_owner']='scripts/central_command_crown.gd'
  row['current_boundary_xz']=p['boundary']
  row['current_boundary_authority']='data/architecture/CENTRAL_CROWN_RUNTIME.json'
  row['current_status']='Unfurnished central crown programme shell under integration; operational equipment, runtime and visual acceptance pending'
 assert len(ledger['destinations'])==161
 write(R/'data/programme_ledger.json',ledger)
 layout=json.loads((R/'data/spatial_layout.json').read_text())
 cover=next(r for r in layout['regions'] if r['id']=='D18_starboard_house_cover')
 cover['previous_programme_reservation']='D18_directory_06'
 cover['programme_owner']=None
 cover['status']='Retained opaque starboard-house cover; former Bridge briefing reservation relocated to central crown. No new room or private pavilion assigned here.'
 write(R/'data/spatial_layout.json',layout)
 extension=json.loads((R/'data/architecture/D13_D17_starboard_house_extension.json').read_text())
 extension['historical_protected_above']='D18_directory_06 Bridge briefing'
 extension['protected_above']='Retained physical cover; Bridge briefing now assigned to the central crown shell'
 write(R/'data/architecture/D13_D17_starboard_house_extension.json',extension)
 print(json.dumps({'programmes_integrated':6,'new_floor_slabs':0,'guest_unit_change':0,'geometry_and_art_acceptance':False,'export_sha256':expected_sha}))
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--expected-sha',required=True);args=parser.parse_args();author(args.expected_sha)
