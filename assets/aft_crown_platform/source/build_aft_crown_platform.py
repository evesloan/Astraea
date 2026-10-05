"""Editable aft receiving foyer and Upper Horizon platform. No authored floor slabs.
World mapping: Blender=(Godot X,-Godot Z,Godot Y). All new work isolated in this family.
"""
from pathlib import Path
import bpy,bmesh,json,math,sys,hashlib
from mathutils import Vector
R=Path(__file__).resolve().parents[1];C=R.parents[1];AID='AST-CMD-005';FAMILY='aft_crown_platform'
manifest=json.loads((C/'catalogue_manifest.json').read_text())
assert all(a['catalogue_id']!=AID or a['family']==FAMILY for a in manifest['assets'])
D=json.loads((R/'source/section_contract.json').read_text())
# A later bounded enclosure revision owns four split Back/Cap objects only. Reproduce it
# from its immutable source baseline rather than silently restoring the old high guards.
if D.get('low_sill_revision'):
 import runpy
 runpy.run_path(str(C/'assets/upper_horizon_enclosure/source/revise_005_guards.py'),run_name='__main__')
 raise SystemExit(0)
for key in ['light_markers','windows','guards','doors']:D[key]=[]
D['support']['hanger_assemblies']=[];D['support']['member_assemblies']=[]
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
sys.path.insert(0,str(C/'standards'));import staff_materials,materials
mats=staff_materials.materials();mats.update(materials.materials())
for m in mats.values():
 for n in m.node_tree.nodes:
  if n.type=='TEX_IMAGE':n.interpolation='Closest'
opal=mats['staff_opal'].copy();opal.name='ASTRAEA_aft_platform_warm_opal';opal['astraea_material_role']='aft_platform_warm_opal';bs=next(n for n in opal.node_tree.nodes if n.type=='BSDF_PRINCIPLED');bs.inputs['Emission Color'].default_value=(1,.78,.50,1);bs.inputs['Emission Strength'].default_value=.65;mats['aft_platform_warm_opal']=opal
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
 for yy in[y0,y1-.16]:box(name+'_Flange',x0,x1,yy,yy+.16,z-.46,z+.46,'staff_zinc',group)
 D['support']['member_assemblies'].append({'name':name,'axis':'x','span':[x0,x1],'z':z,'y':[y0,y1],'group':group})

def girder_z(name,x,z0,z1,y0=111.1,y1=113.88,width=.32,group='transfer'):
 box(name+'_Web',x-width/2,x+width/2,y0,y1,z0,z1,'staff_bluegrey_paint',group)
 for yy in[y0,y1-.16]:box(name+'_Flange',x-.30,x+.30,yy,yy+.16,z0,z1,'staff_zinc',group)
 D['support']['member_assemblies'].append({'name':name,'axis':'z','x':x,'span':[z0,z1],'y':[y0,y1],'group':group})

# Six exact audited keel-bearing footprints. Nothing else descends below the suspended girders.
levels=[-3.2,0,6,12,16.5,21,27,35.5,44,52.5,61,69.5,78,84,88.5,93,97.5,102,106.5,111,114]
for index,(x,z) in enumerate(D['support']['pier_centres_xz']):
 name='ACP_Pier_%02d'%(index+1)
 for ya,yb in zip(levels,levels[1:]):
  box(name+'_Web',x-.32,x+.32,ya,yb,z-.52,z+.52,'staff_bluegrey_paint','pier')
  for sx in[-1,1]:box(name+'_Chord',*sorted([x+sx*.30,x+sx*.40]),ya,yb,z-.60,z+.60,'staff_zinc','pier')
  box(name+'_Collar',x-.4,x+.4,ya,min(ya+.2,yb),z-.6,z+.6,'staff_bluegrey_paint','pier')
 box(name+'_HeadBearing',x-.4,x+.4,111.0,114,z-.6,z+.6,'staff_zinc','transfer')
 marker('DATUM_aft_platform_pier_%02d_base'%(index+1),[x,-3.2,z]);marker('DATUM_aft_platform_pier_%02d_head'%(index+1),[x,114,z])
