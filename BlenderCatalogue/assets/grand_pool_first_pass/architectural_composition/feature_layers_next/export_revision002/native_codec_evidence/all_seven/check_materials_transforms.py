"""Read-only source-backed material/pixel/transform diagnostics for seven GLBs."""
from pathlib import Path
import io,json,struct,ctypes
import numpy as np
from PIL import Image
from diagnose_arrays import STUDY,read,sha,require,decode_glb
LIBM=ctypes.CDLL('libm.so.6');LIBM.powf.argtypes=[ctypes.c_float,ctypes.c_float];LIBM.powf.restype=ctypes.c_float

def srgb(c):
 out=[]
 for x in np.asarray(c[:3],np.float32):
  v=np.float32(np.float32(12.92)*x) if x<np.float32(.0031308) else np.float32(1.055*float(LIBM.powf(float(x),float(np.float32(1)/np.float32(2.4))))-.055)
  out.append(float(v))
 return out+[float(np.float32(c[3]))] if len(c)==4 else out+[1.0]
def eqf(a,b):return bool(np.array_equal(np.asarray(a,np.float32),np.asarray(b,np.float32)))
def matrix(n):
 require(not any(k in n for k in ['matrix','rotation','scale']),'Expected accepted identity-basis source nodes')
 m=np.eye(4,dtype=np.float32);m[:3,3]=np.asarray(n.get('translation',[0,0,0]),np.float32);return m

