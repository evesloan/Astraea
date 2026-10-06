from pathlib import Path
import json,math,numpy as np
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
R=Path(__file__).resolve().parent;P=Path('/workspace/shared/astraea-catalogue-continuation-20261002/assets/grand_lantern_theater_section');S=json.loads((P/'contracts/surface_manifest.json').read_text());G=json.loads((P/'source/geometry.json').read_text());A=json.loads((R/'COMPOSED_ARRIVAL_LIGHT_ARCHITECTURE_002.json').read_text());B=json.loads((R/'PLANTED_COURT_GEOMETRY_002.json').read_text());F=json.loads((R/'FIRST_PASS_ADDITIONS_PLAN.json').read_text());M=json.loads((R.parent/'RETAINED_MODULE_MEASUREMENTS.json').read_text());M.update(B['retained_asset_measurements']);old=[o for o in G['objects']if o['role']!='preview_only'];OV=[np.array(o['vertices_world'])for o in old];LO=np.array([v.min(0)for v in OV]);HI=np.array([v.max(0)for v in OV]);floors={69.5:unary_union([Polygon(p['boundary'],p['holes'])for p in json.loads((P/'contracts/D11_FLAT_FLOOR_CANDIDATE.json').read_text())['polygons']]),70.1:box(-94,-252,-58,-238)}
for y,deck in[(78,'D12'),(84,'D13')]:floors[y]=unary_union([Polygon(p['boundary_xz'])for s in S['surfaces']if s['deck']==deck for p in s['parts']if p.get('top_y')==y])
fail=[];support=[];intentional=[];items=[];taper_witnesses=[]
def clears_west_taper(v):
 slope=8.9/4.5;normal=math.hypot(1,slope);clear=[float(q[0]-(-117.65+slope*(q[1]-87)+.12*normal))for q in v]
 return min(clear)
for o in A['objects']+B['objects']:
 v=np.array(o['vertices_world']);lo=v.min(0);hi=v.max(0);poly=Polygon(v[:,[0,2]]).convex_hull
 for i in np.flatnonzero(np.all(np.minimum(HI,hi)-np.maximum(LO,lo)>3e-5,axis=1)):
  area=poly.intersection(Polygon(OV[i][:,[0,2]]).convex_hull).area
  if area<=1e-8:continue
  if old[i]['name']=='west_acoustic_tapered_return'and clears_west_taper(v)>3e-5:
   taper_witnesses.append({'object':o['name'],'affine_inner_plane_min_clearance_m':clears_west_taper(v)});continue
  if o.get('contact')==old[i]['name'] and '_stringer_'in old[i]['name']:intentional.append([o['name'],old[i]['name'],area])
  else:fail.append({'new':o['name'],'old':old[i]['name'],'bounds_candidate_area':area})
 for floor in[69.5,78,84]:
  if abs(lo[1]-floor)<3e-5:
   missing=poly.difference(floors[floor]).area;support.append({'id':o['name'],'floor':floor,'missing_m2':missing})
   if missing>1e-7:fail.append({'new':o['name'],'missing_floor_m2':missing})
   if hi[1]>floor+.20 and o['role']not in['plant_root_receiver','fixed_furnishing']:
    F['ground_modules'].append({'id':o['name'],'asset':'NEW_ARCHITECTURE','position_world':[float((lo[0]+hi[0])/2),floor,float((lo[2]+hi[2])/2)],'yaw_radians':0,'conservative_footprint_xz':[list(x)for x in poly.exterior.coords[:-1]],'bounds_y':[float(lo[1]),float(hi[1])]})
for row in B['plant_instances']:
 bounds=M[row['asset']]['bounds_gltf'];x,y,z=row['position_world'];a=row['yaw_radians'];c,s=math.cos(a),math.sin(a);pts=np.array([[x+u*c+w*s,y+h,z-u*s+w*c]for u in[bounds['min'][0],bounds['max'][0]]for h in[bounds['min'][1],bounds['max'][1]]for w in[bounds['min'][2],bounds['max'][2]]]);lo=pts.min(0);hi=pts.max(0);poly=Polygon(pts[:,[0,2]]).convex_hull
 for i in np.flatnonzero(np.all(np.minimum(HI,hi)-np.maximum(LO,lo)>3e-5,axis=1)):
  if old[i]['name']=='west_acoustic_tapered_return'and clears_west_taper(pts)>3e-5:
   taper_witnesses.append({'object':row['id'],'affine_inner_plane_min_clearance_m':clears_west_taper(pts)});continue
  if poly.intersection(Polygon(OV[i][:,[0,2]]).convex_hull).area>1e-7:fail.append({'plant':row['id'],'old':old[i]['name']})
for row in F['ground_modules']:
 x,y,z=row['position_world'];poly=Polygon(row['conservative_footprint_xz'])
 if y not in floors:continue
 missing=poly.difference(floors[y]).area
 if missing>1e-7:fail.append({'furniture':row['id'],'missing_floor':missing})
 if 'backstage'in row['id']or'rehearsal'in row['id']or'D11_stage_'in row['id']or'dressing'in row['id']:continue
 for name,p in [('rear_crossroute',box(-113.6,-120.7,-44.6,-117.3)),('shaft_stair_bypass',box(-49.6,-148.7,-44.6,-116.5)),('west_stair_approach',box(-64.5,-153,-60.5,-122))]:
  area=poly.intersection(p).area
  if area>1e-7:fail.append({'object':row['id'],'protected_route':name,'area':area})
(R/'FIRST_PASS_ADDITIONS_PLAN_WITH_ARCHITECTURE.json').write_text(json.dumps(F,indent=2)+'\n');out={'status':'Conservative pure architecture/furniture/plant retained-source and floor/route screen; exact new-source internal contacts still to verify','failures':fail,'floor_bearing_witnesses':support,'intentional_stringer_contacts':intentional,'actual_taper_plane_separation_witnesses':taper_witnesses,'new_architectural_meshes':len(A['objects'])+len(B['objects'])};(R/'ARCHITECTURE_ROUTE_SCREEN.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'failures':fail,'ground_bearings':len(support)},indent=2))