# Primary transfers have positive contact with every pier head. Wide wings hang from these frames.
for z in[119,148,174]:girder_x('ACP_PrimaryTransverse_Z%s'%z,-35.9,35.9,z,111.1,113.94)
# The old002 roof longs end101.84: overlap real steel by0.34m, never start at102 in air.
for x in D['support']['old_roof_link_x']:
 end=193.7 if abs(x)<=24 else 181.7
 girder_z('ACP_RoofLong_X%s'%x,x,101.5,end,111.10,113.90)
 box('ACP_SeamSleeve_X%s'%x,x-.38,x+.38,111.04,113.98,101.50,102.30,'staff_zinc','seam_coupler')
for x in[-24,-16,16,24]:girder_z('ACP_SecondaryLong_X%s'%x,x,102.2,193.7,111.18,112.1,.24)
# Inner pier lines need continuous members linking their three transfer stations.
for x in[-9.5,9.5]:girder_z('ACP_InnerPierLong_X%s'%x,x,118.5,174.5,111.1,113.90)
# Secondary crossframes support perimeter hangers and route-fixture rails.
stations=[102.4,110,119,130,139,148,158,166,174,181.5,187,193.7]
def halfwidth(z):return 36 if z<=182 else 36-(z-182)*10/12
for z in stations:
 width=halfwidth(z)-.30;girder_x('ACP_Secondary_Z%s'%str(z).replace('.','p'),-width,width,z,111.18,112.10,.24)
# Fanned edge roof follows the actual supported platform, with no outboard columns beyond182.
for sign in[-1,1]:
 side='Port'if sign<0 else'Starboard'
 roofpath=[(sign*35.7,102.2),(sign*35.7,181.7),(sign*25.7,193.7),(sign*4.3,193.7)]
 for i,(a,b) in enumerate(zip(roofpath,roofpath[1:])):
  bar('ACP_'+side+'_EdgeRoofWeb_%02d'%i,a,b,.28,111.16,112.2,'staff_bluegrey_paint','transfer')
  for y in[111.16,112.05]:bar('ACP_'+side+'_EdgeRoofFlange_%02d'%i,a,b,.55,y,y+.16,'staff_zinc','transfer')
 # Floor grid entirely outside old spine/core; actual floor is solely parent compiled geometry.
 for z in stations:
  inner=8.05 if z<=139 else 4.42;outer=halfwidth(z)-.30
  girder_x('ACP_'+side+'_FloorCross_Z%s'%str(z).replace('.','p'),*sorted([sign*inner,sign*outer]),z,105.84,106.28,.24,'platform_support')
 for x in[8.4,16,24]:girder_z('ACP_'+side+'_FloorLong_X%s'%x,sign*x,102.2,193.7,105.86,106.28,.20,'platform_support')
 # Outer edge chain carries real backing/handrail and cantilever tail. No inner guard blocks the public wing.
 path=[(sign*10.1,102.2),(sign*35.7,102.2),(sign*35.7,181.7),(sign*25.7,193.7),(sign*4.0,193.7)]
 for i,(a,b)in enumerate(zip(path,path[1:])):
  # Last girder stops outside protected spine; a slab-height shoe finishes the open mouth.
  end=(sign*4.42,193.7)if i==3 else b
  bar('ACP_'+side+'_EdgeGirder_%02d'%i,a,end,.48,105.82,106.28,'staff_bluegrey_paint','platform_support')
  if i==0:continue # Existing command wall closes the front interface; no duplicate guest barrier.
  if i==1:a=(sign*35.7,101.96) # Close the old002 wall junction with0.04m overlap; no0.2m edge gap.
  bar('ACP_'+side+'_GuardToe_%02d'%i,a,b,.28,106.27,106.62,'champagne_metal','guard')
  bar('ACP_'+side+'_GuardBack_%02d'%i,a,b,.16,106.49,107.62,'ivory_enamel','guard')
  bar('ACP_'+side+'_GuardCap_%02d'%i,a,b,.24,107.59,107.82,'warm_walnut','guard')
  D['guards'].append({'id':side+'_%02d'%i,'a_xz':a,'b_xz':b,'height_above_floor':1.32,'backed':True,'support_assembly':'ACP_'+side+'_EdgeGirder_%02d'%i})
 # Actual terminal returns close the narrow outside strip and leave X±4 central continuation open.
 box('ACP_'+side+'_MouthSlabShoe',*sorted([sign*4,sign*4.7]),106.265,106.46,193.46,194,'staff_zinc','platform_support_shallow')
 box('ACP_'+side+'_MouthReturnBack',*sorted([sign*4,sign*4.16]),106.46,107.62,193.60,194,'ivory_enamel','guard')
 box('ACP_'+side+'_MouthReturnCap',*sorted([sign*4,sign*4.24]),107.59,107.82,193.60,194,'warm_walnut','guard')
 # Wall-zone hangers serve edge girders. All legs stop at platform, not cinema/void floors.
 for z in stations:
  x=sign*(halfwidth(z)-.30);tag='ACP_'+side+'_EdgeHanger_Z%s'%str(z).replace('.','p')
  box(tag,x-.10,x+.10,106.02,112.08,z-.14,z+.14,'champagne_metal','hanger');D['support']['hanger_assemblies'].append({'name':tag,'x':x,'z':z,'y':[106.02,112.08]})
 # Inner-wing hangers sit beside the protected core or pier line, never in its bypass or receiving turn.
 for z in[110,119,130,148,166,174,187,193.7]:
  x=sign*(9.5 if z<139 else 24);tag='ACP_'+side+'_InnerHanger_Z%s'%str(z).replace('.','p')
  box(tag,x-.10,x+.10,106.02,112.08,z-.14,z+.14,'champagne_metal','hanger');D['support']['hanger_assemblies'].append({'name':tag,'x':x,'z':z,'y':[106.02,112.08]})
