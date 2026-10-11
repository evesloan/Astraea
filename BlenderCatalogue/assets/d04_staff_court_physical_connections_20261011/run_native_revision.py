"""Launch a reviewed Blender script once; Python failures have nonzero status."""
from pathlib import Path
import subprocess,sys
if len(sys.argv)!=3:raise SystemExit('Usage: run_native_revision.py script.py unique_log_path')
script,log=map(Path,sys.argv[1:])
if not script.is_file() or script.suffix!='.py':raise SystemExit('Expected reviewed local Python script')
with open(log,'xb')as output:
 result=subprocess.run(['/usr/bin/blender','--background','--python-exit-code','1','--python',str(script.resolve())],stdout=output,stderr=subprocess.STDOUT)
raise SystemExit(result.returncode)
