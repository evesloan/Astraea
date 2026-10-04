"""Authored two-level starboard commons within existing D13/D14 programmes."""
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

D=json.loads((ROOT/'source/architecture_contract.json').read_text());contract=D['contract']
# Source anchor maps to ship(63,84,0): localY = -shipZ, localZ=shipY-84.
def xy(p):return(p[0]-63,-p[1])
def segment(name,a,b,z0,z1,width,role):
 a=Vector(a);b=Vector(b);v=(b-a).normalized();n=Vector((-v.y,v.x))*width/2
 return extrusion(name,[tuple(a+n),tuple(b+n),tuple(b-n),tuple(a-n)],z0,z1,role)
def wall_segment(name,a,b,z0,z1,width,role):return segment(name,xy(a),xy(b),z0,z1,width,role)
# Profiled structural piers extend from D12; their ceiling penetrations are
# coordinated in the garden source, never hidden behind opaque overlaps.
for i,(x,z)in enumerate(contract['support_intent']['commons_piers_xz_m']+[contract['support_intent']['offset_arrival_pier_xz_m']]):
 cx,cy=xy((x,z));half=.32;ch=.075
 q=[(cx-half+ch,cy-half),(cx+half-ch,cy-half),(cx+half,cy-half+ch),(cx+half,cy+half-ch),(cx+half-ch,cy+half),(cx-half+ch,cy+half),(cx-half,cy+half-ch),(cx-half,cy-half+ch)]
 extrusion('SC_ProfiledPier_'+str(i),q,-6,8.16,'warm_stone')
 for h in [-5.9,-.3,4.2,7.9]:
  outline=[(cx+(a-cx)*1.05,cy+(b-cy)*1.05)for a,b in q]
  extrusion('SC_PierBand_%d_%s'%(i,h),outline,h,h+.07,'champagne_metal')
wall_segment('SC_OffsetArrivalTransferArm',(60,-17),(60,-11.8),3.66,4.26,.56,'warm_stone')
# Connected arrival soffits carry their actual light sources; no floating lamps.
for label,points,height in [('lower',contract['lower_arrival_centerline_xz_m'],3.83),('upper',contract['upper_arrival_centerline_xz_m'],7.94)]:
 for j,(a,b)in enumerate(zip(points,points[1:])):
  wall_segment('SC_ArrivalCanopy_%s_%d'%(label,j),a,b,height,height+.14,3.8,'oatmeal_weave')
  wall_segment('SC_ArrivalCeilingSpine_%s_%d'%(label,j),a,b,height-.055,height,.18,'warm_walnut')
# North and south wall profiles remain within actual programme; the north
# lower entrance is the residential branch, intentionally offset from atrium.
for level,h in enumerate([0,4.5]):
 for side in [-1,1]:
  points=[(63,side*14),(72,side*14),(78,side*13.2),(82,side*13.2),(86,side*14),(93,side*14),(97,side*10)]
  for j,(a,b)in enumerate(zip(points,points[1:])):
   # True lower residential entrance X82..86 at Z-14.
   if level==0 and side==-1 and j==3:continue
   wall_segment('SC_ProfileWall_%d_%d_%d'%(level,side,j),a,b,h,h+(4.15 if level==0 else 3.5),.16,'ivory_enamel')
   wall_segment('SC_Wainscot_%d_%d_%d'%(level,side,j),a,b,h,h+.70,.20,'warm_walnut')
 # Rear envelope encloses the lift equipment, not false space glazing.
 wall_segment('SC_RearWall_'+str(level),(96.9,-10),(96.9,10),h,h+(4.2 if level==0 else 3.5),.18,'ivory_enamel')
