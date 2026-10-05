"""Original editable D18 central crown. World-origin mapping: Blender=(X,-Z,Y).
No new floors, static moving leaves, furniture or operational command simulation.
"""
from pathlib import Path
import bpy,bmesh,json,math,sys,hashlib
from mathutils import Vector
R=Path(__file__).resolve().parents[1];C=R.parents[1];AID='AST-CMD-001';FAMILY='central_crown'
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
# Programme-specific full enclosures with selected window cuts.
for p in D['programmes']:
 key=p['programme_key'];ring=p['boundary'];x,z=p['entry_xz'];win=p['window_intent'];wx=(36 if win.get('side')=='starboard'else-36)if 'side'in win else None
 for i,(a,b)in enumerate(zip(ring,ring[1:]+ring[:1])):
  axis='x'if a[0]==b[0]else'z';plane=a[0]if axis=='x'else a[1];lo,hi=sorted([a[1],b[1]]if axis=='x'else[a[0],b[0]]);inward=(1 if b[0]>a[0]else-1)if axis=='z'else(-1 if b[1]>a[1]else 1)
  aps=[z]if axis=='x'and abs(plane-x)<1e-6 and lo<z<hi else[]
  wall('CMD_'+key+'_Wall_%02d'%i,axis,plane,lo,hi,inward,aps,win['z_range']if axis=='x'and plane==wx else None)
# Screened corridor inner walls stay out of the public route X±4.
for sign in [-1,1]:
 side='Port'if sign<0 else'Starboard';plane=sign*5;aps=[p['z']for p in D['controlled_crossings']if p['x']*sign>0]
 # Centre on the door plane, rather than copying an unrelated room wall thickness.
 wall('CMD_'+side+'_PublicScreen','x',plane-sign*.08,-78,60,sign,aps)
 # Reset screen plane ap geometry so door plane is exact even though wall lies±0.08 around it.
 # The wall function only positions depth; all ten apertures are the same true frame width/height.
 wall('CMD_'+side+'_NotchClosure','x',sign*10,-78,-70,-sign)
 for zz,inside in [(-78,1),(60,-1)]:wall('CMD_'+side+'_CorridorEnd','z',zz,*sorted([sign*5,sign*10]),inside)
 # Upper corridor beam and shallow coffer rims; no floor runner or raised threshold.
 box('CMD_'+side+'_CorridorCoffer',*sorted([sign*5.08,sign*5.42]),110.65,111,-78,60,'staff_bluegrey_paint','ceiling')
 box('CMD_'+side+'_CorridorRoomRim',*sorted([sign*9.60,sign*9.84]),110.76,111,-78,60,'staff_bluegrey_paint','ceiling')
# Clearances between programmes stay screened; short inboard outer closures fill the gaps.
for sign,gaps in [(-1,[(-28,-24),(14,18)]),(1,[(-28,-24),(28,32)])]:
 for lo,hi in gaps:wall('CMD_InterProgrammeScreen','x',sign*10,lo,hi,sign)
# Ten threshold canopies. Profiles project along entry direction, wholly above the true moving door.
for i,door in enumerate(D['doors']):
 x,y,z=door['position'];s=1 if x>0 else-1;isroom='programme_key'in door
 a,b=sorted([x,x+s*(1.1 if isroom else .55)]);w=1.64 if isroom else 1.50
 profile=[(a,109.54),(b,109.69),(b,109.92),(a,109.92)] if s>0 else[(a,109.69),(b,109.54),(b,109.92),(a,109.92)]
 prism_z('CMD_Threshold_%02d_Profile'%(i+1),profile,z-w,z+w,'staff_bluegrey_paint','threshold')
 box('CMD_Threshold_%02d_Crest'%(i+1),a,b,109.93,110.00,z-w,z+w,'champagne_metal'if isroom and i in [0,2,3]else'staff_zinc','threshold')
 datum(door['marker'],door['position'],{'door_file':door['file'],'yaw_radians':door['yaw'],'programme_key':door.get('programme_key','controlled_crossing')})
