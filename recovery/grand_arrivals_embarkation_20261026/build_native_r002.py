"""Editable exact core receiver plus unchanged surrounding slab; new output only."""
import bpy,bmesh,hashlib,json,pathlib
from mathutils import Vector
R=pathlib.Path(__file__).resolve().parents[2];D=R/'Game/grand_arrivals_tram_20261026/r002';N=R/'BlenderCatalogue/assets/grand_arrivals_tram_20261026/r002'
assert not N.exists() and not (D/'ForeMidCoreReceiving.glb').exists()
source=R/'Game/assets/models/AST-ARR-002.glb';source_sha=hashlib.sha256(source.read_bytes()).hexdigest()
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(source))
roles=['warm_stone','warm_walnut','champagne_metal','ivory_enamel','ArrivalsArchitecturalGlass']
mats={role:next(m for m in bpy.data.materials if m.name==role or m.name.startswith(role+'.')) for role in roles}
for o in list(bpy.data.objects):bpy.data.objects.remove(o,do_unlink=True)
parts=json.loads((D/'PARTS.json').read_text());proof=json.loads((D/'CORE_RECEIVING.json').read_text());f=proof['replacement_region']
vertices=[];faces=[]
for tri in f['triangles']:
 i=len(vertices);vertices.extend([[x,f['floor_y'],z] for x,z in tri]);faces.append([i,i+1,i+2])
 i=len(vertices);vertices.extend([[x,f['floor_y']-f['thickness'],z] for x,z in reversed(tri)]);faces.append([i,i+1,i+2])
for ring in f['rings']:
 for a,b in zip(ring,ring[1:]+ring[:1]):
  i=len(vertices);vertices.extend([[a[0],f['floor_y'],a[1]],[b[0],f['floor_y'],b[1]],[b[0],f['floor_y']-f['thickness'],b[1]],[a[0],f['floor_y']-f['thickness'],a[1]]]);faces.append([i,i+1,i+2,i+3])
parts.append({'name':'D03_ForeMid_ExactRetainedFloorReplacement','vertices':vertices,'faces':faces,'material':'warm_stone','purpose':'Exact source triangles outside authored rail slot, original lift/stair holes retained'})
manifest=json.loads((R/'BlenderCatalogue/materials/material_manifest.json').read_text())['materials'];made=[]
for p in parts:
 mesh=bpy.data.meshes.new(p['name']);mesh.from_pydata([(v[0],-v[2],v[1]) for v in p['vertices']],[],p['faces']);mesh.update()
 bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-8);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free()
 mesh.materials.append(mats[p['material']]);uv=mesh.uv_layers.new(name='RetainedMaterialMetres')
 scale=manifest.get(p['material'],{}).get('meters_per_tile_uv',[1,1])
 for face in mesh.polygons:
  normal=face.normal;axis=max(range(3),key=lambda j:abs(normal[j]));axes=[j for j in range(3) if j!=axis]
  for li in face.loop_indices:
   v=mesh.vertices[mesh.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]]/scale[0],v[axes[1]]/scale[1])
 obj=bpy.data.objects.new(p['name'],mesh);bpy.context.collection.objects.link(obj);obj['purpose']=p['purpose'];obj['material_role']=p['material'];obj['selected']=False;made.append(obj)
for image in bpy.data.images:
 if image.source=='FILE' and image.has_data:image.pack()
N.mkdir(parents=True)
native=N/'ForeMidCoreReceiving_r002.blend';glb=D/'ForeMidCoreReceiving.glb'
bpy.ops.wm.save_as_mainfile(filepath=str(native));bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',export_extras=True,export_yup=True)
receipt={'selected':False,'objects':len(made),'parts_input_sha256':hashlib.sha256((D/'PARTS.json').read_bytes()).hexdigest(),'floor_input_sha256':hashlib.sha256((D/'CORE_RECEIVING.json').read_bytes()).hexdigest(),'material_source':source.relative_to(R).as_posix(),'material_source_sha256':source_sha,'material_names':{k:v.name for k,v in mats.items()},'source_floor_unchanged':True,'outputs':{p.relative_to(R).as_posix():{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [native,glb]}}
(D/'BUILD.json').write_bytes((json.dumps(receipt,indent=2)+'\n').encode());print('ARRIVALS_RECEIVING_NATIVE '+json.dumps(receipt))
