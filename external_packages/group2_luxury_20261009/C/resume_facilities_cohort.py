"""Resume only four unaccepted house adjuncts after preserving compact arrival failure."""
import pathlib,sys,subprocess
R=pathlib.Path(__file__).resolve().parent
for house in ['port_central_upper_house','starboard_central_upper_house','port_aft_upper_house','starboard_aft_upper_house']:
 O=R/'facilities'/house;assert not (O/'house_adjunct.blend').exists()
 recipe='build_house_adjunct_compact.py' if 'central' in house else 'build_house_adjunct.py'
 print('Source adjunct',house,flush=True)
 for script,suffix in [(recipe,'build02'),('verify_house_text.py','text')]:
  with (R/f'facility_{house}_{suffix}.log').open('w',encoding='utf8') as f:result=subprocess.run([sys.executable,str(R/'heavy.py'),str(R/script),house],stdout=f,stderr=subprocess.STDOUT)
  assert result.returncode==0,(house,script)
 print('SOURCE_QA_PASS_ACTUAL_PIXELS_PENDING',house,flush=True)
