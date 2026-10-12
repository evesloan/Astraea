"""Purpose-led northern Tidal bathing chamber; immutable source successor.
Uses retained basin, vault, floors, routes and transfer interfaces. All originals
stay exact. New room geometry is local, not an outer-hull or shared-root edit.
"""
import bpy,bmesh,json,hashlib,math,random
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent;R=P.parents[3];OLD=P.parent/'thermal_rest';ENTRY=P.parent/'thermal_targets'
code=(ENTRY/'author_entries.py').read_text();exec(code[code.index('def digest'):code.index('provenance=')])
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
old=json.loads((OLD/'CONTRACT_02.json').read_text());source=R/old['native'];assert sha(source)==old['native_sha256'];dest=P/'TidalNorthRoom_r006.blend';assert not dest.exists()
bpy.ops.wm.open_mainfile(filepath=str(source));S=bpy.context.scene;originals={o.name:digest(o) for o in S.objects if o.type=='MESH'};packed={im.name:hashlib.sha256(im.packed_file.data).hexdigest() for im in bpy.data.images if im.packed_file};NEW=[]
# Small deterministic material textures, retained in the editable native. These
# are production material families, not a generated room picture or concept.
def material(name,c,rough=.75,metal=0,kind='noise'):
 m=bpy.data.materials.new('G6_TIDAL_'+name);m.use_nodes=True;m.diffuse_color=(*c,1);bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=rough;bs.inputs['Metallic'].default_value=metal;bs.inputs['Base Color'].default_value=(*c,1)
 if kind!='solid':
  size=64;im=bpy.data.images.new('G6_TIDAL_'+name+'_texture',width=size,height=size,alpha=True);rng=random.Random(name);pixels=[]
  for y in range(size):
   for x in range(size):
    v=1+rng.uniform(-.026,.026)
    if kind=='wood':v+=.08*math.sin(x*.42+math.sin(y*.10)*.45)+.025*math.sin(x*1.8)
    if kind=='fabric':v+=.035*((x+y)%2*2-1)
    if kind=='tile' and (x%16==0 or y%16==0):v=.80
    pixels.extend([max(0,min(1,a*v)) for a in c]+[1])
  im.pixels[:]=pixels;im.pack();t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=im;t.interpolation='Closest';m.node_tree.links.new(t.outputs['Color'],bs.inputs['Base Color'])
 return m
M={'floor':material('limestone_pavers',(.71,.69,.60),.86,kind='tile'),'recess':material('glazed_sage',(.40,.54,.48),.62,kind='tile'),'rib':material('vault_stone',(.61,.58,.47),.72,kind='noise'),'steel':material('satin_metal',(.59,.61,.58),.38,.55,kind='solid'),'glass':material('clear_guard',(.70,.82,.79),.3,kind='solid'),'ivory':material('ivory',(.88,.83,.70)), 'stone':material('limestone',(.79,.74,.62),.68,kind='noise'),'wood':material('teak',(.46,.28,.15),.6,kind='wood'),'fabric':material('mint_fabric',(.23,.49,.40),.93,kind='fabric'),'rust':material('rust_fabric',(.48,.16,.09),.93,kind='fabric'),'brass':material('muted_brass',(.35,.25,.12),.43,.55,kind='solid'),'tile':material('pool_mosaic',(.30,.62,.58),.34,kind='tile'),'opal':material('opal_lens',(.92,.84,.58),.5,kind='solid'),'water':material('water_preview',(.12,.47,.50),.18,kind='solid'),'leaf':material('leaf',(.10,.25,.105),.88,kind='solid'),'soil':material('soil',(.10,.058,.028),.95,kind='solid')}
def finish(o,n,mat='ivory',role='architecture'):
 o.name=('G6_TIDAL__'+n).replace('.', '_');o['group6_role']=role;o['programme_key']='D08_directory_02';o.data.materials.clear();o.data.materials.append(M[mat]);o.data.update();uv=o.data.uv_layers.new(name='UV0')
 for f in o.data.polygons:
  axes=[i for i in range(3) if i!=max(range(3),key=lambda i:abs(f.normal[i]))]
  for li in f.loop_indices:
   v=o.data.vertices[o.data.loops[li].vertex_index].co;scale=.7
   if mat=='floor':
    bpy.context.view_layer.update();v=o.matrix_world@v;scale=.25
   uv.data[li].uv=(v[axes[0]]*scale,v[axes[1]]*scale)
 NEW.append(o);return o