# Glazing: closed outward-canted sheets, steel pocketed jambs, continuous lower/upper rails and sloped soffit.
D['windows']=[]
for p in D['programmes']:
 w=p['window_intent']
 if 'side'not in w:continue
 sign=1 if w['side']=='starboard'else-1;lo,hi=w['z_range'];key=p['programme_key'];y0,y1=106.95,110.55
 def at(y):return 35.1+(y-y0)/3.6*.85
 bounds=[lo]+[lo+i*6 for i in range(1,math.ceil((hi-lo)/6))]+[hi]
 for j,(a,b)in enumerate(zip(bounds,bounds[1:])):
  for e,f in segments(a,b):
   profile=[(sign*(at(y0)-.035),y0),(sign*(at(y0)+.035),y0),(sign*(at(y1)+.035),y1),(sign*(at(y1)-.035),y1)]
   prism_z('CMD_'+key+'_Glass_%02d'%j,profile,e,f,'crown_tinted_glass','glazing')
 for q in bounds:
  aa=max(lo,q-.085);bb=min(hi,q+.085)
  profile=[(sign*(at(y0)-.18),y0-.07),(sign*(at(y0)+.045),y0-.07),(sign*(at(y1)+.045),y1+.07),(sign*(at(y1)-.18),y1+.07)]
  prism_z('CMD_'+key+'_CantedMullion',profile,aa,bb,'staff_bluegrey_paint','glazing')
 # End-reveal wedge seals the entire gap from vertical room edge to canted assembly.
 for a,b in [(lo,lo+.12),(hi-.12,hi)]:
  prism_z('CMD_'+key+'_WindowEndReveal',[(sign*34.88,106.88),(sign*36,106.88),(sign*36,110.62),(sign*35.74,110.62)],a,b,'staff_bluegrey_paint','glazing')
 box('CMD_'+key+'_WindowSill',*sorted([sign*34.88,sign*36]),106.86,106.95,lo,hi,'staff_bluegrey_paint','glazing')
 box('CMD_'+key+'_SillMetalLip',*sorted([sign*34.88,sign*35.17]),106.95,107.035,lo,hi,'staff_zinc','glazing')
 box('CMD_'+key+'_WindowHead',*sorted([sign*35.72,sign*36]),110.47,110.64,lo,hi,'staff_bluegrey_paint','glazing')
 for a,b in segments(lo,hi):
  prism_z('CMD_'+key+'_RisingViewSoffit',[(sign*33.90,110.72),(sign*35.76,110.55),(sign*36,111.0),(sign*33.90,111.0)],a,b,'ivory_enamel','ceiling')
 D['windows'].append({'programme_key':key,'side':w['side'],'z_range':[lo,hi],'glass_y':[y0,y1],'glass_centre_abs_x':[35.1,35.95],'glass_thickness_x':.07,'outermost_frame_abs_x':35.995,'mullions_z':bounds,'closed_glass_collision':True})
# One closed roof body, no large outboard canopy. Split before rendering batches.
box('CMD_RoofCeiling',-36,36,111,111.16,-78,64,'staff_white_paint','roof')
for lo,hi,bot,top in D['roof_skin_levels_y']:
 for s in [-1,1]:
  a,b=sorted([s*lo,s*hi]);box('CMD_SteppedRoofSkin',a,b,bot,top,-78,64,'staff_bluegrey_paint','roof')
  # Closed step returns meet adjacent top sheets. Not open planar facades.
  if lo>0:box('CMD_RoofStepReturn',s*lo-.08,s*lo+.08,bot,top+.18,-78,64,'staff_zinc','roof')
