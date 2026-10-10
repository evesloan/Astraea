import pathlib,subprocess,sys,json
R=pathlib.Path(__file__).resolve().parent
units=[781,835,859,832,784,814,838,862]
for unit in units:
 O=R/'sections'/f'{unit}_deluxe'
 if (O/'SECTION_CONTRACT.json').exists():
  assert json.loads((O/'EXPORT_VERIFICATION.json').read_text())['status']=='PASS';continue
 print('Sequential central source',unit,flush=True)
 with (R/f'central_{unit}_build.log').open('w',encoding='utf8') as f:
  result=subprocess.run([sys.executable,str(R/'heavy.py'),str(R/'build_deluxe_central.py'),str(unit)],stdout=f,stderr=subprocess.STDOUT)
 if result.returncode:raise RuntimeError('Preserved central source failure '+str(unit))
 print('Native/export complete, actual pixels pending',unit,flush=True)
