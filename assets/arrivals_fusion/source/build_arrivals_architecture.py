"""Original integrated Cunard-informed arrivals architecture; service circulation is concealed."""
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

D=json.loads((ROOT/'source/section_contract.json').read_text())
for registered in json.loads((CAT/'catalogue_manifest.json').read_text())['assets']:
 if registered['catalogue_id']=='AST-ARR-002':assert registered['source']=='assets/arrivals_fusion/source/AST-ARR-002.blend','Catalogue identity belongs elsewhere'
# Anchor maps source(0,0,0) to ship(-31,0,-432).
def xy(p):return(p[0]+31,-p[1]-432)
def wall(name,a,b,z0,z1,width,role):
 a=Vector(xy(a));b=Vector(xy(b));v=(b-a).normalized();n=Vector((-v.y,v.x))*width/2
 return extrusion(name,[tuple(a+n),tuple(b+n),tuple(b-n),tuple(a-n)],z0,z1,role)
def source_rect(x0,x1,y0,y1):return[(x0,y0),(x1,y0),(x1,y1),(x0,y1)]
def disc_x(name,x,cy,cz,radius,depth,role,n=32):
 v=[(xx,cy+radius*math.cos(2*math.pi*i/n),cz+radius*math.sin(2*math.pi*i/n))for xx in [x-depth/2,x+depth/2]for i in range(n)];f=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n)for i in range(n)];return mesh(name,v,f,role)
# The museum-like machinery display has visibly framed glass, not missing walls.
m=bpy.data.materials.new('ArrivalsArchitecturalGlass');m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.23,.39,.42,.30);bs.inputs['Alpha'].default_value=.30;mats['glass']=m
# True outer enclosure, inset to preserve very close public/service routes.
for z in [-465.85,-398.15]:
 wall('ARR_OuterEnd_'+str(z),(-53.85,z),(-8.15,z),0,11.76,.20,'ivory_enamel')
 wall('ARR_EndWainscot_'+str(z),(-53.85,z),(-8.15,z),.05,1.2,.25,'warm_walnut')
for za,zb in [(-465.85,-435),(-429,-398.15)]:
 wall('ARR_EastEnclosure_'+str(za),(-8.15,za),(-8.15,zb),0,11.76,.20,'ivory_enamel')
for lo,hi in [(4.4,6),(9.8,11.76)]:wall('ARR_PublicEntryHeader_'+str(lo),(-8.15,-435),(-8.15,-429),lo,hi,.25,'warm_stone')
wall('ARR_WestLowerOpaque',(-53.85,-465.85),(-53.85,-398.15),0,6,.20,'ivory_enamel')
for za,zb in [(-465.85,-434),(-430,-398.15)]:wall('ARR_WestServiceEnclosure_'+str(za),(-53.85,za),(-53.85,zb),6,11.76,.20,'ivory_enamel')
wall('ARR_ServiceEntryHeader',(-53.85,-434),(-53.85,-430),9.2,11.76,.20,'ivory_enamel')
# Opaque maintenance portals are opened only inside fully enclosed links.
def screened_wall(name,x,z0,z1,bottom,top,width,role):
 cursor=z0
 for link in sorted(D.get('concealed_exhibit_links',[]),key=lambda v:v['z'][0]):
  a,b=link['z']
  if a<z0 or b>z1:continue
  if a>cursor:wall(name+'_solid_'+str(a),(x,cursor),(x,a),bottom,top,width,role)
  if bottom<6:wall(name+'_plinth_'+str(a),(x,a),(x,b),bottom,6,width,role)
  wall(name+'_header_'+str(a),(x,a),(x,b),9.2,top,width,role)
  cursor=b
 if cursor<z1:wall(name+'_end',(x,cursor),(x,z1),bottom,top,width,role)
# Full-height opaque screens conceal all service paths from both guest levels.
for i,v in enumerate(D['service_screens']):
 a,b=((v['span'][0],v['value']),(v['span'][1],v['value']))if v['axis']=='z'else((v['value'],v['span'][0]),(v['value'],v['span'][1]))
 if v['axis']=='x':screened_wall('ARR_OpaqueServiceScreen_'+str(i),v['value'],v['span'][0],v['span'][1],v['bottom_y'],v['top_y'],.24,'ivory_enamel')
 else:wall('ARR_OpaqueServiceScreen_'+str(i),a,b,v['bottom_y'],v['top_y'],.24,'ivory_enamel')
