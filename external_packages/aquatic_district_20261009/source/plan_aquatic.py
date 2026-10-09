"""Deterministic bounded aquatic section/floor planner. Requires Shapely 2.1.2."""
import json,math,hashlib,sys
from pathlib import Path
P=Path(__file__).resolve().parents[1];R=P.parents[1];INPUT=R if (R/'Game/data/spatial_layout.json').exists() else P/'dependencies'
# Existing installed dependency, no download or modification.
sys.path.insert(0,str(R.parent/'AstraeaTools/pythondeps'))
from shapely.geometry import Polygon,LineString,Point,box
from shapely.ops import triangulate,unary_union
from shapely import constrained_delaunay_triangles
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def lines(g):return [g] if g.geom_type=='LineString' else list(g.geoms)
def coords(g):return [[round(x,6),round(z,6)] for x,z in list(g.exterior.coords)[:-1]]
def polys(g):return [g] if g.geom_type=='Polygon' else list(g.geoms)
def record(n,g,y,t,owner,walk=True):
 ts=[]
 for q in polys(g):
  for tri in constrained_delaunay_triangles(q).geoms:
   assert q.covers(tri)
   ts.append(coords(tri))
 assert abs(sum(Polygon(a).area for a in ts)-g.area)<1e-5,n
 return {'id':n,'deck':'D08','boundary_polygons_xz':[{'boundary':coords(q),'holes':[list(a.coords)[:-1] for a in q.interiors]} for q in polys(g)],'triangles_xz':ts,'top_y':y,'thickness_m':t,'owner':owner,'walkable':walk,'area_m2':g.area}
outer=Polygon([(56,188),(62,182),(94,182),(100,188),(100,244),(94,250),(62,250),(56,244)])
center=[(78+11.5*math.cos(i*2*math.pi/128),216+20.5*math.sin(i*2*math.pi/128)) for i in range(128)]
loop=LineString(center+[center[0]]);river=loop.buffer(1.8,join_style=1,quad_segs=4)
river_outer=Polygon(river.exterior);island=Polygon(river.interiors[0])
arrival=box(56,235,62,247).intersection(outer)
entry_ramp=box(60.8,244.4,78.4,247.4)
runouts=[box(63.0,191.25,69.0,193.35),box(76.5,191.25,82.5,193.35)]
spa_centers=[(81.5,211.5),(81.5,223.5)];spa=[Point(*c).buffer(2.6,quad_segs=12) for c in spa_centers]
wet=outer.difference(unary_union([river_outer,arrival,entry_ramp]+runouts))
islandfloor=island.difference(unary_union(spa))
# All substrate here is new; no host floor rewritten. Only connection tongue touches retained edge.
floors=[record('AQD_annex_substrate',outer,44,.24,'compiler_new_annex_substrate',False),record('AQD_annex_wet_promenade',wet,45.45,.24,'compiler_new_annex_wet_promenade'),record('AQD_island_terrace',islandfloor,45.45,.24,'compiler_new_island_terrace'),record('AQD_public_connection_tongue',box(54,238,56,242),44,.24,'compiler_new_connection_tongue'),record('AQD_river_bed',river,44.30,.15,'asset_river_shell',False)]
ramps=[{'id':'wet_arrival_ramp','a':[61,44,245.9],'b':[78.4,45.45,245.9],'clear_width':2.6,'slope':'1:12'},
 {'id':'bridge_west_ramp','a':[60.5,45.45,229],'b':[60.5,47.70,202],'clear_width':2.6,'slope':'1:12'},
 {'id':'bridge_island_ramp','a':[73.4,47.70,202],'b':[73.4,45.45,229],'clear_width':2.6,'slope':'1:12'},
 {'id':'launch_ramp_flight_1','a':[92.4,45.45,244],'b':[92.4,47.40,220.6],'clear_width':2.4,'slope':'1:12'},
 {'id':'launch_ramp_flight_2','a':[95.2,47.40,220.6],'b':[95.2,49.35,244],'clear_width':2.4,'slope':'1:12'}]
