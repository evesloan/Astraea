"""Original editable D18 central crown. World-origin mapping: Blender=(X,-Z,Y).
No new floors, static moving leaves, furniture or operational command simulation.
"""
from pathlib import Path
import bpy,bmesh,json,math,sys,hashlib
from mathutils import Vector
R=Path(__file__).resolve().parents[1];C=R.parents[1];AID='AST-CMD-002';FAMILY='aft_command'
assert all(a['catalogue_id']!=AID or a['family']==FAMILY for a in json.loads((C/'catalogue_manifest.json').read_text())['assets'])
D=json.loads((R/'source/section_contract.json').read_text());D['light_markers']=[]
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
sys.path.insert(0,str(C/'standards'));import staff_materials,materials
mats=staff_materials.materials();common=materials.materials();mats.update({k:common[k]for k in ['ivory_enamel','champagne_metal','warm_walnut']})
for m in mats.values():
 for n in m.node_tree.nodes:
  if n.type=='TEX_IMAGE':n.interpolation='Closest'
bs=next(n for n in mats['staff_opal'].node_tree.nodes if n.type=='BSDF_PRINCIPLED');bs.inputs['Emission Color'].default_value=(.78,.88,.94,1);bs.inputs['Emission Strength'].default_value=.6
m=bpy.data.materials.new('ASTRAEA_crown_tinted_glass');m.use_nodes=True;m['meters_per_tile_uv']=[1,1];m['astraea_material_role']='crown_tinted_glass';m.diffuse_color=(.26,.46,.51,.20)
bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.26,.46,.51,1);bs.inputs['Roughness'].default_value=.19;bs.inputs['Metallic'].default_value=.08;bs.inputs['Alpha'].default_value=.20;m.surface_render_method='DITHERED';mats['crown_tinted_glass']=m
parts=[];records=[]
def segments(a,b,cell=12):
 cuts=[a]+[v for v in range(math.floor(a/cell)*cell,math.ceil(b/cell)*cell+1,cell)if a+1e-6<v<b-1e-6]+[b];return list(zip(cuts,cuts[1:]))
def mesh(name,verts,faces,role,group='shell'):
 me=bpy.data.meshes.new(name);me.from_pydata([(x,-z,y)for x,y,z in verts],[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
 ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);me.materials.append(mats[role]);ob['catalogue_id']=AID;ob['collision_contract']='concave_static_surface';ob['group']=group
 lo=[min(v[k]for v in verts)for k in range(3)];hi=[max(v[k]for v in verts)for k in range(3)]
 for k,axis in enumerate('xyz'):ob['cell_'+axis]=math.floor((lo[k]+hi[k])/24)
 uv=me.uv_layers.new(name='MetreScaled');scale=mats[role]['meters_per_tile_uv']
 for f in me.polygons:
  n=f.normal.normalized();u=(Vector((1,0,0))-n*n.x).normalized()if abs(n.z)>.7 else Vector((-n.y,n.x,0)).normalized();v=n.cross(u)
  for li in f.loop_indices:
   q=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(q.dot(u)/scale[0],q.dot(v)/scale[1])
 parts.append(ob);records.append({'name':ob.name,'world_aabb':[lo[0],hi[0],lo[1],hi[1],lo[2],hi[2]],'vertices_world':verts,'role':role,'group':group});return ob
FACES=[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
def box(name,x0,x1,y0,y1,z0,z1,role='staff_bluegrey_paint',group='shell'):
 assert x1>x0 and y1>y0 and z1>z0,(name,x0,x1,y0,y1,z0,z1)
 for a,b in segments(x0,x1):
  for c,d in segments(y0,y1):
   for e,f in segments(z0,z1):mesh(name,[(x,y,z)for y in [c,d]for x,z in [(a,e),(b,e),(b,f),(a,f)]],FACES,role,group)
def prism_z(name,profile,z0,z1,role,group='shell'):
 # Closed profile in worldXY, extruded along Z. Recalculate outward normals.
 n=len(profile);v=[(x,y,z)for z in [z0,z1]for x,y in profile];f=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n)for i in range(n)];return mesh(name,v,f,role,group)
