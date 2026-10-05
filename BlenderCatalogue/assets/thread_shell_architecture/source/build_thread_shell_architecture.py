"""Original Thread & Shell boutique architecture in its verified fore retail allocation."""
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



AID='AST-RTL-007';D=json.loads((ROOT/'source/architecture_contract.json').read_text())
assert all(a['catalogue_id']!=AID or a['family']=='thread_shell_architecture' for a in json.loads((CAT/'catalogue_manifest.json').read_text())['assets'])
m=bpy.data.materials.new('RetailVisibleGlass');m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(.23,.42,.44,.28);b.inputs['Alpha'].default_value=.28;mats['glass']=m
F=52.5
def xyz(x,y,z):return(x-8,-(z+216),y-F)
def h(x,z=0):
 profile=D['public_ceiling_profile']
 for (xa,ya),(xb,yb)in zip(profile,profile[1:]):
  if xa<=x<=xb:return ya+(yb-ya)*(x-xa)/(xb-xa)
 return profile[0][1]if x<profile[0][0]else profile[-1][1]
def wall(name,a,b,lo,hi,width,role,_split=True):
 if _split and (callable(lo)or callable(hi))and abs(b[0]-a[0])>.00001:
  ratios=sorted([0.,1.]+[(x-a[0])/(b[0]-a[0])for x,y in D['public_ceiling_profile'][1:-1]if min(a[0],b[0])<x<max(a[0],b[0])])
  if len(ratios)>2:
   result=None
   for i,(u,v)in enumerate(zip(ratios,ratios[1:])):
    aa=(a[0]+(b[0]-a[0])*u,a[1]+(b[1]-a[1])*u);bb=(a[0]+(b[0]-a[0])*v,a[1]+(b[1]-a[1])*v);result=wall(name+'_'+str(i),aa,bb,lo,hi,width,role,False)
   return result
 ax,az=a;bx,bz=b;dx=bx-ax;dz=bz-az;length=math.hypot(dx,dz);nx=-dz/length*width/2;nz=dx/length*width/2
 v=[]
 for side in [-1,1]:
  for x,z,top in [(ax,az,False),(bx,bz,False),(bx,bz,True),(ax,az,True)]:
   x+=side*nx;z+=side*nz;y=(hi(x,z)if callable(hi)else hi)if top else(lo(x,z)if callable(lo)else lo);v.append(xyz(x,y,z))
 return mesh(name,v,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],role)
def slab(name,x0,x1,z0,z1,lo,hi,role):return extrusion(name,[(x0-8,-z0-216),(x1-8,-z0-216),(x1-8,-z1-216),(x0-8,-z1-216)],lo-F,hi-F,role)
def ceiling(name,tri,height,role):
 v=[xyz(x,(height(x,z)if callable(height)else height)+offset,z)for offset in [0,.12]for x,z in tri]
 return mesh(name,v,[(2,1,0),(3,4,5),(0,1,4,3),(1,2,5,4),(2,0,3,5)],role)
def rail(name,a,b):
 wall(name+'_base',a,b,F,F+.22,.13,'ivory_enamel');wall(name+'_glass',a,b,F+.22,F+1.04,.024,'glass');wall(name+'_cap',a,b,F+1.04,F+1.11,.15,'warm_walnut')
# True perimeter follows owned floor. Spine seams remain open.
ring=D['floor_boundary']
for i,(a,b)in enumerate(zip(ring,ring[1:]+ring[:1])):
 if abs(a[0]-4)<.001 and abs(b[0]-4)<.001:continue
 mid=((a[0]+b[0])/2,(a[1]+b[1])/2)
 if max(a[0],b[0])<=12.001 and mid[1]<-198:
  rail('TAIL_PromenadeEdge_'+str(i),a,b);continue
 staff=mid[1]>-198 or min(a[0],b[0])>=37
 if staff:wall('TAIL_StaffOuter_'+str(i),a,b,F,F+3.7,.18,'staff_white_paint')
 else:
  wall('TAIL_PublicDado_'+str(i),a,b,F,F+.85,.18,'warm_walnut')
  wall('TAIL_PublicWall_'+str(i),a,b,F+.85,h,.18,'ivory_enamel')
