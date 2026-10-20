"""Read-only native inspection. Run only with coordinated Blender slot."""
import bpy,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];ROOT=R.parents[1]
p=ROOT/'BlenderCatalogue/assets/d17_connected_royalty/source/AST-RES-006.blend'
assert hashlib.sha256(p.read_bytes()).hexdigest()=='9af75155605ca3c8b0f17cd31c1f7455f1afb54579772d11d9fcae13685d7224'
bpy.ops.wm.open_mainfile(filepath=str(p))
rows=[]
for o in bpy.context.scene.objects:
 row={'name':o.name,'type':o.type,'hide_render':o.hide_render,'properties':{k:str(o[k]) for k in o.keys()}}
 if o.type=='MESH':
  vv=[o.matrix_world@v.co for v in o.data.vertices];world=[[v.x,v.z,-v.y] for v in vv]
  row.update(vertices=len(vv),bounds_world=[[min(v[a] for v in world) for a in range(3)],[max(v[a] for v in world) for a in range(3)]],materials=[m.name for m in o.data.materials])
  if o.name=='CR_RoyaltyLowerRoof':row['world_vertices']=world
 rows.append(row)
(R/'evidence/NATIVE_INSPECTION.json').write_text(json.dumps({'original_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'blender':bpy.app.version_string,'objects':rows},indent=2)+'\n')
print('ROYALTY_NATIVE_INSPECTED',len(rows))
