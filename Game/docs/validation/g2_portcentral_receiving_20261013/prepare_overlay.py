from pathlib import Path
import json,hashlib,shutil,zipfile
P=Path(__file__).parent;T=P/'import/Game';assert 'ERROR:'not in(P/'import.log').read_text()
q=T/'scripts/group2_portcentral_receiving_20261013/guard_window_successor.gd';q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(P/'guard_window_successor.gd',q)
with zipfile.ZipFile(P/'CANDIDATE_OVERLAY.zip','w',zipfile.ZIP_DEFLATED,compresslevel=1)as z:
 for folder in[T/'assets',T/'data',T/'scripts',T/'.godot/imported']:
  for q in folder.rglob('*'):
   if q.is_file():z.write(q,str(q.relative_to(T)))
print('PORTCENTRAL_OVERLAY_READY')