FACES=[(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)]
def mesh(n,vs,fs,mat='ivory',role='architecture'):
 m=bpy.data.meshes.new(n);m.from_pydata([xyz(v) for v in vs],[],fs);m.update();bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(m);bm.free();o=bpy.data.objects.new(n,m);S.collection.objects.link(o);return finish(o,n,mat,role)
def box(n,p,d,mat='ivory',bevel=.03,role='architecture'):
 bpy.ops.mesh.primitive_cube_add(size=1,location=xyz(p));o=bpy.context.object;o.dimensions=(d[0],d[2],d[1]);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if bevel:
  q=o.modifiers.new('Crafted rounded edges','BEVEL');q.width=min(bevel,min(d)*.25);q.segments=3;bpy.ops.object.modifier_apply(modifier=q.name)
 return finish(o,n,mat,role)
def rod(n,a,b,r=.035,mat='brass',role='architecture'):
 a,b=xyz(a),xyz(b);d=b-a;bpy.ops.mesh.primitive_cylinder_add(vertices=16,radius=r,depth=d.length,location=(a+b)/2);o=bpy.context.object;o.rotation_euler=d.to_track_quat('Z','Y').to_euler();bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);return finish(o,n,mat,role)
def cyl(n,p,r,h,mat='stone',role='architecture'):
 bpy.ops.mesh.primitive_cylinder_add(vertices=24,radius=r,depth=h,location=xyz(p));o=bpy.context.object;q=o.modifiers.new('Soft rim','BEVEL');q.width=min(.022,h*.15);q.segments=3;bpy.ops.object.modifier_apply(modifier=q.name);return finish(o,n,mat,role)
# Raised gallery is actual source architecture supported on the existing floor.
box('wet_gallery',(42.05,44.45,-418.0),(1.70,.90,20.40),'floor',.025)
box('wet_landing_join',(42.8,44.45,-430.15),(1.6,.90,3.9),'floor',.025)
box('north_wet_turn',(35.85,44.45,-406.1),(14.1,.90,3.4),'floor',.025)
# Source ramp returns to the same original dry floor without crowding X45.
vs=[(x,y,z) for y in [44,None] for z in [-417,-407.2] for x in [42.9,44.4]]
for k in range(4,8):vs[k]=(vs[k][0],44.9 if k<6 else 44.025,vs[k][2])
mesh('dry_return_ramp',vs,FACES,'floor')
box('dry_return_upper_landing',(43.65,44.45,-417.5),(1.5,.9,1.0),'floor',.02)
# Ramp handrails meet the actual inclined source, leaving the X45 dry lane clear.
for side,x in [('outer',44.37),('inner',42.96)]:
 for k,z in enumerate([-416.9,-413.6,-410.3,-407.3]):
  top=44.9-.875*((z+417)/9.8);rod('ramp_post_'+side+'_'+str(k),(x,top-.012,z),(x,top+1,z),.027,'steel')
 rod('ramp_guard_'+side,(x,45.89107,-416.9),(x,45.03393,-407.3),.027,'steel')
# A visible glazed guard protects the raised gallery; its source mesh still owns
# physical contact. Slim caps/spigots leave the recovery seating readable.
for k,(a,b) in enumerate([(-428.2,-418.05),(-415.95,-407.8)]):
 box('gallery_guard_glass_'+str(k),(42.87,45.425,(a+b)/2),(.016,.97,b-a),'glass',0,'architecture_glass')
 for j,z in enumerate([a+.10,(a+b)/2,b-.10]):box('gallery_guard_spigot_'+str(k)+'_'+str(j),(42.855,44.975,z),(.08,.15,.075),'steel',.01)
 rod('gallery_guard_cap_'+str(k),(42.87,45.925,a),(42.87,45.925,b),.022,'steel')
