"""Read-only saved derivative verification; original candidate stays untouched."""
from pathlib import Path
import bpy,json,hashlib
R=Path(__file__).resolve().parents[1];proof=json.loads((R/'qa/LABEL_CORRECTION_BUILD.json').read_text());p=R/'source/AST-STF-010_home_dogleg_labels002.blend';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();assert sha(p)==proof['source_sha256'];bpy.ops.wm.open_mainfile(filepath=str(p));bpy.context.view_layer.update()
def signature(o):
 if o.type!='MESH':return {'type':o.type,'matrix':[list(row)for row in o.matrix_world]}
 return {'matrix':[list(row)for row in o.matrix_world],'vertices':[list(v.co)for v in o.data.vertices],'polygons':[list(p.vertices)for p in o.data.polygons],'uvs':[[list(q.uv)for q in layer.data]for layer in o.data.uv_layers],'materials':[m.name for m in o.data.materials]}
def sig(o):return hashlib.sha256(json.dumps(signature(o),sort_keys=True,separators=(',',':')).encode()).hexdigest()
for name,h in proof['unchanged_objects'].items():assert sig(bpy.data.objects[name])==h,name
for label in proof['labels']:
 o=bpy.data.objects[label['name']];assert o.type=='MESH'and o.get('collision_contract')=='none'and o.get('label_text')==label['text'];assert o.data.materials[0].get('astraea_material_role')=='staff_rubber';actual_height=(max(v.co.y for v in o.data.vertices)-min(v.co.y for v in o.data.vertices))*o.scale.y;assert abs(actual_height-label['height_m'])<.002 and actual_height>.08
assert sha(p)==proof['source_sha256'];assert sha(R.parent/'source/AST-STF-010_home_dogleg.blend')==proof['input_source_sha256'];report={'status':'PASS_SAVED_LABEL_DERIVATIVE','source_sha256':sha(p),'all_nontext_objects_unchanged':len(proof['unchanged_objects']),'labels':proof['labels'],'original_source_unchanged':True,'no_geometry_wall_floor_door_change':True};(R/'qa/REOPEN.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