# Architectural bearing piers at gallery/exhibit edges; metallic bands are narrow.
piers=[(-44.8,-440.7),(-20.8,-440.7),(-44.8,-423.3),(-20.8,-423.3),(-10.0,-453),(-10.0,-411)]
for i,p in enumerate(piers):
 cx,cy=xy(p);N=16;v=[]
 for h,radius in [(0,.80),(.22,.86),(.40,.67),(5.4,.67),(5.8,.90),(6.16,.90),(6.40,.67),(10.9,.67),(11.4,.95),(11.76,.95)]:
  for j in range(N):v.append((cx+radius*math.cos(2*math.pi*j/N),cy+radius*math.sin(2*math.pi*j/N),h))
 f=[tuple(reversed(range(N))),tuple(range(len(v)-N,len(v)))]+[(k*N+j,k*N+(j+1)%N,(k+1)*N+(j+1)%N,(k+1)*N+j)for k in range(9)for j in range(N)];mesh('ARR_ProfiledBearingPier_'+str(i),v,f,'warm_stone')
 for h in [.21,5.80,11.42]:
  ring=[(cx+.91*math.cos(2*math.pi*j/N),cy+.91*math.sin(2*math.pi*j/N))for j in range(N)];extrusion('ARR_PierBand_%d_%s'%(i,h),ring,h,h+.055,'champagne_metal')
# Framed focal wall behind the stair. The original sun relief is a SunCorp
# architectural motif, not copied Cunard imagery or a second oversized monument.
screened_wall('ARR_StairFocalWall',-47.4,-445,-419,0,11.76,.28,'warm_walnut')
for z in [-444,-420]:wall('ARR_FocalPilaster_'+str(z),(-47.10,z),(-46.7,z),0,11.55,.7,'warm_stone')
disc_x('ARR_EmblemBackplate',-15.98,0,7.5,3.55,.10,'warm_stone')
disc_x('ARR_EmblemSun',-15.86,0,7.5,1.22,.16,'champagne_metal')
for j in range(16):
 a=2*math.pi*j/16;verts=[(-15.74,1.45*math.cos(a-.06),7.5+1.45*math.sin(a-.06)),(-15.74,3.05*math.cos(a),7.5+3.05*math.sin(a)),(-15.74,1.45*math.cos(a+.06),7.5+1.45*math.sin(a+.06)),(-15.86,1.45*math.cos(a),7.5+1.45*math.sin(a))];mesh('ARR_SunRay_'+str(j),verts,[(0,2,1),(0,1,3),(1,2,3),(2,0,3)],'champagne_metal')
# Actual twenty-tread flights; runtime adds matched smooth walking contacts.
for i in range(20):
 x1=-30-i*.30;x0=x1-.30;half=3.0+.45*(1-i/19)
 q=[xy(v)for v in [(x0,-432-half),(x1,-432-half),(x1,-432+half),(x0,-432+half)]]
 extrusion('ARR_StepMain_%02d'%i,q,i*.15,(i+1)*.15,'warm_stone')
for label,sign in [('North',-1),('South',1)]:
 for i in range(20):
  near=-432+sign*5+sign*i*.30;far=near+sign*.30;lo,hi=sorted([near,far]);q=[xy(v)for v in [(-45,lo),(-42,lo),(-42,hi),(-45,hi)]]
  extrusion('ARR_Step%s_%02d'%(label,i),q,3+i*.15,3+(i+1)*.15,'warm_stone')
landing=D['stair']['intermediate_landing'];q=[xy(v)for v in [(landing['x'][0],landing['z'][0]),(landing['x'][1],landing['z'][0]),(landing['x'][1],landing['z'][1]),(landing['x'][0],landing['z'][1])]];extrusion('ARR_IntermediateLanding',q,2.76,3,'warm_stone')
# Supported stepped undersides are opaque; no open triangular escape pockets.
for side in [-1,1]:
 z=-432+side*3;v=[]
 for dz in [-.05,.05]:v.extend([(*xy((-30,z+dz)),0),(*xy((-36,z+dz)),0),(*xy((-36,z+dz)),3)])
 mesh('ARR_MainStringer_'+str(side),v,[(2,1,0),(3,4,5),(0,1,4,3),(1,2,5,4),(2,0,3,5)],'warm_walnut')
