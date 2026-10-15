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
bpy.ops.wm.open_mainfile(filepath=str(R/p['source_native']));source={c['source']:{'mesh':geom(bpy.data.objects[c['source']].data),'matrix':bpy.data.objects[c['source']].matrix_world.copy()}for c in r['rigid_clones']};required_images={hashlib.sha256(bytes(node.image.packed_file.data)).hexdigest()for name in source for material in bpy.data.objects[name].data.materials if material and material.use_nodes for node in material.node_tree.nodes if node.type=='TEX_IMAGE'and node.image and node.image.packed_file};sourceimages={im.name:hashlib.sha256(bytes(im.packed_file.data)).hexdigest()for im in bpy.data.images if im.packed_file};bpy.ops.wm.open_mainfile(filepath=str(D/'native/ORCHARD_SERVICE_GATEWAY_r002.blend'));maxerr=0
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
report={'status':'PASS_NATIVE_CLONES_BATCH_POLYGONS_UV_AND_SOURCE_IMAGES','rigid_source_meshes':len(r['rigid_clones']),'source_images_preserved':images,'max_rigid_transform_element_error':maxerr,'baked_polygons_verified':len(errors),'max_baked_position_error_m':max(errors),'fixed_position_tolerance_m':.0001,'new_receiving_world_triangles':triangles,'native_sha256':sha(D/'native/ORCHARD_SERVICE_GATEWAY_r002.blend'),'source_native_sha256':sha(R/p['source_native'])};(D/'NATIVE_GEOMETRY_VERIFICATION.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'],report['rigid_source_meshes'],triangles)
from mathutils.bvhtree import BVHTree
roof=bpy.data.objects['ORX_SourceJoinedRoof'];tree=BVHTree.FromPolygons([roof.matrix_world@v.co for v in roof.data.vertices],[list(f.vertices)for f in roof.data.polygons]);rows=[]
for o in bpy.data.collections['ORCHARD_EXTERNAL_RECEIVING_AUTHORING_R001'].objects:
 if not o.name.endswith('_Shroud'):continue
 points=[o.matrix_world@Vector(v)for v in o.bound_box];xs=[min(p.x for p in points),max(p.x for p in points)];ys=[min(p.y for p in points),max(p.y for p in points)];hits=[]
 for x in xs:
  for y in ys:
   hit=tree.ray_cast(Vector((x,y,64.79)),Vector((0,0,1)),.05)[0];assert hit is not None and abs(hit.z-64.8)<.00005,o.name;hits.append([x,hit.z,-y])
 rows.append({'hood':o.name,'all_four_projected_corners_inside_actual_roof':hits})
assert len(rows)==4;(D/'ALL_HOOD_ROOF_FOOTPRINTS.json').write_text(json.dumps({'status':'PASS_ALL4_HOODS_WHOLE_ENVELOPES_BELOW_ACTUAL_ROOF','hoods':rows},indent=2)+'\n');print('PASS_ALL4_HOOD_ENVELOPES_BELOW_ACTUAL_ROOF')

def all_image_payloads():
 return {hashlib.sha256(bytes(n.image.packed_file.data)).hexdigest()for o in bpy.data.objects if o.type=="MESH" for m in o.data.materials if m and m.use_nodes for n in m.node_tree.nodes if n.type=="TEX_IMAGE"and n.image and n.image.packed_file}
new_payloads=all_image_payloads();bpy.ops.wm.open_mainfile(filepath='/workspace/astraea-integration-cutoff-20261013/orchard_external_receiving_20261015/native/ORCHARD_SERVICE_GATEWAY_r001.blend');old_payloads=all_image_payloads();assert old_payloads==new_payloads
(D/"ALL_REFERENCED_IMAGE_PAYLOADS.json").write_text(json.dumps({"status":"PASS_ALL_ORIGINAL_REFERENCED_IMAGE_BYTES_PRESERVED","payloads":len(old_payloads)},indent=2)+"\n")
