"""Astraea Cinema/Library receiving candidate r001. Script-assisted editable original.
Run only in an allocated Blender slot: blender -b -t 2 --python this_file -- --out DIR.
Root-owned source only, world metres; Blender=(X,-Z,Y), GLB=(X,Y,Z).
No source-room writes, engine imports or certification claims.
"""
import bpy, math, json, sys, hashlib, importlib.util
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
ARGS=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
OUT=Path(ARGS[ARGS.index('--out')+1]) if '--out' in ARGS else Path(__file__).resolve().parents[1]
CAT=Path('/workspace/shared/Astraea_recovery_20261007_AXWr5x/BlenderCatalogue')
ASSET='AST-RCV-CL-001'; REV='receiving-r001-20261007'
assert ASSET not in (CAT/'catalogue_manifest.json').read_text(), 'New-family ID already assigned; inspect ownership before continuing'
for k in ['source','exports','qa','views']: (OUT/k).mkdir(exist_ok=True)
for p,h in json.loads((OUT/'inputs/source_pins.json').read_text()).items():
 if not p.endswith('catalogue_manifest.json'): assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h,p
bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene; scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
scene.render.threads_mode='FIXED';scene.render.threads=2
spec=importlib.util.spec_from_file_location('astraea_materials',CAT/'standards/auditorium_materials.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);M=m.materials()
COL={}
for name in ['A01_D11_BOUNDARY_PLATE','A02_FIFTEEN_PIERS','A03_FIVE_TRANSVERSE_TRUSSES','A04_LONGITUDINAL_GRID','A05_LIBRARY_SLAB_AND_FEET','A06_SERVICE_BRANCHES','Z00_NONEXPORT_RESERVATIONS','Z01_QA_ONLY']:
 c=bpy.data.collections.new(name);scene.collection.children.link(c);COL[name]=c
ROOT=bpy.data.objects.new(ASSET,None);COL['Z00_NONEXPORT_RESERVATIONS'].objects.link(ROOT)
ROOT['asset_id']=ASSET;ROOT['status']='Authored receiving candidate; source-only; NOT installed';ROOT['world_metres_mapping']='Blender=(X,-Z,Y); exchange=(X,Y,Z)';ROOT['revision']=REV
GEOM=[];CONTACTS=[];DETAILS=[]
def xyz(p): return (p[0],-p[2],p[1])
def world(v): return [v.x,v.z,-v.y]
def mesh(name,verts,faces,role,col,group,bounds=None):
 me=bpy.data.meshes.new(name);me.from_pydata([xyz(v) for v in verts],[],faces);me.update();o=bpy.data.objects.new(name,me);COL[col].objects.link(o);o.data.materials.append(M[role]);o['asset_id']=ASSET;o['owner']='root';o['authoring_status']='authored_receiving_candidate';o['semantic_group']=group;o['astraea_material_role']=role;o['collision_owner']='root_candidate_only';
 import bmesh
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free();
 uv=me.uv_layers.new(name='UVMap'); tile=M[role].get('meters_per_tile_uv',1); tile=(tile,tile) if isinstance(tile,(int,float)) else tuple(tile)
 for poly in me.polygons:
  n=poly.normal; ax=max(range(3),key=lambda i:abs(n[i]));axes=([1,2],[0,2],[0,1])[ax]
  for li in poly.loop_indices:
   v=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]]/tile[0],v[axes[1]]/tile[1])
 lo=[min(v[i] for v in verts) for i in range(3)];hi=[max(v[i] for v in verts) for i in range(3)]
 o['world_min_xyz']=lo;o['world_max_xyz']=hi
 if bounds: o['reservation_id']=bounds
 GEOM.append(o);return o
FACES=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
def box(name,lo,hi,role,col,group,bounds=None):
 a,b,c=lo;d,e,f=hi
 return mesh(name,[(a,b,c),(d,b,c),(d,b,f),(a,b,f),(a,e,c),(d,e,c),(d,e,f),(a,e,f)],FACES,role,col,group,bounds)
