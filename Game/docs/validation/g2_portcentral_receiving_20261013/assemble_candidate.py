from pathlib import Path
import json,shutil,zipfile
P=Path(__file__).parent;T=P/'import/Game';d=json.loads((P/'EXACT_RESOURCE_AND_GUARD_PREIMAGES.json').read_text());assert d['status']=='PASS_PORTCENTRAL_THREE_RESOURCES_AND_GUARD_PREIMAGES';q=T/'data/group2_portcentral_receiving_20261013/PLAN.json';q.write_text(json.dumps(d['plan'],indent=2)+'\n');shutil.copyfile(P/'package.gd',T/'scripts/group2_portcentral_receiving_20261013/package.gd')
with zipfile.ZipFile(P/'CANDIDATE_OVERLAY.zip','w',zipfile.ZIP_DEFLATED,compresslevel=1)as z:
 for folder in[T/'assets',T/'data',T/'scripts',T/'.godot/imported']:
  for q in folder.rglob('*'):
   if q.is_file():z.write(q,str(q.relative_to(T)))
print('PORTCENTRAL_CANDIDATE_READY')
