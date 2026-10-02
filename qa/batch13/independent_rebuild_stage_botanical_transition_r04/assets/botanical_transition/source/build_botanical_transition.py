"""AST-BOT-010: original script-assisted raised planted-seat end transition.
Self-contained generator plus local helpers and unchanged shared original materials.
Source X along edge, Y rear, Z up. Source root is start nominal seam/floor.
"""
import bpy,bmesh,json,math,hashlib,importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];CAT=ROOT.parents[1]
def load(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
H=load('transition_profiles',ROOT/'source/profile_helpers.py')
MATS=load('original_guest_materials',CAT/'standards/materials.py').materials()
MATS.update(load('original_botanical_materials',CAT/'standards/botanical_materials.py').materials());H.MATS=MATS
FRONT=[(-.150,.095),(-.150,.402),(-.115,.413),(-.032,.413),(.004,.381),(.018,.177),(.084,.105),(.084,0),(-.090,0),(-.129,.045)]
BACK=[(-.880,.095),(-.880,.402),(-.925,.415),(-.984,.415),(-1.019,.375),(-1.014,.092),(-.975,0),(-.865,0),(-.840,.060),(-.840,.095)]
FRONT_CAP=[(-.177,.413),(-.163,.430),(.043,.430),(.058,.417),(.053,.396),(-.164,.396)]
BACK_CAP=[(-1.037,.414),(-1.024,.430),(-.868,.430),(-.854,.417),(-.861,.396),(-1.024,.396)]
BRACKET=[(-.033,.065),(.227,.065),(.247,.091),(.280,.218),(.420,.355),(.442,.394),(.442,.415),(-.032,.415),(-.063,.370),(-.063,.107)]
FOOT=[(-.075,0),(.240,0),(.252,.019),(.244,.065),(-.058,.065)]
PARTS=[];COLL=[];MARKERS=[]
def sta(a,b):return [(a,0,1,0,a),(b,0,1,0,b)]
def points(a,b,profile):return [[x,-d,z] for x in [a,b] for d,z in profile]
def physical(name,points,purpose):COLL.append({'name':name,'type':'convex_hull_points','points_source_m':points,'purpose':purpose})
def part(name,a,b,p,role,bevel=.0007,collision=False,purpose=''):
 o=H.sweep(name,sta(a,b),p,role,bevel);PARTS.append(o)
 if collision:physical(name,points(a,b,p),purpose or name)
 return o
def box(name,x0,x1,y0,y1,z0,z1,role,collision=True,bevel=.0007,purpose=''):
 return part(name,x0,x1,[(-y0,z0),(-y1,z0),(-y1,z1),(-y0,z1)],role,bevel,collision,purpose)
def loft(name,profile,stations,role,cap=False,collision=True):
 p0=profile
 o=part(name,stations[0][0],stations[-1][0],p0,role)
 bpy.data.objects.remove(o,do_unlink=True);PARTS.remove(o)
 verts=[]
 for x,rise in stations:
  verts += [(x,-d,z+rise*(1 if cap else min(1,max(0,(z-.105)/.270)))) for d,z in profile]
 n=len(profile);faces=[(k*n+j,k*n+(j+1)%n,(k+1)*n+(j+1)%n,(k+1)*n+j) for k in range(len(stations)-1) for j in range(n)];faces +=[tuple(reversed(range(n))),tuple((len(stations)-1)*n+j for j in range(n))]
 me=bpy.data.meshes.new(name+'_mesh');me.from_pydata(verts,[],faces);me.update();ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);me.materials.append(MATS[role]);ob['material_role']=role;ob['design_method']='Intentional retaining profile with discrete supported upper cell, editable loft mesh';PARTS.append(ob)
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
 uv=me.uv_layers.new(name='metric_material_uv');sc=tuple(MATS[role].get('meters_per_tile_uv',[1,1]))
 for f in me.polygons:
  axes=sorted(range(3),key=lambda i:abs(f.normal[i]))[:2]
  for li in f.loop_indices:
   v=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]]/sc[0],v[axes[1]]/sc[1])
 b=ob.modifiers.new('Editable eased arris','BEVEL');b.width=.0007;b.segments=1;b.limit_method='ANGLE';b.angle_limit=math.radians(42)
 w=ob.modifiers.new('Editable weighted normals','WEIGHTED_NORMAL');w.keep_sharp=True
 if collision:
  if name=='front_rising_retaining_wall':
   def clip_profile(poly,upper):
    out=[]
    for a,b in zip(poly,poly[1:]+poly[:1]):
     ia=a[1]>=.177 if upper else a[1]<=.177;ib=b[1]>=.177 if upper else b[1]<=.177
     if ia:out.append(a)
     if ia!=ib:
      t=(.177-a[1])/(b[1]-a[1]);out.append([a[j]+t*(b[j]-a[j]) for j in range(2)])
    return out
   for k in range(len(stations)-1):
    for label,upper in [('lower_foot',False),('upper_face',True)]:
     pp=clip_profile(profile,upper);pts=[[x,-d,z+r*min(1,max(0,(z-.105)/.270))] for x,r in stations[k:k+2] for d,z in pp]
     physical(name+'_'+label+'_segment_'+str(k+1),pts,'Split actual front profile to preserve seated back clearance above Z0.47')
  elif name=='rear_rising_retaining_wall':
   def clip_z(poly,upper):
    out=[]
    for a,b in zip(poly,poly[1:]+poly[:1]):
     ia=a[2]>=.105 if upper else a[2]<=.105;ib=b[2]>=.105 if upper else b[2]<=.105
     if ia:out.append(a)
     if ia!=ib:
      t=(.105-a[2])/(b[2]-a[2]);out.append([a[j]+t*(b[j]-a[j]) for j in range(3)])
    return out
   physical(name+'_lower_plinth',clip_z(verts[:n],False)+clip_z(verts[-n:],False),'Rear lower inside return isolated below soil base; cannot bridge planting cavity')
   for k in range(len(stations)-1):physical(name+'_upper_segment_'+str(k+1),clip_z(verts[k*n:(k+1)*n],True)+clip_z(verts[(k+1)*n:(k+2)*n],True),'Rear wall above soil base; preserves actual 730mm clear structural cavity')
  else:
   for k in range(len(stations)-1):physical(name+'_segment_'+str(k+1),verts[k*n:(k+2)*n],name)
 return ob

