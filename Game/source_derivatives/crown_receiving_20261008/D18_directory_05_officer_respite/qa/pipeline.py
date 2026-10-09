"""One section's sequential QA/render; call only through heavy_job.py (mutex already held)."""
import subprocess,sys,pathlib,json
p=pathlib.Path(sys.argv[1]);mode=sys.argv[2] if len(sys.argv)>2 else 'all';blender=r'C:/Users/cered/Dolphin/AstraeaTools/blender-4.3.2-windows-x64/blender.exe'
def run(script,args=()):
 result=subprocess.call([blender,'--threads','4','--background','--factory-startup','--python-exit-code','1','--python',str(script),'--',str(p),*args])
 if result:raise SystemExit(result)
if mode=='all':run(p/'source/build.py')
run(p/'qa/validate.py')
r=json.loads((p/'qa/validation.json').read_text())
if r['status']!='PASS':raise SystemExit('Independent QA failed; rendering held')
run(p/'qa/render.py')

