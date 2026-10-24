"""Editable paired transfer layout; retained sources are linked, never overwritten."""
from pathlib import Path
import bpy,json,hashlib,os,math,struct
from mathutils import Vector
R=Path(__file__).resolve().parents[3];N=Path(__file__).resolve().parent;P=R/'Game/clinical_transfer_junctions_20261024';plan=json.loads((P/'PLAN.json').read_text());walls=json.loads((P/'evidence/WALL_SUCCESSORS.json').read_text());gates=json.loads((P/'evidence/GATE_SUCCESSORS.json').read_text());B=lambda p:Vector((p[0],-p[2],p[1]));target=N/'ClinicalTransferJunctions_r001.blend';assert not target.exists()
for path,digest in plan['source_pins'].items():assert hashlib.sha256((R/path).read_bytes()).hexdigest()==digest,path
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0;materials={};groups={}
for file in ['AST-MED-G3-007.blend','AST-MED-G3-008.blend','AST-MED-G3-009.blend']:
 with bpy.data.libraries.load(str(R/plan['native_library']/file),link=True)as(a,b):b.materials=list(a.materials)
 for material in b.materials:
  materials.setdefault(material.name,material);materials.setdefault(material.name.removeprefix('ASTRAEA_'),material)
# The historical D01 native package path is absent locally. Preserve its
# exact retained GLB material definitions and embedded PNG bytes in this new
# editable successor; do not claim recovery of its original .blend.
raw=(R/'Game/assets/models/SOL_D05_directory_01_remaining_batch.glb').read_bytes();length=struct.unpack_from('<I',raw,12)[0];gltf=json.loads(raw[20:20+length]);binary=raw[28+length:];image_pins={};temp=Path('/tmp/astraea-transfer-native-materials');temp.mkdir(exist_ok=True)
for definition in gltf['materials']:
 name=definition['name']
 if name not in ['A_blue','A_ivory']:continue
 pbr=definition['pbrMetallicRoughness'];image=gltf['images'][gltf['textures'][pbr['baseColorTexture']['index']]['source']];view=gltf['bufferViews'][image['bufferView']];data=binary[view.get('byteOffset',0):view.get('byteOffset',0)+view['byteLength']];assert data.startswith(b'\x89PNG\r\n\x1a\n');path=temp/(name+'.png');path.write_bytes(data);image_pins[name]=hashlib.sha256(data).hexdigest()
 material=bpy.data.materials.new(name);material.use_nodes=True;bs=material.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=pbr['roughnessFactor'];bs.inputs['Metallic'].default_value=pbr['metallicFactor'];texture=material.node_tree.nodes.new('ShaderNodeTexImage');texture.image=bpy.data.images.load(str(path),check_existing=False);texture.image.pack();sampler=gltf['samplers'][gltf['textures'][pbr['baseColorTexture']['index']].get('sampler',0)];texture.interpolation='Closest'if sampler.get('magFilter',9729)==9728 else'Linear';material.node_tree.links.new(texture.outputs['Color'],bs.inputs['Base Color']);material['retained_glb_material']=name;material['embedded_png_sha256']=image_pins[name];materials[name]=material
for zone in plan['zones']:
 c=bpy.data.collections.new(zone['id']);bpy.context.scene.collection.children.link(c);groups[zone['id']]=c
for row in plan['parts']:
 mesh=bpy.data.meshes.new(row['name']);mesh.from_pydata([B(p)for p in row['verts']],[],row['faces']);mesh.update();mesh.materials.append(materials[row['role']]);uv=mesh.uv_layers.new(name='MetreScaled')
 for poly in mesh.polygons:
  for li in poly.loop_indices:
   q=mesh.vertices[mesh.loops[li].vertex_index].co;uv.data[li].uv=(q.x*.5,-q.y*.5)if abs(poly.normal.z)>.7 else(-q.y*.5,q.z*.5)
 obj=bpy.data.objects.new(row['name'],mesh);groups[row['zone']].objects.link(obj)
