"""Add editable exact floor receiving and bridge to a new native successor."""
from pathlib import Path
import bpy,json,hashlib
R=Path(__file__).resolve().parents[2];D=R/'Game/orchard_tram_interior_20261025/integration'
source=R/'BlenderCatalogue/assets/orchard_tram_interior_20261025/r003/OrchardInteriorRoute.blend'
out=source.parent.parent/'integration/OrchardIntegratedReceiving.blend'
assert not out.exists();before=hashlib.sha256(source.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(source))
proof=json.loads((D/'PIT_AND_BINDING.json').read_text())
mat=next(m for m in bpy.data.materials if 'stone' in m.name.lower())
def xyz(v):return(v[0],-v[2],v[1])
for region in [proof['after'],proof['old_pit_infill']]:
 verts=[];faces=[];y=region['floor_y'];bottom=y-region['thickness']
 def face(points):
  start=len(verts);verts.extend(xyz(v) for v in points);faces.append(tuple(range(start,start+len(points))))
 for t in region['triangles']:
  face([(p[0],y,p[1]) for p in t]);face([(p[0],bottom,p[1]) for p in reversed(t)])
 for ring in region['rings']:
  for a,b in zip(ring,ring[1:]+ring[:1]):face([(a[0],y,a[1]),(b[0],y,b[1]),(b[0],bottom,b[1]),(a[0],bottom,a[1])])
 mesh=bpy.data.meshes.new(region['id']);mesh.from_pydata(verts,[],faces);mesh.update();mesh.materials.append(mat)
 o=bpy.data.objects.new(region['id'],mesh);bpy.context.collection.objects.link(o);o['floor_receiving_source']='PIT_AND_BINDING.json';o['production_selected']=False
old=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(D/'ForemidBridge.glb'));new=set(bpy.data.objects)-old
for o in new:
 if o.parent not in new:o.location.x+=14.9;o.location.y+=236.1;o.location.z+=56.1
text=bpy.data.texts.new('EXACT_FLOOR_AND_BRIDGE_RECEIPT.json');text.write(json.dumps(proof,indent=2))
bpy.context.scene['status']='Unselected integrated receiving; installed/circulation/operation acceptance pending'
bpy.ops.file.pack_all();out.parent.mkdir(exist_ok=True);bpy.ops.wm.save_as_mainfile(filepath=str(out))
assert hashlib.sha256(source.read_bytes()).hexdigest()==before
receipt={'original_native_unchanged_sha256':before,'successor':out.relative_to(R).as_posix(),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'bytes':out.stat().st_size,'bridge_nodes':len(new),'floor_regions':2,'selected':False}
(D/'NATIVE_RECEIPT.json').write_bytes((json.dumps(receipt,indent=2)+'\n').encode());print(json.dumps(receipt))
