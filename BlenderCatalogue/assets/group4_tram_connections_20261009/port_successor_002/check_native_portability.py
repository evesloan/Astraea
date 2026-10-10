from pathlib import Path
import bpy,json,hashlib
W=Path(__file__).resolve().parent;R=Path('/workspace/shared/Astraea_direct_recovery_20261008_hcozu5z4');bpy.ops.wm.open_mainfile(filepath=str(W/'Group4_Port_Successor_002.blend'));meta=json.loads((W/'SUCCESSOR_INTERFACE.json').read_text());rows=json.loads((W/'MESH_PARTS.json').read_text());images=[]
for im in bpy.data.images:
 if im.source!='FILE' or im.size[0]==0:continue
 assert im.packed_file,im.name
 data=bytes(im.packed_file.data);h=hashlib.sha256(data).hexdigest();matches=[p for p,v in meta['source_material_sha256'].items() if v==h];assert matches,im.name
 images.append({'name':im.name,'packed_sha256':h,'retained_source_matches':matches,'size_px':list(im.size)})
meshes=[o for o in bpy.data.objects if o.type=='MESH' and o.get('construction_family')=='group4_tram_connections_port_successor_002'];assert len(meshes)==len(rows)==1375
report={'status':'MOVED_NATIVE_READ_AND_PACKED_SOURCE_PASS','native_file':'Group4_Port_Successor_002.blend','sha256':hashlib.sha256((W/'Group4_Port_Successor_002.blend').read_bytes()).hexdigest(),'editable_meshes':len(meshes),'packed_material_images':images,'native_unchanged_by_check':True,'source_only':True,'not_claimed':['Godot import','operating transport','structural/visual final acceptance']}
(W/'NATIVE_PORTABILITY.json').write_text(json.dumps(report,indent=2)+'\n');print('NATIVE_PORTABLE',len(meshes),'editablemeshes',len(images),'packedimages')
