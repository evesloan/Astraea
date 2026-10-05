"""Editable chined lower-body shell; upper guest facades remain open for window design."""
from pathlib import Path
import bpy,bmesh,json,hashlib
from mathutils import Vector
R=Path(__file__).resolve().parents[1];C=R.parents[1];AID='AST-HUL-001'
assert all(a['catalogue_id']!=AID or a['family']=='lower_hull_body'for a in json.loads((C/'catalogue_manifest.json').read_text())['assets'])
D=json.loads((R/'source/body_contract.json').read_text());bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
materials={}
for role,file in [('body','staff/staff_bluegrey_paint.png'),('keel','staff/staff_zinc.png')]:
 m=bpy.data.materials.new('hull_'+role);m.use_nodes=True;n=m.node_tree.nodes.get('Principled BSDF');n.inputs['Roughness'].default_value=.82
 t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(C/'materials'/file));t.interpolation='Closest';m.node_tree.links.new(t.outputs['Color'],n.inputs['Base Color']);materials[role]=m
parts=[]
def mesh(name,verts,faces,role):
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);me.materials.append(materials[role]);uv=me.uv_layers.new(name='MetreScaled')
 for f in me.polygons:
  n=f.normal.normalized();u=(Vector((1,0,0))-n*n.x).normalized()if abs(n.z)>.7 else Vector((-n.y,n.x,0)).normalized();v=n.cross(u)
  for k in f.loop_indices:
   q=me.vertices[me.loops[k].vertex_index].co;uv.data[k].uv=(q.dot(u),q.dot(v))
 parts.append(o)
for j,(lo,hi)in enumerate(zip(D['rings'],D['rings'][1:])):
 n=len(lo['outer']);verts=[]
 for ring,key in [(lo,'outer'),(hi,'outer'),(lo,'inner'),(hi,'inner')]:verts +=[(x,-z,ring['y'])for x,z in ring[key]]
 faces=[]
 for i in range(n):
  k=(i+1)%n;faces.extend([(i,k,n+k,n+i),(2*n+k,2*n+i,3*n+i,3*n+k),(n+i,n+k,3*n+k,3*n+i),(k,i,2*n+i,2*n+k)])
 mesh('HUL_LowerBand_%02d'%j,verts,faces,'body')
lo=D['rings'][0];n=len(lo['inner']);verts=[(x,-z,y)for y in [lo['y'],D['keel_top_y']]for x,z in lo['inner']];faces=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n)for i in range(n)];mesh('HUL_KeelPan',verts,faces,'keel')
for name,location in [('keel',(0,0,-3.5)),('D01',(0,0,0)),('D04_rim',(0,0,16.5))]:
 o=bpy.data.objects.new('DATUM_'+name,None);bpy.context.collection.objects.link(o);o.location=location
bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1;bpy.ops.file.pack_all();src=R/'source'/(AID+'.blend');out=R/'exports'/(AID+'.glb');bpy.ops.wm.save_as_mainfile(filepath=str(src));bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',export_yup=True,export_extras=True)
tri=sum(len(p.vertices)-2 for o in parts for p in o.data.polygons)
manifest={'catalogue_id':AID,'name':'Chined lower structural hull body and keel pan','source':'source/'+AID+'.blend','export':'exports/'+AID+'.glb','triangles':tri,'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'export_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'status':'Structural platform source; fit, runtime, apertures and visual acceptance pending','scope':D['scope']}
(R/(AID+'.manifest.json')).write_text(json.dumps(manifest,indent=2)+'\n');print(AID,tri)
