from pathlib import Path
import json,math
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
R=Path(__file__).resolve().parent;P=Path('/workspace/shared/astraea-catalogue-continuation-20261002/assets/grand_lantern_theater_section');D=json.loads((R/'FIRST_PASS_ADDITIONS_PLAN.json').read_text());S=json.loads((P/'contracts/surface_manifest.json').read_text());floors={69.5:unary_union([Polygon(p['boundary'],p['holes'])for p in json.loads((P/'contracts/D11_FLAT_FLOOR_CANDIDATE.json').read_text())['polygons']]),70.1:box(-94,-252,-58,-238)}
for y,deck in [(78,'D12'),(84,'D13')]:floors[y]=unary_union([Polygon(p['boundary_xz'])for s in S['surfaces']if s['deck']==deck for p in s['parts']if p.get('top_y')==y])
rects={'AST-CUL-002':[('public_low_writing',[-.9,.55,.9,1.45]),('rear_staff',[-.9,-1.35,.9,-.55])],'AST-CUL-001':[('programme_view',[-.8,.45,.8,1.35]),('rear_cassette',[-.6,-1.26,.6,-.36])],'AST-FUR-001':[('seat_front',[-1.2,.47,1.2,1.16])],'AST-FUR-002':[('seat_front',[-.47,.47,.47,1.16])],'AST-STF-007':[('front_work_retrieval',[-.9,.45,.9,1.4])],'AST-CRW-003':[('front_storage',[-.5,.4,.5,1.2])],'AST-LND-004':[('inspection_front',[-.8,.12,.8,1.15])],'AST-CUL-004':[('cue_operator',[-.55,.5,.55,1.3])]}
results=[];bad=[]
for item in D['ground_modules']:
 x,y,z=item['position_world'];a=item['yaw_radians'];c,s=math.cos(a),math.sin(a)
 for name,r in rects.get(item['asset'],[]):
  p=Polygon([(x+u*c+v*s,z-u*s+v*c)for u,v in [(r[0],r[1]),(r[2],r[1]),(r[2],r[3]),(r[0],r[3])]]);missing=p.difference(floors[y]).area;contacts=[]
  for other in D['ground_modules']:
   if other['id']==item['id']or abs(other['position_world'][1]-y)>1e-7:continue
   a=p.intersection(Polygon(other['conservative_footprint_xz'])).area
   if a>1e-7:contacts.append({'module':other['id'],'positive_overlap_m2':a})
  row={'module':item['id'],'stance':name,'missing_floor_area_m2':missing,'other_module_contacts':contacts,'polygon_xz':[list(v)for v in list(p.exterior.coords)[:-1]]};results.append(row)
  if missing>1e-7 or contacts:bad.append(row)
report={'status':'Conservative source-plan stance check, not anatomy or moving door/drawer sweep','stance_count':len(results),'failures':bad,'witnesses':results,'not_checked':['Complete source cabinet leaf/drawer sweep','All supported species','Actual physical operator/cart movement']};(R/'FURNITURE_STANCE_SCREEN.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'stances':len(results),'failures':bad},indent=2))
