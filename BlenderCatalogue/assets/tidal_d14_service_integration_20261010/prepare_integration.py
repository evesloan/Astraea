from pathlib import Path
import json,hashlib,sys
sys.path.insert(0,'/workspace/shared/astraea_python_deps')
import shapely
from shapely.geometry import Polygon
from shapely.ops import unary_union
W=Path(__file__).resolve().parent;S=Path('/tmp/astraea_tidal_d14_receiver_20261010');R=Path('/workspace/shared/Astraea_direct_recovery_20261008_hcozu5z4');G=R/'Game';F=R/'BlenderCatalogue/assets/group3_crew_service_20261009';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();P=json.load(open(S/'D14_SHARED_RECEIVER_PLAN.json'));frozen=json.load(open(S/'FROZEN_D14_SHARED_RECEIVER_BATCH.json'))
for f,d in frozen['files'].items():assert sha(S/f)==d['sha256']and(S/f).stat().st_size==d['bytes']
for f,h in P['source_pins'].items():assert sha(R/f)==h,f
a=json.load(open(F/'source/TIDAL_STAFF_INTERFACE.json'));parts=[p for p in a['parts']if'D14'in p['name']and p['category']not in['upper_shaft','landing_threshold']];assert len(parts)==64
id='AST-RES-TIDAL-D14-CORRIDOR-001'
def unused(v):
 if isinstance(v,dict):
  for x in v.values():unused(x)
 elif isinstance(v,list):
  for x in v:unused(x)
 elif isinstance(v,str):assert v!=id,'ID collision'
unused(json.load(open(R/'BlenderCatalogue/catalogue_manifest.json')))
closures=[{'name':'D14_UnfinishedShaftPhysicalClosure','aabb':[-23.18,-23.02,88.5,91.84,-492.2,-487.8],'role':'staff_bluegrey_paint','category':'unfinished_shaft_closed'},{'name':'D14_AbandonedCleanWestMouthPhysicalClosure','aabb':[-62.94,-62.8,88.5,91.3,-494.8,-491.2],'role':'staff_bluegrey_paint','category':'abandoned_mouth_closed'},{'name':'D14_AbandonedReturnsWestMouthPhysicalClosure','aabb':[-62.94,-62.8,88.5,91.3,-488.8,-485.2],'role':'staff_bluegrey_paint','category':'abandoned_mouth_closed'}]
fp=next(x for x in a['floor_proposals']if x['deck']=='D14');regions=[]
for i,q in enumerate(fp['polygons']):
 poly=Polygon(q['boundary'],q['holes']);regions.append({'id':'TIDAL_D14_ServiceApproach_'+str(i),'deck':'D14','floor_y':88.5,'thickness':.24,'material_role':'staff_floor','rings':[list(poly.exterior.coords)[:-1]]+[list(h.coords)[:-1]for h in poly.interiors],'triangles':[list(t.exterior.coords)[:3]for t in shapely.constrained_delaunay_triangles(poly).geoms],'area_m2':poly.area})
assert json.load(open(S/'D14_ACTUAL_SOURCE_SURVEY.json'))['approach_existing_floor_overlap_m2']<1e-7
plan={'schema':'astraea.tidal.d14_corridor_integration.v1','catalogue_id':id,'retained_source_parts':parts,'closures':closures,'fixture_markers':[q for q in a['fixtures']if'D14'in q['name']],'batched_patch_targets':{'screen_wall_staff_bluegrey_paint_D14_-6_-63':['TidalStaffWallLow_D14_-6_-63_0','TidalStaffWallLow_D14_-6_-63_1'],'screen_wall_staff_white_paint_D14_-6_-63':['TidalStaffWallHigh_D14_-6_-63_0','TidalStaffWallHigh_D14_-6_-63_1']},'floor_regions':regions,'new_approach_floor_area_m2':sum(q['area_m2']for q in regions),'source_proposal_receipt_sha256':sha(S/'FROZEN_D14_SHARED_RECEIVER_BATCH.json'),'source_proposal_directory':str(S),'source_pins':P['source_pins'],'preserved_staff_lift_stops':[0,6,12,46.2,52.5],'no_upper_lift_activation':True,'original_adoption_sha256':sha(W/'predecessors/tidal_garden_adoption.gd')}
(W/'D14_CORRIDOR_INTEGRATION_PLAN.json').write_text(json.dumps(plan,indent=2)+'\n');print('D14_CORRIDOR_PLAN_PASS',len(parts),len(closures),len(plan['fixture_markers']),plan['new_approach_floor_area_m2'])
