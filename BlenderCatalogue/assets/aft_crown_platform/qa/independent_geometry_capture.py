from pathlib import Path
import bpy,json,hashlib
R=Path(__file__).resolve().parents[1]; Q=R/'qa'; A=R.parent/'aft_command'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def val(v):
 if isinstance(v,(str,int,float,bool)) or v is None:return v
 try:return list(v)
 except:return str(v)
def capture(path):
 bpy.ops.wm.open_mainfile(filepath=str(path));out={};mats={}
 for o in bpy.context.scene.objects:
  d={'type':o.type,'matrix':[list(r) for r in o.matrix_world], 'properties':{k:val(o[k]) for k in o.keys()}}
  if o.type=='MESH':
   vs=[o.matrix_world@v.co for v in o.data.vertices]
   d.update(vertices_world=[[v.x,v.z,-v.y] for v in vs],polygons=[list(f.vertices) for f in o.data.polygons],material_indices=[f.material_index for f in o.data.polygons],uv={u.name:[list(x.uv) for x in u.data] for u in o.data.uv_layers},materials=[m.name if m else None for m in o.data.materials])
  out[o.name]=d
 for m in bpy.data.materials:
  d={'diffuse_color':list(m.diffuse_color),'roughness':m.roughness,'metallic':m.metallic,'properties':{k:val(m[k]) for k in m.keys()}}
  if m.node_tree:
   d['nodes']=[{'name':n.name,'type':n.type,'inputs':{s.name:val(s.default_value) for s in n.inputs if hasattr(s,'default_value')},'image':n.image.filepath if n.type=='TEX_IMAGE' and n.image else None} for n in m.node_tree.nodes]
   d['links']=[(l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name) for l in m.node_tree.links]
  mats[m.name]=d
 return out,mats
old,om=capture(Q/'baseline_002_AST-CMD-002.blend');new,nm=capture(A/'source/AST-CMD-002.blend')
allow=set(json.loads((Q/'002_allowlist.json').read_text())['allowed_old_meshes']); unauthorized=[];changes=[];removed=[]
for n,v in old.items():
 if n not in new:removed.append(n)
 elif v!=new[n]:changes.append(n)
 if (n not in new or v!=new[n]) and n not in allow:unauthorized.append(n)
used={m for n,v in old.items() if n not in allow and v['type']=='MESH' for m in v['materials']};material_changes=[m for m in used if om[m]!=nm[m]]
actual,materials=capture(R/'source/AST-CMD-005.blend');ledger=json.loads((R/'source/geometry_parts.json').read_text())['parts'];errors=[];max_error=0
for p in ledger:
 a=actual[p['name']];ev=p['vertices_world'];av=a['vertices_world'];e=max(abs(x-y) for v,w in zip(av,ev) for x,y in zip(v,w));max_error=max(e,max_error)
 if len(av)!=len(ev) or e>2e-5:errors.append(p['name'])
assert not errors and not unauthorized and not material_changes,(errors,unauthorized,material_changes)
assert len([v for v in actual.values() if v['type']=='MESH'])==len(ledger)
r={'pass':True,'hashes':{'005_source':sha(R/'source/AST-CMD-005.blend'),'005_export':sha(R/'exports/AST-CMD-005.glb'),'005_geometry_ledger':sha(R/'source/geometry_parts.json'),'002_source':sha(A/'source/AST-CMD-002.blend'),'002_export':sha(A/'exports/AST-CMD-002.glb'),'002_baseline':sha(Q/'baseline_002_AST-CMD-002.blend')},'005_actual_mesh_count':len(ledger),'ledger_max_coordinate_error_m':max_error,'002_changed':changes,'002_removed':removed,'002_added':sorted(set(new)-set(old)),'002_unauthorized_changes':unauthorized,'002_unchanged_count':sum(n in new and old[n]==new[n] for n in old),'002_unchanged_used_material_count':len(used),'002_unchanged_material_changes':material_changes,'005_actual_meshes':{n:v for n,v in actual.items() if v['type']=='MESH'}}
(Q/'independent_actual_geometry.json').write_text(json.dumps(r,separators=(',',':'))+'\n');print('INDEPENDENT_ACTUAL_PASS',len(ledger),max_error,r['002_unchanged_count'])
