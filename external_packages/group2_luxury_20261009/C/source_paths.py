"""Worker-owned source paths from the fixed81 identity inventory."""
import pathlib,json
R=pathlib.Path(__file__).resolve().parent
def section(unit):
 row=next(x for x in json.loads((R/'LUXURY_81_INVENTORY.json').read_text(encoding='utf-8'))['records'] if x['identity']['source_envelope_index']==int(unit))
 tier=row['reservation']['tier'];o=R/'sections'/f'{unit}_{tier}'
 return row,o,o/f'{unit}_{tier}.blend',o/f'{unit}_{tier}.glb'
def inside_polygon(x,z,p,tolerance=.0001):
 # Boundary distance first, then an ordinary even/odd crossing test. Supports
 # actual irregular reservations; a bounding rectangle is not accepted as fit.
 import math
 inside=False
 for a,b in zip(p,p[1:]+p[:1]):
  dx=b[0]-a[0];dz=b[1]-a[1];d=dx*dx+dz*dz
  t=max(0,min(1,((x-a[0])*dx+(z-a[1])*dz)/d)) if d else 0
  if math.hypot(x-a[0]-t*dx,z-a[1]-t*dz)<=tolerance:return True
  if (a[1]>z)!=(b[1]>z) and x<(b[0]-a[0])*(z-a[1])/(b[1]-a[1])+a[0]:inside=not inside
 return inside
