"""Pure geometry source authoring. No engine or shared writes."""
from pathlib import Path
import json,hashlib,math,sys
from shapely.geometry import Polygon,box,LineString,Point
from shapely.ops import unary_union
R=Path(__file__).resolve().parents[1];C=R.parents[1];G=C.parent/'astraea-godot-production-20261003'
P=G/'data/architecture/packages/crew_living'
review=json.loads((P/'CONNECTOR_AND_DETOUR_REVIEW.json').read_text());plan=json.loads((P/'SECTION_DISTRIBUTION_PROPOSAL.json').read_text());planning=json.loads((P/'PLANNING_CHECKS.json').read_text())
assert not any(a['catalogue_id']=='AST-STF-010' for a in json.loads((C/'catalogue_manifest.json').read_text())['assets'])
def polygons(g):
 return [{'boundary':list(p.exterior.coords)[:-1],'holes':[list(h.coords)[:-1] for h in p.interiors]} for p in ([g] if g.geom_type=='Polygon' else g.geoms) if not p.is_empty]
def frompoly(r):return Polygon(r['boundary'],r.get('holes',[]))
base=unary_union([frompoly(p) for p in review['staff_route_union_polygons']])
old=json.loads((C/'assets/lower_staff_network/source/section_contract.json').read_text());oldroute=unary_union([Polygon(p) for p in old['decks'][2]['floor_union_polygons_xz']])
# Existing threshold branches/home are deliberately not reauthored.
branches=[];gates=[];turns=[]
for side in [-1,1]:
 for z in [-344,-40,40,344]:
  x=side*86;turns.append([x,z]);base=base.union(box(x-2.5,z-2.5,x+2.5,z+2.5))
for pts in review['staff_route_centrelines']:
 turns.extend(pts[1:-1])
def branch(key,pts,terminal=True):
 l=LineString(pts);shape=l.buffer(1.8,cap_style=2,join_style=2)
 if terminal:
  x,z=pts[-1];bay=box(x-2.5,z-2.5,x+2.5,z+2.5);shape=shape.union(bay);turns.append([x,z])
 branches.append((key,shape,pts));return shape
branch('breakroom_receiving',[(57,-420),(52.7,-420)])
branch('dining_receiving',[(57,-216),(52.7,-216)])
branch('training_vestibule',[(-103,0),(-98,0),(-56,0)])
branch('administration_vestibule',[(103,0),(98,0),(56,0)])
branch('recreation_receiving',[(-57,216),(-52.7,216),(-52.7,215)])
branch('briefing_receiving',[(57,216),(52.7,216)])
branch('care_screened_receiving',[(-57,422),(-54,422),(-12,422)],False)
branch('lockers_receiving',[(57,427),(54,427),(14,427)],False)
home=unary_union([frompoly(p) for p in review['home_connector_union_polygons']]);all_clear=unary_union([base,home]+[b[1] for b in branches]);new=all_clear.difference(oldroute)
# Apertures are reserved openings; existing family door/controller integration belongs to parent.
for a in review['proposed_owned_aperture_centres']:
 gates.append(dict(a,clear_width_m=3.6,clear_height_m=2.65,owner='parent existing-family door integration',controller_created=False))
# Explicit open seams: portal rectangles extend beyond boundary, avoiding accidental cross-walls.
openings=[box(-59,-216.01,-55,-214.19),box(-48.01,-433.8,-47.99,-430.2)]
# Receiving ports from branches to children; geometry ends honestly at these interfaces.
ports=[('breakroom',50.2,-420),('dining',50.2,-216),('recreation',-50.2,215),('briefing',50.2,216),('training',-54,0),('administration',54,0),('care',-12,422),('lockers',14,427),('home_quiet_lobby',-41,-423)]
for key,x,z in ports:
 openings.append(box(x-.02,z-1.8,x+.02,z+1.8) if key!='home_quiet_lobby' else box(x-1.8,z-.02,x+1.8,z+.02))
# Gate pockets stay outside clear polygons; all named dynamic hardware remains reserved.
parts=[]
def add(name,bounds,role,kind='static_architecture'):
 assert all(bounds[i+1]>bounds[i] for i in [0,2,4]);parts.append(dict(name=name,world_aabb=bounds,role=role,kind=kind,catalogue_id='AST-STF-010'))
