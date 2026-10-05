from pathlib import Path
import json
from shapely.geometry import Polygon,box
from shapely.ops import triangulate
R=Path(__file__).resolve().parents[1]
poly=box(-36,102,36,142).union(Polygon([(-36,142),(36,142),(36,182),(26,194),(-26,194),(-36,182)])).union(box(-4,194,4,206)).union(box(-36,96,36,102))
for h in[box(-1.82,110.98,1.82,115.02),box(-3.1,123,3.1,133.7)]:poly=poly.difference(h)
tris=[list(t.exterior.coords)[:3]for t in triangulate(poly)if poly.covers(t)]
(R/'qa/preview_floor_context.json').write_text(json.dumps({'scope':'Unsaved QA-only planned platform, existing core holes and context aprons. Parent owns exact floor compilation. Never exported in005.','triangles':tris},indent=2)+'\n')
