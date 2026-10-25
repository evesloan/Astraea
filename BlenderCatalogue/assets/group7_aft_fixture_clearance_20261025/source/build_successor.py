"""Bounded authored successor: one complete fixture raised50mm; originals immutable."""
import bpy, pathlib, json, hashlib, struct, math
from mathutils import Vector
ROOT=pathlib.Path(__file__).resolve().parents[4]
OUT=pathlib.Path(__file__).resolve().parents[1]
GAME=ROOT/'Game/group7_aft_fixture_clearance_20261025'
SOURCE=ROOT/'BlenderCatalogue/assets/aft_crown_platform/source/AST-CMD-005.blend'
ORIGINAL=ROOT/'Game/assets/models/AST-CMD-005.glb'
NATIVE=OUT/'AST-CMD-005_fixture_clearance_r002.blend'
EXPORT=GAME/'AST-CMD-005_fixture_clearance_r002.glb'
DELTA=.05
PARTS=['ACP_CentreLight_Z193p7_Housing','ACP_CentreLight_Z193p7_Housing.001','ACP_CentreLight_Z193p7_Lens','ACP_CentreLight_Z193p7_Lens.001']
MARKER='DATUM_light_acp_centrelight_z193p7'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(SOURCE)=='4f96d43ec2d5c018451704168809592d9ca28269b07b7820421f482f4f5c92b9'
assert sha(ORIGINAL)=='323a26fe17cb9d6bd652309c0a4c99e4d1ce2d3316526b4d125d732dec0c0cf6'
assert not NATIVE.exists() and not EXPORT.exists(),'Preserve existing outputs'
OUT.mkdir(parents=True,exist_ok=True);GAME.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
def fingerprint(o):
 data={'type':o.type,'matrix':[list(r) for r in o.matrix_world],'materials':[m.name if m else None for m in o.data.materials] if o.type=='MESH' else []}
 if o.type=='MESH':data.update(vertices=[list(v.co) for v in o.data.vertices],polygons=[list(p.vertices) for p in o.data.polygons])
 return hashlib.sha256(json.dumps(data,sort_keys=True).encode()).hexdigest()
before={o.name:fingerprint(o) for o in bpy.data.objects}
poses={n:[list(bpy.data.objects[n].matrix_world@v.co) for v in bpy.data.objects[n].data.vertices] for n in PARTS}
for name in PARTS+[MARKER]:
 o=bpy.data.objects.get(name);assert o is not None,name
 o.location.z+=DELTA
bpy.context.view_layer.update()
for o in bpy.data.objects:
 if o.name not in PARTS+[MARKER]:assert fingerprint(o)==before[o.name],o.name
for n in PARTS:
 for previous,v in zip(poses[n],bpy.data.objects[n].data.vertices):
  expected=Vector(previous)+Vector((0,0,DELTA));assert (bpy.data.objects[n].matrix_world@v.co-expected).length<.00002
for image in bpy.data.images:
 if image.source=='FILE' and not image.packed_file:
  assert image.has_data,'Missing native image: '+image.name
  image.pack()
bpy.context.scene['authored_successor']='AST-CMD-005 complete centre fixture Z193.7 raised50mm; original structural geometry unchanged'
bpy.ops.wm.save_as_mainfile(filepath=str(NATIVE))
raw=ORIGINAL.read_bytes();assert raw[:4]==b'glTF'
jn=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+jn]);offset=20+jn
bn,kind=struct.unpack_from('<II',raw,offset);assert kind==0x004e4942
binary=bytearray(raw[offset+8:offset+8+bn]);old_binary=bytes(binary)
changes=[];allowed_offsets=set()
for node in doc['nodes']:
 name=node.get('name','')
 if name==MARKER:node['translation'][1]+=DELTA
 if not(name.startswith(('ACP_CELL_X-1_Y13_Z24_','ACP_CELL_X0_Y13_Z24_')) and name.endswith(('ASTRAEA_aft_platform_warm_opal','ASTRAEA_champagne_metal'))):continue
 for primitive in doc['meshes'][node['mesh']]['primitives']:
  ai=primitive['attributes']['POSITION'];a=doc['accessors'][ai];v=doc['bufferViews'][a['bufferView']]
  assert a['componentType']==5126 and a['type']=='VEC3'
  start=v.get('byteOffset',0)+a.get('byteOffset',0);stride=v.get('byteStride',12);count=0;coords=[]
  for i in range(a['count']):
   at=start+i*stride;x,y,z=struct.unpack_from('<fff',binary,at)
   if abs(x)<=.721 and 110.469<=y<=111.241 and 193.479<=z<=193.921:
    struct.pack_into('<f',binary,at+4,y+DELTA);allowed_offsets.update(range(at+4,at+8));count+=1
   coords.append(struct.unpack_from('<fff',binary,at))
  assert count==24,(name,count)
  a['min']=[min(p[i] for p in coords) for i in range(3)];a['max']=[max(p[i] for p in coords) for i in range(3)]
  changes.append({'node':name,'position_accessor':ai,'changed_vertices':count,'bounds_min':a['min'],'bounds_max':a['max']})
assert len(changes)==4
assert all(a==b or i in allowed_offsets for i,(a,b) in enumerate(zip(old_binary,binary)))
js=json.dumps(doc,separators=(',',':'),ensure_ascii=False).encode();js+=b' '*((-len(js))%4)
out=struct.pack('<4sII',b'glTF',2,12+8+len(js)+8+len(binary))+struct.pack('<II',len(js),0x4e4f534a)+js+struct.pack('<II',len(binary),0x004e4942)+binary
EXPORT.write_bytes(out)
receipt={'baseline_native':str(SOURCE.relative_to(ROOT)),'baseline_native_sha256':sha(SOURCE),'baseline_model_sha256':sha(ORIGINAL),'successor_native_sha256':sha(NATIVE),'successor_model_sha256':sha(EXPORT),'delta_y_m':DELTA,'changed_native_objects':PARTS+[MARKER],'unchanged_native_objects':len(before)-5,'changed_runtime_batches':changes,'preserved_binary_bytes_except_selected_Y_components':True,'lens_clearance_m':4.02,'housing_beam_overlap_y_m':.11,'source_floor_y':106.5,'fixture_marker':MARKER,'light_energy_range_angle_colour_preserved':True,'runtime_installed_accepted':False}
(OUT/'BUILD_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
(GAME/'BUILD_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
print('FIXTURE_SUCCESSOR',json.dumps(receipt))