def datum(name,p,extras=None):
 o=bpy.data.objects.new(name,None);bpy.context.collection.objects.link(o);o.location=(p[0],-p[2],p[1]);o.empty_display_size=.12
 if extras:
  for k,v in extras.items():o[k]=v
 return o
def wall(name,axis,plane,lo,hi,inward,apertures=(),window=None):
 cuts=[lo,hi]
 for ap in apertures:cuts.extend([max(lo,ap-1.375),min(hi,ap+1.375)])
 if window:cuts.extend([max(lo,window[0]),min(hi,window[1])])
 cuts=sorted(set(cuts))
 for i,(a,b)in enumerate(zip(cuts,cuts[1:])):
  if b-a<1e-5:continue
  mid=(a+b)/2;isdoor=any(abs(mid-ap)<1.375 for ap in apertures);iswindow=window and window[0]<mid<window[1]
  ranges=[(109.315,111,'staff_white_paint')]if isdoor else ([(106.5,106.95,'staff_bluegrey_paint'),(110.55,111,'staff_white_paint')]if iswindow else [(106.5,107.6,'staff_bluegrey_paint'),(107.6,111,'staff_white_paint')])
  t0,t1=sorted([plane,plane+inward*.16]);label=name+'_%02d'%i
  for y0,y1,role in ranges:
   box(label,a,b,y0,y1,t0,t1,role)if axis=='z'else box(label,t0,t1,y0,y1,a,b,role)
  if not isdoor and not iswindow:
   q0,q1=sorted([plane+inward*.16,plane+inward*.19]);box(label+'_LowRail',a,b,107.30,107.43,q0,q1,'staff_zinc')if axis=='z'else box(label+'_LowRail',q0,q1,107.30,107.43,a,b,'staff_zinc')
   for q in range(math.ceil(a/6)*6,math.floor(b/6)*6+1,6):
    if q-.035<a or q+.035>b:continue
    box(label+'_PanelStile',q-.025,q+.025,107.6,110.77,q0,q1,'staff_bluegrey_paint')if axis=='z'else box(label+'_PanelStile',q0,q1,107.6,110.77,q-.025,q+.025,'staff_bluegrey_paint')
# Two programme enclosures retain original command allocations, without new floor bodies.
for p in D['programmes']:
 key=p['programme_key'];ring=p['boundary'];x,z=p['entry_xz']
 for i,(a,b) in enumerate(zip(ring,ring[1:]+ring[:1])):
  axis='x'if a[0]==b[0]else'z';plane=a[0]if axis=='x'else a[1];lo,hi=sorted([a[1],b[1]]if axis=='x'else[a[0],b[0]]);inward=(1 if b[0]>a[0]else-1)if axis=='z'else(-1 if b[1]>a[1]else 1)
  wall('AFC_'+key+'_Wall_%02d'%i,axis,plane,lo,hi,inward,[z]if axis=='x'and plane==x else[])
for sign in [-1,1]:
 side='Port'if sign<0 else'Starboard'
 wall('AFC_'+side+'_PublicScreen','x',sign*4.92,66.2,102,sign)
 wall('AFC_'+side+'_FrontReturn','z',66.2,*sorted([sign*5,sign*10]),1,[sign*7.5])
 wall('AFC_'+side+'_AftReturn','z',102,*sorted([sign*5,sign*10]),-1)
 box('AFC_'+side+'_CorridorCoffer',*sorted([sign*5.08,sign*5.42]),110.65,111,66.2,102,'staff_bluegrey_paint','ceiling')
 box('AFC_'+side+'_CorridorRoomRim',*sorted([sign*9.60,sign*9.84]),110.76,111,66.2,102,'staff_bluegrey_paint','ceiling')
