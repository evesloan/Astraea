from pathlib import Path
import bpy,json,hashlib
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.load(open(W/'PLAN.json'));sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();pins={f:sha(R/f)for f in P['source_pins']}
def payload(m):
 bs=m.node_tree.nodes.get('Principled BSDF');imgs=[]
 for node in m.node_tree.nodes:
  if node.type=='TEX_IMAGE' and node.image:
   im=node.image;assert im.packed_file is not None;imgs.append({'sha256':hashlib.sha256(bytes(im.packed_file.data)).hexdigest(),'colorspace':im.colorspace_settings.name,'interpolation':node.interpolation,'size':list(im.size)})
 return {'roughness':bs.inputs['Roughness'].default_value,'images':imgs,'links':[(l.from_node.type,l.from_socket.name,l.to_node.type,l.to_socket.name)for l in m.node_tree.links]}
expected={}
for file in sorted({q['material_native']for q in P['parts']}):
 bpy.ops.wm.open_mainfile(filepath=str(R/file))
 for row in P['parts']:
  if row['material_native']==file:expected[row['name']]=[payload(m)for m in bpy.data.objects[row['source_name']].data.materials]
bpy.ops.wm.open_mainfile(filepath=str(W/P['structure']['native']))
for row in P['parts']:assert [payload(m)for m in bpy.data.objects[row['name']].data.materials]==expected[row['name']],row['name']
for f,h in pins.items():assert sha(R/f)==h
for f,h in P['source_protected_native_exports'].items():assert sha(R/f)==h
(W/'EXACT_NATIVE_MATERIAL_AUDIT001.json').write_text(json.dumps({'status':'PASS','fitted_meshes':len(P['parts']),'original_material_packed_texture_bytes_roughness_links_exact':True,'original_native_files_byte_identical':len(P['source_protected_native_exports']),'source_pins_unchanged':True,'selected_native':P['structure']['native'],'selected_fresh_repeat_identical':P['structure']['fresh_native_repeat_identical']},indent=2)+'\n');print('Original material audit passed',len(P['parts']))
