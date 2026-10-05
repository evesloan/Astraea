"""Independent actual Blender/source/imported-glTF proofs for revised005 and new006."""
from pathlib import Path
from collections import Counter
import bpy,bmesh,json,hashlib,math,struct
from mathutils import Vector
R=Path(__file__).resolve().parents[1];C=R.parents[1];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def f32(v):return struct.unpack('<f',struct.pack('<f',v))[0]
def triangles(o,source=False):
 o.data.calc_loop_triangles();uv=o.data.uv_layers.active
 for t in o.data.loop_triangles:
  ps=[]
  for vi,li in zip(t.vertices,t.loops):
   q=o.matrix_world@o.data.vertices[vi].co;u,v=uv.data[li].uv
   if source:v=f32(1-f32(1-v))
   ps.append(tuple(float(x)for x in(*q,u,v)))
  yield(o.data.materials[t.material_index].name,min(tuple(ps[i:]+ps[:i])for i in range(3)))
def mat(m):
 s=m.node_tree.nodes.get('Principled BSDF');d={}
 for k in ['Base Color','Metallic','Roughness','Alpha']:
  v=s.inputs[k].default_value;d[k]=[round(q,6)for q in v]if hasattr(v,'__len__')else round(v,6)
 d['effective_emission_rgb']=[round(q*s.inputs['Emission Strength'].default_value,6)for q in s.inputs['Emission Color'].default_value[:3]]
 d['textures']=sorted([{'sha256':sha_bytes(n.image.packed_file.data),'size':list(n.image.size),'interpolation':n.interpolation}for n in m.node_tree.nodes if n.type=='TEX_IMAGE'and n.image],key=lambda q:q['sha256']);return d
def sha_bytes(b):return hashlib.sha256(b).hexdigest()
reports={}
for family,aid in [('aft_crown_platform','AST-CMD-005'),('upper_horizon_enclosure','AST-CMD-006')]:
 root=C/'assets'/family;src=root/'source'/(aid+'.blend');out=root/'exports'/(aid+'.glb');bpy.ops.wm.open_mainfile(filepath=str(src));P=json.loads((root/'source/geometry_parts.json').read_text())['parts'];actual={o.name:o for o in bpy.context.scene.objects if o.type=='MESH'};assert len(P)==len(actual)
 for p in P:
  o=actual[p['name']];assert len(o.data.vertices)==len(p['vertices_world'])
  for v,e in zip(o.data.vertices,p['vertices_world']):
   q=o.matrix_world@v.co;assert(Vector((q.x,q.z,-q.y))-Vector(e)).length<.000025,(p['name'],q,e)
 S=Counter();uvmax=0;faces=0;actualparts=[]
 for o in actual.values():
  bm=bmesh.new();bm.from_mesh(o.data);assert all(e.is_manifold for e in bm.edges),o.name;assert bm.calc_volume(signed=True)>0,o.name;assert all(f.calc_area()>1e-10 for f in bm.faces),o.name;bm.free();assert o.data.uv_layers
  uv=o.data.uv_layers.active.data;scale=o.data.materials[0]['meters_per_tile_uv']
  for f in o.data.polygons:
   qs=[uv[i].uv for i in f.loop_indices];area=abs(sum(a.x*b.y-a.y*b.x for a,b in zip(qs,qs[1:]+qs[:1])))/2;err=abs(area*scale[0]*scale[1]-f.area)/f.area;uvmax=max(uvmax,err);faces+=1;assert err<.05,(o.name,err)
  S.update(triangles(o,True));o.data.calc_loop_triangles()
  actualparts.append({'name':o.name,'group':o.get('group'),'vertices_world':[[q.x,q.z,-q.y]for v in o.data.vertices for q in[o.matrix_world@v.co]],'triangles':[list(t.vertices)for t in o.data.loop_triangles]})
 markers={o.name:{'location':list(o.location),'props':dict(o.items())}for o in bpy.context.scene.objects if o.type=='EMPTY'};ms={m.name:mat(m)for o in actual.values()for m in o.data.materials}
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 for m in list(bpy.data.materials):bpy.data.materials.remove(m,do_unlink=True)
 bpy.ops.import_scene.gltf(filepath=str(out));E=Counter();sizes=[]
 for o in bpy.context.scene.objects:
  if o.type!='MESH':continue
  E.update(triangles(o));vs=[o.matrix_world@v.co for v in o.data.vertices];size=[max(v[k]for v in vs)-min(v[k]for v in vs)for k in range(3)];sizes.append(size);assert max(size)<16.01,(o.name,size)
 assert S==E,(aid,'oriented triangle/UV/material mismatch',sum((S-E).values()),sum((E-S).values()))
 es={m.name:mat(m)for o in bpy.context.scene.objects if o.type=='MESH'for m in o.data.materials};assert ms==es,(aid,'material mismatch',ms,es)
 em={o.name:o for o in bpy.context.scene.objects if o.type=='EMPTY'}
 for name,marker in markers.items():
  assert name in em and(Vector(marker['location'])-em[name].location).length<.00001,name
  assert all(em[name].get(k)==v for k,v in marker['props'].items()),name
 rep={'pass':True,'catalogue_id':aid,'source_sha256':sha(src),'export_sha256':sha(out),'source_part_count':len(actual),'triangles':sum(S.values()),'runtime_mesh_batches':len(sizes),'source_closed_outward':True,'exact_float32_oriented_position_triangle_uv_material_equality':True,'uv_rule':'OnlysourceV float32(1-float32(1-v)); models unmodified','material_parameters_and_packed_texture_bytes_equal':True,'materials':ms,'all_markers_and_properties_equal':True,'marker_count':len(markers),'metric_uv_faces':faces,'maximum_uv_area_relative_error':uvmax,'runtime_max_blender_dimensions':[max(s[k]for s in sizes)for k in range(3)]};reports[aid]=rep
 (R/'qa'/('actual_'+aid+'_triangles.json')).write_text(json.dumps({'source_sha256':sha(src),'parts':actualparts},separators=(',',':'))+'\n')
 print('ROUNDTRIP_PASS',aid,len(actual),sum(S.values()),len(sizes),uvmax)
(R/'qa/source_export_validation.json').write_text(json.dumps(reports,indent=2)+'\n')
