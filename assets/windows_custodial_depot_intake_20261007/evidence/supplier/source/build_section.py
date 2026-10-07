"""Portable WP09 complete source candidate; Blender4.3.2, CPU12. No live writes."""
from pathlib import Path
import bpy,bmesh,math,json,hashlib
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[1]
for d in ('source','exports','qa','renders','docs'):(ROOT/d).mkdir(exist_ok=True)
def dump(p,v):(ROOT/p).write_text(json.dumps(v,indent=2)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
ROW=json.loads((ROOT/'docs/current_allocation.json').read_text())
assert ROW['proposed_portal_xyz']==[8,0,460] and ROW['floor_y']==0
for d in json.loads((ROOT/'docs/dependencies.json').read_text()):assert sha(ROOT/d['package_path'])==d['sha256'],d
bpy.ops.wm.read_factory_settings(use_empty=True)
SC=bpy.context.scene;SC.unit_settings.system='METRIC';SC.unit_settings.scale_length=1
COLL=bpy.data.collections.new('WP09_ARCHITECTURE');SC.collection.children.link(COLL)
PRE=bpy.data.collections.new('SOURCE_PREVIEW_ONLY');SC.collection.children.link(PRE)
MAT={};COLLISIONS=[];INSTANCES=[];LIGHTS=[];PROTO={}
specs=json.loads((ROOT/'dependencies/materials/staff/manifest.json').read_text())['materials']
for role,s in specs.items():
 m=bpy.data.materials.new('WP09_'+role);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=s['roughness'];bs.inputs['Metallic'].default_value=s['metallic']
 tx=m.node_tree.nodes.new('ShaderNodeTexImage');tx.image=bpy.data.images.load(str(ROOT/'dependencies/materials/staff'/s['file']));tx.interpolation='Closest';m.node_tree.links.new(tx.outputs['Color'],bs.inputs['Base Color']);m['meters_per_tile_uv']=s['meters_per_tile_uv'];MAT[role]=m
for role,col in [('cardboard',(.45,.37,.26,1)),('cloth',(.64,.67,.64,1)),('ink',(.026,.052,.06,1)),('amber',(.76,.40,.065,1)),('opal',(.76,.86,1,1))]:
 m=bpy.data.materials.new('WP09_'+role);m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=col;b.inputs['Roughness'].default_value=.8
 if role=='opal':b.inputs['Emission Color'].default_value=col;b.inputs['Emission Strength'].default_value=3
 MAT[role]=m
def p(x,z,h=0):return Vector((x-8,460-z,h))
def uv(o):
 me=o.data;lay=me.uv_layers.new(name='UV_Metric');scale=me.materials[0].get('meters_per_tile_uv',[1,1])
 for f in me.polygons:
  ax=max(range(3),key=lambda k:abs(f.normal[k]));axes=[k for k in range(3) if k!=ax]
  for li in f.loop_indices:
   q=me.vertices[me.loops[li].vertex_index].co;lay.data[li].uv=(q[axes[0]]/scale[0],q[axes[1]]/scale[1])
def poly(name,xz,lo,hi,role='staff_white_paint',preview=False):
 n=len(xz);vs=[tuple(p(x,z,h)) for h in (lo,hi) for x,z in xz];fs=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free()
 o=bpy.data.objects.new(name,me);(PRE if preview else COLL).objects.link(o);me.materials.append(MAT[role]);uv(o);o['package']='WP09';o['export_enabled']=not preview;return o
def box(name,x0,x1,z0,z1,h0,h1,role='staff_white_paint',collision=False,preview=False,bevel=0):
 o=poly(name,[(x0,z0),(x1,z0),(x1,z1),(x0,z1)],h0,h1,role,preview)
 if bevel:m=o.modifiers.new('Folded edge ease','BEVEL');m.width=bevel;m.segments=1
 if collision:COLLISIONS.append({'name':name,'type':'box','local_glb_min':[x0-8,h0,z0-460],'local_glb_max':[x1-8,h1,z1-460]})
 return o
def text(name,body,x,z,h,size=.28,face='south',role='ink'):
 cu=bpy.data.curves.new(name,'FONT');cu.body=body;cu.align_x='CENTER';cu.size=size;cu.extrude=.002;cu.resolution_u=2;o=bpy.data.objects.new(name,cu);COLL.objects.link(o);o.location=p(x,z,h);o.rotation_euler=(math.pi/2,0,0 if face=='south' else math.pi);cu.materials.append(MAT[role]);o['export_enabled']=True;return o
def sign(name,body,x,z,h=2.5,width=5,face='south'):
 box(name+'_backing',x-width/2,x+width/2,z-.055,z+.055,h-.14,h+.48,'staff_bluegrey_paint',bevel=.025)
 text(name,body,x,z+(.061 if face=='south' else -.061),h,.27,face,'staff_label')
def asset(aid,name,x,z,h=0,yaw=0):
 if aid not in PROTO:
  with bpy.data.libraries.load(str(ROOT/'dependencies/native'/f'{aid}.blend'),link=False) as (src,dst):dst.objects=list(src.objects)
  obs=[o for o in dst.objects if o and o.type in {'MESH','EMPTY','CURVE'}]
  # Link complete original hierarchy and evaluate before capturing any transforms.
  for o in obs:COLL.objects.link(o)
  bpy.context.view_layer.update();PROTO[aid]=obs
  for o in obs:
   for m in getattr(o.data,'materials',[]) if o.type in {'MESH','CURVE'} else []:
    if m and m.use_nodes:
     for nd in m.node_tree.nodes:
      if nd.type=='TEX_IMAGE' and nd.image and not nd.image.packed_file:
       found=list((ROOT/'dependencies/materials').rglob(Path(nd.image.filepath).name))
       if found:nd.image.filepath=str(found[0]);nd.image.reload()
   COLL.objects.unlink(o)
 obs=PROTO[aid];mapping={o:o.copy() for o in obs};root=bpy.data.objects.new(name+'_placement',None);COLL.objects.link(root);root.location=p(x,z,h);root.rotation_euler.z=math.radians(yaw);root['source_catalogue_id']=aid
 for orig,o in mapping.items():
  COLL.objects.link(o);o.name=name+'__'+orig.name;o.parent=mapping.get(orig.parent,root);o.matrix_parent_inverse=orig.matrix_parent_inverse.copy();o.matrix_basis=orig.matrix_basis.copy();o['source_catalogue_id']=aid;o['export_enabled']=True
 INSTANCES.append({'name':name,'catalogue_id':aid,'world_xyz':[x,h,z],'yaw_blender_deg':yaw,'native_source_unscaled':True});return root
def light(name,x,z,mount=5.5,power=420):
 asset('AST-STF-006',name+'_native_housing',x-.6,z,mount)
 # Supplement source opaque lens with an integrated opal face; source identity retained.
 box(name+'_opal_face',x-.47,x+.47,z-.11,z+.11,mount-.563,mount-.552,'opal')
 d=bpy.data.lights.new(name+'_effective','POINT');d.energy=power;d.color=(.77,.86,1);d.shadow_soft_size=.43;o=bpy.data.objects.new(name+'_effective',d);COLL.objects.link(o);o.location=p(x,z,mount-.68);o['export_enabled']=True
 LIGHTS.append({'name':name,'world_xyz':[x,mount-.68,z],'watts':power,'support':'native plates/drops on physical ceiling or soffit','fixture':'AST-STF-006','engine_photometry_accepted':False})
def shelf(name,x,z,width=5,depth=1.05):
 # Open shelves: discrete posts/cross braces; never a solid cube collision across access.
 for xx in (x,x+width):
  for zz in (z,z+depth):box(name+'_post',xx-.055,xx+.055,zz-.055,zz+.055,0,3.05,'staff_zinc',True)
 for h in (.20,.92,1.64,2.36):
  box(name+'_shelf',x-.03,x+width+.03,z-.03,z+depth+.03,h-.065,h,'staff_bluegrey_paint',True)
  for j in range(int(width/1.0)):
   xx=x+.16+j*1.02
   # Stock rests on shelf tops; mixed cartons and folded textiles, no inventory claim.
   if j%3:
    box(name+'_carton',xx,xx+.72,z+.10,z+depth-.10,h,h+.43,'cardboard',bevel=.02)
    box(name+'_carton_label',xx+.14,xx+.57,z+depth-.085,z+depth-.078,h+.12,h+.28,'staff_label')
   else:
    for k in range(3):box(name+'_fold',xx,xx+.68,z+.12,z+depth-.12,h+k*.105,h+(k+1)*.105,'cloth',bevel=.025)
 box(name+'_back_brace',x,x+width,z-.02,z+.055,1.45,1.53,'staff_zinc')
 sign(name+'_stock_id',name.replace('_',' ').upper(),x+width/2,z+depth+.055,2.73,width)
def cabinet(name,x,z,yaw=0):
 asset('AST-STF-007',name,x,z,0,yaw)
 # Deliberately leave original cabinet worktop/door sweep empty.
def bench(name,x0,x1,z):
 box(name+'_seat',x0,x1,z-.38,z+.38,.44,.53,'staff_bluegrey_paint',True,bevel=.04)
 for x in (x0+.25,x1-.25):box(name+'_leg',x-.09,x+.09,z-.25,z+.25,0,.44,'staff_zinc',True)
box('SOURCE_PREVIEW_ONLY_floor',8,54,398,466,-.16,0,'staff_floor',preview=True)
box('West_fore',8,8.38,398,458,0,5.7,collision=True);box('West_aft',8,8.38,462,466,0,5.7,collision=True)
box('Portal_lintel',8,10.5,458,462,3.5,5.7,collision=True)
box('East_wall',53.62,54,398,466,0,5.7,collision=True);box('Fore_wall',8.38,53.62,398,398.38,0,5.7,collision=True);box('Aft_wall',8.38,53.62,465.62,466,0,5.7,collision=True)
box('Opaque_supported_ceiling',8,54,398,466,5.5,5.7,collision=True)
for z in (398.5,406,414,422,430,438,446,454,465.4):
 box('Transverse_ceiling_beam',8.35,53.65,z-.18,z+.18,5.03,5.52,'staff_bluegrey_paint')
 for x in (8.65,21.5,30.5,53.35):
  box('Bearing_pier',x-.17,x+.17,z-.22,z+.22,0,5.12,'staff_white_paint',True)
  box('Bearing_cap',x-.29,x+.29,z-.31,z+.31,4.9,5.22,'staff_zinc')
for z in (457.65,462.35):box('Deep_threshold_jamb',8.38,12,z-.15,z+.15,0,3.7,'staff_bluegrey_paint',True)
box('Entry_canopy',8.4,13,457.5,462.5,3.5,3.75,'staff_bluegrey_paint')
light('Entry_practical',10.9,460,3.5,220)
# Dispatch: fitted chamfered counter with lowered return and real staff-side access.
poly('Dispatch_base',[(32,458),(39,458),(40,459),(40,461.2),(39,462.2),(32,462.2)],0,.97,'staff_bluegrey_paint')
poly('Dispatch_worktop',[(31.85,457.85),(39.06,457.85),(40.15,458.94),(40.15,461.26),(39.06,462.35),(31.85,462.35)],.97,1.07,'staff_zinc')
box('Lower_dispatch_top',30.3,32,460.5,462.2,.72,.82,'staff_white_paint',True);box('Lower_dispatch_support',30.5,31.7,460.7,462,0,.72,'staff_bluegrey_paint',True)
sign('Depot_identity','CUSTODIAL  /  DISPATCH',25,465.58,2.7,10,face='north')
bench('Crew_briefing',13.5,20,464.75)
box('Noticeboard',13.2,20.3,465.28,465.48,1.2,2.7,'staff_bluegrey_paint')
for i in range(6):box('Shift_notice',13.5+i,14.15+i,465.25,465.27,1.5,2.25,'staff_label')
for xx in (13.5,20):box('Noticeboard_wall_mount',xx-.09,xx+.09,465.45,465.64,1.35,2.5,'staff_zinc')
text('Board_title','SHIFT NOTES',16.7,465.22,2.4,.25,'north','staff_label')
for xx in (34,36,38):box('Dispatch_folder',xx,xx+.6,459.6,460.0,1.07,1.10,'amber')
# Internal dispatch cabinet room: native threshold used only in its smaller internal role.
box('Dispatch_room_side',43.0,43.25,457,465.6,0,3.7,collision=True)
box('Dispatch_room_front_L',43.25,44.62,457,457.3,0,3.7,collision=True);box('Dispatch_room_front_R',47.38,53.6,457,457.3,0,3.7,collision=True)
box('Dispatch_room_header',44.62,47.38,457,457.3,2.82,3.7,collision=True);box('Dispatch_room_ceiling',43,53.6,457,465.6,3.7,3.9)
asset('AST-STF-008','Dispatch_internal_staff_threshold',46,457.15,0,180)
cabinet('Dispatch_records_cabinet',49.8,464.9,180);light('Dispatch_records_light',49.7,461,3.7,260)
sign('Internal_records_label','RECORDS  /  STAFF',49.3,457.35,2.8,6)
# Three west recessed work bays: no fittings project into the central circulation spine.
for i,z0 in enumerate((423,434,445)):
 name=f'Workbay_{i+1:02d}'
 for zz in (z0,z0+8):box(name+'_end_wall',8.38,20.4,zz,zz+.28,0,3.6,collision=True)
 box(name+'_soffit',8.4,20.4,z0,z0+8.28,3.6,3.8)
 for xx in (9,19.9):box(name+'_soffit_edge',xx-.12,xx+.12,z0,z0+8.28,3.35,3.7,'staff_bluegrey_paint')
 # Authentic panel train on endwall with backing Y0 plane and unscaled pitch.
 for j in range(6):asset('AST-STF-001',name+'_panel_'+str(j),9.0+1.2*j,z0+.28)
 asset('AST-STF-003',name+'_panel_terminal',16.2,z0+.28)
 asset('AST-STF-002',name+'_corner',8.40,z0+.28)
 for j,x in enumerate((10.5,13,15.5)):cabinet(name+'_cabinet_'+str(j),x,z0+1.0)
 shelf(name+'_parts',9.2,z0+6.6,7,1.0)
 sign(name+'_name',['CART WORK','RESTOCK','EQUIPMENT CHECK'][i],14.5,z0+7.98,2.65,9,face='north')
 for xx in (12,18):light(name+'_task'+str(xx),xx,z0+3.7,3.6,290)
 # Empty cart rectangle is source-only marking, no duplicate cart, no route obstruction.
 for zz in (z0+3,z0+5.5):box(name+'_parking_mark',10.3,17.5,zz,zz+.08,.002,.004,'amber',preview=True)
# Fore-west receiving station: used-only carrier bays and purpose-specific workbenches.
box('Receiving_divider',8.4,21.8,418.65,418.9,0,3.4,collision=True)
box('Receiving_soffit',8.4,21.8,405,418.9,3.6,3.8)
for x in (9,21.3):box('Receiving_soffit_bearer',x-.13,x+.13,405,418.9,3.38,3.7,'staff_bluegrey_paint')
for i,x in enumerate((11,14,17,20)):
 asset('AST-HSK-003','Textile_sort_'+str(i),x,416.8,0,180)
 asset('AST-HSK-004','Used_carrier_'+str(i),x,408.5,0,180)
sign('Used_receiving','USED TEXTILES  /  HOLD',15,418.52,2.55,11,face='north')
for xx in (12,18):light('Textile_task_'+str(xx),xx,412.5,3.6,350)
# Reserve and ready stock: low readable long ranges with4m+ transverse breaks.
for zi,z in enumerate((407,413,425,434,443,451)):
 for xi,x in enumerate((32.5,43.2)):shelf(f'Stock_{zi+1:02d}_{xi+1:02d}',x,z,7.5,1.15)
cabinet('Issue_work_cabinet_A',34,453.6,180);cabinet('Issue_work_cabinet_B',37,453.6,180)
sign('Ready_stock_wayfinding','READY STOCK  /  ISSUE',41.5,453.5,3.2,13)
sign('Reserve_wayfinding','RESERVE  /  CHECK',41,418.6,3.2,12)
for name,x,z,w in [('Issue_wayfinding',41.5,453.5,13),('Reserve_wayfinding',41,418.6,12)]:
 for xx in (x-w/2+.3,x+w/2-.3):box(name+'_ceiling_rod',xx-.035,xx+.035,z-.04,z+.04,3.65,5.52,'staff_zinc')
# Overhead utility path uses native1.2m pitches and exact quarter-turn mating seam.
box('Service_run_long_bearing',10.8,26.5,455.6,456.4,5.13,5.5,'staff_bluegrey_paint')
for i in range(12):asset('AST-STF-004','Overhead_dispatch_run_'+str(i),11+1.2*i,456,5.13)
asset('AST-STF-005','Overhead_quarter_turn',25.4,456,5.13)
box('Service_run_spine_bearing',25.58,26.42,407,455.7,5.13,5.5,'staff_bluegrey_paint')
for i in range(40):asset('AST-STF-004','Overhead_spine_run_'+str(i),26,455.4-1.2*i,5.13,90)
box('Service_run_end_terminal',25.64,26.36,407.36,407.44,4.75,5.13,'staff_zinc')
# Effective cool practical lights, each on the actual opaque ceiling.
for x in (14,26,38,49):
 for z in (406,414,422,430,438,446,454,462):
  if (x==14 and z<454) or (x==49 and z==462):continue
  light('Ceiling_practical_'+str(x)+'_'+str(z),x,z,5.03 if z!=462 else 5.5,500)
CAMERAS={
 '01_arrival':((10,460,1.65),(32,460,1.8)),
 '02_dispatch':((25,458.5,1.65),(36,460,1.6)),
 '03_cart_spine':((26.5,453,1.65),(26.5,422,2.0)),
 '04_cart_work':((19.4,439,1.65),(12.5,436,1.5)),
 '05_ready_stock':((39,449,1.65),(41,434,1.8)),
 '06_textile_receiving':((20,412,1.65),(12.5,416,1.4)),
 '07_used_carriers':((19.5,405,1.65),(14,408.5,1.1)),
 '08_overhead_support':((27.7,451,1.65),(26,440,4.7)),
 '09_reserve_stock':((40.8,418,1.65),(40.8,407,1.6)),
 '10_workbay_reverse':((11,448,1.65),(19,450,1.8))}
for name,(eye,target) in CAMERAS.items():
 d=bpy.data.cameras.new(name);d.lens=24;d.clip_end=140;o=bpy.data.objects.new('REVIEW_'+name,d);PRE.objects.link(o);o.location=p(*eye);o.rotation_euler=(p(*target)-o.location).to_track_quat('-Z','Y').to_euler()
SC.camera=bpy.data.objects['REVIEW_01_arrival'];SC.render.engine='CYCLES';SC.cycles.device='CPU';SC.cycles.samples=24;SC.cycles.use_denoising=True;SC.render.threads_mode='FIXED';SC.render.threads=12;SC.render.resolution_x=1280;SC.render.resolution_y=720;SC.render.resolution_percentage=100
SC.world=bpy.data.worlds.new('WP09 restrained ambient');SC.world.use_nodes=True;SC.world.node_tree.nodes['Background'].inputs[0].default_value=(.12,.14,.17,1);SC.world.node_tree.nodes['Background'].inputs[1].default_value=.08;SC.view_settings.view_transform='AgX'
bpy.context.view_layer.update()
missing=[im.filepath for im in bpy.data.images if im.source=='FILE' and not im.packed_file and not Path(bpy.path.abspath(im.filepath)).exists()];assert not missing,missing
bpy.ops.file.pack_all();source=ROOT/'source/WP09_custodial_depot.blend';bpy.ops.wm.save_as_mainfile(filepath=str(source))
bpy.ops.object.select_all(action='DESELECT')
for o in COLL.objects:
 if o.type in {'MESH','CURVE','EMPTY','LIGHT'}:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(ROOT/'exports/WP09_custodial_depot.glb'),export_format='GLB',use_selection=True,export_yup=True,export_extras=True,export_lights=True,export_cameras=False)