# Screened staff L links have3.6m actual clear width including corner. Their heads are supported by roof rails.
for sign in[-1,1]:
 side='Port'if sign<0 else'Starboard'
 def sb(name,a,b,y0,y1,z0,z1,role='staff_bluegrey_paint',group='service_screen'):box('ACP_'+side+'_'+name,*sorted([sign*a,sign*b]),y0,y1,z0,z1,role,group)
 sb('CrosslinkInnerReturn',5,5.16,106.28,111.18,102,105.96)
 sb('CrosslinkFront',10,33.96,106.28,111.18,102,102.2)
 sb('CrosslinkRear',5,30.2,106.28,111.18,105.8,105.96,'ivory_enamel')
 sb('ServiceInnerScreen',30.04,30.2,106.28,111.18,105.8,142,'ivory_enamel')
 sb('ServiceOuterScreen',33.8,33.96,106.28,111.18,102,142)
 sb('CrosslinkCeiling',5,33.96,110.7,111.22,102,105.96,'staff_white_paint','service_ceiling')
 sb('ServiceCeiling',30.04,33.96,110.7,111.22,105.8,142,'staff_white_paint','service_ceiling')
 # Terminal shared-door boundary remains closed independently of the public fan route.
 for lo,hi in[(30.04,30.625),(33.375,33.96)]:sb('ServiceTerminalJamb',lo,hi,106.28,111.18,141.84,142)
 sb('ServiceTerminalHeader',30.625,33.375,109.315,111.18,141.84,142)
 dn='aft_platform_'+side.lower()+'_service_exit';mn='DATUM_door_'+dn
 marker(mn,[sign*32,106.5,141.92],{'door_file':'AST-STF-008.glb','yaw_radians':0.0,'programme_key':'controlled_crossing'})
 D['doors'].append({'id':dn,'name':dn,'position':[sign*32,106.5,141.92],'yaw':0.0,'yaw_radians':0.0,'file':'AST-STF-008.glb','marker':mn,'wall_aperture_half_width':1.375,'wall_aperture_height':2.815,'fixed_frame_outer_half_width':1.38,'fixed_frame_outer_height':2.82,'fixed_frame_half_depth':.18,'join_overlap_m':.005})
 # Ceiling bearer directly joins the real roof line and screen heads.
 girder_z('ACP_'+side+'_ServiceCeilingBearer',sign*32,102.2,142,111.0,112.1,.20,'transfer')
 for z in[110,119,130,139]:
  sb('ServiceScreenCrown',29.9,30.3,110.5,111.22,z-.18,z+.18,'champagne_metal','service_profile')
  sb('ServiceScreenTimberReveal',29.96,30.05,107.12,107.42,z-3,z+3,'warm_walnut','service_profile')
 # Floor bearer ends stop beyond coreX7.8; source-supported shallow brackets carry inner return.
 sb('CrosslinkInnerShallowShoe',4.98,8.65,106.265,106.35,102.15,102.45,'staff_zinc','platform_support_shallow')
 # 3.6m service turns and inward door sweeps remain free of pilasters and furniture.
 marker('DATUM_staff_'+side+'_turn',[sign*32,106.5,104]);marker('DATUM_staff_'+side+'_exit',[sign*32,106.5,142])
