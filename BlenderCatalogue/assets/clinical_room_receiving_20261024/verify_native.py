"""Read-only reopening check of the editable clinical receiver and linked originals."""
from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
R=Path(__file__).resolve().parents[3];N=Path(__file__).resolve().parent;P=R/'Game/clinical_room_receiving_20261024';native=N/'ClinicalRoomReceiving_r001.blend'
bpy.ops.wm.open_mainfile(filepath=str(native))
plan=json.loads((P/'PLAN.json').read_text());walls=json.loads((P/'evidence/WALL_SUCCESSORS.json').read_text());B=lambda p:Vector((p[0],-p[2],p[1]));maximum=0;checks=0
for library in bpy.data.libraries:
 assert library.filepath.startswith('//')and Path(bpy.path.abspath(library.filepath)).is_file(),library.filepath;checks+=1
for row in plan['parts']:
 obj=bpy.data.objects[row['name']];assert len(obj.data.vertices)==len(row['verts'])and len(obj.data.polygons)==len(row['faces']);assert obj.data.materials[0].name=='ASTRAEA_'+row['role'];checks+=3
 for a,b in zip(obj.data.vertices,row['verts']):maximum=max(maximum,(a.co-B(b)).length)
for port in plan['ports']:
 obj=bpy.data.objects[port['id']+'_ClosedSourceCassette'];assert obj.instance_type=='COLLECTION'and len(obj.instance_collection.objects)==21;assert (obj.location-B(port['gate_position'])).length<.0002;assert not obj['operation_admitted'];checks+=3
 for light in port['lights']:
  obj=bpy.data.objects[light['name']];assert obj.type=='LIGHT'and obj.data.type=='SPOT';assert obj['Godot_energy']==light['energy']and obj['Godot_range']==light['range'];checks+=2
for wall in walls:
 for si,surface in enumerate(wall['surfaces']):
  obj=bpy.data.objects[wall['room']+'_'+wall['source_name']+'_ReceiverSkin'];assert len(obj.data.vertices)==len(surface['positions']);checks+=1
  for a,b in zip(obj.data.vertices,surface['positions']):maximum=max(maximum,(a.co-B(b)).length)
assert maximum<.0002
for image in bpy.data.images:
 if image.library is None and image.source=='FILE':assert image.packed_file or Path(bpy.path.abspath(image.filepath)).is_file(),image.name
receipt={'status':'PASS','checks':checks,'maximum_native_position_error_m':maximum,'relative_source_libraries':len(bpy.data.libraries),'editable_architecture_parts':len(plan['parts']),'exact_closed_source_cassettes':len(plan['ports']),'wall_successors':len(walls),'native_sha256':hashlib.sha256(native.read_bytes()).hexdigest(),'saved_again':False,'visual_accepted':False}
(P/'evidence/NATIVE_REOPEN_CHECK.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
