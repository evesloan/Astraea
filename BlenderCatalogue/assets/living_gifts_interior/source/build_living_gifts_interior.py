"""Living Gifts: recessed nursery frontage, branching browse floor and screened wrapping/stock work bay."""
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


D=json.loads((ROOT/'source/room_contract.json').read_text());AID='AST-RTL-006'
m=bpy.data.materials.new('FloristTerracottaEnamel');m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Roughness'].default_value=.76;t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(CAT/'materials/retail/retail_terracotta_enamel.png'));t.interpolation='Closest';m.node_tree.links.new(t.outputs['Color'],b.inputs['Base Color']);m['meters_per_tile_uv']=[1,1];mats['orange']=m
m=bpy.data.materials.new('LivingGiftsGlass');m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(.23,.39,.42,.28);b.inputs['Alpha'].default_value=.28;mats['glass']=m
def xyz(x,y,z):return(x-46,230.4-z,y-52.5)
def wall(name,a,b,lo,hi,width,role):
 a=Vector((a[0]-46,230.4-a[1]));b=Vector((b[0]-46,230.4-b[1]));t=(b-a).normalized();n=Vector((-t.y,t.x))*width/2
 return extrusion(name,[tuple(a+n),tuple(b+n),tuple(b-n),tuple(a-n)],lo-52.5,hi-52.5,role)
def slab(name,poly,lo,hi,role):return extrusion(name,[(x-46,230.4-z)for x,z in poly],lo-52.5,hi-52.5,role)
outline=[(46.2,232.7),(47,231),(49.2,230.6),(52.6,230.6),(53.65,231.4),(53.65,242.3),(47.2,242.3),(46.3,240.8),(46.4,239.1),(47.2,238.1),(46.8,236),(47.2,234.1)]
# The roof follows the offset nursery and entrance rather than spanning an unaltered rectangular lid.
slab('RTL_ShapedRoof',outline,56.6,56.8,'ivory_enamel')
solid=[[(46.2,232.7),(47,231),(49.2,230.6),(52.6,230.6),(53.65,231.4),(53.65,242.3)],[(47.2,242.3),(51.4,242.3)],[(53.4,242.3),(53.65,242.3)]]
for group,path in enumerate(solid):
 for i,(a,b)in enumerate(zip(path,path[1:])):
  wall('RTL_Wall_%s_%s'%(group,i),a,b,52.5,56.6,.16,'ivory_enamel');wall('RTL_WallPlinth_%s_%s'%(group,i),a,b,52.5,53.2,.19,'warm_walnut')
# Transparent nursery/flower fronts are true interfaces into this same shop.
for group,path in enumerate([[(46.2,232.7),(47.2,234.1)],[(47.2,238.1),(46.4,239.1),(46.3,240.8),(47.2,242.3)]]):
 for i,(a,b)in enumerate(zip(path,path[1:])):
  wall('RTL_WindowBase_%s_%s'%(group,i),a,b,52.5,53.05,.20,'ivory_enamel');wall('RTL_WindowGlass_%s_%s'%(group,i),a,b,53.05,55.7,.035,'glass');wall('RTL_RecessOrange_%s_%s'%(group,i),a,b,55.7,56.6,.24,'orange')
# Deep rising portal spans a clear four-metre opening, wholly within the reserved bay.
for z in [234.1,238.1]:wall('RTL_PortalJamb_'+str(z),(46.9,z),(47.5,z),52.5,55.45,.22,'ivory_enamel')
portal=[(234.1,55.35),(234.25,55.7),(234.6,56.0),(235.2,56.22),(236,56.3),(236.8,56.22),(237.4,56.0),(237.75,55.7),(238.1,55.35)]
for i,((za,ha),(zb,hb))in enumerate(zip(portal,portal[1:])):
 v=[xyz(x,y,z)for x in [46.9,47.5]for z,y in [(za,ha),(zb,hb),(zb,56.6),(za,56.6)]];mesh('RTL_PortalSweep_'+str(i),v,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'orange')
 beam('RTL_PortalFineEdge_'+str(i),[xyz(46.88,ha,za),xyz(46.88,hb,zb)],.08,.075,'champagne_metal')