def extrusion(name,poly,y0,y1,role,col,group,bounds=None):
 n=len(poly);v=[(x,y,z) for y in [y0,y1] for x,z in poly];tri=tessellate_polygon([[Vector((x,z,0)) for x,z in poly]])
 lookup={(round(x,6),round(z,6)):i for i,(x,z) in enumerate(poly)};faces=[]
 for t in tri:
  inds=tuple((q if isinstance(q,int) else lookup[(round(q.x,6),round(q.y,6))]) for q in t);faces.extend([inds,tuple(i+n for i in inds)])
 faces += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 return mesh(name,v,faces,role,col,group,bounds)
def profile_rect(x,z,w,d,c=.10):
 return [(x-w/2+c,z-d/2),(x+w/2-c,z-d/2),(x+w/2,z-d/2+c),(x+w/2,z+d/2-c),(x+w/2-c,z+d/2),(x-w/2+c,z+d/2),(x-w/2,z+d/2-c),(x-w/2,z-d/2+c)]
def taper(name,x,z,levels,role,col,group,bounds):
 verts=[]
 for y,w,d,c in levels:verts += [(xx,y,zz) for xx,zz in profile_rect(x,z,w,d,c)]
 faces=[tuple(range(7,-1,-1)),tuple(range((len(levels)-1)*8,len(levels)*8))]
 for k in range(len(levels)-1):
  for i in range(8):faces.append((k*8+i,k*8+(i+1)%8,(k+1)*8+(i+1)%8,(k+1)*8+i))
 return mesh(name,verts,faces,role,col,group,bounds)
def xy_web(name,xa,xb,y0,y1,z,dep,rising,col,group,bounds):
 # Horizontal cut ends contact the chord surfaces exactly; twin side-plane webs.
 w=min(.22,(xb-xa)*.2)
 p=[(xa,y0),(xa+w,y0),(xb,y1),(xb-w,y1)] if rising else [(xa,y1),(xa+w,y1),(xb,y0),(xb-w,y0)]
 vs=[(x,y,zz) for zz in [z-dep/2,z+dep/2] for x,y in p]
 return mesh(name,vs,FACES,'ivory_enamel',col,group,bounds)
def zy_web(name,za,zb,y0,y1,x,dep,rising,col,group,bounds):
 w=min(.22,(zb-za)*.2);p=[(za,y0),(za+w,y0),(zb,y1),(zb-w,y1)] if rising else [(za,y1),(za+w,y1),(zb,y0),(zb-w,y0)]
 vs=[(xx,y,z) for xx in [x-dep/2,x+dep/2] for z,y in p]
 return mesh(name,vs,FACES,'ivory_enamel',col,group,bounds)
def contact(name,lower,upper,axis,plane,footprint,status='internal_exact_contact'):
 CONTACTS.append(dict(id=name,lower=lower,upper=upper,axis=axis,world_plane=plane,footprint=footprint,status=status))
