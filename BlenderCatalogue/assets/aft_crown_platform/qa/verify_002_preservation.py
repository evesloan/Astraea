from pathlib import Path
import bpy,json,hashlib
R=Path(__file__).resolve().parents[1];C=R.parents[1];Q=R/'qa';A=C/'assets/aft_command'
allow=set(json.loads((Q/'002_allowlist.json').read_text())['allowed_old_meshes'])
def capture(path):
 bpy.ops.wm.open_mainfile(filepath=str(path));result={}
 for o in bpy.context.scene.objects:
  q={'type':o.type,'matrix':list(v for row in o.matrix_world for v in row),'properties':{k:o[k]for k in o.keys()}}
  if o.type=='MESH':q.update(vertices=[list(v.co)for v in o.data.vertices],polygons=[list(f.vertices)for f in o.data.polygons],uv=[list(x.uv)for x in o.data.uv_layers.active.data],materials=[m.name for m in o.data.materials])
  result[o.name]=q
 return result
old=capture(Q/'baseline_002_AST-CMD-002.blend');new=capture(A/'source/AST-CMD-002.blend');unchanged=[];changed=[];removed=[]
for name,before in old.items():
 if name not in new:assert name in allow,name;removed.append(name);continue
 if before==new[name]:unchanged.append(name)
 else:assert name in allow,name;changed.append(name)
added=sorted(set(new)-set(old));new_markers=json.loads((Q/'002_allowlist.json').read_text())['new_markers']
for name in added:assert name in new_markers or ('_AftReturn_'in name and new[name]['type']=='MESH'),name
od=json.loads((Q/'baseline_002_section_contract.json').read_text());nd=json.loads((A/'source/section_contract.json').read_text())
assert nd['doors'][:len(od['doors'])]==od['doors'];assert len(nd['doors'])==len(od['doors'])+2
for key in od:
 if key!='doors':assert od[key]==nd[key],key
report={'pass':True,'source_before_sha256':hashlib.sha256((Q/'baseline_002_AST-CMD-002.blend').read_bytes()).hexdigest(),'source_after_sha256':hashlib.sha256((A/'source/AST-CMD-002.blend').read_bytes()).hexdigest(),'unchanged_object_count':len(unchanged),'allowed_old_meshes':sorted(allow),'changed_old_meshes':changed,'removed_old_meshes':removed,'added_objects':added,'all_old_markers_exact':True,'all_old_contract_fields_exact_except_two_appended_doors':True,'method':'Actual complete Blender object capture: geometry, topology,UV,material slots,transforms,custom properties; every unapproved old mesh and all old markers exactly unchanged'}
(Q/'002_actual_preservation.json').write_text(json.dumps(report,indent=2)+'\n');print('PRESERVATION_PASS',len(unchanged),len(changed),len(removed),len(added))