# Stock is screened behind the wrapping area; the east service throat stays straight and clear.
wall('RTL_StockScreen',(51.18,239),(51.18,242.1),52.5,55.4,.16,'warm_walnut')
slab('RTL_WorkBaySoffit',[(48,238.5),(51.1,238.5),(51.1,242.1),(48,242.1)],55.45,55.62,'ivory_enamel')
slab('RTL_NurseryCanopy',[(46.7,232.2),(47.4,231.3),(50.0,231.3),(50.0,233.8),(48,234.1),(47.2,234.0)],56.0,56.18,'ivory_enamel')
# A real two-metre rear service opening; no leaf projects into the aft circulation.
for x in [51.32,53.48]:wall('RTL_ServiceJamb_'+str(x),(x,242.1),(x,242.4),52.5,55.1,.16,'warm_walnut')
wall('RTL_ServiceHeader',(51.4,242.3),(53.4,242.3),55.1,56.6,.18,'warm_walnut')
# Fitted nursery vessels supply actual soil surfaces for separate catalogue plants.
for i,(x,z,r,h)in enumerate([(48.3,232.4,.68,.40),(47.1,240,.38,.55),(47.1,241.15,.38,.85),(47.25,233.1,.25,.65)]):
 cx,cy=x-46,230.4-z;q=[(cx+r*math.cos(j*math.pi/8),cy+r*math.sin(j*math.pi/8))for j in range(16)];extrusion('RTL_PlanterVessel_'+str(i),q,0,h-.08,'warm_stone');
 vv=[(cx+(a-cx)*scale,cy+(b-cy)*scale,yy)for yy in [h-.08,h]for scale in [1,.82]for a,b in q];ff=[]
 for j in range(16):
  k=(j+1)%16;ff.extend([(j,k,k+32,j+32),(j+16,j+48,k+48,k+16),(j+32,k+32,k+48,j+48),(j,k,k+16,j+16)])
 mesh('RTL_PlanterRim_'+str(i),vv,ff,'warm_stone');extrusion('RTL_PlanterSoil_'+str(i),[(cx+(a-cx)*.82,cy+(b-cy)*.82)for a,b in q],h-.08,h-.03,'botanical_soil');datum('flora_'+str(i),xyz(x,52.5+h-.035,z))
datum('display_bay',xyz(53.0,52.5,232.7));datum('wrapping_workbench',xyz(48.9,52.5,239.6));datum('guest_entry',xyz(47.2,52.5,236));datum('service_entry',xyz(52.4,52.5,242.3));datum('interior_turn',xyz(50.8,52.5,235.7))
# Floor finish is visual-only, preserving the original structural floor and holes.
q=[xyz(50+(x-50)*.965,52.504,236.3+(z-236.3)*.965)for x,z in outline];o=mesh('RTL_Finish_Inlay',q,[tuple(range(len(q)))],'warm_stone');bm=bmesh.new();bm.from_mesh(o.data);bm.normal_update();down=[f for f in bm.faces if f.normal.z<0]
if down:bmesh.ops.reverse_faces(bm,faces=down)
bm.to_mesh(o.data);bm.free()
for i,(x,z,h)in enumerate([(48.3,232.4,55.75),(50.8,235.7,56.35),(48.9,240.3,55.20),(47.2,236,56.05)]):
 cx,cy=x-46,230.4-z;q=[(cx+.20*math.cos(j*math.pi/8),cy+.20*math.sin(j*math.pi/8))for j in range(16)];extrusion('RTL_SourceHousing_'+str(i),q,h-52.5,h-52.5+.20,'champagne_metal');extrusion('RTL_SourceLens_'+str(i),[(cx+(a-cx)*.87,cy+(b-cy)*.87)for a,b in q],h-52.5-.025,h-52.5,'lens');datum('light_'+str(i),xyz(x,h-.07,z))
 mount=[56.0,56.6,55.45,56.3][i];beam('RTL_SourceMount_'+str(i),[xyz(x,h+.20,z),xyz(x,mount,z)],.07,.07,'champagne_metal')
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1;bpy.ops.file.pack_all();source=ROOT/'source'/(AID+'.blend');export=ROOT/'exports'/(AID+'.glb');bpy.ops.wm.save_as_mainfile(filepath=str(source));tri=0
for o in parts:o.data.calc_loop_triangles();tri+=len(o.data.loop_triangles);o['finish_only']=o.name.startswith('RTL_Finish')
for finish in [False,True]:
 for role,m in mats.items():
  selected=[o for o in list(scene.objects)if o.type=='MESH'and o.get('finish_only')==finish and o.data.materials and o.data.materials[0]==m]
  if not selected:continue
  bpy.ops.object.select_all(action='DESELECT')
  for o in selected:o.select_set(True)
  bpy.context.view_layer.objects.active=selected[0];bpy.ops.object.join();bpy.context.object.name=('RTL_finish_'if finish else'RTL_static_')+role
bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',export_yup=True,export_extras=True)
record={'catalogue_id':AID,'name':'Living Gifts recessed nursery and wrapping interior','source':'source/'+AID+'.blend','export':'exports/'+AID+'.glb','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'export_sha256':hashlib.sha256(export.read_bytes()).hexdigest(),'triangles':tri,'status':'Editable partial florist interior; actual routes, support, optical and art review pending'};(ROOT/(AID+'.manifest.json')).write_text(json.dumps(record,indent=2)+'\n');print(record)
