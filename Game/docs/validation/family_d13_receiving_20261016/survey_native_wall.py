import bpy,json,hashlib
from pathlib import Path
R=Path('/workspace/Astraea');E=Path('/workspace/family-d13-integration');rows=[]
files=['RetainedConstruction/group3/payloads/BlenderCatalogue/assets/group3_crew_service_20261009/extensions/remaining_riser_sources_batch017/source/AST-STF-G3-034.blend']
for f in files:
 bpy.ops.wm.open_mainfile(filepath=str(R/f));near=[]
 for o in bpy.data.objects:
  if o.type!='MESH':continue
  vs=[o.matrix_world@v.co for v in o.data.vertices];vs=[(v.x,v.z,-v.y)for v in vs];lo=[min(v[i]for v in vs)for i in range(3)];hi=[max(v[i]for v in vs)for i in range(3)]
  if all(lo[i]<[47,87.5,497][i]and hi[i]>[18,83.7,477][i]for i in range(3)):near.append({'name':o.name,'min':lo,'max':hi})
 rows.append({'native':f,'sha256':hashlib.sha256((R/f).read_bytes()).hexdigest(),'nearby':near})
(E/'NATIVE_WALL_SURVEY.json').write_text(json.dumps(rows,indent=2)+'\n');print([(r['native'],len(r['nearby']))for r in rows])