# Visible local fixtures: all housings directly overlap a real beam or service ceiling.
def fixture(name,x,z,cool=False):
 role='staff_zinc'if cool else'champagne_metal';opal='staff_opal'if cool else'aft_platform_warm_opal'
 box(name+'_Housing',x-.72,x+.72,110.50,111.24,z-.22,z+.22,role,'fixture')
 box(name+'_Lens',x-.65,x+.65,110.47,110.51,z-.16,z+.16,opal,'fixture')
 pos=[x,110.46,z];mn='DATUM_light_'+name.lower();marker(mn,pos,{'profile':'aft_platform_route','direction':'down'})
 D['light_markers'].append({'name':mn,'position':pos,'direction':[0,-1,0],'profile':'aft_platform_route','temperature':'cool'if cool else'warm','suggested_color':[.78,.88,1]if cool else[1,.78,.50],'suggested_range':11,'suggested_spot_angle_degrees':82,'fixture_assembly':name,'support':'Housing overlaps actual secondary beam or service ceiling'})
for sign in[-1,1]:
 for z in[110,130,148,166,187]:fixture('ACP_GuestLight_X%s_Z%s'%(sign*16,z),sign*16,z)
 for z in[110,130,140]:fixture('ACP_ServiceLight_X%s_Z%s'%(sign*32,z),sign*32,z,True)
 for x in[8,20,32]:fixture('ACP_CrosslinkLight_X%s'%(sign*x),sign*x,104,True)
for z in[148,174,193.7]:fixture('ACP_CentreLight_Z%s'%str(z).replace('.','p'),0,z)
marker('DATUM_origin',[0,0,0]);marker('DATUM_aft_receiving_turn',[0,106.5,142]);marker('DATUM_upper_horizon',[0,106.5,168]);marker('DATUM_onward_spine',[0,106.5,194])
D['source_validation']='qa/exact_roundtrip.json';D['status']='Construction source candidate; parent runtime and final art acceptance pending'
(R/'source/section_contract.json').write_text(json.dumps(D,indent=2)+'\n');(R/'source/geometry_parts.json').write_text(json.dumps({'catalogue_id':AID,'parts':records},indent=2)+'\n')
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1;bpy.context.preferences.filepaths.save_version=0;bpy.ops.file.pack_all();src=R/'source'/(AID+'.blend');out=R/'exports'/(AID+'.glb');bpy.ops.wm.save_as_mainfile(filepath=str(src))
triangles=0;batches={}
for ob in parts:
 ob.data.calc_loop_triangles();triangles+=len(ob.data.loop_triangles);key=(ob['cell_x'],ob['cell_y'],ob['cell_z'],ob.data.materials[0].name);batches.setdefault(key,[]).append(ob)
for key,obs in sorted(batches.items()):
 name='ACP_CELL_X%d_Y%d_Z%d_%s'%key;verts=[];faces=[];uvs=[]
 for ob in obs:
  offset=len(verts);verts.extend(tuple(v.co)for v in ob.data.vertices);faces.extend(tuple(i+offset for i in f.vertices)for f in ob.data.polygons);uvs.extend(tuple(v.uv)for v in ob.data.uv_layers.active.data)
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();me.materials.append(obs[0].data.materials[0]);uv=me.uv_layers.new(name='MetreScaled')
 for li,q in enumerate(uvs):uv.data[li].uv=q
 ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);ob['catalogue_id']=AID;ob['collision_contract']='concave_static_surface';ob['spatial_cell_metres']=8
bpy.ops.object.select_all(action='DESELECT')
for ob in parts:ob.select_set(True)
bpy.ops.object.delete(use_global=False)
bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',export_yup=True,export_extras=True)
M={'catalogue_id':AID,'family':FAMILY,'name':'D18 aft receiving foyer and Upper Horizon supported route platform','source':'source/'+AID+'.blend','export':'exports/'+AID+'.glb','source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'export_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'triangles':triangles,'editable_part_count':len(parts),'runtime_mesh_batches':len(batches),'light_marker_count':len(D['light_markers']),'coordinate_contract':'source/section_contract.json','status':'Construction source; verification pending. No operational systems or final art acceptance.'}
(R/(AID+'.manifest.json')).write_text(json.dumps(M,indent=2)+'\n');print(json.dumps(M))
