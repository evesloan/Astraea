"""Original local retail/dining exchange court inside verified D09/D10 allocations."""
from pathlib import Path
import bpy,bmesh,math,json,hashlib
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];CAT=ROOT.parents[1]
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
mats={};parts=[];material_contract=json.loads((CAT/'materials/material_manifest.json').read_text())['materials']
for role in ['ivory_enamel','warm_walnut','warm_stone','champagne_metal','teal_weave','botanical_soil','oatmeal_weave','clay_weave','retail_terracotta_enamel','staff_white_paint','staff_floor']:
 m=bpy.data.materials.new(role);m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Roughness'].default_value=material_contract.get(role,{}).get('roughness',.82);b.inputs['Metallic'].default_value=material_contract.get(role,{}).get('metallic',0);m['meters_per_tile_uv']=material_contract.get(role,{}).get('meters_per_tile_uv',[1,1])
 path=CAT/'materials'/(('botanical/'if role.startswith('botanical') else 'retail/'if role.startswith('retail') else 'staff/'if role.startswith('staff') else '')+role+'.png')
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



m=bpy.data.materials.new('ExchangeGlazing');m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(.23,.42,.44,.28);b.inputs['Alpha'].default_value=.28;mats['glass']=m
AID='AST-RTL-009';D=json.loads((ROOT/'source/section_contract.json').read_text());F=52.5
assert all(a['catalogue_id']!=AID or a['family']=='orchard_exchange'for a in json.loads((CAT/'catalogue_manifest.json').read_text())['assets'])
def xyz(x,y,z):return(x-4,-(z+250),y-F)
def slab(name,x0,x1,z0,z1,lo,hi,role):return extrusion(name,[(x0-4,-z0-250),(x1-4,-z0-250),(x1-4,-z1-250),(x0-4,-z1-250)],lo-F,hi-F,role)
def wall(name,a,b,lo,hi,width,role):
 ax,az=a;bx,bz=b;dx=bx-ax;dz=bz-az;length=math.hypot(dx,dz);nx=-dz/length*width/2;nz=dx/length*width/2
 v=[xyz(x+sign*nx,y,z+sign*nz)for sign in [-1,1]for x,y,z in [(ax,lo,az),(bx,lo,bz),(bx,hi,bz),(ax,hi,az)]]
 return mesh(name,v,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],role)
# Opaque neighbouring-volume boundaries; no invented hull or space windows.
for level in [52.5,61]:
 slab('EX_NorthDado_'+str(level),4,24,-250,-249.78,level,level+.78,'warm_walnut')
 slab('EX_NorthWall_'+str(level),4,24,-250,-249.84,level+.78,(60.3 if level<61 else 69.1),'ivory_enamel')
 for x in [7,16,21]:
  slab('EX_NorthRecess_'+str(level)+'_'+str(x),x-.7,x+.7,-249.76,-249.70,level+1.1,level+3.1,'retail_terracotta_enamel')
# East side ends at an actual upper food-hall approach; lower shop enclosure retained.
slab('EX_EastLowerWall',23.84,24,-250,-236,52.5,61,'ivory_enamel')
slab('EX_EastUpperDado',23.84,24,-250,-235.75,61,62.1,'ivory_enamel')
slab('EX_UpperDiningGlass',23.90,23.94,-249.9,-235.8,62.1,64.6,'glass')
slab('EX_EastUpperTransom',23.84,24,-250,-235.75,64.6,69.1,'ivory_enamel')
for z in [-249.9,-246.4,-242.9,-239.4,-235.8]:slab('EX_DiningWindowMullion_'+str(z),23.82,24.06,z-.06,z+.06,62.05,64.65,'warm_walnut')
slab('EX_UpperPortalHeader',23.76,24.08,-235.75,-233,65.1,69.1,'retail_terracotta_enamel')
slab('EX_NorthJoint',4,24,-250,-249.72,60.3,61,'warm_stone')
# Profiled upper edge around the real switchback opening, with supported guards.
for i,(a,b)in enumerate([((7.8,-248.2),(14.2,-248.2)),((7.8,-248.2),(7.8,-237.5)),((14.2,-248.2),(14.2,-237.5))]):
 wall('EX_GalleryFascia_'+str(i),a,b,60.40,60.76,.23,'warm_stone')
 wall('EX_GalleryGuardBase_'+str(i),a,b,61,61.2,.14,'ivory_enamel')
 wall('EX_GalleryGlass_'+str(i),a,b,61.2,62.10,.024,'glass')
 wall('EX_GalleryHandrail_'+str(i),a,b,62.10,62.18,.17,'warm_walnut')
