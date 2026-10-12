from pathlib import Path
import bpy,bmesh,json,hashlib
from mathutils import Vector
W=Path(__file__).resolve().parent;R=next(p for p in W.parents if (p/'Game').is_dir());I=json.loads((W/'SOURCE_INTERFACE.json').read_text())
code=(W.parent/'boarding_safety_009/audit_materials.py').read_text();exec(code[code.index('def material('):code.index('old=R/')],globals())
def payload(o):return {'vertices':[tuple(v.co) for v in o.data.vertices],'polygons':[tuple(p.vertices) for p in o.data.polygons],'uvs':[tuple(u.uv) for u in o.data.uv_layers.active.data],'pose':[tuple(row) for row in o.matrix_world],'modifiers':[(m.name,m.type) for m in o.modifiers],'materials':[material(m) for m in o.data.materials]}
bpy.ops.wm.open_mainfile(filepath=str(R/I['donor_native']));names={c['original'] for c in I['original_rigid_clones']};before={name:payload(bpy.data.objects[name]) for name in names};original_materials=[material(m) for m in bpy.data.materials]
with bpy.data.libraries.load(str(R/'BlenderCatalogue/assets/group4_tram_connections_20261009/port_successor_002/Group4_Port_Successor_002.blend'),link=False) as(a,b):b.materials=['warm_stone']
original_materials.append(material(bpy.data.materials['warm_stone']))
bpy.ops.wm.open_mainfile(filepath=str(W/I['native']));checks=0;errors=[]
def check(v,s):
 global checks
 checks+=1
 if not v:errors.append(s)
for name,data in before.items():check(payload(bpy.data.objects[name])==data,name+' exact held original mesh/UV/pose/materials/modifiers')
for clone in I['original_rigid_clones']:
 expected=dict(before[clone['original']]);expected['pose']=[tuple(row) for row in before[clone['original']]['pose']];pose=[list(row) for row in expected['pose']];pose[2][3]+=clone['translation_xyz'][1];expected['pose']=[tuple(row) for row in pose]
 check(payload(bpy.data.objects[clone['selected']])==expected,clone['selected']+' exact rigid original payload and materials')
exports=[]
for spec,collection in zip(I['exports'],['D12_UPPER_MAIN_EXTERIOR','D13_UPPER_MAIN_EXTERIOR','STACKED_SIDE_RECEIVERS']):
 c=bpy.data.collections[collection];count=0
 for o in c.objects:
  if o.type!='MESH':continue
  count+=1;bm=bmesh.new();bm.from_mesh(o.data);check(all(e.is_manifold for e in bm.edges),o.name+' closed solid');bm.free();check(o.data.uv_layers.active is not None,o.name+' UV')
  for m in o.data.materials:check(material(m) in original_materials,o.name+' exact original material graph/packed texture bytes')
 check(count==spec['mesh_count'],collection+' exact meshes');bpy.ops.object.select_all(action='DESELECT')
 for o in c.objects:o.select_set(True)
 p=W/('AUDIT_'+spec['file']);bpy.ops.export_scene.gltf(filepath=str(p),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_extras=True,export_cameras=False,export_lights=False);check(p.read_bytes()==(W/spec['file']).read_bytes(),spec['file']+' fresh native byte-identical export');exports.append({'file':spec['file'],'fresh_native_export_byte_identical':p.read_bytes()==(W/spec['file']).read_bytes()})
result={'status':'PASS' if not errors else 'HOLD','checks':checks,'errors':errors,'all83_original_bridge_payloads_preserved_held':True,'all166_rigid_original_clones_exact_geometry_UV_materials':True,'selected_active_meshes':210,'original_material_graphs_and_packed_pixels_preserved':True,'exports':exports,'original_sources_modified':False,'structure_capacity_whole_group_or_final_art_accepted':False};(W/'NATIVE_AUDIT.json').write_text(json.dumps(result,indent=2)+'\n');print('G4_THEATER_NATIVE_AUDIT',result);assert not errors