# Deep profiled room portals and restrained controlled corridor entry hoods.
for i,door in enumerate(D['doors']):
 x,y,z=door['position'];isroom='programme_key'in door;depth=1.1 if isroom else.55;w=1.64 if isroom else 1.50;co,si=math.cos(door['yaw']),math.sin(door['yaw'])
 def pt(width,back,height):return(x+co*width-si*back,height,z-si*width-co*back)
 vs=[pt(wi,de,he)for wi,de,he in[(-w,0,109.54),(w,0,109.54),(w,depth,109.69),(-w,depth,109.69),(-w,0,109.92),(w,0,109.92),(w,depth,109.92),(-w,depth,109.92)]]
 mesh('AFC_Threshold_%02d_Profile'%(i+1),vs,FACES,'staff_bluegrey_paint','threshold')
 vs=[pt(wi,de,he)for he in[109.93,110]for wi,de in[(-w,0),(w,0),(w,depth),(-w,depth)]];mesh('AFC_Threshold_%02d_Crest'%(i+1),vs,FACES,'staff_zinc','threshold')
 datum(door['marker'],door['position'],{'door_file':door['file'],'yaw_radians':door['yaw'],'programme_key':door.get('programme_key','controlled_crossing')})
# Closed roof extends by a butt joint at Z64; the six-room source roof is untouched.
box('AFC_RoofCeiling',-36,36,111,111.16,64,102,'staff_white_paint','roof')
for lo,hi,bot,top in D['roof_skin_levels_y']:
 for sign in [-1,1]:
  box('AFC_SteppedRoofSkin',*sorted([sign*lo,sign*hi]),bot,top,64,102,'staff_bluegrey_paint','roof')
  if lo>0:box('AFC_RoofStepReturn',sign*lo-.08,sign*lo+.08,bot,top+.18,64,102,'staff_zinc','roof')
for sign in [-1,1]:box('AFC_RoofOuterFascia',*sorted([sign*35.84,sign*36]),111.16,113.84,64,102,'staff_bluegrey_paint','roof')
for lo,hi,bot,top in D['roof_skin_levels_y']:
 for sign in [-1,1]:box('AFC_RoofAftFascia',*sorted([sign*lo,sign*hi]),111.16,bot,101.84,102,'staff_bluegrey_paint','roof')
# Useful ceiling bay hierarchy and continuous sheltered service edge, not furniture decoration.
for index,p in enumerate(D['programmes']):
 key=p['programme_key'];sign=-1 if index==0 else 1;depth=.22 if index==0 else.36
 box('AFC_'+key+'_ServiceEdgeCoffer',*sorted([sign*10.16,sign*14.0]),110.52,111,66.16,101.84,'staff_bluegrey_paint','ceiling')
 for z in [70,82,94]:
  box('AFC_'+key+'_CofferReturn',*sorted([sign*14,sign*35.84]),111-depth,111,z-.14,z+.14,'staff_zinc','ceiling')
 for xx in [18,28]:
  for j,z in enumerate([72,84,96]):
   x=sign*xx;name='AFC_'+key+'_Task_%s_%s'%(xx,j);box(name+'_Housing',x-.72,x+.72,110.62,111,z-.21,z+.21,'staff_zinc','fixture');box(name+'_Lens',x-.65,x+.65,110.60,110.62,z-.15,z+.15,'staff_opal','fixture');marker='DATUM_light_aft_'+key+'_%s_%s'%(xx,j);pos=[x,110.59,z];datum(marker,pos,{'profile':'crown_task','direction':'down'});D['light_markers'].append({'name':marker,'position':pos,'direction':[0,-1,0],'profile':'crown_task','programme_key':key,'temperature':'cool','suggested_color':[.78,.88,1.0],'suggested_range':10.0,'suggested_spot_angle_degrees':76})
