"""Editable stage-two connected fan bridge enclosure. No floor, lights, furniture or door leaves.
World mapping: Blender=(Godot X,-Godot Z,Godot Y). All new work isolated in this family.
"""
from pathlib import Path
import bpy,bmesh,json,math,sys,hashlib
from mathutils import Vector
R=Path(__file__).resolve().parents[1];C=R.parents[1];AID='AST-CMD-004';FAMILY='bridge_enclosure'
manifest=json.loads((C/'catalogue_manifest.json').read_text())
assert all(a['catalogue_id']!=AID or a['family']==FAMILY for a in manifest['assets'])
D={'catalogue_id':AID,'family':FAMILY,'floor_y':106.5,'windows':[],'doors':[],'light_markers':[],'support_contacts':[],'unbuilt_reservations':[]}
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
sys.path.insert(0,str(C/'standards'));import staff_materials,materials
mats=staff_materials.materials();mats.update(materials.materials())
for m in mats.values():
 for n in m.node_tree.nodes:
  if n.type=='TEX_IMAGE':n.interpolation='Closest'
opal=mats['staff_opal'].copy();opal.name='ASTRAEA_bridge_threshold_opal';opal['astraea_material_role']='bridge_warm_opal';bs=next(n for n in opal.node_tree.nodes if n.type=='BSDF_PRINCIPLED');bs.inputs['Emission Color'].default_value=(1,.78,.50,1);bs.inputs['Emission Strength'].default_value=.65;mats['bridge_warm_opal']=opal
m=bpy.data.materials.new('ASTRAEA_bridge_pressure_glass');m.use_nodes=True;m['meters_per_tile_uv']=[1,1];m['astraea_material_role']='bridge_pressure_glass';m.diffuse_color=(.23,.42,.44,.28);bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.23,.42,.44,1);bs.inputs['Roughness'].default_value=.22;bs.inputs['Metallic'].default_value=.08;bs.inputs['Alpha'].default_value=.28;m.surface_render_method='DITHERED';mats['bridge_pressure_glass']=m
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

# Convex fan boundary with exact line-line offset mitres. World X/Z, clockwise viewed above.
outline=[(-29.7,-171.7),(29.7,-171.7),(35.7,-159.7),(35.7,-118.3),(-35.7,-118.3),(-35.7,-159.7)]
def offset_poly(poly,d):
 out=[]
 for i,p in enumerate(poly):
  a=poly[i-1];b=poly[(i+1)%len(poly)];u=Vector((p[0]-a[0],p[1]-a[1]));v=Vector((b[0]-p[0],b[1]-p[1]));u.normalize();v.normalize();nu=Vector((u.y,-u.x));nv=Vector((v.y,-v.x));q=Vector(p)+d*nu;r=Vector(p)+d*nv;cross=lambda a,b:a.x*b.y-a.y*b.x;t=cross(r-q,v)/cross(u,v);out.append(tuple(q+t*u))
 return out
outer=offset_poly(outline,.16);inner=offset_poly(outline,-.16)
D['boundary_xz']=outline;D['wall_thickness_m']=.32;D['corner_mitres']=[{'reference':p,'outer':o,'inner':i}for p,o,i in zip(outline,outer,inner)]
def ring_part(name,poly,y0,y1,role,group):
 n=len(poly);mesh(name,[(x,y,z)for y in[y0,y1]for x,z in poly],[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n)for i in range(n)],role,group)
def edge_piece(name,e,t0,t1,y0,y1,role='ivory_enamel',group='enclosure'):
 # Fractions share the exact mitred end, so no corner crack or piled rectangular bars.
 j=(e+1)%6;a,b=outer[e],outer[j];c,d=inner[e],inner[j];lerp=lambda p,q,t:(p[0]+(q[0]-p[0])*t,p[1]+(q[1]-p[1])*t)
 n=max(1,math.ceil(math.dist(outline[e],outline[j])*(t1-t0)/6))
 for k in range(n):
  lo=t0+(t1-t0)*k/n;hi=t0+(t1-t0)*(k+1)/n;ring_part(name,[lerp(a,b,lo),lerp(a,b,hi),lerp(c,d,hi),lerp(c,d,lo)],y0,y1,role,group)
