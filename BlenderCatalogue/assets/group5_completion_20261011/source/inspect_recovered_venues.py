"""Read recovered originals with their matching reader; never save them."""
from pathlib import Path
import bpy,json,hashlib
P=Path(__file__).resolve().parents[1]
source=json.loads((P/'qa/VENUE_SOURCE_RECOVERY.json').read_text())
rows=[]
for row in source['rows']:
    path=P/row['native']['recovered_path'];before=hashlib.sha256(path.read_bytes()).hexdigest()
    bpy.ops.wm.open_mainfile(filepath=str(path))
    rows.append({'programme_key':row['programme_key'],'native':row['native']['recovered_path'],'sha256_before':before,'unchanged_after_read':hashlib.sha256(path.read_bytes()).hexdigest()==before,'reader':bpy.app.version_string,'scene_meshes':sum(o.type=='MESH' for o in bpy.context.scene.objects),'linked_libraries':[x.filepath for x in bpy.data.libraries],'packed_images':sum(x.packed_file is not None for x in bpy.data.images),'unpacked_file_images':[x.name for x in bpy.data.images if x.source=='FILE' and not x.packed_file],'runtime_export_identity':row['archived_export_matches_current_runtime'],'scope':'Read-only inventory of exact archive-native bytes;not renewed native/runtime geometric,visual,operational or whole-group acceptance'})
r={'status':'PASS_READ_ONLY_SOURCE_INVENTORY' if all(x['unchanged_after_read'] for x in rows) else 'HOLD','rows':rows,'source_acceptance':'five current export identities;D05 later entry-correction source still held;no original source resaved','whole_group_accepted':False}
(P/'qa/RECOVERED_VENUE_READ_ONLY.json').write_text(json.dumps(r,indent=2)+'\n');print('GROUP5_RECOVERED_NATIVE_READ',r['status'],len(rows))