skins=bpy.data.collections.new('Exact retained owner skin successors');bpy.context.scene.collection.children.link(skins)
def surface_object(name,surface,group,origin=None):
 positions=surface['positions'];positions=[[p[i]-origin[i]for i in range(3)]for p in positions]if origin else positions
 ids=surface['indices']or list(range(len(positions)));faces=[(ids[i],ids[i+2],ids[i+1])for i in range(0,len(ids),3)];mesh=bpy.data.meshes.new(name);mesh.from_pydata([B(p)for p in positions],[],faces);mesh.update();mesh.materials.append(materials[surface['material']]);uv=mesh.uv_layers.new(name='RetainedSourceUV')
 for poly in mesh.polygons:
  for li in poly.loop_indices:uv.data[li].uv=surface['uvs'][mesh.loops[li].vertex_index]
 obj=bpy.data.objects.new(name,mesh);group.objects.link(obj);return obj
for row in walls:
 for i,surface in enumerate(row['surfaces']):surface_object(row['name']+'_TransferSkin_'+str(i),surface,skins)
prototype=bpy.data.collections.new('Shared cassette3.7x3.3')
for row in gates:
 for i,surface in enumerate(row['surfaces']):surface_object(row['name'].split('__',1)[1],surface,prototype,plan['gates'][0]['position'])
for row in plan['gates']:
 obj=bpy.data.objects.new(row['name'],None);obj.instance_type='COLLECTION';obj.instance_collection=prototype;obj.location=B(row['position']);obj.rotation_euler.z=row['yaw'];obj['original_position']=row['prior_position'];obj['operating_admission']=False;obj['retained_original_nodes_reused']=row['existing'];groups[row['zone']].objects.link(obj)
for zone in plan['zones']:
 for row in zone['lights']:
  data=bpy.data.lights.new(row['name'],'SPOT');data.energy=80;data.color=row['color'];data.spot_size=math.radians(130);obj=bpy.data.objects.new(row['name'],data);obj.location=B(row['position']);obj['Godot_energy']=row['energy'];obj['Godot_range']=row['range'];obj['Blender_watts_not_runtime_calibration']=True;groups[zone['id']].objects.link(obj)
bpy.data.texts.new('Source ownership and operating holds.json').write(json.dumps({'source_pins':plan['source_pins'],'gate_bindings':plan['gates'],'room_cuts':plan['room_cuts'],'new_capacity':0,'clinical_operation':False,'visual_accepted':False},indent=2))
for library in bpy.data.libraries:library.filepath='//'+os.path.relpath(bpy.path.abspath(library.filepath),str(N))
bpy.ops.wm.save_as_mainfile(filepath=str(target),compress=True,relative_remap=False)
# Reopen the saved native bytes and check every authored part and loaded skin.
bpy.ops.wm.open_mainfile(filepath=str(target));checks=0;maximum=0
for lib in bpy.data.libraries:assert lib.filepath.startswith('//')and Path(bpy.path.abspath(lib.filepath)).is_file();checks+=1
for row in plan['parts']:
 obj=bpy.data.objects[row['name']];assert len(obj.data.vertices)==len(row['verts']);checks+=1
 for vertex,point in zip(obj.data.vertices,row['verts']):maximum=max(maximum,(vertex.co-B(point)).length)
for row in walls:
 for i,surface in enumerate(row['surfaces']):
  obj=bpy.data.objects[row['name']+'_TransferSkin_'+str(i)];assert len(obj.data.vertices)==len(surface['positions']);checks+=1
  for vertex,point in zip(obj.data.vertices,surface['positions']):maximum=max(maximum,(vertex.co-B(point)).length)
for row in plan['gates']:
 obj=bpy.data.objects[row['name']];assert len(obj.instance_collection.objects)==21 and (obj.location-B(row['position'])).length<.0001 and abs(obj.rotation_euler.z-row['yaw'])<.0001;checks+=1
for name,digest in image_pins.items():
 image=bpy.data.images[name+'.png'];assert image.packed_file and hashlib.sha256(image.packed_file.data).hexdigest()==digest;checks+=1
assert maximum<.0001,maximum
receipt={'status':'PASS','file':str(target.relative_to(R)),'bytes':target.stat().st_size,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'checks':checks,'max_position_error_m':maximum,'parts':len(plan['parts']),'owner_skin_successors':len(walls),'gate_instances':8,'shared_gate_meshes':21,'source_libraries':len(bpy.data.libraries),'retained_glb_embedded_materials':image_pins,'original_D01_native_not_claimed_recovered':True,'clinical_operation':False,'visual_accepted':False}
(P/'evidence/NATIVE.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