def range_x(e,a,b):return ((a-outline[e][0])/(outline[(e+1)%6][0]-outline[e][0]),(b-outline[e][0])/(outline[(e+1)%6][0]-outline[e][0]))
def window_run(tag,e,t0,t1,cuts):
 # Sill meets existing lowered cap at107.08..107.12; glazing overlaps sill and header.
 edge_piece('BRE_'+tag+'_Sill',e,t0,t1,107.08,107.22,'champagne_metal','window_frame')
 edge_piece('BRE_'+tag+'_Header',e,t0,t1,110.50,111.18,'ivory_enamel','enclosure')
 for t in cuts:
  # At mitres collars rather than off-axis rectangular mullions close the corner.
  dt=.16/math.dist(outline[e],outline[(e+1)%6]);edge_piece('BRE_'+tag+'_Mullion',e,max(t0,t-dt),min(t1,t+dt),107.10,110.58,'champagne_metal','window_frame')
 for n,(a,b)in enumerate(zip(cuts,cuts[1:])):
  aa=a+.12/math.dist(outline[e],outline[(e+1)%6]);bb=b-.12/math.dist(outline[e],outline[(e+1)%6]);p=outline[e];q=outline[(e+1)%6];u=(p[0]+(q[0]-p[0])*aa,p[1]+(q[1]-p[1])*aa);v=(p[0]+(q[0]-p[0])*bb,p[1]+(q[1]-p[1])*bb);name='BRE_'+tag+'_Glass_%02d'%n;bar(name,u,v,.08,107.10,110.55,'bridge_pressure_glass','glass');D['windows'].append({'id':tag+'_%02d'%n,'glass_assembly':name,'edge':e,'a_xz':u,'b_xz':v,'y':[107.10,110.55],'closed_glass_collision':True,'glass_thickness_m':.08,'frame_overlap_m':.04,'view':'existing transverse public gallery'if tag=='PortFore'else'fixed global sky; starboard principal planet, forward stars'})
# Fore glazing flanks a deep opaque doorway cheek, with the old thin terminal returns inside it.
for tag,a,b,cutsx in [('PortFore',-29.7,-4.4,[-29.7,-24,-16,-8,-4.4]),('StarboardFore',4.4,29.7,[4.4,12,20,29.7])]:
 t0,t1=range_x(0,a,b);window_run(tag,0,t0,t1,[range_x(0,x,x)[0]for x in cutsx])
window_run('StarboardDiagonal',1,0,1,[0,.5,1])
window_run('StarboardPlanet',2,0,1,[0]+[(z+159.7)/41.4 for z in[-148,-136,-124]]+[1])
# Retained port diagonal, port longitudinal and aft guards ARE the lower opaque wall.
# The upper panel starts inside their cap, not as a second parallel lower skin.
for e,tag in [(4,'PortLong'),(5,'PortDiagonal')]:edge_piece('BRE_'+tag+'_UpperOpaque',e,0,1,107.70,111.18,'ivory_enamel','enclosure')
# Aft wing walls omit the old spine entry and land on the original full-height guards.
for a,b in [(35.7,4.4),(-4.4,-35.7)]:
 t0,t1=range_x(3,a,b);edge_piece('BRE_AftUpperOpaque',3,t0,t1,107.70,111.18,'ivory_enamel','enclosure')
# Deep inset reveals at both door interfaces: no static frame or leaf duplication.
for tag,z,inward in [('Fore',-171.7,1),('Aft',-118.3,-1)]:
 for s in[-1,1]:
  xa,xb=sorted([s*1.375,s*4.45]);box('BRE_'+tag+'_DoorCheek',xa,xb,106.5,111.18,z-.33,z+.33,'ivory_enamel','door_reveal')
 box('BRE_'+tag+'_DoorHeader',-1.375,1.375,109.315,111.18,z-.33,z+.33,'ivory_enamel','door_reveal')
 marker('DATUM_bridge_'+tag.lower()+'_door',[0,106.5,z],{'reuse_catalogue_id':'AST-STF-008','yaw_radians':math.pi if tag=='Fore'else 0.,'opening_inward_z':inward})
 D['doors'].append({'id':tag.lower(),'position':[0,106.5,z],'yaw_radians':math.pi if tag=='Fore'else 0,'reuse_catalogue_id':'AST-STF-008','aperture_width':2.75,'aperture_height':2.815,'frame_dimensions':[2.76,2.82,.36],'frame_wall_overlap_m':.005,'clear_open_handles_width':2.168,'opening_inward_z':inward,'no_static_leaf':True})
# Fitted corner collars catch actual off-line nose and shoulder hangers, with shallow edge returns.
for s in[-1,1]:
 for tag,x,z in [('Fore',s*29.85,-171.7),('Shoulder',s*35.7,-160),('Aft',s*35.7,-118.3)]:
  box('BRE_'+tag+'_HangerCollar',x-.23,x+.23,107.10,111.18,z-.26,z+.26,'champagne_metal','window_frame')
# Small approach enclosure on existing floor only. Demountable infill reserves a future staff crosslink.
for s in[-1,1]:
 xa,xb=sorted([s*3.68,s*4]);
 for a,b in[(-118.3,-116.3),(-116.3,-113.7),(-113.7,-112.98)]:
  box('BRE_AftVestibule_DemountableInfill'if a==-116.3 else'BRE_AftVestibule_Cheek',xa,xb,106.5,109.80,a,b,'staff_bluegrey_paint'if a==-116.3 else'ivory_enamel','vestibule')
 box('BRE_ForeApproach_Cheek',xa,xb,106.5,111.12,-173,-171.7,'ivory_enamel','vestibule')