slides=[]
for i,cx in enumerate([72,85.5]):
 path=[]
 for j in range(97):
  angle=math.pi/2+j*2*math.pi/96
  path.append([cx+5*math.cos(angle),49.35-4.0*j/96,188.5+4*math.sin(angle)])
 # End tangent continues left into isolated runout, away from AFK loop.
 for j in range(1,15):path.append([cx-.5*j,45.35,192.5])
 slides.append({'id':'AQD_slide_'+str(i+1),'trajectory_xyz':path,'internal_width_m':1.3,'wall_height_m':.48,'closed_side_thickness_m':.12,'launch_y':49.35,'runout_water_y':45.30,'runout_poly':coords(runouts[i]),'launch_pad':[cx,49.35,192.5],'exit_xyz':[cx-7,45.45,190.8],'physics':'not_implemented'})
lights=[]
for i,(x,z) in enumerate([(60,234),(63,186),(94,186),(97,234),(94,246),(79,247),(59,211),(97,209),(73,214),(77,230),(70,196),(88,196)]):
 lights.append({'id':'AQD_fixture_'+str(i),'xyz':[x,48.5 if x not in [73,77] else 48.0,z],'receiver_xyz':[x,45.45,z],'energy':1.2,'range_m':7,'role':'warm_guest_source','fixture':'modeled pendant on actual overhead bearing'})
for i,cx in enumerate([72,85.5]):lights.append({'id':'launch_task_'+str(i),'xyz':[cx,51.1,194.4],'receiver_xyz':[cx,49.35,194.4],'energy':1.2,'range_m':5,'role':'launch_task_source','fixture':'modeled pendant on actual roof bearing'})
plan={'schema':1,'status':'bounded construction delivery; host adoption pending','programme_key':'D08_directory_08','catalogue_registration':'Root must reserve identities; AQD names are package-local only. No catalogue changes.','coordinate_system':'Godot world XYZ metres; Blender=(X,-Z,Y); origin0, identity GLB placement',
 'annex_boundary':coords(outer),'no_material_below_y':43.76,'maximum_top_y':51.95,'protected_next_deck_datum_y':52.5,'floor_records':floors,'ramps':ramps,'plinth_closure_segments_xz':[[list(a),list(b)] for line in lines(wet.boundary.difference(outer.boundary).difference(river_outer.boundary).difference(unary_union([q.boundary for q in runouts]))) for a,b in zip(list(line.coords),list(line.coords)[1:])],
 'river':{'centerline_xyz':[[x,45.25,z] for x,z in center]+[[center[0][0],45.25,center[0][1]]],'length_m':loop.length,'clear_width_m':3.6,'bottom_y':44.3,'water_y':45.25,'rim_y':45.45,'bed_polygons':floors[-1]['boundary_polygons_xz'],'outer_xz':coords(river_outer),'island_xz':coords(island),'AFK':'closed topology reserved; no current, buoyancy, float mount, pause, save or recovery logic implemented'},
 'boarding':[{'id':'south_board','bank_xyz':[78,45.45,240.6],'water_xyz':[78,45.25,237.4],'transfer_xyz':[76,45.45,240.0],'recovery':True},{'id':'north_recovery','bank_xyz':[75,45.45,193.5],'water_xyz':[75,45.25,195.3],'transfer_xyz':[73.5,45.45,193.5],'recovery':True}],
 'slides':slides,'new_thermal_spa_pools':[{'id':'AQD_spa_5' if i==0 else 'AQD_spa_6','center_xz':list(c),'radius_m':2.6,'bottom_y':44.4,'water_y':45.05,'rim_y':45.45,'parent_programme':'D08_directory_08','gravity_adaptive_reservation':True} for i,c in enumerate(spa_centers)],
 'thermal_count_reconciliation':{'target':6,'retained':[{'parent':'D08_directory_02','source':'sol_entry_successors_20261008/D/D08_directory_02','basins':['bath_basin_bottom0','bath_basin_bottom1']},{'parent':'D08_directory_03','source':'sol_entry_successors_20261008/D/D08_directory_03','basins':['mineral_court_bottom','quiet_court_bottom']}],'new':2,'extra_directory_rooms':0,'gravity_physics':'not_implemented; handholds/transfer equipment and service/control reservations only; parameters undecided'},
 'lights':lights,'retained_cascade_interface':{'original_center_xz':[25,215],'original_radius':1.4,'original_bottom_y':42.8,'maintenance_deck_rect_xz':[21.0,23.0,214.3,215.7],'maintenance_top_y':44,'splash_screen_half_arc':'east half at radius2.2, bottom42.8, top45.4; leaves western maintainable side and falling stream clear','acoustic':'physical absorptive canopy/reveals only; no audio processing or hydraulic response'},
 'connectors':[{'id':'gentle_to_annex','host_xyz':[54,44,240],'annex_xyz':[56,44,240],'clear_width_m':4,'new_floor_owner':'compiler_new_connection_tongue','host_edit_required':False},{'id':'universal_changing_to_gentle','from_xyz':[-8,44,216],'to_xyz':[8,44,216],'status':'Root-owned host link; preserve existing axial arrival and adopt missing floor only if consolidated source still lacks it.'},{'id':'wet_service_annex','xyz':[100,45.45,210],'clear_width_m':2.4,'status':'Source built internal service pad; onward ship-service route root-owned'}],
 'retained_vs_new':{'retained':['50x18m Grand Pool and Orchard section','Gentle Waters basin and retreat','Vesper watercourse receiver/stream/support/guards','D08-D10 aquatic lift and stairs','Living Gifts and Vesper floors/programmes','Eight delivered bath/wellness/changing/towel destination parents'],'new':['closed lazy-river shell and water visual','boarding/recovery/physical tubes','two helical slides with isolated runouts','step-free launch route and gallery','step-free island bridge','two complementary spa pools','splash/maintenance interfaces','wet support pavilions and real fixtures','new annex floor proposals']},
 'later_interfaces':['Water/swimming volumes and oxygen-independent recovery rules','Tube attachment/buoyancy/current and AFK safe interruption','Slide admission/start/exit/ride transfer','Pool temperature/gravity controls and gravity-safe failure state','Privacy door controllers and towel stock persistence','Service logistics, NPC reservations/body fit','Host floor compiler/collision/light-budget adoption']}
