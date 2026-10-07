"""Read-only fresh native scene audit; isolated QA receipt only."""
import bpy,json,struct,hashlib
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[2]
source=P/'source/WP07_listening_salon.blend';export=P/'exports/WP07_listening_salon.glb'
bpy.ops.wm.open_mainfile(filepath=str(source))
deps=bpy.context.evaluated_depsgraph_get();rows=[];fonts=[];preview=[]
for obj in bpy.context.scene.objects:
    if obj.get('SOURCE_PREVIEW_ONLY'):
        preview.append(obj.name);continue
    if obj.type not in {'MESH','CURVE','FONT'}:continue
    if obj.type=='FONT':fonts.append(obj.name)
    ev=obj.evaluated_get(deps);me=ev.to_mesh();pts=[ev.matrix_world@v.co for v in me.vertices]
    if pts:rows.append({'name':obj.name,'local_glb_min':[min(v.x for v in pts),min(v.z for v in pts),-max(v.y for v in pts)],'local_glb_max':[max(v.x for v in pts),max(v.z for v in pts),-min(v.y for v in pts)]})
    ev.to_mesh_clear()
lo=[min(r['local_glb_min'][k] for r in rows) for k in range(3)];hi=[max(r['local_glb_max'][k] for r in rows) for k in range(3)]
imgs=[]
for i in bpy.data.images:
    if i.source!='FILE':continue
    was_loaded=bool(i.has_data);packed=bool(i.packed_file)
    # Native reopening is lazy: force decoding from the retained packed bytes before
    # treating has_data as evidence. This does not change the saved source file.
    packed_bytes=len(i.packed_file.data) if packed else 0
    decoded_first_pixel=list(i.pixels[:4]) if packed else []
    imgs.append({'name':i.name,'has_data_before_decode':was_loaded,'has_data':bool(i.has_data),'packed':packed,'packed_bytes':packed_bytes,'size':list(i.size),'decoded_first_pixel':decoded_first_pixel})
bad_images=[i for i in imgs if not i['has_data'] or not i['packed'] or i['packed_bytes']==0 or len(i['decoded_first_pixel'])!=4]
blob=export.read_bytes();n=struct.unpack_from('<I',blob,12)[0];g=json.loads(blob[20:20+n]);gnames={r.get('name') for r in g['nodes'] if 'mesh' in r};missing_fonts=sorted(set(fonts)-gnames)
checks={'allocation':all(lo[k]>=(-23,0,-34)[k]-.002 and hi[k]<=(23,5.75,34)[k]+.002 for k in range(3)),'all_file_images_loaded_and_packed':not bad_images,'no_external_libraries':not bpy.data.libraries,'preview_floor_present':any('SOURCE_PREVIEW_ONLY_floor' in s for s in preview),'all_authored_signs_exported':bool(fonts) and not missing_fonts}
r={'scope':'Fresh native actual-vertex reload and exported signage correspondence; no render/engine acceptance','checks':checks,'pass':all(checks.values()),'native_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'glb_sha256':hashlib.sha256(blob).hexdigest(),'native_shapes':len(rows),'native_local_gltf_bounds':[lo,hi],'native_world_bounds':[[v+o for v,o in zip(a,[-31,78,-324])] for a in [lo,hi]],'file_images':imgs,'bad_images':bad_images,'external_libraries':[l.filepath for l in bpy.data.libraries],'authored_signage':fonts,'missing_signage':missing_fonts,'preview_objects':preview,'bounds':rows}
(P/'qa/receiving_source_review/NATIVE_RELOAD_RECEIPT.json').write_text(json.dumps(r,indent=2));print(json.dumps({k:v for k,v in r.items() if k not in ['bounds','file_images']}));assert r['pass']
