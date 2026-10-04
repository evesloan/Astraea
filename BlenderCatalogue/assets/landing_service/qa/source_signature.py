"""Read-only editable-source equivalence digest for original and fresh rebuild."""
import bpy,json,hashlib,sys
from pathlib import Path
args=sys.argv[sys.argv.index('--')+1:];bases=[Path(a) for a in args];rows=[]
for base in bases:
 for ident in ['AST-LND-003','AST-LND-004']:
  path=base/'source'/f'{ident}.blend';bpy.ops.wm.open_mainfile(filepath=str(path));data=[]
  for o in sorted(bpy.context.scene.objects,key=lambda x:x.name):
   r={'name':o.name,'type':o.type,'matrix_world':[[float(c) for c in v] for v in o.matrix_world],'parent':o.parent.name if o.parent else None,'properties':{k:o[k] for k in o.keys() if k!='_RNA_UI'}}
   # JSON-normalize ID arrays.
   for k,v in list(r['properties'].items()):
    if hasattr(v,'to_list'):r['properties'][k]=v.to_list()
   if o.type=='MESH':
    r['vertices']=[list(v.co) for v in o.data.vertices];r['polygons']=[list(p.vertices) for p in o.data.polygons];r['uv']=[list(d.uv) for d in o.data.uv_layers.active.data];r['materials']=[m.name for m in o.data.materials];r['modifiers']=[{'type':m.type,'width':m.width if m.type=='BEVEL' else None,'segments':m.segments if m.type=='BEVEL' else None} for m in o.modifiers]
   data.append(r)
  digest=hashlib.sha256(json.dumps(data,sort_keys=True,separators=(',',':')).encode()).hexdigest();rows.append({'base':str(base),'id':ident,'source_file_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'semantic_geometry_hierarchy_material_uv_modifier_sha256':digest,'objects':len(data)})
Path(args[0]+'/qa/source_signature_comparison.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows,indent=2))
