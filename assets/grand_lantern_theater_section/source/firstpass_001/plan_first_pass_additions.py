"""Pure additive first-pass placement proposal. No Blender/Godot/shared writes."""
from pathlib import Path
import json,math,hashlib,itertools,collections
import numpy as np
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
R=Path(__file__).resolve().parent;P=Path('/workspace/shared/astraea-catalogue-continuation-20261002/assets/grand_lantern_theater_section');M=json.loads((R/'RETAINED_MODULE_MEASUREMENTS.json').read_text());G=json.loads((P/'source/geometry.json').read_text());S=json.loads((P/'contracts/surface_manifest.json').read_text());routes=json.loads((P/'contracts/route_reservations.json').read_text())['routes'];proposed=[]
def add(id,asset,x,y,z,yaw=0,zone='foyer',purpose=''):
 proposed.append({'id':id,'asset':asset,'position_world':[x,y,z],'yaw_radians':yaw,'scale':[1,1,1],'zone':zone,'purpose':purpose})
# Distinct foyer compositions; all informal waiting seats remain separate from2200audience places.
layouts={69.5:{'D':'D11','counter':[(-69,-133),(-73,-133)],'program':[(-65.5,-131),(-77,-131)],'bench':[(-103,-136,0),(-98,-130,math.pi),(-91,-137,0),(-86,-129,math.pi)],'chair':[],'table':[(-103,-134.4),(-98,-131.6),(-91,-135.4),(-86,-130.6)]},78:{'D':'D12','counter':[(-67,-136)],'program':[(-65.25,-134),(-110,-125)],'bench':[(-100,-128,math.pi),(-90,-141,0)],'chair':[(-97,-134,math.pi/2),(-93,-134,-math.pi/2),(-79,-132,0),(-77,-132,0)],'table':[(-100,-129.6),(-90,-139.4),(-95,-134),(-78,-130.7)]},84:{'D':'D13','counter':[(-67,-132)],'program':[(-65.25,-130),(-109,-125)],'bench':[(-102,-138,0),(-87,-136,0)],'chair':[(-98,-129,math.pi),(-96,-129,math.pi),(-79,-129,math.pi),(-77,-129,math.pi)],'table':[(-102,-136.4),(-87,-134.4),(-97,-130.5),(-78,-130.5)]}}
for y,l in layouts.items():
 D=l['D']
 for i,(x,z)in enumerate(l['counter']):add(f'{D}_usher_{i}','AST-CUL-002',x,y,z,purpose='Usher/programme work with low writing wing; real staff rear stance reserved')
 for i,(x,z)in enumerate(l['program']):add(f'{D}_programme_{i}','AST-CUL-001',x,y,z,purpose='Original programme/wayfinding cassette; no invented performance/time')
 for i,(x,z,a)in enumerate(l['bench']):add(f'{D}_waiting_bench_{i}','AST-FUR-001',x,y,z,a,purpose='Informal waiting, not an additional audience-capacity anchor')
 for i,(x,z,a)in enumerate(l['chair']):add(f'{D}_waiting_chair_{i}','AST-FUR-002',x,y,z,a,purpose='Intermission pause, not an additional audience-capacity anchor')
 for i,(x,z)in enumerate(l['table']):add(f'{D}_waiting_table_{i}','AST-FUR-003',x,y,z,purpose='Reachable supported shared surface beside, not inside, seat approach')
# Backstage bays: practical work/storage, screened dressing, rehearsal support, scenery/props.
for i,(asset,x,z)in enumerate([('AST-STF-007',-105,-261.4),('AST-STF-007',-99.4,-261.4),('AST-LND-004',-113.5,-261.3),('AST-CRW-003',-93,-261.3),('AST-CRW-003',-78.5,-261.3),('AST-STF-007',-85.5,-261.4),('AST-FUR-002',-90,-260.1),('AST-FUR-002',-81,-260.1),('AST-FUR-001',-67.5,-261.4),('AST-CUL-004',-73,-261.5),('AST-STF-007',-60.5,-261.4),('AST-LND-004',-51,-261.3),('AST-LND-004',-42,-261.3),('AST-STF-007',-46.5,-261.4),('AST-CRW-003',-37.5,-261.4)]):add(f'D11_backstage_{i:02}',asset,x,69.5,z,zone='backstage',purpose='Fixed supported backstage furnishing; active doors/drawers remain source-sweep checks')
for i,x in enumerate([-87.68,-82.68]):add(f'D11_dressing_privacy_{i}','AST-CRW-002',x,69.5,-260.35,zone='backstage',purpose='Original self-supported privacy track/curtain; no whole-source scaling')
for side,xs in [('port',[-109,-102]),('starboard',[-49.5,-44])]:
 for j,x in enumerate(xs):
  add(f'D11_{side}_rehearsal_chair_{j}','AST-FUR-002',x,69.5,-238,zone='orchestra_support',purpose='Staff rehearsal/support use only')
  add(f'D11_{side}_rehearsal_cue_{j}','AST-CUL-004',x+1.2,69.5,-236.6,math.pi,zone='orchestra_support',purpose='Shielded notes/task-light stand, no active show protocol')
