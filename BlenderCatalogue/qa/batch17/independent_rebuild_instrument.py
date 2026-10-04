"""Non-ptrace read instrumentation: Python open events plus actual Blender image datablocks."""
import bpy,sys,runpy,json,hashlib
from pathlib import Path
args=sys.argv[sys.argv.index('--')+1:];generator=Path(args[0]);out=Path(args[1]);stage=generator.parents[3];events=[]
def audit(event,args):
 if event=='open'and args and isinstance(args[0],str):
  p=Path(args[0]).resolve();mode=args[1]if len(args)>1 else''
  if p.is_absolute()and p.is_relative_to(stage):events.append({'path':str(p.relative_to(stage)),'mode':str(mode)})
sys.addaudithook(audit);runpy.run_path(str(generator),run_name='__main__')
images=[]
for im in bpy.data.images:
 p=Path(bpy.path.abspath(im.filepath)).resolve()if im.filepath else None
 if p and p.is_relative_to(stage)and p.exists():images.append({'path':str(p.relative_to(stage)),'image':im.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'packed':bool(im.packed_file)})
out.write_text(json.dumps({'python_open_events':events,'actual_blender_image_files':images,'scope':'Python-level catalogue file-open events plus native-loaded Blender image filepath/packed-data witnesses. Not an OS syscall trace.'},indent=2)+'\n')
