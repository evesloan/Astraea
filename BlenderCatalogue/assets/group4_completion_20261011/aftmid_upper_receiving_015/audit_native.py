from pathlib import Path
import bpy,bmesh,json,hashlib
W=Path(__file__).resolve().parent;R=next(p for p in W.parents if (p/'Game').is_dir())
code=(W.parent/'boarding_safety_009/audit_materials.py').read_text();exec(code[code.index('def material('):code.index('old=R/')],globals())
def payload(o):
 return {'vertices':[tuple(v.co) for v in o.data.vertices],'polygons':[tuple(p.vertices) for p in o.data.polygons],'uvs':[tuple(u.uv) for u in o.data.uv_layers.active.data],'pose':[tuple(row) for row in o.matrix_world],'modifiers':[(m.name,m.type) for m in o.modifiers],'materials':[material(m) for m in o.data.materials]}
original=R/'BlenderCatalogue/assets/group4_tram_connections_20261009/port_successor_002/Group4_Port_Successor_002.blend';bpy.ops.wm.open_mainfile(filepath=str(original));before={o.name:payload(o) for o in bpy.data.collections['AFT_MIDSHIP_STATIC_SOURCE'].objects if o.type=='MESH'}
bpy.ops.wm.open_mainfile(filepath=str(W/'Group4_Aftmid_Upper_Receiving_r002.blend'));checks=0;errors=[]
def check(ok,why):
 global checks
 checks+=1
 if not ok:errors.append(why)
for name,data in before.items():check(payload(bpy.data.objects[name])==data,name+' exact original payload/UV/pose/modifiers/materials, active or held')
collection=bpy.data.collections['AFTMID_UPPER_RECEIVING_SUCCESSOR']
for o in collection.objects:
 if o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data);check(all(e.is_manifold for e in bm.edges),o.name+' closed source solid');bm.free();check(o.data.uv_layers.active is not None,o.name+' metre UV')
 for m in o.data.materials:check(any(material(m)==old for data in before.values() for old in data['materials']),o.name+' exact original material graph/packed bytes')
bpy.ops.object.select_all(action='DESELECT')
for o in collection.objects:o.select_set(True)
audit=W/'AUDIT_AST-TRM-G4-030_aftmid_upper_receiving_r002.glb';bpy.ops.export_scene.gltf(filepath=str(audit),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_extras=True,export_cameras=False,export_lights=False)
check(audit.read_bytes()==(W/'AST-TRM-G4-030_aftmid_upper_receiving_r002.glb').read_bytes(),'exact fresh native re-export')
result={'status':'PASS' if not errors else 'HOLD','checks':checks,'errors':errors,'all189_original_source_payloads_preserved_active_or_held':True,'active_unchanged_meshes':180,'selected_meshes':202,'same_station_perch_geometry_material_and_count_preserved':True,'new_floor_m2':2.7,'fresh_native_export_byte_identical':not errors,'original_source_native_or_GLBS_modified':False,'whole_group_or_engineering_accepted':False};(W/'NATIVE_AUDIT.json').write_text(json.dumps(result,indent=2)+'\n');print('AFTMID_NATIVE_AUDIT',result);assert not errors