# Extract exact orthogonal boundary, with outside-only shells preserving TRUE 3.6 m clear.
open_union=unary_union(openings)
for pi,p in enumerate([new] if new.geom_type=='Polygon' else new.geoms):
 for ri,ring in enumerate([p.exterior]+list(p.interiors)):
  pts=list(ring.coords)
  for ei,(a,b) in enumerate(zip(pts,pts[1:])):
   edge=LineString([a,b]);segs=edge.difference(open_union)
   for si,s in enumerate([segs] if segs.geom_type=='LineString' else getattr(segs,'geoms',[])):
    if s.length<.001:continue
    aa,bb=list(s.coords)[0],list(s.coords)[-1];mx,mz=s.interpolate(.5,normalized=True).coords[0]
    vertical=abs(aa[0]-bb[0])<1e-8;axis=0 if vertical else 1
    # Sample either side rather than depend on ring orientation.
    sample=Point(mx+(.01 if vertical else 0),mz+(0 if vertical else .01));sign=-1 if all_clear.covers(sample) else 1
    plane=mx if vertical else mz;lo,hi=sorted([aa[1],bb[1]] if vertical else [aa[0],bb[0]])
    cuts=[lo]+[v for v in range(math.ceil(lo/4)*4,math.floor(hi/4)*4+1,4) if lo<v<hi]+[hi]
    for ci,(u,v) in enumerate(zip(cuts,cuts[1:])):
     def slab(y0,y1,t0,t1,role,label):
      t0,t1=sorted([plane+sign*t0,plane+sign*t1]);add(f'CRW_Wall_{pi}_{ri}_{ei}_{si}_{ci}_{label}',[t0,t1,y0,y1,u,v] if vertical else [u,v,y0,y1,t0,t1],role)
     slab(12,13.03,.03,.18,'staff_bluegrey_paint','LowerPanel');slab(13.03,15.2,.03,.18,'staff_white_paint','Enamel')
     slab(12.72,12.86,0,.03,'staff_rubber','Bumper');slab(15.02,15.16,0,.03,'staff_zinc','ServiceRecessLip')
# Disjoint rectangular ceiling cells, exact union. No walkable floor goes into asset.
cap_region=new.buffer(.18,join_style=2).difference(oldroute)
xs=sorted({q[0] for r in polygons(cap_region) for q in r['boundary']});zs=sorted({q[1] for r in polygons(cap_region) for q in r['boundary']})
for xi,(a,b) in enumerate(zip(xs,xs[1:])):
 for zi,(c,d) in enumerate(zip(zs,zs[1:])):
  if cap_region.covers(Point((a+b)/2,(c+d)/2)):add(f'CRW_Cap_{xi}_{zi}',[a,b,15.2,15.34,c,d],'staff_bluegrey_paint','ceiling_cap')
# Source-supported fixtures: metal hanger reaches cap, light bottom at 15.015 (3.015 clear).
lights=[]
lines=review['staff_route_centrelines']+[b[2] for b in branches]
for li,pts in enumerate(lines):
 line=LineString(pts)
 for j in range(max(1,int(line.length/12))):
  pt=line.interpolate(min(line.length,(j+.5)*12));x,z=pt.coords[0]
  if not new.covers(box(x-.7,z-.15,x+.7,z+.15)):continue
  add(f'CRW_Task_{li}_{j}_Housing',[x-.7,x+.7,15.05,15.14,z-.15,z+.15],'staff_zinc','supported_light')
  add(f'CRW_Task_{li}_{j}_Opal',[x-.64,x+.64,15.015,15.055,z-.11,z+.11],'staff_opal','supported_light')
  for k,dx in enumerate([-.5,.5]):add(f'CRW_Task_{li}_{j}_Hanger{k}',[x+dx-.025,x+dx+.025,15.14,15.21,z-.04,z+.04],'staff_zinc','fixture_support')
  lights.append(dict(xyz=[x,15.03,z],catalogue_source='AST-STF-009 supported task fixture profile; AST-STF-006 role family',lowest_y=15.015))