# Rounded stone cap and blue-green liner reveal the basin depth and boundary.
for n,p,d in [('west',(29,45.09,-418),(.38,.14,20.3)),('east',(41,45.09,-418),(.38,.14,20.3)),('north',(35,45.09,-408),(11.8,.14,.38))]:box('coping_'+n,p,d,'stone',.055)
mesh('basin_liner',[(29.21,44.306,-427.79),(40.79,44.306,-427.79),(40.79,44.306,-408.21),(29.21,44.306,-408.21)],[(0,1,2,3)],'tile','visual_liner')
mesh('water_face',[(29.2,44.9,-427.8),(40.8,44.9,-427.8),(40.8,44.9,-408.2),(29.2,44.9,-408.2)],[(0,1,2,3)],'water','visual_water')
# Vault infill meets the retained sloping members; a stepped cove gives the
# recovery edge a comfortable section instead of another freestanding shelter.
def base_y(z):return 49.8+(28-abs(z+432))/28+.255
def east_limit(z):return min(50.7,-358-z)
for k in range(8):
 za=-430+k*3.25;zb=min(-403.95,za+3.25)
 if zb<=za:continue
 profile=[]
 for a in range(13):
  x=28+14*a/12;profile.append((x,.35*math.sin(math.pi*a/12)))
 vs=[(x,base_y(z)+rise+h,z) for h in [0,.13] for z in [za,zb] for x,rise in profile];fs=[]
 for a in range(12):
  fs.extend([(a,a+1,14+a,13+a),(26+a,39+a,40+a,27+a),(a,26+a,27+a,a+1),(13+a,14+a,40+a,39+a)])
 fs.extend([(0,13,39,26),(12,38,51,25)]);mesh('vault_infill_'+str(k),vs,fs,'ivory')
 # Roof-edge east panel closes into the existing facade, clipped to its chamfer.
 x0,x1=east_limit(za),east_limit(zb);v=[(x,y+h,z) for h in [0,.13] for x,y,z in [(42,base_y(za),za),(x0,50.65,za),(42,base_y(zb),zb),(x1,50.65,zb)]];mesh('east_roof_infill_'+str(k),v,FACES,'ivory')
# Shaped vault ribs and receiving shoes make the ceiling/beam joints legible.
for k,z in enumerate([-428,-421,-414,-407]):
 profile=[(28+14*a/12,.35*math.sin(math.pi*a/12)) for a in range(13)]
 vs=[(x,base_y(z)+rise+h,z+dz) for h in [-.17,.015] for dz in [-.10,.10] for x,rise in profile];fs=[]
 for a in range(12):fs.extend([(a,a+1,14+a,13+a),(26+a,39+a,40+a,27+a),(a,26+a,27+a,a+1),(13+a,14+a,40+a,39+a)])
 fs.extend([(0,13,39,26),(12,38,51,25)]);mesh('vault_rib_'+str(k),vs,fs,'rib')
 for j,x in enumerate([28,42]):box('vault_receiving_shoe_'+str(k)+'_'+str(j),(x,base_y(z)-.14,z),(.52,.36,.46),'rib',.045)
# Cove is carried from the retained sloping vault frame, above circulation.
# The former added floor piers are removed from this new export only.
for k,z in enumerate([-433.5,-425.5,-417.8,-409.5]):
 rod('cove_vault_hanger_'+str(k),(42,48.4,z),(42,base_y(z)-.48,z),.070,'steel')
 box('cove_hanger_shoe_'+str(k),(41.9,48.42,z),(.85,.14,.45),'rib',.025)
for k in range(10):
 za=-437+k*3.2;zb=za+3.2;x0,x1=east_limit(za)-.08,east_limit(zb)-.08
 v=[(x,y+h,z) for h in [0,.15] for x,y,z in [(41.5,48.35,za),(x0,48.35,za),(41.5,48.35,zb),(x1,48.35,zb)]];mesh('recovery_cove_'+str(k),v,FACES,'ivory');box('cove_front_fascia_'+str(k),(41.5,48.29,(za+zb)/2),(.18,.30,3.24),'wood',.035)
