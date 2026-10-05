"""Reversible exact four-object low-bay revision. Rebuilds from retained Git source.
The two toes and all unrelated meshes/materials/markers are left byte-for-byte in source data.
"""
from pathlib import Path
from collections import Counter
import bpy,bmesh,json,hashlib,subprocess,tempfile,struct,math
from mathutils import Vector
R=Path(__file__).resolve().parents[1];C=R.parents[1];P=C/'assets/aft_crown_platform';BASE='62ecbc2c24d9a64c4999c8e7afc25bfc7ed3f4b8'
assert all(a['catalogue_id']!='AST-CMD-005' or a['family']=='aft_crown_platform'for a in json.loads((C/'catalogue_manifest.json').read_text())['assets'])
freeze=json.loads((R/'qa/preauthor_baseline.json').read_text());allow={q['old_name']:q for q in freeze['guard_migration']}
def original(path):return subprocess.check_output(['git','-C',str(C),'show',BASE+':'+path])
basepath=Path(tempfile.gettempdir())/'upper_horizon_original_005.blend';basepath.write_bytes(original('assets/aft_crown_platform/source/AST-CMD-005.blend'))
bpy.ops.wm.open_mainfile(filepath=str(basepath))
def objdata(o):
 d={'type':o.type,'matrix':[list(row)for row in o.matrix_world],'props':dict(o.items())}
 if o.type=='MESH':d.update(vertices=[list(v.co)for v in o.data.vertices],polys=[list(p.vertices)for p in o.data.polygons],uv=[list(v.uv)for v in o.data.uv_layers.active.data],materials=[m.name for m in o.data.materials],poly_materials=[p.material_index for p in o.data.polygons])
 return d
def h(o):return hashlib.sha256(json.dumps(objdata(o),sort_keys=True).encode()).hexdigest()
before={o.name:h(o)for o in bpy.context.scene.objects};materials_before={m.name:m.as_pointer()for m in bpy.data.materials}
ledger=json.loads(original('assets/aft_crown_platform/source/geometry_parts.json'));oldrecords={q['name']:q for q in ledger['parts']};newrecords=[];audit=[]
for name,map_ in allow.items():
 old=bpy.data.objects[name];olddata=objdata(old);a=map_['old_aabb'];uvlayer=old.data.uv_layers.active.data
 # Source cuboids have affine per-face metric UVs. Preserve old boundary vertices/UVs exactly;
 # interpolate only the new Z cuts. Added closure faces use the original end-face affine map.
 for spec in map_['replacement']:
  me=old.data.copy();ob=old.copy();ob.data=me;ob.name=spec['name'];me.name=spec['name'];bpy.context.collection.objects.link(ob)
  lo,hi=spec['z'];newy=spec['y'];oldlo,oldhi=a[4:6];ya,yb=a[2:4]
  originals=[v.co.copy()for v in old.data.vertices]
  for v in me.vertices:
   q=v.co;zz=-q.y;q.y=-(lo if abs(zz-oldlo)<abs(zz-oldhi)else hi)
   if spec['name'].endswith('__low_bay'):q.z=newy[0]if abs(q.z-ya)<abs(q.z-yb)else newy[1]
  # Map each updated face through the source face basis. This preserves world-space texture
  # mapping on every retained stub and produces deterministic cut closures.
  for f in me.polygons:
   src=old.data.polygons[f.index];lis=list(src.loop_indices);p0=originals[old.data.loops[lis[0]].vertex_index];u0=uvlayer[lis[0]].uv.copy()
   p1=originals[old.data.loops[lis[1]].vertex_index];u1=uvlayer[lis[1]].uv.copy();p2=originals[old.data.loops[lis[-1]].vertex_index];u2=uvlayer[lis[-1]].uv.copy();e1=p1-p0;e2=p2-p0
   for li in f.loop_indices:
    q=me.vertices[me.loops[li].vertex_index].co;delta=q-p0
    uv=u0+(u1-u0)*delta.dot(e1)/e1.length_squared+(u2-u0)*delta.dot(e2)/e2.length_squared
    me.uv_layers.active.data[li].uv=uv
  me.update();ob['assembly']=spec['name'];ob['guard_migration_origin']=name
  world=[(v.co.x,v.co.z,-v.co.y)for v in me.vertices];bounds=[min(v[0]for v in world),max(v[0]for v in world),min(v[1]for v in world),max(v[1]for v in world),min(v[2]for v in world),max(v[2]for v in world)]
  newrecords.append({'name':ob.name,'assembly':ob['assembly'],'world_aabb':bounds,'vertices_world':world,'role':oldrecords[name]['role'],'group':'guard'})
  audit.append({'old_object':name,'new_object':ob.name,'source_geometry':objdata(ob),'expected_slice':spec,'added_closure_planes_z':[v for v in spec['z']if v in [160,164]]})
 bpy.data.objects.remove(old,do_unlink=True)
