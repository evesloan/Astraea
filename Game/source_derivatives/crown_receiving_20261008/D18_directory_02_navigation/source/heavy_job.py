import ctypes,ctypes.wintypes as w,subprocess,sys,time,pathlib,json,datetime
k=ctypes.WinDLL('kernel32',use_last_error=True)
k.CreateMutexW.argtypes=[ctypes.c_void_p,w.BOOL,w.LPCWSTR];k.CreateMutexW.restype=w.HANDLE
k.WaitForSingleObject.argtypes=[w.HANDLE,w.DWORD];k.WaitForSingleObject.restype=w.DWORD
k.ReleaseMutex.argtypes=[w.HANDLE];k.CloseHandle.argtypes=[w.HANDLE]
name=r'Local\Astraea_SolBatch_20261008_HeavyBuild'
h=k.CreateMutexW(None,False,name)
if not h:raise ctypes.WinError(ctypes.get_last_error())
held=False
def heavy():
 p=subprocess.run(['powershell','-NoProfile','-Command',"Get-Process blender,godot,godot_console -ErrorAction SilentlyContinue | Select-Object Id,ProcessName | ConvertTo-Json -Compress"],capture_output=True,text=True)
 return p.stdout.strip()
try:
 print('WAITING',name,datetime.datetime.now(datetime.timezone.utc).isoformat(),flush=True)
 while True:
  rc=k.WaitForSingleObject(h,1000)
  if rc in [0,128]:held=True;break
  if rc!=258:raise RuntimeError('mutex wait '+str(rc))
 processes=heavy()
 if processes:raise RuntimeError('Surviving heavy processes; job refused: '+processes)
 print('ACQUIRED',name,'abandoned' if rc==128 else 'clean',flush=True)
 cmd=sys.argv[1:]
 if not cmd:raise RuntimeError('Command required')
 if pathlib.Path(cmd[0]).name.lower().startswith('blender') and ('--threads' not in cmd or cmd[cmd.index('--threads')+1]!='4'):raise RuntimeError('Blender must use --threads 4')
 print('START',datetime.datetime.now(datetime.timezone.utc).isoformat(),flush=True)
 result=subprocess.call(cmd)
 print('END',datetime.datetime.now(datetime.timezone.utc).isoformat(),result,flush=True)
 sys.exit(result)
finally:
 if held:k.ReleaseMutex(h)
 k.CloseHandle(h)