# Designed glazing beside the generous central entry looks into actual retail volume.
for i,(a,b)in enumerate([((8,-224),(10,-232)),((8,-224),(8,-219)),((8,-213),(8,-208)),((8,-208),(12,-201))]):
 wall('TAIL_DisplayPlinth_'+str(i),a,b,F,F+1.0,.20,'warm_stone')
 wall('TAIL_FrontGlass_'+str(i),a,b,F+1.0,F+4.20,.032,'glass')
 wall('TAIL_TerracottaFascia_'+str(i),a,b,F+4.20,h,.23,'retail_terracotta_enamel')
 for j,p in enumerate([a,b]):wall('TAIL_FrontMullion_%s_%s'%(i,j),(p[0]-.06,p[1]),(p[0]+.06,p[1]),F+.95,F+4.25,.12,'champagne_metal')
for i,z in enumerate([-219,-213]):
 slab('TAIL_EntryPier_'+str(i),7.72,8.35,z-.18,z+.18,F,h(8),'ivory_enamel')
wall('TAIL_EntryLintel',(8,-219),(8,-213),F+4.8,h,.42,'retail_terracotta_enamel')
# Rising public ceiling with real higher pockets exposing the column capitals.
for i,tri in enumerate(D['public_triangles']):ceiling('TAIL_PublicCeiling_'+str(i),tri,h,'ivory_enamel')
for index,ring in enumerate(D['ceiling_coffers']):
 for i,(a,b)in enumerate(zip(ring,ring[1:]+ring[:1])):wall('TAIL_CapitalCoffer_%s_%s'%(index,i),a,b,lambda x,z:h(x,z)+.12,60.76,.12,'warm_walnut')
for i,tri in enumerate(D['service_triangles']):ceiling('TAIL_ServiceCeiling_'+str(i),tri,F+3.7,'staff_white_paint')
# A lower porch marks the promenade without replacing the taller shop volume.
slab('TAIL_PromenadeCanopy',4.05,8.0,-232,-200,F+4.6,F+4.77,'ivory_enamel')
for z in [-231,-201]:
 slab('TAIL_PorchBearing_'+str(z),7.5,7.8,z-.16,z+.16,F,F+4.6,'warm_stone')
# The private bays have closed roofs and complete wide door pockets, not exposed curtains.
for pod in D['fitting_pods']:
 key=pod['id'];x0=pod['front_x'];x1=pod['back_x'];z=pod['center_z'];half=pod['width']/2
 for side in [-1,1]:wall('TAIL_PrivateSide_%s_%s'%(key,side),(x0,z+side*half),(x1,z+side*half),F,F+3.4,.16,'oatmeal_weave')
 wall('TAIL_PrivateBack_'+key,(x1,z-half),(x1,z+half),F,F+3.4,.16,'ivory_enamel')
 for a,b in [(z-half,z-2.58),(z+2.58,z+half)]:wall('TAIL_PrivateFront_'+key+str(a),(x0,a),(x0,b),F,F+3.4,.16,'retail_terracotta_enamel')
 wall('TAIL_PrivateDoorHeader_'+key,(x0,z-2.58),(x0,z+2.58),F+2.66,F+3.4,.16,'retail_terracotta_enamel')
 slab('TAIL_PrivateRoof_'+key,x0,x1,z-half,z+half,F+3.4,F+3.55,'ivory_enamel')
 datum('fitting_door_'+key,xyz(x0,F,z))
 slab('TAIL_FittingBenchBase_'+key,x1-1.15,x1-.30,z-1.50,z+1.50,F,F+.42,'warm_walnut')
 slab('TAIL_FittingBenchPad_'+key,x1-1.10,x1-.34,z-1.43,z+1.43,F+.42,F+.50,'clay_weave')
 datum('fitting_seat_'+key,xyz(x1-.74,F+.50,z));datum('fitting_approach_'+key,xyz(x1-2.2,F,z))
 # Useful hooks/rack use the nearby bench and remain inside the opaque bay.
 for i,zz in enumerate([z-1.15,z,z+1.15]):
  wall('TAIL_FittingHook_%s_%s'%(key,i),(x1-.08,zz),(x1-.52,zz),F+1.42,F+1.50,.08,'champagne_metal')
# The upper rear screen closes the volume above the lower fitting and staff roofs.
for i,(a,b,low)in enumerate([(-234,-228.5,F),(-228.5,-222.5,F+3.4),(-222.5,-212.5,F+3.7),(-212.5,-206.5,F+3.4),(-206.5,-197,F)]):
 wall('TAIL_UpperStaffScreen_'+str(i),(37,a),(37,b),low,lambda x,z:h(x,z)+.12,.18,'ivory_enamel')
