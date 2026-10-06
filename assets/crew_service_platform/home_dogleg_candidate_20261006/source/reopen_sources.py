"""Independent read-only reopen: editable preservation, concrete bounds and export membership inputs."""
from pathlib import Path
import bpy,json,hashlib,math
R=Path(__file__).resolve().parents[1];D=json.loads((R/'source/HOME_SPEC.json').read_text());PINS=json.loads((R/'source/INPUT_PINS.json').read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def signature(o):
 if o.type!='MESH':return {'type':o.type,'matrix':[list(row)for row in o.matrix_world]}
 return {'matrix':[list(row)for row in o.matrix_world],'vertices':[list(v.co)for v in o.data.vertices],'polygons':[list(p.vertices)for p in o.data.polygons],'uvs':[[list(q.uv)for q in layer.data]for layer in o.data.uv_layers],'materials':[m.name for m in o.data.materials]}
def sig(o):return hashlib.sha256(json.dumps(signature(o),sort_keys=True,separators=(',',':')).encode()).hexdigest()
records=[]
for stem,proof_file,key in[('AST-STF-010_home_dogleg','HOME_RETAINED_85_SIGNATURES.json','before'),('AST-STF-009_pool_market_home','WALL_RETAINED_SIGNATURES.json','unchanged')]:
 p=R/'source'/(stem+'.blend');before=sha(p);build=json.loads((R/'qa'/(stem+'_BUILD.json')).read_text());assert before==build['source_sha256'];bpy.ops.wm.open_mainfile(filepath=str(p));bpy.context.view_layer.update();proof=json.loads((R/'qa'/proof_file).read_text())[key]
 for name,h in proof.items():assert name in bpy.data.objects and sig(bpy.data.objects[name])==h,name
 meshes=[]
 for o in bpy.context.scene.objects:
  if o.type!='MESH':continue
  assert len(o.data.materials)>0 and o.data.uv_layers.active is not None,o.name
  o.data.calc_loop_triangles();vs=[o.matrix_world@v.co for v in o.data.vertices];vv=[(v.x,v.z,-v.y)for v in vs];assert vv and all(math.isfinite(x)for v in vv for x in v)
  meshes.append({'name':o.name,'vertices':len(vv),'triangles':len(o.data.loop_triangles),'bounds_min':[min(v[i]for v in vv)for i in range(3)],'bounds_max':[max(v[i]for v in vv)for i in range(3)],'materials':[m.name for m in o.data.materials],'roles':[m.get('astraea_material_role')for m in o.data.materials],'collision_contract':o.get('collision_contract','static_surface')})
 assert len(meshes)==build['editable_meshes'];assert sum(r['triangles']for r in meshes)==build['triangles'];assert sha(p)==before
 if stem.startswith('AST-STF-010'):
  assert all(r['name']in bpy.data.objects for r in D['retained_home_parts']);assert all(x['name']in bpy.data.objects for x in D['labels']);assert all(bpy.data.objects[x['name']].get('label_text')==x['text']for x in D['labels']);assert not any(o.type=='LIGHT'for o in bpy.context.scene.objects)
 record={'stem':stem,'source_sha256':before,'reopened_unchanged_objects':len(proof),'editable_meshes':len(meshes),'triangles':sum(r['triangles']for r in meshes),'meshes':meshes,'source_unchanged_after_read':True};(R/'qa'/(stem+'_REOPEN.json')).write_text(json.dumps(record,indent=2)+'\n');records.append({k:v for k,v in record.items()if k!='meshes'})
for p,h in PINS.items():assert sha(p)==h,p
print(json.dumps({'status':'PASS_INDEPENDENT_SAVED_SOURCE_REOPEN','records':records,'runtime_or_visual_acceptance':False},indent=2))
