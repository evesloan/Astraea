"""Exact recorded-world edge contacts for the D11 proposed bridge, no Game writes."""
from pathlib import Path
import json,hashlib,sys,numpy as np
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
R=Path(__file__).resolve().parent;C=R/'bridge_census_run001/retained_world_census.json';D=json.loads(C.read_text());P=Path('/workspace/shared/astraea-catalogue-continuation-20261002/assets/grand_lantern_theater_section');sys.path.insert(0,'/workspace/scratch/375c2e438292/engineering-dense-bays/qa');from geometry_review import Query
assert not D['stale_or_missing_imports']and not D['unhandled_geometry'];assert len(D['render_triangle_candidates'])==len(D['collision_bound_candidates'])==1
render=D['render_triangle_candidates'][0];collision=D['collision_bound_candidates'][0];assert '/D11_fore_route/'in render['node']and'/D11_fore_route/'in collision['node'];a=np.array(render['exact_candidate_triangles_world']);b=np.array(collision['exact_candidate_triangles_world']);assert np.array_equal(a,b)and len(a)==6
q=Query([{'triangles':a,'node':render['node'],'primitive':0}]);floor=[-34,69.26,-129.05,-4,69.5,-122.95];route=[-34,69.50002,-128.6,-4,72.5,-123.4];assert not q.prism_hits(floor,tolerance=1e-7);assert not q.prism_hits(route,tolerance=1e-7)
vertical=[t for t in a if np.max(abs(t[:,0]+4))<1e-7];face=unary_union([Polygon(t[:,[2,1]])for t in vertical]);assert face.is_valid
pads=[]
for ident,z in [('fore',-128.8),('aft',-123.2)]:
 rectangle=box(z-.15,69.28,z+.15,69.48);assert face.covers(rectangle);pads.append({'end':'fore_spine','side':ident,'plane_x':-4,'contact_z':[z-.15,z+.15],'contact_y':[69.28,69.48],'covered_m2':rectangle.area})
foundation=json.loads((P/'contracts/D11_FOUNDATION_OWNERSHIP_PROPOSAL.json').read_text());shape=unary_union([Polygon(p['boundary'],p['holes'])for p in foundation['polygons']])
for ident,z in [('fore',-128.8),('aft',-123.2)]:
 # Existing approved-in-plan foundation is the receiving owner, not a pocket wall.
 inward=box(-34.01,z-.15,-34,z+.15);assert shape.covers(inward);pads.append({'end':'theater_approved_foundation','side':ident,'plane_x':-34,'contact_z':[z-.15,z+.15],'contact_y':[69.28,69.48],'inward_foundation_strip_depth_m':.01,'scope':'Foundation still requires compiler adoption; not claimed built by the census'})
report={'status':'Recorded retained-world exact terminal screen PASS; construction/import/traversal remain pending','census_sha256':hashlib.sha256(C.read_bytes()).hexdigest(),'render_collision_candidate_triangles_identical':True,'only_retained_candidate':render['node'],'strict_new_floor_positive_volume_hits':0,'clear_walk_volume_positive_area_hits':0,'retained_floor_top_y':69.5,'retained_floor_bottom_y':float(a[:,:,1].min()),'retained_floor_nominal_bottom_error_m':abs(float(a[:,:,1].min())-69.26),'terminal_contact_pads':pads,'foundation_sha256':hashlib.sha256((P/'contracts/D11_FOUNDATION_OWNERSHIP_PROPOSAL.json').read_bytes()).hexdigest(),'source_bridge_authoring_limits':{'floor_x':[-34,-4],'floor_z':[-129.05,-122.95],'floor_y':69.5,'clear_route_z':[-128.6,-123.4],'side_bearings_m':.45,'no_retained_guard_cut_needed_at_recorded_terminal':True},'not_claimed':['Foundation/live bridge already exists','Beam/connection load capacity','Runtime imported contact precision','Loaded species/cart and door operation']};o=R/'BRIDGE_TERMINAL_CONTACT_SCREEN.json';assert not o.exists();o.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
