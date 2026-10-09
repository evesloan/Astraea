import subprocess,json,pathlib,sys
p=pathlib.Path(sys.argv[1]).resolve();b=r'C:/Users/cered/Dolphin/AstraeaTools/blender-4.3.2-windows-x64/blender.exe'
for script,args in [('validate.py',[]),('render.py',['--only','fore_archive'])]:
 subprocess.run([b,'--threads','4','--background','--factory-startup','--python-exit-code','1','--python',str(p/'qa'/script),'--',str(p),*args],check=True)
 if script=='validate.py':assert json.loads((p/'qa/validation.json').read_text())['status']=='PASS'
