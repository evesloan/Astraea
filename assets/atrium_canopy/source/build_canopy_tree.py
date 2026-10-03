"""Original forked conservatory tree; editable branches and individual leaf sprays."""
from pathlib import Path
import bpy,bmesh,math,json,hashlib,random
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];CAT=ROOT.parents[1];rng=random.Random(73191)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
mats={}
for role in ['bark','leaf_jade','leaf_olive','leaf_sage']:
 m=bpy.data.materials.new('Canopy_'+role);m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Roughness'].default_value=.9
 t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(CAT/'materials/botanical'/('botanical_'+role+'.png')));t.interpolation='Closest';m.node_tree.links.new(t.outputs['Color'],b.inputs['Base Color']);mats[role]=m
parts=[]
def mesh(name,v,f,role,uvs=None):
 d=bpy.data.meshes.new(name);d.from_pydata(v,[],f);d.update();o=bpy.data.objects.new(name,d);bpy.context.collection.objects.link(o);d.materials.append(mats[role]);parts.append(o);uv=d.uv_layers.new(name='AuthoredLeafOrBark')
 for p in d.polygons:
  for li in p.loop_indices:
   vi=d.loops[li].vertex_index;q=d.vertices[vi].co;uv.data[li].uv=uvs[vi] if uvs else (q.x*.4,q.z*.4)
 return o
def branch(name,points,radii):
 v=[];n=8;ps=[Vector(p) for p in points]
 for i,p in enumerate(ps):
  tangent=(ps[min(i+1,len(ps)-1)]-ps[max(0,i-1)]).normalized();u=tangent.cross(Vector((0,1,0))).normalized();w=tangent.cross(u).normalized()
  for j in range(n):v.append(tuple(p+radii[i]*(u*math.cos(j*2*math.pi/n)+w*math.sin(j*2*math.pi/n))))
 f=[tuple(reversed(range(n))),tuple(range((len(ps)-1)*n,len(ps)*n))]+[(i*n+j,i*n+(j+1)%n,(i+1)*n+(j+1)%n,(i+1)*n+j) for i in range(len(ps)-1) for j in range(n)]
 o=mesh(name,v,f,'bark');bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
branch('TREE_FlutedTrunk',[(0,0,0),(.35,-.15,1.6),(.25,.15,4),(-.45,.1,6.6),(-.15,0,9.2)],[.95,.66,.50,.4,.24])
for i in range(7):
 a=i*2*math.pi/7;branch('TREE_Root_'+str(i),[(0,0,.8),(1.1*math.cos(a),1.1*math.sin(a),.25),(2.2*math.cos(a+.13),2.2*math.sin(a+.13),.03)],[.28,.16,.015])
ends=[]
for i in range(9):
 a=i*2*math.pi/9+.35;base=5.5+(i%3)*1.0;reach=4.1+(i%3)*.6;height=12.7+(i%4)*.85
 points=[(-.3,0,base),(.8*math.cos(a),.8*math.sin(a),base+1.8),(2.3*math.cos(a+.12),2.3*math.sin(a+.12),height-2),(reach*math.cos(a+.16),reach*math.sin(a+.16),height)]
 branch('TREE_MainLimb_'+str(i),points,[.30,.22,.12,.045]);end=Vector(points[-1])
 for j in range(5):
  theta=a+(j-2)*.45;start=Vector(points[2]).lerp(end,.25+j*.14);dest=start+Vector((math.cos(theta)*2.1,math.sin(theta)*2.1,1.1+(j%2)*.5));middle=start.lerp(dest,.5)+Vector((0,0,.35));branch(f'TREE_Twig_{i}_{j}',[start,middle,dest],[.065,.035,.009]);ends.append((dest,theta))
for k,(center,a) in enumerate(ends):
 v=[];f=[];uv=[]
 for j in range(30):
  t=j*2.399963;radius=math.sqrt((j+.5)/30)*1.9;pos=center+Vector((math.cos(t)*radius,math.sin(t)*radius,.45*math.sin(t*1.3)-radius*.15));direction=Vector((math.cos(t+.3),math.sin(t+.3),rng.uniform(-.2,.4))).normalized();side=direction.cross(Vector((0,0,1))).normalized();length=rng.uniform(.55,.95);width=length*.36
  points=[pos-direction*length*.5,pos-side*width,pos+Vector((0,0,.09)),pos+side*width,pos+direction*length*.55]
  o=len(v);v.extend(tuple(x) for x in points);uv.extend([(0,.5),(.48,0),(.5,.5),(.48,1),(1,.5)])
  for tri in [(0,1,2),(0,2,3),(1,4,2),(2,4,3)]:f.append(tuple(o+x for x in tri));f.append(tuple(o+x for x in reversed(tri)))
 mesh('TREE_LeafSpray_'+str(k),v,f,['leaf_jade','leaf_olive','leaf_sage'][k%3],uv)
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1;bpy.ops.file.pack_all();blend=ROOT/'source/AST-BOT-011.blend';bpy.ops.wm.save_as_mainfile(filepath=str(blend))
tri=0
for o in parts:o.data.calc_loop_triangles();tri+=len(o.data.loop_triangles)
# Compact exported drawing by material while keeping individual authored source parts.
for role,m in mats.items():
 bpy.ops.object.select_all(action='DESELECT');objects=[o for o in list(bpy.context.scene.objects) if o.type=='MESH' and o.data.materials[0]==m]
 for o in objects:o.select_set(True)
 bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();bpy.context.object.name='TREE_'+role
bpy.ops.object.select_all(action='SELECT');glb=ROOT/'exports/AST-BOT-011.glb';bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',export_yup=True,export_extras=True)
(ROOT/'AST-BOT-011.manifest.json').write_text(json.dumps({'catalogue_id':'AST-BOT-011','name':'Forked conservatory canopy tree','source':'source/AST-BOT-011.blend','export':'exports/AST-BOT-011.glb','triangles':tri,'leaf_count':len(ends)*30,'status':'Draft; silhouette, lighting and runtime review pending','source_sha256':hashlib.sha256(blend.read_bytes()).hexdigest(),'export_sha256':hashlib.sha256(glb.read_bytes()).hexdigest()},indent=2)+'\n');print('CANOPY_TREE_CREATED',tri)
