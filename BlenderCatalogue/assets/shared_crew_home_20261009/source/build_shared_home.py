from pathlib import Path
import bpy,bmesh,json,hashlib
from mathutils import Vector
R=Path(__file__).resolve().parents[1];C=R.parents[1];D=json.loads((R/'source/SHARED_HOME.json').read_text())
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
materials={};defs=json.loads((C/'materials/staff/manifest.json').read_text())['materials']
def mat(role):
 if role in materials:return materials[role]
 row=defs[role];m=bpy.data.materials.new(role);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=row['roughness'];bs.inputs['Metallic'].default_value=row['metallic'];tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(C/'materials/staff'/row['file']),check_existing=True);tex.image.pack();m.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color']);materials[role]=m;return m
def gv(x,y,z):return (x,-z,y)
for p in D['parts']:
 verts=[];faces=[];lo,hi=p['y']
 for tri in p['triangles']:
  k=len(verts);verts.extend([gv(x,lo,z) for x,z in tri]+[gv(x,hi,z) for x,z in tri]);faces.extend([(k+2,k+1,k),(k+3,k+4,k+5)])
 for ring in [p['boundary']]+p['holes']:
  for a,b in zip(ring,ring[1:]+ring[:1]):
   k=len(verts);verts.extend([gv(a[0],lo,a[1]),gv(b[0],lo,b[1]),gv(b[0],hi,b[1]),gv(a[0],hi,a[1])]);faces.append((k,k+1,k+2,k+3))
 me=bpy.data.meshes.new(p['name']);me.from_pydata(verts,[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=.000001);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free();o=bpy.data.objects.new(p['name'],me);bpy.context.collection.objects.link(o);me.materials.append(mat(p['role']));o['source_role']=p['role'];o['construction_wip']=True
 uv=me.uv_layers.new(name='MetreScaled')
 for poly in me.polygons:
  n=poly.normal;axis=max(range(3),key=lambda a:abs(n[a]));axes=[a for a in range(3) if a!=axis]
  for li in poly.loop_indices:
   v=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]],v[axes[1]])
for i,pos in enumerate(D['fixtures']):
 o=bpy.data.objects.new('LightDatum'+str(i),None);o.location=gv(*pos);bpy.context.collection.objects.link(o)
bpy.ops.wm.save_as_mainfile(filepath=str(R/'source/SharedCrewHome.blend'))
bpy.ops.export_scene.gltf(filepath=str(R/'exports/SharedCrewHome.next.glb'),export_format='GLB',export_extras=True,export_yup=True)
(R/'exports/SharedCrewHome.next.glb').replace(R/'exports/SharedCrewHome.glb')
b=(R/'exports/SharedCrewHome.glb').read_bytes();(R/'qa/BUILD.json').write_text(json.dumps({'status':'source_export_completed','parts':len(D['parts']),'glb_sha256':hashlib.sha256(b).hexdigest(),'native_source':'source/SharedCrewHome.blend','runtime_acceptance':False},indent=2)+'\n')
