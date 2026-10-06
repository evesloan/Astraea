"""One bounded scratch source build, independent reopen and same-camera8-source view."""
from pathlib import Path
import hashlib,json,datetime,subprocess
R=Path(__file__).resolve().parent;RUN=R/'composed_run001';BASE=Path('/workspace/shared/astraea-catalogue-continuation-20261002/assets/grand_lantern_theater_section/source/AST-CUL-005_firstpass_001.blend');OUT=R/'source/AST-CUL-005_firstpass_002.blend';PINS=R/'COMPOSED_RUN_INPUT_PINS.json';EXPECTED='955492b552bbc4909e84e43de8ae6446a8324353671280dabd158413af39c71d'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
def main():
 assert sha(PINS)==EXPECTED;pin=json.loads(PINS.read_text())
 for path,h in pin['input_sha256'].items():assert sha(path)==h,path
 assert sha(BASE)=='a3f1d01b0927ddd873986b2d1f2dbb44f234bced2b034c2cff42c2c0bfd8d0ce';assert not RUN.exists()and not OUT.exists()
 assert not json.loads((R/'ARCHITECTURE_ROUTE_SCREEN.json').read_text())['failures'];assert not json.loads((R/'FURNITURE_ARCHITECTURE_STANCE_SCREEN.json').read_text())['failures']
 RUN.mkdir();r={'started_utc':now(),'status':'NEW_SCRATCH_SOURCE_BUILD','base_source_sha256':sha(BASE),'input_pins_sha256':EXPECTED,'no_shared_source_or_game_writes':True}
 def save():(RUN/'receipt.json').write_text(json.dumps(r,indent=2)+'\n')
 def engine(script,log,args=[]):
  command=['/usr/bin/blender','--background','--factory-startup','--threads','2','--python-exit-code','1','--python',str(R/script)]+(['--']+args if args else[])
  with (RUN/log).open('xb')as f:p=subprocess.run(command,cwd=R,stdout=f,stderr=subprocess.STDOUT,timeout=900,check=False)
  r[log+'_returncode']=p.returncode;save();assert p.returncode==0,log+' failed; preserve source/log, no blind retry'
 save()
 try:
  engine('build_arrival_revision02_blender.py','build.log');r['source_sha256']=sha(OUT);r['status']='INDEPENDENT_REOPEN';save();engine('verify_arrival_revision02.py','reopen.log');r['status']='EIGHT_SOURCE_SAME_CAMERA_RENDER';save()
  engine('render_arrival_eight_source.py','render.log',['--source-sha',r['source_sha256'],'--output-dir',str(RUN/'images'),'--views','D11_main_arrival','--samples','32'])
  assert sha(BASE)==r['base_source_sha256']and sha(OUT)==r['source_sha256'];r['status']='COMPOSED_SOURCE_AND_IMAGE_READY_FOR_VISUAL_REVIEW';r['completed_utc']=now();r['reopen_report_sha256']=sha(R/'SOURCE_REOPEN_REPORT_002.json');r['render_receipt_sha256']=sha(RUN/'images/render_receipt.json');save();print(json.dumps(r,indent=2))
 except BaseException as exc:r['status']='STOPPED_PRESERVE_ALL_OUTPUTS';r['error']=str(exc);r['completed_utc']=now();save();raise
if __name__=='__main__':main()
