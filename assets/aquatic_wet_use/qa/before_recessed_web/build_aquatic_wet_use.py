"""Original editable aquatic wet-use components. Blender 4.3.2.
Source-only: blender -b -t 2 --python-exit-code 1 --python this_file.
No substance, fluid behavior, temperature, pressure, anatomy, species or host acceptance.
"""
import bpy,bmesh,math,json,hashlib,importlib.util
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parents[1];CAT=BASE.parents[1]
for sub in ('source','exports','qa'):(BASE/sub).mkdir(parents=True,exist_ok=True)
spec=importlib.util.spec_from_file_location('aquatic_materials',CAT/'standards/aquatic_materials.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);MATS=mod.materials()
P='aquatic_pearl_float';O='aquatic_orange_float';T='aquatic_edge_tile';D='aquatic_dark_grip';A='aquatic_satin_alloy'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def glb(p):return [p[0],p[2],-p[1]]
def reset(ident):
 global PARTS,MARKERS,JOINS,COLL,VOIDS,ROOT,REMOVALS,MOVING
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);PARTS=[];MARKERS=[];JOINS=[];COLL=[];VOIDS=[];REMOVALS=[];MOVING=[]
 ROOT=bpy.data.objects.new(ident,None);bpy.context.collection.objects.link(ROOT);ROOT['catalogue_id']=ident;ROOT['source_frame']='metres X width Y depth Z up front -Y';ROOT['native_glb_frame']='metres X width Y up Z front';ROOT['water_behavior']='UNIMPLEMENTED; capped interfaces, substance and species unknown'
 bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1

