"""Editable connected Grand Pool/Orchard section. One original architectural family.
Shared metric materials; existing stair/enclosure design derivatives. No Godot writes.
Common floor previews and unchanged door-fitting previews are excluded from GLB.
"""
from pathlib import Path
import bpy,bmesh,math,json,hashlib,sys
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1];C=R.parents[1];D=json.loads((R/'source/connected_contract.json').read_text());AID='AST-AQU-016'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for p,h in D['preserved_catalogue_inputs'].items():assert sha(C/p)==h,p
assert all(a['catalogue_id']!=AID or a['family']=='grand_pool_orchard_section' for a in json.loads((C/'catalogue_manifest.json').read_text())['assets'])
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
sys.path.insert(0,str(C/'standards'));import retail_materials,aquatic_materials,botanical_materials
mats=retail_materials.materials();mats.update(aquatic_materials.materials());mats.update(botanical_materials.materials())
# Keep the established shared material graphs and metric UV settings unchanged.
glass=bpy.data.materials.new('circulation_glass');glass.use_nodes=True;n=glass.node_tree.nodes.get('Principled BSDF');n.inputs['Base Color'].default_value=(.23,.49,.51,1);n.inputs['Alpha'].default_value=.23;n.inputs['Roughness'].default_value=.22;glass.diffuse_color=(.23,.49,.51,.23);glass.surface_render_method='DITHERED';mats['glass']=glass
lens=bpy.data.materials.new('GardenOpalLens');lens.use_nodes=True;n=lens.node_tree.nodes.get('Principled BSDF');n.inputs['Base Color'].default_value=(1,.95,.84,1);n.inputs['Emission Color'].default_value=(1,.91,.75,1);n.inputs['Emission Strength'].default_value=.7;mats['lens']=lens
parts=[];D['fixtures']=[];D['interfaces']=[];D['source_parts']=[]
def mesh(name,verts,faces,role,owner=AID,preview=False):
 me=bpy.data.meshes.new(name);me.from_pydata([(x,-z,y)for x,y,z in verts],[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
 o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);me.materials.append(mats[role]);o['catalogue_id']=owner;o['assembly_owner']=AID;o['export_excluded']=preview;o['collision_contract']='none' if preview else ('visual_only_stair_tread' if name.startswith(('CIR630_Tread','CIR630_Nose','CIR630_FinalRiser','GP_CeremonialTread','GP_CeremonialFinalRiser')) else 'concave_static_surface');uv=me.uv_layers.new(name='MetreScaled');scale=mats[role].get('meters_per_tile_uv',[1,1])
 for p in me.polygons:
  normal=p.normal.normalized();u=(Vector((1,0,0))-normal*normal.x).normalized()if abs(normal.z)>.7 else Vector((-normal.y,normal.x,0)).normalized();v=normal.cross(u)
  for k in p.loop_indices:
   q=me.vertices[me.loops[k].vertex_index].co;uv.data[k].uv=(q.dot(u)/scale[0],q.dot(v)/scale[1])
 if preview:o.hide_render=True;o.display_type='WIRE'
 else:parts.append(o)
 D['source_parts'].append({'name':o.name,'role':role,'parent_design_id':owner,'export_excluded':preview,'collision_contract':o['collision_contract'],'world_vertices':verts})
 return o
F=[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
def box(name,x0,x1,z0,z1,y0,y1,role='ivory_enamel',owner=AID):
 assert x1>x0 and z1>z0 and y1>y0,(name,x0,x1,z0,z1,y0,y1)
 return mesh(name,[(x,y,z)for y in[y0,y1]for x,z in[(x0,z0),(x1,z0),(x1,z1),(x0,z1)]],F,role,owner)
def prism(name,poly,y0,y1,role='ivory_enamel',owner=AID):
 n=len(poly);return mesh(name,[(x,y,z)for y in[y0,y1]for x,z in poly],[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n)for i in range(n)],role,owner)
def beam(name,a,b,w,h,role='ivory_enamel',owner=AID):
 a,b=Vector(a),Vector(b);t=(b-a).normalized();u=t.cross(Vector((0,1,0))).normalized()
 if u.length<.5:u=Vector((1,0,0))
 v=t.cross(u).normalized();vv=[tuple(p+u*q+v*r)for p in[a,b]for q,r in[(-w/2,-h/2),(w/2,-h/2),(w/2,h/2),(-w/2,h/2)]]
 return mesh(name,vv,F,role,owner)
def wall(name,a,b,y0,y1,width=.16,role='ivory_enamel',owner=AID):
 va,vb=Vector(a),Vector(b);delta=vb-va;t=delta.normalized();n=Vector((-t.y,t.x))*width/2
 return prism(name,[tuple(va+n),tuple(vb+n),tuple(vb-n),tuple(va-n)],y0,y1,role,owner)
def chamfer_rect(x0,x1,z0,z1,c):return[(x0+c,z0),(x1-c,z0),(x1,z0+c),(x1,z1-c),(x1-c,z1),(x0+c,z1),(x0,z1-c),(x0,z0+c)]
def tapered(name,rings,role):
 n=len(rings[0][1]);verts=[(x,y,z)for y,p in rings for x,z in p];faces=[tuple(range(n-1,-1,-1)),tuple(range((len(rings)-1)*n,len(rings)*n))]+[(j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i)for j in range(len(rings)-1)for i in range(n)];return mesh(name,verts,faces,role)
def marker(name,p,kind='interface',extra=None):
 o=bpy.data.objects.new('DATUM_'+name,None);bpy.context.collection.objects.link(o);o.location=(p[0],-p[2],p[1]);o.empty_display_size=.18;o['kind']=kind
 if extra:
  for k,v in extra.items():o[k]=v
 D['interfaces'].append({'name':o.name,'position_xyz':p,'kind':kind,**(extra or{})});return o

def fixture(name,x,y,z,width=.7,length=.7,profile='warm_pool',energy=.8,range=10):
 box(name+'_Recess',x-width/2-.09,x+width/2+.09,z-length/2-.09,z+length/2+.09,y,y+.18,'warm_walnut')
 box(name+'_Lens',x-width/2,x+width/2,z-length/2,z+length/2,y-.025,y,'lens')
 p=[x,y-.055,z];marker('light_'+name,p,'fixture',{'profile':profile});D['fixtures'].append({'name':'DATUM_light_'+name,'position_xyz':p,'direction':[0,-1,0],'suggested_range_m':range,'suggested_energy':energy,'suggested_spot_angle_degrees':75,'profile':profile,'physical_housing':name+'_Recess','physical_lens':name+'_Lens'})
# 1. Five compact retained-keel seats, with no passage through any old floor/home/court allocation.
for b in D['bearings']:
 n=b['name'];x0,x1=b['x'];z0,z1=b['z'];box('GP_KeelSeat_'+n,x0,x1,z0,z1,-3.2,-2.8,'champagne_metal')
 poly=chamfer_rect(x0+.10,x1-.10,z0+.12,z1-.12,.22)
 prism('GP_Bearing_'+n,poly,-2.8,43.76,'warm_stone')
 # Long stems are indispensable contacts, not isolated new spaces or additional deck allocations.
 marker('retained_contact_'+n,[(x0+x1)/2,-3.2,(z0+z1)/2],extra={'retained_object':'HUL_KeelPan'})
# Two side girders receive the basin pan and visible framed public architecture.
for x0,x1,label in[(-41.4,-40.4,'PortBasin'),(-21.6,-20.6,'StarboardBasin'),(-53.7,-52.2,'PortPerimeter')]:
 box('GP_Transfer_'+label,x0,x1,-465.2,-398.8,43.76,45.96,'warm_stone')
for z in[-453,-432,-405]:
 box('GP_WestSeatArm_'+str(z),-60.6,-40.4,z-.55,z+.55,43.76,45.96,'warm_stone')
for z in[-465.4,-404]:
 # Deep side member ends at the basin wall. It never cuts the low arrival/ramp pocket.
 box('GP_EastSeatArm_'+str(z),-21.6,-6,z-.55,z+.55,43.76,45.96,'warm_stone')
for z in[-451,-440,-429,-418,-408]:
 box('GP_UnderBasinRib_'+str(z),-40.4,-21.6,z-.24,z+.24,43.76,44.4,'champagne_metal')
for z in[-459,-401]:
 box('GP_EndTransfer_'+str(z),-53.7,-20.6,z-.55,z+.55,43.76,45.96,'warm_stone')
# Base receives compiler slab at Y44. No horizontal top at route height exported from the family.
# Pool pan and its four liner walls are the explicitly asset-owned basin.
box('GP_BasinPan',-40.4,-21.6,-457.4,-406.6,44.4,44.8,'aquatic_edge_tile')
for side,x0,x1 in[('Port',-40.4,-40),('Starboard',-22,-21.6)]:box('GP_BasinWall_'+side,x0,x1,-457.4,-406.6,44.8,46.2,'aquatic_edge_tile')
for label,z0,z1 in[('Fore',-457.4,-457),('Aft',-407,-406.6)]:box('GP_BasinWall_'+label,-40,-22,z0,z1,44.8,46.2,'aquatic_edge_tile')
# Coping stays outside the exact50x18 lane; discreet trench/drain reservation outside coping.
for x0,x1 in[(-40.75,-40.4),(-21.6,-21.25)]:box('GP_CopingLong',x0,x1,-457.7,-406.3,46.13,46.2,'warm_stone')
for z0,z1 in[(-457.7,-457.4),(-406.6,-406.3)]:box('GP_CopingEnd',-40.4,-21.6,z0,z1,46.13,46.2,'warm_stone')
for x0,x1 in[(-40.95,-40.79),(-21.21,-21.05)]:box('GP_DrainGrilleLong',x0,x1,-457.7,-406.3,46.12,46.195,'aquatic_dark_grip')
marker('water_trial',[-31,46.05,-432],extra={'simulation':'not_implemented','clear_lane_xz':[-40,-22,-457,-407]})
# 2. Sculpted west gallery piers and asymmetric entry piers. Broad capitals carry deep fascia.
piers=[(-50.7,-451,46.2,2.5,2.8),(-50.7,-433,46.2,2.5,2.8),(-50.7,-416,46.2,2.5,2.8),(-12.5,-440.5,44,1.6,2.0),(-9.25,-458,46.2,1.45,2.0),(-12.3,-404.9,46.2,1.8,1.4)]
for i,(x,z,y,w,d)in enumerate(piers):
 # Short solid bearing joins from transfer/base into the visible plinth, kept away from walking bands.
 if y>44:box('GP_PierPedestal_'+str(i),x-w/2,x+w/2,z-d/2,z+d/2,43.76,y,'warm_stone')
 p0=chamfer_rect(x-w*.62,x+w*.62,z-d*.62,z+d*.62,.32);p1=chamfer_rect(x-w*.45,x+w*.45,z-d*.45,z+d*.45,.28);p2=chamfer_rect(x-w*.57,x+w*.57,z-d*.57,z+d*.57,.32)
 tapered('GP_SculptedPier_'+str(i),[(y,p0),(y+.42,p0),(y+.90,p1),(50.7,p1),(51.08,p2),(52.26,p2)],'warm_stone')
 # Upper piers are visibly a continuation above the dry gallery, not extra storeys.
 tapered('GP_UpperPier_'+str(i),[(52.5,p2),(53.05,p1),(59.0,p1),(59.35,p2),(60.76,p2)],'ivory_enamel')
 for h in[y+.42,50.7,52.25,59.0]:
  prism('GP_PierCollar_'+str(i)+'_'+str(h),p2,h,h+.10,'champagne_metal')
# 3. Enclosing walls have real port/service cuts. No guessed exterior window.
# West wall: wet-service and market-service doors. Cassette-width opening permits real existing paired door pockets.
for lo,hi in[(44,46.2),(46.2,52.26),(52.26,52.5),(52.5,60.76)]:
 if lo in[46.2,52.5]:
  for z0,z1 in[(-466,-465.58),(-460.42,-398)]:box('GP_WestWall',-54,-53.72,z0,z1,lo,hi)
  box('GP_WestDoorHeader',-54,-53.72,-465.58,-460.42,lo+2.66,hi)
 else:box('GP_WestWallBand',-54,-53.72,-466,-398,lo,hi)
for lo,hi in[(44,52.26),(52.26,52.5),(52.5,60.76)]:
 if lo in[44,52.5]:
  for z0,z1 in[(-466,-435),(-429,-398)]:box('GP_EastWall',-8.20,-8,z0,z1,lo,hi)
  box('GP_PublicPortalHeader',-8.20,-8,-435,-429,lo+3.2,hi)
 else:box('GP_EastWallBand',-8.20,-8,-466,-398,lo,hi)
for z0,z1 in[(-466,-465.72),(-398.28,-398)]:box('GP_EndEnclosure',-54,-8,z0,z1,44,60.76)
# Deep curved/faceted west frontage: three nested orange public bays outside the3.4m market band.
for i,(za,zb)in enumerate([(-456.8,-444.6),(-443,-427.3),(-425.8,-409.0)]):
 outer=chamfer_rect(-53.6,-48.1,za,zb,.75)
 # Rear is recessed; arch-like shoulders frame real depth rather than an orange sticker on a box.
 wall('GP_MarketBayRear_'+str(i),(-53.42,za+.75),(-53.42,zb-.75),52.5,58.2,.16,'retail_terracotta_enamel')
 for z in[za,zb]:
  poly=[(-53.6,z),(-48.1,z),(-48.1,z+(.7 if z==za else-.7)),(-49.05,z+(1.5 if z==za else-1.5)),(-53.6,z+(1.5 if z==za else-1.5))]
  prism('GP_OrangeReveal_'+str(i)+'_'+str(z),poly,52.5,58.2,'retail_terracotta_enamel')
 prism('GP_BayCanopy_'+str(i),outer,57.95,58.25,'ivory_enamel')
 for z in[za+3,(za+zb)/2,zb-3]:fixture('GP_MarketBayFixture_'+str(i)+'_'+str(z),-50.6,57.94,z,.9,.9,'market_warm',.75,7.5)
 # Nested planting trough is an architectural pocket, not a finished garden asset or retail stock.
 for z in[za+2.1,zb-2.1]:
  poly=chamfer_rect(-50.8,-48.15,z-.7,z+.7,.35);prism('GP_PlantPocket_'+str(i)+'_'+str(z),poly,52.5,53.15,'warm_stone');prism('GP_PlantSoil_'+str(i)+'_'+str(z),chamfer_rect(-50.58,-48.37,z-.48,z+.48,.23),53.15,53.20,'botanical_soil')
# 4. Shaped continuous opening edge: deep layered fascia, full-height environmental glass, dry circuit.
main=D['opening']['main_boundary'];segments=[]
for a,b in zip(main,main[1:]+main[:1]):
 if a[0]==b[0]==-18:
  for lo,hi in[(-458,-428),(-406.9,-406)]:segments.append(([-18,lo],[-18,hi]))
 else:segments.append((a,b))
# Upper link enclosures join the wet volume. The dry bypass lies east ofX-11.1.
segments += [([-18,-428],[-11.1,-428]),([-11.1,-428],[-11.1,-406.9]),([-11.1,-406.9],[-18,-406.9])]
doors=[]
for z in[-428,-406.9]:doors.append({'name':'wet_market_'+('stair'if z==-428 else'lift'),'root_xyz':[-14.55,52.5,z],'yaw_radians':0,'clear_width':2.4,'cassette_width':5.16,'parent':'AST-DOR-002','export':'AST-DOR-002_wide.glb','floor_y':52.5,'normal_axis':'z','opening_centre':-14.55})
for level in[46.2,52.5]:doors.append({'name':'service_'+str(level),'root_xyz':[-53.86,level,-463],'yaw_radians':math.pi/2,'clear_width':2.4,'cassette_width':5.16,'parent':'AST-DOR-002','export':'AST-DOR-002_wide.glb','floor_y':level,'normal_axis':'x','opening_centre':-463})
for i,(a,b)in enumerate(segments):
 # Fascia sits below the compiler slab and remains visibly deep in wet views.
 wall('GP_GalleryFasciaBody_'+str(i),a,b,51.08,52.26,.48,'ivory_enamel')
 wall('GP_GalleryFasciaLowerReturn_'+str(i),a,b,50.95,51.12,.72,'warm_stone')
 wall('GP_GalleryEdgeRibbon_'+str(i),a,b,52.20,52.5,.20,'champagne_metal')
 isdoor=a[1]==b[1]and a[1]in[-428,-406.9]
 if isdoor:
  z=a[1]
  for x0,x1 in[(-18,-17.13),(-11.97,-11.1)]:wall('GP_WetSealDoorSide', [x0,z],[x1,z],52.5,60.76,.12,'glass')
  wall('GP_WetSealDoorTransom',[-17.13,z],[-11.97,z],55.16,60.76,.12,'glass')
  wall('GP_WetSealDoorHeader',[-17.13,z],[-11.97,z],55.16,55.32,.26,'champagne_metal')
 else:
  wall('GP_WetDryGlazing_'+str(i),a,b,52.5,60.76,.10,'glass')
  wall('GP_GlazingBase_'+str(i),a,b,52.5,52.70,.14,'warm_stone')
 # Continuous ceiling seal, large mullions at segment ends plus every~4m.
 wall('GP_GlazingHeadSeal_'+str(i),a,b,60.54,60.76,.20,'ivory_enamel')
 length=(Vector(b)-Vector(a)).length
 for j in range(math.ceil(length/4)+1):
  p=Vector(a).lerp(Vector(b),j/math.ceil(length/4))
  if isdoor and -17.13<p.x<-11.97:continue
  box('GP_GlazingMullion',p.x-.055,p.x+.055,p.y-.055,p.y+.055,52.5,60.76,'champagne_metal')
# Framed overhead composition. Three broad transverse sculpted ribs meet perimeter/upper-pier system.
for z in[-451,-433,-416]:
 poly=[(-53.72,z-.45),(-48.5,z-.45),(-44,z-.22),(-18,z-.22),(-12,z-.45),(-8.2,z-.45),(-8.2,z+.45),(-12,z+.45),(-18,z+.22),(-44,z+.22),(-48.5,z+.45),(-53.72,z+.45)]
 prism('GP_RoofRib_'+str(z),poly,59.16,60.76,'ivory_enamel')
 # Central fitted luminous panels are actual objects fixed to the rib, not a fictitious skylight.
 for x in[-36,-26]:fixture('GP_VaultLamp_'+str(z)+'_'+str(x),x,59.15,z,2.4,1.0,'pool_vault',1.1,16)
for x in[-50.7,-12.5]:
 box('GP_LongCeilingReturn_'+str(x),x-.32,x+.32,-465.72,-398.28,59.8,60.76,'warm_stone')
for x in[-46.3,-16.4]:
 for z in[-456,-442,-430,-405]:
  # Fixtures are mounted into gallery slab soffit or its shaped return.
  fixture('GP_WetGalleryLamp_'+str(x)+'_'+str(z),x,52.10,z,.65,.9,'wet_terrace',.85,10)
# 5. Ceremonial fourteen-riser arrival and genuine2.4m clear switchback ramp.
for i in range(13):
 x1=-11-i*.4;x0=x1-.4;top=44+(i+1)*2.2/14
 box('GP_CeremonialTread_'+str(i),x0,x1,-434,-430,44,top,'warm_stone','AST-CIR-001')
box('GP_CeremonialFinalRiser',-16.22,-16.18,-434,-430,44+13*2.2/14,46.2,'warm_stone','AST-CIR-001')
# Sloping structural ramp pans, with all rail projections outside declared clear bands.
for label,x0,x1,z0,z1,y0,y1 in[('Lower',-13.2,-10.8,-449,-462.2,44,45.1),('Upper',-16.4,-14,-462.2,-449,45.1,46.2)]:
 vv=[(x,y,z)for y,z in[(y0-.20,z0),(y1-.20,z1),(y0,z0),(y1,z1)]for x in[x0-.14,x1+.14]]
 mesh('GP_RampPan_'+label,vv,[(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)],'warm_stone')
 for x in[x0-.085,x1+.085]:
  beam('GP_RampRail_'+label,(x,y0+1.08,z0),(x,y1+1.08,z1),.075,.075,'warm_walnut')
  beam('GP_RampKick_'+label,(x,y0+.10,z0),(x,y1+.10,z1),.08,.18,'champagne_metal')
  for j in range(6):
   t=j/5;z=z0+(z1-z0)*t;y=y0+(y1-y0)*t;box('GP_RampPost_'+label,x-.035,x+.035,z-.035,z+.035,y,y+1.08,'champagne_metal')
box('GP_RampReturnLanding',-16.56,-10.64,-464.78,-462.2,44.90,45.1,'warm_stone')
for a,b in[((-16.5,-464.7),(-10.7,-464.7)),((-16.5,-464.7),(-16.5,-462.2)),((-10.7,-464.7),(-10.7,-462.2))]:
 wall('GP_RampReturnGuard',a,b,45.1,46.18,.10,'glass');wall('GP_RampReturnCap',a,b,46.15,46.23,.13,'warm_walnut')
# Solid sloping pans are visibly seated on low plenum pedestals, with no walking route underneath.
for x0,x1 in[(-13.2,-10.8),(-16.4,-14)]:
 for z in[-452,-456,-460]:
  yy=44+(-449-z)/12 if x0==-13.2 else 45.1+(z+462.2)/12
  if yy-.20>44:box('GP_RampUnderseat',x0,x1,z-.16,z+.16,44,yy-.20,'ivory_enamel')
# Guard raised terrace edges around arrival/ramp pockets; no guard across landing/stair connections.
for a,b in[((-18,-445.6),(-10.8,-445.6)),((-18,-428.2),(-8.2,-428.2)),((-18,-445.6),(-18,-434)),((-18,-430),(-18,-428.2)),((-18,-446.3),(-18,-445.6))]:
 wall('GP_RaisedEdgeFascia',a,b,44,46.2,.12,'ivory_enamel');wall('GP_RaisedEdgeGlazing',a,b,46.2,47.24,.05,'glass');wall('GP_RaisedEdgeRail',a,b,47.24,47.32,.10,'warm_walnut')
# Complete guards at all exposed ramp-pocket and upper-link floor edges.
for a,b in[((-18.06,-464.93),(-18.06,-449.06)),((-18.06,-464.93),(-10.46,-464.93)),((-10.46,-464.93),(-10.46,-449.06)),((-18.06,-446.55),(-18.06,-445.6))]:
 wall('GP_RampPocketGuard',a,b,46.2,47.25,.07,'glass');wall('GP_RampPocketCap',a,b,47.24,47.32,.12,'warm_walnut')
for a,b in[((-18,-425.5),(-14,-425.5)),((-14,-425.5),(-14,-423.5)),((-18,-428),(-18,-425.5)),((-13.5,-415.7),(-11.1,-415.7)),((-13.5,-415.7),(-13.5,-414.6)),((-18,-410.2),(-18,-406.9))]:
 wall('GP_UpperWetLinkGuard',a,b,52.5,53.55,.07,'glass');wall('GP_UpperWetLinkRail',a,b,53.54,53.62,.12,'warm_walnut')
# Explicit source derivative ofCIR001:36risers,6.3m,2.6m clear flights,17goings per flight.
for flight,(x0,x1)in enumerate([(-17.1,-14.5),(-13.9,-11.3)]):
 start=-423.5 if flight==0 else-418.06;sign=1 if flight==0 else-1;y0=46.2 if flight==0 else 49.35
 # Each tread is connected to a continuous fitted stringer. Final eighteenth riser lands directly on landing.
 for i in range(17):
  z0=start+sign*i*.32;z1=start+sign*(i+1)*.32;lo,hi=sorted([z0,z1]);yt=y0+(i+1)*.175
  box('CIR630_Tread_%s_%s'%(flight,i),x0,x1,lo,hi,yt-.22,yt,'warm_stone','AST-CIR-001')
  box('CIR630_Nose_%s_%s'%(flight,i),x0+.08,x1-.08,lo if sign>0 else hi-.035,lo+.035 if sign>0 else hi,yt-.017,yt+.001,'dark_rubber','AST-CIR-001')
 for x in[x0-.095,x1+.095]:
  beam('CIR630_Stringer',(x,y0-.13,start),(x,y0+3.15-.13,start+sign*5.44),.23,.32,'ivory_enamel','AST-CIR-001')
  beam('CIR630_Handrail',(x,y0+1.08,start),(x,y0+3.15+1.08,start+sign*5.44),.10,.10,'warm_walnut','AST-CIR-001')
  for i in range(7):
   t=i/6;z=start+sign*t*5.44;y=y0+t*3.15;box('CIR630_Post',x-.035,x+.035,z-.035,z+.035,y-.10,y+1.08,'champagne_metal','AST-CIR-001')
 # Last full riser closes the landing face, no missing vertical step.
 zend=start+sign*5.44;box('CIR630_FinalRiser',x0,x1,zend-.018,zend+.018,y0+2.975,y0+3.15,'warm_stone','AST-CIR-001')
box('CIR630_MidLanding',-17.2,-11.2,-418.06,-416.06,49.03,49.35,'warm_stone','AST-CIR-001')
for a,b in[((-17.25,-416.01),(-11.15,-416.01)),((-17.25,-418.06),(-17.25,-416.01)),((-11.15,-418.06),(-11.15,-416.01))]:
 wall('CIR630_MidGuard',a,b,49.35,50.40,.06,'glass','AST-CIR-001');wall('CIR630_MidRail',a,b,50.39,50.47,.11,'warm_walnut','AST-CIR-001')
# Stair seating studs fit completely below the flights, inside the authored local-link envelope.
for x in[-17.17,-11.23]:box('CIR630_MidSupport',x-.06,x+.06,-416.28,-416.12,46.2,49.03,'champagne_metal','AST-CIR-001')
marker('local_stair_lower',[-15.8,46.2,-424.4]);marker('local_stair_upper',[-12.6,52.5,-424.4]);marker('local_stair_mid',[-14.25,49.35,-417.0])
# 6. Local existing-family lift enclosure. East-facing aperture agrees with actual unchanged controller.
for z0,z1 in[(-414.6,-414.44),(-410.36,-410.2)]:box('GP_LocalLiftSide',-17.52,-13.24,z0,z1,45.96,55.6,'ivory_enamel','AST-CIR-004')
box('GP_LocalLiftRear',-17.52,-17.36,-414.44,-410.36,45.96,55.6,'ivory_enamel','AST-CIR-004')
for z0,z1 in[(-414.44,-414.3),(-410.5,-410.36)]:box('GP_LocalLiftJamb',-13.4,-13.24,z0,z1,45.96,55.6,'ivory_enamel','AST-CIR-004')
for y0,y1 in[(45.96,46.2),(49.05,52.5),(55.35,55.6)]:box('GP_LocalLiftFrontSpandrel',-13.4,-13.24,-414.3,-410.5,y0,y1,'ivory_enamel','AST-CIR-004')
box('GP_LocalLiftPit',-17.36,-13.4,-414.44,-410.36,45.96,46.0,'champagne_metal','AST-CIR-004')
box('GP_LocalLiftCap',-17.52,-13.24,-414.6,-410.2,55.6,55.74,'ivory_enamel','AST-CIR-004')
for y in[46.2,52.5]:
 box('GP_LocalLiftHeader',-13.24,-13.10,-414.0,-410.8,y+2.93,y+3.06,'warm_walnut','AST-CIR-004')
 marker('local_lift_stop_'+str(y),[-13.48,y,-412.4],extra={'parent':'AST-CIR-003','dynamic_gate':'separate_runtime_owner'})
marker('local_lift_root',[-15.4,46.2,-412.4],extra={'yaw_radians':math.pi,'gate_origin_xz':[-1.8,0],'relative_stops':[0,6.3]})
# 7. Screened service vestibules. Two pockets for clean/damp service sit outside dogleg turn envelope.
for y in[46.2,52.5]:
 for a,b in[((-54,-465.8),(-48,-465.8)),((-54,-456.8),(-48,-456.8)),((-48,-465.8),(-48,-459.8)),((-48,-457.4),(-48,-456.8))]:wall('GP_ServiceVestibuleWall',a,b,y,y+3.2,.16,'ivory_enamel')
 box('GP_ServicePrivacyScreen',-51.2,-51.0,-465.8,-459.5,y,y+3.2,'retail_terracotta_enamel')
 box('GP_ServiceVestibuleCeiling',-54,-48,-465.8,-456.8,y+3.2,y+3.34,'ivory_enamel')
 for label,z0,z1 in[('DrySupply',-459.5,-458.3),('TowelReturn',-457.9,-457.0)]:
  box('GP_ServiceNicheBack_'+label,-53.85,-53.73,z0,z1,y+.3,y+2.5,'warm_walnut');marker(label+'_'+str(y),[-52.9,y,-(abs(z0)+abs(z1))/2],extra={'status':'recess_reserved_no_stock'})
 fixture('GP_ServiceVestibule_'+str(y),-51.5,y+3.04,-458.6,.65,.7,'staff_work',.8,6)
# Supported service mouths, core tongues and ramp interface markers.
for y in[44,52.5]:marker('public_portal_'+str(y),[-7.9,y,-432],extra={'clear_width_m':6,'clear_height_m':3.2})
for i,p in enumerate(D['accessible_ramp']['route_xyz']):marker('ramp_route_'+str(i),p,'route')
D['staff']['adopted_screen_rect']=[-51.2,-51.0,-465.8,-459.5]
D['staff']['adopted_route_xz']=[[-23.08,-490],[-21,-490],[-21,-500],[-57,-500],[-57,-463],[-52.5,-463],[-52.5,-458.15],[-48,-458.15]]
D['door_fittings']=doors
for door in doors:marker(door['name'],door['root_xyz'],'door_fitting',{k:door[k]for k in['parent','export','yaw_radians','clear_width','cassette_width']})
# Common compiler floors are review-only transparent ownership previews, never GLB mesh/collision.
for f in D['floor_regions']:
 verts=[];faces=[]
 for t in f['triangles']:
  offset=len(verts);verts += [(x,f['floor_y'],z)for x,z in t];faces.append(tuple(range(offset,offset+3)))
 mesh('PREVIEW_ONLY_'+f['id'],verts,faces,'warm_stone',preview=True)
# Source preview uses the actual retained door geometry, preserving all articulation. Parent instances same asset.
for door in doors:
 with bpy.data.libraries.load(str(C/'assets/guest_entry_door/source/AST-DOR-002_wide.blend'),link=False)as(a,b):b.objects=list(a.objects)
 root=bpy.data.objects.new('PREVIEW_ONLY_DoorFitting_'+door['name'],None);bpy.context.collection.objects.link(root);p=door['root_xyz'];root.location=(p[0],-p[2],p[1]);root.rotation_euler.z=door['yaw_radians'];root['export_excluded']=True
 loaded=set(b.objects)
 for o in b.objects:
  bpy.context.collection.objects.link(o);o.name='PREVIEW_ONLY_'+door['name']+'_'+o.name;o['export_excluded']=True
  if o.parent not in loaded:o.parent=root
  o.hide_render=True
# Capture editable source before material+spatial batching. Source objects stay independently authorable.
bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1;bpy.context.preferences.filepaths.save_version=0
D['stair_collision_contacts']={'convention':'Same existing CIR001 ramp-prism flight contacts as primary_atrium_core.gd; visual tread batches receive no collision. Separate guards stay static.','thickness_m':.24,'quads_xyz':[[[-11,44,-434],[-11,44,-430],[-16.2,46.2,-430],[-16.2,46.2,-434]],[[-17.1,46.2,-423.5],[-14.5,46.2,-423.5],[-14.5,49.35,-418.06],[-17.1,49.35,-418.06]],[[-13.9,52.5,-423.5],[-11.3,52.5,-423.5],[-11.3,49.35,-418.06],[-13.9,49.35,-418.06]]]}
D['actual_floor_preview_count']=len(D['floor_regions']);D['builder']='source/build_connected_section.py'
D['market']['adopted_dry_loop_centreline_xz']=[[-15.5,-432],[-15.5,-463.1],[-45.9,-463.1],[-45.9,-400.9],[-9.65,-400.9],[-9.65,-429.5],[-15.5,-429.5],[-15.5,-432]]
D['market']['loop_fit_note']='Front cross-connection moved1.5m away from closed stair-door cassette planeZ-428; dry bypass remainsX-10.85..-8.45.'
(R/'source/connected_contract.json').write_text(json.dumps(D,indent=2)+'\n')
bpy.ops.file.pack_all();src=R/'source'/f'{AID}.blend';out=R/'exports'/f'{AID}.glb';bpy.ops.wm.save_as_mainfile(filepath=str(src))
tri=0
for o in parts:o.data.calc_loop_triangles();tri+=len(o.data.loop_triangles)
for o in list(bpy.context.scene.objects):
 if o.get('export_excluded',False):bpy.data.objects.remove(o,do_unlink=True)
batches={}
for o in parts:
 vv=[v.co for v in o.data.vertices];x=sum(v.x for v in vv)/len(vv);z=-sum(v.y for v in vv)/len(vv);y=sum(v.z for v in vv)/len(vv)
 # Spatial material batches: no hull/remesh, UV layers remain the same name.
 key=(math.floor(x/20),math.floor(z/20),math.floor(y/8.5),o.data.materials[0].name,o['collision_contract']);batches.setdefault(key,[]).append(o)
for key,objects in sorted(batches.items()):
 bpy.ops.object.select_all(action='DESELECT')
 for o in objects:o.select_set(True)
 bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();o=bpy.context.object;o.name='GPM_CELL_%d_%d_%d_%s_%s'%key;o['source_piece_count']=len(objects);o['batching']='material/spatial join only; no weld/remesh/convexification'
bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',export_yup=True,export_extras=True)
manifest={'catalogue_id':AID,'family':'grand_pool_orchard_section','name':'Connected Grand Pool and Orchard Market architectural section','source':'source/'+src.name,'export':'exports/'+out.name,'source_sha256':sha(src),'export_sha256':sha(out),'contract_sha256':sha(R/'source/connected_contract.json'),'triangles':tri,'editable_part_count':len(parts),'runtime_mesh_batches':len(batches),'fixture_count':len(D['fixtures']),'floor_preview_count':len(D['floor_regions']),'exported_common_floor_count':0,'status':'Built editable source; final QA and runtime integration pending'}
(R/(AID+'.manifest.json')).write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(manifest))