for x in [-7.5,0,7.5]:
 for z in [70,82,94,100]if x!=0 else[70,82,94,100]:
  name='AFC_RouteLight_X%s_Z%s'%(str(x).replace('.','p'),z);box(name+'_Housing',x-.2,x+.2,110.58,111,z-.74,z+.74,'staff_zinc','fixture');box(name+'_Lens',x-.15,x+.15,110.56,110.58,z-.67,z+.67,'staff_opal','fixture');marker='DATUM_light_aft_route_%s_%s'%(str(x).replace('.','p'),z);pos=[x,110.55,z];datum(marker,pos,{'profile':'crown_route','direction':'down'});D['light_markers'].append({'name':marker,'position':pos,'direction':[0,-1,0],'profile':'crown_route','temperature':'cool','suggested_color':[.78,.88,1.0],'suggested_range':9.0,'suggested_spot_angle_degrees':70})
# Cross-street source lights hang directly from the existing unchanged crown roof.
# Their complete housings stay above the standing belt and all emission starts below the real lens.
for x in [-30,-18,-6,6,18,30]:
 z=63;name='AFC_CrossStreetLight_X%s'%x
 box(name+'_Housing',x-.72,x+.72,110.58,111,z-.21,z+.21,'staff_zinc','fixture')
 box(name+'_Lens',x-.65,x+.65,110.56,110.58,z-.15,z+.15,'staff_opal','fixture')
 marker='DATUM_light_aft_cross_street_X%s'%x;pos=[x,110.55,z]
 datum(marker,pos,{'profile':'crown_route','direction':'down'})
 D['light_markers'].append({'name':marker,'position':pos,'direction':[0,-1,0],'profile':'crown_route','temperature':'cool','suggested_color':[.78,.88,1.0],'suggested_range':9.0,'suggested_spot_angle_degrees':76,'support':'Existing AST-CMD-001 roof underside Y111; no old source changed'})
# Full-height audited bearing envelopes. Every web/chord/collar stays inside 0.8 by1.2m.
levels=[-3.2,0,6,12,16.5,21,27,35.5,44,52.5,61,69.5,78,84,88.5,93,97.5,102,106.5,111,114]
for x,z in D['support']['pier_centres_xz']:
 tag='Port'if x<0 else'Starboard'
 for n,(ya,yb) in enumerate(zip(levels,levels[1:])):
  box('AFC_Pier_'+tag+'_Web_%02d'%n,x-.32,x+.32,ya,yb,z-.52,z+.52,'staff_bluegrey_paint','pier')
  for sx in [-1,1]:box('AFC_Pier_'+tag+'_Chord',*sorted([x+sx*.30,x+sx*.40]),ya,yb,z-.60,z+.60,'staff_zinc','pier')
  box('AFC_Pier_'+tag+'_Collar_%02d'%n,x-.4,x+.4,ya,min(ya+.2,yb),z-.6,z+.6,'staff_bluegrey_paint','pier')
 datum('DATUM_aft_pier_base_'+tag,[x,-3.2,z]);datum('DATUM_aft_pier_top_'+tag,[x,114,z])
# New transverse roof frame and seven explicit positive overlaps to existing Z71 frame.
box('AFC_TransferGirder_Web',-35.5,35.5,111.40,113.82,85.82,86.18,'staff_bluegrey_paint','transfer')
for y in [111.25,113.82]:box('AFC_TransferGirder_Flange',-35.5,35.5,y,y+.18,85.45,86.55,'staff_zinc','transfer')
for x in D['support']['roof_link_x']:
 box('AFC_Longitudinal_Web',x-.16,x+.16,111.10,113.80,70.80,101.84,'staff_bluegrey_paint','transfer')
 for y in [111.10,113.70]:box('AFC_Longitudinal_Flange',x-.30,x+.30,y,y+.20,70.80,101.84,'staff_zinc','transfer')