# Continuous enclosed lift shaft: no unguarded side access to the reserved hole.
for side in [-1,1]:wall_segment('SC_LiftShaftSide_'+str(side),(92.02,side*2.10),(95.96,side*2.10),-.24,8.16,.12,'ivory_enamel')
wall_segment('SC_LiftShaftBack',(95.96,-2.10),(95.96,2.10),-.24,8.16,.12,'warm_walnut')
for lo,hi in [(2.86,4.5),(7.36,8.16)]:wall_segment('SC_LiftShaftFrontBand_'+str(lo),(92.1,-2.04),(92.1,2.04),lo,hi,.12,'ivory_enamel')
# Visible triangular maintenance closures match the volume under each flight.
for flight,f in enumerate([contract['stair']['first_flight'],contract['stair']['second_flight']]):
 for x in [f['x'][0],f['x'][1]]:
  a,b=f['z'];za,zb=(f['bottom_y']-84,f['top_y']-84)if flight==0 else(f['top_y']-84,f['bottom_y']-84)
  verts=[]
  for dx in [-.04,.04]:verts.extend([(x-63+dx,-a,0),(x-63+dx,-b,0),(x-63+dx,-b,zb),(x-63+dx,-a,za)])
  mesh('SC_UnderflightSide_%d_%s'%(flight,x),verts,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'warm_walnut')
# Coordinated upper ceiling: faceted bowed ribs above shared centre and
# quieter lower ceiling zones around the lounge walls.
outline=[xy(p)for p in contract['envelope_xz_m']]
extrusion('SC_OpaqueRoof',outline,8.16,8.4,'ivory_enamel')
for z in [-10,-5,0,5,10]:
 pts=[(0,-z,7.35),(5,-z,7.70),(12,-z,8.05),(22,-z,8.05),(30,-z,7.60),(33,-z,7.35)]
 beam('SC_CurvedCeilingRib_'+str(z),pts,.24,.18,'warm_walnut')
m=bpy.data.materials.new('CommonsSmokedGlass');m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.25,.46,.49,.38);bs.inputs['Alpha'].default_value=.38;mats['glass']=m
# Continuous faceted ceiling shell follows the ribs, rather than leaving a
# flat lid above disconnected decorative strips. The occupied deck stays intact.
roof_stations=[(0,7.35),(5,7.70),(12,8.05),(22,8.05),(30,7.60),(34,7.35)]
for j,((xa,za),(xb,zb))in enumerate(zip(roof_stations,roof_stations[1:])):
 wa=14-max(0,xa-30);wb=14-max(0,xb-30)
 q=[(xa,-wa,za),(xb,-wb,zb),(xb,wb,zb),(xa,wa,za)]
 mesh('SC_ContinuousCeilingShell_'+str(j),q+[(x,y,z+.07)for x,y,z in q],[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'ivory_enamel')
# Preserve the reserved lift headroom inside its closed shaft. The original
# opaque roof above remains intact; only the lowered decorative soffit is cut.
for target in [o for o in parts if o.name.startswith(('SC_ContinuousCeilingShell','SC_CurvedCeilingRib'))]:
 bpy.ops.mesh.primitive_cube_add(size=1,location=(31.04,0,7.8));cutter=bpy.context.object;cutter.dimensions=(4.08,4.5,2)
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);bpy.context.view_layer.objects.active=target
 mod=target.modifiers.new('ReservedLiftHeadroom','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
 bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cutter,do_unlink=True)