# Real internal threshold, not a backdrop covering the shared exterior. The
# arched opening remains clear below47.4..47.95; source transfer hardware is lower.
profile=[(28+14*a/16,.55*math.sin(math.pi*a/16)) for a in range(17)]
vs=[(x,(47.4+rise if h==0 else base_y(-429.15)+.35*math.sin(math.pi*a/16)+.05),z) for h in [0,1] for z in [-429.30,-429.0] for a,(x,rise) in enumerate(profile)];fs=[]
for a in range(16):fs.extend([(a,a+1,18+a,17+a),(34+a,51+a,52+a,35+a),(a,34+a,35+a,a+1),(17+a,18+a,52+a,51+a)])
fs.extend([(0,17,51,34),(16,50,67,33)]);mesh('threshold_arch_spandrel',vs,fs,'ivory')
box('threshold_cove_return',(46.25,49.4,-429.15),(8.50,2.6,.30),'ivory',.05)
box('threshold_west_jamb',(27.85,45.8,-429.15),(.40,3.60,.45),'rib',.035)
box('threshold_east_jamb',(50.45,46.175,-429.15),(.40,4.35,.45),'rib',.035)
# Profiled interior lining; opaque original enclosure remains behind it.
for k in range(10):
 za=-436.5+k*3.15;zb=za+3.05
 def front(z):return min(50.50,-358.45-z)
 for n,lo,hi,mat in [('dado',44,45.25,'wood'),('panel',45.35,48.0,'recess')]:
  v=[(front(z)+dx,y,z) for dx in [0,.14] for z in [za,zb] for y in [lo,hi]]
  mesh('wall_'+n+'_'+str(k),v,[(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)],mat)
 for j,z in enumerate([za,zb]):box('wall_panel_reveal_'+str(k)+'_'+str(j),(front(z)-.04,46.62,z),(.12,2.95,.10),'rib',.02)
 rod('wall_crown_'+str(k),(front(za),48.15,za),(front(zb),48.15,zb),.085,'rib')
# Room-facing internal wall returns meet the retained north vault/piers and
# original floor. Outer enclosure/receiving shell and west promenade remain exact.
for k,(za,zb) in enumerate([(-428.8,-422.6),(-422.6,-416.4),(-416.4,-410.2),(-410.2,-404.0)]):
 v=[(x,y,z) for x in [27.75,28.0] for z in [za,zb] for y in [44,base_y(z)+.035]]
 mesh('west_room_return_'+str(k),v,[(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)],'ivory')
 z=(za+zb)/2;box('west_timber_dado_'+str(k),(28.065,44.6,z),(.13,1.2,zb-za),'wood',.02)
 box('west_recess_inlay_'+str(k),(28.076,46.66,z),(.04,2.85,4.8),'recess',.035)
 for dz in [-2.46,2.46]:box('west_recess_reveal_'+str(k)+'_'+str(dz),(28.12,46.66,z+dz),(.12,3.0,.11),'brass',.02)
 rod('west_crown_'+str(k),(28.12,base_y(za)-.14,za),(28.12,base_y(zb)-.14,zb),.085,'stone')
box('north_room_return',(35,47.38,-404.18),(14.2,6.76,.26),'ivory',.04)
box('north_timber_dado',(35,44.65,-404.39),(14.0,1.3,.16),'wood',.03)
for k,x in enumerate([30.2,35,39.8]):
 box('north_inlay_'+str(k),(x,46.7,-404.405),(3.55,2.8,.05),'recess',.035)
 for dx in [-1.83,1.83]:box('north_reveal_'+str(k)+'_'+str(dx),(x+dx,46.7,-404.44),(.11,3.0,.12),'brass',.02)
