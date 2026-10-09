from pathlib import Path
import json,sys
sys.path.insert(0,'/workspace/shared/astraea_python_deps')
from shapely.geometry import Polygon,LineString,box
from shapely.ops import unary_union
r=Path(__file__).resolve().parents[3];g=r/'Game';o=r/'BlenderCatalogue/assets/central_residential_streets_20261009';p=g/'data/architecture/CENTRAL_RESIDENTIAL_STREETS.json';d=json.load(open(p));prior=[x for f in ['structural_meshes.json','received_structural_meshes.json'] for x in json.load(open(g/'data/generated'/f))['regions']]
b=r/'BlenderCatalogue/assets/residential_hotels/central_room_families_20261007_r001/residential-neighborhood-courts-20261007';units=[]
for folder,name in [('star_atlas_interiors','STAR_ATLAS_85_CURRENT_APPLICATION.json'),('night_garden_interiors','NIGHT_GARDEN_80_CURRENT_APPLICATION.json')]:
 app=json.load(open(b/folder/name));units.extend(app['units']);units.extend(app.get('preserved_installed',[]))
guards=[]
for region in d['regions']:
 y=region['floor_y'];existing=unary_union([Polygon(t) for v in prior if abs(v['floor_y']-y)<.001 for t in v['triangles']]);rooms=unary_union([box(u['allocation_x'][0],u['allocation_z'][0],u['allocation_x'][1],u['allocation_z'][1]) for u in units if abs(u['floor_y']-y)<.001]);skip=existing.buffer(.021).union(rooms.buffer(.021))
 for ring in region['rings']:
  line=LineString(ring+[ring[0]]).difference(skip)
  for part in ([line] if line.geom_type=='LineString' else getattr(line,'geoms',[])):
   coords=list(part.coords)
   for a,b in zip(coords,coords[1:]):
    if LineString([a,b]).length>.08:guards.append({'id':region['id']+'_Guard_'+str(len(guards)),'a':[a[0],y,a[1]],'b':[b[0],y,b[1]],'height':1.1})
d['exposed_edge_guards']=guards
for path in [p,o/'STREET_PLAN.json']:
 t=path.with_name(path.name+'.new');t.write_text(json.dumps(d,indent=2)+'\n');t.replace(path)
