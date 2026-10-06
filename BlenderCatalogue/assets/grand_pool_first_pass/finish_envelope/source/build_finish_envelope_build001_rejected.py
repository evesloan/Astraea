"""Parent-scheduled Blender authoring. Default saves NEW editable source only.
No original family, shared material, runtime file or existing source is overwritten.
Export is a separate explicit --export step after source QA and parent retention.
"""
import bpy,bmesh,json,hashlib,sys,math
from pathlib import Path
from mathutils import Vector
HERE=Path(__file__).resolve().parents[1];CAT=Path('/workspace/shared/astraea-catalogue-continuation-20261002')
CONTRACT=HERE/'source/finish_contract.json';D=json.loads(CONTRACT.read_text());SOURCE=HERE/'source/grand_pool_finish_envelope.blend';EXPORT=HERE/'exports/AST-AQU-016_finish_envelope.glb'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert len(D['fixtures'])==14,'Fail closed until all14 real source mounts are coordinated'
assert sha(CAT/'assets/grand_pool_orchard_section/source/AST-AQU-016.blend')==D['original_inputs']['original_blend_sha256']
assert sha(CAT/'assets/grand_pool_orchard_section/source/connected_contract.json')==D['original_inputs']['connected_contract_sha256']
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
if '--export' in args:
 assert SOURCE.exists() and not EXPORT.exists(),'Never overwrite a surviving source/export'
 report=json.loads((HERE/'qa/editable_source_report.json').read_text());assert report['status']=='source_checks_pass' and not report['issues'];assert sha(SOURCE)==report['source_sha256']
 retained=json.loads((HERE/'qa/parent_source_retention.json').read_text());assert retained['source_sha256']==sha(SOURCE) and retained['independently_retained'] is True,'Parent must provide verified independent source retention before export'
 bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
 # Material/spatial batching changes only the unsaved export scene. Keep exact
 # markers and map every retained source part to its joined runtime batch.
 records={x['name']:x for x in D['parts']};groups={};batches=[]
 for ob in list(bpy.context.scene.objects):
  if ob.type!='MESH':continue
  row=records[ob.name];center=[(a+b)*.5 for a,b in zip(row['bounds_min_xyz'],row['bounds_max_xyz'])]
  key=(math.floor(center[0]/16),math.floor(center[1]/8),math.floor(center[2]/16),row['material_role'],row['collision_contract'],row.get('cast_shadow',True));groups.setdefault(key,[]).append(ob)
 for index,(key,objects) in enumerate(sorted(groups.items())):
  names=[o.name for o in objects];bpy.ops.object.select_all(action='DESELECT')
  for ob in objects:ob.select_set(True)
  bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();ob=bpy.context.object;ob.name='GPF_BATCH_%03d_%s'%(index,key[3]);ob['source_part_names']=json.dumps(names);ob['collision_contract']=key[4];ob['cast_shadow']=key[5]
  batches.append({'name':ob.name,'source_parts':names,'material_role':key[3],'collision_contract':key[4],'cast_shadow':key[5]})
 EXPORT.parent.mkdir(exist_ok=True)
 bpy.ops.export_scene.gltf(filepath=str(EXPORT),export_format='GLB',export_yup=True,export_apply=True,export_extras=True,export_cameras=False,export_lights=False)
 (HERE/'qa/EXPORT_BATCHES.json').write_text(json.dumps({'source_sha256':sha(SOURCE),'export_sha256':sha(EXPORT),'batches':batches,'fixture_markers_preserved':14},indent=2)+'\n')
 print(json.dumps({'export':str(EXPORT),'sha256':sha(EXPORT),'batches':len(batches),'status':'source_export_created_pending_roundtrip_QA'}))
 raise SystemExit