def inspect_asset(asset):
 doc,_=decode_glb(asset['path'],asset['sha256']);raw=Path(asset['path']).read_bytes();n=struct.unpack_from('<I',raw,12)[0];binary=raw[28+n:]
 path=STUDY/'output/native_arrays'/f"{asset['name']}_ACTUAL_NATIVE_DUMP.json";dump=read(path);actual={x['name']:x for x in dump['nodes'] if x['name'] in {n['name'] for n in doc['nodes']}};require(len(actual)==len(doc['nodes']),'Native source node mapping missing')
 issues=[];mats=[];trans=[];textures=0
 def flag(ok,category,detail):
  if not ok:issues.append(dict(category=category,**detail))
 nodes={n['name']:n for n in doc['nodes']};parents={doc['nodes'][int(c)]['name']:n['name'] for n in doc['nodes'] for c in n.get('children',[])}
 def world(name):return (world(parents[name])@matrix(nodes[name])).astype(np.float32) if name in parents else matrix(nodes[name])
 for name,node in nodes.items():
  native=actual[name];local=matrix(node);w=world(name);local_ok=eqf(native['local_transform'],local);world_ok=eqf(native['actual_world_transform'],w);flag(local_ok and world_ok,'IMPORT_TRANSFORM_MISMATCH',{'node':name});trans.append(dict(node=name,local_f32_exact=local_ok,import_world_f32_exact=world_ok))
  for surface in native.get('surfaces',[]):
   si=int(surface['surface']);prim=doc['meshes'][int(node['mesh'])]['primitives'][si];gm=doc['materials'][prim['material']];pbr=gm.get('pbrMetallicRoughness',{});am=surface['active_material'];props={k:v['value'] for k,v in am['properties'].items()};checks={}
   checks['material_name']=am['resource_name']==gm['name'];checks['class']=am['class']=='StandardMaterial3D';checks['no_overlay_override']=not native['material_overlay']['present'] and not native['material_override']['present']
   checks['opaque']=props['transparency']==0 and gm.get('alphaMode','OPAQUE')=='OPAQUE';checks['culling']=props['cull_mode']==(2 if gm.get('doubleSided',False) else 0)
   checks['metallic_f32_exact']=eqf(props['metallic'],pbr.get('metallicFactor',1));checks['roughness_f32_exact']=eqf(props['roughness'],pbr.get('roughnessFactor',1));checks['albedo_documented_conversion_exact']=eqf(props['albedo_color'],srgb(pbr.get('baseColorFactor',[1,1,1,1])))
   emission=gm.get('emissiveFactor',[0,0,0]);checks['emission_enabled']=props['emission_enabled']==('emissiveFactor' in gm or 'emissiveTexture' in gm);checks['emission_documented_conversion_exact']=eqf(props['emission'],srgb(emission));checks['emission_strength_f32_exact']=eqf(props['emission_energy_multiplier'],gm.get('extensions',{}).get('KHR_materials_emissive_strength',{}).get('emissiveStrength',1))
   checks['uv_identity']=eqf(props['uv1_scale'],[1,1,1]) and eqf(props['uv1_offset'],[0,0,0]);trows=[];wanted=[]
   for material_property,container,key in [('albedo_texture',pbr,'baseColorTexture'),('emission_texture',gm,'emissiveTexture')]:
    if key not in container:continue
    wanted.append(material_property);ref=container[key];texture=doc['textures'][ref['index']];image=doc['images'][texture['source']];view=doc['bufferViews'][image['bufferView']];start=view.get('byteOffset',0);png=binary[start:start+view['byteLength']]
    nr=next(x for x in am['textures'] if x['property']==material_property);require(not nr['compressed'],'Expected uncompressed runtime image');mode={0:'L',1:'LA',4:'RGB',5:'RGBA'}[int(nr['format'])];source=Image.open(io.BytesIO(png)).convert(mode);source_bytes=source.tobytes();record=nr['actual_pixel_bytes'];require(sha(record['file'])==record['sha256'],'Stored texture bytes changed');native_bytes=Path(record['file']).read_bytes();pixels_equal=source_bytes==native_bytes[:len(source_bytes)];dimensions_equal=source.size==(nr['width'],nr['height']);flag(pixels_equal and dimensions_equal,'TEXTURE_BASE_PIXELS_MISMATCH',{'mesh':name,'material':gm['name'],'property':material_property})
    sampler=doc.get('samplers',[])[texture['sampler']] if 'sampler' in texture else {};linear=sampler.get('magFilter',9729)==9729;minf=sampler.get('minFilter',9987);expected_filter=3 if linear and minf in [9985,9987] else 2 if not linear and minf in [9984,9986] else 1 if linear else 0
    checks['texture_filter']=props['texture_filter']==expected_filter;checks['texture_repeat']=props['texture_repeat']==(sampler.get('wrapS',10497)==10497 and sampler.get('wrapT',10497)==10497)
    trows.append(dict(property=material_property,source_png_sha256=__import__('hashlib').sha256(png).hexdigest(),native_pixel_dump_sha256=record['sha256'],base_pixels_exact=pixels_equal,dimensions_exact=dimensions_equal,format=nr['format'],mipmaps=nr['mipmaps'],base_bytes=len(source_bytes),actual_bytes=len(native_bytes)));textures+=1
   checks['texture_inventory']=sorted(wanted)==sorted(x['property'] for x in am['textures'])
   for k,ok in checks.items():flag(ok,'MATERIAL_'+k.upper(),{'mesh':name,'material':gm['name'],'actual':props.get(k)})
   mats.append(dict(mesh=name,surface=si,material=gm['name'],checks=checks,textures=trows,albedo_actual=props['albedo_color'],albedo_predicted=srgb(pbr.get('baseColorFactor',[1,1,1,1])),emission_actual=props['emission'],emission_predicted=srgb(emission)))
 placement=None
 if asset['family']=='plant':
  composition=read(STUDY/'output/ACTUAL_NATIVE_COMPOSITION_UNVERIFIED.json');p=next(x for x in composition['placements'] if x['source_asset']==asset['name']);position=next(x for x in read(STUDY/'NATIVE_INPUTS.json')['replacement']['assets'] if x['instance']==p['instance'])
  angle=np.float32(position['yaw_radians']);co=np.float32(np.cos(angle));si=np.float32(np.sin(angle));pred=np.array([[co,0,si,0],[0,1,0,0],[-si,0,co,0],[0,0,0,1]],dtype=np.float32);pred[:3,3]=np.asarray(position['position_xyz'],np.float32)
  unchanged=eqf(p['old_transform'],p['candidate_transform']);predicted=eqf(p['candidate_transform'],pred);flag(unchanged and predicted,'PLACEMENT_CHANGED',{'asset':asset['name']})
  placed=read(STUDY/'output/native_arrays'/f"{asset['name']}_PLACED_TRANSFORMS.json");placed_rows=[]
  for row in placed['nodes']:
   expected_world=(pred@world(row['name'])).astype(np.float32);ok=eqf(row['actual_world_transform'],expected_world);flag(ok,'PLACED_NODE_TRANSFORM_MISMATCH',{'node':row['name']});placed_rows.append({'node':row['name'],'exact_f32_world':ok,'max_abs_delta':float(np.max(np.abs(np.asarray(row['actual_world_transform'])-expected_world)))})
  placement=dict(instance=p['instance'],original_candidate_exact=unchanged,source_yaw_position_f32_exact=predicted,unit_scale=eqf(p['unit_scale'],[1,1,1]),nodes=placed_rows)
 return {'asset':asset['name'],'verification':'UNVERIFIED_IMPORT_EQUIVALENCE','installed':False,'geometry_acceptance':False,'manifest_sha256':sha(path),'materials':mats,'transforms':trans,'placement':placement,'texture_occurrences':textures,'issues':issues,'material_post_draw_state':'NOT_RECORDED; no claim of second material snapshot','primary_sources':['https://raw.githubusercontent.com/godotengine/godot/4.6.3-stable/modules/gltf/gltf_document.cpp#L2848','https://raw.githubusercontent.com/godotengine/godot/4.6.3-stable/core/math/color.h#L184','https://raw.githubusercontent.com/godotengine/godot/4.6.3-stable/core/io/image.h#L67']}
