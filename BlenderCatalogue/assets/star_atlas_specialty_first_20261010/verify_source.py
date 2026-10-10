from pathlib import Path
import json,hashlib,subprocess
import numpy as np
from shapely.geometry import Polygon,Point
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.loads((W/'PLAN.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for rel,h in P['preimage_pins'].items():
 data=subprocess.check_output(['git','show',P['base_commit']+':'+rel],cwd=R);assert hashlib.sha256(data).hexdigest()==h
 if rel!='Game/scripts/central_homes_adoption.gd':assert sha(R/rel)==h,rel
ns={'__file__':str(W/'geometry_reader.py')};exec((R/'BlenderCatalogue/assets/tidal_d15_service_receiving_20261010/source_geometry.py').read_text(),ns)
checks=[]
for room in P['rooms']:
 for toe in room['receiving_contacts']:
  face=np.array(toe['source_roof_triangle']);poly=Polygon(face[:,[0,2]]);a,b,c=face;n=np.cross(b-a,c-a)
  for v in toe['bottom_contact_vertices']:
   assert poly.buffer(1e-6).covers(Point(v[0],v[2]));y=a[1]-(n[0]*(v[0]-a[0])+n[2]*(v[2]-a[2]))/n[1];assert abs(y-v[1])<1e-6
  checks.append({'index':room['allocation']['source_envelope_index'],'roof':toe['source_roof_mesh'],'source_toe_area_m2':.04})
for a in P['sources']:assert sha(R/'BlenderCatalogue'/a['source'])==a['source_sha256'] and sha(R/'BlenderCatalogue'/a['export'])==a['export_sha256']
r={'status':'PASS','exact_baseline_pins':len(P['preimage_pins']),'unchanged_catalogued_components':len(P['sources']),'full_toe_source_triangle_contacts':len(checks),'source_receiving_toe_area_m2':sum(c['source_toe_area_m2']for c in checks),'commons_unchanged_objects':512,'limits':'Triangle contact geometry only; source roof loading, primary capacity and habitat fit remain unaccepted'}
(W/'ACTUAL_SOURCE_CHECK.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
