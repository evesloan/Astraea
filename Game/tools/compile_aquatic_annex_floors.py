"""Adopt four exact aquatic annex slabs without editing retained floor owners."""
from pathlib import Path
import json,math,hashlib
import shapely
from shapely.geometry import Polygon,box
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
r=Path(__file__).resolve().parents[1]
p=json.load(open(r/'data/architecture/AQUATIC_ANNEX_PLAN.json'))
retained={};pins={}
for f in sorted(list((r/'data/generated').glob('*.json'))+list((r/'data/architecture').glob('*.json'))):
 if f.name=='AQUATIC_ANNEX_FLOORS.json':continue
 try:d=json.load(open(f))
 except (ValueError,UnicodeError):continue
 if not isinstance(d,dict):continue
 for a in d.get('regions',[]):
  if isinstance(a,dict) and all(k in a for k in ['id','triangles','floor_y','thickness']):
   retained[a['id']]=a;pins[str(f.relative_to(r))]=hashlib.sha256(f.read_bytes()).hexdigest()
old=[(a,unary_union([Polygon(t)for t in a['triangles']]))for a in retained.values()]
rows=[]
for a in p['floor_records']:
 if not a['owner'].startswith('compiler_'):continue
 assert a['id'] not in retained
 shape=unary_union([Polygon(q['boundary'],q.get('holes',[]))for q in a['boundary_polygons_xz']]);assert shape.is_valid
 y=a['top_y'];th=a['thickness_m']
 for b,prior in old:
  if shape.intersection(prior).area>1e-7:assert min(y,b['floor_y'])-max(y-th,b['floor_y']-b['thickness'])<1e-7,(a['id'],b['id'])
 triangles=a['triangles_xz'];assert abs(sum(Polygon(t).area for t in triangles)-shape.area)<1e-5
 chunks=[];x0,z0,x1,z1=shape.bounds
 for x in range(math.floor(x0/8),math.ceil(x1/8)):
  for z in range(math.floor(z0/8),math.ceil(z1/8)):
   piece=shape.intersection(box(x*8,z*8,(x+1)*8,(z+1)*8))
   if piece.area>1e-8:chunks.append({'id':f'cell_{x}_{z}','triangles':[list(t.exterior.coords)[:3] for t in shapely.constrained_delaunay_triangles(piece).geoms]})
 rings=[]
 for poly in ([shape] if shape.geom_type=='Polygon' else shape.geoms):
  poly=orient(poly,sign=1);rings += [list(poly.exterior.coords)[:-1]]+[list(h.coords)[:-1]for h in poly.interiors]
 row={'id':a['id'],'deck':'D08','floor_y':y,'thickness':th,'triangles':triangles,'rings':rings,'render_chunks':chunks,'structural_area_m2':shape.area,'material_role':'guest_floor','owner':a['owner'],'walkable_programme':a.get('walkable',True)};rows.append(row);old.append((row,shape))
assert len(rows)==4
out={'source_checks':{'retained_input_hashes':pins,'retained_owner_count':len(retained),'new_owner_count':4,'slab_volumes_disjoint':True,'river_bed_owner':'asset_river_shell; not duplicated','scope':'Slab contact/nonoverlap only; per-height hull/whole-mesh fit unaccepted'},'regions':rows}
(r/'data/architecture/AQUATIC_ANNEX_FLOORS.json').write_text(json.dumps(out,separators=(',',':'))+'\n');print(json.dumps({'owners':4,'retained_owners':len(retained),'area_m2':sum(a['structural_area_m2']for a in rows)}))