# Rounded architectural reveals connect the bathing walls to the vault language.
def arch_band(n,center,normal_axis,radius,spring_y,mat='ivory'):
 vs=[]
 for depth in [-.06,.06]:
  for r in [radius,radius-.16]:
   for j in range(17):
    a=math.pi*j/16;u=r*math.cos(a);y=spring_y+r*math.sin(a)
    vs.append((center[0]+depth,y,center[2]+u) if normal_axis=='x' else (center[0]+u,y,center[2]+depth))
 fs=[]
 for j in range(16):
  fs.extend([(j,j+1,18+j,17+j),(34+j,51+j,52+j,35+j),(j,34+j,35+j,j+1),(17+j,18+j,52+j,51+j)])
 fs.extend([(0,17,51,34),(16,50,67,33)]);mesh(n,vs,fs,mat)
 for side in [-1,1]:
  p=(center[0],(45.3+spring_y)/2,center[2]+side*(radius-.08)) if normal_axis=='x' else (center[0]+side*(radius-.08),(45.3+spring_y)/2,center[2])
  box(n+'_leg_'+str(side),p,(.12,spring_y-45.3,.16) if normal_axis=='x' else (.16,spring_y-45.3,.12),mat,.025)
for k,z in enumerate([-425.7,-419.5,-413.3,-407.1]):arch_band('west_arch_reveal_'+str(k),(28.18,0,z),'x',2.20,47.15,'ivory')
for k,x in enumerate([30.2,35,39.8]):arch_band('north_arch_reveal_'+str(k),(x,0,-404.49),'z',1.78,47.15,'ivory')
# Local floor finish on the existing dry floor; zero contact/floor-owner addition.
mesh('dry_floor_finish',[(44.6,44.006,-437),(50.55,44.006,-437),(50.55,44.006,-408.85),(45.65,44.006,-403.95),(44.6,44.006,-403.95)],[(0,1,2,3,4)],'floor','visual_liner')
# Northern bench keeps its established footprint/identity but reads as seating.
box('banquette_recessed_base',(47.05,44.18,-412),(1.02,.36,4.90),'wood',.08)
box('banquette_load_pan',(46.96,44.385,-412),(1.26,.09,4.98),'ivory',.08)
for k in range(4):
 z=-413.89+k*1.26;box('seat_cushion_'+str(k),(46.98,44.49,z),(1.17,.19,1.20),'fabric',.09)
 o=box('back_cushion_'+str(k),(47.53,44.94,z),(.22,.79,1.20),'fabric',.08);o.rotation_euler.y=-.13
for k,z in enumerate([-414.45,-409.55]):box('banquette_return_'+str(k),(47.05,44.61,z),(1.27,.36,.16),'ivory',.07)
# A connected rounded niche, not a gazebo, gives seating a framed backdrop.
for k,z in enumerate([-414.75,-409.25]):
 box('seat_niche_side_'+str(k),(48.75,46.18,z),(3.10,4.36,.25),'ivory',.075)
box('seat_niche_crown',(48.70,48.32,-412),(3.25,.28,5.75),'ivory',.10)
box('seat_niche_back',(50.34,46.33,-412),(.16,3.4,5.2),'wood',.06)
for k,z in enumerate([-413.55,-410.45]):
 cyl('table_base_'+str(k),(46.0,44.035,z),.20,.07,'brass');rod('table_stem_'+str(k),(46,44.07,z),(46,44.62,z),.045,'brass');cyl('table_top_'+str(k),(46,44.655,z),.32,.07,'stone')
 cyl('cup_saucer_'+str(k),(46.02,44.697,z),.10,.014,'ivory','visual_furnishing');cyl('ceramic_cup_'+str(k),(46.02,44.77,z),.068,.13,'ivory','visual_furnishing')
 bpy.ops.mesh.primitive_torus_add(major_segments=12,minor_segments=6,major_radius=.051,minor_radius=.012,location=xyz((46.09,44.77,z)));o=bpy.context.object;o.rotation_euler.x=math.pi/2;finish(o,'cup_handle_'+str(k),'ivory','visual_furnishing')
# Replace the prior central pavilion with the same wall-connected recovery
# construction in its established bench footprint. No extra vessel props or seats.
for o in list(NEW):
 if o.name.startswith(('G6_TIDAL__banquette_','G6_TIDAL__seat_cushion_','G6_TIDAL__back_cushion_','G6_TIDAL__seat_niche_')):
  n=o.copy();n.data=o.data.copy();n.name=o.name.replace('__','__central_',1);S.collection.objects.link(n);n.location.y+=20;NEW.append(n)