def marker(name,p,role,target,normal=None):
 o=bpy.data.objects.new('MARKER_'+name,None);bpy.context.collection.objects.link(o);o.location=p;o.empty_display_size=.026;o.empty_display_type='PLAIN_AXES';o['marker_kind']=role;o['physical_target']=target;o['source_m']=list(p)
 if normal:o['physical_normal_source']=normal
 o['native_glb_m']=[p[0],p[2],-p[1]];MARKERS.append(o);return o

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1
 stations=[(.001,0),(.300,0),(.680,.400),(1.799,.400)]
 wall_stations=stations[:-1]+[(1.796,.400)]
 loft('front_rising_retaining_wall',FRONT,wall_stations,'warm_stone')
 loft('rear_rising_retaining_wall',BACK,wall_stations,'warm_stone')
 part('lower_basin_floor',.001,1.796,[(-.880,.075),(-.130,.075),(-.130,.105),(-.880,.105)],'warm_stone',collision=True)
 # Original seam coping is unmodified through the 300mm start run. The raised
 # upper front coping becomes the back of the sitting edge while the narrow
 # low bearing shoulder retains the timber seat at its unchanged datum.
 part('original_start_front_coping',.001,.300,FRONT_CAP,'ivory_enamel',collision=False)
 raised_front_profile=[(-.177,.413),(-.163,.430),(-.055,.430),(-.030,.417),(-.035,.396),(-.164,.396)]
 loft('raised_front_coping',raised_front_profile,[(.300,0),(.680,.4),(1.799,.4)],'ivory_enamel',True,False)
 loft('rear_rising_coping',BACK_CAP,stations,'ivory_enamel',True,False)
 low_shoulder=[(-.030,.396),(-.030,.430),(.043,.430),(.058,.417),(.053,.396)]
 part('continuous_low_seat_bearing_shoulder',.300,1.793,low_shoulder,'ivory_enamel',collision=False)
 # Caps are covered by conservative wall-following compounds, not extra tiny hulls.
 # Their modest finite overreach is measured explicitly in QA.
 box('transverse_riser_retaining_wall',.560,.680,.150,.880,.105,.813,'warm_stone',purpose='Separates soil levels and supports upper floor end')
 box('transverse_riser_coping',.551,.689,.150,.880,.813,.830,'ivory_enamel',False)
 box('upper_cell_floor',.680,1.680,.150,.880,.335,.365,'warm_stone',purpose='Physical upper soil support slab')
 for i,(x0,x1) in enumerate([(.730,.830),(1.520,1.620)],1):
  box('upper_cell_floor_pier_'+str(i),x0,x1,.220,.810,0,.335,'warm_stone',purpose='Floor contact through actual pier to upper soil base')
 box('closed_end_retaining_return',1.680,1.796,.150,.880,.105,.813,'warm_stone',purpose='Terminal wall closes both basin levels')
 box('closed_end_coping_return',1.680,1.799,.177,1.024,.813,.830,'ivory_enamel',False)
 box('lower_usable_soil_volume',.001,.560,.150,.880,.105,.390,'botanical_soil',False,0)
 box('upper_usable_soil_volume',.680,1.680,.150,.880,.365,.790,'botanical_soil',False,0)
 for i,(a,b) in enumerate([(.020,.166),(.174,.326),(.334,.490)],1):
  p=[(a,.415),(a,.465),(a+.004,.470),(b-.008,.470),(b,.464),(b,.431),(b-.014,.415)]
  part('timber_sitting_ribbon_'+str(i),.001,1.799,p,'warm_walnut',.0006,False)
 # One broad plate represents three slats; it closes 8mm ribbon slots only.
 physical('seat_support_plate',points(.001,1.799,[(.020,.415),(.490,.415),(.490,.470),(.020,.470)]),'Three solid seat ribbons, maximum slot overreach 4mm')
 for i,(a,b) in enumerate([(.080,.120),(.350,.390)],1):part('timber_underseat_bearing_rail_'+str(i),.001,1.799,[(a,.381),(b,.381),(b,.415),(a,.415)],'warm_walnut',collision=True)
 part('recessed_front_shadow_stringer',.001,1.790,[(.021,.198),(.026,.198),(.026,.211),(.021,.211)],'champagne_metal',0)
 for i,x in enumerate([.220,.900,1.580],1):
  part('seat_load_bracket_'+str(i),x-.043,x+.043,BRACKET,'ivory_enamel',.0005,False)
  part('floor_contact_bracket_shoe_'+str(i),x-.043,x+.043,FOOT,'warm_stone',.0005,False)
  # A single purposeful support compound per shoe+bracket, does not bridge bays.
  def split_support(poly,upper):
   out=[]
   for a,b in zip(poly,poly[1:]+poly[:1]):
    ia=a[1]>=.218 if upper else a[1]<=.218;ib=b[1]>=.218 if upper else b[1]<=.218
    if ia:out.append(a)
    if ia!=ib:
     t=(.218-a[1])/(b[1]-a[1]);out.append([a[j]+t*(b[j]-a[j])for j in range(2)])
   return out
  physical('floor_to_seat_support_lower_'+str(i),points(x-.043,x+.043,split_support(BRACKET,False)+FOOT),'Bracket/shoe lower knee compound, no bridge to upper flare')
  physical('floor_to_seat_support_upper_'+str(i),points(x-.043,x+.043,split_support(BRACKET,True)),'Actual upper flared bracket, split at kneeZ.218 to reduce under-seat overreach')
  marker('seat_contact_'+str(i),(x,-.250,.470),'physical seat upper surface','timber_sitting_ribbon_2',[0,0,1])
  marker('floor_contact_'+str(i),(x,-.100,0),'physical floor contact','floor_contact_bracket_shoe_'+str(i),[0,0,-1])
  marker('seat_bearing_'+str(i),(x,-.100,.415),'physical bracket-to-timber bearing','seat_load_bracket_'+str(i),[0,0,1])
 marker('origin',(0,0,0),'nominal floor/seam datum','nominal, deliberately 1mm before physical seam')
 marker('start_front_wall',(.001,.080,.200),'physical mating face','front_rising_retaining_wall',[-1,0,0])
 marker('start_rear_wall',(.001,.930,.200),'physical mating face','rear_rising_retaining_wall',[-1,0,0])
 marker('start_seat',(.001,-.240,.445),'physical mating face','timber_sitting_ribbon_2',[-1,0,0])
 marker('lower_soil',(.280,.515,.390),'physical planting surface','lower_usable_soil_volume',[0,0,1])
 marker('upper_soil',(1.100,.690,.790),'physical planting/root surface','upper_usable_soil_volume',[0,0,1])
 marker('upper_base_contact',(1.100,.515,.365),'physical soil-to-base contact','upper_cell_floor',[0,0,1])
 marker('rear_coping_top',(1.100,.940,.830),'physical coping upper surface','rear_rising_coping',[0,0,1])
 marker('closed_end',(1.796,.515,.600),'physical terminal outer surface','closed_end_retaining_return',[1,0,0])
 for o in PARTS+MARKERS:o['catalogue_id']='AST-BOT-010'
 sc=bpy.context.scene;sc['catalogue_id']='AST-BOT-010';sc['source_method']='Original script-assisted editable semantic meshes with retained modifiers';sc['scope']='Component only, no host, species, actor, structural or game acceptance';bpy.context.view_layer.update()
 lo,hi,dims,tris=H.measured(PARTS)
 blend=ROOT/'source/AST-BOT-010.blend';glb=ROOT/'exports/AST-BOT-010.glb'
 bpy.ops.wm.save_as_mainfile(filepath=str(blend),compress=True)
 repairs=H.export(PARTS,glb,MARKERS)
 cells=[{'id':'lower','soil_polygon_source_xy_m':[[.001,.15],[.560,.15],[.560,.88],[.001,.88]],'soil_top_z_m':.390,'base_top_z_m':.105,'depth_m':.285},{'id':'upper','soil_polygon_source_xy_m':[[.680,.15],[1.680,.15],[1.680,.88],[.680,.88]],'soil_top_z_m':.790,'base_top_z_m':.365,'depth_m':.425}]
 manifest={'catalogue_id':'AST-BOT-010','name':'Raised planted-seat end transition','source_blend':'source/AST-BOT-010.blend','runtime_glb':'exports/AST-BOT-010.glb','dimensions_m':dims,'min_m':lo,'max_m':hi,'triangles':tris,'source_parts':len(PARTS),'editable_semantic_parts':[o.name for o in PARTS],'material_roles':sorted(set(o['material_role'] for o in PARTS)),'pivot_source_m':[0,0,0],'frame':'Blender source X along, Y rear, Z up; native GLB (x,z,-y)','seams':[{'id':'start','profile':'planted_seat_470_soil_390','nominal_source_m':[0,0,0],'physical_face_x_m':.001,'outward_normal_source':[-1,0,0],'nominal_joint_m':.002}],'closed_terminal':True,'terminal_finish':{'stone_outer_face_x_m':1.796,'coping_and_timber_outer_x_m':1.799,'physical_finish_reveal_m':.003,'low_seat_shoulder_end_x_m':1.793,'metal_stringer_end_x_m':1.790,'purpose':'Real finish terminations eliminate exposed same-facing cross-material end planes; unchanged start profile retained'},'seat':{'top_z_m':.470,'underside_z_m':.415,'front_y_m':-.490,'back_y_m':-.020,'useful_length_m':1.798,'supports_x_m':[.220,.900,1.580],'support_width_m':.086,'support_chain':'Three timber ribbons/two bearing rails to three flared brackets, three shoes, floor Z0'},'soil_cells':cells,'upper_soil_support':{'slab_z_m':[.335,.365],'piers_x_m':[[.730,.830],[1.520,1.620]],'piers_y_m':[.220,.810],'piers_z_m':[0,.335],'side_and_end_retaining_walls':True},'root_reservations':[{'asset_id':'AST-BOT-008','root_source_m':[1.100,.690,.790],'root_max_xy_m':[.400,.350],'rear_trailing_only':True}],'plant_context':'AST-BOT-007 canopy and AST-BOT-009 flowering roots use unchanged AST-BOT-004 context; no claim of all roots sharing this cell','rear_coping_upper_section':{'source_y_m':[.854,1.037],'source_z_m':[.796,.830],'root_relative_y_m':[.164,.347],'root_relative_top_z_m':.040},'approaches':{'front_clear_box_source_m':[[.001,-1.690,0],[1.799,-.490,2.0]],'rear_maintenance_clear_box_source_m':[[.001,1.080,0],[1.799,1.880,2.0]],'trailing_exception':'BOT-008 swept foliage beyond rear coping is reserved; maintenance access is flanking/from rear outside that measured sweep','not_actor_certification':True},'markers':[{'name':o.name,'source_m':list(o.location),'native_glb_m':[o.location.x,o.location.z,-o.location.y],'kind':o['marker_kind'],'physical_target':o['physical_target'],'physical_normal_source':list(o.get('physical_normal_source',[]))} for o in MARKERS],'collision_file':'collision_proposals.json','export':{'y_up':True,'role_consolidation':True,'retained_markers':len(MARKERS),'UV_repaired_polygons':repairs,'opaque_materials':True,'packed_original_textures':True},'hashes':{'blend_sha256':sha(blend),'glb_sha256':sha(glb)},'limitations':['Original editable component proposal only','No recovered host room, deck void, structural load, irrigation, species suitability or game integration','Collision proposal excludes soil/foliage to preserve planting cavities; optional soil support volume may be adopted separately']}
 (ROOT/'AST-BOT-010.manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');(ROOT/'manifest.json').write_text(json.dumps({'family':'AST-BOT raised planted-seat extension','unique_assets':1,'assets':[manifest]},indent=2)+'\n')
 (ROOT/'collision_proposals.json').write_text(json.dumps({'asset_id':'AST-BOT-010','frame':'Blender source metres','status':'Purposeful numeric compounds, not adopted physics','solids':COLL,'excluded':['soil masses','fine finish layers','front approach','between-bracket underseat bays','upper/lower planting volumes'],'count':len(COLL)},indent=2)+'\n')
 print('TRANSITION_BUILT',json.dumps({'dims':dims,'triangles':tris,'parts':len(PARTS),'collision':len(COLL),'markers':len(MARKERS)}))
if __name__=='__main__':main()
