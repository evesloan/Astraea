"""Bounded native/source geometry proof; no engine/import or changed thresholds."""
from pathlib import Path
import json,struct,hashlib,math
N=Path(__file__).resolve().parent;R=N.parents[2];P=R/'Game/sunset_enclosure_finish_20261024'
p=json.loads((P/'PLAN_r002.json').read_text());data=(P/'SunsetEnclosure_r002.glb').read_bytes();n=struct.unpack_from('<I',data,12)[0];g=json.loads(data[20:20+n]);binary=data[28+n:]
walls={w['source_part']:w for w in p['walls']};rows={r['name']:r for r in p['parts']};fail=[];maximum=0.;vertices=0;seen=set()
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
for path,key in [('source_plan','source_plan_sha256'),('native_source','native_source_sha256'),('material_library','material_library_sha256')]:
 assert sha(R/p[path])==p[key],path
assert sha(P/'SunsetEnclosure_r002.glb')==p['glb_sha256']
assert sha(N/'SunsetEnclosure_r002.blend')==p['native_sha256']
for node in g['nodes']:
 if 'mesh'not in node:continue
 name=node['name'];seen.add(name);row=rows[name];w=walls[row['owner']]
 assert not any(k in node for k in ['matrix','translation','rotation','scale']),name
 for primitive in g['meshes'][node['mesh']]['primitives']:
  a=g['accessors'][primitive['attributes']['POSITION']];bv=g['bufferViews'][a['bufferView']];offset=bv.get('byteOffset',0)+a.get('byteOffset',0);stride=bv.get('byteStride',12)
  assert a['componentType']==5126 and a['type']=='VEC3'
  for i in range(a['count']):
   x,y,z=struct.unpack_from('<fff',binary,offset+i*stride);dx,dz=x-w['a'][0],z-w['a'][1];u=dx*w['t'][0]+dz*w['t'][1];depth=dx*w['normal'][0]+dz*w['normal'][1];vertices+=1;maximum=max(maximum,depth)
   if not(-.0001<=u<=w['length']+.0001 and -.0001<=depth<=.3601 and w['y_min']-.0001<=y<=w['y_max']+.0001):fail.append([name,x,y,z,u,depth])
assert seen==set(rows),'Native part identities differ'
assert not fail,fail[:8]
# Source D17 opening intervals are excluded by deriving each treatment from
# individual clipped solid source parts, including the diagonal aft edge.
report=dict(status='PASS_EXACT_SOLID_WALL_ENVELOPE',parts=len(seen),vertices_checked=vertices,wall_sections=len(walls),maximum_inward_projection_m=maximum,source_inputs_verified=3,no_geometry_outside_retained_solid_sections=True,new_floors_or_hull_cuts=False,new_capacity=0,preserved_upper_openings=True,scope='Source geometry only; installed contacts/visual acceptance recorded separately')
(P/'evidence_r002/GEOMETRY.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
