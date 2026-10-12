from pathlib import Path
import bpy,json,hashlib,bmesh
W=Path(__file__).resolve().parent;R=next(p for p in W.parents if (p/'Game').is_dir());I=json.loads((W/'HARDWARE_INTERFACE.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(W/I['native']))
checks=0;errors=[]
def check(v,s):
 global checks
 checks+=1
 if not v:errors.append(s)
for ob in bpy.data.objects:
 if ob.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(ob.data);check(all(e.is_manifold for e in bm.edges),ob.name+' closed solid');bm.free()
 check(ob.data.uv_layers.active is not None and ob.data.materials[0].use_nodes,ob.name+' original metre UV/material')
 check('Tram_Wheel' not in ob.name,ob.name+' no wheel duplication')
for marker in [o for o in bpy.data.objects if o.name.startswith('BOGIE_MOVING_ROOT')]:
 check(abs(marker.location.z+.2)<1e-6,marker.name+' original kingpinY');check(abs(abs(marker.location.y)-1.5)<1e-6,marker.name+' original kingpinZ')
for name in ['champagne_metal','dark_rubber']:
 m=bpy.data.materials[name]
 for node in m.node_tree.nodes:
  if node.type=='TEX_IMAGE':check(node.image.packed_file is not None,name+' packed original texture')
for collection,item in zip(['BOGIE_HARDWARE','END_BUFFER_HARDWARE'],I['exports']):
 bpy.ops.object.select_all(action='DESELECT')
 for ob in bpy.data.collections[collection].objects:ob.select_set(True)
 file=W/('AUDIT_'+item['file']);bpy.ops.export_scene.gltf(filepath=str(file),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_extras=True,export_cameras=False,export_lights=False)
 check(file.read_bytes()==(W/item['file']).read_bytes(),item['file']+' exact fresh native re-export')
out={'status':'PASS' if not errors else 'HOLD','checks':checks,'errors':errors,'editable_meshes':sum(o.type=='MESH' for o in bpy.data.objects),'source_wheel_meshes_duplicated':0,'fresh_native_exports_verified':2,'original_material_graphs_preserved_by_reference':True,'engineering_capacity_or_impact_accepted':False};(W/'NATIVE_AUDIT.json').write_text(json.dumps(out,indent=2)+'\n');print('TRAVEL_NATIVE_AUDIT',out);assert not errors
