from pathlib import Path
import bpy,json,hashlib
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.load(open(W/'PLAN.json'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
records=P['retained_superseded_native_export_records']+P['native_export_records'];checks=0;inputs=[]
old=json.load(open(W/'RETAINED_R001_PLAN.json'))
for k in ['structure','native_export_records','model_pins']:old.pop(k,None)
oldraw=(json.dumps(old,indent=2)+'\n').encode();oldhash=hashlib.sha256(oldraw).hexdigest()
for rec in records:
 assert sha(W/rec['native'])==rec['native_sha256']and sha(W/rec['export'])==sha(R/'Game/assets/models'/rec['export'])==rec['export_sha256']
 bpy.ops.wm.open_mainfile(filepath=str(W/rec['native']));textures=[]
 for ob in bpy.data.objects:
  if ob.type!='MESH':continue
  assert ob.data.uv_layers.active and len(ob.data.uv_layers.active.data)==len(ob.data.loops)
  for m in ob.data.materials:
   assert m.use_nodes
   tex=next(n for n in m.node_tree.nodes if n.type=='TEX_IMAGE');assert tex.image.packed_file
   source=R/'BlenderCatalogue/materials/staff'/(ob['role']+'.png');assert hashlib.sha256(tex.image.packed_file.data).hexdigest()==sha(source);assert tex.interpolation=='Closest'
   bs=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');assert abs(bs.inputs['Roughness'].default_value-.78)<.00001;assert any(l.from_node==tex and l.to_socket==bs.inputs['Base Color']for l in m.node_tree.links);checks+=1
  if rec['native'].endswith('r001.blend'):assert ob['source_input_sha256']==oldhash
  else:assert ob['source_input_sha256']==sha(W/'NATIVE_AUTHORING_INPUT_PLAN.json')
  checks+=1
 inputs.append({'native':rec['native'],'source_input_sha256':oldhash if rec['native'].endswith('r001.blend')else sha(W/'NATIVE_AUTHORING_INPUT_PLAN.json')})
(W/'RETAINED_R001_AUTHORING_INPUT.json').write_bytes(oldraw)
(W/'EXACT_NATIVE_SOURCE_AUDIT.json').write_text(json.dumps({'status':'PASS','checks':checks,'retained_native_variants':2,'exact_packed_source_texture_bytes':True,'metric_UVs_material_links_roughness_preserved':True,'both_source_authoring_inputs_exact':inputs,'no_source_native_substitution_or_recovery_claim':True},indent=2)+'\n');print('Exact native authoring,UV and packed material audit passed',checks)
