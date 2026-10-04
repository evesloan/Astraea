"""Original compact custodial cart and loose cleaner bottle; editable metric parts."""
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
 d=bpy.data.meshes.new(name);d.from_pydata(vertices,[],faces);d.update();bm=bmesh.new();bm.from_mesh(d);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(d);bm.free();o=bpy.data.objects.new(name,d);bpy.context.collection.objects.link(o);d.materials.append(mats[role]);parts.append(o);uv=d.uv_layers.new(name='MetreScaled')
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
  p=Vector(p);t=(Vector(points[min(i+1,len(points)-1)])-Vector(points[max(0,i-1)])).normalized();side=Vector((0,1,0));up=t.cross(side).normalized()
  for w,h in [(-width/2,-depth/2),(width/2,-depth/2),(width/2,depth/2),(-width/2,depth/2)]:v.append(tuple(p+side*w+up*h))
 f=[(3,2,1,0),tuple(range(len(v)-4,len(v)))]+[(i*4+j,i*4+(j+1)%4,(i+1)*4+(j+1)%4,(i+1)*4+j)for i in range(len(points)-1)for j in range(4)];return mesh(name,v,f,role)

def datum(name,p):
 o=bpy.data.objects.new('DATUM_'+name,None);bpy.context.collection.objects.link(o);o.location=p

staff_materials=json.loads((CAT/'materials/staff/manifest.json').read_text())['materials']
for role in ['staff_bluegrey_paint','staff_white_paint','staff_zinc','staff_rubber']:
 m=bpy.data.materials.new(role);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=staff_materials[role]['roughness'];bs.inputs['Metallic'].default_value=staff_materials[role]['metallic'];m['meters_per_tile_uv']=staff_materials[role]['meters_per_tile_uv']
 tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(CAT/'materials/staff'/(role+'.png')));tex.interpolation='Closest';m.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color']);mats[role]=m

def tube(name,path,radius,role,n=12):
 verts=[]
 for i,p in enumerate(path):
  p=Vector(p);t=(Vector(path[min(i+1,len(path)-1)])-Vector(path[max(0,i-1)])).normalized();ref=Vector((0,0,1))if abs(t.z)<.9 else Vector((1,0,0));u=t.cross(ref).normalized();v=t.cross(u).normalized()
  for j in range(n):a=2*math.pi*j/n;verts.append(tuple(p+radius*(u*math.cos(a)+v*math.sin(a))))
 faces=[tuple(reversed(range(n))),tuple(range(len(verts)-n,len(verts)))]+[(i*n+j,i*n+(j+1)%n,(i+1)*n+(j+1)%n,(i+1)*n+j)for i in range(len(path)-1)for j in range(n)]
 return mesh(name,verts,faces,role)
def lathe(name,rings,role,n=16):
 v=[(r*math.cos(2*math.pi*i/n),r*math.sin(2*math.pi*i/n),z)for z,r in rings for i in range(n)]
 f=[tuple(reversed(range(n))),tuple(range(len(v)-n,len(v)))]+[(j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i)for j in range(len(rings)-1)for i in range(n)]
 return mesh(name,v,f,role)