# Authored balcony edge profile. Structural floors are separate, avoiding
# accidental collision across real openings. Portal/stair/shaft interfaces stay open.
for region in D['floor_regions']:
 if region['id']!='D02_fusion_visitor_galleries':continue
 for ring in [region['boundary']]+region['holes']:
  for i,(a,b)in enumerate(zip(ring,ring[1:]+ring[:1])):
   mid=((a[0]+b[0])/2,(a[1]+b[1])/2)
   if abs(mid[0])<.01:continue
   if -16.5<mid[0]<-12.7 and -426.1<mid[1]<-421.9:continue
   if -45.15<mid[0]<-41.85 and (abs(mid[1]+443)<.03 or abs(mid[1]+421)<.03):continue
   if mid[0]>-8.2 or mid[0]<-47.5:continue
   wall('ARR_BalconyFascia_'+str(i),a,b,5.62,6.03,.28,'ivory_enamel')
   wall('ARR_BalconyLowerCornice_'+str(i),a,b,5.35,5.47,.30,'ivory_enamel')
   wall('ARR_BalconyTimberReveal_'+str(i),a,b,5.47,5.62,.22,'warm_walnut')
   wall('ARR_BalconyGlass_'+str(i),a,b,6.24,7.08,.024,'glass')
   wall('ARR_BalconyBase_'+str(i),a,b,6.03,6.24,.12,'warm_walnut')
   wall('ARR_BalconyCap_'+str(i),a,b,7.08,7.17,.10,'champagne_metal')
# Smooth guarded stair slopes express the same profiled bronze language.
for side in [-1,1]:
 a=xy((-30,-432+side*3.5));b=xy((-36,-432+side*3.15));beam('ARR_MainStairRail_'+str(side),[(*a,1.08),(*b,4.08)],.09,.09,'champagne_metal')
 for j in range(9):
  t=j/8;x=-30-6*t;z=-432+side*(3.5-.35*t);cx,cy=xy((x,z));extrusion('ARR_MainBaluster_%s_%s'%(side,j),source_rect(cx-.025,cx+.025,cy-.025,cy+.025),3*t+.05,3*t+1.05,'champagne_metal')
for label,z0,z1 in [('N',-437,-443),('S',-427,-421)]:
 for x in [-45.04,-41.96]:
  a=xy((x,z0));b=xy((x,z1));beam('ARR_UpperStairRail_%s_%s'%(label,x),[(*a,4.08),(*b,7.08)],.085,.085,'champagne_metal')
  for j in range(9):
   t=j/8;z=z0+(z1-z0)*t;cx,cy=xy((x,z));extrusion('ARR_UpperBaluster_%s_%s_%s'%(label,x,j),source_rect(cx-.025,cx+.025,cy-.025,cy+.025),3+3*t+.05,4.05+3*t,'champagne_metal')

# Continuous guard glazing and intermediate landing edges protect ordinary
# movement and loose props; narrow balusters alone do not close these openings.
def slope_glass(name,a,b,low_a,low_b):
 a=Vector(xy(a));b=Vector(xy(b));v=(b-a).normalized();n=Vector((-v.y,v.x))*.012
 points=[]
 for sign in [-1,1]:
  aa=a+n*sign;bb=b+n*sign;points.extend([(aa.x,aa.y,low_a+.15),(bb.x,bb.y,low_b+.15),(bb.x,bb.y,low_b+1.0),(aa.x,aa.y,low_a+1.0)])
 mesh(name,points,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'glass')
for side in [-1,1]:slope_glass('ARR_MainStairGlass_'+str(side),(-30,-432+side*3.5),(-36,-432+side*3.15),0,3)
for label,z0,z1 in [('N',-437,-443),('S',-427,-421)]:
 for x in [-45.04,-41.96]:
  slope_glass('ARR_UpperStairGlass_%s_%s'%(label,x),(x,z0),(x,z1),3,6)
  a=xy((x,z0));b=xy((x,z1));beam('ARR_UpperStringer_%s_%s'%(label,x),[(*a,2.86),(*b,5.86)],.20,.28,'warm_stone')
for i,(a,b)in enumerate([((-45,-437),(-45,-427)),((-42,-437),(-36,-437)),((-42,-427),(-36,-427)),((-36,-437),(-36,-435)),((-36,-429),(-36,-427))]):
 wall('ARR_MidLandingGlass_'+str(i),a,b,3.15,4.02,.024,'glass');wall('ARR_MidLandingCap_'+str(i),a,b,4.02,4.11,.10,'champagne_metal')
