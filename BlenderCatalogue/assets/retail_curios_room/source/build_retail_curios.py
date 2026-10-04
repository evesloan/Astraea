"""Authored R070 curiosity shop enclosure and coordinated ceiling/frontage."""
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

# A deterministic low-resolution painted enamel carries restrained surface variation.
import random
rng=random.Random(7001);image=bpy.data.images.new('R070_BurntOrangeEnamel',width=128,height=128);pixels=[]
for y in range(128):
 for x in range(128):
  n=rng.uniform(-.016,.016);pixels.extend((.72+n,.31+n*.55,.07+n*.25,1))
image.pixels=pixels;image.pack();m=bpy.data.materials.new('BurntOrangeEnamel');m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Roughness'].default_value=.66;t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=image;t.interpolation='Closest';m.node_tree.links.new(t.outputs['Color'],p.inputs['Base Color']);m['meters_per_tile_uv']=[1,1];mats['orange']=m
m=bpy.data.materials.new('CuriosSmokedGlass');m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.28,.43,.43,.30);p.inputs['Alpha'].default_value=.30;mats['glass']=m
D=json.loads((ROOT/'source/room_contract.json').read_text());outline=D['source_plan_polygon_xy']
def wall(name,a,b,z0,z1,width,role):
 a=Vector(a);b=Vector(b);v=(b-a).normalized();n=Vector((-v.y,v.x))*width/2
 return extrusion(name,[tuple(a+n),tuple(b+n),tuple(b-n),tuple(a-n)],z0,z1,role)
def arc_outline(cx,cy,rx,ry,start,end,n=16):return[(cx+rx*math.cos(start+(end-start)*i/n),cy+ry*math.sin(start+(end-start)*i/n))for i in range(n+1)]
def lathe(name,cx,cy,rings,role,n=16):
 v=[(cx+r*math.cos(2*math.pi*i/n),cy+r*math.sin(2*math.pi*i/n),z)for z,r in rings for i in range(n)];f=[tuple(reversed(range(n))),tuple(range((len(rings)-1)*n,len(rings)*n))]
 for j in range(len(rings)-1):
  for i in range(n):f.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
 return mesh(name,v,f,role)
# Continuous side/rear plan is deliberately tapered and recessed around uses.
for i,(a,b)in enumerate(zip(outline,outline[1:])):
 wall('CUR_Wall_%02d'%i,a,b,0,6.35,.16,'ivory_enamel')
 wall('CUR_Dado_%02d'%i,a,b,.12,.85,.20,'warm_walnut')
 wall('CUR_ShadowBase_%02d'%i,a,b,0,.12,.22,'champagne_metal')
# Recessed front portals: clear central3.6m route; glass display wings flank it.
for side in [-1,1]:
 x0,x1=sorted([side*1.85,side*5.75]);wall('CUR_FrontGlass_'+str(side),(x0,-5.71),(x1,-5.71),.35,3.85,.024,'glass')
 wall('CUR_FrontSill_'+str(side),(x0,-5.71),(x1,-5.71),.18,.35,.14,'warm_stone')
 wall('CUR_FrontHeader_'+str(side),(x0,-5.71),(x1,-5.71),3.85,4.15,.18,'champagne_metal')
 for x in [side*1.85,side*5.75]:wall('CUR_WindowMullion_%s_%s'%(side,x),(x,-5.8),(x,-5.62),.35,4.15,.09,'champagne_metal')
 # Recessed arch profiles spring from sturdy orange side returns.
 wall('CUR_PortalJamb_'+str(side),(side*2.03,-5.88),(side*2.03,-4.32),0,3.85,.28,'orange')
 pts=[]
 for i in range(13):
  a=math.pi*i/12;pts.append((2.04*math.cos(a),-5.05,3.82+1.20*math.sin(a)))
 if side==-1:
  beam('CUR_OrangePortalArch',pts,1.64,.28,'orange')
  beam('CUR_PortalInnerMetal',[(x,y-.76,z-.16)for x,y,z in pts],.055,.045,'champagne_metal')
  beam('CUR_PortalOpal',[(x,y-.68,z-.20)for x,y,z in pts],.042,.028,'lens')
 # Faceted aggregate column widens into a profiled capital.
 cx=side*4.85;cy=-5.14
 lathe('CUR_StreetColumn_'+str(side),cx,cy,[(0,.52),(.15,.56),(.30,.48),(4.9,.48),(5.45,.60),(5.62,.78),(5.78,.78)],'warm_stone')
 lathe('CUR_ColumnCapitalMetal_'+str(side),cx,cy,[(5.61,.80),(5.69,.80)],'champagne_metal')
 lathe('CUR_ColumnCapitalLens_'+str(side),cx,cy,[(5.54,.71),(5.60,.75)],'lens')
 datum('column_light_'+str(side),(cx-side*.73,cy,5.43))
