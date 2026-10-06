from pathlib import Path
import json,sys,hashlib,numpy as np
from shapely.geometry import Polygon,box
sys.path.insert(0,'/workspace/scratch/375c2e438292/engineering-dense-bays/qa');from geometry_review import Query
R=Path(__file__).resolve().parent;path=R/'BRIDGE_GEOMETRY_002.json';d=json.loads(path.read_text());meshes=[]
for o in d['objects']:
 v=np.array(o['vertices_world']);tri=np.array([[v[f[0]],v[f[i]],v[f[i+1]]]for f in o['faces']for i in range(1,len(f)-1)]);meshes.append({'triangles':tri,'node':o['name'],'primitive':0})
q=Query(meshes);hits=q.prism_hits([-34,69.5001,-128.6,-4,72.5,-123.4]);assert not hits,hits[:10]
footprints=[]
for o in d['objects']:
 if o['role']not in ['arrival_pier','guard_post']:continue
 v=np.array(o['vertices_world']);lo=v.min(0);hi=v.max(0);foot=Polygon(v[abs(v[:,1]-69.5)<1e-6][:,[0,2]]).convex_hull;assert box(-34,-129.05,-4,-122.95).covers(foot);footprints.append({'part':o['name'],'bearing_area_m2':foot.area,'top_floor_y':69.5})
report={'passed_source_route_and_floor_support':True,'geometry_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'source_parts':len(d['objects']),'triangles':sum(len(m['triangles'])for m in meshes),'headroom_volume_hits':hits,'pier_post_floor_bearings':footprints,'minimum_required_clear_headroom_m':3,'existing_receiver_proof':'BRIDGE_TERMINAL_CONTACT_SCREEN.json','unscreened_current_world_lower_band_y':[68.55,69.20],'lower_band_gate':'Reconcile this below-floor beam band against current world before installation; first terminal census covered Y69.20 and above. No walking-volume uncertainty hidden.','no_engine_or_shared_changes':True};out=R/'GEOMETRY_SCREEN.json';assert not out.exists();out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items()if k!='pier_post_floor_bearings'}))
