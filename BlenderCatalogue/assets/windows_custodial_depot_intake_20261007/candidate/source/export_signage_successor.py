"""Export only from the exact retained native. Never rebuild architecture or save .blend."""
from pathlib import Path
import bpy,json,hashlib,struct
P=Path(__file__).resolve().parents[1];PIN=json.loads((P/'qa/INPUT_PINS.json').read_text());N=P/PIN['successor_native_path'];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert bpy.app.version[:3]==(4,3,2);assert sha(N)==PIN['original_native_sha256']
bpy.ops.wm.open_mainfile(filepath=str(N));C=bpy.data.collections['WP09_ARCHITECTURE'];expected=set(PIN['expected_authored_sign_names']);fonts={o.name:o for o in C.objects if o.type=='FONT'}
assert set(fonts)==expected and len(fonts)==24
text_before={name:{'body':o.data.body,'matrix_world':[list(r) for r in o.matrix_world]} for name,o in fonts.items()};assert all(r['body'] for r in text_before.values())
images=[]
for im in bpy.data.images:
 if im.type!='IMAGE':continue
 packed=bool(im.packed_file);data=bytes(im.packed_file.data) if packed else b'';pix=list(im.pixels[:4]) if packed else []
 images.append({'name':im.name,'packed':packed,'bytes':len(data),'packed_sha256':hashlib.sha256(data).hexdigest() if data else None,'decoded':bool(im.has_data) and len(pix)==4,'dimensions':list(im.size)})
assert images and all(r['packed'] and r['bytes']>0 and r['decoded'] for r in images)
assert len(bpy.data.libraries)==0
original_meshes={o.name for o in C.objects if o.type=='MESH'};assert len(original_meshes)==7376
# Save is deliberately absent. Only editable lettering is converted in memory.
bpy.ops.object.select_all(action='DESELECT')
for name in sorted(expected):
 o=bpy.data.objects[name];o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.convert(target='MESH');o.select_set(False)
bpy.ops.object.select_all(action='DESELECT')
for o in C.objects:
 if o.type in {'MESH','CURVE','EMPTY','LIGHT'}:o.select_set(True)
G=P/'exports/WP09_custodial_depot.glb'
bpy.ops.export_scene.gltf(filepath=str(G),export_format='GLB',use_selection=True,export_yup=True,export_extras=True,export_lights=True,export_cameras=False)
raw=G.read_bytes();n=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+n]);meshes={o.get('name'):o for o in doc['nodes'] if 'mesh' in o}
assert set(meshes)==original_meshes|expected
signs=[]
for name in sorted(expected):
 node=meshes[name];primitives=doc['meshes'][node['mesh']]['primitives'];count=sum(doc['accessors'][p['attributes']['POSITION']]['count'] for p in primitives)
 assert count>0;signs.append({'name':name,'position_vertices':count,'mesh_node_present':True})
assert len(signs)==24 and not any('SOURCE_PREVIEW_ONLY' in o.get('name','') for o in doc['nodes'])
assert sha(N)==PIN['original_native_sha256']
# Fresh reopen, not just an unchanged file hash, proves all native text stays editable.
bpy.ops.wm.open_mainfile(filepath=str(N));native_fonts={o.name:o for o in bpy.data.collections['WP09_ARCHITECTURE'].objects if o.type=='FONT'}
assert set(native_fonts)==expected;assert all(o.data.body==text_before[name]['body'] for name,o in native_fonts.items())
assert sha(N)==PIN['original_native_sha256']
r={'scope':'Export-only FONT parity correction; no architecture rebuild, native save, render or runtime adoption','pass':True,'native_sha256_unchanged':sha(N),'original_glb_sha256':PIN['original_glb_sha256'],'successor_glb_sha256':sha(G),'native_text_reopened_editable':24,'exact_exported_section_sign_count':len(signs),'original_mesh_node_count':len(original_meshes),'successor_mesh_node_count':len(meshes),'unrelated_mesh_names_added_or_removed':[],'signs':signs,'native_text_inventory':text_before,'native_packed_images':images,'originals_unchanged':True,'external_libraries':[]}
(P/'qa/EXPORT_ONLY_RECEIPT.json').write_text(json.dumps(r,indent=2));print('WP09_EXPORT_ONLY_PASS',json.dumps({k:v for k,v in r.items() if k not in ['signs','native_text_inventory','native_packed_images']}))