for cy in [-1.5,1.5]:beam('ARR_EmblemStandOff_'+str(cy),[(-16.40,cy,7.5),(-16.03,cy,7.5)],.20,.20,'champagne_metal')

# Lift shaft matches the tested cabin contract; no alternate controller is made.
origin=D['lift']['origin_xz'];front=origin[0];cz=origin[1]
for side in [-1,1]:wall('ARR_LiftShaftSide_'+str(side),(front-.18,cz+side*2.10),(front+3.76,cz+side*2.10),-.24,9.35,.12,'ivory_enamel')
wall('ARR_LiftShaftRear',(front+3.76,cz-2.10),(front+3.76,cz+2.10),-.24,9.35,.12,'ivory_enamel')
for lo,hi in [(2.86,6),(8.86,9.35)]:wall('ARR_LiftFrontBand_'+str(lo),(front-.10,cz-2.04),(front-.10,cz+2.04),lo,hi,.12,'ivory_enamel')
# Enclosed service connectors: opaque floors, sides and roofs. No guest-facing
# catwalks or visible access doors; the route terminates in a screened end bay.
for link in D.get('concealed_exhibit_links',[]):
 x0,x1=link['x'];z0,z1=link['z'];name=link['id']
 for z in [z0,z1]:wall('ARR_EnclosedLink_'+name+str(z),(x0,z),(x1,z),6,9.4,.18,'warm_walnut')
 q=[xy(v)for v in [(x0,z0),(x1,z0),(x1,z1),(x0,z1)]]
 extrusion('ARR_LinkRoof_'+name,q,9.2,9.4,'ivory_enamel')
# Selected overhead exhibit glazing with opaque structural edge frames. All
# maintenance is behind the dedicated screens, not visible factory catwalks.
for index,housing in enumerate(D['exhibit_housings']):
 bay_x0,x1=housing['x'];x0=housing['opaque_service_bay_end_x'];z0,z1=housing['z'];lo=housing['glazed_underside_y'];hi=housing['top_y'];q=[xy(v)for v in [(x0,z0),(x1,z0),(x1,z1),(x0,z1)]]
 extrusion('ARR_ExhibitGlassBelly_'+str(index),q,lo,lo+.06,'glass')
 bay=[xy(v)for v in [(bay_x0,z0),(x0,z0),(x0,z1),(bay_x0,z1)]]
 extrusion('ARR_ServiceBayBase_'+str(index),bay,5.76,6,'warm_stone')
 extrusion('ARR_ServiceBayRoof_'+str(index),bay,hi-.12,hi+.08,'ivory_enamel')
 for z in [z0,z1]:wall('ARR_ServiceBaySide_'+str(index),(bay_x0,z),(x0,z),6,hi,.18,'warm_walnut')
 link=D['concealed_exhibit_links'][index];a,b=link['z']
 for za,zb in [(z0,a),(b,z1)]:wall('ARR_ServiceBayWest_'+str(index),(bay_x0,za),(bay_x0,zb),6,hi,.18,'warm_walnut')
 wall('ARR_ServiceBayDoorHeader_'+str(index),(bay_x0,a),(bay_x0,b),9.2,hi,.18,'warm_walnut')
 # Opaque separation hides the service bay from the curated display volume.
 wall('ARR_ServiceBayDisplayPartition_'+str(index),(x0,z0),(x0,z1),6,hi,.18,'warm_walnut')
 for a,b in zip([(x0,z0),(x1,z0),(x1,z1),(x0,z1)],[(x1,z0),(x1,z1),(x0,z1),(x0,z0)]):
  wall('ARR_ExhibitLowerFrame_'+str(index),a,b,lo-.16,lo+.08,.23,'warm_stone')
  wall('ARR_ExhibitUpperFrame_'+str(index),a,b,hi-.12,hi+.08,.22,'warm_stone')
  wall('ARR_ExhibitGlassSide_'+str(index),a,b,lo+.08,hi-.12,.035,'glass')
 for x in [x0,x0+(x1-x0)/3,x0+2*(x1-x0)/3,x1]:
  for z in [z0,z1]:wall('ARR_ExhibitMullion_'+str(index),(x-.04,z),(x+.04,z),lo,hi,.12,'champagne_metal')
 for x in [(x0+x1)/2-5.5,(x0+x1)/2+5.5]:wall('ARR_ExhibitBearingCrossbeam_'+str(index),(x,z0),(x,z1),10.83,10.98,.32,'ivory_enamel')
 front_z=z0 if index==0 else z1
 for pier_x,target_x in [(-44.8,x0),(-20.8,x1)]:wall('ARR_ExhibitTransferShoulder_'+str(index),(pier_x,front_z),(target_x,front_z),10.40,10.98,.85,'warm_stone')
 datum('exhibit_center_'+str(index),(*xy(((bay_x0+x1)/2,(z0+z1)/2)),8.65))
