"""Bounded, non-adopted Royalty790 native successor. Requires inspection receipt.
No existing source, shared Godot script, registry, bootstrap or export is overwritten.
"""
from pathlib import Path
import bpy,bmesh,json,hashlib,math
from mathutils import Vector
R=Path(__file__).resolve().parents[1];ROOT=R.parents[1]
assert (R/'evidence/NATIVE_INSPECTION.json').exists(),'Read native source before authoring'
PINS=json.loads((R/'evidence/INPUT_PINS.json').read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for p,h in PINS.items():assert sha(ROOT/p)==h,p
src=ROOT/'BlenderCatalogue/assets/d17_connected_royalty/source/AST-RES-006.blend'
bpy.ops.wm.open_mainfile(filepath=str(src));bpy.context.preferences.filepaths.save_version=0

def fingerprint(o):
 d={'name':o.name,'type':o.type,'matrix':[list(row) for row in o.matrix_world],'properties':{k:str(o[k]) for k in o.keys()},'hide_render':o.hide_render}
 if o.type=='MESH':d.update(vertices=[list(v.co) for v in o.data.vertices],faces=[list(f.vertices) for f in o.data.polygons],materials=[m.name for m in o.data.materials],uv=[[list(u.uv) for u in l.data] for l in o.data.uv_layers])
 return hashlib.sha256(json.dumps(d,sort_keys=True).encode()).hexdigest()
original={o.name:fingerprint(o) for o in bpy.context.scene.objects}
M={n:bpy.data.materials[n] for n in ['ivory_enamel','warm_walnut','warm_stone','champagne_metal','HouseSmokedGlass','GardenOpalLens']}
new=[];collision=[]
def xyz(v):return(v[0],-v[2],v[1])
def mesh(name,world,faces,mat='ivory_enamel',role='architecture'):
 me=bpy.data.meshes.new(name);me.from_pydata([xyz(v) for v in world],[],faces);me.update()
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=0.000001);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=0.000001);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
 ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);me.materials.append(M[mat])
 uv=me.uv_layers.new(name='MetreScaled')
 for f in me.polygons:
  n=f.normal.normalized();u=(Vector((1,0,0))-n*n.x).normalized() if abs(n.z)>.7 else Vector((-n.y,n.x,0)).normalized();v=n.cross(u).normalized();scale=M[mat].get('meters_per_tile_uv',[1,1])
  for i in f.loop_indices:
   p=me.vertices[me.loops[i].vertex_index].co;uv.data[i].uv=(p.dot(u)/scale[0],p.dot(v)/scale[1])
 ob['source_owner']='royalty_790_completion_20261020';ob['same_unit_source_index']=790;ob['role']=role;new.append(ob);return ob
