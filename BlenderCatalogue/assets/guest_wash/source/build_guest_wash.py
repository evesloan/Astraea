"""Original D06 garden overlook: sheltered back, rising roof and open court-facing edge."""
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

for role,color,rough,metal in [('porcelain',(.88,.90,.89,1),.25,0),('mirror',(.56,.66,.68,1),.16,.95),('bath_glass',(.38,.58,.59,.26),.23,0)]:
 m=bpy.data.materials.new('Bath_'+role);m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=color;b.inputs['Roughness'].default_value=rough;b.inputs['Metallic'].default_value=metal
 if role=='bath_glass':b.inputs['Alpha'].default_value=.26
 mats[role]=m

def ellipse(cx,cy,rx,ry,n=24):return [(cx+rx*math.cos(i*math.tau/n),cy+ry*math.sin(i*math.tau/n))for i in range(n)]
def bowl(name,profiles,cx,cy,role):
 n=24;v=[(cx+rx*math.cos(i*math.tau/n),cy+ry*math.sin(i*math.tau/n),z)for z,rx,ry in profiles for i in range(n)]
 f=[(k*n+i,k*n+(i+1)%n,(k+1)*n+(i+1)%n,(k+1)*n+i)for k in range(len(profiles)-1)for i in range(n)]+[tuple(reversed(range(n))),tuple(range((len(profiles)-1)*n,len(profiles)*n))]
 return mesh(name,v,f,role)
def tube(name,points,r,role):
 v=[]
 for i,p in enumerate(points):
  p=Vector(p);t=(Vector(points[min(i+1,len(points)-1)])-Vector(points[max(i-1,0)])).normalized();u=Vector((0,1,0)) if abs(t.y)<.95 else Vector((1,0,0));u=(u-t*t.dot(u)).normalized();w=t.cross(u)
  v.extend(tuple(p+r*(u*math.cos(j*math.tau/8)+w*math.sin(j*math.tau/8)))for j in range(8))
 f=[tuple(reversed(range(8))),tuple(range(len(v)-8,len(v)))]+[(k*8+j,k*8+(j+1)%8,(k+1)*8+(j+1)%8,(k+1)*8+j)for k in range(len(points)-1)for j in range(8)]
 return mesh(name,v,f,role)