bpy.context.view_layer.update()
# Two integrated planted pauses, outside the existing X45 promenade.
for k,(x,z) in enumerate([(48.75,-416.1),(48.75,-407.7)]):
 cyl('planter_foot_'+str(k),(x,44.06,z),.43,.12,'brass');cyl('planter_bowl_'+str(k),(x,44.38,z),.46,.56,'stone');cyl('planter_soil_'+str(k),(x,44.665,z),.39,.018,'soil','visual_furnishing')
 for j in range(5):
  a=j*math.tau/5;end=(x+.31*math.cos(a),45.35+.13*(j%2),z+.31*math.sin(a));rod('plant_stem_'+str(k)+'_'+str(j),(x,44.67,z),end,.012,'leaf','visual_furnishing')
  for t in [.55,.82,1]:
   cx=x+(end[0]-x)*t;cy=44.67+(end[1]-44.67)*t;cz=z+(end[2]-z)*t;mesh('plant_leaf_'+str(k)+'_'+str(j)+'_'+str(t),[(cx,cy,cz),(cx+.26*math.cos(a+.8),cy+.08,cz+.26*math.sin(a+.8)),(cx+.15*math.cos(a),cy+.19,cz+.15*math.sin(a)),(cx-.05*math.sin(a),cy+.03,cz+.05*math.cos(a))],[(0,1,2,3)],'leaf','visual_furnishing')
# Actual light housings. Geometry is not an emissive-only lighting claim.
fittings=[]
for k,z in enumerate([-425,-417,-409]):
 rod('pendant_drop_'+str(k),(35,base_y(z)+.35,z),(35,48.75,z),.028,'brass');cyl('pendant_crown_'+str(k),(35,48.78,z),.32,.10,'brass');cyl('pendant_globe_'+str(k),(35,48.57,z),.27,.30,'opal','fixture_lens');cyl('pendant_ring_'+str(k),(35,48.41,z),.30,.045,'brass')
 fittings.append({'id':'tidal_north_pendant_'+str(k)+'_001','source_xyz':[35,48.36,z],'target_xyz':[35,44.94,z],'energy':8.5,'range_m':10,'cone_degrees':70,'color_rgb':[1,.95,.84],'receiver':'protected northern bath water'})
# Top-mounted reflector lenses light the vaulted room section as real sources.
# Two uplights plus the six task sources stay inside the unchanged budget of eight.
for k,z in enumerate([-425,-409]):
 cyl('pendant_uplight_lens_'+str(k),(35,48.844,z),.22,.028,'opal','fixture_lens')
 fittings.append({'id':'tidal_north_vault_uplight_'+str(k)+'_001','source_xyz':[35,48.88,z],'target_xyz':[35,base_y(z)+.32,z],'energy':3.5,'range_m':6,'cone_degrees':87,'color_rgb':[1,.94,.80],'receiver':'vault underside'})
for k,z in enumerate([-432,-412]):
 rod('cove_light_drop_'+str(k),(49.7,48.36,z),(49.7,48.27,z),.075,'brass');box('cove_light_mount_'+str(k),(49.7,48.19,z),(.55,.20,.48),'brass',.06);box('cove_light_lens_'+str(k),(49.7,48.045,z),(.40,.06,.34),'opal',.045,'fixture_lens')
 fittings.append({'id':'tidal_north_cove_'+str(k)+'_001','source_xyz':[49.7,47.995,z],'target_xyz':[46.7,44.65,z],'energy':5.5,'range_m':9,'cone_degrees':68,'color_rgb':[1,.88,.68],'receiver':'recovery surface and passage'})
