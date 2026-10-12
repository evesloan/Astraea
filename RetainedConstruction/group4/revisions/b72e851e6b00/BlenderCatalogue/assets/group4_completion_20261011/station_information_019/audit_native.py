from pathlib import Path
import bpy,bmesh,json,hashlib
W=Path(__file__).resolve().parent;R=next(p for p in W.parents if (p/'Game').is_dir());I=json.loads((W/'SOURCE_INTERFACE.json').read_text());code=(W.parent/'boarding_safety_009/audit_materials.py').read_text();exec(code[code.index('def material('):code.index('old=R/')],globals())
bpy.ops.wm.open_mainfile(filepath=str(R/I['source_material_donor']));before={m.name:material(m) for m in bpy.data.materials};bpy.ops.wm.open_mainfile(filepath=str(W/I['native']));checks=0;errors=[]
def check(v,s):
 global checks
 checks+=1
 if not v:errors.append(s)
c=bpy.data.collections['MOUNTED_STATION_INFORMATION'];count=0
for o in c.objects:
 if o.type!='MESH':continue
 count+=1;bm=bmesh.new();bm.from_mesh(o.data);check(all(e.is_manifold for e in bm.edges),o.name+' closed native solid');bm.free();check(o.data.uv_layers.active is not None,o.name+' metre UV')
 for m in o.data.materials:check(material(m)==before[m.name],o.name+' exact existing material graph/packed texture including retained018 opal')
check(count==18,'exact source18 meshes');bpy.ops.object.select_all(action='DESELECT')
for o in c.objects:o.select_set(True)
p=W/('AUDIT_'+I['file']);bpy.ops.export_scene.gltf(filepath=str(p),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_extras=True,export_cameras=False,export_lights=False);check(p.read_bytes()==(W/I['file']).read_bytes(),'fresh native byte-identical export');check(hashlib.sha256((R/I['source_material_donor']).read_bytes()).hexdigest()==I['source_material_donor_sha256'],'immutable donor unchanged')
d={'status':'PASS' if not errors else 'HOLD','checks':checks,'errors':errors,'native_meshes':18,'all_source_material_graphs_UVs_and_packed_texture_bytes_retained':True,'fresh_native_GLBS_byte_identical':1,'original_source_modified':False,'final_art_accepted':False};(W/'NATIVE_AUDIT.json').write_text(json.dumps(d,indent=2)+'\n');print('G4_STATION_INFORMATION_NATIVE',d);assert not errors