for s in [-1,1]:box('CMD_RoofOuterFascia',*sorted([s*35.84,s*36]),110.63,114.04,-78,64,'staff_bluegrey_paint','roof')
for z in [-78,63.84]:box('CMD_RoofEndFascia',-36,36,111,114.04,z,z+.16,'staff_bluegrey_paint','roof')
# Ceilings differ by programme through useful bay rhythm, integrated wall/window transitions and task zones.
for idx,p in enumerate(D['programmes']):
 key=p['programme_key'];sgn=1 if p['entry_xz'][0]>0 else-1;zs=[v[1]for v in p['boundary']];lo,hi=min(zs),max(zs);a,b=sorted([sgn*11.1,sgn*33.9]);depth=[.20,.31,.25,.16,.34,.28][idx]
 box('CMD_'+key+'_InboardCeilingRibbon',*sorted([sgn*11.1,sgn*12.0]),111-depth,111,lo+.3,hi-.3,'staff_bluegrey_paint','ceiling')
 for zz in range(math.ceil((lo+3)/12)*12,math.floor((hi-3)/12)*12+1,12):box('CMD_'+key+'_CeilingCrossRib',a,b,111-depth,111,zz-.14,zz+.14,'staff_zinc'if idx in[1,4,5]else'ivory_enamel','ceiling')
 # Room-wide task fixture rows, with respite's warmer material accent remaining restrained.
 for xx in [17,28]:
  for j,zz in enumerate(range(math.ceil((lo+4)/12)*12,math.floor((hi-4)/12)*12+1,12)):
   x=sgn*xx
   if lo< -70 and zz< -70 and xx<16:continue
   name='CMD_'+key+'_Task_%s_%s'%(xx,j);box(name+'_Housing',x-.72,x+.72,110.62,111,zz-.21,zz+.21,'warm_walnut'if idx==3 else'staff_zinc','fixture');box(name+'_Lens',x-.65,x+.65,110.60,110.62,zz-.15,zz+.15,'staff_opal','fixture');marker='DATUM_light_'+key+'_%s_%s'%(xx,j);p0=[x,110.59,zz];datum(marker,p0,{'profile':'crown_task','direction':'down'});D['light_markers'].append({'name':marker,'position':p0,'direction':[0,-1,0],'profile':'crown_task','programme_key':key,'temperature':'warm'if idx==3 else'cool','suggested_color':[1.0,.84,.68]if idx==3 else[.78,.88,1.0],'suggested_range':10.0,'suggested_spot_angle_degrees':76})
# Gallery and screened corridor source fixtures: directional rows, no hidden point sources.
for x in [-7.5,0,7.5]:
 for z in range(-72,61,12):
  name='CMD_RouteLight_X%s_Z%s'%(str(x).replace('.','p'),z);box(name+'_Housing',x-.2,x+.2,110.58,111,z-.74,z+.74,'staff_zinc','fixture');box(name+'_Lens',x-.15,x+.15,110.56,110.58,z-.67,z+.67,'staff_opal','fixture');mark='DATUM_light_route_%s_%s'%(str(x).replace('.','p'),z);p0=[x,110.55,z];datum(mark,p0,{'profile':'crown_route','direction':'down'});D['light_markers'].append({'name':mark,'position':p0,'direction':[0,-1,0],'profile':'crown_route','temperature':'cool','suggested_color':[.78,.88,1.0],'suggested_range':9.0,'suggested_spot_angle_degrees':70})
# Four segmented bearing spines. Every collar, shoe and face rib stays inside audited0.8×1.2 footprint.
levels=[-3.2,0,6,12,16.5,21,27,35.5,44,52.5,61,69.5,78,84,88.5,93,97.5,102,106.5,111,114]
for x,z in D['support']['pier_centres_xz']:
 tag='X%s_Z%s'%('P'if x>0 else'M','P'if z>0 else'M')
 for n,(ya,yb)in enumerate(zip(levels,levels[1:])):
  box('CMD_Pier_'+tag+'_Web_%02d'%n,x-.32,x+.32,ya,yb,z-.52,z+.52,'staff_bluegrey_paint','pier')
  for sx in [-1,1]:box('CMD_Pier_'+tag+'_Chord',*sorted([x+sx*.30,x+sx*.40]),ya,yb,z-.60,z+.60,'staff_zinc','pier')
  box('CMD_Pier_'+tag+'_Collar_%02d'%n,x-.40,x+.40,ya,min(ya+.20,yb),z-.60,z+.60,'staff_bluegrey_paint','pier')
 datum('DATUM_pier_base_'+tag,[x,-3.2,z]);datum('DATUM_pier_top_'+tag,[x,114,z])