# Closed exact floor union: Cinema eight-point footprint plus bounded west strip, no core infill.
p=json.loads((OUT/'inputs/floor_and_receivers.json').read_text())['floor_polygon_world_xz']
poly=[(8,-466),(11.4,-466),(11.4,-464.1),(15.1,-467.8),(56.9,-467.8),(60.8,-463.9),(60.8,-400.1),(56.9,-396.2),(15.1,-396.2),(11.4,-399.9),(11.4,-398),(8,-398)]
floor=extrusion('D11_ExactCinemaPlusWestStrip_UNION',poly,69.26,69.50,'warm_stone','A01_D11_BOUNDARY_PLATE','D11_floor')
floor['source_cinema_polygon_json']=json.dumps(p);floor['bounded_west_strip_json']=json.dumps([8,11.4,-466,-398]);floor['protected_adjacent_boundary']='Sunward top at Y69.26; no geometry below'
stations=[-462.6,-450.8,-435,-419,-400.2];xs=[9,13,59]
# 15 intentional chamfered, slightly flared pier bodies, separate exact-touch feet/shoes/caps.
for iz,z in enumerate(stations):
 for x in xs:
  g=f'P{iz+1}_X{x}';res=f'ROOT_C11_BEAR_X{x}_Z{z:g}';col='A02_FIFTEEN_PIERS'
  foot=taper(g+'_StoneFoot',x,z,[(69.50,.98,1.18,.12),(69.63,.98,1.18,.12),(69.72,.84,1.04,.10)],'warm_stone',col,g,res)
  shoe=taper(g+'_SteelShoe',x,z,[(69.72,.84,1.04,.10),(69.84,.84,1.04,.10)],'champagne_metal',col,g,res)
  core=taper(g+'_FacetedCore',x,z,[(69.84,.70,.86,.12),(70.15,.66,.82,.11),(74.98,.66,.82,.11),(75.18,.74,.94,.12)],'ivory_enamel',col,g,res)
  cap=taper(g+'_ShoulderedCapital',x,z,[(75.18,.74,.94,.12),(75.43,.98,1.18,.12),(75.53,.98,1.18,.12)],'warm_stone',col,g,res)
  plate=box(g+'_BearingPlate',[x-.49,75.53,z-.59],[x+.49,75.65,z+.59],'champagne_metal',col,g,res)
  # Recessed-looking vertical inlay on flat side face; sits on the outside, with own thickness.
  for s in [-1,1]:
   zz=z+s*.410
   box(g+f'_Reveal_{s}',[x-.14,70.20,min(zz,zz+s*.016)],[x+.14,74.92,max(zz,zz+s*.016)],'warm_walnut',col,g,res)
  for a,b,y in [(floor,foot,69.50),(foot,shoe,69.72),(shoe,core,69.84),(core,cap,75.18),(cap,plate,75.53)]: contact(g+'_'+str(y),a.name,b.name,'Y',y,profile_rect(x,z,.66,.82,.11))
# I-profile chord construction, twin Warren webs and end-node posts; zero coarse overlap.
rails=[(9,1),(13,1),(25,.8),(40,.8),(53.8,.4),(59,1)]
for iz,z in enumerate(stations):
 g=f'TRUSS_{iz+1}';res=f'ROOT_C12_TRANSFER_Z{z:g}';col='A03_FIVE_TRANSVERSE_TRUSSES'
 chordparts=[]
 for tag,y0,y1 in [('Bottom',75.65,75.99),('Top',77.42,77.76)]:
  for part,ya,yb,d in [('lower_flange',y0,y0+.10,1.0),('web',y0+.10,y1-.10,.24),('upper_flange',y1-.10,y1,1.0)]:
   o=box(g+'_'+tag+'_'+part,[8.5,ya,z-d/2],[59.5,yb,z+d/2],'champagne_metal' if 'flange' in part else 'auditorium_navy_fibre',col,g,res);chordparts.append(o)
  # Named load surfaces are continuous, not duplicated material slabs.
 nodes=[8.5,9,13,18.75,25,30.25,36,40,46,53.8,59,59.5]
 for j,(a,b) in enumerate(zip(nodes,nodes[1:])):
  if b-a<1:continue
  for side in [-1,1]:xy_web(g+f'_Warren_{j}_{side}',a+.11,b-.11,75.99,77.42,z+side*.35,.18,j%2==0,col,g,res)
 for j,x in enumerate(nodes):
  if x in [8.5,59.5]+[r[0] for r in rails]:continue
  for s in [-1,1]:
   box(g+f'_Node_{j}_{s}',[x-.11,75.99,z+s*.35-.09],[x+.11,77.42,z+s*.35+.09],'ivory_enamel',col,g,res)
 for x,w in rails:
  for side in [-1,1]:
   a,b=sorted([z+side*.5,z+side*.6]);y0=77.05 if x in[25,40] and ((iz==0 and side==1) or (iz==1 and side==-1)) else 75.65
   box(g+f'_RailEndPlate_X{x}_{side}',[x-w/2,y0,a],[x+w/2,77.76,b],'champagne_metal',col,g,res)
  # Cross-grid stiffener occupies middle plane and joins both flanges. Twin web nodes remain legible.
  box(g+f'_GridDiaphragm_X{x}',[x-.11,75.99,z-.50],[x+.11,77.42,z+.50],'ivory_enamel',col,g,res)
 for x in xs:contact(g+f'_PierSeat_X{x}',f'P{iz+1}_X{x}_BearingPlate',g+'_Bottom_lower_flange','Y',75.65,[[x-.49,z-.49],[x+.49,z+.49]])