# New foremost purlin seats directly on the lower existing longitudinal crown beams.
for x in [-32,0,32]:box('AFC_ForwardPurlinSaddle',x-.22,x+.22,113.05,113.85,65.72,66.28,'staff_zinc','transfer')
for z in [66,74,82,90,98,101.8]:box('AFC_RoofPurlin',-35.84,35.84,113.76,114.27,z-.10,z+.10,'staff_bluegrey_paint','roof')
# Hangers are inside wall zones rather than the public belt. Their lower ends positively overlap edge girders.
for x in D['support']['hanger_x']:
 for z in D['support']['hanger_z']:
  box('AFC_Hanger_X%s_Z%s'%(str(x).replace('.','p'),z),x-.10,x+.10,106.05,113.82,z-.18,z+.18,'staff_zinc','hanger')
# Under-platform edge girders seat into the single parent-owned slab by20mm; no floor surface is authored here.
for x in D['support']['floor_edge_girder_x']:
 box('AFC_FloorEdgeGirder_Web',x-.12,x+.12,105.84,106.27,79.80,102,'staff_bluegrey_paint','platform_support')
 for y in [105.84,106.16]:box('AFC_FloorEdgeGirder_Flange',x-.28,x+.28,y,y+.12,79.80,102,'staff_zinc','platform_support')
for z in D['support']['floor_cross_bearer_z']:
 for sign in [-1,1]:
  box('AFC_PlatformCrossBearer',*sorted([sign*4,sign*36]),105.88,106.28,z-.12,z+.12,'staff_bluegrey_paint','platform_support')
for tie in D['support']['authored_ties']:box(tie['name'],*tie['world_aabb'],'staff_zinc','tie')
datum('DATUM_origin',[0,0,0]);scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
D['windows']=[]
(R/'source/section_contract.json').write_text(json.dumps(D,indent=2)+'\n');(R/'source/geometry_parts.json').write_text(json.dumps({'catalogue_id':AID,'parts':records},indent=2)+'\n')
bpy.context.preferences.filepaths.save_version=0;bpy.ops.file.pack_all();src=R/'source'/(AID+'.blend');out=R/'exports'/(AID+'.glb');bpy.ops.wm.save_as_mainfile(filepath=str(src))
triangles=0
for o in parts:o.data.calc_loop_triangles();triangles+=len(o.data.loop_triangles)
batches={}
for o in parts:
 key=(o['cell_x'],o['cell_y'],o['cell_z'],o.data.materials[0].name);batches.setdefault(key,[]).append(o)
# Build equivalent spatial render batches without hundreds of context-sensitive join operators.
for key,obs in sorted(batches.items()):
 name='AFC_CELL_X%d_Y%d_Z%d_%s'%key;verts=[];faces=[];uvs=[]
 for o in obs:
  offset=len(verts);verts.extend(tuple(v.co)for v in o.data.vertices);faces.extend(tuple(i+offset for i in f.vertices)for f in o.data.polygons);uvs.extend(tuple(v.uv)for v in o.data.uv_layers.active.data)
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();me.materials.append(obs[0].data.materials[0]);uv=me.uv_layers.new(name='MetreScaled')
 for li,q in enumerate(uvs):uv.data[li].uv=q
 ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);ob['catalogue_id']=AID;ob['collision_contract']='concave_static_surface';ob['spatial_cell_metres']=12
bpy.ops.object.select_all(action='DESELECT')
for o in parts:o.select_set(True)
bpy.ops.object.delete(use_global=False)
bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',export_yup=True,export_extras=True)
manifest={'catalogue_id':AID,'family':FAMILY,'name':'Aft D18 two-command shells and suspended-platform roof support','source':'source/'+AID+'.blend','export':'exports/'+AID+'.glb','source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'export_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'triangles':triangles,'editable_part_count':len(parts),'runtime_mesh_batches':len(batches),'light_marker_count':len(D['light_markers']),'coordinate_contract':'source/section_contract.json','status':'Editable construction kit; source verification pending; parent owns runtime integration and final art acceptance.'}
(R/(AID+'.manifest.json')).write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(manifest))
