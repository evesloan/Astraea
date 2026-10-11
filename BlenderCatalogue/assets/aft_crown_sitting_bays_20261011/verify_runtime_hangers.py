from pathlib import Path
import struct,json,hashlib
import numpy as np
from shapely.geometry import LineString,Polygon,box
from shapely.ops import unary_union,polygonize
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.load(open(W/'PLAN.json'));raw=(R/'Game/assets/models/AST-CMD-005.glb').read_bytes();n=struct.unpack_from('<I',raw,12)[0];D=json.loads(raw[20:20+n]);start=20+n+8;binary=raw[start:];types={5126:np.float32,5125:np.uint32,5123:np.uint16,5121:np.uint8}
def data(i):
 a=D['accessors'][i];v=D['bufferViews'][a['bufferView']];dt=np.dtype(types[a['componentType']]);width={'SCALAR':1,'VEC3':3}[a['type']];offset=v.get('byteOffset',0)+a.get('byteOffset',0);stride=v.get('byteStride',dt.itemsize*width);return np.ndarray((a['count'],width),dtype=dt,buffer=binary,offset=offset,strides=(stride,dt.itemsize))
triangles=[]
for node in D['nodes']:
 if 'mesh'not in node:continue
 assert not any(k in node for k in ['matrix','rotation','scale','translation','children'])
 for p in D['meshes'][node['mesh']]['primitives']:
  vs=data(p['attributes']['POSITION']);idx=data(p['indices']).reshape(-1)if'indices'in p else np.arange(len(vs));triangles.extend(vs[idx].reshape(-1,3,3))
triangles=np.array(triangles);Y=110.96;cross=triangles[(triangles[:,:,1].min(axis=1)<Y)&(triangles[:,:,1].max(axis=1)>Y)];report=[]
for bay in P['bays']:
 expected=unary_union([Polygon(q['polygon'])for q in P['retained_roof_member_fits']if q['bay']==bay['name']]);bounds=expected.bounds;zone=box(bounds[0]-.2,bounds[1]-.2,bounds[2]+.2,bounds[3]+.2);lines=[]
 for tri in cross:
  pts=[]
  for a,b in zip(tri,np.roll(tri,-1,axis=0)):
   if (a[1]-Y)*(b[1]-Y)<0:
    v=a+(b-a)*((Y-a[1])/(b[1]-a[1]));pts.append((round(float(v[0]),5),round(float(v[2]),5)))
  if len(pts)==2:
   line=LineString(pts)
   if zone.covers(line):lines.append(line)
 actual=unary_union(list(polygonize(unary_union(lines))));assert actual.area>0,bay['name'];difference=actual.symmetric_difference(expected).area;assert difference<.00002,(bay['name'],difference,actual.area,expected.area)
 report.append({'bay':bay['name'],'runtime_spatial_batches_cross_section_y':Y,'source_native_and_actual_runtime_hanger_footprint_difference_m2':difference,'runtime_hanger_footprint_m2':actual.area})
(W/'ACTUAL_RUNTIME_HANGER_PREFLIGHT.json').write_text(json.dumps({'status':'PASS','actual_original_runtime_model_sha256':hashlib.sha256(raw).hexdigest(),'spatial_batched_original_mesh_cross_sections':report,'native_owner_names_are_batched_in_runtime':True,'original_model_unchanged':True},indent=2)+'\n');print('PASS actual runtime hanger cross sections',report)
