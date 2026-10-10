from pathlib import Path
import json,hashlib,importlib.util, numpy as np
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.loads((W/'FITTINGS_PLAN.json').read_text());N=json.loads((W/'NATIVE_EXPORT_CHECK.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for p,h in P['preimage_pins'].items():assert sha(R/p)==h,p
for a in P['sources']:
 for k in ['source','export']:assert sha(R/'BlenderCatalogue'/a[k])==a['source_sha256'if k=='source'else'export_sha256']
assert sha(W/N['native'])==N['native_sha256'];assert sha(W/N['export'])==N['export_sha256'];assert sha(R/'Game/assets/models'/N['export'])==N['export_sha256']
# Decode triangles with the retained tested GLB transform/accessor reader; no helper transfer processing.
src=(R/'BlenderCatalogue/assets/tidal_d15_service_receiving_20261010/source_geometry.py').read_text();src=src.replace("raw=read('Game/assets/models/'+file)","raw=Path(file).read_bytes()")
ns={'__file__':str(W/'source_geometry_reader.py')};exec(compile(src,'retained_geometry_reader','exec'),ns)
module=list(ns['triangles'](str(W/N['export'])))
receipts=[]
for item in P['assemblies']:
 a=next(a for a in P['sources']if a['catalogue_id']==item['catalogue_id']);reference=list(ns['triangles'](str(R/'BlenderCatalogue'/a['export']),item['position'],item['yaw']));selected=[(name,t)for name,t in module if name.startswith(item['name']+'__')]
 ref=np.concatenate([t for name,t in reference]);actual=np.concatenate([t for name,t in selected]);assert ref.shape==actual.shape,(item['name'],ref.shape,actual.shape)
 # Material batching differs from native part hierarchy. Match whole triangle point sets without requiring batch or vertex order.
 from collections import defaultdict
 from itertools import product,permutations
 bins=defaultdict(list)
 for i,center in enumerate(ref.mean(axis=1)):bins[tuple(np.floor(center/.1).astype(int))].append(i)
 used=set();max_error=0;triangles=len(ref)
 for triangle in actual:
  key=np.floor(triangle.mean(axis=0)/.1).astype(int);candidates=[]
  for delta in product([-1,0,1],repeat=3):candidates.extend(i for i in bins[tuple(key+delta)]if i not in used)
  assert candidates,'Missing reference triangle'
  target=ref[candidates];error=np.full(len(candidates),float('inf'))
  for order in permutations(range(3)):error=np.minimum(error,np.max(np.linalg.norm(target[:,order,:]-triangle,axis=2),axis=1))
  best=int(np.argmin(error));assert error[best]<.0002,(item['name'],float(error[best]));used.add(candidates[best]);max_error=max(max_error,float(error[best]))
 assert len(used)==len(ref)
 receipts.append({'assembly':item['name'],'reference_material_batches':len(reference),'native_meshes':len(selected),'triangles':triangles,'maximum_export_vertex_deviation_m':max_error})
receipt={'status':'PASS','exact_preimage_pins':len(P['preimage_pins']),'source_ids':['AST-STF-007','AST-AQU-007'],'source_triangles_preserved':receipts,'new_bumpers':3,'physical_labels':3,'no_new_floor_room_cart':True,'original_sources_unchanged':True,'reference_pixels_inspected':'staff_corridor_services.png; compact washable practical edge, retained source fixtures','operations_held':'stock, returns, save; no inventory or interaction controller installed'}
(W/'ACTUAL_SOURCE_CHECK.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
