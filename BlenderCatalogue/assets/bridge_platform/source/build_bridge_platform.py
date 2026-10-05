"""Editable stage-one bridge platform and enclosed public bypass. No authored floor slabs.
World mapping: Blender=(Godot X,-Godot Z,Godot Y). All new work isolated in this family.
"""
from pathlib import Path
import bpy,bmesh,json,math,sys,hashlib
from mathutils import Vector
R=Path(__file__).resolve().parents[1];C=R.parents[1];AID='AST-CMD-003';FAMILY='bridge_platform'
manifest=json.loads((C/'catalogue_manifest.json').read_text())
assert all(a['catalogue_id']!=AID or a['family']==FAMILY for a in manifest['assets'])
D=json.loads((R/'source/section_contract.json').read_text())
for key in ['light_markers','windows','guards']:D[key]=[]
D['support']['hanger_assemblies']=[];D['support']['member_assemblies']=[]
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
sys.path.insert(0,str(C/'standards'));import staff_materials,materials
mats=staff_materials.materials();mats.update(materials.materials())
for m in mats.values():
 for n in m.node_tree.nodes:
  if n.type=='TEX_IMAGE':n.interpolation='Closest'
opal=mats['staff_opal'].copy();opal.name='ASTRAEA_bridge_warm_opal';opal['astraea_material_role']='bridge_warm_opal';bs=next(n for n in opal.node_tree.nodes if n.type=='BSDF_PRINCIPLED');bs.inputs['Emission Color'].default_value=(1,.78,.50,1);bs.inputs['Emission Strength'].default_value=.65;mats['bridge_warm_opal']=opal
m=bpy.data.materials.new('ASTRAEA_bridge_gallery_glass');m.use_nodes=True;m['meters_per_tile_uv']=[1,1];m['astraea_material_role']='bridge_gallery_glass';m.diffuse_color=(.23,.42,.44,.28);bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.23,.42,.44,1);bs.inputs['Roughness'].default_value=.22;bs.inputs['Metallic'].default_value=.08;bs.inputs['Alpha'].default_value=.28;m.surface_render_method='DITHERED';mats['bridge_gallery_glass']=m
parts=[];records=[]
FACES=[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
def segments(a,b,cell=8):
 cuts=[a]+[v for v in range(math.floor(a/cell)*cell,math.ceil(b/cell)*cell+1,cell)if a+1e-7<v<b-1e-7]+[b];return list(zip(cuts,cuts[1:]))
def mesh(name,verts,faces,role,group):
 me=bpy.data.meshes.new(name);me.from_pydata([(x,-z,y)for x,y,z in verts],[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
 ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);me.materials.append(mats[role]);ob['catalogue_id']=AID;ob['collision_contract']='concave_static_surface';ob['group']=group;ob['assembly']=name
 lo=[min(v[k]for v in verts)for k in range(3)];hi=[max(v[k]for v in verts)for k in range(3)]
 for k,axis in enumerate('xyz'):ob['cell_'+axis]=math.floor((lo[k]+hi[k])/16)
 uv=me.uv_layers.new(name='MetreScaled');scale=mats[role]['meters_per_tile_uv']
 for f in me.polygons:
  n=f.normal.normalized();u=(Vector((1,0,0))-n*n.x).normalized()if abs(n.z)>.7 else Vector((-n.y,n.x,0)).normalized();v=n.cross(u)
  for li in f.loop_indices:
   q=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=tuple(round(value*8192)/8192 for value in(q.dot(u)/scale[0],q.dot(v)/scale[1]))
 parts.append(ob);records.append({'name':ob.name,'assembly':name,'world_aabb':[lo[0],hi[0],lo[1],hi[1],lo[2],hi[2]],'vertices_world':verts,'role':role,'group':group});return ob

def box(name,x0,x1,y0,y1,z0,z1,role='staff_bluegrey_paint',group='shell'):
 assert x1>x0 and y1>y0 and z1>z0,(name,x0,x1,y0,y1,z0,z1)
 for a,b in segments(x0,x1):
  for c,d in segments(y0,y1):
   for e,f in segments(z0,z1):mesh(name,[(x,y,z)for y in[c,d]for x,z in[(a,e),(b,e),(b,f),(a,f)]],FACES,role,group)

def bar(name,a,b,width,y0,y1,role='staff_bluegrey_paint',group='platform_support'):
 # Plan-oriented closed rectangular bar, bounded subdivision, joints remain exactly continuous.
 dx=b[0]-a[0];dz=b[1]-a[1];length=math.hypot(dx,dz);nx=-dz/length*width/2;nz=dx/length*width/2;n=max(1,math.ceil(length/7.5))
 for i in range(n):
  p=[a[0]+dx*i/n,a[1]+dz*i/n];q=[a[0]+dx*(i+1)/n,a[1]+dz*(i+1)/n]
  ring=[(p[0]+nx,p[1]+nz),(q[0]+nx,q[1]+nz),(q[0]-nx,q[1]-nz),(p[0]-nx,p[1]-nz)]
  mesh(name,[(x,y,z)for y in[y0,y1]for x,z in ring],FACES,role,group)

def marker(name,p,extras=None):
 ob=bpy.data.objects.new(name,None);bpy.context.collection.objects.link(ob);ob.location=(p[0],-p[2],p[1]);ob.empty_display_size=.12
 for k,v in (extras or {}).items():ob[k]=v
 return ob

def girder_x(name,x0,x1,z,y0=111.1,y1=113.88,depth=.36,group='transfer'):
 box(name+'_Web',x0,x1,y0,y1,z-depth/2,z+depth/2,'staff_bluegrey_paint',group)
 for yy in[y0,y1-.16]:box(name+'_Flange',x0,x1,yy,yy+.16,max(-181,z-.46),min(-80,z+.46),'staff_zinc',group)
 D['support']['member_assemblies'].append({'name':name,'axis':'x','span':[x0,x1],'z':z,'y':[y0,y1],'group':group})

def girder_z(name,x,z0,z1,y0=111.1,y1=113.88,width=.32,group='transfer'):
 box(name+'_Web',x-width/2,x+width/2,y0,y1,z0,z1,'staff_bluegrey_paint',group)
 for yy in[y0,y1-.16]:box(name+'_Flange',max(-48,x-.30),x+.30,yy,yy+.16,z0,z1,'staff_zinc',group)
 D['support']['member_assemblies'].append({'name':name,'axis':'z','x':x,'span':[z0,z1],'y':[y0,y1],'group':group})

# The only keel-reaching parts use the four audited exact footprints.
levels=[-3.2,0,6,12,16.5,21,27,35.5,44,52.5,61,69.5,78,84,88.5,93,97.5,102,106.5,111,114]
for index,(x,z)in enumerate(D['support']['pier_centres_xz']):
 name='BRP_Pier_%02d'%(index+1)
 for ya,yb in zip(levels,levels[1:]):
  box(name+'_Web',x-.32,x+.32,ya,yb,z-.52,z+.52,'staff_bluegrey_paint','pier')
  for sx in[-1,1]:box(name+'_Chord',*sorted([x+sx*.3,x+sx*.4]),ya,yb,z-.60,z+.60,'staff_zinc','pier')
  box(name+'_Collar',x-.4,x+.4,ya,min(ya+.2,yb),z-.6,z+.6,'staff_bluegrey_paint','pier')
 marker('DATUM_bridge_pier_%02d_base'%(index+1),[x,-3.2,z]);marker('DATUM_bridge_pier_%02d_head'%(index+1),[x,114,z])
 box(name+'_HeadBearing',x-.4,x+.4,111,113.99,z-.6,z+.6,'staff_zinc','transfer')
# Both transverse frames extend positively past all heads and carry the port cantilever.
for z in[-168,-86]:girder_x('BRP_PrimaryTransverse_Z%s'%abs(z),-47.85,35.85,z)
for x in[-32,32]:girder_z('BRP_PrimaryLongitudinal_X%s'%x,x,-180.8,-80.0)
for x in[-47.8,-40.2]:girder_z('BRP_BypassRoofEdge_X%s'%str(x).replace('.','p'),x,-180.8,-80.0,111.05,113.92,.28,'bypass_transfer')
# Secondary frame is an explicit positive-contact network, not reliance on the original spine.
bridge_stations=[-171.7,-160,-148,-136,-124,-118.3]
for z in bridge_stations:girder_x('BRP_BridgeSecondary_Z%s'%str(abs(z)).replace('.','p'),-35.9,35.9,z,111.12,112.05,.24)
# Short outer roof cantilevers stop at the bypass enclosure. Every one crosses the -32 primary.
bypass_stations=[-180.7,-174,-168,-156,-144,-132,-120,-108,-96,-86,-80.3]
for z in bypass_stations:girder_x('BRP_BypassCantilever_Z%s'%str(abs(z)).replace('.','p'),-48,-31.7,z,111.16,112.15,.24,'bypass_transfer')
# The transverse fore gallery has supported roof members across to its east return.
for z in[-180.7,-173.3]:girder_x('BRP_ForeGalleryRoof_Z%s'%str(abs(z)).replace('.','p'),-47.85,4.18,z,111.12,112.1,.24,'bypass_transfer')
# Additional roof lines support inner platform hangers on both sides while retaining an open 8m spine.
for x in[-4.5,4.5]:girder_z('BRP_InnerWingRoof_X%s'%str(x).replace('.','p'),x,-171.9,-118.1,111.12,112.05,.24)
# Roof purlins bridge from upper beam flanges to the weather skin, with positive seats.
for z in bypass_stations:box('BRP_BypassRoofPurlin',-48,-40,113.80,114.22,z-.14,z+.14,'staff_bluegrey_paint','roof_support')
for x in[-47.7,-40.2,-32,-24,-16,-8,3.85]:box('BRP_ForeRoofPurlin',x-.14,x+.14,111.92,114.22,-181,-173,'staff_bluegrey_paint','roof_support')

# Suspended bridge wings: separate inner/outer edge girders, complete boundary girders and a floor grid.
def outer_x(z):return 30+(z+172)*.5 if z<-160 else 36
for s in[-1,1]:
 side='Port'if s<0 else'Starboard'
 for z in bridge_stations:
  ox=s*(outer_x(z)-.30);ix=s*4.50
  a,b=sorted([ix,ox]);girder_x('BRP_'+side+'_FloorGrid_Z%s'%str(abs(z)).replace('.','p'),a-.15,b+.15,z,105.82,106.28,.24,'platform_support')
  for edge,x in[('Inner',ix),('Outer',ox)]:
   tag='BRP_'+side+'_'+edge+'_Hanger_Z%s'%str(abs(z)).replace('.','p');box(tag,x-.11,x+.11,105.98,111.85,z-.15,z+.15,'staff_zinc','hanger');D['support']['hanger_assemblies'].append({'name':tag,'kind':'bridge_wing','edge':edge,'x':x,'z':z,'y':[105.98,111.85]})
 # Explicit perimeter chain is inboard of the parent boundary; widths stay below the walk surface.
 path=[(s*4.12,-171.7),(s*29.7,-171.7),(s*35.7,-159.7),(s*35.7,-118.3),(s*4.12,-118.3)]
 for i,(a,b)in enumerate(zip(path,path[1:])):bar('BRP_'+side+'_Perimeter_%02d'%i,a,b,.48,105.80,106.28)
 girder_z('BRP_'+side+'_InnerFloorEdge',s*4.5,-171.8,-118.2,105.82,106.28,.26,'platform_support')
 for x in[12,20,28]:girder_z('BRP_'+side+'_FloorStringer_%s'%x,s*x,-171.7,-118.3,105.9,106.28,.18,'platform_support')
 # Solid backed guards around every exterior open edge, leaving the original centreline mouth clear.
 guard_path=[(s*4,-171.7)]+path[1:-1]+[(s*4,-118.3)]
 for end_z in[-171.7,-118.3]:box('BRP_'+side+'_GuardMouthShoe',*sorted([s*4,s*4.60]),106.265,106.47,end_z-.24,end_z+.24,'staff_zinc','platform_support_shallow')
 for i,(a,b)in enumerate(zip(guard_path,guard_path[1:])):
  bar('BRP_'+side+'_GuardBack_%02d'%i,a,b,.16,106.45,107.70,'staff_bluegrey_paint','guard')
  bar('BRP_'+side+'_GuardCap_%02d'%i,a,b,.22,107.68,107.82,'staff_zinc','guard')
  bar('BRP_'+side+'_GuardToe_%02d'%i,a,b,.24,106.28,106.58,'staff_zinc','guard')
  D['guards'].append({'id':side+'_%02d'%i,'a_xz':a,'b_xz':b,'backed':True,'height_above_floor':1.32,'positive_support':'matching BRP_'+side+'_Perimeter_%02d'%i,'connection_mouth_policy':'No guard along inner X±4.5 line; wings open to centreline. Fore/aft mouths X±4 remain fully clear.'})
 # Backed terminal returns stop a sidestep behind the deliberately inboard safety guard.
 for end,z0,z1 in[('Fore',-172,-171.68),('Aft',-118.32,-118)]:
  box('BRP_'+side+'_'+end+'_GuardMouthReturnBack',*sorted([s*4,s*4.16]),106.45,107.70,z0,z1,'staff_bluegrey_paint','guard')
  box('BRP_'+side+'_'+end+'_GuardMouthReturnCap',*sorted([s*4,s*4.22]),107.68,107.82,z0,z1,'staff_zinc','guard')
  box('BRP_'+side+'_'+end+'_GuardMouthReturnToe',*sorted([s*4,s*4.24]),106.28,106.58,z0,z1,'staff_zinc','guard')
  box('BRP_'+side+'_'+end+'_GuardMouthReturnShoe',*sorted([s*4,s*4.60]),106.265,106.47,z0,z1,'staff_zinc','platform_support_shallow')
  D['guards'].append({'id':side+'_'+end+'_terminal_return','world_aabb':sorted([s*4,s*4.24])+[106.28,107.82,z0,z1],'backed':True,'height_above_floor':1.32,'positive_support':'Slab-height return shoe joined to original mouth shoe and perimeter girder','purpose':'Close the narrow outside guard strip at actual platform Z boundary without intrusion into X±4 spine'})


# Bypass floor edge system hangs entirely above D17, even over the lower theatre void.
for x in[-47.8,-40.2]:girder_z('BRP_BypassFloorEdge_X%s'%str(x).replace('.','p'),x,-180.8,-80.0,105.80,106.28,.26,'platform_support')
for z in[-180.7,-173.3]:girder_x('BRP_ForeGalleryFloorEdge_Z%s'%str(abs(z)).replace('.','p'),-47.85,-4.1,z,105.8,106.28,.24,'platform_support')
for z in bypass_stations:
 girder_x('BRP_BypassFloorGrid_Z%s'%str(abs(z)).replace('.','p'),-47.9,-40.1,z,105.87,106.28,.22,'platform_support')
 for edge,x in[('Outer',-47.8),('Inner',-40.2)]:
  # At the L turn, inner edge below the former corner is omitted so a full turning square remains clear.
  if edge=='Inner'and z<-173:continue
  tag='BRP_Bypass_'+edge+'_Hanger_Z%s'%str(abs(z)).replace('.','p');box(tag,x-.12,x+.12,105.96,111.9,z-.14,z+.14,'champagne_metal','hanger');D['support']['hanger_assemblies'].append({'name':tag,'kind':'bypass','edge':edge,'x':x,'z':z,'y':[105.96,111.9]})
for x in[-32,-24,-16,-8,4.08]:
 
 if x<0:girder_z('BRP_ForeGalleryFloorGrid_X%s'%str(x).replace('.','p'),x,-180.8,-173.2,105.88,106.28,.20,'platform_support')
 else:box('BRP_EastReturnSlabHeightClosure',3.74,4.18,106.265,106.49,-181,-173,'staff_zinc','platform_support_shallow')
 for edge,z in[('Fore',-180.7),('Aft',-173.3)]:
  # All eastern hanger geometry stays beyond X=4.0; spine remains exactly open.
  tag='BRP_ForeGallery_'+edge+'_Hanger_X%s'%str(x).replace('.','p');hw=.08 if x>0 else.12;box(tag,x-hw,x+hw,106.265 if x>0 else 105.96,111.90,z-.14,z+.14,'champagne_metal','hanger');D['support']['hanger_assemblies'].append({'name':tag,'kind':'fore_gallery','edge':edge,'x':x,'z':z,'y':[106.265 if x>0 else 105.96,111.9]})
# Shallow slab-height saddles span the spine at fore junctions without descending into D17 headroom.
# These are narrow structural strips, not a duplicate floor or standing-height threshold.
for z in[-180.7,-173.3]:box('BRP_SpineShallowSaddle',-4.12,4.18,106.265,106.285,z-.23,z+.23,'staff_zinc','platform_support_shallow')

# Enclosed public L route. Sidewalls, framing and sills are real supported geometry.
# Port window wall is rhythmically framed, visibly glazed and sill-backed. No invented exterior views.
port_cuts=[-181,-173,-165,-157,-149,-141,-133,-125,-117,-109,-101,-93,-85,-80]
box('BRP_PortWindowSill',-48,-47.68,106.28,107.08,-181,-80,'ivory_enamel','enclosure')
box('BRP_PortWindowHeader',-48,-47.68,110.35,111.18,-181,-80,'ivory_enamel','enclosure')
box('BRP_PortTimberHandrail',-47.69,-47.64,107.02,107.14,-181,-80,'warm_walnut','enclosure')
for z in port_cuts:
 lo=max(-181,z-.13);hi=min(-80,z+.13)
 box('BRP_PortWindowMullion',-48,-47.62,107.04,110.40,lo,hi,'champagne_metal','window_frame')
for i,(a,b)in enumerate(zip(port_cuts,port_cuts[1:])):
 name='BRP_PortGlass_%02d'%i;box(name,-47.93,-47.85,107.06,110.37,a+.10,b-.10,'bridge_gallery_glass','glass')
 D['windows'].append({'id':'port_%02d'%i,'side':'port','glass_assembly':name,'world_aabb':[-47.93,-47.85,107.06,110.37,a+.10,b-.10],'thickness_m':.08,'closed_glass_collision':True,'outward_normal':[-1,0,0],'world_view':'Static quiet port crescent; do not rotate sky','frame_contact_overlap_m':.03})
# Opaque inner screen provides a clear guest/unfinished-platform boundary with layered upper profiles.
box('BRP_InnerScreen',-40.32,-40,106.28,111.18,-173,-80,'ivory_enamel','enclosure')
box('BRP_InnerTimberDado',-40.38,-40.30,106.55,107.48,-173,-80,'warm_walnut','enclosure')
box('BRP_InnerDadoCap',-40.40,-40.28,107.43,107.55,-173,-80,'champagne_metal','enclosure')
for z in[-172.8,-164,-152,-140,-128,-116,-104,-92,-80.2]:box('BRP_InnerScreenPilaster',-40.40,-40,107.5,110.48,z-.15,z+.15,'champagne_metal','enclosure')
# Transverse gallery closes fore and aft only west of X=-4. No wall across either spine opening.
for side,z0,z1 in[('Fore',-181,-180.68),('Aft',-173.32,-173)]:
 x0=-48 if side=='Fore'else-40
 box('BRP_'+side+'GalleryWallBase',x0,-4,106.28,107.08,z0,z1,'ivory_enamel','enclosure')
 box('BRP_'+side+'GalleryWallHeader',x0,-4,110.35,111.18,z0,z1,'ivory_enamel','enclosure')
 # Fore windows face forward; aft glazing honestly reveals the future bridge/platform.
 cuts=[x0]+[x for x in[-40,-32,-24,-16,-8]if x>x0]+[-4]
 for x in cuts:box('BRP_'+side+'GalleryMullion',max(x0,x-.12),min(-4,x+.12),107.04,110.40,z0,z1,'champagne_metal','window_frame')
 for i,(a,b)in enumerate(zip(cuts,cuts[1:])):
  mid=(z0+z1)/2;name='BRP_'+side+'Glass_%02d'%i;box(name,a+.10,b-.10,107.06,110.37,mid-.04,mid+.04,'bridge_gallery_glass','glass');D['windows'].append({'id':side.lower()+'_%02d'%i,'side':side.lower(),'glass_assembly':name,'world_aabb':[a+.10,b-.10,107.06,110.37,mid-.04,mid+.04],'thickness_m':.08,'closed_glass_collision':True,'outward_normal':[0,0,-1 if side=='Fore'else 1],'world_view':'Forward space'if side=='Fore'else'Future bridge frame visible; no fake panorama','frame_contact_overlap_m':.02})
# An east-side return encloses the route at its junction while preserving the entire original spine.
box('BRP_EastJunctionReturn',4,4.18,106.28,111.18,-181,-173,'ivory_enamel','enclosure')
# Roof/ceiling follows the L footprint, with only the documented east wall tolerance.
for x0,x1,z0,z1 in[(-48,-40,-173,-80),(-48,4.18,-181,-173)]:
 box('BRP_GalleryCeiling',x0,x1,111,111.18,z0,z1,'ivory_enamel','ceiling')
 box('BRP_GalleryRoofSkin',x0,x1,114.12,114.32,z0,z1,'staff_bluegrey_paint','roof')
for x0,x1 in[(-48,-47.85),(-40.15,-40)]:box('BRP_GalleryRoofSideFascia',x0,x1,111.10,114.32,-173,-80,'staff_bluegrey_paint','roof')
for z0,z1 in[(-181,-180.85),(-173.15,-173)]:box('BRP_ForeRoofFascia',-48,4.18,111.1,114.32,z0,z1,'staff_bluegrey_paint','roof')
box('BRP_GalleryAftRoofFascia',-48,-40,111.10,114.32,-80.15,-80,'staff_bluegrey_paint','roof')
box('BRP_EastRoofFascia',4.03,4.18,111.10,114.32,-181,-173,'staff_bluegrey_paint','roof')
# Layered public ceiling edges are deliberately shallower than the main structural ceiling.
for x0,x1 in[(-47.70,-46.95),(-41.05,-40.30)]:
 box('BRP_GalleryCove',x0,x1,110.63,111.08,-173,-80,'ivory_enamel','ceiling')
 box('BRP_GalleryCoveReveal',x0+.08,x1-.08,110.58,110.65,-173,-80,'warm_walnut','ceiling')
for z0,z1 in[(-180.70,-179.95),(-174.05,-173.30)]:box('BRP_ForeGalleryCove',-47.7,-4,110.63,111.08,z0,z1,'ivory_enamel','ceiling')
for z in[-171,-159,-147,-135,-123,-111,-99,-87]:box('BRP_GalleryCeilingRib',-47.7,-40.3,110.72,111.08,z-.12,z+.12,'champagne_metal','ceiling')
# Visible warm fixtures supported by actual ceiling/ribs, with markers below their real lenses.
def fixture(name,x,z,long_axis='z'):
 dx,dz=(.23,.8)if long_axis=='z'else(.8,.23)
 box(name+'_Housing',x-dx,x+dx,110.45,111.20,z-dz,z+dz,'champagne_metal','fixture')
 box(name+'_Lens',x-dx+.05,x+dx-.05,110.42,110.46,z-dz+.06,z+dz-.06,'bridge_warm_opal','fixture')
 # Enclosing frame has restrained profile; emission remains below the complete housing.
 pos=[x,110.41,z];mn='DATUM_light_'+name.lower();marker(mn,pos,{'profile':'bridge_guest_route','direction':'down'})
 D['light_markers'].append({'name':mn,'position':pos,'direction':[0,-1,0],'profile':'bridge_guest_route','temperature':'warm','suggested_color':[1,.78,.50],'suggested_range':9.5,'suggested_spot_angle_degrees':76,'fixture_assembly':name,'support':'Actual housing Y110.45..111.20 intersects ceiling or structural crossmember'})
for z in[-172,-160,-148,-136,-124,-112,-100,-88,-82]:fixture('BRP_GalleryLight_Z%s'%abs(z),-44,z)
for x in[-44,-32,-20,-8,0]:fixture('BRP_ForeGalleryLight_X%s'%x,x,-177,'x')
# Quiet future platform task-wayfinding lights hang from real crossmembers, not floating points.
for z in[-160,-136,-124]:
 for x in[-20,20]:fixture('BRP_PlatformLight_X%s_Z%s'%(x,str(abs(z)).replace('.','p')),x,z,'x')
marker('DATUM_origin',[0,0,0]);marker('DATUM_bypass_turn',[-44,106.5,-177]);marker('DATUM_bypass_apron',[-44,106.5,-80]);marker('DATUM_old_spine_fore',[0,106.5,-181]);marker('DATUM_old_spine_aft',[0,106.5,-173])
D['source_validation']='qa/source_export_validation.json';D['status']='Stage1 editable construction kit; source verification and parent runtime acceptance required';D['support']['old_frame_optional_ties']='Not used; all primary loads resolve geometrically to the four new keel-bearing piers'
D['source_groups']=['pier','transfer','bypass_transfer','roof_support','hanger','platform_support','platform_support_shallow','guard','enclosure','window_frame','glass','ceiling','roof','fixture']
(R/'source/section_contract.json').write_text(json.dumps(D,indent=2)+'\n');(R/'source/geometry_parts.json').write_text(json.dumps({'catalogue_id':AID,'parts':records},indent=2)+'\n')
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1;bpy.context.preferences.filepaths.save_version=0;bpy.ops.file.pack_all();src=R/'source'/(AID+'.blend');out=R/'exports'/(AID+'.glb');bpy.ops.wm.save_as_mainfile(filepath=str(src))
triangles=0;batches={}
for ob in parts:
 ob.data.calc_loop_triangles();triangles+=len(ob.data.loop_triangles);key=(ob['cell_x'],ob['cell_y'],ob['cell_z'],ob.data.materials[0].name);batches.setdefault(key,[]).append(ob)
for key,obs in sorted(batches.items()):
 name='BRP_CELL_X%d_Y%d_Z%d_%s'%key;verts=[];faces=[];uvs=[]
 for ob in obs:
  offset=len(verts);verts.extend(tuple(v.co)for v in ob.data.vertices);faces.extend(tuple(i+offset for i in f.vertices)for f in ob.data.polygons);uvs.extend(tuple(v.uv)for v in ob.data.uv_layers.active.data)
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();me.materials.append(obs[0].data.materials[0]);uv=me.uv_layers.new(name='MetreScaled')
 for li,q in enumerate(uvs):uv.data[li].uv=q
 ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);ob['catalogue_id']=AID;ob['collision_contract']='concave_static_surface';ob['spatial_cell_metres']=8
bpy.ops.object.select_all(action='DESELECT')
for ob in parts:ob.select_set(True)
bpy.ops.object.delete(use_global=False)
bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',export_yup=True,export_extras=True)
M={'catalogue_id':AID,'family':FAMILY,'name':'D18 four-bearing bridge platform and enclosed public port bypass','source':'source/'+AID+'.blend','export':'exports/'+AID+'.glb','source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'export_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'triangles':triangles,'editable_part_count':len(parts),'runtime_mesh_batches':len(batches),'light_marker_count':len(D['light_markers']),'coordinate_contract':'source/section_contract.json','status':'Construction source; verification pending. Not an operating bridge or final art acceptance.'}
(R/(AID+'.manifest.json')).write_text(json.dumps(M,indent=2)+'\n');print(json.dumps(M))