# Roof penetrates existing core cover by20mm horizontally and70mm vertically; exact cover remains untouched.
box('BRE_AftVestibule_Roof',-4,4,109.73,109.85,-118.3,-112.98,'ivory_enamel','vestibule_roof')
box('BRE_ForeApproach_Roof',-4,4,111,111.18,-173.02,-171.54,'ivory_enamel','vestibule_roof')
D['unbuilt_reservations']=[{'name':'future_staff_crosslink','z':-115,'status':'unbuilt, sealed demountable side infill; no connected-route claim'}]
D['core_cover_interface']={'actual_unchanged_cover_y':[109.73,109.85],'contact_z':[-113,-112.98],'contact_x':[-4,4]}
# Convex polygon clipping to a bounded grid for a genuine fan ceiling/roof, never a rectangular lid.
def clip(poly,axis,value,greater):
 out=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  ia=a[axis]>=value-1e-9 if greater else a[axis]<=value+1e-9;ib=b[axis]>=value-1e-9 if greater else b[axis]<=value+1e-9
  if ia:out.append(a)
  if ia!=ib:
   t=(value-a[axis])/(b[axis]-a[axis]);q=[a[0]+t*(b[0]-a[0]),a[1]+t*(b[1]-a[1])];q[axis]=value;out.append(tuple(q))
 return out
# Reliefs around the unchanged6 bridge housings; no lamp position/settings or lens is altered.
holes=[(x-.82,x+.82,z-.25,z+.25)for z in[-160,-136,-124]for x in[-20,20]]
def tiled_skin(name,poly,y0,y1,role,group,reliefs=False):
 xs=sorted(set([p[0]for p in poly]+list(range(-32,33,8))+([q for h in holes for q in h[:2]]if reliefs else[])));zs=sorted(set([p[1]for p in poly]+list(range(-168,-119,8))+([q for h in holes for q in h[2:]]if reliefs else[])))
 for xa,xb in zip(xs,xs[1:]):
  for za,zb in zip(zs,zs[1:]):
   if reliefs and any(h[0]<(xa+xb)/2<h[1]and h[2]<(za+zb)/2<h[3]for h in holes):continue
   p=poly
   for ax,v,g in[(0,xa,True),(0,xb,False),(1,za,True),(1,zb,False)]:p=clip(p,ax,v,g)if p else[]
   clean=[]
   for q in p:
    if not clean or math.dist(clean[-1],q)>1e-7:clean.append(q)
   if len(clean)>2 and math.dist(clean[0],clean[-1])<1e-7:clean.pop()
   area=abs(sum(a[0]*b[1]-a[1]*b[0]for a,b in zip(clean,clean[1:]+clean[:1])))/2 if len(clean)>2 else 0
   if area>1e-7:ring_part(name,clean,y0,y1,role,group)
tiled_skin('BRE_FanCeiling',outer,111,111.18,'ivory_enamel','ceiling',True)
tiled_skin('BRE_FanRoofSkin',outer,114.12,114.32,'staff_bluegrey_paint','roof')
D['ceiling_housing_reliefs']=[{'world_xz_rect':h,'fixture_retained':True}for h in holes]
# Layered fan perimeter soffits sit above every optical aperture, staying peripheral to lamp cones.
for e in range(6):
 edge_piece('BRE_PerimeterRoofFascia',e,0,1,111.10,114.32,'staff_bluegrey_paint','roof_fascia')
 a,b=inner[e],inner[(e+1)%6];bar('BRE_ShallowPerimeterSoffit',a,b,.95,110.65,111.10,'ivory_enamel','soffit')
 bar('BRE_PerimeterWarmReveal',a,b,.48,110.61,110.68,'warm_walnut','soffit')
# Shaped entry fan canopy, beyond the door sweep and above lens exits.
for z,s in[(-171.7,1),(-118.3,-1)]:
 poly=[(-4.4,z),(4.4,z),(6,z+s*2.2),(3,z+s*3.4),(-3,z+s*3.4),(-6,z+s*2.2)]
 if s<0:poly.reverse()
 tiled_skin('BRE_EntryFanSoffit',poly,110.65,111.10,'ivory_enamel','soffit')
