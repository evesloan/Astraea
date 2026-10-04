"""Original Vesper glass watercourse and contained cascade receiver."""
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


D=json.loads((ROOT/'source/watercourse_contract.json').read_text());AID='AST-AQU-015';pts=[Vector((x-21.5,-z+207,0))for x,z in D['path_xz']];heights=[y-61 for y in D['floor_surface_y']]
m=bpy.data.materials.new('WatercourseGlass');m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(.23,.39,.42,.3);b.inputs['Alpha'].default_value=.3;mats['glass']=m
normals=[]
for i,p in enumerate(pts):
 t=(pts[min(i+1,len(pts)-1)]-pts[max(0,i-1)]).normalized();normals.append(Vector((-t.y,t.x,0)))
def ribbon(name,width,bottom,top,role,offset=0,limit=None):
 count=len(pts)if limit is None else limit;v=[]
 for h in [bottom,top]:
  for i in range(count):
   for side in [-1,1]:
    q=pts[i]+normals[i]*(offset+side*width/2);v.append((q.x,q.y,h[i]))
 n=count*2;f=[]
 for i in range(count-1):
  k=i*2;f.extend([(k,k+2,k+3,k+1),(n+k,n+k+1,n+k+3,n+k+2),(k,n+k,n+k+2,k+2),(k+1,k+3,n+k+3,n+k+1)])
 f.extend([(0,1,n+1,n),(n-2,2*n-2,2*n-1,n-1)]);return mesh(name,v,f,role)
# Continuous supported cabinet keeps the low under-trough space non-walkable.
ribbon('WAT_SculptedSupportCabinet',.50,[.02]*6,[h-.075 for h in heights],'warm_walnut',limit=5)
ribbon('WAT_StoneChannelFloor',.81,[h-.06 for h in heights],heights,'warm_stone')
for sign in [-1,1]:
 ribbon('WAT_GlassBank_'+str(sign),.035,heights,[h+.30 for h in heights],'glass',sign*.37)
 ribbon('WAT_BankRim_'+str(sign),.055,[h+.28 for h in heights],[h+.315 for h in heights],'champagne_metal',sign*.37)
 ribbon('WAT_LowerReveal_'+str(sign),.055,[h-.055 for h in heights],[h-.015 for h in heights],'ivory_enamel',sign*.377)
# Source-side end is closed; the terminal remains a real spill mouth.
q=pts[0];n=normals[0];v=[]
for h in [heights[0],heights[0]+.30]:
 for side in [-1,1]:
  a=q+n*side*.39;v.append((a.x,a.y,h))
mesh('WAT_SourceEndGlass',v,[(0,1,3,2)],'glass')
def flow(name,rows):
 v=[];distance=0;uv=[]
 for i,(center,normal,width)in enumerate(rows):
  if i:distance+=(center-rows[i-1][0]).length
  for side in [-1,1]:v.append(tuple(center+normal*side*width/2));uv.append(((side+1)/2,distance))
 o=mesh(name,v,[(2*i,2*i+1,2*i+3,2*i+2)for i in range(len(rows)-1)],'glass')
 for face in o.data.polygons:
  for li in face.loop_indices:o.data.uv_layers.active.data[li].uv=uv[o.data.loops[li].vertex_index]
 return o
flow('WAT_visual_trough',[(pts[i]+Vector((0,0,heights[i]+.12)),normals[i],.65)for i in range(len(pts))])
rows=[]
for i in range(25):
 t=i/24;rows.append((Vector((3.5+.12*math.sin(math.pi*t),-8,1.36-18.5*t)),Vector((0,1,0)),.65+.15*t))
flow('WAT_visual_fall',rows)
def lathe(name,cx,cy,profile,role,n=24):
 v=[(cx+r*math.cos(2*math.pi*i/n),cy+r*math.sin(2*math.pi*i/n),h)for r,h in profile for i in range(n)];f=[tuple(reversed(range(n))),tuple(range((len(profile)-1)*n,len(profile)*n))]+[(j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i)for j in range(len(profile)-1)for i in range(n)];return mesh(name,v,f,role)
# Sculpted return/support spine and closed receiver stand on the retained basin floor.
lathe('WAT_ConcealedReturnSpine',3.95,-8,[(.15,-18.2),(.15,-17.0),(.12,-15),(.12,.8),(.15,1.40)],'ivory_enamel',12)
beam('WAT_OutletBearing',[(3.5,-8,1.13),(3.95,-8,1.13),(3.95,-8,1.38)],.14,.14,'champagne_metal')
lathe('WAT_ReceiverBody',3.5,-8,[(.70,-18.2),(.85,-18.05),(1.25,-17.25),(1.40,-16.9),(1.18,-16.9),(.67,-17.45)],'warm_stone')
# A contained shallow return pool, with an actual intake grille visible beneath it.
q=[(3.5+1.12*math.cos(2*math.pi*i/32),-8+1.12*math.sin(2*math.pi*i/32))for i in range(32)];extrusion('WAT_visual_receiver',q,-17.145,-17.14,'glass')
for i in range(7):
 x=2.65+i*.12;beam('WAT_ReturnGrille_'+str(i),[(x,-8.55,-17.18),(x,-8.25,-17.18)],.035,.045,'champagne_metal')
for i,(x,y,h)in enumerate([(0,0,heights[0]-.10),(0,-6.7,heights[3]-.10),(2.2,-8,-16.86)]):
 q=[(x+.065*math.cos(2*math.pi*j/12),y+.065*math.sin(2*math.pi*j/12))for j in range(12)];extrusion('WAT_FixtureBody_'+str(i),q,h+.015,h+.07,'champagne_metal');extrusion('WAT_FixtureLens_'+str(i),q,h,h+.015,'lens');datum('light_'+str(i),(x,y,h-.02))
for i in range(5):datum('supported_base_'+str(i),(pts[i].x,pts[i].y,0))
datum('spillway_guard_crossing',(23.2347-21.5,-8,62.2707-61));datum('receiver_floor',(3.5,-8,-18.2));datum('outlet',(3.5,-8,1.36))
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1;bpy.ops.file.pack_all();source=ROOT/'source'/(AID+'.blend');export=ROOT/'exports'/(AID+'.glb');bpy.ops.wm.save_as_mainfile(filepath=str(source));tri=0
for o in parts:o.data.calc_loop_triangles();tri+=len(o.data.loop_triangles)
bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',export_yup=True,export_extras=True)
record={'catalogue_id':AID,'name':'Vesper supported watercourse and contained cascade','source':'source/'+AID+'.blend','export':'exports/'+AID+'.glb','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'export_sha256':hashlib.sha256(export.read_bytes()).hexdigest(),'triangles':tri,'status':'Editable fitted feature; runtime support, guard clearance, appearance and operational systems pending'};(ROOT/(AID+'.manifest.json')).write_text(json.dumps(record,indent=2)+'\n');print(record)
