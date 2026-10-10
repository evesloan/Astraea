from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
W=Path(__file__).resolve().parent;R=W.parents[2];p=R/'BlenderCatalogue/assets/crew_service_platform/home_dogleg_candidate_20261006/source/AST-STF-009_pool_market_home.blend';bpy.ops.wm.open_mainfile(filepath=str(p));c=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 vs=[o.matrix_world@v.co for v in o.data.vertices];g=[(v.x,v.z,-v.y)for v in vs];lo=[min(v[i]for v in g)for i in range(3)];hi=[max(v[i]for v in g)for i in range(3)]
 if hi[1]>=55.59 and lo[1]<=55.75 and hi[0]>=-27.2 and lo[0]<=-22.8 and hi[2]>=-492.2 and lo[2]<=-487.8:c.append({'name':o.name,'min':lo,'max':hi,'vertices':len(vs),'polygons':len(o.data.polygons)})
d={'source':str(p.relative_to(R)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'objects_at_cap':c};(W/'NATIVE_CAP_SURVEY.json').write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(d))
