from pathlib import Path
import bpy,json,hashlib,struct,collections
from mathutils import Matrix,Vector
D=Path(__file__).resolve().parent;R=Path('/workspace/astraea-protected-integration-20261012');p=json.loads((D/'NATIVE_PLAN.json').read_text());r=json.loads((D/'NATIVE_VERIFICATION.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def geom(data):
 h=hashlib.sha256()
 for v in data.vertices:h.update(struct.pack('<3f',*v.co))
 for f in data.polygons:h.update(struct.pack('<I',len(f.vertices)));h.update(struct.pack('<'+'I'*len(f.vertices),*f.vertices))
 for layer in data.uv_layers:
  h.update(layer.name.encode())
  for v in layer.data:h.update(struct.pack('<2f',*v.uv))
 return h.hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(R/p['source_native']));source={c['source']:{'mesh':geom(bpy.data.objects[c['source']].data),'matrix':bpy.data.objects[c['source']].matrix_world.copy()}for c in r['rigid_clones']};required_images={hashlib.sha256(bytes(node.image.packed_file.data)).hexdigest()for name in source for material in bpy.data.objects[name].data.materials if material and material.use_nodes for node in material.node_tree.nodes if node.type=='TEX_IMAGE'and node.image and node.image.packed_file};sourceimages={im.name:hashlib.sha256(bytes(im.packed_file.data)).hexdigest()for im in bpy.data.images if im.packed_file};bpy.ops.wm.open_mainfile(filepath=str(D/'native/ORCHARD_SERVICE_GATEWAY_r001.blend'));maxerr=0
for row in r['rigid_clones']:
 o=bpy.data.objects[row['name']];s=source[row['source']];assert geom(o.data)==s['mesh'];expected=Matrix(row['rigid_matrix_blender'])@s['matrix'];err=max(abs(expected[i][j]-o.matrix_world[i][j])for i in range(4)for j in range(4));assert err<.0001;maxerr=max(maxerr,err)
images=0
for im in bpy.data.images:
 if im.packed_file and im.name in sourceimages:assert hashlib.sha256(bytes(im.packed_file.data)).hexdigest()==sourceimages[im.name];images+=1
native_payloads={hashlib.sha256(bytes(im.packed_file.data)).hexdigest()for im in bpy.data.images if im.packed_file};assert required_images and required_images<=native_payloads;images=len(required_images)
# Exact polygon construction and UV correspondence, allowing only float storage error in baked world positions.
errors=[];triangles=0
for row in r['batches']:
 b=bpy.data.objects[row['name']];b.data.calc_loop_triangles();triangles+=len(b.data.loop_triangles);expected=[]
 # Locate every authored face by coarse geometric key, then compare exact positions/UVs within fixed tolerance.
 key=lambda ps:tuple(sorted(tuple(round(float(x),2)for x in p)for p in ps))
 sourcefaces=collections.defaultdict(list)
 for name in row['members']:
  o=bpy.data.objects[name]
  for f in o.data.polygons:
   material=o.data.materials[f.material_index]
   if material.name!=row['material']:continue
   vs=[o.matrix_world@o.data.vertices[o.data.loops[li].vertex_index].co for li in f.loop_indices];uvs=[o.data.uv_layers.active.data[li].uv.copy()for li in f.loop_indices];sourcefaces[key(vs)].append((vs,uvs))
 for f in b.data.polygons:
  vs=[b.data.vertices[b.data.loops[li].vertex_index].co for li in f.loop_indices];uvs=[b.data.uv_layers.active.data[li].uv for li in f.loop_indices];bucket=sourcefaces[key(vs)];assert bucket
  matches=[(i,max((a-c).length for a,c in zip(old,vs)),max((a-c).length for a,c in zip(old_uv,uvs)))for i,(old,old_uv)in enumerate(bucket)if len(old)==len(vs)]
  match=next((m for m in matches if m[1]<.0001 and m[2]<.000001),None);assert match is not None,(row['name'],f.index,matches)
  bucket.pop(match[0]);errors.append(match[1])
 assert not any(sourcefaces.values())
report={'status':'PASS_NATIVE_CLONES_BATCH_POLYGONS_UV_AND_SOURCE_IMAGES','rigid_source_meshes':len(r['rigid_clones']),'source_images_preserved':images,'max_rigid_transform_element_error':maxerr,'baked_polygons_verified':len(errors),'max_baked_position_error_m':max(errors),'fixed_position_tolerance_m':.0001,'new_receiving_world_triangles':triangles,'native_sha256':sha(D/'native/ORCHARD_SERVICE_GATEWAY_r001.blend'),'source_native_sha256':sha(R/p['source_native'])};(D/'NATIVE_GEOMETRY_VERIFICATION.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'],report['rigid_source_meshes'],triangles)
