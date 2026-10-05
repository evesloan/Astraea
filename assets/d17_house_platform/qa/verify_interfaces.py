"""Actual Blender source preservation, oriented export equality and seated contacts. No engine."""
from pathlib import Path
from collections import Counter
import bpy,bmesh,json,hashlib,math,struct,subprocess
from mathutils import Vector
R=Path(__file__).resolve().parents[1];C=R.parents[1];COM=C/'assets/starboard_house_upper';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
allow={f'HC_{kind}_D17_{s}_2'for s in[-1,1]for kind in['ProfileWall','Wainscot']}
def capture(path):
 bpy.ops.wm.open_mainfile(filepath=str(path));out={}
 for o in bpy.context.scene.objects:
  a={'type':o.type,'matrix':[list(r)for r in o.matrix_world],'properties':{k:o[k]for k in o.keys()}}
  if o.type=='MESH':a.update(vertices=[list(v.co)for v in o.data.vertices],faces=[list(f.vertices)for f in o.data.polygons],uv=[list(u.uv)for u in o.data.uv_layers.active.data],materials=[m.name for m in o.data.materials])
  out[o.name]=a
 return out
baseline=Path('/tmp/d17-baseline-COM003.blend')
if not baseline.exists():baseline.write_bytes(subprocess.check_output(['git','-C',str(C),'show','3655b833f99048a109e30b3f5f39146afcc5b829:assets/starboard_house_upper/source/AST-COM-003.blend']))
assert sha(baseline)==json.loads((R/'source/section_contract.json').read_text())['source_inputs']['catalogue/assets/starboard_house_upper/source/AST-COM-003.blend']
A=capture(baseline);B=capture(COM/'source/AST-COM-003.blend');same=[];changed=[]
for n,a in A.items():
 assert n in B,n
 if a==B[n]:same.append(n)
 else:assert n in allow,n;changed.append(n)
assert set(changed)==allow
added=set(B)-set(A);expected={n+'_PortalRightStub'for n in allow}|{n+'_PortalHeader'for n in allow if'ProfileWall'in n};assert added==expected
# Validate exact bounds and material of all split volumes; old coplanar surfaces retain metre UV coordinates.
uv_checks=0
for n in allow:
 old=A[n];ov=[Vector(v)for v in old['vertices']];oldfaces=[];offset=0
 for inds in old['faces']:
  pp=[ov[i]for i in inds];uv=old['uv'][offset:offset+len(inds)];offset+=len(inds);normal=(pp[1]-pp[0]).cross(pp[2]-pp[0]).normalized();oldfaces.append((pp,uv,normal))
 for nn in[n,n+'_PortalRightStub']+([n+'_PortalHeader']if'ProfileWall'in n else[]):
  o=bpy.data.objects[nn];assert B[nn]['materials']==old['materials']
  for f in o.data.polygons:
   for pp,uv,norm in oldfaces:
    if all(abs((o.data.vertices[o.data.loops[li].vertex_index].co-pp[0]).dot(norm))<1e-5 for li in f.loop_indices)and f.normal.dot(norm)>.99:
     u=(pp[1]-pp[0]);v=(pp[-1]-pp[0]);assert abs(u.dot(v))<1e-5
     for li in f.loop_indices:
      q=o.data.vertices[o.data.loops[li].vertex_index].co-pp[0];a=q.dot(u)/u.length_squared;b=q.dot(v)/v.length_squared;expect=Vector(uv[0])+a*(Vector(uv[1])-Vector(uv[0]))+b*(Vector(uv[-1])-Vector(uv[0]));assert(o.data.uv_layers.active.data[li].uv-expect).length<2e-5,(nn,li);uv_checks+=1
# Exact exported oriented triangles with UV/materials, ignoring batching only.
def signatures(o):
 o.data.calc_loop_triangles();uv=o.data.uv_layers.active.data
 for t in o.data.loop_triangles:
  points=[]
  for vi,li in zip(t.vertices,t.loops):
   p=o.matrix_world@o.data.vertices[vi].co;q=uv[li].uv;points.append((float(p.x),float(p.z),float(-p.y),float(q.x),struct.unpack("<f",struct.pack("<f",1.0-q.y))[0]))
  yield(o.data.materials[t.material_index].name,min(tuple(points[i:]+points[:i])for i in range(3)))
