"""Fixed three uncontested Royalty reservations; preserve protected790 unchanged."""
import pathlib,json,subprocess,sys
R=pathlib.Path(__file__).resolve().parent
assert json.loads((R/'sections/792_royalty/SECTION_CONTRACT.json').read_text())['status']=='BOUNDED_FIT_VERIFIED_EDITABLE_SOURCE_CANDIDATE'
for unit in [794,795,797]:
 O=R/'sections'/f'{unit}_royalty'
 assert not (O/f'{unit}_royalty.blend').exists(),'Preserve any existing candidate before rebuild'
 print('Sequential Royalty source',unit,flush=True)
 with (R/f'royalty_{unit}_build.log').open('w',encoding='utf8') as f:result=subprocess.run([sys.executable,str(R/'heavy.py'),str(R/'build_royalty.py'),str(unit)],stdout=f,stderr=subprocess.STDOUT)
 if result.returncode:raise RuntimeError('Preserved Royalty source failure '+str(unit))
 subprocess.run([sys.executable,str(R/'verify_private_levels.py'),str(unit)],check=True)
 print('Native/export/private-level QA passed; actual pixels pending',unit,flush=True)
