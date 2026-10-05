"""Editable Upper Horizon enclosure. No floor, lights, furniture or door leaves.
World mapping: Blender=(Godot X,-Godot Z,Godot Y). All new work isolated in this family.
"""
from pathlib import Path
import bpy,bmesh,json,math,sys,hashlib
from mathutils import Vector
R=Path(__file__).resolve().parents[1];C=R.parents[1];AID='AST-CMD-006';FAMILY='upper_horizon_enclosure'
manifest=json.loads((C/'catalogue_manifest.json').read_text())
assert all(a['catalogue_id']!=AID or a['family']==FAMILY for a in manifest['assets'])
D=json.loads((R/'source/section_contract.json').read_text());D['windows']=[]
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
sys.path.insert(0,str(C/'standards'));import staff_materials,materials
mats=staff_materials.materials();mats.update(materials.materials())
for m in mats.values():
 for n in m.node_tree.nodes:
  if n.type=='TEX_IMAGE':n.interpolation='Closest'
opal=mats['staff_opal'].copy();opal.name='ASTRAEA_bridge_threshold_opal';opal['astraea_material_role']='bridge_warm_opal';bs=next(n for n in opal.node_tree.nodes if n.type=='BSDF_PRINCIPLED');bs.inputs['Emission Color'].default_value=(1,.78,.50,1);bs.inputs['Emission Strength'].default_value=.65;mats['bridge_warm_opal']=opal
m=bpy.data.materials.new('ASTRAEA_upper_horizon_protective_glass');m.use_nodes=True;m['meters_per_tile_uv']=[1,1];m['astraea_material_role']='upper_horizon_protective_glass';m.diffuse_color=(.23,.42,.44,.28);bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.23,.42,.44,1);bs.inputs['Roughness'].default_value=.22;bs.inputs['Metallic'].default_value=.08;bs.inputs['Alpha'].default_value=.28;m.surface_render_method='DITHERED';mats['upper_horizon_protective_glass']=m
parts=[];records=[];serials={}
FACES=[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
def segments(a,b,cell=8):
 cuts=[a]+[v for v in range(math.floor(a/cell)*cell,math.ceil(b/cell)*cell+1,cell)if a+1e-7<v<b-1e-7]+[b];return list(zip(cuts,cuts[1:]))
def mesh(name,verts,faces,role,group):
 assembly=name;serial=serials.get(name,0);serials[name]=serial+1;name=name+'__p%03d'%serial
 me=bpy.data.meshes.new(name);me.from_pydata([(x,-z,y)for x,y,z in verts],[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
 ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);me.materials.append(mats[role]);ob['catalogue_id']=AID;ob['collision_contract']='concave_static_surface';ob['group']=group;ob['assembly']=assembly
 lo=[min(v[k]for v in verts)for k in range(3)];hi=[max(v[k]for v in verts)for k in range(3)]
 for k,axis in enumerate('xyz'):ob['cell_'+axis]=math.floor((lo[k]+hi[k])/16)
 uv=me.uv_layers.new(name='MetreScaled');scale=mats[role]['meters_per_tile_uv']
 for f in me.polygons:
  n=f.normal.normalized();u=(Vector((1,0,0))-n*n.x).normalized()if abs(n.z)>.7 else Vector((-n.y,n.x,0)).normalized();v=n.cross(u)
  for li in f.loop_indices:
   q=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=tuple(round(value*8192)/8192 for value in(q.dot(u)/scale[0],q.dot(v)/scale[1]))
 parts.append(ob);records.append({'name':ob.name,'assembly':assembly,'footprint_xz':[[v[0],v[2]]for v in verts[:len(verts)//2]],'world_aabb':[lo[0],hi[0],lo[1],hi[1],lo[2],hi[2]],'vertices_world':verts,'role':role,'group':group});return ob

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

def prism(name,poly,y0,y1,role,group):
 n=len(poly);return mesh(name,[(x,y,z)for y in[y0,y1]for x,z in poly],[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n)for i in range(n)],role,group)
# Deep main roof lands in the old high frame; a separate thin shoulder has no new underside below113.40.
for cell in D['roof_cells']:prism(cell['name'],cell['polygon_xz'],*cell['y'],'staff_white_paint',cell['group'])
def outerhalf(z):
 if z<=139:return 35.9
 if z<=142:return 35.9+(z-139)*8.1/3
 if z<=150:return 44+(z-142)
 if z<=182:return 52
 return 52-(z-182)*.5
# Cross-box ribs overlap BOTH high old longs and the roof skin; no attachment to low edge hangers.
# Longitudinal closed edge beams distribute these rib contacts. This is geometric bearing, not load certification.
for z in [142,148,158,166,174,182,190,198]:
 end=outerhalf(z)-.20
 box('UHE_RootedShoulderRib_Z%s'%z,-end,end,113.40,114.20,z-.22,z+.22,'staff_bluegrey_paint','shoulder_support')
for sign in [-1,1]:
 side='Port'if sign<0 else'Starboard'
 path=[(sign*35.65,138.8),(sign*43.85,142.2),(sign*51.8,150.1),(sign*51.8,181.95),(sign*41.9,201.8)]
 for k,(a,b)in enumerate(zip(path,path[1:])):bar('UHE_'+side+'_ShoulderEave_%d'%k,a,b,.28,113.40,114.23,'champagne_metal','shoulder_support')
 # High longitudinal rib attaches the aft projection to the old X±24 frame via main roof and cross boxes.
 box('UHE_'+side+'_AftShoulderRoot',*sorted([sign*23.72,sign*24.28]),113.40,114.20,188,202,'staff_bluegrey_paint','shoulder_support')
# Raised aft rim is backed by the longitudinal roots. The route beneath remains open pastZ198.
box('UHE_AftShoulderRim',-42,42,113.40,114.23,201.72,202,'champagne_metal','shoulder_support')
# Side shell uses retained backing and has exactly two deliberately lowered framed glass bays.
for sign in [-1,1]:
 side='Port'if sign<0 else'Starboard';x=sign*35.7
 def sb(tag,y0,y1,z0,z1,role='ivory_enamel',depth=.32,group='enclosure'):
  box('UHE_'+side+'_'+tag,x-depth/2,x+depth/2,y0,y1,z0,z1,role,group)
 sb('FoyerOpaque',107.79,114.2,101.96,142)
 sb('FoyerInteriorReveal',110.84,111.06,101.96,142,'champagne_metal',.40,'profile')
 # Broad shared observation ribbon uses unchanged high guards; only two deliberate bays lower the sill.
 for cuts in [[142,148,158,160],[164,166,174,181.7]]:
  for z in cuts:sb('ObservationMullion_Z%s'%str(z).replace('.','p'),107.79,114.20,z-.10,z+.10,'champagne_metal',.36,'window_frame')
  for j,(za,zb)in enumerate(zip(cuts,cuts[1:])):
   tag='SharedWindow_Z%s'%str(za).replace('.','p')
   sb(tag+'_Sill',107.79,107.86,za,zb,'champagne_metal',.36,'window_frame')
   sb(tag+'_Crown',111.05,114.20,za,zb,'ivory_enamel',.36,'window_frame')
   sb(tag+'_Glass',107.84,111.12,za+.08,zb-.08,'upper_horizon_protective_glass',.06,'glass')
   D['windows'].append({'id':side+'_'+tag,'glass_assembly':'UHE_'+side+'_'+tag+'_Glass','a_xz':[x,za+.08],'b_xz':[x,zb-.08],'glass_y':[107.84,111.12],'single_plane':True,'unchanged_guard_top_y':107.82,'clear_aperture_y':[107.86,111.05],'view':'Shared standing observation ribbon; final full-window ray review pending'})
 # Jambs are full-depth and full-height with positive contact to retained/lowered caps and upper roof frame.
 for tag,a,b in [('ForeJamb',160,160.10),('AftJamb',163.90,164)]:sb('LowBay_'+tag,107.36,114.20,a,b,'champagne_metal',.36,'window_frame')
 sb('LowBay_Sill',107.36,107.40,160,164,'champagne_metal',.36,'window_frame')
 sb('LowBay_Header',111.05,114.20,160,164,'ivory_enamel',.36,'window_frame')
 sb('LowBay_HeadSeal',111.05,111.13,160.08,163.92,'staff_zinc',.14,'window_seal')
 # A single closed solid pane, not two parallel rail/pressure panes.
 sb('LowBay_Glass',107.38,111.12,160.08,163.92,'upper_horizon_protective_glass',.06,'glass')
 D['windows'].append({'id':side+'_low_sill','glass_assembly':'UHE_'+side+'_LowBay_Glass','position':[x,109.25,162],'clear_aperture_y':[107.40,111.05],'clear_aperture_z':[160.10,163.90],'glass_aabb':[x-.03,x+.03,107.38,111.12,160.08,163.92],'single_plane':True,'collision':'closed_solid_concave_static','frame_depth':.36,'opaque_top_above_floor':.90,'join_overlap_m':.02})
 marker('DATUM_upper_horizon_'+side.lower()+'_view',[sign*32.9,108.15,161.2 if sign>0 else 162.35],{'programme_key':'D18_directory_09','profile':'bounded_standing_eye_box','not_capacity':True})
 # Glazed fan diagonals and rear wings complete the shared view ribbon over unchanged guards.
 a=(sign*35.7,181.7);b=(sign*25.7,193.7);c=(sign*4.02,193.7)
 for corner,(px,pz)in enumerate([a,b]):
  box('UHE_'+side+'_FanCorner_%d'%corner,px-.23,px+.23,107.79,114.20,pz-.23,pz+.23,'champagne_metal','window_frame')
 for label,start,end in [('Diagonal',a,b),('Rear',b,c)]:
  length=math.dist(start,end);n=math.ceil(length/6);dx=(end[0]-start[0])/length;dz=(end[1]-start[1])/length
  bar('UHE_'+side+'_'+label+'_Sill',start,end,.36,107.79,107.86,'champagne_metal','window_frame')
  bar('UHE_'+side+'_'+label+'_Crown',start,end,.36,111.05,114.20,'ivory_enamel','window_frame')
  for k in range(n+1):
   t=length*k/n;pt=(start[0]+dx*t,start[1]+dz*t)
   # End jamb at the onward side stays outside|X|4.02; existing end cheek owns it.
   if label=='Rear'and k==n:continue
   bar('UHE_'+side+'_'+label+'_Mullion_%d'%k,(pt[0]-dx*.10,pt[1]-dz*.10),(pt[0]+dx*.10,pt[1]+dz*.10),.36,107.79,114.20,'champagne_metal','window_frame')
  for k in range(n):
   ta=length*k/n+.08;tb=length*(k+1)/n-.08;pa=(start[0]+dx*ta,start[1]+dz*ta);pb=(start[0]+dx*tb,start[1]+dz*tb);tag='UHE_'+side+'_'+label+'_Glass_%d'%k
   bar(tag,pa,pb,.06,107.84,111.12,'upper_horizon_protective_glass','glass')
   D['windows'].append({'id':side+'_'+label+'_%d'%k,'glass_assembly':tag,'a_xz':pa,'b_xz':pb,'glass_y':[107.84,111.12],'single_plane':True,'unchanged_guard_top_y':107.82,'clear_aperture_y':[107.86,111.05],'view':'Shared outward standing view; future massing and final composition not accepted'})
 # Cheek outside|X|4.02 has low return contact; it does not shrink the protected8m opening.
 box('UHE_'+side+'_OnwardCheek',*sorted([sign*4.02,sign*4.24]),107.79,114.20,193.50,193.90,'champagne_metal','onward_frame')
# Header clears housing AND optical exit; no static leaf, sill, threshold or invented controller.
box('UHE_OnwardRaisedHeader',-4.18,4.18,112.28,114.20,193.50,193.90,'ivory_enamel','onward_frame')
# Ceiling-edge profile gives the retained grand receiving space an authored perimeter without posts.
# All downward profiles stop outside the selected ray corridor and touch the shell directly.
for sign in[-1,1]:
 side='Port'if sign<0 else'Starboard'
 box('UHE_'+side+'_FoyerCeilingReveal',*sorted([sign*34.9,sign*35.62]),112.26,112.56,102.0,139.0,'warm_walnut','ceiling_profile')
marker('DATUM_origin',[0,0,0]);marker('DATUM_upper_horizon_onward_open',[0,106.5,194],{'state':'unfinished_open_boundary','clear_width_m':8})
D['status']='Bounded source construction candidate; parent integration, route, view and aggregate evidence pending'
(R/'source/section_contract.json').write_text(json.dumps(D,indent=2)+'\n');(R/'source/geometry_parts.json').write_text(json.dumps({'catalogue_id':AID,'parts':records},indent=2)+'\n')
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1;bpy.context.preferences.filepaths.save_version=0;bpy.ops.file.pack_all();src=R/'source'/(AID+'.blend');out=R/'exports'/(AID+'.glb');bpy.ops.wm.save_as_mainfile(filepath=str(src))
triangles=0;batches={}
for ob in parts:
 ob.data.calc_loop_triangles();triangles+=len(ob.data.loop_triangles);key=(ob['cell_x'],ob['cell_y'],ob['cell_z'],ob.data.materials[0].name);batches.setdefault(key,[]).append(ob)
for key,obs in sorted(batches.items()):
 name='UHE_CELL_X%d_Y%d_Z%d_%s'%key;verts=[];faces=[];uvs=[]
 for ob in obs:
  offset=len(verts);verts.extend(tuple(v.co)for v in ob.data.vertices);faces.extend(tuple(i+offset for i in f.vertices)for f in ob.data.polygons);uvs.extend(tuple(v.uv)for v in ob.data.uv_layers.active.data)
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();me.materials.append(obs[0].data.materials[0]);uv=me.uv_layers.new(name='MetreScaled')
 for li,q in enumerate(uvs):uv.data[li].uv=q
 ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);ob['catalogue_id']=AID;ob['collision_contract']='concave_static_surface';ob['spatial_cell_metres']=8
for ob in parts:bpy.data.objects.remove(ob,do_unlink=True)
bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',export_yup=True,export_extras=True)
M={'catalogue_id':AID,'family':FAMILY,'name':'D18 Upper Horizon supported enclosure and two low-sill observation bays','source':'source/'+AID+'.blend','export':'exports/'+AID+'.glb','source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'export_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'triangles':triangles,'editable_part_count':len(parts),'runtime_mesh_batches':len(batches),'light_marker_count':0,'protective_glass_panes':len(D['windows']),'low_sill_bays':2,'coordinate_contract':'source/section_contract.json','status':'Source construction; final art, ship pressure closure and runtime validation pending.'}
(R/(AID+'.manifest.json')).write_text(json.dumps(M,indent=2)+'\n');print(json.dumps(M))
