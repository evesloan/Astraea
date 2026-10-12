import ctypes, ctypes.wintypes as w, subprocess, sys, pathlib, json, time
K=ctypes.WinDLL('kernel32',use_last_error=True)
K.CreateMutexW.argtypes=[w.LPVOID,w.BOOL,w.LPCWSTR];K.CreateMutexW.restype=w.HANDLE
K.WaitForSingleObject.argtypes=[w.HANDLE,w.DWORD];K.WaitForSingleObject.restype=w.DWORD
K.ReleaseMutex.argtypes=[w.HANDLE];K.CloseHandle.argtypes=[w.HANDLE]
h=K.CreateMutexW(None,False,'Local\\Astraea_SolBatch_20261008_HeavyBuild')
if not h:raise ctypes.WinError(ctypes.get_last_error())
held=False
try:
 print('Waiting for shared heavy-build mutex',flush=True)
 while True:
  status=K.WaitForSingleObject(h,30000)
  if status in (0,128):held=True;break
  if status!=258:raise RuntimeError('mutex wait failed '+str(status))
  print('Still waiting for shared heavy-build mutex',flush=True)
 # Check all surviving heavy jobs, including jobs outside the five-batch system.
 ps=subprocess.check_output(['powershell','-NoProfile','-Command',"Get-CimInstance Win32_Process | Where-Object { $_.Name -match '^(blender|godot.*)\\.exe$' } | Select-Object ProcessId,Name,CommandLine | ConvertTo-Json -Compress"],text=True).strip()
 while ps:
  print('Existing heavy process; safely queued:',ps,flush=True)
  time.sleep(30)
  ps=subprocess.check_output(['powershell','-NoProfile','-Command',"Get-CimInstance Win32_Process | Where-Object { $_.Name -match '^(blender|godot.*)\\.exe$' } | Select-Object ProcessId,Name,CommandLine | ConvertTo-Json -Compress"],text=True).strip()
 print('Mutex acquired; no surviving Blender/Godot process. Abandoned='+str(status==128),flush=True)
 exe=pathlib.Path('C:/Users/cered/Dolphin/AstraeaTools/blender-4.3.2-windows-x64/blender.exe')
 cmd=[str(exe),'--background','--factory-startup','--threads','2','--python-exit-code','2','--python',sys.argv[1],'--']+sys.argv[2:]
 print('Launching serialized Blender, threads=2',flush=True)
 result=subprocess.run(cmd)
 sys.exit(result.returncode)
finally:
 if held:K.ReleaseMutex(h)
 K.CloseHandle(h)