# A closed staff threshold leads to the separately enclosed rear branch.
for a,b in [(-222.5,-216.75),(-214.25,-212.5)]:wall('TAIL_ServiceScreen_'+str(a),(37,a),(37,b),F,F+3.7,.18,'ivory_enamel')
wall('TAIL_ServiceDoorHeader',(37,-216.75),(37,-214.25),F+2.63,F+3.7,.18,'ivory_enamel')
datum('service_door',xyz(37,F,-215.5))
for a,b in [(-196.1,-195.75),(-193.25,-192.9)]:wall('TAIL_StaffEntranceJamb_'+str(a),(6,a),(6,b),F,F+3.7,.18,'staff_white_paint')
wall('TAIL_StaffEntranceHeader',(6,-195.75),(6,-193.25),F+2.63,F+3.7,.18,'staff_white_paint')
datum('staff_entry_door',xyz(6,F,-194.5))
# Bespoke work counter: lowered guest return, long fabric inspection surface and storage.
slab('TAIL_WorkCounterBase',31.1,34.9,-221.4,-218.2,F,F+.78,'warm_walnut')
slab('TAIL_WorkCounterTop',30.9,35.1,-221.6,-218.0,F+.78,F+.88,'warm_stone')
slab('TAIL_LowerGuestCounter',30.9,32.3,-218.0,-216.9,F+.64,F+.72,'warm_walnut')
# Curved textile-display frames divide browsing around the centre rather than fill its route.
for index,(cx,cz,start,end)in enumerate([(19,-226,-65,65),(19,-206,115,245)]):
 points=[(cx+2.5*math.cos(math.radians(start+(end-start)*i/12)),cz+2.5*math.sin(math.radians(start+(end-start)*i/12)))for i in range(13)]
 for i,(a,b)in enumerate(zip(points,points[1:])):
  wall('TAIL_DisplayFoot_%s_%s'%(index,i),a,b,F,F+.20,.48,'warm_walnut')
  wall('TAIL_DisplayRail_%s_%s'%(index,i),a,b,F+1.62,F+1.70,.08,'champagne_metal')
 for i in [0,6,12]:
  x,z=points[i];slab('TAIL_DisplayPost_%s_%s'%(index,i),x-.045,x+.045,z-.045,z+.045,F+.20,F+1.70,'champagne_metal')
 for i in [2,4,6,8,10]:
  x=(points[i][0]+points[i+1][0])/2;z=(points[i][1]+points[i+1][1])/2;datum('fabric_%s_%s'%(index,i),xyz(x,F+1.60,z))
# Actual fixture housings touch their ceiling or private roof.
fixtures=[('public_'+str(i),x,z,h(x,z),True)for i,(x,z)in enumerate([(18,-228),(18,-204),(22,-216),(32,-217)])]+[('private_'+str(i),33,z,F+3.4,True)for i,z in enumerate([-225.5,-209.5])]+[('staff_'+str(i),x,z,F+3.7,False)for i,(x,z)in enumerate([(40,-227),(40,-209),(22,-194.5)])]
for key,x,z,top,warm in fixtures:
 slab('TAIL_FixtureHousing_'+key,x-.36,x+.36,z-.28,z+.28,top-.16,top,'champagne_metal')
 slab('TAIL_FixtureLens_'+key,x-.31,x+.31,z-.23,z+.23,top-.175,top-.16,'lens')
 datum('light_'+key,xyz(x,top-.20,z))
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1;bpy.ops.file.pack_all();source=ROOT/'source'/(AID+'.blend');export=ROOT/'exports'/(AID+'.glb');bpy.ops.wm.save_as_mainfile(filepath=str(source))
bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',export_yup=True,export_extras=True)
record={'catalogue_id':AID,'name':'Thread & Shell profiled boutique and private fitting architecture','source':'source/'+AID+'.blend','export':'exports/'+AID+'.glb','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'export_sha256':hashlib.sha256(export.read_bytes()).hexdigest(),'status':'Original real allocation architecture; runtime access, privacy and final art pending'}
(ROOT/(AID+'.manifest.json')).write_text(json.dumps(record,indent=2)+'\n');print(record)