# Roof load path: actual old transverse flanges, fitted longitudinal carriers, seated purlins, skin.
for x in[-32,-16,0,16,32]:box('BRE_MainRoofCarrier',x-.14,x+.14,112.00,114.22,-166.7 if abs(x)==32 else -168.20,-118.18,'staff_bluegrey_paint','roof_support')
for x in[-28,-16,0,16,28]:box('BRE_NoseToTransferCarrier',x-.14,x+.14,111.92,114.22,-171.82,-167.60,'staff_bluegrey_paint','roof_support')
for z in[-171.7,-168,-160,-148,-136,-124,-118.3]:
 hw=29.7+(z+171.7)*.5 if z<-159.7 else 35.7
 box('BRE_SeatedRoofPurlin',-hw,hw,114.02,114.22,z-.12,z+.12,'staff_zinc','roof_support')
# Ceiling battens are supported by the existing transfers and inner hangers, with tops above ceiling.
for x in[-28,-16,0,16,28]:box('BRE_CeilingCarrier',x-.09,x+.09,111.10,112.12,-171.70,-118.30,'staff_bluegrey_paint','ceiling_support')
# Small ceiling edge seal around housing reliefs lives above lens plane; old housing is the closure.
for x0,x1,z0,z1 in holes:
 for a,b,c,d in[(x0-.05,x0+.04,z0,z1),(x1-.04,x1+.05,z0,z1),(x0,x1,z0-.05,z0+.04),(x0,x1,z1-.04,z1+.05)]:box('BRE_HousingReliefSeal',a,b,110.96,111.18,c,d,'champagne_metal','ceiling_support')
D['support_strategy']='Closed contact network to unchanged003 transfers/hangers and retained floor. Nose carriers meet actualZ-168 transverse; no fictitious X32 support at narrowing nose. Roof/ceiling skins have bounded real carrier contacts. Geometric contact, not engineering certification.'
D['floor_policy']='No floor in004; all existing floor polygons and owners unchanged. One connected fan interior across old spine. No deep new underfloor geometry.'
D['lights_policy']='All20 old003 fixtures and markers unchanged; no added lights, sky change, or ambient change.'
D['public_bypass_route_xz']=[[0,-520],[0,-177],[-44,-177],[-44,-77]]
D['status']='Architectural source construction; runtime and final art acceptance pending; no operational bridge, life-support simulation or ship-wide pressure claim.'
D['source_validation']='qa/source_export_validation.json';D['source_groups']=sorted(set(p['group']for p in records))
marker('DATUM_origin',[0,0,0]);marker('DATUM_bridge_planet_standing_eye',[28,108.10,-145]);marker('DATUM_bridge_planet_seated_eye',[28,107.65,-145]);marker('DATUM_bridge_front_left_gallery_eye',[15,108.10,-155])
(R/'source/section_contract.json').write_text(json.dumps(D,indent=2)+'\n');(R/'source/geometry_parts.json').write_text(json.dumps({'catalogue_id':AID,'parts':records},indent=2)+'\n')
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1;bpy.context.preferences.filepaths.save_version=0;bpy.ops.file.pack_all();src=R/'source'/(AID+'.blend');out=R/'exports'/(AID+'.glb');bpy.ops.wm.save_as_mainfile(filepath=str(src))
triangles=0;batches={}
for ob in parts:
 ob.data.calc_loop_triangles();triangles+=len(ob.data.loop_triangles);key=(ob['cell_x'],ob['cell_y'],ob['cell_z'],ob.data.materials[0].name);batches.setdefault(key,[]).append(ob)
for key,obs in sorted(batches.items()):
 name='BRE_CELL_X%d_Y%d_Z%d_%s'%key;verts=[];faces=[];uvs=[]
 for ob in obs:
  offset=len(verts);verts.extend(tuple(v.co)for v in ob.data.vertices);faces.extend(tuple(i+offset for i in f.vertices)for f in ob.data.polygons);uvs.extend(tuple(v.uv)for v in ob.data.uv_layers.active.data)
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();me.materials.append(obs[0].data.materials[0]);uv=me.uv_layers.new(name='MetreScaled')
 for li,q in enumerate(uvs):uv.data[li].uv=q
 ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);ob['catalogue_id']=AID;ob['collision_contract']='concave_static_surface';ob['spatial_cell_metres']=8
bpy.ops.object.select_all(action='DESELECT')
for ob in parts:ob.select_set(True)
bpy.ops.object.delete(use_global=False)
bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',export_yup=True,export_extras=True)
M={'catalogue_id':AID,'family':FAMILY,'name':'D18 fan bridge pressure shell and paired service-door interfaces','source':'source/'+AID+'.blend','export':'exports/'+AID+'.glb','source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'export_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'triangles':triangles,'editable_part_count':len(parts),'runtime_mesh_batches':len(batches),'light_marker_count':0,'coordinate_contract':'source/section_contract.json','status':'Architectural construction source; verification pending. No furnishings or operating bridge; not final art acceptance.'}
(R/(AID+'.manifest.json')).write_text(json.dumps(M,indent=2)+'\n');print(json.dumps(M))
