import ast,json,hashlib,numpy as np,struct
from pathlib import Path
C=Path('/workspace/shared/astraea-catalogue-continuation-20261002');R=Path(__file__).resolve().parent
parser=C/'assets/grand_lantern_theater_section/tools/screen_retained_source_neighbours.py';tree=ast.parse(parser.read_text());fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='glb');exec(compile(ast.Module(body=[fn],type_ignores=[]),str(parser),'exec'))
reg={r['catalogue_id']:r for r in json.loads((C/'catalogue_manifest.json').read_text())['assets']};rows={}
for ident in ['AST-BOT-001','AST-BOT-002','AST-BOT-003','AST-BOT-004','AST-BOT-005','AST-BOT-006','AST-BOT-007','AST-BOT-008','AST-BOT-009','AST-BOT-010','AST-BOT-011','AST-SAL-004','AST-RES-003','AST-COM-002']:
 a=reg[ident];meshes=glb(C/a['export']);vs=np.concatenate([v for _,v,_ in meshes]);rows[ident]={'name':a['name'],'source':a['source'],'export':a['export'],'source_sha256':hashlib.sha256((C/a['source']).read_bytes()).hexdigest(),'export_sha256':hashlib.sha256((C/a['export']).read_bytes()).hexdigest(),'bounds_gltf':{'min':vs.min(0).tolist(),'max':vs.max(0).tolist()},'dimensions':(vs.max(0)-vs.min(0)).tolist(),'mesh_bounds':[{'name':n,'min':v.min(0).tolist(),'max':v.max(0).tolist()}for n,v,_ in meshes]}
(R/'RETAINED_FOCAL_ASSET_BOUNDS.json').write_text(json.dumps(rows,indent=2)+'\n')
for k,r in rows.items():print(k,r['name'],[round(x,3)for x in r['dimensions']])
