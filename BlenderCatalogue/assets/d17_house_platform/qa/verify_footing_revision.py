"""Prove the bounded RES005 relocation preserves all portal objects and source materials."""
from pathlib import Path
import bpy,json,hashlib,subprocess
R=Path(__file__).resolve().parents[1];C=R.parents[1];BASE='5366abf49708d61cd5c17ce4475e32e90c4ad3f2'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
old=Path('/tmp/d17-res005-footing-baseline.blend')
if not old.exists():old.write_bytes(subprocess.check_output(['git','-C',str(C),'show',BASE+':assets/d17_house_platform/source/AST-RES-005.blend']))
assert sha(old)=='8086a869e18f54c8fd0f7f754468ebf6d890e0bf4627f89d2762ca92f64d732d'
def capture(path):
 bpy.ops.wm.open_mainfile(filepath=str(path));objects={};materials={}
 for o in bpy.context.scene.objects:
  a={'type':o.type,'matrix':[list(r) for r in o.matrix_world],'properties':{k:o[k] for k in o.keys()}}
  if o.type=='MESH':a.update(vertices=[list(v.co) for v in o.data.vertices],faces=[list(f.vertices) for f in o.data.polygons],uv=[list(u.uv) for u in o.data.uv_layers.active.data],materials=[m.name for m in o.data.materials])
  objects[o.name]=a
 for m in bpy.data.materials:
  if not m.use_nodes:continue
  nodes=[]
  for n in m.node_tree.nodes:
   defaults={}
   for p in n.inputs:
    if not hasattr(p,'default_value'):continue
    v=p.default_value
    if hasattr(v,'to_list'):v=v.to_list()
    elif not isinstance(v,(str,int,float,bool)):
     try:v=list(v)
     except TypeError:continue
    defaults[p.name]=v
   row={'type':n.bl_idname,'inputs':defaults}
   if n.type=='TEX_IMAGE':row.update(image_sha256=hashlib.sha256(n.image.packed_file.data).hexdigest(),interpolation=n.interpolation)
   nodes.append(row)
  materials[m.name]=nodes
 return objects,materials
A,MA=capture(old);B,MB=capture(R/'source/AST-RES-005.blend');assert A.keys()==B.keys();changed=sorted(n for n in A if A[n]!=B[n]);assert changed==['D17_SeatedHullFooting_0','D17_SeatedHullFooting_1'];assert MA==MB
D=json.loads((R/'source/section_contract.json').read_text());assert all(u['compiler_candidate']['status'].startswith('HELD') for u in D['units']);assert D['new_walkable_source_meshes']==0
assert sha(C/'assets/starboard_house_upper/source/AST-COM-003.blend')=='d1bde7f87521ae520eded0b115e0217b7d12bb910cee195ac3eb76404027689d'
assert sha(C/'assets/starboard_house_upper/exports/AST-COM-003.glb')=='88842ee744fe33c633e43e2020a55fda2448945de88d6ee163cf60eefb4f1034'
r={'pass':True,'baseline_commit':BASE,'changed_objects':changed,'unchanged_objects':len(A)-len(changed),'materials_and_packed_textures_unchanged':True,'COM003_unchanged_from_partial_stage':True,'source_sha256':sha(R/'source/AST-RES-005.blend'),'export_sha256':sha(R/'exports/AST-RES-005.glb'),'scope':'Only two unadopted footing objects moved; no floor, pier, portal adoption or whole-house acceptance'}
(R/'qa/footing_revision_preservation.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
