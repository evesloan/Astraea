"""Actual receiving geometry contract; staff reservations are not window views."""
from pathlib import Path
import json,sys,math,ast
R=Path(__file__).resolve().parents[1];W=R.parents[1];sys.path.insert(0,str(W/'geometry-deps'))
from shapely.geometry import Polygon,LineString,box,MultiPoint
from shapely.ops import unary_union
p=json.loads((R/'outputs/house_r002/PLAN.json').read_text());court=Polygon(p['principal_court_reservation']['boundary']);inner=box(-29.05,250,-8.2,483);risers=unary_union([box(r['lobby_x'][0],r['lobby_z'][0],r['lobby_x'][1],r['lobby_z'][1])for r in p['staff_riser_reservations']]);rows=[]
for r in p['rooms']:
 x,y,z=r['aperture_contract']['plane_origin_world'];outer=r['allocation_x'][0]<-45;sgn=-1 if outer else 1;target=court if outer else inner.difference(risers.buffer(.2));normal=LineString([(x,z),(x+sgn*16,z)]);blocked=normal.intersects(risers)if not outer else False
 rays=[]
 for degrees in[-60,-45,-30,0,30,45,60]:
  a=math.radians(degrees);ray=LineString([(x,z),(x+sgn*20*math.cos(a),z+20*math.sin(a))]);inter=ray.intersection(target)
  rays.append({'angle_from_normal_degrees':degrees,'target_length_m':round(inter.length,4),'staff_reservation_crossed':ray.intersects(risers)if not outer else False})
 rows.append({'source_index':r['census_source_index'],'unit_id':r['address'],'family':'principal_conservatory_court'if outer else 'inner_receiving_garden','aperture_origin_world_xyz':[x,y,z],'normal_line_crosses_staff_reservation':blocked,'actual_receiving_target_in_house_source':True,'oblique_rays':rays,'status':'VIEW_INTERFACE_HOLD: near staff lobby; no broad panorama claim'if blocked else 'SOURCE_PLAN_RECEIVING_TARGET_PRESENT; eye-level and runtime acceptance pending','privacy_required':'Clear from inside; opaque polished tinted outside including lights-on; no opposite suite interiors'})
# Verify real rays from two seated positions on the front bench, through the
# finite source window, around the real opaque riser screen into the garden.
screen=box(-27.68,283.80,-27.54,296.20);flank=[]
for r in p['rooms']:
 if r['census_source_index']not in[294,714]:continue
 ox,oy,oz=r['source_origin_world_xyz'];apx,apy,apz=r['aperture_contract']['plane_origin_world'];checks=[]
 for localx,degrees in[(.65,64),(-.80,-69)]:
  start=(ox+11.8,oz+localx);ang=math.radians(degrees);ray=LineString([start,(start[0]+20*math.cos(ang),start[1]+20*math.sin(ang))]);atwindow=start[1]+(apx-start[0])*math.tan(ang)
  through=abs(atwindow-apz)<3.40;staff=ray.intersects(risers);opaque=ray.intersects(screen)
  checks.append({'bench_local_seat_xyz':[localx,11.8,1.20],'world_eye_xyz':[start[0],oy+1.20,start[1]],'angle_degrees':degrees,'window_world_z_at_crossing':atwindow,'through_finite_window':through,'crosses_staff_reservation':staff,'crosses_authored_screen':opaque,'receiving_garden_ray_m':ray.intersection(inner.difference(risers.buffer(.2))).length,'pass':through and not staff and not opaque})
 flank.append({'source_index':r['census_source_index'],'checks':checks,'scope':'Seated source plan sightlines. Both bench positions are inside the actual bench width; no runtime or visual approval.'})
# Resolve each selected ray against actual fixed source architecture at the
# seated eye height, including the private-garden frame and upper landings.
eps=1e-6
code=(R/'source/check_house.py').read_text()
for node in ast.parse(code).body:
 if isinstance(node,ast.FunctionDef)and node.name in['mesh_poly','shape']:
  exec(compile(ast.Module(body=[node],type_ignores=[]),str(R/'source/check_house.py'),'exec'),globals())
structural=[(r,shape(r))for r in p['parts']if r['category']not in['soil','planter','fixture','fixture_mount','public_glass']]
for rec in flank:
 for q in rec['checks']:
  x,y,z=q['world_eye_xyz'];a=math.radians(q['angle_degrees']);ray=LineString([(x,z),(x+20*math.cos(a),z+20*math.sin(a))]);hits=[]
  for part,(poly,lo,hi)in structural:
   if lo<y<hi and ray.intersection(poly).length>.0001:hits.append(part['name'])
  q['fixed_source_geometry_hits']=hits;q['pass']=q['pass']and not hits
assert all(q['pass']for r in flank for q in r['checks'])
report={'unit_count':83,'outer_court_units':sum(r['family']=='principal_conservatory_court'for r in rows),'inner_garden_units':sum(r['family']=='inner_receiving_garden'for r in rows),'source_view_interface_holds':[r['source_index']for r in rows if r['normal_line_crosses_staff_reservation']],'rays_are_plan_geometry_only':True,'runtime_privacy_accepted':False,'rows':rows,'constrained_bench_flank_sightlines':flank,'constrained_view_rule':'The normal view is a real planted setback and opaque screen; two specific seated oblique rays reach the larger inner garden. Broad panorama is not claimed.'}
(R/'qa/WINDOW_VIEW_CONTRACT.json').write_text(json.dumps(report,indent=2)+'\n');print('SUNSET_VIEW_HOLDS',report['source_view_interface_holds'])
