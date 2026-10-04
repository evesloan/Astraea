"""Original Vesper dining backdrop, crosswise stair and fitted local lift architecture."""
from pathlib import Path
import bpy,bmesh,math,json,hashlib
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];CAT=ROOT.parents[1]
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
mats={};parts=[];material_contract=json.loads((CAT/'materials/material_manifest.json').read_text())['materials']
for role in ['ivory_enamel','warm_walnut','warm_stone','champagne_metal','teal_weave','botanical_soil','oatmeal_weave','clay_weave']:
 m=bpy.data.materials.new(role);m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Roughness'].default_value=material_contract.get(role,{}).get('roughness',.82);b.inputs['Metallic'].default_value=material_contract.get(role,{}).get('metallic',0);m['meters_per_tile_uv']=material_contract.get(role,{}).get('meters_per_tile_uv',[1,1])
 path=CAT/'materials'/('botanical/'+role+'.png' if role.startswith('botanical') else role+'.png')
 t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(path));t.interpolation='Closest';m.node_tree.links.new(t.outputs['Color'],b.inputs['Base Color']);mats[role]=m
m=bpy.data.materials.new('GardenOpalLens');m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(1,.95,.84,1);b.inputs['Emission Color'].default_value=(1,.91,.75,1);b.inputs['Emission Strength'].default_value=.7;mats['lens']=m

def mesh(name,vertices,faces,role):
 d=bpy.data.meshes.new(name);d.from_pydata(vertices,[],faces);d.update();bm=bmesh.new();bm.from_mesh(d);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-7);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(d);bm.free();o=bpy.data.objects.new(name,d);bpy.context.collection.objects.link(o);d.materials.append(mats[role]);parts.append(o);uv=d.uv_layers.new(name='MetreScaled')
 for p in d.polygons:
  n=p.normal.normalized();u=(Vector((1,0,0))-n*n.x).normalized() if abs(n.z)>.7 else Vector((-n.y,n.x,0)).normalized();v=n.cross(u).normalized();scale=mats[role].get('meters_per_tile_uv',[1,1])
  for li in p.loop_indices:
   q=d.vertices[d.loops[li].vertex_index].co
   uv.data[li].uv=(q.dot(u)/scale[0],q.dot(v)/scale[1])
 return o

def extrusion(name,outline,bottom,top,role):
 n=len(outline);v=[(x,y,z)for z in [bottom,top]for x,y in outline];f=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n)for i in range(n)];return mesh(name,v,f,role)

def beam(name,points,width,depth,role):
 v=[]
 for i,p in enumerate(points):
  p=Vector(p);t=(Vector(points[min(i+1,len(points)-1)])-Vector(points[max(0,i-1)])).normalized();side=Vector((0,1,0)) if abs(t.y)<.95 else Vector((1,0,0));side=(side-t*t.dot(side)).normalized();up=t.cross(side).normalized()
  for w,h in [(-width/2,-depth/2),(width/2,-depth/2),(width/2,depth/2),(-width/2,depth/2)]:v.append(tuple(p+side*w+up*h))
 f=[(3,2,1,0),tuple(range(len(v)-4,len(v)))]+[(i*4+j,i*4+(j+1)%4,(i+1)*4+(j+1)%4,(i+1)*4+j)for i in range(len(points)-1)for j in range(4)];return mesh(name,v,f,role)

def datum(name,p):
 o=bpy.data.objects.new('DATUM_'+name,None);bpy.context.collection.objects.link(o);o.location=p



# North-edge modules: shaped wall, acoustic field and ceiling return in one family.
def xyz(x,y,z):return(x,-z,y)
def panel(name,x0,x1,y0,y1,z0,z1,role):
 v=[xyz(x,y,z)for z in [z0,z1]for x,y in [(x0,y0),(x1,y0),(x1,y1),(x0,y1)]]
 return mesh(name,v,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],role)
for aid,H in [('AST-DIN-005',2.9),('AST-DIN-005_lower',3.22)]:
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);parts=[]
 # Continuous solid back keeps the retained dining volume enclosed at its real boundary.
 panel('DIN_BackdropSolid',0,5.4,0,H,.02,.12,'ivory_enamel')
 panel('DIN_StoneSkirting',0,5.4,0,.16,.12,.25,'warm_stone')
 panel('DIN_WalnutDado',0,5.4,.16,.79,.12,.20,'warm_walnut')
 panel('DIN_AcousticField',.35,5.05,.83,H-.28,.12,.165,'teal_weave')
 # Profiled end returns splay toward the ceiling and become a continuous cornice.
 for index,x in enumerate([.16,5.24]):
  profile=[(.12,.16),(.25,.16),(.22,.82),(.19,H-.52),(.33,H-.19),(.33,H),(.12,H)]
  v=[xyz(x+dx,y,z)for dx in [-.16,.16]for z,y in profile];n=len(profile)
  mesh('DIN_SplayedReturn_'+str(index),v,[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n)for i in range(n)],'ivory_enamel')
 panel('DIN_UpperWalnutFrieze',.32,5.08,H-.28,H-.14,.12,.22,'warm_walnut')
 panel('DIN_UpperStoneReturn',0,5.4,H-.14,H,.12,.33,'ivory_enamel')
 # Broad acoustic ribs, deliberately economical rather than ornament subdivisions.
 for i in range(9):
  x=.62+i*.52
  panel('DIN_AcousticRib_'+str(i),x-.028,x+.028,.88,H-.34,.165,.205,'warm_walnut')
 for x in [.34,5.06]:panel('DIN_ChampagneJunction_'+str(x),x-.015,x+.015,.80,H-.27,.16,.23,'champagne_metal')
 # Small physically supported wall-wash source beneath the cornice.
 panel('DIN_WashHousing',2.44,2.96,H-.20,H-.14,.24,.43,'champagne_metal')
 panel('DIN_WashLens',2.48,2.92,H-.212,H-.20,.27,.40,'lens')
 datum('wash_source',(2.7,-.45,H-.23))
 datum('wall_receiver',(2.7,-.215,1.40))
 scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1;bpy.ops.file.pack_all()
 source=ROOT/'source'/(aid+'.blend');export=ROOT/'exports'/(aid+'.glb');bpy.ops.wm.save_as_mainfile(filepath=str(source))
 for o in parts:o.data.calc_loop_triangles()
 triangles=sum(len(o.data.loop_triangles) for o in parts)
 bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',export_yup=True,export_extras=True)
 record={'catalogue_id':aid,'name':'Vesper splayed acoustic dining wall and ceiling return','source':'source/'+aid+'.blend','export':'exports/'+aid+'.glb','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'export_sha256':hashlib.sha256(export.read_bytes()).hexdigest(),'triangles':triangles,'status':'Editable fitted north-edge architecture; runtime support, guest routes and visual review pending'}
 (ROOT/(aid+'.manifest.json')).write_text(json.dumps(record,indent=2)+'\n');print(record)
