from pathlib import Path
import bpy,json,hashlib
D=Path(__file__).parent
for V,old,new in [(D,D.parent/'vesper_service_receiving_20261015/native/VESPER_SERVICE_RECEIVER_r001.blend',D/'native/VESPER_SERVICE_RECEIVER_r002.blend'),(D/'orchard',D.parent/'orchard_external_receiving_20261015/native/ORCHARD_SERVICE_GATEWAY_r001.blend',D/'orchard/native/ORCHARD_SERVICE_GATEWAY_r002.blend')]:
 def payloads(p):
  bpy.ops.wm.open_mainfile(filepath=str(p));return {hashlib.sha256(bytes(n.image.packed_file.data)).hexdigest()for o in bpy.data.objects if o.type=='MESH'for m in o.data.materials if m and m.use_nodes for n in m.node_tree.nodes if n.type=='TEX_IMAGE'and n.image and n.image.packed_file}
 a=payloads(old);b=payloads(new);assert a==b;(V/'ALL_REFERENCED_IMAGE_PAYLOADS.json').write_text(json.dumps({'status':'PASS_ALL_ORIGINAL_REFERENCED_IMAGE_BYTES_PRESERVED','payloads':len(a)},indent=2)+'\n')
print('PASS_BOTH_ALL_REFERENCED_IMAGE_BYTES')