# Longitudinal I-chord truss links; explicit fore/aft cantilevers, butt joint at +/-0.6m.
segments=[(-465.8,stations[0]-.6,None,0)] + [(a+.6,b-.6,i,i+1) for i,(a,b) in enumerate(zip(stations,stations[1:]))] + [(stations[-1]+.6,-398.2,4,None)]
for x,w in rails:
 for seg,(a,b,ia,ib) in enumerate(segments):
  g=f'LONG_X{x}_S{seg}';col='A04_LONGITUDINAL_GRID';bottom=77.05 if x in[25,40] and seg==1 else 75.65
  res=f'ROOT_C12_LONG_X{x}_Z'+('-465.8' if seg==0 else '-462' if seg==1 else '-451.4')
  if bottom==77.05:
   # Shallow screen-pocket box girder, ends directly contact the raised receiving end plates.
   layers=[('bottom',bottom,bottom+.12,w),('web',bottom+.12,77.64,.16),('top',77.64,77.76,w)]
   for tag,y0,y1,ww in layers:box(g+'_'+tag,[x-ww/2,y0,a],[x+ww/2,y1,b],'champagne_metal' if tag!='web' else 'ivory_enamel',col,g,res)
   for n,z0 in enumerate([a,(a+b)/2,b]):
    aa=max(a,z0-.06);bb=min(b,z0+.06)
    box(g+f'_Stiffener{n}',[x-w/2,bottom+.12,aa],[x+w/2,77.64,bb],'ivory_enamel',col,g,res)
  else:
   for tag,y0,y1 in [('Bottom',75.65,75.99),('Top',77.42,77.76)]:
    for part,ya,yb,ww in [('lower_flange',y0,y0+.10,w),('web',y0+.10,y1-.10,min(.16,w*.4)),('upper_flange',y1-.10,y1,w)]:
     box(g+'_'+tag+'_'+part,[x-ww/2,ya,a],[x+ww/2,yb,b],'champagne_metal' if 'flange' in part else 'auditorium_navy_fibre',col,g,res)
   n=max(1,math.ceil((b-a)/4.8));step=(b-a)/n
   for j in range(n):
    za=a+j*step;zb=za+step
    for s in[-1,1]:zy_web(g+f'_Web{j}_{s}',za+.07,zb-.07,75.99,77.42,x+s*w*.30,min(.14,w*.24),j%2==0,col,g,res)
   for j in range(n+1):
    zz=a+j*step;aa=max(a,zz-.07);bb=min(b,zz+.07)
    for s in[-1,1]:box(g+f'_Post{j}_{s}',[x+s*w*.30-min(.14,w*.24)/2,75.99,aa],[x+s*w*.30+min(.14,w*.24)/2,77.42,bb],'ivory_enamel',col,g,res)
  for label,idx,zz in [('fore',ia,a),('aft',ib,b)]:
   if idx is not None:contact(g+'_'+label,g,f'TRUSS_{idx+1}','Z',zz,[[x-w/2,bottom],[x+w/2,77.76]])