# Ring-edge fascia and guards. Omit genuine arrival seams and stair mouth.
for region in D['floor_regions']:
 h=region['floor_y']-84
 for ri,ring in enumerate([region['boundary']]+region['holes']):
  for j,(a,b)in enumerate(zip(ring,ring[1:]+ring[:1])):
   if abs(a[0]-50)<.001 and abs(b[0]-50)<.001:continue
   if abs(a[1]+26)<.001 and abs(b[1]+26)<.001:continue
   if ri>0 and max(a[0],b[0])>92:continue # Gates and shaft own this hole.
   if h==4.5 and abs(a[1]+9.58)<.001 and abs(b[1]+9.58)<.001:
    # Split the edge at the actual upper stair exit.
    lo,hi=sorted([a[0],b[0]])
    for k,(x0,x1)in enumerate([(lo,min(hi,67.15)),(max(lo,69.25),hi)]):
     if x1>x0:
      wall_segment('SC_StairMouthGuard_'+str(k),(x0,a[1]),(x1,a[1]),h,h+1.08,.09,'warm_walnut')
    continue
   # Keep exterior wall edges free of duplicated rails; arrival edges and
   # actual upper void edges need guards with a coordinated fascia below.
   if ri==0 and min(a[0],b[0])>=63 and max(a[0],b[0])<=97 and max(abs(a[1]),abs(b[1]))<=14.001 and (abs(a[1])>=13 or abs(b[1])>=13):continue
   wall_segment('SC_Fascia_%s_%d_%d'%(h,ri,j),a,b,h-.24,h+.025,.14,'ivory_enamel')
   wall_segment('SC_GuardBase_%s_%d_%d'%(h,ri,j),a,b,h+.025,h+.35,.10,'warm_walnut')
   wall_segment('SC_Handrail_%s_%d_%d'%(h,ri,j),a,b,h+1.01,h+1.09,.12,'champagne_metal')
   wall_segment('SC_GuardGlazing_%s_%d_%d'%(h,ri,j),a,b,h+.35,h+1.01,.024,'glass')
   length=math.dist(a,b)
   for k in range(max(1,math.ceil(length/1.5))+1):
    t=k/max(1,math.ceil(length/1.5));x=a[0]+(b[0]-a[0])*t;z=a[1]+(b[1]-a[1])*t
    cx,cy=xy((x,z));extrusion('SC_GuardPost_%s_%d_%d_%d'%(h,ri,j,k),[(cx-.035,cy-.035),(cx+.035,cy-.035),(cx+.035,cy+.035),(cx-.035,cy+.035)],h+.35,h+1.04,'champagne_metal')
# Full-geometry steps; the runtime supplies smooth matched ramp contacts.
for flight,f in enumerate([contract['stair']['first_flight'],contract['stair']['second_flight']]):
 x0,x1=f['x'];z0,z1=f['z'];bottom=f['bottom_y']-84
 for i in range(15):
  a=z0+i*.32 if flight==0 else z1-(i+1)*.32;b=a+.32
  q=[xy((x0,a)),xy((x1,a)),xy((x1,b)),xy((x0,b))]
  extrusion('SC_StepVisual_%d_%d'%(flight,i),q,bottom+i*.15,bottom+(i+1)*.15,'warm_stone')
  wall_segment('SC_StepNosing_%d_%d'%(flight,i),(x0,b if flight==0 else a),(x1,b if flight==0 else a),bottom+(i+1)*.15-.025,bottom+(i+1)*.15,.045,'champagne_metal')
# Sloped solid balustrades keep people and loose objects on each flight.
for flight,f in enumerate([contract['stair']['first_flight'],contract['stair']['second_flight']]):
 for side,x in enumerate([f['x'][0]-.05,f['x'][1]+.05]):
  a,b=f['z'];za,zb=(f['bottom_y']-84,f['top_y']-84)if flight==0 else(f['top_y']-84,f['bottom_y']-84)
  for role,lo,hi,width in [('warm_walnut',.05,.33,.10),('glass',.33,1.02,.024),('champagne_metal',1.02,1.10,.12)]:
   points=[]
   for dx in [-width/2,width/2]:points.extend([(x-63+dx,-a,za+lo),(x-63+dx,-b,zb+lo),(x-63+dx,-b,zb+hi),(x-63+dx,-a,za+hi)])
   mesh('SC_StairGuard_%d_%d_%s'%(flight,side,role),points,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],role)