dump('docs/floor_contact_proposal.json',{'scope':'source proposal only','frame':'ship Godot metres','floor_y':0,'polygon_xz':[[8,398],[54,398],[54,466],[8,466]],'receiver_portal':[8,0,460],'external_link_x':[4,8],'external_link_owner':'Higgins unbuilt','asset_floor_exported':False,'parent_to_choose_single_floor_owner':True,'no_cross_datum_cuts':True})
plan=json.loads((ROOT/'docs/plan_contract.json').read_text())
route_hits=[]
for route in plan['reserved_clear_routes']:
 a,b,c,d=route['rect_xz']
 for primitive in COLLISIONS:
  lo,hi=primitive['local_glb_min'],primitive['local_glb_max']
  if lo[1]>=2.65 or hi[1]<=0:continue
  if min(b,hi[0]+8)-max(a,lo[0]+8)>.005 and min(d,hi[2]+460)-max(c,lo[2]+460)>.005:route_hits.append({'route':route['id'],'primitive':primitive['name']})
dump('qa/reserved_routes.json',{'scope':'authored primitive AABB reservation screen only; native fixture/actor/sweep runtime not covered','low_geometry_intersections':route_hits,'passed':not route_hits})
assert not route_hits,route_hits
dump('docs/collision_proposal.json',{'scope':'source primitive proposals; no runtime acceptance','frame':'package-local GLB Y-up origin[8,0,460]','primitives':COLLISIONS,'asset_collisions':'retain original semantic contact/voids; no blanket hull across shelf/cabinet/threshold','runtime_accepted':False})
dump('docs/instances.json',INSTANCES);dump('docs/lights.json',LIGHTS);dump('docs/cameras.json',CAMERAS)
dump('qa/build_receipt.json',{'blender_version':bpy.app.version_string,'source_sha256':sha(source),'glb_sha256':sha(ROOT/'exports/WP09_custodial_depot.glb'),'mesh_objects':len([o for o in COLL.objects if o.type=='MESH']),'light_count':len(LIGHTS),'source_images_missing':missing,'normal_eye_visual_review':'pending','native_reopen':'pending','live_integration':False,'claim':'complete fitted source candidate, no live acceptance'})
print('WP09_SOURCE_BUILD_COMPLETE',str(source),flush=True)