# Ceiling loft coordinates with the floor shoulders; raised inner area uses
# corresponding ring vertices, with lower thresholds and display edges.
inner=[(x*.68,y*.64+.35)for x,y in outline];n=len(outline)
for j in range(n):
 k=(j+1)%n;z0=5.45 if j in [0,n-1] else 6.15
 v=[(*outline[j],z0),(*outline[k],z0),(*inner[k],6.95),(*inner[j],6.95)]
 mesh('CUR_CeilingSoffit_%02d'%j,v+[(x,y,z+.10)for x,y,z in v],[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'ivory_enamel')
 wall('CUR_CeilingCrown_%02d'%j,inner[j],inner[k],6.82,6.95,.16,'warm_walnut')
extrusion('CUR_RaisedCeiling',inner,6.95,7.12,'oatmeal_weave')
# A shallow front canopy and broad side hoods give arrival and displays shelter.
for side in [-1,1]:
 q=[(side*1.85,-5.85),(side*5.75,-5.85),(side*4.75,-4.3),(side*1.85,-4.3)]
 if side<0:q.reverse()
 extrusion('CUR_FrontageCanopy_'+str(side),q,4.12,4.28,'ivory_enamel')
# Display bays sit in the plan's shoulders; furnishings explain their recesses.
for side in [-1,1]:
 for j,cy in enumerate([-2.1,1.0]):
  cx=side*4.72;foot=arc_outline(cx,cy,.56,1.05,0,2*math.pi,16)[:-1]
  extrusion('CUR_DisplayFoot_%s_%d'%(side,j),foot,.05,.20,'warm_stone')
  extrusion('CUR_DisplayBody_%s_%d'%(side,j),[(cx+(x-cx)*.90,cy+(y-cy)*.90)for x,y in foot],.20,.95,'warm_walnut')
  extrusion('CUR_DisplayCap_%s_%d'%(side,j),foot,.95,1.03,'champagne_metal')
  datum('display_%s_%d'%(side,j),(cx,cy,1.035))
# Curved wrapping counter occupies the rear gathering edge; staff access is
# maintained on its left. This is architecture, not a new commerce system.
q=arc_outline(.55,3.50,2.65,.88,math.pi,2*math.pi,20)+arc_outline(.55,3.50,2.00,.24,2*math.pi,math.pi,20)
extrusion('CUR_WrappingCounterBase',q,.05,.95,'orange');extrusion('CUR_WrappingCounterTop',q,.95,1.04,'warm_stone')
datum('service_approach',(.55,2.0,0));datum('staff_approach',(.55,4.3,0))
# Deliberate patterned floor border without owning another collision floor.
for j,(a,b)in enumerate(zip(outline,outline[1:]+outline[:1])):wall('CUR_VisualFloorBorder_%02d'%j,(a[0]*.90,a[1]*.90),(b[0]*.90,b[1]*.90),.012,.019,.11,'orange')
# Paired fitted rear cases give the wrapping counter a legible working backdrop.
for side in [-1,1]:
 cx=side*1.9
 wall('CUR_CaseBack_'+str(side),(cx-.88,5.52),(cx+.88,5.52),.20,3.65,.10,'warm_walnut')
 for dx in [-.90,.90]:wall('CUR_CaseJamb_%s_%s'%(side,dx),(cx+dx,4.79),(cx+dx,5.57),.10,3.10,.095,'champagne_metal')
 pts=[(cx+.90*math.cos(math.pi*i/16),5.18,3.08+.58*math.sin(math.pi*i/16))for i in range(17)]
 beam('CUR_CaseArchedHood_'+str(side),pts,.80,.12,'orange')
 for shelf,h in enumerate([.80,1.58,2.36]):
  extrusion('CUR_CaseShelf_%s_%d'%(side,shelf),[(cx-.86,4.80),(cx+.86,4.80),(cx+.86,5.54),(cx-.86,5.54)],h,h+.065,'warm_stone')
  datum('case_%s_%d'%(side,shelf),(cx,5.11,h+.067))

# Three lamps follow the central browse route; their actual emitters sit below lenses.
for i,(cx,cy,h)in enumerate([(-2.0,.20,6.30),(2.0,.20,6.30),(0,3.1,5.7)]):
 lathe('CUR_PendantStem_'+str(i),cx,cy,[(h+.15,.035),(6.97,.035)],'champagne_metal',8)
 lathe('CUR_PendantShade_'+str(i),cx,cy,[(h,.48),(h+.08,.52),(h+.24,.25)],'ivory_enamel')
 lathe('CUR_PendantLens_'+str(i),cx,cy,[(h-.025,.43),(h,.45)],'lens');datum('ceiling_light_'+str(i),(cx,cy,h-.04))
datum('entry',(0,-5.95,0));datum('browse',(0,0,0));datum('floor_origin',(0,0,0))
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1;bpy.ops.file.pack_all();source=ROOT/'source/AST-RTL-002.blend';export=ROOT/'exports/AST-RTL-002.glb';bpy.ops.wm.save_as_mainfile(filepath=str(source));tri=0
for o in parts:o.data.calc_loop_triangles();tri+=len(o.data.loop_triangles)
bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',export_yup=True,export_extras=True)
record={'catalogue_id':'AST-RTL-002','name':'Kind Curios R070 authored shop enclosure','source':'source/AST-RTL-002.blend','export':'exports/AST-RTL-002.glb','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'export_sha256':hashlib.sha256(export.read_bytes()).hexdigest(),'triangles':tri,'status':'Editable authored draft; integration and visual/clearance review pending'};(ROOT/'AST-RTL-002.manifest.json').write_text(json.dumps(record,indent=2)+'\n');print(record)
