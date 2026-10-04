"""Source-only label-normal alignment with byte-identical exported GLB geometry."""
import bpy,bmesh,json,hashlib
from pathlib import Path
B=Path(__file__).resolve().parents[1];path=B/'source/AST-HSP-004.blend';old=hashlib.sha256(path.read_bytes()).hexdigest();glb=B/'exports/AST-HSP-004.glb';gh=hashlib.sha256(glb.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(path));ob=bpy.data.objects['guest_return_instruction'];before=list(ob.data.polygons[0].normal)
if ob.data.polygons[0].normal.y>0:
 bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.reverse_faces(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob.data.update()
# Establish each atlas corner from its vertex position, independent of loop order.
for loop in ob.data.loops:
 co=ob.data.vertices[loop.vertex_index].co;ob.data.uv_layers[0].data[loop.index].uv=(0 if co.x<0 else .5,0 if co.z<1.185 else .5)
after=list(ob.data.polygons[0].normal);assert after[1]<-.99
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True);new=hashlib.sha256(path.read_bytes()).hexdigest();assert gh==hashlib.sha256(glb.read_bytes()).hexdigest()
report={'catalogue_id':'AST-HSP-004','operation':'Reverse editable open-label source winding to guest-facing-Y. Vertex positions, role and semantic UV corners preserved. GLB remains byte-identical.','old_source_sha256':old,'new_source_sha256':new,'unchanged_glb_sha256':gh,'before_source_normal':before,'after_source_normal':after}
(B/'qa/source_label_winding_revision.json').write_text(json.dumps(report,indent=2)+'\n')
for f in (B/'AST-HSP-004.manifest.json',B/'manifest.json'):
 m=json.loads(f.read_text());records=[m]if'catalogue_id'in m else m['assets']
 for a in records:
  if a['catalogue_id']=='AST-HSP-004':a['source_sha256']=new;a['source_only_revision']='qa/source_label_winding_revision.json'
 f.write_text(json.dumps(m,indent=2)+'\n')
print(report)
