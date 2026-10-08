import ctypes,subprocess,sys,pathlib,json,time,datetime
from ctypes import wintypes
base=pathlib.Path(__file__).resolve().parent
k=ctypes.WinDLL('kernel32',use_last_error=True); k.CreateMutexW.argtypes=[ctypes.c_void_p,wintypes.BOOL,wintypes.LPCWSTR];k.CreateMutexW.restype=wintypes.HANDLE;k.WaitForSingleObject.argtypes=[wintypes.HANDLE,wintypes.DWORD];k.WaitForSingleObject.restype=wintypes.DWORD;k.ReleaseMutex.argtypes=[wintypes.HANDLE];k.CloseHandle.argtypes=[wintypes.HANDLE]
h=k.CreateMutexW(None,False,r'Local\Astraea_SolBatch_20261008_HeavyBuild');owned=False
if not h:raise ctypes.WinError(ctypes.get_last_error())
try:
 print('Waiting for shared heavy mutex',flush=True)
 while True:
  status=k.WaitForSingleObject(h,60000)
  if status in (0,0x80):owned=True;break
  if status!=0x102:raise RuntimeError('Mutex wait failure '+str(status))
 # Any surviving heavy job blocks this worker, even after abandoned ownership.
 cmd="Get-CimInstance Win32_Process | Where-Object { $_.Name -match '^(blender|godot.*)\\.exe$' } | Select-Object ProcessId,Name,CommandLine | ConvertTo-Json -Compress"
 check=subprocess.run(['powershell','-NoProfile','-Command',cmd],capture_output=True,text=True,check=True)
 if check.stdout.strip():
  (base/'heavy_process_blocker.json').write_text(check.stdout);raise RuntimeError('Surviving heavy process; inspect blocker; no process stopped')
 print('Acquired shared heavy mutex',flush=True)
 section=sys.argv[1];mode=sys.argv[2] if len(sys.argv)>2 else 'build';out=base/section/'qa';out.mkdir(parents=True,exist_ok=True)
 receipt={'mutex':r'Local\Astraea_SolBatch_20261008_HeavyBuild','wait_status':status,'pid':__import__('os').getpid(),'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'threads':4}
 (out/('mutex_'+mode+'.json')).write_text(json.dumps(receipt,indent=2))
 blender=pathlib.Path(__import__('os').environ.get('ASTRAEA_BLENDER_EXE',str(base.parents[3]/'AstraeaTools/blender-4.3.2-windows-x64/blender.exe')))
 args=[str(blender),'--background','--factory-startup','--threads','4','--python-exit-code','1','--python',str(base/('verify_sections.py' if mode=='verify' else 'render_sections.py' if mode.startswith('render') and (base/'render_sections.py').exists() else 'build_sections.py')),'--',section,mode]
 with (out/(mode+'.log')).open('w',encoding='utf8') as log:
  job=subprocess.Popen(args,stdout=log,stderr=subprocess.STDOUT);code=job.wait()
 if code==0 and mode=='full':
  args=[str(blender),'--background','--factory-startup','--threads','4','--python-exit-code','1','--python',str(base/'verify_sections.py'),'--',section,'verify']
  with (out/'verify.log').open('w',encoding='utf8') as log:
   job=subprocess.Popen(args,stdout=log,stderr=subprocess.STDOUT);code=job.wait()
 receipt.update(exit_code=code,finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());(out/('mutex_'+mode+'.json')).write_text(json.dumps(receipt,indent=2));print('Completed',section,mode,'exit',code,flush=True)
 if code:raise SystemExit(code)
finally:
 if owned:k.ReleaseMutex(h)
 k.CloseHandle(h)
