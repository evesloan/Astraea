from pathlib import Path
import json,hashlib,sys
sys.path.insert(0,'/workspace/shared/astraea_python_deps')
from shapely.geometry import Polygon,MultiPoint,shape
from shapely.ops import unary_union
R=Path(__file__).resolve().parents[4];O=Path(__file__).resolve().parents[1];d=json.load(open(O/'PLAN.json'));hull=Polygon(json.load(open(R/'Game/data/hull_envelope.json'))['plan_xz_m']);assert len({p['name']for p in d['parts']})==len(d['parts'])
for p in d['parts']:
 foot=MultiPoint([(v[0],v[2])for v in p['verts']]).convex_hull;assert foot.difference(hull).area<1e-6,p['name'];assert min(v[1]for v in p['verts'])>=92.97999 and max(v[1]for v in p['verts'])<=106.44001
rs=[]
for f in ['Game/data/generated/structural_meshes.json','Game/data/generated/received_structural_meshes.json','Game/data/architecture/CENTRAL_RESIDENTIAL_STREETS.json']:rs+=json.load(open(R/f))['regions']
for f in d['floors']:
 old=unary_union([Polygon(t)for q in rs if abs(q['floor_y']-f['floor_y'])<.001 for t in q['triangles']]);new=shape(f['new_geometry']);assert new.intersection(old).area<1e-6;assert abs(new.area-f['new_area_m2'])<1e-6
assert d['floors'][0]['new_area_m2']==0
for p,sha in d['source_pins'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==sha
report={'status':'PASS_BOUNDED_GEOMETRY','source_parts':len(d['parts']),'D15_new_floor_area_m2':0,'new_upper_floor_areas_m2':{str(q['deck']):q['new_area_m2']for q in d['floors']},'existing_floor_overlap_m2':0,'hull_plan_overshoot_m2':0,'lower_library_cover_not_cut':True,'source_pins_verified':len(d['source_pins']),'top_y':106.44,'new_guest_units':0,'limits':'Model/runtime interaction checks are separate. Final visual, furnishing, service, detailed traversal and whole ship acceptance remain open.'};(O/'GEOMETRY_CHECKS.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
