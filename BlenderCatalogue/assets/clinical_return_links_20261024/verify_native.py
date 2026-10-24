"""Correct binding metadata in a named successor, then verify editable geometry."""
from pathlib import Path
import bpy,json,hashlib,os
from mathutils import Vector
R=Path(__file__).resolve().parents[3];N=Path(__file__).resolve().parent;P=R/'Game/clinical_return_links_20261024';plan=json.loads((P/'PLAN.json').read_text());walls=json.loads((P/'evidence/WALL_SUCCESSORS.json').read_text());B=lambda p:Vector((p[0],-p[2],p[1]));checks=0;maximum=0
prior=N/'ClinicalRoomReceiving_r002.blend';successor=N/'ClinicalRoomReceiving_r003.blend';assert not successor.exists();bpy.ops.wm.open_mainfile(filepath=str(prior));bpy.context.preferences.filepaths.save_version=0
text=bpy.data.texts['Canonical gate bindings.json'];text.clear();text.write(json.dumps(plan['retained_gate_bindings'],indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(successor),compress=True,relative_remap=False)
for file in [successor,N/'ClinicalThroughRoutes_r001.blend']:
 bpy.ops.wm.open_mainfile(filepath=str(file))
 for lib in bpy.data.libraries:assert lib.filepath.startswith('//')and Path(bpy.path.abspath(lib.filepath)).is_file(),lib.filepath;checks+=1
 if file==successor:
  old=json.loads((R/'Game/clinical_room_receiving_20261024/PLAN.json').read_text());rows=old['parts'];oldwalls=json.loads((R/'Game/clinical_room_receiving_20261024/evidence/WALL_SUCCESSORS.json').read_text());bound={r['receiver']:r for r in plan['retained_gate_bindings']}
  for port in old['ports']:
   name=port['id']+'_ClosedSourceCassette';obj=bpy.data.objects[name]
   if name in bound:assert obj.instance_type=='NONE'and obj.instance_collection is None and obj['source_binding_only']
   else:assert obj.instance_type=='COLLECTION'and len(obj.instance_collection.objects)==21
   checks+=1
  assert json.loads(bpy.data.texts['Canonical gate bindings.json'].as_string())==plan['retained_gate_bindings'];checks+=1
  for row in oldwalls:
   for surface in row['surfaces']:
    obj=bpy.data.objects[row['room']+'_'+row['source_name']+'_ReceiverSkin'];assert len(obj.data.vertices)==len(surface['positions']);checks+=1
    for vertex,expected in zip(obj.data.vertices,surface['positions']):maximum=max(maximum,(vertex.co-B(expected)).length)
 else:
  rows=plan['parts']
  for row in walls:
   for surface in row['surfaces']:
    obj=bpy.data.objects[row['name']+'_ThroughRouteSkin'];assert len(obj.data.vertices)==len(surface['positions']);checks+=1
    for vertex,expected in zip(obj.data.vertices,surface['positions']):maximum=max(maximum,(vertex.co-B(expected)).length)
  for route in plan['routes']:
   for lamp in route['lights']:
    obj=bpy.data.objects[lamp['name']];assert obj.type=='LIGHT'and obj['Godot_energy']==lamp['energy']and obj['Godot_range']==lamp['range'];checks+=1
 for row in rows:
  obj=bpy.data.objects[row['name']];assert len(obj.data.vertices)==len(row['verts'])and len(obj.data.polygons)==len(row['faces']);assert obj.data.materials[0].name=='ASTRAEA_'+row['role'];checks+=2
  for vertex,expected in zip(obj.data.vertices,row['verts']):maximum=max(maximum,(vertex.co-B(expected)).length)
assert maximum<.0002
receipt={'status':'PASS','checks':checks,'maximum_native_position_error_m':maximum,'scope':'Both selected native files reopen, resolve relative source libraries, and match their runtime geometry; binding metadata corrected without geometry changes.','active_files':[{'path':str(file.relative_to(R)),'bytes':file.stat().st_size,'sha256':hashlib.sha256(file.read_bytes()).hexdigest()}for file in [successor,N/'ClinicalThroughRoutes_r001.blend']],'prior_r002_retained_sha256':hashlib.sha256(prior.read_bytes()).hexdigest(),'visual_accepted':False}
(P/'evidence/NATIVE_REOPEN_CHECK.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