def finish(aid,name):
 bpy.context.view_layer.update();bpy.ops.file.pack_all();source=ROOT/'source'/(aid+'.blend');export=ROOT/'exports'/(aid+'.glb');bpy.ops.wm.save_as_mainfile(filepath=str(source));tri=0
 for o in parts:o.data.calc_loop_triangles();tri+=len(o.data.loop_triangles)
 parents=[]
 for o in parts:
  if o.parent not in parents:parents.append(o.parent)
 for parent in parents:
  for role,material in mats.items():
   selected=[o for o in list(bpy.context.scene.objects)if o.type=='MESH' and o.parent==parent and o.data.materials and o.data.materials[0]==material]
   if not selected:continue
   bpy.ops.object.select_all(action='DESELECT')
   for o in selected:o.select_set(True)
   bpy.context.view_layer.objects.active=selected[0];bpy.ops.object.join();bpy.context.object.name=aid+'_'+('moving_' if parent else 'fixed_')+role
 bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',export_yup=True,export_extras=True)
 (ROOT/(aid+'.manifest.json')).write_text(json.dumps({'catalogue_id':aid,'name':name,'source':'source/'+aid+'.blend','export':'exports/'+aid+'.glb','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'export_sha256':hashlib.sha256(export.read_bytes()).hexdigest(),'triangles':tri,'status':'Original dry-suite fixture; no water, plumbing simulation, species-fit or final-art acceptance'},indent=2)+'\n')
 print('WASH_FIXTURE_AUTHORED',aid,tri)

def reset():
 global parts
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);parts=[]
reset()
# Vanity axis +X projects from its host wall; the bowl has an actual open rim.
extrusion('VAN_WallCabinet',[(.02,-.54),(.43,-.54),(.53,-.40),(.53,.40),(.43,.54),(.02,.54)],.34,.68,'warm_walnut')
bowl('VAN_RimAndBowl',[(.66,.065,.09),(.76,.21,.42),(.82,.26,.53),(.86,.26,.53),(.86,.18,.38),(.76,.14,.30),(.685,.045,.07)],.29,0,'porcelain')
# Separate non-overlapping small deck behind the bowl for the real tap base.
extrusion('VAN_TapDeck',[(.015,-.53),(.075,-.53),(.075,.53),(.015,.53)],.80,.84,'warm_stone')
tube('VAN_ArchedTap',[(.065,0,.84),(.065,0,1.02),(.12,0,1.07),(.25,0,1.07),(.30,0,1.02)],.018,'champagne_metal')
extrusion('VAN_Control',[(.055,.17),(.11,.17),(.11,.24),(.055,.24)],.84,.93,'champagne_metal')
# Mirror surface is intentionally ordinary reflective material, not a fake live feed.
mesh('VAN_Mirror',[(.026,-.48,1.14),(.026,.48,1.14),(.026,.48,2.10),(.026,-.48,2.10)],[(0,1,2,3)],'mirror')
for y in [-.52,.52]:tube('VAN_MirrorJamb_'+str(y),[(.035,y,1.10),(.035,y,2.14)],.025,'warm_walnut')
for z in [1.10,2.14]:tube('VAN_MirrorRail_'+str(z),[(.035,-.52,z),(.035,.52,z)],.025,'warm_walnut')
datum('water_origin',(.30,0,1.015));datum('drain',(.29,0,.685));datum('standing',(.95,0,0));finish('AST-SAN-001','Wall-hung guest vanity with open basin')
reset()
bowl('WC_SculptedBowl',[(0,.17,.21),(.10,.19,.24),(.28,.25,.31),(.425,.30,.37),(.455,.30,.37),(.455,.22,.28),(.34,.17,.23),(.19,.055,.08)],0,0,'porcelain')
extrusion('WC_Tank',ellipse(0,-.49,.255,.115,16),.28,.87,'porcelain')
extrusion('WC_TankCap',ellipse(0,-.49,.266,.123,16),.87,.90,'porcelain')
# A discrete lid hinge is preserved for future interaction; runtime starts closed.
hinge=bpy.data.objects.new('HINGE_LID',None);bpy.context.collection.objects.link(hinge);hinge.location=(0,-.32,.465)
lid=extrusion('WC_Lid',ellipse(0,.32,.30,.34),.015,.055,'ivory_enamel');lid.parent=hinge
extrusion('WC_FlushPad',ellipse(.12,-.49,.045,.028,12),.90,.908,'champagne_metal')
datum('flush',(.12,-.49,.925));datum('standing',(0,.95,0));finish('AST-SAN-002','Compact guest toilet with sculpted bowl and lid hinge')
reset()
# Front tray bevel is a walkable slope rather than a raised step.
outer=[(-.62,-.725),(.62,-.725),(.62,.725),(-.62,.725)];inner=[(-.57,-.675),(.57,-.675),(.57,.675),(-.57,.675)]
v=[(x,y,z)for poly,z in [(outer,0),(inner,.020)]for x,y in poly]
mesh('SHW_SlopedTray',v,[(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)],'warm_stone')
extrusion('SHW_Drain',ellipse(0,0,.07,.07,16),.020,.022,'champagne_metal')
extrusion('SHW_SideGlass',[(-.613,-.70),(-.597,-.70),(-.597,.70),(-.613,.70)],.025,1.96,'bath_glass')
for y in [-.70,.70]:tube('SHW_GlassPost_'+str(y),[(-.605,y,.025),(-.605,y,1.98)],.018,'champagne_metal')
tube('SHW_Riser',[(0,-.67,.8),(0,-.67,2.03),(0,-.60,2.10),(0,-.39,2.10)],.018,'champagne_metal')
extrusion('SHW_RainHead',ellipse(0,-.39,.11,.11,16),2.075,2.12,'champagne_metal')
extrusion('SHW_Valve',ellipse(0,-.655,.07,.04,12),1.05,1.14,'champagne_metal')
datum('water_origin',(0,-.39,2.06));datum('valve',(0,-.59,1.1));datum('standing',(0,.15,.02));finish('AST-SAN-003','Low-threshold shower tray and framed side screen')