after={o.name:h(o)for o in bpy.context.scene.objects};unchanged=sorted(set(before)-set(allow));assert all(before[n]==after[n]for n in unchanged)
assert set(before)-set(after)==set(allow);assert set(after)-set(before)=={s['name']for m in allow.values()for s in m['replacement']}
assert materials_before=={m.name:m.as_pointer()for m in bpy.data.materials}
for n in freeze['unchanged_toes']:assert before[n]==after[n]
ledger['parts']=[q for q in ledger['parts']if q['name']not in allow]+newrecords
(P/'source/geometry_parts.json').write_text(json.dumps(ledger,indent=2)+'\n')
D=json.loads(original('assets/aft_crown_platform/source/section_contract.json'));D['low_sill_revision']={'source_family':'upper_horizon_enclosure','baseline':BASE,'z':[160,164],'opaque_top_y':107.4,'changed_old_parts':sorted(allow),'toes_unchanged':freeze['unchanged_toes'],'audit':'../upper_horizon_enclosure/qa/005_preservation.json','limits':'Barrier continuous only with006 protective glass; parent must adopt005 and006 together.'};(P/'source/section_contract.json').write_text(json.dumps(D,indent=2)+'\n')
bpy.context.preferences.filepaths.save_version=0;src=P/'source/AST-CMD-005.blend';out=P/'exports/AST-CMD-005.glb';bpy.ops.wm.save_as_mainfile(filepath=str(src))
parts=[o for o in bpy.context.scene.objects if o.type=='MESH'];batches={};triangles=0
for o in parts:
 o.data.calc_loop_triangles();triangles+=len(o.data.loop_triangles);key=(o['cell_x'],o['cell_y'],o['cell_z'],o.data.materials[0].name);batches.setdefault(key,[]).append(o)
for key,obs in sorted(batches.items()):
 name='ACP_CELL_X%d_Y%d_Z%d_%s'%key;verts=[];faces=[];uvs=[]
 for ob in obs:
  offset=len(verts);verts.extend(tuple(v.co)for v in ob.data.vertices);faces.extend(tuple(i+offset for i in f.vertices)for f in ob.data.polygons);uvs.extend(tuple(v.uv)for v in ob.data.uv_layers.active.data)
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();me.materials.append(obs[0].data.materials[0]);uv=me.uv_layers.new(name='MetreScaled')
 for li,q in enumerate(uvs):uv.data[li].uv=q
 ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);ob['catalogue_id']='AST-CMD-005';ob['collision_contract']='concave_static_surface';ob['spatial_cell_metres']=8
for o in parts:bpy.data.objects.remove(o,do_unlink=True)
bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',export_yup=True,export_extras=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();M=json.loads((P/'AST-CMD-005.manifest.json').read_text());M.update(source_sha256=sha(src),export_sha256=sha(out),triangles=triangles,editable_part_count=len(parts),runtime_mesh_batches=len(batches),guard_revision='Only4Back/Cap centralZ160..164 lowered; two toes and all other objects exact; install with006')
(P/'AST-CMD-005.manifest.json').write_text(json.dumps(M,indent=2)+'\n')
report={'pass':True,'baseline':BASE,'baseline_source_sha256':hashlib.sha256(basepath.read_bytes()).hexdigest(),'source_sha256':sha(src),'export_sha256':sha(out),'exact_unaffected_objects':len(unchanged),'unaffected_object_hashes':{n:before[n]for n in unchanged},'removed_exact_allowlist':sorted(allow),'added_exact_names':sorted(set(after)-set(before)),'material_datablocks_unmodified':True,'toes_exact':True,'old_source_geometry':{n:oldrecords[n]for n in allow},'replacements':audit,'reversal':'Recover005source/export/ledger/contract/manifest from baseline Git commit; no002 change.'};(R/'qa/005_preservation.json').write_text(json.dumps(report,indent=2)+'\n');print('005_PRESERVATION_PASS',len(unchanged),triangles,len(batches))
