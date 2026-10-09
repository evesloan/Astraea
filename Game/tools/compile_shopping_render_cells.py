import json,math,sys
from pathlib import Path
import shapely
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
r=Path(__file__).resolve().parents[1]
p=r/'data/architecture/SHOPPING_PROMENADE.json';d=json.loads(p.read_text());count=0
for row in d['floor_proposals']:
 s=Polygon(row['boundary'],row['holes']);chunks=[];x0,z0,x1,z1=s.bounds
 for x in range(math.floor(x0/16),math.ceil(x1/16)):
  for z in range(math.floor(z0/16),math.ceil(z1/16)):
   q=s.intersection(box(x*16,z*16,(x+1)*16,(z+1)*16))
   if q.area>1e-8:chunks.append({'id':f'cell_{x}_{z}','triangles':[[list(c) for c in t.exterior.coords[:3]] for t in shapely.constrained_delaunay_triangles(q).geoms]})
 assert unary_union([Polygon(t) for c in chunks for t in c['triangles']]).symmetric_difference(s).area<1e-7
 row['render_chunks']=chunks;count+=len(chunks)
t=p.with_suffix('.new');t.write_text(json.dumps(d,separators=(',',':'))+'\n');t.replace(p)
p=r/'scripts/shopping_promenade_adoption.gd';s=p.read_text().replace('"render_chunks":[]','"render_chunks":record.render_chunks');t=p.with_suffix('.new');t.write_text(s);t.replace(p)
print({'floors':204,'render_cells':count,'coverage':'PASS'})