# Slab is a 180mm structural plate plus 60mm wearing course and flush load shoes.
slab=box('Library_Plate_Structural180',[8,77.76,-466],[54,77.94,-398],'warm_stone','A05_LIBRARY_SLAB_AND_FEET','Library_slab','ROOT_LIBRARY_BASE_PLATE')
R=json.loads((OUT/'inputs/SELECTED_RECEIVING_SECTION_R1.json').read_text());feet=[]
for v in R['volumes']:
 if v['id'].startswith('WP06_PIER_FOOT_') or v['id'].startswith('WP06_EAST_WALL_BEAR_'):
  lo=v['min_xyz'];hi=v['max_xyz'];feet.append((lo[0],hi[0],lo[2],hi[2],v['id']))
xx=sorted(set([8,54]+[v for f in feet for v in f[:2]]));zz=sorted(set([-466,-398]+[v for f in feet for v in f[2:4]]))
for i,(a,b) in enumerate(zip(xx,xx[1:])):
 for j,(c,d) in enumerate(zip(zz,zz[1:])):
  cx=(a+b)/2;cz=(c+d)/2
  if any(x0<cx<x1 and z0<cz<z1 for x0,x1,z0,z1,_ in feet):continue
  box(f'Library_WearingCourse_{i:02}_{j:02}',[a,77.94,c],[b,78,d],'warm_stone','A05_LIBRARY_SLAB_AND_FEET','Library_slab','ROOT_LIBRARY_BASE_PLATE')
for i,(a,b,c,d,target) in enumerate(feet):
 name=f'Library_FlushFootReceiver_{i+1:02}'
 shoe=box(name,[a,77.94,c],[b,78,d],'champagne_metal','A05_LIBRARY_SLAB_AND_FEET','Library_feet','ROOT_LIBRARY_BASE_PLATE');shoe['pending_counterpart']=target
 contact(name+'_slab',slab.name,name,'Y',77.94,[[a,c],[b,d]])
 contact(name+'_WP06',name,target,'Y',78,[[a,c],[b,d]],'external_counterpart_pending_source_owner')
for iz,z in enumerate(stations):contact(f'Library_on_Truss{iz+1}',f'TRUSS_{iz+1}_Top_upper_flange',slab.name,'Y',77.76,[[8.5,z-.5],[54,z+.5]])
# Contained service branches in the west transfer line, with proper trays, saddles and backed terminals.
# Each link has bounded terminals at structural nodes; through-node utilities remain external interface work.
for seg,(a,b,ia,ib) in enumerate(segments):
 if ia is None or ib is None:continue
 col='A06_SERVICE_BRANCHES';g=f'SERVICE_WEST_{seg}';res='ROOT_C12_LONG_X9_Z'+('-462' if seg==1 else '-451.4');a+=.14;b-=.14
 box(g+'_Tray',[8.82,76.42,a],[9.18,76.46,b],'champagne_metal',col,g,res)
 for x in[8.82,9.15]:box(g+f'_TrayRim{x}',[x,76.46,a],[x+.03,76.56,b],'champagne_metal',col,g,res)
 for x in[8.91,9.08]:
  box(g+f'_Cable{x}',[x-.025,76.49,a],[x+.025,76.54,b],'dark_rubber',col,g,res)
 for n,z in enumerate([a,b]):
  box(g+f'_Junction{n}',[8.80,76.36,z-.06],[9.20,76.68,z+.06],'ivory_enamel',col,g,res)
  box(g+f'_AccessFace{n}',[8.83,76.39,z-.071],[9.17,76.65,z-.061],'auditorium_navy_fibre',col,g,res)
 for n in range(math.ceil((b-a)/3)+1):
  z=min(a+n*3,b);box(g+f'_Saddle{n}',[8.74,76.39,z-.035],[9.26,76.42,z+.035],'champagne_metal',col,g,res)
  for side,xx in [('west',8.77),('east',9.19)]:
   box(g+f'_Hanger{n}_{side}',[xx,76.42,z-.025],[xx+.04,77.42,z+.025],'champagne_metal',col,g,res)