# Binding coarse fit checks: actual current regions and plan-hull; includes all D08 programme rectangles.
hull=Polygon(json.loads((INPUT/'Game/data/hull_envelope.json').read_text())['plan_xz_m']);assert hull.contains(outer)
layout=json.loads((INPUT/'Game/data/spatial_layout.json').read_text());overlap=[]
for a in layout['regions']:
 if a.get('deck')!='D08':continue
 q=Polygon(a['boundary'],a.get('holes',[]));area=q.intersection(outer).area
 if area>1e-5:overlap.append({'id':a['id'],'area':area})
assert not overlap,overlap
assert river.is_valid and river.geom_type=='Polygon' and len(river.interiors)==1
assert island.covers(unary_union(spa));assert all(river.intersection(q).area<1e-6 for q in runouts)
for a in ramps:
 dx=a['b'][0]-a['a'][0];dz=a['b'][2]-a['a'][2];rise=abs(a['b'][1]-a['a'][1]);assert abs(math.hypot(dx,dz)/rise-12)<1e-5
for i in range(2):
 # Major projected slide separation; own helix turn uses real4m vertical separation.
 if i==0:assert LineString([(q[0],q[2]) for q in slides[0]['trajectory_xyz']]).distance(LineString([(q[0],q[2]) for q in slides[1]['trajectory_xyz']]))>1.54
(P/'docs/AQUATIC_CONSTRUCTION_PLAN.json').write_text(json.dumps(plan,indent=2))
(P/'qa/plan_fit.json').write_text(json.dumps({'passed':True,'loop_closed':True,'loop_length_m':loop.length,'one_island':True,'six_thermal_targets_accounted':True,'new_directory_programmes':0,'D08_region_area_conflicts':overlap,'annex_min_plan_hull_clearance_m':outer.distance(hull.boundary),'ramps_all_1_to_12':True,'host_shared_files_modified':False,'scope':'Coarse plan and datum/source fit. Does not prove consolidated branch annex availability, pressure hull loads, routes, bodies, collision or ride operation.'},indent=2))
print('Plan passes: %.2fm closed river, two helices, six thermal targets, zero existing D08 floor area overlap.'%loop.length)