add('D11_stage_cue','AST-CUL-004',-60,70.1,-250,zone='stage',purpose='Original seventh mount: all four retained soles on actual stage top; actual hood/aperture and task light')

floor={69.5:unary_union([Polygon(p['boundary'],p['holes'])for p in json.loads((P/'contracts/D11_FLAT_FLOOR_CANDIDATE.json').read_text())['polygons']])}
for y,deck in [(78,'D12'),(84,'D13')]:floor[y]=unary_union([Polygon(p['boundary_xz'])for s in S['surfaces']if s['deck']==deck for p in s['parts']if p.get('top_y')==y])
floor[70.1]=box(-94,-252,-58,-238)
old=[]
for o in G['objects']:
 if o['role']=='preview_only':continue
 v=np.array(o['vertices_world']);old.append((o['name'],v.min(0),v.max(0),Polygon(v[:,[0,2]]).convex_hull))
checks=[];fail=[];new_shapes=[]
for p in proposed:
 m=M[p['asset']];lo,hi=m['bounds_gltf']['min'],m['bounds_gltf']['max'];x,y,z=p['position_world'];a=p['yaw_radians'];c,s=math.cos(a),math.sin(a)
 poly=Polygon([(x+u*c+w*s,z-u*s+w*c)for u,w in [(lo[0],lo[2]),(hi[0],lo[2]),(hi[0],hi[2]),(lo[0],hi[2])]]);yb=[y+lo[1],y+hi[1]];missing=poly.difference(floor[y]).area;contacts=[]
 for name,blo,bhi,q in old:
  if min(yb[1],bhi[1])-max(yb[0],blo[1])<=.00003:continue
  if poly.intersection(q).area>1e-7:contacts.append(name)
 route_hits=[]
 for q in routes:
  tier={'stalls':69.5,'first_gallery':78,'crown_gallery':84}[q['tier']]
  if abs(tier-y)>.001:continue
  if poly.intersection(Polygon(q['boundary'])).area>1e-7:route_hits.append(q['id'])
 # New protected foyer approach graph, separate from old source cart routes.
 if p['zone']=='foyer':
  for key,q in [('rear_crossroute',box(-113.6,-120.7,-44.6,-117.3)),('shaft_stair_bypass',box(-49.6,-148.7,-44.6,-116.5)),('west_stair_approach',box(-64.5,-153,-60.5,-122))]:
   if poly.intersection(q).area>1e-7:route_hits.append(key)
 row={'id':p['id'],'full_bounds_floor_missing_m2':missing,'retained_structure_candidates':contacts,'protected_route_contacts':route_hits}
 checks.append(row);new_shapes.append((p,poly,yb))
 if missing>1e-7 or contacts or route_hits:fail.append(row)
 # Preserve precise transformed boxes for future actual-source mesh/contact checks.
 p['conservative_footprint_xz']=[list(v)for v in list(poly.exterior.coords)[:-1]];p['bounds_y']=yb
pair=[]
for i,(a,p,ay)in enumerate(new_shapes):
 for b,q,by in new_shapes[i+1:]:
  if min(ay[1],by[1])-max(ay[0],by[0])<=.00003:continue
  area=p.intersection(q).area
  if area>1e-7:pair.append({'a':a['id'],'b':b['id'],'positive_bounds_overlap_m2':area})
# Actual six retained mounts, complete original LGT001 geometry and outside-lens emitters.
lights=[]
base=json.loads((P/'contracts/fixture_markers.json').read_text())['fixtures']
for f in base[:-1]:
 x,y,z=f['position_world'];port=x<-76;back=-104.25 if port else-47.75;yaw=math.pi/2 if port else-math.pi/2
 lights.append({'id':f['id'],'asset':'AST-LGT-001','origin_world':[back,y-.45,z],'yaw_radians':yaw,'existing_mount':f['position_world'],'real_backplate_overlap_m':.015,'emitter_world':[back+(.31 if port else-.31),y,z],'emitter_basis':'Actual DATUM_light_exit;20mm beyond lens and10mm beyond complete fixture envelope','preview_light':'Practical only, no ambient/fill; warm light; receiver rays and normal-eye review required'})
