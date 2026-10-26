import bpy,json,pathlib,hashlib,ast,collections
R=pathlib.Path(__file__).resolve().parents[2];D=R/'Game/grand_arrivals_tram_20261026/r007'
tree=ast.parse((R/'recovery/grand_arrivals_embarkation_20261026/verify_core_enclosure_r003.py').read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'protected_snapshot','exec'))
results=[]
for version,receipt,file in [('r006','BUILD.json','LowerDeparture.glb'),('r007','BUILD.json','LowerDeparture.glb'),('r006','HALL_BUILD.json','ArrivalsHallExit.glb'),('r007','ENCLOSURE_BUILD.json','ForwardGroundEnclosure.glb')]:
 D=R/'Game/grand_arrivals_tram_20261026'/version
 b=json.loads((D/receipt).read_text())
 for p,row in b['outputs'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==row['sha256']
 bpy.ops.wm.open_mainfile(filepath=str(next(R/p for p in b['outputs'] if p.endswith('.blend'))));native=snapshot()
 clear();bpy.ops.import_scene.gltf(filepath=str(D/file));runtime=snapshot();assert native==runtime,(file,'native/runtime difference')
 row={'file':version+'/'+file,'objects':len(native),'triangle_uv_material_equality_0_1mm':True}
 if receipt in ['ENCLOSURE_BUILD.json','HALL_BUILD.json']:
  clear();bpy.ops.import_scene.gltf(filepath=str(R/b['source']));original=snapshot()
  unchanged=set(original)-set(b['changed_objects']);assert all(original[n]==runtime[n] for n in unchanged)
  assert set(runtime)==set(original)|set(b.get('added_objects',[]));row['untouched_original_mesh_objects']=len(unchanged)
 results.append(row)
out={'passed':True,'selected':False,'results':results,'scope':'Independent native/runtime geometry/material/UV and untouched original mesh preservation, not visual/installed acceptance'}
(D/'NATIVE_RUNTIME_CHECK.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
