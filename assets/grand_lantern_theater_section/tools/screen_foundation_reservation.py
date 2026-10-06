"""Check the reviewed fixed foundations against proposed shell and retained slabs.
Package-only outputs, no engine, floor adoption or structural certification.
"""
import json,hashlib
from pathlib import Path
import numpy as np
from scipy.spatial import ConvexHull
from shapely.geometry import Polygon
from shapely.ops import unary_union
import shapely
R=Path(__file__).resolve().parents[1];G=Path('/workspace/shared/astraea-godot-production-20261003')
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
F=read(R/'contracts/D11_FOUNDATION_OWNERSHIP_PROPOSAL.json');H=read(R/'contracts/END_RETURN_MITER_RESERVATION.json');out=np.array(H['outer_vertices_world']);inside=np.array(H['inner_vertices_world']);bands=[]
for tri in H['triangles']:
 v=np.concatenate([out[tri],inside[tri]]);bands.append((v,ConvexHull(v)))
parts=[Polygon(p['boundary'],p['holes'])for p in F['polygons']];area=unary_union(parts);chunks=[]
for p in parts:
 for tri in shapely.constrained_delaunay_triangles(p).geoms:
  assert p.covers(tri)
  chunks.append(np.array([[x,y,z]for y in [F['datum_bottom_y'],F['datum_top_y']]for x,z in list(tri.exterior.coords)[:3]]))
contacts=[];resolved=[]
for i,q in enumerate(chunks):
 for j,(v,h)in enumerate(bands):
  if not np.all(q.max(0)>=v.min(0)-1e-9)or not np.all(v.max(0)>=q.min(0)-1e-9):continue
  planes=[float(min(q@eq[:3]+eq[3]))for eq in h.equations]
  if max(planes)>1e-8:resolved.append({'foundation_triangle':i,'reservation_facet':j,'separating_plane_margin_m':max(planes)})
  else:contacts.append({'foundation_triangle':i,'reservation_facet':j})
slabs=[];path=G/'data/generated/structural_meshes.json'
for r in read(path)['regions']:
 overlap_y=min(r['floor_y'],F['datum_top_y'])-max(r['floor_y']-r['thickness'],F['datum_bottom_y'])
 if overlap_y<=1e-8:continue
 p=unary_union([Polygon(t)for t in r['triangles']]);overlap=area.intersection(p).area
 if overlap>1e-8:slabs.append({'id':r['id'],'height_overlap_m':overlap_y,'plan_overlap_m2':overlap})
report={'status':'Reviewed fixed-foundation source reservation/slab check; not live adoption','foundation_sha256':sha(R/'contracts/D11_FOUNDATION_OWNERSHIP_PROPOSAL.json'),'shell_reservation_sha256':sha(R/'contracts/END_RETURN_MITER_RESERVATION.json'),'compiled_meshes_sha256':sha(path),'foundation_area_m2':area.area,'exact_foundation_prisms':len(chunks),'normal_miter_shell_contacts':contacts,'conservative_shell_candidates_resolved':resolved,'retained_compiled_slab_volume_overlaps':slabs,'walking_floor_or_cabin_added':False,'remaining':['Retained dynamic/procedural world census','Source/export normal-height review','Structural load/spans and pressure enclosure']}
(R/'qa/foundation_reservation_screen.json').write_text(json.dumps(report,indent=2)+'\n');assert not contacts and not slabs
print(json.dumps({'foundation_area_m2':area.area,'exact_prisms':len(chunks),'shell_contacts':len(contacts),'retained_slab_overlaps':len(slabs)}))