F=[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
def box(n,x0,x1,y0,y1,z0,z1,m='ivory_enamel',role='architecture'):
 return mesh(n,[[x,y,z]for y in[y0,y1]for x,z in[(x0,z0),(x1,z0),(x1,z1),(x0,z1)]],F,m,role)
def prism(n,poly,lo,hi,m='ivory_enamel',role='architecture'):
 l=len(poly);return mesh(n,[[x,y,z]for y in[lo,hi]for x,z in poly],[tuple(reversed(range(l))),tuple(range(l,2*l))]+[(i,(i+1)%l,(i+1)%l+l,i+l)for i in range(l)],m,role)
def wall(n,a,b,lo,hi,w,m='ivory_enamel',role='architecture'):
 a,b=Vector(a),Vector(b);t=(b-a).normalized();s=Vector((-t.y,t.x))*w/2
 return prism(n,[list(a+s),list(b+s),list(b-s),list(a-s)],lo,hi,m,role)
def rail(n,a,b,r=.045,m='warm_walnut'):
 a,b=Vector(a),Vector(b);axis=(b-a).normalized();u=axis.cross(Vector((0,1,0)))
 if u.length<.1:u=Vector((1,0,0))
 u.normalize();v=axis.cross(u);verts=[list(p+r*(math.cos(i*math.pi/4)*u+math.sin(i*math.pi/4)*v))for p in[a,b]for i in range(8)]
 return mesh(n,verts,[tuple(reversed(range(8))),tuple(range(8,16))]+[(i,(i+1)%8,8+(i+1)%8,8+i)for i in range(8)],m,'guard')
def cut(obj,rect,label):
 x0,x1,z0,z1=rect;c=box('TEMP_'+label,x0,x1,101,113,z0,z1);bpy.context.view_layer.objects.active=obj
 mod=obj.modifiers.new(label,'BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=c;bpy.ops.object.modifier_apply(modifier=mod.name)
 new.remove(c);bpy.data.objects.remove(c,do_unlink=True)
# Exact passage/headroom holes; reservations are not holes.
holes={'stair_first_headroom':[94.65,96.75,45.0,48.35],'stair_return':[96.75,98.85,42.0,48.35],'lift_sweep':[99.55,103.95,45.48,49.4]}
roof=bpy.data.objects['CR_RoyaltyLowerRoof']
for label,h in holes.items():cut(roof,h,label)
# Relocate complete existing fixture and binding, not only its lamp mesh.
relocated=[]
for n in ['CR_LampHousing_CourtView','CR_LampLens_CourtView','CR_LampStem_CourtView','DATUM_light_CourtView']:
 ob=bpy.data.objects[n];ob.location+=Vector(xyz((2.0,0,-3.5)));relocated.append(n)
# The inset upper gallery is folded around the same-unit circulation core.
poly=[[94.25,35.8],[103.8,35.8],[107,36.6],[111.5,39],[112,42],[110.5,45.5],[108,47.4],[108,50.6],[94.25,50.6]]
floor=prism('RG_UpperGalleryFloor',poly,106.26,106.5,'warm_stone','floor')
for label,h in holes.items():cut(floor,h,'upper_'+label)
# Expressed ring and beams root directly onto retained roof ring/root locations.
for i,(a,b) in enumerate(zip(poly,poly[1:]+poly[:1])):
 wall('RG_UpperFloorFascia_%02d'%i,a,b,106.26,106.48,.12,'ivory_enamel','structure')
 # Continuous parapet plus glass and warm handrail, in the retained family.
 wall('RG_UpperGuardBase_%02d'%i,a,b,106.5,106.76,.12,'warm_walnut','guard')
 wall('RG_UpperGuardGlass_%02d'%i,a,b,106.76,107.56,.028,'HouseSmokedGlass','guard')
 wall('RG_UpperGuardCap_%02d'%i,a,b,107.56,107.64,.14,'champagne_metal','guard')
# Local load-bearing ribs stay above the protected original ceiling, no D16 intrusion.
for z in [36,40,44,50.4]:
 # The stair/lift apertures must not receive a hidden beam across passage.
 ends=[(94.25,108)] if z in[36,40,50.4] else [(98.85,108)]
 for a,b in ends:box('RG_FloorRib_'+str(z),a,b,106.26,106.46,z-.09,z+.09,'warm_walnut','structure')
# Support rooted to unchanged roof, upper columns at floor ring corners only.
for label,x,z in [('WestFore',94.45,36),('EastFore',103.6,36),('View',111.55,41.8),('EastAft',107.75,50.35),('WestAft',94.45,50.35)]:
 box('RG_UpperPier_'+label,x-.10,x+.10,106.26,110.5,z-.12,z+.12,'ivory_enamel','structure')
# Set-back upper canopy, shaped with the gallery; no commons or central-view roof.
prism('RG_UpperRoof',poly,110.5,110.72,'ivory_enamel','ceiling')
for i,(a,b) in enumerate(zip(poly,poly[1:]+poly[:1])):wall('RG_UpperCornice_%02d'%i,a,b,110.25,110.65,.28,'warm_walnut','structure')
# Privacy remains on the inward edge; view-side above parapet stays open/glazed.
wall('RG_InwardPrivacyWall',[94.4,36],[94.4,50.35],107.64,110.5,.12,'ivory_enamel','privacy')
wall('RG_AftPrivacyReturn',[94.4,50.35],[107.75,50.35],107.64,110.5,.12,'ivory_enamel','privacy')
# Fitted stair re-authors the retained CIR-001 family at explicit dimensions, not scale.
rise=2.25;steps=14;going=.30
for flight,(x0,x1) in enumerate([(94.8,96.6),(96.9,98.7)]):
 def p(t,h):return(42+t,102+h) if flight==0 else(46.2-t,104.25+h)
 profile=[p(0,-.18),p(4.2,rise-.18),p(4.2,rise)]
 for i in reversed(range(steps)):profile.extend([p(i*going,(i+1)*rise/steps),p(i*going,i*rise/steps)])
 # First step does not penetrate the immutable lower slab.
 if flight==0:profile=[(z,max(102,y))for z,y in profile]
 vv=[[x,y,z]for x in[x0,x1]for z,y in profile];l=len(profile)
 mesh('RG_StairFlight_'+str(flight),vv,[tuple(reversed(range(l))),tuple(range(l,2*l))]+[(i,(i+1)%l,(i+1)%l+l,i+l)for i in range(l)],'warm_stone','stair_visual')
 for i in range(steps):
  z,y=p(i*going,(i+1)*rise/steps);dz=.04 if flight==0 else-.04
  box('RG_StairNosing_%d_%02d'%(flight,i),x0+.09,x1-.09,y-.018,y+.002,min(z,z+dz),max(z,z+dz),'champagne_metal','stair_visual')
 for side,x in enumerate([x0+.06,x1-.06]):
  for j in range(5):
   z,y=p(j*1.05,j*rise/4);rail('RG_StairPost_%d_%d_%d'%(flight,side,j),[x,y+.03,z],[x,y+1.06,z],.025,'champagne_metal')
  za,ya=p(0,1.06);zb,yb=p(4.2,rise+1.06);rail('RG_StairRail_%d_%d'%(flight,side),[x,ya,za],[x,yb,zb])
  # Actual sloping solid guard, no open riser-side drop.
  za,ya=p(0,.15);zb,yb=p(4.2,rise+.15)
  mesh('RG_StairGlass_%d_%d'%(flight,side),[[xx,y,z]for xx in[x-.014,x+.014]for z,y in[(za,ya),(zb,yb),(zb,yb+.85),(za,ya+.85)]],F,'HouseSmokedGlass','guard')
 # Faithful ramp contact lives inside source stair; no convex hull over void.
 z0,y0=p(0,0);z1,y1=p(4.2,rise)
 collision.append({'name':'StairRamp_'+str(flight),'vertices':[[x,y,z]for x in[x0,x1]for z,y in[(z0,max(102,y0-.16)),(z1,y1-.16),(z1,y1),(z0,y0)]]})
box('RG_StairMidLanding',94.8,98.7,104.01,104.25,46.2,48.2,'warm_stone','floor')
for i,(a,b) in enumerate([([94.86,46.2],[94.86,48.14]),([94.86,48.14],[98.64,48.14]),([98.64,48.14],[98.64,46.2])]):
 wall('RG_MidLandingGuard_'+str(i),a,b,104.25,105.29,.045,'HouseSmokedGlass','guard');rail('RG_MidLandingRail_'+str(i),[a[0],105.31,a[1]],[b[0],105.31,b[1]])
# Two bearing cheeks under landing, entirely inside private stair reservation.
for x in[94.9,98.6]:box('RG_MidLandingBearing_'+str(x),x-.08,x+.08,102,104.02,47.9,48.1,'ivory_enamel','structure')
# Guards around actual stair opening, omitting upper entry at X96.9..98.7/Z42.
for i,(a,b) in enumerate([([94.65,45],[94.65,48.35]),([94.65,48.35],[98.85,48.35]),([98.85,48.35],[98.85,42]),([94.65,45],[96.75,45]),([96.75,45],[96.75,42])]):
 wall('RG_StairWellBase_'+str(i),a,b,106.5,106.67,.09,'warm_walnut','guard');wall('RG_StairWellGlass_'+str(i),a,b,106.67,107.55,.028,'HouseSmokedGlass','guard');wall('RG_StairWellCap_'+str(i),a,b,107.55,107.63,.12,'champagne_metal','guard')
# Open-edge support around hole follows actual perimeter, no beam across routes.
for i,(a,b) in enumerate([([94.6,45],[94.6,48.4]),([94.6,48.4],[98.9,48.4]),([98.9,48.4],[98.9,42]),([96.7,45],[96.7,42])]):wall('RG_OpeningTrimmer_'+str(i),a,b,106.26,106.5,.10,'warm_walnut','structure')
# Pitless lower receiver. No added vertex falls below Y102.
vv=[[x,y,z]for x in[100.5,103]for z,y in[(43.05,102),(45.45,102),(45.45,102.2),(43.05,102)]]
mesh('RG_PitlessBoardingRamp',vv,F,'warm_stone','ramp')
box('RG_LowerBoardingSill',100.5,103,102,102.2,45.45,45.55,'warm_stone','floor')
# Three fixed shaft sides, the existing telescoping gates own each front aperture.
for i,(a,b) in enumerate([([99.6,45.5],[99.6,49.35]),([99.6,49.35],[103.9,49.35]),([103.9,49.35],[103.9,45.5])]):
 wall('RG_ShaftGlass_'+str(i),a,b,102.02,109.65,.06,'HouseSmokedGlass','shaft')
 for j,p in enumerate([a,b]):box('RG_ShaftMullion_%d_%d'%(i,j),p[0]-.045,p[0]+.045,102.02,109.7,p[1]-.045,p[1]+.045,'champagne_metal','shaft')
box('RG_ShaftCrown',99.55,103.95,109.65,109.8,45.48,49.4,'ivory_enamel','shaft')
# Front closes between gates and above upper header, never across gate apertures.
for x0,x1 in[(99.6,100.5),(103,103.9)]:box('RG_ShaftFrontPier_'+str(x0),x0,x1,102.02,109.65,45.48,45.54,'ivory_enamel','shaft')
box('RG_ShaftFrontInterfloor',100.5,103,104.99,106.5,45.48,45.54,'ivory_enamel','shaft')
box('RG_ShaftFrontHead',100.5,103,109.3,109.65,45.48,45.54,'ivory_enamel','shaft')
# Useful quiet niche and outlook edge are integrated, not a second berth programme.
box('RG_QuietDeskPlinth',95.2,98.3,106.5,106.85,36.3,37.1,'ivory_enamel','built_in')
box('RG_QuietDesk',95.1,98.4,107.24,107.34,36.2,37.3,'warm_walnut','built_in')
box('RG_QuietDeskBack',95.2,98.3,106.85,107.25,36.3,36.45,'ivory_enamel','built_in')
for i,z in enumerate([38.4,39.1]):box('RG_InwardShelf_'+str(i),94.5,95.1,108.1,108.18,z,z+.45,'warm_walnut','built_in')
# Sheltered pause angled to the actual gallery edge, leaving broad circulation.
for i,(a,b) in enumerate([([108.7,39.1],[110.6,40.1]),([110.6,40.1],[110.6,42.4])]):
 wall('RG_ViewSeatBase_'+str(i),a,b,106.5,106.87,.65,'ivory_enamel','built_in');wall('RG_ViewSeatTop_'+str(i),a,b,106.87,107.0,.72,'warm_walnut','built_in')
# Source fixture family, each complete assembly paired to a light marker.
for name,x,z,y in[('Landing',100.1,40,109.3),('Quiet',97,37.6,109.3),('View',109.3,41.5,110.1),('Stair',96.6,47.2,109.3)]:
 box('RG_LampStem_'+name,x-.04,x+.04,y+.12,110.51,z-.04,z+.04,'champagne_metal','fixture');box('RG_LampHousing_'+name,x-.35,x+.35,y,y+.12,z-.20,z+.20,'warm_walnut','fixture');box('RG_LampLens_'+name,x-.29,x+.29,y-.035,y,z-.15,z+.15,'GardenOpalLens','fixture')
 ob=bpy.data.objects.new('DATUM_RG_light_'+name,None);bpy.context.collection.objects.link(ob);ob.location=xyz((x,y-.07,z));ob['kind']='visible fixture light';new.append(ob)
# Preserve originals except the declared bounded roof and complete fixture relocation.
allowed=['CR_RoyaltyLowerRoof']+relocated
preserved={n:original[n]==fingerprint(bpy.data.objects[n])for n in original if n not in allowed}
assert all(preserved.values()),[n for n,v in preserved.items()if not v]
for o in new:
 if o.type=='MESH':
  vv=[o.matrix_world@v.co for v in o.data.vertices]
  assert min(v.z for v in vv)>=101.9999,(o.name,min(v.z for v in vv))
  assert max(v.z for v in vv)<=112.0001,o.name
  assert min(-v.y for v in vv)>=29 and max(-v.y for v in vv)<51,o.name
# Original immutable source preserved. Save named successor then selected runtime geometry.
bpy.ops.file.pack_all();native=R/'source/ROYALTY790_upper_candidate_r002.blend';bpy.ops.wm.save_as_mainfile(filepath=str(native))
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.context.scene.objects:
 if o.type in['MESH','EMPTY'] and not o.hide_render:o.select_set(True)
export=R/'exports/ROYALTY790_upper_candidate_r002.glb';bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',export_yup=True,export_extras=True,use_selection=True)
checks=[]
for o in new:
 if o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data);volume=bm.calc_volume(signed=True);bad=sum(not e.is_manifold for e in bm.edges);bm.free();checks.append({'name':o.name,'volume':volume,'nonmanifold_edges':bad})
assert sha(src)==PINS[str(src.relative_to(ROOT))]
receipt={'status':'AUTHORED_CANDIDATE_NOT_ADOPTED','native_sha256':sha(native),'export_sha256':sha(export),'source_original_unchanged':True,'preserved_original_objects':preserved,'declared_changed_originals':allowed,'new_meshes':len(checks),'mesh_checks':checks,'holes_world_xxzZ':holes,'upper_floor_boundary':poly,'collision_ramps':collision,'lift':{'origin_world':[101.75,0,45.65],'rotation_y':-math.pi/2,'floor_heights':[102.2,106.5],'same_unit':790,'operation_ready':False},'open_gates':['native_reopen','export_equivalence','body_headroom','runtime_traversal','main_context_review','admission_binding']}
(R/'evidence/BUILD_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('ROYALTY_CANDIDATE_AUTHORED',len(checks),'original objects preserved',len(preserved))