DETAILS.append('West transfer inter-bay cable branches are fully materialized and terminate at bounded junction boxes. Through-primary utility connection is pending, not silently routed through solid webs.')
# Exact nonexporting wire volumes; they are never counted as finished geometry.
for v in R['volumes']:
 if not v['id'].startswith('ROOT_'):continue
 o=bpy.data.objects.new('RESERVATION_'+v['id'],None);COL['Z00_NONEXPORT_RESERVATIONS'].objects.link(o);o.empty_display_type='CUBE';lo=v['min_xyz'];hi=v['max_xyz'];o.location=xyz([(a+b)/2 for a,b in zip(lo,hi)]);o.scale=((hi[0]-lo[0])/2,(hi[2]-lo[2])/2,(hi[1]-lo[1])/2);o['status']='reservation_only_nonexporting';o['source_reservation_id']=v['id'];o.hide_render=True
# Static record and geometry envelopes.
record=[]
for o in GEOM:
 o.data.calc_loop_triangles();record.append(dict(name=o.name,semantic_group=o['semantic_group'],reservation_id=o.get('reservation_id'),min_xyz=list(o['world_min_xyz']),max_xyz=list(o['world_max_xyz']),vertices=len(o.data.vertices),triangles=len(o.data.loop_triangles),material=o['astraea_material_role']))
(OUT/'qa/authored_geometry.json').write_text(json.dumps(record,indent=2))
(OUT/'exports/receiver_contacts.json').write_text(json.dumps(dict(frame='world XYZ Y-up metres',status='candidate; source-only',contacts=CONTACTS),indent=2))
(OUT/'exports/floor_contract.json').write_text(json.dumps(dict(world_y=[69.26,69.50],source_cinema_polygon=p,bounded_west_strip=[8,11.4,-466,-398],union_polygon=poly,library_slab_bounds=[[8,77.76,-466],[54,78,-398]],floor_collision_owner='root candidate; runtime adoption pending',collision_strategy='Explicit concave polygon/tile or triangle surface; never whole-assembly convex hull',external_foot_count=len(feet)),indent=2))
# Editable object-per-member source. Preview cameras/context are separate, nonexporting.
scene['candidate_status']='Root source-only lower receiving frame. Old Cinema roof conflicts until owner revision. Upper lattice remains reserved, not authored.'
scene.world=bpy.data.worlds.new('Receiving_QA_World');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.055,.066,.088,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.5
scene.render.engine='CYCLES';scene.cycles.samples=20;scene.cycles.use_denoising=True
scene.view_settings.view_transform='AgX';scene.render.resolution_x=1280;scene.render.resolution_y=720;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
bpy.ops.object.select_all(action='DESELECT')
for o in GEOM:o.select_set(True)
bpy.context.view_layer.objects.active=GEOM[0]
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'source/cinema_library_receiving_r001.blend'),check_existing=False)
bpy.ops.export_scene.gltf(filepath=str(OUT/'exports/cinema_library_receiving_r001.glb'),export_format='GLB',use_selection=True,export_extras=True,export_yup=True,export_apply=True,export_cameras=False,export_lights=False)
(OUT/'qa/build_receipt.json').write_text(json.dumps(dict(asset_id=ASSET,revision=REV,blender=bpy.app.version_string,meshes=len(GEOM),triangles=sum(r['triangles'] for r in record),internal_contacts=len([c for c in CONTACTS if c['status']=='internal_exact_contact']),external_contacts=20,upper_lattice='Not authored; optional scope retained as named reservation',details=DETAILS,frame='BLENDER=(world X,-world Z,world Y); GLB world XYZ Y-up',source_only=True),indent=2))
print('RECEIVING_BUILD_COMPLETE',len(GEOM))
