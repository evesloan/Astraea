from pathlib import Path
import subprocess,os,time,json,socket
P=Path(__file__).parent;R=Path('/workspace/astraea-protected-integration-20261012/Game');E=Path('/workspace/astraea-protected-integration-evidence-20261012');name='g2_family_meal_installed_startup117';env=os.environ.copy()
for k,n in [('XDG_DATA_HOME','data'),('XDG_CONFIG_HOME','config'),('XDG_CACHE_HOME','cache')]:env[k]=str(R/'.godot/validation_state'/n)
config=P/'single_capture_xorg.conf';config.write_text('''Section "ServerFlags"
 Option "AutoAddDevices" "false"
 Option "AutoAddGPU" "false"
 Option "AllowMouseOpenFail" "true"
EndSection
Section "Device"
 Identifier "PrivateCaptureDummy"
 Driver "dummy"
 VideoRam 256000
EndSection
Section "Monitor"
 Identifier "PrivateCaptureMonitor"
 HorizSync 28-85
 VertRefresh 48-76
 Modeline "1280x720" 74.50 1280 1344 1472 1664 720 723 728 748 +HSync +VSync
EndSection
Section "Screen"
 Identifier "PrivateCaptureScreen"
 Device "PrivateCaptureDummy"
 Monitor "PrivateCaptureMonitor"
 DefaultDepth 24
 SubSection "Display"
  Depth 24
  Modes "1280x720"
 EndSubSection
EndSection
''')
display=next(i for i in range(199,210)if not Path(f'/tmp/.X{i}-lock').exists()and not Path(f'/tmp/.X11-unix/X{i}').exists());x=None;ready=False;start=time.monotonic()
with (P/'XORG_STARTUP_STDOUT.log').open('w')as output:
 x=subprocess.Popen(['/usr/bin/Xorg',f':{display}','-config',str(config),'-logfile',str(P/'XORG_CAPTURE.log'),'-nolisten','tcp','-noreset','-novtswitch','-sharevts'],stdout=output,stderr=subprocess.STDOUT)
 for _ in range(40):
  if x.poll()is not None:break
  path=f'/tmp/.X11-unix/X{display}'
  if Path(path).exists():
   try:
    with socket.socket(socket.AF_UNIX)as s:s.connect(path)
    ready=True;break
   except OSError:pass
  time.sleep(.1)
 (P/'DISPLAY_CAPTURE_CAPABILITY.json').write_text(json.dumps({'xorg_dummy_driver_already_installed':True,'existing_display_was_absent':True,'private_local_display_started':ready,'display':f':{display}'if ready else None,'network_listener_enabled':False,'new_install_credentials_or_permissions':False,'xorg_exit_code':x.poll()},indent=2)+'\n')
 try:
  args=['godot','--path',str(R),'--fixed-fps','60','--main-pack','/workspace/astraea-windows-build-evidence-20261012/Astraea_Windows_Preview_47eb835_20261012.zip','--script',str(P/'validate_installed_startup.gd')]
  if ready:env['DISPLAY']=f':{display}';env['ASTRAEA_CAPTURE_MEAL']='1';args+=['--display-driver','x11','--rendering-driver','opengl3','--audio-driver','Dummy','--resolution','1280x720','--disable-render-loop']
  else:args+=['--headless'];print('No usable private display;proceeding with normal headless startup. See XORG_CAPTURE.log',flush=True)
  errors=[]
  with (E/(name+'.log')).open('w')as log:
   process=subprocess.Popen(args,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
   for line in process.stdout:
    log.write(line);log.flush()
    if 'ERROR:'in line or'Assertion failed'in line or'Parse Error'in line:errors.append(line.strip());process.terminate()
   process.wait()
  passed=process.returncode==0 and not errors and 'STARTUP_PASS'in (E/(name+'.log')).read_text();report={'name':name,'exit_code':process.returncode,'errors':errors,'passed':passed,'wall_seconds':time.monotonic()-start,'graphical_capture_attempted':ready,'command':args};(E/(name+'.json')).write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
 finally:
  if x.poll()is None:x.terminate();x.wait(timeout=10)
raise SystemExit(0 if passed else 1)
