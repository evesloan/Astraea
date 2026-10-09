from pathlib import Path
import json,struct,ast,sys,hashlib,io
import numpy as np
from PIL import Image
O=Path(__file__).resolve().parent;B=O/'native_attempts/build002';S=O.parent
sys.path.insert(0,str(S/'botanical_receiving_court_build_20261007/python_deps'))
from shapely.geometry import Polygon,box,LineString
from shapely.ops import unary_union
ns={'np':np,'json':json,'struct':struct}
for p,names in [(S/'lounge_entry_successors_20261008/patch_runtime.py',{'read','acc','meshes'}),(S/'lounge_entry_successors_20261008/verify_geometry.py',{'clip','box_hits'})]:exec(compile(ast.Module(body=[n for n in ast.parse(p.read_text()).body if isinstance(n,ast.FunctionDef)and n.name in names],type_ignores=[]),str(p),'exec'),ns)
raw=(B/'AST-RCV-D12-PAIR-001.glb').read_bytes();d,b=ns['read'](raw);ms=ns['meshes'](d,b);snapshot=json.loads((B/'NATIVE_SNAPSHOT.json').read_text());source=json.loads((O/'GUARD_SOLIDS.json').read_text());assert len(ms)==116
assert not d.get('extensionsUsed') or all(x!='KHR_draco_mesh_compression' for x in d['extensionsUsed'])
rows=[]
for name,v,ix in ms:
 native=snapshot['objects'][name];node=next(n for n in d['nodes'] if n.get('name')==name);assert not any(k in node for k in ['matrix','rotation','scale','translation']);prim=d['meshes'][node['mesh']]['primitives'];assert len(prim)==1;pr=prim[0];norm=ns['acc'](d,b,pr['attributes']['NORMAL']);uv=ns['acc'](d,b,pr['attributes']['TEXCOORD_0']);assert len(ix)==len(native['triangles'])
 nv=np.array(native['vertices'])[:,[0,2,1]]*np.array([1,1,-1]);nn=np.array(native['normals'])[:,[0,2,1]]*np.array([1,1,-1]);nu=np.array(native['uv']);nu[:,1]=1-nu[:,1]
 # Match each exported corner by native triangle POSITION/NORMAL/UV, allowing cyclic triangle order.
 unmatched=list(range(len(native['triangles'])));maxv=maxn=maxuv=0
 for tri in ix:
  found=None
  for j in unmatched:
   vv=nv[native['triangles'][j]];loops=native['triangle_loops'][j]
   for shift in range(3):
    order=np.roll(np.arange(3),shift);err=float(np.max(np.abs(v[tri]-vv[order])))
    if err<2e-5:
     ne=float(np.max(np.abs(norm[tri]-nn[np.array(loops)[order]])));ue=float(np.max(np.abs(uv[tri]-nu[np.array(loops)[order]])))
     if ne<1e-4 and ue<4e-5:found=(j,err,ne,ue);break
   if found:break
  assert found,(name,tri.tolist());unmatched.remove(found[0]);maxv=max(maxv,found[1]);maxn=max(maxn,found[2]);maxuv=max(maxuv,found[3])
 assert not unmatched and np.all(np.isfinite(uv)) and np.all(np.isfinite(norm));assert np.max(abs(np.linalg.norm(norm,axis=1)-1))<2e-6
 mat=d['materials'][pr['material']];assert mat['name']==native['materials'][0];assert node['extras']['support']==native['props']['support'];assert node['extras']['astraea_material_role']==native['props']['astraea_material_role']
 # Recompute positive winding volume from actual exported triangles.
 volume=float(sum(np.dot(t[0],np.cross(t[1],t[2]))for t in v[ix])/6);assert volume>0
 tn=np.cross(v[ix][:,1]-v[ix][:,0],v[ix][:,2]-v[ix][:,0]);length=np.linalg.norm(tn,axis=1);assert np.all(length>1e-10);tn/=length[:,None];assert np.min(np.einsum('ij,ij->i',tn,norm[ix[:,0]]))>.9999
 rows.append({'name':name,'triangles':len(ix),'native_export_vertex_max_delta_m':maxv,'normal_max_delta':maxn,'uv_max_delta':maxuv,'positive_winding_volume_m3':volume,'support_and_material_identity_exact':True})
images=[]
for image in d['images']:
 view=d['bufferViews'][image['bufferView']];embedded=bytes(b[view.get('byteOffset',0):view.get('byteOffset',0)+view['byteLength']]);sha=hashlib.sha256(embedded).hexdigest();native=next(v for name,v in snapshot['images'].items() if name.startswith(image['name']));assert sha==native['packed_sha256'];im=Image.open(io.BytesIO(embedded));assert list(im.size)==native['size'];images.append({'name':image['name'],'embedded_bytes':len(embedded),'sha256':sha,'native_packed_bytes_exact':True,'size':list(im.size)})
for m in d['materials']:
 n=snapshot['materials'][m['name']];bs=next(x for x in n['nodes']if x['type']=='BSDF_PRINCIPLED')['inputs'];pbr=m['pbrMetallicRoughness'];assert abs(pbr.get('metallicFactor',1)-bs['Metallic'])<1e-7 and abs(pbr.get('roughnessFactor',1)-bs['Roughness'])<1e-7