wall_segment('SC_MidlandingWellGuard',(66.2,-4.8),(67.2,-4.8),2.25,3.35,.10,'warm_walnut')
wall_segment('SC_MidlandingGuard',(64.15,-2.55),(69.25,-2.55),2.25,3.35,.10,'warm_walnut')
for x in [64.15,69.25]:
 wall_segment('SC_MidlandingSide_'+str(x),(x,-4.8),(x,-2.55),0,3.35,.10,'warm_walnut')
wall_segment('SC_HighFlightFrontClosure',(67.15,-9.65),(69.25,-9.65),0,4.5,.10,'warm_walnut')
wall_segment('SC_CentreMaintenanceClosure',(66.2,-9.65),(67.2,-9.65),0,2.25,.10,'warm_walnut')
mid=contract['stair']['middle_landing'];q=[xy((x,z))for x,z in [(mid['x'][0],mid['z'][0]),(mid['x'][1],mid['z'][0]),(mid['x'][1],mid['z'][1]),(mid['x'][0],mid['z'][1])]]
extrusion('SC_IntermediateLanding',q,2.01,2.25,'warm_stone')
# Enclose low under-stair space as a fitted maintenance volume.
wall_segment('SC_UnderStairClosure',(64.15,-2.55),(69.25,-2.55),0,2.25,.12,'warm_walnut')
# Two distinct gathering edges, kept away from entrance/lift approaches.
for group,(cx,cy,level)in enumerate([(16,-10,0),(19,10,4.5)]):
 for i in range(7):
  a=math.pi*.12+i*.11*math.pi;b=a+.10*math.pi
  q=[(cx+r*math.cos(t),cy+r*math.sin(t))for r,t in [(2.2,a),(2.95,a),(2.95,b),(2.2,b)]]
  extrusion('SC_ConversationBase_%d_%d'%(group,i),q,level,level+.39,'warm_walnut')
  extrusion('SC_ConversationSeat_%d_%d'%(group,i),q,level+.39,level+.49,'teal_weave')
 datum('conversation_'+str(group),(cx,cy,level))
for j,(x,z,h)in enumerate([(70,10,3.65),(85,10,3.65),(88,-9,3.65),(61,0,3.6),(70,-12,7.65),(84,10,7.65),(90,-8,7.65),(60,-11.8,7.55)]):
 cx,cy=xy((x,z));extrusion('SC_LampHousing_'+str(j),[(cx-.5,cy-.23),(cx+.5,cy-.23),(cx+.5,cy+.23),(cx-.5,cy+.23)],h,h+.12,'champagne_metal');extrusion('SC_LampLens_'+str(j),[(cx-.44,cy-.19),(cx+.44,cy-.19),(cx+.44,cy+.19),(cx-.44,cy+.19)],h-.015,h,'lens');datum('light_'+str(j),(cx,cy,h-.03))
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1;bpy.ops.file.pack_all();source=ROOT/'source/AST-COM-001.blend';export=ROOT/'exports/AST-COM-001.glb';bpy.ops.wm.save_as_mainfile(filepath=str(source))
# Preserve visual-only step meshes as a distinct contact category.
for tag in ['step','static']:
 for role,material in mats.items():
  selected=[o for o in list(scene.objects)if o.type=='MESH'and o.data.materials and o.data.materials[0]==material and (o.name.startswith(('SC_StepVisual','SC_StepNosing','SC_step_')))==(tag=='step')]
  if not selected:continue
  bpy.ops.object.select_all(action='DESELECT')
  for o in selected:o.select_set(True)
  bpy.context.view_layer.objects.active=selected[0];bpy.ops.object.join();bpy.context.object.name='SC_'+tag+'_'+role
bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',export_yup=True,export_extras=True)
(ROOT/'AST-COM-001.manifest.json').write_text(json.dumps({'catalogue_id':'AST-COM-001','name':'Starboard vertical commons architecture','source':'source/AST-COM-001.blend','export':'exports/AST-COM-001.glb','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'export_sha256':hashlib.sha256(export.read_bytes()).hexdigest(),'status':'Work in progress; integration, contacts and visual review pending'},indent=2)+'\n')