compiler=all_clear.difference(unary_union([frompoly(r) for r in json.loads((G/'data/spatial_layout.json').read_text())['regions'] if r.get('deck')=='D03']))
D=dict(schema='astraea_crew_service_platform_v1',catalogue_id='AST-STF-010',family='crew_service_platform',coordinate_system='Godot world XYZ metres; Blender X,-Z,Y',floor_y=12,ceiling_underside_y=15.2,ceiling_top_y=15.34,source_clear_polygons=polygons(all_clear),new_architecture_clear_polygons=polygons(new),compiler_preview_floor_polygons=review['staff_new_compiler_floor_polygons'],branch_support_candidates_parent_review_required=polygons(compiler.difference(unary_union([frompoly(p) for p in review['staff_new_compiler_floor_polygons']]))),reviewed_compiler_floor_area_m2=10931.2,compiler_preview_only=True,floor_exported=False,framing_outside_clear_envelope=True,clear_route_width_m=3.6,turn_square_m=5,fixture_minimum_headroom_m=3.015,gate_clear_height_m=2.65,gate_reservations=gates,open_interface_ports=ports,turn_centres=turns,light_markers=lights,ownership={'floor':'parent compiler only','dynamic_doors':'parent existing door families','AST-STF-009':'untouched retained lower network','cabins':'not rebuilt; no new anchors/persons'},unbuilt_interfaces=['starboard real vertical arrival','D03 to D05 crew-care vertical transfer'],source_hashes={str(p.relative_to(G)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [P/'CONNECTOR_AND_DETOUR_REVIEW.json',P/'SECTION_DISTRIBUTION_PROPOSAL.json',P/'PLANNING_CHECKS.json']},reference_implementation=['segmented screened service distribution','deep receiving thresholds and opaque dogleg','supported overhead fixture housings','pale enamel / blue-grey low panels / zinc service recess / cart bumper'],acceptance='pure source geometry only; source Blender/export/live capsule/cart/visual untested')
(R/'source/section_contract.json').write_text(json.dumps(D,indent=2)+'\n');(R/'source/geometry_parts.json').write_text(json.dumps(parts,indent=2)+'\n')
# Proof against actual geometry, not a claimed gross corridor width.
wall_intrusions=[]
for p in parts:
 x0,x1,y0,y1,z0,z1=p['world_aabb']
 if y0<15 and box(x0,z0,x1,z1).intersection(all_clear).area>1e-7:wall_intrusions.append(p['name'])
checks=dict(parts=len(parts),wall_clear_intrusions=wall_intrusions,all_frames_outside_clear=not wall_intrusions,source_floor_parts=0,compiler_duplicate_floor_area_m2=compiler.intersection(unary_union([frompoly(r) for r in json.loads((G/'data/spatial_layout.json').read_text())['regions'] if r.get('deck')=='D03'])).area,compiler_new_floor_area_m2=compiler.area,minimum_fixture_headroom_m=3.015,cap_underside_headroom_m=3.2,turn_disk_clear=all(all_clear.covers(Point(x,z).buffer(2.2)) for x,z in turns),home_additional_floor_m2=home.difference(unary_union([frompoly(r) for r in json.loads((G/'data/spatial_layout.json').read_text())['regions'] if r.get('deck')=='D03'])).area,lower_network_files_mutated=False,engine_executed=False,source_export_verified=False,runtime_cart_verified=False)
protected_cells=unary_union([box(a['x'][0],a['z'][0],a['x'][1],a['z'][1]) for a in plan['subspaces'] if a['package_local_key']!='home_quiet_lobby']+[box(a['x'][0],a['z'][0],a['x'][1],a['z'][1]) for a in plan['bank_source_records']])
layout=json.loads((G/'data/spatial_layout.json').read_text())
protected_public=unary_union([frompoly(a) for a in layout['voids'] if 'D03' in a.get('decks',[])]+[frompoly(a) for a in layout['regions'] if a.get('deck')=='D03' and 'public_core' in a['id']])
hull=Polygon(next(a['inner'] for a in json.loads((G/'data/architecture/LOWER_HULL_BODY.json').read_text())['rings'] if a['y']==12))
checks['source_parts_protected_cell_intrusions']=[];checks['source_parts_public_void_intrusions']=[];checks['source_parts_outside_hull']=[]
for q in parts:
 x0,x1,y0,y1,z0,z1=q['world_aabb'];foot=box(x0,z0,x1,z1)
 if foot.intersection(protected_cells).area>1e-7:checks['source_parts_protected_cell_intrusions'].append(q['name'])
 if foot.intersection(protected_public).area>1e-7:checks['source_parts_public_void_intrusions'].append(q['name'])
 if not hull.covers(foot):checks['source_parts_outside_hull'].append(q['name'])
oldparts=json.loads((C/'assets/lower_staff_network/source/geometry_parts.json').read_text())['boxes']
from shapely.strtree import STRtree
tree=STRtree([box(p['world_aabb'][0],p['world_aabb'][4],p['world_aabb'][1],p['world_aabb'][5]) for p in oldparts]);existing_hits=[]
for q in parts:
 r=q['world_aabb']
 for i in tree.query(box(r[0],r[4],r[1],r[5])):
  o=oldparts[int(i)];s=o['world_aabb'];over=[min(r[k+1],s[k+1])-max(r[k],s[k]) for k in [0,2,4]]
  if min(over)>1e-7:existing_hits.append([q['name'],o['name']])
checks['actual_AST_STF_009_surface_overlaps']=existing_hits
checks['existing_surface_scope']='all retained AST-STF-009 source AABBs; other imported architecture and dynamic sweep require parent serial source/export survey'
assert not existing_hits
checks['reviewed_compiler_floor_area_m2']=10931.2
checks['additional_branch_support_candidate_area_m2']=compiler.area-10931.2
checks['branch_support_parent_review_required']=True
assert not checks['source_parts_protected_cell_intrusions'] and not checks['source_parts_public_void_intrusions'] and not checks['source_parts_outside_hull']
assert checks['all_frames_outside_clear'] and checks['turn_disk_clear'] and checks['compiler_duplicate_floor_area_m2']<1e-7
(R/'qa/PURE_GEOMETRY_CHECKS.json').write_text(json.dumps(checks,indent=2)+'\n');print(json.dumps(checks,indent=2))