lights.append({'id':'stage_cue_worklight','asset':'AST-CUL-004','origin_world':[-60,70.1,-250],'yaw_radians':0,'emitter_world':[-60,71.647,-250.015],'emitter_basis':'3mm outward along actual downward diffuser normal; saved source aperture at1.55m above base','direction_world':[0,-1,0],'receiver_world':[-60,71.062,-250.015],'preserved_physical_notes_and_four_soles':True})
# The upper-gallery ceiling fixtures have exact existing source surface support.
soffits=[]
for deck in ['D12','D13']:
 f=next(s for s in S['surfaces']if s['region_id']==deck+'_theater_gallery_seating')
 for radius in [26.5,35.5,43]:
  for angle in [-40,-15,15,40]:
   x=-76+radius*math.sin(math.radians(angle));z=-238+radius*math.cos(math.radians(angle));cover=[(name,p)for name,p in zip(f['objects'],f['parts'])if Polygon(p['boundary_xz']).covers(Polygon([(x-.20,z-.20),(x+.20,z-.20),(x+.20,z+.20),(x-.20,z+.20)]))]
   if not cover:
    cover=[(name,p)for name,p in zip(f['objects'],f['parts'])if Polygon(p['boundary_xz']).covers(__import__('shapely').Point(x,z))]
   assert cover;name,p=cover[0]
   theta=math.radians(angle);radial=np.array([math.sin(theta),math.cos(theta)]);tangent=np.array([math.cos(theta),-math.sin(theta)]);centre=np.array([x,z]);plate=Polygon([(centre+tangent*u+radial*v).tolist()for u,v in [(-.205,-.445),(.205,-.445),(.205,.445),(-.205,.445)]])
   coplanar=unary_union([Polygon(q['boundary_xz'])for q in f['parts']if abs(q['top_y']-p['top_y'])<1e-8]);missing=plate.difference(coplanar).area;assert missing<1e-8,('Unsupported soffit plate',deck,radius,angle,missing)
   soffits.append({'id':f'{deck}_soffit_r{radius}_a{angle}','source_family':'AST-LGT-001 ceiling-oriented derivative','backplate_support_world':[x,p['top_y']-.45,z],'source_support_object':name,'orientation':'Retained wall normal mapped downward; long plate axis radial; complete0.89x0.41m envelope is on the union of actual coplanar facets','full_backplate_missing_support_area_m2':missing,'backplate_polygon_xz':[list(v)for v in list(plate.exterior.coords)[:-1]],'emitter_world':[x,p['top_y']-.45-.31,z],'world_aim':[0,-1,0]})
plan={'status':'Pure additive placement proposal; parent review before explicit new source derivative','saved_base_sha256':'c91193af1e4a14aac3a4e75c743e7c86b6a57a669981e9a7e7cfb0412e1cb5f5','proposed_new_source_filename':'AST-CUL-005_firstpass_001.blend','protected_architecture_and_2200chairs':'Unchanged; no base overwrite, runtime/registry/compiler changes','ground_modules':proposed,'seven_original_fixture_completions':lights,'source_surface_backed_soffit_positions':soffits,'stage_access_no_furniture_reservation':{'ramp':[-55,-246,-51,-238.8],'low_landing':[-55,-238.8,-51,-237],'high_landing':[-58,-249.4,-51,-246]},'informal_waiting_capacity':'Not part of2200audience places; no ticket/occupancy/berth registry update','input_module_measurements':'RETAINED_MODULE_MEASUREMENTS.json','source_geometry_sha256':hashlib.sha256((P/'source/geometry.json').read_bytes()).hexdigest()}
(R/'FIRST_PASS_ADDITIONS_PLAN.json').write_text(json.dumps(plan,indent=2)+'\n');report={'ground_module_count':len(proposed),'per_asset_counts':dict(collections.Counter(p['asset']for p in proposed)),'full_bounds_floor_support_checks':checks,'retained_structure_or_route_failures':fail,'proposed_module_pair_contacts':pair,'seven_real_fixtures':len(lights),'soffit_fixture_targets':len(soffits),'limitations':['Conservative transformed full-model bounds, not exact mesh/drawer/seat approach acceptance','All24soffit plates have full conservative coplanar bearing; actual mesh contacts/source normals still to verify','No engine/source build or lighting/render acceptance']};(R/'PLACEMENT_SCREEN.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items()if k!='full_bounds_floor_support_checks'},indent=2))