def mesh(name,verts,faces,role=P,bevel=0):
 me=bpy.data.meshes.new(name+'_editable');me.from_pydata(verts,[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
 ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);ob.parent=ROOT;ob['material_role']=role;ob['provenance']='Original aquatic component geometry; generic metric UV authoring';me.materials.append(MATS[role]);uv=me.uv_layers.new(name='metric_material_uv');uv.active_render=True
 sx,sy=MATS[role]['meters_per_tile_uv']
 for f in me.polygons:
  axis=max(range(3),key=lambda k:abs(f.normal[k]));axes=[k for k in range(3)if k!=axis]
  for li in f.loop_indices:
   p=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(p[axes[0]]/sx,p[axes[1]]/sy)
 if bevel:
  m=ob.modifiers.new('Editable edge easing','BEVEL');m.width=bevel;m.segments=2;m.limit_method='ANGLE';m.angle_limit=math.radians(35)
  m=ob.modifiers.new('Editable weighted normals','WEIGHTED_NORMAL');m.keep_sharp=True
 PARTS.append(ob);return ob

def box(name,c,d,role=P,bevel=.002):
 x,y,z=c;a,b,h=[v/2 for v in d]
 return mesh(name,[(x+i*a,y+j*b,z+k*h)for i,j,k in[(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],role,bevel)
def extrude(name,profile,axis,a,b,role=P,bevel=0):
 axes=[i for i in range(3)if i!=axis];vs=[]
 for dep in(a,b):
  for p in profile:
   v=[0,0,0];v[axis]=dep;v[axes[0]]=p[0];v[axes[1]]=p[1];vs.append(v)
 n=len(profile);return mesh(name,vs,[tuple(reversed(range(n))),tuple(n+i for i in range(n))]+[(i,(i+1)%n,(i+1)%n+n,i+n)for i in range(n)],role,bevel)
def clipped(w,d,c=.06,x=0,y=0):return [(x-w/2+c,y-d/2),(x+w/2-c,y-d/2),(x+w/2,y-d/2+c),(x+w/2,y+d/2-c),(x+w/2-c,y+d/2),(x-w/2+c,y+d/2),(x-w/2,y+d/2-c),(x-w/2,y-d/2+c)]
def rod(name,a,b,r,role=A,n=12,phase=0):
 a,b=Vector(a),Vector(b);di=(b-a).normalized();seed=Vector((1,0,0))if abs(di.x)<.9 else Vector((0,1,0));u=di.cross(seed).normalized();v=di.cross(u)
 vs=[p+r*(u*math.cos(2*math.pi*i/n+phase)+v*math.sin(2*math.pi*i/n+phase))for p in(a,b)for i in range(n)]
 return mesh(name,vs,[tuple(reversed(range(n))),tuple(n+i for i in range(n))]+[(i,(i+1)%n,(i+1)%n+n,i+n)for i in range(n)],role)
def join(a,b,p,kind='boundary_contact'):
 JOINS.append({'parts':[a.name,b.name],'probe_source_m':list(p),'probe_gltf_m':glb(p),'kind':kind})
def mark(name,p,part=None,n=None,kind='physical_surface_contact',note=''):
 o=bpy.data.objects.new(name,None);bpy.context.collection.objects.link(o);o.parent=part.parent if part else ROOT;o.location=p
 if part and part.parent!=ROOT:o.location=Vector(p)-part.parent.location
 o.empty_display_size=.02
 row={'name':name,'kind':kind,'source_m':list(p),'gltf_m':glb(p),'physical_part':part.name if part else None,'note':note};o['marker_kind']=kind;o['source_position_m']=list(p);o['gltf_position_m']=glb(p)
 if part:o['physical_part']=part.name
 if n:row['surface_normal_source']=n;row['surface_normal_gltf']=glb(n);o['surface_normal_source']=n;o['surface_normal_gltf']=glb(n)
 MARKERS.append(row)
def bounds(lo,hi):return {'min_source_m':lo,'max_source_m':hi,'min_gltf_m':[lo[0],lo[2],-hi[1]],'max_gltf_m':[hi[0],hi[2],-lo[1]]}
def void(name,lo,hi,purpose):VOIDS.append(dict(name=name,purpose=purpose,**bounds(lo,hi)))
def hull(name,vs,parts,note):COLL.append({'name':name,'type':'convex_hull_points','points_source_m':[list(p)for p in vs],'points_gltf_m':[glb(p)for p in vs],'covered_parts':[o.name for o in parts],'approximation_note':note})
def part_hull(ob,others=None,note='Local convex structural compound; edge easing is at most 2mm'):
 obs=[ob]+(others or []);hull(ob.name+'_compound',[v.co for o in obs for v in o.data.vertices],obs,note)
def collar_cap(name,a,b,r,host,p):
 ob=rod(name,a,b,r,A,12);join(ob,host,p);return ob

def panel(name,xwidth,y,zmin,zmax,left,right):
 # Straight-withdrawal cover rests against rear stops; seam never shares an exposed plane with the surrounding rim.
 cover=box(name,(0,y+.0125,(zmin+zmax)/2),(xwidth,.025,zmax-zmin),O,.003)
 for side,host,x in [('left',left,-xwidth/2+.018),('right',right,xwidth/2-.018)]:join(cover,host,[x,y,(zmin+zmax)/2])
 for x in[-xwidth*.32,xwidth*.32]:
  lug=box(name+'_grip_'+str(x),(x,y+.037,(zmin+zmax)/2),(.045,.025,.085),D,.004);join(lug,cover,[x,y+.025,(zmin+zmax)/2])
 moving_parts=[o for o in PARTS if o.name==name or o.name.startswith(name+'_grip_')]
 pivot=bpy.data.objects.new(name+'_REMOVAL_ROOT',None);bpy.context.collection.objects.link(pivot);pivot.parent=ROOT;pivot.location=(0,y+.0125,(zmin+zmax)/2);pivot.empty_display_size=.035;pivot['purpose']='Independent removable plate and grips; straight withdrawal only, no latch/dynamics implementation';pivot['zero_pose_source_m']=list(pivot.location);pivot['zero_pose_gltf_m']=glb(pivot.location);pivot['removal_vector_source_m']=[0,.40,0];pivot['removal_vector_gltf_m']=[0,0,-.40];bpy.context.view_layer.update()
 for ob in moving_parts:
  world=ob.matrix_world.copy();ob.parent=pivot;ob.matrix_world=world
 MOVING.append({'name':pivot.name,'parts':[o.name for o in moving_parts],'zero_pose_source_m':list(pivot.location),'zero_pose_gltf_m':glb(pivot.location),'removal_vector_source_m':[0,.40,0],'removal_vector_gltf_m':[0,0,-.40]})
 part_hull(cover,[o for o in PARTS if o.name.startswith(name+'_grip_')],note='Plate and short solid relief pulls combined; max 25mm convex fill between pulls, no hand opening declared');mark(name.upper()+'_SERVICE_FACE',[0,y+.025,(zmin+zmax)/2],cover,[0,1,0],note='Pull rearward after releasing unspecified retainers; no lock or operation simulation')
 REMOVALS.append({'name':name,'parts':[o.name for o in PARTS if o.name.startswith(name)],'translation_source_m':[0,.40,0],'translation_gltf_m':[0,0,-.40],'reserve':bounds([-xwidth/2-.006,y+.001,zmin-.006],[xwidth/2+.006,y+.40+.056,zmax+.006]),'method':'Full translated AABB sweep excludes only this cover and its two grips; 1mm departure avoids intentional seating contact','limitations':'Nominal removable cover proposal; release hardware, reach and force unknown'})
 return cover

def refreshment():
 sole=extrude('continuous_floor_isolator',clipped(.66,.54,.095),2,0,.025,D);part_hull(sole);mark('FLOOR_CONTACT',[0,0,0],sole,[0,0,-1])
 plinth=extrude('pearl_splayed_pedestal',clipped(.72,.60,.10),2,.025,.13,P,.003);join(sole,plinth,[0,0,.025]);part_hull(plinth)
 # Two thick swept side ribs make a supported open-front crescent, rather than a counter.
 ribs=[]
 profile=[(.015,.13),(.25,.13),(.25,1.385),(.195,1.50),(-.14,1.50),(-.265,1.415),(-.265,1.32),(-.19,1.32),(-.11,1.40),(.145,1.40),(.145,.24),(.015,.24)]
 for s,tag in[(-1,'left'),(1,'right')]:
  ob=extrude(tag+'_swept_crescent_rib',profile,0,s*.25-.035,s*.25+.035,P,.003);ribs.append(ob);join(ob,plinth,[s*.25,.12,.13])
  # Split profile compounds retain the useful vessel and service hollows.
  for suffix,prof in [('upright',[(.145,.13),(.25,.13),(.25,1.385),(.195,1.50),(.145,1.40)]),('head',[(.145,1.40),(.195,1.50),(-.14,1.50),(-.265,1.415),(-.265,1.32),(-.19,1.32),(-.11,1.40)]),('foot',[(.015,.13),(.145,.13),(.145,.24),(.015,.24)])]:
   vs=[(x,y,z)for x in[s*.25-.035,s*.25+.035]for y,z in prof];hull(tag+'_'+suffix,vs,[ob],'Profile-following local rib hull; no enclosing crescent hull')
 back=box('teal_splash_back',(0,.164,1.10),(.43,.038,.60),T,0)
 for ob in ribs:join(back,ob,[(-.215 if ob==ribs[0]else .215),.164,1.10])
 part_hull(back)
 hood=extrude('arched_orange_hood_infill',[(-.18,1.395),(.14,1.395),(.14,1.47),(-.13,1.47),(-.235,1.40),(-.235,1.345),(-.19,1.345)],0,-.215,.215,O,.002)
 for ob in ribs:join(hood,ob,[(-.215 if ob==ribs[0]else .215),0,1.43])
 part_hull(hood,note='Small convex approximation fills at most the 45mm underside hood corner; vessel clear volume terminates below it')
 # Hollow collector shell as four bands around a lower tray. Nothing pretends to be water.
 floor=extrude('orange_splash_collection_floor',clipped(.58,.51,.085,y=-.045),2,.835,.875,O,.002)
 for ob in ribs:join(floor,ob,[(-.24 if ob==ribs[0]else .24),.16,.85],kind='buried_structural_overlap')
 part_hull(floor)
 for x,tag in[(-.266,'left'),(.266,'right')]:
  rim=box(tag+'_raised_collection_return',(x,-.035,.907),(.048,.32,.064),O,.005);join(rim,floor,[x,-.035,.875]);part_hull(rim)
 lip=extrude('clipped_front_collection_lip',[(-.21,-.30),(.21,-.30),(.26,-.25),(.235,-.225),(-.235,-.225),(-.26,-.25)],2,.875,.930,O,.004);join(lip,floor,[0,-.275,.875]);part_hull(lip)
 # Raised narrow rails define a vessel contact; open gaps lead only to the contained collector.
 rails=[]
 for x in[-.075,0,.075]:
  ob=box('vessel_landing_rail_'+str(x),(x,-.11,.895),(.036,.22,.04),A,.003);join(ob,floor,[x,-.11,.875]);part_hull(ob);rails.append(ob)
 mark('VESSEL_CONTACT',[0,-.11,.915],rails[1],[0,0,1],note='Actual 36mm central landing rail; adjacent support rails; vessel and user compatibility unknown')
 cap=collar_cap('protected_capped_optional_outlet',[0,-.11,1.395],[0,-.11,1.31],.028,hood,[0,-.11,1.395]);part_hull(cap);mark('OPTIONAL_OUTLET_CAP',[0,-.11,1.31],cap,[0,0,-1],kind='physical_capped_interface',note='Closed adjustable interface; no substance or functioning flow')
 ctl=rod('bounded_select_pad',[.125,.145,1.20],[.125,.105,1.20],.055,O,12);join(ctl,back,[.125,.145,1.20]);part_hull(ctl);mark('SELECT_CONTACT',[.125,.105,1.20],ctl,[0,-1,0],kind='physical_control_contact')
 # Original raised cup glyph with open top, attached to the splash back. Material/color is supplemental.
 for name,c,d in[('glyph_vessel_left',(-.14,.140,1.19),(.014,.014,.10)),('glyph_vessel_right',(-.05,.140,1.19),(.014,.014,.10)),('glyph_vessel_base',(-.095,.140,1.14),(.10,.014,.014))]:
  g=box(name,c,d,P,0);join(g,back,[c[0],.145,c[2]])
 # Real rear service frame and support stops define a hollow low access bay.
 stops=[]
 for x,tag in[(-.18,'left'),(.18,'right')]:
  stop=box(tag+'_rear_panel_seat',(x,.215,.49),(.07,.040,.52),P,0);join(stop,ribs[0 if x<0 else 1],[(-.215 if x<0 else .215),.215,.49]);part_hull(stop);stops.append(stop)
 lower=box('service_bay_lower_sill',(0,.205,.22),(.43,.08,.05),P,0);join(lower,stops[0],[-.18,.215,.245]);join(lower,stops[1],[.18,.215,.245]);part_hull(lower)
 panel('rear_removable_service_plate',.35,.235,.255,.735,*stops)
 drain=collar_cap('visible_front_low_drain_cap',[0,-.29,.075],[0,-.325,.075],.029,plinth,[0,-.29,.075]);part_hull(drain);mark('LOW_DRAIN_CAP',[0,-.325,.075],drain,[0,-1,0],kind='physical_capped_interface',note='Capped provision only; drain route, host aperture and fluid behavior absent')
 mark('FRONT_APPROACH',[0,-.88,0],kind='nonphysical_approach_proposal',note='Not an actor position or reach certificate');mark('FLOOR_ORIGIN',[0,0,0],kind='placement_origin')
 void('vessel_air_space',[-.12,-.205,.925],[.12,.025,1.275],'Unoccupied vessel accommodation above landing rails; actual vessel fit unassigned')
 void('contained_splash_collection_air',[-.20,-.20,.880],[.20,.115,.887],'Collector air space above floor, deliberately excludes raised landing rails through separate smaller test regions')
 VOIDS.pop() # Three useful collector openings preserve the real raised rail geometry.
 for x in[-.1375,-.0375,.0375,.1375]:void('collector_gap_'+str(x),[x-.015,-.20,.880],[x+.015,-.025,.908],'Unoccupied collector gap between/alongside raised vessel landing rails')
 void('rear_service_approach',[-.32,.72,.05],[.32,1.05,.85],'Separate rear maintenance space after cover extraction; not a recovered room route')
 return 'Crescent optional refreshment pedestal',{'roles':['optional compatible-user refreshment','bounded vessel landing','contained splash collection','separate rear maintenance'],'fixed_height_m':1.50,'outlet_state':'closed cap','no_claims':['substance','temperature','pressure','consumption need','species suitability','working water'],'shape_intent':'Pearl twin crescent support ribs and orange recessed hood; no bar furniture or clinical wash anatomy'}

def rinse():
 sole=extrude('continuous_rinse_floor_isolator',clipped(.59,.51,.09,y=-.025),2,0,.025,D);part_hull(sole);mark('FLOOR_CONTACT',[0,-.025,0],sole,[0,0,-1])
 plinth=extrude('flared_rinse_load_plinth',clipped(.64,.60,.10,y=-.025),2,.025,.11,P,.003);join(sole,plinth,[0,-.025,.025]);part_hull(plinth)
 # Tapered perimeter spine has a genuine service hollow at the foot; upper plate is carried by both rails.
 rails=[]
 for s,tag in[(-1,'left'),(1,'right')]:
  profile=[(s*.245,.11),(s*.245,.72),(s*.16,1.92),(s*.10,2.06),(s*.065,2.06),(s*.11,1.91),(s*.185,.70),(s*.185,.11)]
  ob=extrude(tag+'_tapered_spine_rail',profile,1,.10,.24,P,.002);rails.append(ob);join(ob,plinth,[s*.215,.17,.11]);part_hull(ob,note='Tapered structural rail convex approximation; service opening remains between rails')
 back=extrude('upper_teal_control_web',[(-.19,.70),(.19,.70),(.115,1.91),(.070,2.06),(-.070,2.06),(-.115,1.91)],1,.10,.15,T,0)
 for ob,s in zip(rails,[-1,1]):join(back,ob,[s*.15,.125,1.28],kind='buried_structural_overlap')
 part_hull(back)
 # Protective head: curved plate plus two honest triangular gussets into the upper spine.
 head=extrude('swept_protective_head',[(-.34,1.995),(-.34,2.105),(-.24,2.18),(.12,2.18),(.24,2.095),(.24,2.01),(.13,2.08),(-.215,2.08)],0,-.205,.205,P,.002)
 for ob,s in zip(rails,[-1,1]):join(head,ob,[s*.09,.20,2.055],kind='buried_structural_overlap')
 part_hull(head,note='Protective head local hull may occupy shallow underside corner; capped interface region is below it')
 gussets=[]
 for x,tag in[(-.115,'left'),(.115,'right')]:
  ob=extrude(tag+'_head_load_gusset',[(.10,1.77),(.145,1.78),(.145,2.08),(-.23,2.08),(-.23,2.02)],0,x-.025,x+.025,O,.001);gussets.append(ob);join(ob,back,[x,.125,1.83],kind='buried_structural_overlap');join(ob,head,[x,-.17,2.08]);part_hull(ob)
 cap=collar_cap('capped_adjustable_head_interface',[0,-.205,2.08],[0,-.205,2.015],.053,head,[0,-.205,2.08]);part_hull(cap);mark('HEAD_INTERFACE_CAP',[0,-.205,2.015],cap,[0,0,-1],kind='physical_capped_interface',note='Protective housing only; cap center may be repositioned at authoring; no headroom, body, aiming, pressure or fluid claim')
 cradle=extrude('orange_bounded_control_cradle',[(-.15,.965),(.15,.965),(.16,1.04),(.13,1.195),(-.13,1.195),(-.16,1.04)],1,.047,.10,O,.004);join(cradle,back,[0,.10,1.08]);part_hull(cradle)
 controls=[]
 for x,r,tag in[(-.065,.042,'select'),(.070,.035,'stop')]:
  ob=rod('bounded_'+tag+'_control',[x,.047,1.08],[x,.018,1.08],r,D,12);join(ob,cradle,[x,.047,1.08]);part_hull(ob);controls.append(ob);mark(tag.upper()+'_CONTROL_CONTACT',[x,.018,1.08],ob,[0,-1,0],kind='physical_control_contact',note='Uncalibrated control area; no temperature, pressure or mode implementation')
 # Original three descending solid strokes inside the upper web indicate optional directed use, not water simulation.
 for i,x in enumerate([-.055,0,.055]):
  g=box('original_optional_rinse_glyph_'+str(i),(x,.092,1.51-abs(x)*.5),(.016,.016,.11),P,0);join(g,back,[x,.10,1.51-abs(x)*.5])
 lower=box('lower_service_cross_tie',(0,.17,.185),(.38,.14,.075),P,.002)
 for ob,s in zip(rails,[-1,1]):join(lower,ob,[s*.187,.17,.185],kind='buried_structural_overlap')
 part_hull(lower)
 stops=[]
 for x,tag in[(-.165,'left'),(.165,'right')]:
  ob=box(tag+'_rear_cover_seat',(x,.225,.44),(.075,.040,.45),P,0);join(ob,rails[0 if x<0 else 1],[(-.195 if x<0 else .195),.225,.44]);part_hull(ob);stops.append(ob)
 panel('rinse_rear_removable_plate',.32,.245,.225,.645,*stops)
 drain=collar_cap('low_front_capped_connection',[0,-.305,.07],[0,-.347,.07],.030,plinth,[0,-.305,.07]);part_hull(drain);mark('LOW_CONNECTION_CAP',[0,-.347,.07],drain,[0,-1,0],kind='physical_capped_interface')
 # Small open splash floor preserves a working void rather than a solid enclosing collider.
 tray=extrude('tile_splash_landing',clipped(.43,.28,.045,y=-.13),2,.11,.12,T,0);join(tray,plinth,[0,-.13,.11]);part_hull(tray);mark('SPLASH_FLOOR_CONTACT',[0,-.13,.12],tray,[0,0,1],note='Physical tile surface only; no standing/foot/body fit or drain performance')
 for x,tag in[(-.24,'left'),(.24,'right')]:
  curb=box(tag+'_splash_guard',(x,-.08,.1375),(.035,.24,.055),O,.005);join(curb,plinth,[x,-.08,.11]);part_hull(curb)
 mark('FRONT_APPROACH',[0,-.95,0],kind='nonphysical_approach_proposal',note='Unvalidated placement reservation, no species/body pose');mark('FLOOR_ORIGIN',[0,0,0],kind='placement_origin')
 void('front_unoccupied_rinse_space',[-.20,-.30,.17],[.20,.0,1.82],'Component-front air volume, not a shower stall, actor pose or body clearance certificate')
 void('rear_maintenance_approach',[-.33,.74,.05],[.33,1.05,.80],'Separate maintenance reserve after panel removal; host route unknown')
 return 'Supported rinse control blade',{'support':'Two tapered rails carry head and explicit orange gussets through flared floor plinth; wall support is not assumed','controls':'Bounded select and stop regions, uncalibrated','connections':'Closed downward head cap and low front capped provision, adjustable authoring positions','no_claims':['water behavior','body fit','headroom','plumbing','species compatibility','temperature','pressure','game interaction']}

def measure():
 dg=bpy.context.evaluated_depsgraph_get();points=[];tri=0
 for ob in PARTS:
  ev=ob.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();tri+=len(me.loop_triangles);points.extend(ob.matrix_world@v.co for v in me.vertices);ev.to_mesh_clear()
 lo=[min(p[i]for p in points)for i in range(3)];hi=[max(p[i]for p in points)for i in range(3)];return {'min_m':lo,'max_m':hi,'dimensions_m':[b-a for a,b in zip(lo,hi)]},tri

def export(ident):
 dg=bpy.context.evaluated_depsgraph_get();groups={};out=[]
 for src in PARTS:
  me=bpy.data.meshes.new_from_object(src.evaluated_get(dg));uv=me.uv_layers.active
  for layer in list(me.uv_layers):
   if layer!=uv:me.uv_layers.remove(layer)
  uv.name='metric_material_uv';uv.active_render=True;me.calc_loop_triangles();fix=set()
  for tr in me.loop_triangles:
   a,b,c=[uv.data[i].uv for i in tr.loops]
   if abs((b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x))<2e-12:fix.add(tr.polygon_index)
  sx,sy=MATS[src['material_role']]['meters_per_tile_uv']
  for pi in fix:
   p=me.polygons[pi];axis=max(range(3),key=lambda i:abs(p.normal[i]));axes=[i for i in range(3)if i!=axis]
   for li in p.loop_indices:
    co=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(co[axes[0]]/sx,co[axes[1]]/sy)
  ob=bpy.data.objects.new('EXPORT_'+src.name,me);bpy.context.collection.objects.link(ob);ob.matrix_world=src.matrix_world.copy();groups.setdefault((src.parent.name,src['material_role']),[]).append(ob)
 for (parentname,role),obs in groups.items():
  bpy.ops.object.select_all(action='DESELECT')
  for ob in obs:ob.select_set(True)
  bpy.context.view_layer.objects.active=obs[0];bpy.ops.object.join();ob=obs[0];ob.name=ident+'__'+('body' if parentname==ROOT.name else 'plate')+'__'+role;world=ob.matrix_world.copy();ob.parent=bpy.data.objects[parentname];ob.matrix_world=world;ob['material_role']=role;ob['semantic_parts']=json.dumps([s.name for s in PARTS if s['material_role']==role and s.parent.name==parentname]);out.append(ob)
 bpy.ops.object.select_all(action='DESELECT');ROOT.select_set(True)
 for ob in out:ob.select_set(True)
 for row in MOVING:bpy.data.objects[row['name']].select_set(True)
 for row in MARKERS:bpy.data.objects[row['name']].select_set(True)
 bpy.context.view_layer.objects.active=ROOT;bpy.ops.export_scene.gltf(filepath=str(BASE/'exports'/f'{ident}.glb'),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_extras=True,export_materials='EXPORT',export_texcoords=True,export_normals=True,export_cameras=False,export_lights=False)
 for ob in out:bpy.data.objects.remove(ob,do_unlink=True)

def main():
 bpy.context.preferences.filepaths.save_version=0;rows=[];coll={};api={}
 for ident,fn in[('AST-AQU-009',refreshment),('AST-AQU-010',rinse)]:
  reset(ident);title,details=fn();bpy.context.view_layer.update();bd,tri=measure()
  for im in bpy.data.images:
   if im.source=='FILE'and not im.packed_file:im.pack()
  bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'source'/f'{ident}.blend'),compress=True);export(ident)
  lo,hi=bd['min_m'],bd['max_m'];glo=[lo[0],lo[2],-hi[1]];ghi=[hi[0],hi[2],-lo[1]]
  rec={'catalogue_id':ident,'name':title,'title':title,'unique_design':True,'source':f'source/{ident}.blend','export':f'exports/{ident}.glb','generator':'source/build_aquatic_wet_use.py','source_frame':'metres Blender X width Y depth Z up front -Y','exchange_frame':'metres native GLB Y-up source(x,y,z)->(x,z,-y)','pivot':{'source_m':[0,0,0],'gltf_m':[0,0,0],'datum':'floor contact datum; host support unknown'},'bounds_blender_z_up':bd,'bounds_gltf_y_up':{'min_m':glo,'max_m':ghi,'dimensions_m':[b-a for a,b in zip(glo,ghi)]},'dimensions_blender_xyz_m':bd['dimensions_m'],'evaluated_triangles':tri,'editable_semantic_parts':len(PARTS),'semantic_parts':[o.name for o in PARTS],'material_roles':sorted(set(o['material_role']for o in PARTS)),'runtime_consolidation':'Static evaluated body copies grouped by material; separate purposeful removable plate root with plate/grips grouped by material; source/native zero pose and removal vector explicit','physical_and_proposal_markers':MARKERS,'joins':JOINS,'receiver_voids':VOIDS,'removal_proposals':REMOVALS,'independent_removable_roots':MOVING,'collision_proposal_file':'collision_proposals.json','marker_api_file':'marker_api.json','source_sha256':sha(BASE/'source'/f'{ident}.blend'),'glb_sha256':sha(BASE/'exports'/f'{ident}.glb'),'generator_sha256':sha(Path(__file__)),'details':details,'limitations':['Component only; no game, room, host fixture, anatomy/species or performance acceptance','Historical D08 changing and aft staff towel care remain separate; no recovered connecting aperture','No new room, guest, changing slot, seat or population','Substance, temperature, pressure, water behavior and plumbing unimplemented','Editable cap locations and removable cover are proposals; host support, headroom, release hardware and maintenance reach unknown']}
  rows.append(rec);(BASE/f'{ident}.manifest.json').write_text(json.dumps(rec,indent=2)+'\n');coll[ident]={'source_frame':'Blender Z-up metres','exchange_frame':'Native GLB Y-up metres','shapes':COLL,'preserve_voids':VOIDS,'removal_proposals':REMOVALS,'status':'Structural compound proposals; no engine physics or performance claim'};api[ident]=MARKERS
 (BASE/'manifest.json').write_text(json.dumps({'family':'aquatic_wet_use','revision':'aquatic-wet-use-01','assets':rows},indent=2)+'\n');(BASE/'collision_proposals.json').write_text(json.dumps(coll,indent=2)+'\n');(BASE/'marker_api.json').write_text(json.dumps(api,indent=2)+'\n')
 print('BUILT',[(r['catalogue_id'],r['evaluated_triangles'],r['dimensions_blender_xyz_m'])for r in rows])
if __name__=='__main__':main()