# Actual exported support, clear strips, source mesh interiors and self contacts.
compiled=json.loads((O/'isolated/Game/data/generated/structural_meshes.json').read_text());floor=unary_union([Polygon(t)for r in compiled['regions']if r['floor_y']==78 for t in r['triangles']]);geoms={};source_ms={};checks=[]
for key in ['D12_directory_07','D12_directory_08']:source_ms[key]=ns['meshes'](*ns['read']((S/'lounge_entry_successors_20261008'/key/'exports'/f'{key}_entry_successor.glb').read_bytes()))
for name,v,ix in ms:
 key=name[:16];assert key in source_ms
 plan=unary_union([Polygon(t[:,[0,2]])for t in v[ix]if Polygon(t[:,[0,2]]).area>1e-12]);unsupported=plan.difference(floor).area;clear=plan.intersection(box(-16,214,16,218)).area;assert unsupported<1e-6 and clear==0,(name,unsupported,clear)
 yz=unary_union([Polygon(t[:,[1,2]])for t in v[ix]if Polygon(t[:,[1,2]]).area>1e-12]);geoms[name]=(float(v[:,0].min()),float(v[:,0].max()),yz)
 hits=[]
 if 'SourceProfiledTerminal' not in name:
  hits=ns['box_hits'](source_ms[key],v.min(0)+2e-5,v.max(0)-2e-5);assert not hits,(name,hits)
 checks.append({'name':name,'unsupported_plan_area_m2':unsupported,'clear_strip_intrusion_m2':clear,'source_box_interior_hits_with_20micrometre_export_tolerance':hits})
contacts=[];graph={n:set()for n in geoms};floor_names={n for n,v,ix in ms if abs(v[:,1].min()-78)<1e-7};maxoverlap=0
for i,(an,(a,b,p))in enumerate(geoms.items()):
 for bn,(c,e,q)in list(geoms.items())[i+1:]:
  dx=min(b,e)-max(a,c);cross=p.intersection(q);vol=max(dx,0)*cross.area;maxoverlap=max(maxoverlap,vol);assert vol<1e-10,(an,bn,vol)
  face=cross.area if abs(dx)<1e-8 else cross.length*dx if dx>0 and p.distance(q)<1e-8 else 0
  if face>1e-10:contacts.append({'a':an,'b':bn,'face_area_m2':face});graph[an].add(bn);graph[bn].add(an)
reach=set(floor_names)
while True:
 nxt=reach|{b for a in reach for b in graph[a]}
 if nxt==reach:break
 reach=nxt
assert reach==set(graph),set(graph)-reach
# Piecewise-linear actual-export barrier at every height event and midpoint.
levels=sorted({float(y)for _,v,ix in ms for y in v[:,1]});heights=sorted(set(levels+[(a+b)/2 for a,b in zip(levels,levels[1:])]))
for yy in heights:
 shapes=[]
 for x0,x1,yz in geoms.values():
  cut=yz.intersection(LineString([(yy,200),(yy,230)]))
  if not cut.is_empty:shapes.append(box(x0,cut.bounds[1],x1,cut.bounds[3]))
 barrier=unary_union(shapes)
 for side,key in [(-1,'D12_directory_07'),(1,'D12_directory_08')]:
  for suffix,z in [('_south',213.85),('_north',218.15)]:
   r=next(r for r in source['solids']if r['name']==key+suffix+'_SourceProfiledTerminal');profile=r['profile_yz'];clamp=min(max(yy,78),79.1);end=float(np.interp(clamp,[p[0]for p in profile],[p[1]for p in profile]));line=LineString([(side*4,z),(side*8.65,z),(side*8.65,end)]);assert line.difference(barrier.buffer(2e-5)).length<2e-5,(yy,key,suffix)
# Measured source-fit residual for all four exported terminal pieces, including lower bevel.
helper=O/'guards.py';exec(compile(ast.Module(body=[n for n in ast.parse(helper.read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='inner_z'],type_ignores=[]),str(helper),'exec'),ns)
interfaces=[]
for name,v,ix in ms:
 if 'SourceProfiledTerminal' not in name:continue
 key=name[:16];neg='_south_' in name;x0,x1,yz=geoms[name];jamb=[r for r in source_ms[key] if r[0]==key+('__portal_jamb-4' if neg else '__portal_jamb4')]
 levels=sorted(set(float(y)for y in v[:,1]));samples=levels+[(a+b)/2 for a,b in zip(levels,levels[1:])];residual=[]
 for yy in samples:
  cut=yz.intersection(LineString([(yy,200),(yy,230)]));zz=cut.bounds[1] if neg else cut.bounds[3]
  for xx in [x0,(x0+x1)/2,x1]:residual.append(zz-ns['inner_z'](jamb,xx,yy,neg))
 assert max(abs(x)for x in residual)<2e-5,(name,max(abs(x)for x in residual))
 interfaces.append({'name':name,'samples':len(residual),'minimum_signed_z_residual_m':min(residual),'maximum_signed_z_residual_m':max(residual),'max_absolute_residual_m':max(abs(x)for x in residual)})
result={'status':'PASS','glb_sha256':hashlib.sha256(raw).hexdigest(),'glb_bytes':len(raw),'mesh_count':116,'triangle_count':sum(r['triangles']for r in rows),'native_export_geometry_normals_uvs':rows,'embedded_images':images,'source_support_clearance':checks,'guard_contact_faces':contacts,'all_exported_parts_floor_connected':True,'max_self_overlap_volume_m3':maxoverlap,'full_height_barrier_samples':len(heights),'export_tolerance_m':2e-5,'runtime_engine_executed':False,'actual_source_terminal_interfaces':interfaces,'maximum_native_export_normal_component_delta':max(r['normal_max_delta']for r in rows),'normal_component_tolerance':1e-4,'normal_tolerance_reason':'Blender exporter recomputes float32 polygon normals on the tiny bevel facets; unit orientation and triangle winding are independently checked'}
(B/'EXPORT_VERIFICATION.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS actual GLB geometry, UV/normals, resources, contact, floor, clearance and full-height guard barrier')