assert not SOURCE.exists(),'Do not overwrite a surviving editable source'
bpy.ops.wm.read_factory_settings(use_empty=True);scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
# Pull each material from a known actual source part. This avoids selecting an
# unused similarly named material or rebuilding/altering the shared palette.
exemplars={'ivory_enamel':'GP_WestWallBand','warm_stone':'GP_SculptedPier_0','warm_walnut':'GP_VaultLamp_-433_-36_Recess','champagne_metal':'GP_GlazingMullion','aquatic_edge_tile':'GP_BasinWall_Port','lens':'GP_VaultLamp_-433_-36_Lens'}
with bpy.data.libraries.load(str(CAT/'assets/grand_pool_orchard_section/source/AST-AQU-016.blend'),link=False) as(src,dst):
 assert set(exemplars.values())<=set(src.objects);dst.objects=list(exemplars.values())
loaded={o.name:o for o in dst.objects};mats={role:loaded[name].data.materials[0] for role,name in exemplars.items()}
for ob in list(loaded.values()):
 data=ob.data;bpy.data.objects.remove(ob)
 if data.users==0:bpy.data.meshes.remove(data)
material_evidence={}
for role,mat in mats.items():
 imgs=[]
 for node in mat.node_tree.nodes:
  if node.type=='TEX_IMAGE' and node.image:
   im=node.image;assert min(im.size)>0;imgs.append({'name':im.name,'size':list(im.size),'packed':bool(im.packed_file or im.packed_files),'filepath':im.filepath})
 material_evidence[role]={'source_exemplar':exemplars[role],'material':mat.name,'metric_tile_m':list(mat.get('meters_per_tile_uv',[1,1])),'images':imgs}
for row in D['parts']:
 vertices=[(v[0],-v[2],v[1]) for v in row['world_vertices']]
 data=bpy.data.meshes.new(row['name']+'_editable_mesh');data.from_pydata(vertices,[],row['faces']);data.update();bm=bmesh.new();bm.from_mesh(data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-7);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(data);bm.free()
 ob=bpy.data.objects.new(row['name'],data);scene.collection.objects.link(ob);data.materials.append(mats[row['material_role']]);ob['parent_design_id']='AST-AQU-016';ob['retained_host']=row['support'];ob['collision_contract']=row['collision_contract'];ob['material_role']=row['material_role'];ob['source_contract_sha256']=sha(CONTRACT)
 if row.get('cast_shadow') is False:ob['cast_shadow']=False
 uv=data.uv_layers.new(name='MetreScaled');scale=mats[row['material_role']].get('meters_per_tile_uv',[1,1])
 for poly in data.polygons:
  n=poly.normal.normalized();u=(Vector((1,0,0))-n*n.x).normalized() if abs(n.z)>.7 else Vector((-n.y,n.x,0)).normalized();v=n.cross(u).normalized()
  for li in poly.loop_indices:
   p=data.vertices[data.loops[li].vertex_index].co;uv.data[li].uv=(p.dot(u)/scale[0],p.dot(v)/scale[1])
for row in D['fixtures']:
 ob=bpy.data.objects.new(row['name'],None);scene.collection.objects.link(ob);x,y,z=row['position_xyz'];ob.location=(x,-z,y);ob['direction_godot_xyz']=row['direction_xyz'];ob['receiver_godot_xyz']=row['receiver_xyz'];ob['physical_housing']=row['physical_housing'];ob['physical_lens']=row['physical_lens'];ob['retained_host']=row['host'];ob['suggested_range_m']=row['suggested_range_m'];ob['suggested_energy']=row['suggested_energy'];ob['suggested_spot_angle_degrees']=row['suggested_spot_angle_degrees']
bpy.context.view_layer.update();assert len(scene.objects)==len(D['parts'])+14;assert all(o.type in {'MESH','EMPTY'} for o in scene.objects)
scene['scope']='Additive source-only Grand Pool finish; no accepted source/runtime/visual stage implied';scene['source_contract_sha256']=sha(CONTRACT);bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
(HERE/'qa/build_receipt.json').write_text(json.dumps({'status':'new_editable_source_saved_pending_QA','source_sha256':sha(SOURCE),'contract_sha256':sha(CONTRACT),'mesh_parts':len(D['parts']),'fixture_markers':14,'material_source_evidence':material_evidence,'export_created':False},indent=2)+'\n');print('Saved NEW editable finish source only:',SOURCE)