for tie in D['support']['authored_ties']:box(tie['name'],*tie['world_aabb'],'staff_zinc','tie')
# Transverse transfer girders atop four bearings, and three longitudinal members inside the roof.
for z in [-71,71]:
 box('CMD_TransferGirder_Web',-51.5,51.5,111.45,113.82,z-.18,z+.18,'staff_bluegrey_paint','transfer')
 for y in [111.25,113.82]:box('CMD_TransferGirder_Flange',-51.5,51.5,y,y+.18,z-.55,z+.55,'staff_zinc','transfer')
for x in [-32,0,32]:
 box('CMD_Longitudinal_Web',x-.18,x+.18,111.05,113.15,-71.30,71.30,'staff_bluegrey_paint','transfer')
 for y in [111.05,112.99]:box('CMD_Longitudinal_Flange',x-.40,x+.40,y,y+.16,-71.3,71.3,'staff_zinc','transfer')
# Short roof purlins seat ceiling/upper skin to the longitudinal system; no outboard curtain canopy.
for z in range(-72,61,12):box('CMD_RoofPurlin',-35.84,35.84,113.10,113.88,z-.10,z+.10,'staff_bluegrey_paint','roof')
datum('DATUM_origin',[0,0,0]);scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
D['glass_material']='ASTRAEA_crown_tinted_glass';D['glass_batch_name_pattern']='CMD_CELL_X{cell}_Y{cell}_Z{cell}_ASTRAEA_crown_tinted_glass';D['label_backing']={'y':109.65,'room_front_plane_x':[10,-10],'solid_header_y':[109.315,111],'signage_in_source':False}
(R/'source/section_contract.json').write_text(json.dumps(D,indent=2)+'\n');(R/'source/geometry_parts.json').write_text(json.dumps({'catalogue_id':AID,'parts':records},indent=2)+'\n')
bpy.context.preferences.filepaths.save_version=0;bpy.ops.file.pack_all();src=R/'source'/(AID+'.blend');out=R/'exports'/(AID+'.glb');bpy.ops.wm.save_as_mainfile(filepath=str(src))
triangles=0
for o in parts:o.data.calc_loop_triangles();triangles+=len(o.data.loop_triangles)
batches={}
for o in parts:
 key=(o['cell_x'],o['cell_y'],o['cell_z'],o.data.materials[0].name);batches.setdefault(key,[]).append(o)
for key,obs in sorted(batches.items()):
 bpy.ops.object.select_all(action='DESELECT')
 for o in obs:o.select_set(True)
 bpy.context.view_layer.objects.active=obs[0];bpy.ops.object.join();bpy.context.object.name='CMD_CELL_X%d_Y%d_Z%d_%s'%key
bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',export_yup=True,export_extras=True)
manifest={'catalogue_id':AID,'family':FAMILY,'name':'Central D18 six-programme crown shells and four-spine roof frame','source':'source/'+AID+'.blend','export':'exports/'+AID+'.glb','source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'export_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'triangles':triangles,'editable_part_count':len(parts),'runtime_mesh_batches':len(batches),'light_marker_count':len(D['light_markers']),'coordinate_contract':'source/section_contract.json','status':'Editable construction kit; source verification pending; parent owns runtime integration and final art acceptance.'}
(R/(AID+'.manifest.json')).write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(manifest))