# Fitted local lift enclosure: sides/back, relieved entrance and source floor/roof.
x0,x1=19.62,23.62;z0,z1=-243.66,-239.34
slab('EX_LiftBack',x1-.16,x1,z0,z1,52.26,64.35,'ivory_enamel')
for z in [z0,z1-.12]:slab('EX_LiftSide_'+str(z),x0,x1,z,z+.12,52.26,64.35,'ivory_enamel')
for level in [52.5,61]:
 for a,b in [(z0,-242.75),(-240.25,z1)]:slab('EX_LiftJamb_'+str(level)+str(a),x0,x0+.16,a,b,level,level+3.2,'retail_terracotta_enamel')
 slab('EX_LiftHeader_'+str(level),x0,x0+.16,-242.75,-240.25,level+2.64,level+3.2,'retail_terracotta_enamel')
slab('EX_LiftFrontBetween',x0,x0+.16,z0,z1,55.7,61,'ivory_enamel')
slab('EX_LiftPit',x0,x1,z0,z1,52.26,52.30,'warm_stone')
slab('EX_LiftCap',x0,x1,z0,z1,64.23,64.35,'warm_stone')
# The high room closes below protected D11. Layered perimeter soffits make the
# central vertical route legible without closing it with an intermediate lid.
slab('EX_HighRoof',4,24,-250,-233,69.1,69.24,'ivory_enamel')
slab('EX_WestSoffit',4,7.5,-246.9,-233,67.9,69.1,'ivory_enamel')
slab('EX_NorthSoffit',7.5,21,-250,-248.6,68.15,69.1,'warm_walnut')
# Ground-floor and upper resting ledges face the exchange, out of lift staging.
for level in [52.5,61]:
 slab('EX_RestBase_'+str(level),22.65,23.70,-246.5,-244.6,level,level+.40,'warm_walnut')
 slab('EX_RestCushion_'+str(level),22.69,23.65,-246.4,-244.7,level+.40,level+.49,'clay_weave')
 slab('EX_RestBack_'+str(level),23.58,23.73,-246.5,-244.6,level+.49,level+1.10,'oatmeal_weave')
 datum('seat_'+str(int(level)),xyz(23.05,level+.49,-245.55))
# Visible local sources at actual landings and resting destinations.
for i,(x,y,z)in enumerate([(6,55.7,-236),(16,55.7,-246.6),(6,64.3,-236),(16,64.3,-246.6),(21.5,65,-235.7)]):
 slab('EX_LampMount_'+str(i),x-.035,x+.035,z-.035,z+.035,y,(60.76 if y<61 else 69.1),'champagne_metal')
 slab('EX_LampHousing_'+str(i),x-.4,x+.4,z-.28,z+.28,y-.13,y,'warm_walnut')
 slab('EX_LampLens_'+str(i),x-.34,x+.34,z-.22,z+.22,y-.15,y-.13,'lens')
 datum('light_'+str(i),xyz(x,y-.18,z))
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1;bpy.ops.file.pack_all();source=ROOT/'source'/(AID+'.blend');export=ROOT/'exports'/(AID+'.glb');bpy.ops.wm.save_as_mainfile(filepath=str(source));bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',export_yup=True,export_extras=True)
record={'catalogue_id':AID,'name':'Orchard exchange court, profiled gallery and fitted local lift enclosure','source':'source/'+AID+'.blend','export':'exports/'+AID+'.glb','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'export_sha256':hashlib.sha256(export.read_bytes()).hexdigest(),'status':'Original connected section architecture under construction; runtime and art checks pending'}
(ROOT/(AID+'.manifest.json')).write_text(json.dumps(record,indent=2)+'\n');print(record)