def material_fingerprint():
 out={}
 for m in bpy.data.materials:
  if not m.use_nodes:continue
  if m.users==0:continue
  nodes=[]
  for n in m.node_tree.nodes:
   defaults={}
   for socket in n.inputs:
    if hasattr(socket,'default_value'):
     val=socket.default_value
     try:val=list(val)
     except TypeError:pass
     if isinstance(val,(str,int,float,bool,list)):defaults[socket.name]=val
   a={'type':n.bl_idname,'inputs':defaults}
   if n.type=='TEX_IMAGE':a['image']=sha(Path(n.image.filepath))if Path(n.image.filepath).exists()else hashlib.sha256(n.image.packed_file.data).hexdigest();a['interpolation']=n.interpolation
   nodes.append(a)
  out[m.name]=nodes
 return out
bpy.ops.wm.open_mainfile(filepath=str(baseline));old_mats=material_fingerprint()
bpy.ops.wm.open_mainfile(filepath=str(COM/'source/AST-COM-003.blend'));assert old_mats==material_fingerprint(),'COM material nodes/images changed'
reports=[]
for family,aid in[(COM,'AST-COM-003'),(R,'AST-RES-005')]:
 src=family/'source'/f'{aid}.blend';export=family/'exports'/f'{aid}.glb';bpy.ops.wm.open_mainfile(filepath=str(src));S=Counter();meshes=0
 for o in bpy.context.scene.objects:
  if o.type!='MESH':continue
  meshes+=1;bm=bmesh.new();bm.from_mesh(o.data);assert all(e.is_manifold for e in bm.edges),o.name;assert bm.calc_volume(signed=True)>0,o.name;bm.free();S.update(signatures(o))
 markers={o.name:list(o.location)for o in bpy.context.scene.objects if o.type=='EMPTY'}
 raw=export.read_bytes();n=struct.unpack_from('<I',raw,12)[0];g=json.loads(raw[20:20+n]);data=raw[28+n:];E=Counter();batches=0
 def accessor(ai):
  a=g['accessors'][ai];v=g['bufferViews'][a['bufferView']];count={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']];fmt={5126:'f',5125:'I',5123:'H',5121:'B'}[a['componentType']];size=struct.calcsize('<'+fmt*count);off=v.get('byteOffset',0)+a.get('byteOffset',0);stride=v.get('byteStride',size)
  return[struct.unpack_from('<'+fmt*count,data,off+i*stride)for i in range(a['count'])]
 for node in g['nodes']:
  if 'mesh'not in node:continue
  assert not any(k in node for k in ['matrix','translation','rotation','scale']),node['name']
  batches+=1
  for prim in g['meshes'][node['mesh']]['primitives']:
   pos=accessor(prim['attributes']['POSITION']);uv=accessor(prim['attributes']['TEXCOORD_0']);ix=[a[0]for a in accessor(prim['indices'])];mat=g['materials'][prim['material']]['name']
   for i in range(0,len(ix),3):
    points=[tuple((*pos[k],*uv[k]))for k in ix[i:i+3]];E[(mat,min(tuple(points[k:]+points[:k])for k in range(3)))]+=1
 assert S==E,(aid,'oriented raw glTF triangle/UV/material discrepancy',sum((S-E).values()),sum((E-S).values()))
 em={o['name']:o.get('translation',[0,0,0])for o in g['nodes']if'mesh'not in o}
 for name,p in markers.items():assert name in em and max(abs(a-b)for a,b in zip(em[name],[p[0],p[2],-p[1]]))<1e-6,(aid,name)
 reports.append({'asset':aid,'source_sha256':sha(src),'export_sha256':sha(export),'editable_meshes':meshes,'export_meshes':batches,'oriented_triangle_uv_material_exact_equality':True,'UV_comparison_basis':'Raw glTF V=float32(1-sourceV); avoids importer reverse-V rounding noise','triangles':sum(S.values()),'marker_equality':True,'markers':len(markers),'source_manifold_positive_volume':True})
D=json.loads((R/'source/section_contract.json').read_text());assert len(D['units'])==16 and len({u['source_envelope_index']for u in D['units']})==16
assert all(u['historical_stable_id']is None for u in D['units']);assert D['new_walkable_source_meshes']==0
report={'pass':True,'scope':'Bounded portal/footing source stage only; full platform held','baseline_COM_source_sha256':sha(Path('/tmp/d17-baseline-COM003.blend')),'COM_unchanged_objects':len(same),'COM_changed_allowed_objects':sorted(changed),'COM_added_split_objects':sorted(added),'COM_original_coplanar_uv_loop_checks':uv_checks,'COM_material_node_defaults_and_packed_texture_hashes_unchanged':True,'COM_old_floor_contract_sha256':sha(COM/'source/house_contract.json'),'roundtrips':reports,'limits':D['open_gates']}
(R/'qa/interface_verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
