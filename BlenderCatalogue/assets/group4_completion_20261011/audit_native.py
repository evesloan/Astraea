from pathlib import Path
import bpy,json,hashlib,bmesh
W=Path(__file__).resolve().parent;R=W.parents[2]
bpy.ops.wm.open_mainfile(filepath=str(W/'Group4_Completion_Receiving_r002.blend'))
checks=0;errors=[];meshes=[]
def ck(v,s):
 global checks
 checks+=1
 if not v:errors.append(s)
for ob in bpy.data.collections['COMPLETION_RECEIVERS'].objects:
 if ob.type!='MESH':continue
 meshes.append(ob);bm=bmesh.new();bm.from_mesh(ob.data)
 ck(all(e.is_manifold for e in bm.edges),ob.name+' closed manifold native');bm.free()
 ck(len(ob.data.uv_layers)==1,ob.name+' explicit original metre UV')
 ck(ob.data.materials[0].use_nodes,ob.name+' source material link')
pins=json.loads((W/'NATIVE_BUILD.json').read_text())['materials'];images=[]
for im in bpy.data.images:
 if im.source!='FILE' or not im.size[0]:continue
 ck(im.packed_file is not None,im.name+' packed image')
 h=hashlib.sha256(bytes(im.packed_file.data)).hexdigest()
 ck(h in pins.values(),im.name+' retained texture bytes');images.append({'name':im.name,'sha256':h})
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.data.collections['COMPLETION_RECEIVERS'].objects:o.select_set(True)
bpy.context.view_layer.objects.active=meshes[0]
repeat=W/'AUDIT_REEXPORT_r002.glb'
bpy.ops.export_scene.gltf(filepath=str(repeat),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_extras=True,export_cameras=False,export_lights=False,export_animations=False,export_materials='EXPORT')
ck(repeat.read_bytes()==(W/'AST-TRM-G4-023_station_receiving_r002.glb').read_bytes(),'fresh native byte-identical reexport')
report={'status':'PASS' if not errors else 'HOLD','checks':checks,'errors':errors,'editable_meshes':len(meshes),'packed_images':images,'native_sha256':hashlib.sha256((W/'Group4_Completion_Receiving_r002.blend').read_bytes()).hexdigest(),'fresh_reexport_sha256':hashlib.sha256(repeat.read_bytes()).hexdigest()}
(W/'NATIVE_AUDIT.json').write_text(json.dumps(report,indent=2)+'\n');print('NATIVE_AUDIT',report['status'],checks);assert not errors,errors
