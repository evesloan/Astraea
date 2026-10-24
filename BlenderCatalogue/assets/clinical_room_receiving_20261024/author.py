"""Editable receiving parts with linked original clinical cassettes/materials."""
from pathlib import Path
import bpy,json,hashlib,math,os
from mathutils import Vector
R=Path(__file__).resolve().parents[3];N=Path(__file__).resolve().parent;P=R/'Game/clinical_room_receiving_20261024'
plan=json.loads((P/'PLAN.json').read_text());walls=json.loads((P/'evidence/WALL_SUCCESSORS.json').read_text());out=N/'ClinicalRoomReceiving_r001.blend';assert not out.exists()
for path,digest in plan['source_pins'].items():assert hashlib.sha256((R/path).read_bytes()).hexdigest()==digest,path
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
B=lambda p:Vector((p[0],-p[2],p[1]));materials={};groups={};made=[]
for file in ['AST-MED-G3-007.blend','AST-MED-G3-008.blend','AST-MED-G3-009.blend']:
 with bpy.data.libraries.load(str(R/plan['native_library']/file),link=True)as(a,b):
  b.materials=[n for n in a.materials if n.startswith('ASTRAEA_staff_')]
 for m in b.materials:materials.setdefault(m.name.removeprefix('ASTRAEA_'),m)
for row in plan['rooms']:
 col=bpy.data.collections.new(row['key']+' — '+row['name']+' receiving');bpy.context.scene.collection.children.link(col);groups[row['key']]=col
for row in plan['parts']:
 mesh=bpy.data.meshes.new(row['name']);mesh.from_pydata([B(p)for p in row['verts']],[],row['faces']);mesh.update();mesh.materials.append(materials[row['role']]);uv=mesh.uv_layers.new(name='AuthoredMetreUV')
 for polygon in mesh.polygons:
  normal=polygon.normal;horizontal=abs(normal.z)>.7
  for li in polygon.loop_indices:
   point=mesh.vertices[mesh.loops[li].vertex_index].co;uv.data[li].uv=(point.x*.5,-point.y*.5)if horizontal else(-point.y*.5,point.z*.5)
 obj=bpy.data.objects.new(row['name'],mesh);groups[row['room']].objects.link(obj);made.append(obj)
source_collection=bpy.data.collections.new('Immutable source clinical cassette')
with bpy.data.libraries.load(str(R/plan['native_library']/'AST-MED-G3-009.blend'),link=True)as(a,b):b.objects=a.objects
for obj in b.objects:
 if obj.type=='MESH':source_collection.objects.link(obj)
for port in plan['ports']:
 obj=bpy.data.objects.new(port['id']+'_ClosedSourceCassette',None);obj.instance_type='COLLECTION';obj.instance_collection=source_collection;obj.location=B(port['gate_position']);obj.rotation_euler.z=port['gate_yaw'];obj['operation_admitted']=False;groups[port['room']].objects.link(obj);made.append(obj)
 for lamp in port['lights']:
  data=bpy.data.lights.new(lamp['name'],'SPOT');data.color=lamp['color'];data.energy=80;data.spot_size=math.radians(130);obj=bpy.data.objects.new(lamp['name'],data);obj.location=B(lamp['position']);obj['Godot_energy']=lamp['energy'];obj['Godot_range']=lamp['range'];obj['Blender_watts_not_runtime_calibration']=True;groups[port['room']].objects.link(obj);made.append(obj)
# Exact runtime-generated source-skin successors: preserve each donor material
# and its embedded images. Original room native files are never overwritten.
for row in walls:
 definition=next(q for q in plan['rooms']if q['key']==row['room']);before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(R/'Game'/definition['model']));imported=set(bpy.data.objects)-before
 donor=next(o for o in imported if o.type=='MESH'and o.name.startswith(row['source_name']));mats=list(donor.data.materials)
 for si,surface in enumerate(row['surfaces']):
  points=surface['positions'];indices=surface['indices']or list(range(len(points)));faces=[(indices[i],indices[i+2],indices[i+1])for i in range(0,len(indices),3)];name=row['room']+'_'+row['source_name']+'_ReceiverSkin';mesh=bpy.data.meshes.new(name);mesh.from_pydata([B(p)for p in points],[],faces);mesh.update();mesh.materials.append(mats[si]);uv=mesh.uv_layers.new(name='RetainedSourceUV')
  for polygon in mesh.polygons:
   for li in polygon.loop_indices:uv.data[li].uv=surface['uvs'][mesh.loops[li].vertex_index]
  obj=bpy.data.objects.new(name,mesh);groups[row['room']].objects.link(obj);made.append(obj)
 for obj in imported:bpy.data.objects.remove(obj,do_unlink=True)
for image in bpy.data.images:
 if image.library is None and image.source=='FILE'and not image.packed_file:image.pack()
bpy.data.texts.new('Receiving scope and holds.json').write(json.dumps({'source_plan':'Game/clinical_room_receiving_20261024/PLAN.json','new_rooms':0,'new_capacity':0,'clinical_operations':False,'immutable_source_pins':plan['source_pins'],'wall_successors':'Game/clinical_room_receiving_20261024/evidence/WALL_SUCCESSORS.json','original_rooms_preserved':True,'final_visual_accepted':False},indent=2))
for library in bpy.data.libraries:
 library.filepath="//"+os.path.relpath(bpy.path.abspath(library.filepath),str(N))
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True,relative_remap=False)
receipt=dict(status='SAVED_EDITABLE_UNFINISHED_NATIVE',path=str(out.relative_to(R)),bytes=out.stat().st_size,sha256=hashlib.sha256(out.read_bytes()).hexdigest(),authored_parts=len(plan['parts']),source_cassettes=len(plan['ports']),wall_successors=len(walls),source_link_paths=[lib.filepath for lib in bpy.data.libraries],visual_accepted=False)
(P/'evidence/NATIVE.json').write_text(json.dumps(receipt,indent=2)+'\n');print('NATIVE_SAVED',out.stat().st_size)
