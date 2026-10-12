from pathlib import Path
import bpy,bmesh,json,hashlib,copy
W=Path(__file__).resolve().parent;R=next(p for p in W.parents if (p/'Game').is_dir());I=json.loads((W/'SOURCE_INTERFACE.json').read_text())
code=(W.parent/'boarding_safety_009/audit_materials.py').read_text();exec(code[code.index('def material('):code.index('old=R/')],globals())
bpy.ops.wm.open_mainfile(filepath=str(R/I['material_donor_native']));originals={m.name:material(m) for m in bpy.data.materials};allowed=copy.deepcopy(originals['ivory_enamel'])
for n in allowed['nodes']:
 if n['type']=='ShaderNodeBsdfPrincipled':n['inputs']['Emission Color']=[1.0,.8600000143051147,.6700000166893005,1.0];n['inputs']['Emission Strength']=.6000000238418579
bpy.ops.wm.open_mainfile(filepath=str(W/I['native']));checks=0;errors=[];exports=[]
def check(v,s):
 global checks
 checks+=1
 if not v:errors.append(s)
for spec,collection in zip(I['exports'],['CAR_CONSOLE_AND_WORK_LAMP','STATION_GATE_CALL_CONTROL']):
 c=bpy.data.collections[collection];count=0
 for o in c.objects:
  if o.type!='MESH':continue
  count+=1;bm=bmesh.new();bm.from_mesh(o.data);check(all(e.is_manifold for e in bm.edges),o.name+' closed manifold');bm.free();check(o.data.uv_layers.active is not None,o.name+' metre UV')
  for m in o.data.materials:check(material(m)==(allowed if m.name=='G4_Operating_Opal_r001' else originals[m.name]),o.name+' exact retained graph/packed texture or explicit copied emission derivative')
 check(count==spec['mesh_count'],collection+' exact mesh count');bpy.ops.object.select_all(action='DESELECT')
 for o in c.objects:o.select_set(True)
 p=W/('AUDIT_'+spec['file']);bpy.ops.export_scene.gltf(filepath=str(p),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_extras=True,export_cameras=False,export_lights=False);same=p.read_bytes()==(W/spec['file']).read_bytes();check(same,spec['file']+' fresh native byte-identical export');exports.append({'file':spec['file'],'fresh_native_export_byte_identical':same})
check(hashlib.sha256((R/I['material_donor_native']).read_bytes()).hexdigest()==I['material_donor_sha256'],'original donor unchanged')
result={'status':'PASS' if not errors else 'HOLD','checks':checks,'errors':errors,'mesh_count':25,'exports':exports,'original_source_material_graphs_and_packed_pixels_preserved':True,'explicit_local_opal_copy_changes':['material name','Principled emission color','Principled emission strength'],'originals_modified':False,'final_art_or_engineering_accepted':False};(W/'NATIVE_AUDIT.json').write_text(json.dumps(result,indent=2)+'\n');print('G4_OPERATING_NATIVE',result);assert not errors
