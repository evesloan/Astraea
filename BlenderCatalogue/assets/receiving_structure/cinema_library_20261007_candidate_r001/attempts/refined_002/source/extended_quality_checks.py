from pathlib import Path
import json,struct,hashlib,collections,sys
import numpy as np
O=Path(__file__).resolve().parents[1];sys.path.insert(0,str(O/'inputs'));from decode_sections import glb
M,N=glb(O/'exports/cinema_library_receiving_r001.glb',np.zeros(3));by={m['name']:m for m in M};pol=json.load(open(O/'exports/floor_contract.json'))
def area(p):return abs(sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(p,p[1:]+p[:1])))/2
p=pol['source_cinema_polygon'];rect=[8,11.4,-466,-398]
def cut(poly,axis,plane,sign):
 out=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  fa=sign*(a[axis]-plane);fb=sign*(b[axis]-plane)
  if fa>=0:out.append(a)
  if (fa>=0)!=(fb>=0):out.append([a[i]+(b[i]-a[i])*fa/(fa-fb) for i in range(2)])
 return out
inter=p
for ax,val,sgn in [(0,8,1),(0,11.4,-1),(1,-466,1),(1,-398,-1)]:inter=cut(inter,ax,val,sgn)
expected=area(p)+(rect[1]-rect[0])*(rect[3]-rect[2])-area(inter);actual=area(pol['union_polygon'])
hangers=[]
for m in M:
 if '_Hanger' not in m['name']:continue
 g=m['extras']['semantic_group'];segment=g.rsplit('_',1)[-1];top=by[f'LONG_X9_S{segment}_Top_lower_flange'];num=m['name'].split('_Hanger')[1].split('_')[0];saddle=by[g+'_Saddle'+num];
 hangers.append(dict(name=m['name'],top_gap_m=float(top['min'][1]-m['max'][1]),bottom_gap_m=float(m['min'][1]-saddle['max'][1])))
b=(O/'exports/cinema_library_receiving_r001.glb').read_bytes();n,k=struct.unpack_from('<II',b,12);d=json.loads(b[20:20+n]);types={5120:'i1',5121:'u1',5122:'<i2',5123:'<u2',5125:'<u4',5126:'<f4'};rawstart=20+n+8;raw=b[rawstart:]
def acc(i,c):
 a=d['accessors'][i];v=d['bufferViews'][a['bufferView']];t=np.dtype(types[a['componentType']]);return np.ndarray((a['count'],c),dtype=t,buffer=raw,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',c*t.itemsize),t.itemsize)).copy()
uv=[]
for mesh in d['meshes']:
 for prim in mesh['primitives']:
  if 'TEXCOORD_0' not in prim['attributes']:uv.append(False);continue
  q=acc(prim['attributes']['TEXCOORD_0'],2);f=acc(prim['indices'],1).reshape(-1,3);t=q[f];a=t[:,1]-t[:,0];bb=t[:,2]-t[:,0];uv.append(bool(np.any(abs(a[:,0]*bb[:,1]-a[:,1]*bb[:,0])>1e-9)))
report=dict(status='PASS',floor_union={'source_polygon_area_m2':area(p),'west_strip_area_m2':(rect[1]-rect[0])*(rect[3]-rect[2]),'overlap_area_m2':area(inter),'expected_union_area_m2':expected,'authored_union_area_m2':actual,'passed':abs(expected-actual)<1e-6},service_hanger_contacts=hangers,all_service_hangers_touch_saddle_and_chord=all(abs(x['top_gap_m'])<6e-5 and abs(x['bottom_gap_m'])<6e-5 for x in hangers),material_count=len(d['materials']),texture_count=len(d['textures']),images_embedded=all('bufferView' in im and not im.get('uri') for im in d['images']),all_export_primitives_have_nonzero_uv_area=all(uv),selected_glb_sha256=hashlib.sha256(b).hexdigest())
if not all([report['floor_union']['passed'],report['all_service_hangers_touch_saddle_and_chord'],report['images_embedded'],report['all_export_primitives_have_nonzero_uv_area']]):report['status']='FAIL'
(O/'qa/extended_quality_checks.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));assert report['status']=='PASS'
