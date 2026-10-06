import ast,json,struct,hashlib,numpy as np
from pathlib import Path
C=Path('/workspace/shared/astraea-catalogue-continuation-20261002');REG={a['catalogue_id']:a for a in json.loads((C/'catalogue_manifest.json').read_text())['assets']}
p=Path('/workspace/shared/astraea-catalogue-continuation-20261002/assets/grand_lantern_theater_section/tools/screen_retained_source_neighbours.py');tree=ast.parse(p.read_text());fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='glb');exec(compile(ast.Module(body=[fn],type_ignores=[]),str(p),'exec'))
ids=['AST-STF-006','AST-LGT-001','AST-CUL-001','AST-CUL-002','AST-CUL-004','AST-FUR-001','AST-FUR-002','AST-FUR-003','AST-STF-007','AST-LND-004','AST-BOT-004','AST-BOT-005','AST-BOT-006','AST-BOT-002','AST-BOT-003','AST-BOT-012','AST-CRW-002','AST-CRW-003']
rows={}
for id in ids:
 a=REG[id];vs=np.concatenate([v for _,v,_ in glb(C/a['export'])]);rows[id]={'catalogue_id':id,'name':a.get('name'),'source':a['source'],'export':a['export'],'source_sha256':hashlib.sha256((C/a['source']).read_bytes()).hexdigest(),'export_sha256':hashlib.sha256((C/a['export']).read_bytes()).hexdigest(),'bounds_gltf':{'min':vs.min(0).tolist(),'max':vs.max(0).tolist()},'dimensions':(vs.max(0)-vs.min(0)).tolist()}
print(json.dumps(rows,indent=2));Path(__file__).with_name('RETAINED_MODULE_MEASUREMENTS.json').write_text(json.dumps(rows,indent=2)+'\n')