# Soffits frame the entry and the side hospitality bays rather than lowering
# the entire court. The central view remains clear of giant chandeliers.
for i,(x0,x1,z0,z1,h)in enumerate([(-18,-8,-442,-422,4.15),(-44,-18,-465,-456,3.8),(-44,-18,-408,-399,3.8)]):
 pieces=[(x0,x1,z0,z1)] if i!=0 else [(-18,-16.7,z0,z1),(-12.5,-8,z0,z1),(-16.7,-12.5,z0,-426.3)]
 for j,(a,b,c,d)in enumerate(pieces):
  q=[xy(v)for v in [(a,c),(b,c),(b,d),(a,d)]];extrusion('ARR_HospitalityCanopy_%d_%d'%(i,j),q,h,h+.18,'ivory_enamel')
# Fixtures attach to actual structure and emit below their lenses.
light_points=[(-14,-436,3.92),(-14,-428,3.92),(-25,-441,5.70),(-35,-441,5.70),(-25,-423,5.70),(-35,-423,5.70),(-40,-443.7,9.2),(-22,-432,11.25),(-40,-420.3,9.2),(-31,-460,3.56),(-31,-404,3.56)]
for i,(x,z,h)in enumerate(light_points):
 cx,cy=xy((x,z));N=16;q=[(cx+.30*math.cos(2*math.pi*j/N),cy+.30*math.sin(2*math.pi*j/N))for j in range(N)];extrusion('ARR_FixtureCasing_'+str(i),q,h,h+.10,'champagne_metal');extrusion('ARR_FixtureLens_'+str(i),[(cx+(a-cx)*.88,cy+(b-cy)*.88)for a,b in q],h-.025,h,'lens');datum('light_'+str(i),(cx,cy,h-.04))
 mount=4.15 if i<2 else (5.76 if i<6 else (11.76 if i<9 else 3.8))
 if mount>h+.10:beam('ARR_FixtureMount_'+str(i),[(cx,cy,h+.10),(cx,cy,mount)],.04,.04,'champagne_metal')

# Two visible directional luminaires reveal the relief and timber wall.
for i,z in enumerate([-432.7,-431.3]):
 cx,cy=xy((-43.7,z));h=10.5
 disc_x('ARR_WallwashHousing_'+str(i),cx+.04,cy,h,.32,.14,'champagne_metal',16)
 disc_x('ARR_WallwashLens_'+str(i),cx-.045,cy,h,.265,.025,'lens',16)
 beam('ARR_WallwashStem_'+str(i),[(cx,cy,h+.25),(cx,cy,11.76)],.055,.055,'champagne_metal')
 datum('wallwash_'+str(i),(cx-.08,cy,h))

scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1;bpy.ops.file.pack_all();source=ROOT/'source/AST-ARR-002.blend';export=ROOT/'exports/AST-ARR-002.glb';bpy.ops.wm.save_as_mainfile(filepath=str(source));tri=0
for o in parts:o.data.calc_loop_triangles();tri+=len(o.data.loop_triangles)
bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',export_yup=True,export_extras=True)
record={'catalogue_id':'AST-ARR-002','name':'Integrated arrivals and curated fusion-gallery architecture','source':'source/AST-ARR-002.blend','export':'exports/AST-ARR-002.glb','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'export_sha256':hashlib.sha256(export.read_bytes()).hexdigest(),'triangles':tri,'status':'Editable section draft; runtime route, screening, machinery, fixture attachment and visual checks pending'};(ROOT/'AST-ARR-002.manifest.json').write_text(json.dumps(record,indent=2)+'\n');print(record)
