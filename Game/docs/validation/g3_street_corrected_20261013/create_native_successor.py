import bpy,json,hashlib
from pathlib import Path
P=Path(__file__).parent
plan=json.loads((P/'FLOOR_RECEIVING_SUCCESSOR_PLAN.json').read_text())
source=P/'source/AST-STF-G3-058_ORIGINAL.blend'
assert hashlib.sha256(source.read_bytes()).hexdigest()=='7cf5177c0b4a5ea7f3be8f394f0abe8398c8fc6e1a83a199fa2cf3167d1a7cd6'
def signature(o):
 m=o.data
 d={'matrix':[list(r) for r in o.matrix_world],'vertices':[list(v.co)for v in m.vertices],'faces':[list(f.vertices)for f in m.polygons],'material_indices':[f.material_index for f in m.polygons],'materials':[x.name for x in m.materials],'uv':{x.name:[list(q.uv)for q in x.data]for x in m.uv_layers},'custom_properties':dict(o.items())}
 return hashlib.sha256(json.dumps(d,sort_keys=True).encode()).hexdigest()
old={o.name:signature(o)for o in bpy.data.objects if o.type=='MESH'}
assert len(old)==21
for name in plan['changed_parts']:
 part=next(x for x in plan['parts']if x['name']==name)
 assert not part['top_polygons'] and part['corrected_area_m2']==0
 bpy.data.objects.remove(bpy.data.objects[name],do_unlink=True)
new={o.name:signature(o)for o in bpy.data.objects if o.type=='MESH'}
assert len(new)==18 and all(old[n]==s for n,s in new.items())
D=P/'proposed';D.mkdir(exist_ok=True)
blend=D/'AST-STF-G3-058_current_receiving_successor001.blend'
glb=D/'AST-STF-G3-058_current_receiving_successor001.glb'
bpy.ops.wm.save_as_mainfile(filepath=str(blend))
bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',export_yup=True,export_apply=False)
r={'status':'PASS_NATIVE_MISSING_ONLY_SUCCESSOR','original_native_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'original_objects':21,'removed_fully_duplicated_parts':plan['changed_parts'],'unchanged_objects':18,'unchanged_geometry_uv_material_pose_signatures':new,'removed_overlap_m2':plan['removed_overlap_m2'],'corrected_geometric_area_m2':plan['corrected_geometric_area_m2'],'protected_current_source_pins':plan['protected_current_source_pins'],'files':{str(p.relative_to(P)):{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}for p in [blend,glb]},'original_criteria_preserved':13,'operational_admission':False}
(P/'NATIVE_SUCCESSOR_RECEIPT.json').write_text(json.dumps(r,indent=2)+'\n')
print('PASS_NATIVE_SUCCESSOR unchanged=18 removed=3')