cyl('arrival_pier_foot',(43.8,44.06,-428.4),.16,.12,'stone');rod('arrival_pier',(43.8,44.12,-428.4),(43.8,48.4,-428.4),.11,'ivory');box('arrival_pier_ceiling_join',(43.8,48.425,-428.0),(.34,.15,.95),'ivory',.035)
box('entry_sconce_body',(43.8,47.10,-428.4),(.34,.60,.20),'brass',.07);box('entry_sconce_lens',(43.8,47.10,-428.25),(.25,.43,.065),'opal',.05,'fixture_lens')
fittings.append({'id':'tidal_north_entry_sconce_001','source_xyz':[43.8,46.96,-428.19],'target_xyz':[45,44.06,-426.7],'energy':2.4,'range_m':7,'cone_degrees':68,'color_rgb':[1,.93,.80],'receiver':'original east dry arrival route on clear side of sconce pier'})
# Exact, reviewable substitutions. No source native or shared scene is changed.
original_exclusions=['D08_directory_02__static_water_surface1']+[f'D08_directory_02__dry_recovery{j}_{s}' for j in [1,2] for s in ['plinth','pad','back','arm-1','arm1']]+[f'D08_directory_02__bath_light3_{s}' for s in ['post','arm','shade','lens']]
prior_recovery_exclusions=[n for n in originals if n.startswith(('G6_REST_02__bay_1_','G6_REST_02__bay_2_'))]
for n in original_exclusions+prior_recovery_exclusions:assert n in originals;bpy.data.objects[n].hide_render=True
assert all(digest(bpy.data.objects[n])==h for n,h in originals.items())
for im in bpy.data.images:
 if im.packed_file:im.use_fake_user=True
bpy.ops.wm.save_as_mainfile(filepath=str(dest));bpy.ops.object.select_all(action='DESELECT')
for o in NEW:o.select_set(True)
export=P/'Group6TidalNorthRoom_r006.glb';bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',use_selection=True,export_extras=True,export_cameras=False,export_lights=False,export_materials='EXPORT')
def game_bounds(o):
 vs=[o.matrix_world@v.co for v in o.data.vertices];a=[[min(v[k] for v in vs),max(v[k] for v in vs)] for k in range(3)];return [a[0],a[2],[-a[1][1],-a[1][0]]]
spec={'programme_key':'D08_directory_02','status':'one coherent northern room candidate; shared adoption pending','source_context':str(source.relative_to(R)),'source_context_sha256':sha(source),'original_context_meshes':originals,'original_packed_images':packed,'native':str(dest.relative_to(R)),'native_sha256':sha(dest),'export':str(export.relative_to(R)),'export_sha256':sha(export),'runtime_addition':'Game/assets/models/'+export.name,'current_room_runtime':old['current_room_runtime'],'current_room_runtime_sha256':old['current_room_runtime_sha256'],'required_recovery_export':old['runtime_addition'],'required_recovery_export_sha256':old['export_sha256'],'new_meshes':{o.name:digest(o) for o in NEW},'new_mesh_roles':{o.name:o['group6_role'] for o in NEW},'original_runtime_exclusions':original_exclusions,'prior_recovery_runtime_exclusions':prior_recovery_exclusions,'original_source_exclusion_bounds_xyz':{n:game_bounds(bpy.data.objects[n]) for n in original_exclusions},'fittings':fittings,'new_room_or_capacity_or_floor_owner':0,'water_boundary_xz':[[29.2,40.8],[-427.8,-408.2]],'water_nominal_y':44.9,'water_visual_wave_amplitude_m':.006,'original_bed_top_y':44.3,'original_east_dry_route_x':45,'wet_gallery_center_x':42.05,'wet_gallery_top_y':44.9,'original_shell_and_vault_changed':False,'refinement_of':'TidalNorthRoom_r005.blend','prior_refinement_native_sha256':'84cda549f72004e58fee7eefca4477ad2c1f3cffcbabcb46c96792bf69fab083','internal_threshold_clear_lower_y':[47.4,47.95],'central_recovery_successor_footprint_unchanged':True,'recovery_cove_extent_z':[-437,-405],'cove_carried_from_original_vault_above_circulation':True,'swimming_fluid_occupied_hoist_accepted':False,'geometry_materials_water_and_lighting_part_of_construction':True}
(P/'ROOM_CONTRACT.json').write_text(json.dumps(spec,indent=2)+'\n');print('TIDAL ROOM SOURCE',len(originals),len(NEW),len(fittings))