def save(aid,name,parents,details):
 source=ROOT/'source'/(aid+'.blend');export=ROOT/'exports'/(aid+'.glb');bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1;bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(source));tri=0
 for o in parts:o.data.calc_loop_triangles();tri+=len(o.data.loop_triangles)
 for parent in [None]+parents:
  for role,material in mats.items():
   selected=[o for o in list(bpy.context.scene.objects)if o.type=='MESH'and o.parent==parent and o.data.materials and o.data.materials[0]==material]
   if not selected:continue
   bpy.ops.object.select_all(action='DESELECT')
   for o in selected:o.select_set(True)
   bpy.context.view_layer.objects.active=selected[0];bpy.ops.object.join();bpy.context.object.name=aid+'_'+role+('_wheel'if parent else '')
 bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',export_yup=True,export_extras=True)
 m={'catalogue_id':aid,'name':name,'source':'source/'+aid+'.blend','export':'exports/'+aid+'.glb','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'export_sha256':hashlib.sha256(export.read_bytes()).hexdigest(),'triangles':tri,'status':'Authored source; physics and visual validation pending'};m.update(details);(ROOT/(aid+'.manifest.json')).write_text(json.dumps(m,indent=2)+'\n')
# Two open shelves have real floors and raised lips rather than solid tubs.
outline=[(-.30,-.55),(.30,-.55),(.37,-.48),(.37,.48),(.30,.55),(-.30,.55),(-.37,.48),(-.37,-.48)]
inner=[(-.29,-.51),(.29,-.51),(.33,-.47),(.33,.47),(.29,.51),(-.29,.51),(-.33,.47),(-.33,-.47)]
for i,z in enumerate([.26,.88]):
 extrusion('CART_TrayFloor_'+str(i),outline,z,z+.04,'staff_bluegrey_paint')
 for j in range(8):
  k=(j+1)%8;extrusion('CART_RaisedRim_%d_%d'%(i,j),[outline[j],outline[k],inner[k],inner[j]],z+.04,z+.13,'staff_white_paint')
for x in [-.32,.32]:
 for y in [-.45,.45]:tube('CART_Frame_%s_%s'%(x,y),[(x,y,.18),(x,y,.93)],.027,'staff_zinc')
 tube('CART_BackHandleUpright_'+str(x),[(x,-.45,.77),(x,-.46,.92),(x,-.57,1.055),(x,-.67,1.08)],.028,'staff_zinc')
tube('CART_HandGrip',[(-.36,-.67,1.08),(.36,-.67,1.08)],.034,'staff_rubber')
extrusion('CART_ServiceBack',[(-.29,-.48),(.29,-.48),(.29,-.45),(-.29,-.45)],.34,.80,'staff_bluegrey_paint')
extrusion('CART_SmallIdentityPlate',[(-.17,-.493),(.17,-.493),(.17,-.482),(-.17,-.482)],.52,.66,'staff_white_paint')
wheel_parents=[]
for i,(x,y)in enumerate([(-.32,-.43),(.32,-.43),(-.32,.43),(.32,.43)]):
 root=bpy.data.objects.new('WHEEL_ROLL_'+str(i),None);bpy.context.collection.objects.link(root);root.location=(x,y,.09);wheel_parents.append(root)
 o=tube('CART_Tyre_'+str(i),[(-.029,0,0),(.029,0,0)],.09,'staff_rubber',16);o.parent=root
 o=tube('CART_Hub_'+str(i),[(-.034,0,0),(.034,0,0)],.047,'staff_zinc',12);o.parent=root
 tube('CART_CasterFork_'+str(i),[(x-.035,y,.10),(x-.035,y,.20),(x,y,.23),(x+.035,y,.20),(x+.035,y,.10)],.014,'staff_zinc',8)
datum('handle',(0,-.67,1.08));datum('upper_tray',(0,0,.92));datum('lower_tray',(0,0,.30))
boxes=[{'name':'chassis','center':[0,.24,0],'size':[.70,.08,1.06]},{'name':'upper_floor','center':[0,.90,0],'size':[.72,.04,1.06]},{'name':'lower_floor','center':[0,.28,0],'size':[.72,.04,1.06]},{'name':'service_back','center':[0,.57,.47],'size':[.58,.46,.04]},{'name':'handle','center':[0,1.08,.67],'size':[.74,.068,.068]}]
for z in [.26,.88]:
 for side in [-1,1]:
  boxes.append({'name':'side_rim','center':[side*.35,z+.085,0],'size':[.04,.09,1.0]});boxes.append({'name':'end_rim','center':[0,z+.085,side*.53],'size':[.62,.09,.04]})
for x in [-.32,.32]:
 for z in [-.45,.45]:boxes.append({'name':'corner_frame','center':[x,.56,z],'size':[.054,.74,.054]})
 for z in [.58]:boxes.append({'name':'handle_upright','center':[x,.97,z],'size':[.058,.24,.20]})
coll={'frame':'Godot local XYZ metres','boxes':boxes,'wheel_contacts':[{'center':[x,.09,-y],'radius':.09}for x,y in [(-.32,-.43),(.32,-.43),(-.32,.43),(.32,.43)]],'scope':'Compound chassis with simplified caster contacts; visual wheels are not separately jointed rigid bodies'}
(ROOT/'collision_proposals.json').write_text(json.dumps(coll,indent=2)+'\n')
save('AST-HSK-005','Compact two-tier custodial cleaning cart',wheel_parents,{'handle_source_m':[0,-.67,1.08],'upper_tray_source_m':[0,0,.92],'collision_proposals':'collision_proposals.json'})
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);parts=[]
lathe('PRODUCT_BottleBody',[(0,.045),(.01,.056),(.16,.056),(.205,.040),(.225,.022)],'staff_white_paint')
lathe('PRODUCT_LabelBand',[(.045,.0565),(.14,.0565)],'teal_weave')
lathe('PRODUCT_ScrewCap',[(.218,.026),(.242,.026),(.249,.023)],'staff_bluegrey_paint',12)
datum('grip',(0,0,.13))
save('AST-HSK-006','Loose capped cleaning-product bottle',[],{'collision':'Cylinder radius0.057m height0.25m,centreGodotY0.125','scope':'Product identity/chemistry and consumption deferred'})
