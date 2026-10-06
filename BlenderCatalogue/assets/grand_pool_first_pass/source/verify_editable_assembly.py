"""Parent-allocated read-only Blender source QA; writes NEW package report only."""
import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
HERE=Path(__file__).resolve().parents[1];ROOT=HERE.parents[1]
c=json.loads((HERE/'source/placement_contract.json').read_text());f=HERE/'source/grand_pool_first_pass_editable_corrected.blend'
assert f.exists(),'Verify the repaired source explicitly; failed original remains retained'
bpy.ops.wm.open_mainfile(filepath=str(f));bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();issues=[];records=[];verts={};bvhs={}
for it in c['placements']:
 coll=bpy.data.collections.get(it['name']);assert coll,it['name'];vv=[];faces=[];materials=set();parts=0
 for ob in coll.objects:
  if ob.type!='MESH':continue
  parts+=1;eo=ob.evaluated_get(deps);m=eo.to_mesh();off=len(vv);vv.extend([eo.matrix_world@v.co for v in m.vertices]);faces.extend([tuple(off+i for i in p.vertices) for p in m.polygons]);materials.update(x.name for x in ob.data.materials if x);eo.to_mesh_clear()
 assert vv and faces
 bvhs[it['name']]=BVHTree.FromPolygons(vv,faces,all_triangles=False);verts[it['name']]=vv
 godot=[(v.x,v.z,-v.y) for v in vv];lo=[min(v[k] for v in godot) for k in range(3)];hi=[max(v[k] for v in godot) for k in range(3)]
 err=max(abs(a-b) for a,b in zip(lo+hi,it['envelope_min_xyz']+it['envelope_max_xyz']))
 if err>.001:issues.append(dict(item=it['name'],source_vs_export_bounds_error_m=err))
 records.append(dict(item=it['name'],editable_mesh_parts=parts,source_bounds_godot=[lo,hi],bounds_max_error_m=err,materials=sorted(materials)))
contacts=[]
for it in c['placements']:
 vv=verts[it['name']];bottom=min(v.z for v in vv);sole=[v for v in vv if v.z<=bottom+.0001];support=it['support'];errors=[]
 if support.startswith('D0'):
  y=next(x['floor_y'] for x in json.loads((ROOT/'assets/grand_pool_orchard_section/source/connected_contract.json').read_text())['floor_regions'] if x['id']==support);errors=[abs(bottom-y)]
 elif support in bvhs:
  for v in sole:
   hit,normal,index,distance=bvhs[support].ray_cast(v+Vector((0,0,.005)),Vector((0,0,-1)),.02)
   errors.append(abs(hit.z-v.z) if hit is not None else 1)
 else:
  sec=json.loads((ROOT/'assets/grand_pool_orchard_section/source/connected_contract.json').read_text());p=next(x for x in sec['source_parts'] if x['name']==support);top=max(v[1] for v in p['world_vertices']);errors=[abs(bottom-top)]
 worst=max(errors);contacts.append(dict(item=it['name'],support=support,bottom_vertex_count=len(sole),max_vertical_contact_error_m=worst))
 if worst>.005:issues.append(dict(item=it['name'],support_contact_error_m=worst))
images=[]
for im in bpy.data.images:
 if im.source not in {'FILE','GENERATED'}:continue
 packed=bool(im.packed_file or im.packed_files);images.append(dict(name=im.name,source=im.source,size=list(im.size),packed=packed))
 if im.source=='FILE' and not packed:issues.append(dict(unpacked_image=im.name))
 if min(im.size)<=0:issues.append(dict(empty_image=im.name))
hashes=[]
for key,a in c['input_inventory'].items():
 for field,h in [('path','sha256'),('editable_source','editable_source_sha256')]:
  actual=hashlib.sha256((ROOT/a[field]).read_bytes()).hexdigest();okay=actual==a[h];hashes.append(dict(asset=key,path=a[field],preserved=okay))
  if not okay:issues.append(dict(changed_retained_input=a[field]))
report=dict(verified_source=str(f.relative_to(HERE)),status='source_checks_pass' if not issues else 'source_checks_failed',source_sha256=hashlib.sha256(f.read_bytes()).hexdigest(),placements=len(records),mesh_parts=sum(x['editable_mesh_parts'] for x in records),records=records,contacts=contacts,images=images,retained_hash_checks=hashes,issues=issues,limitations=['No GLB export or live adoption','Contact rays check assembled retained parent meshes; compiler/soil support uses pinned datum plus earlier footprint checks','No runtime collision/cart/lighting or final first-pass visual acceptance'])
(HERE/'qa/editable_source_report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status=report['status'],placements=report['placements'],parts=report['mesh_parts'],images=len(images),issues=issues),indent=2));assert not issues,'Source QA issues remain'
