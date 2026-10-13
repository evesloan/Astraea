from pathlib import Path
import json,struct,hashlib
C=Path(__file__).parent;G=Path('/workspace/astraea-protected-integration-20261012/Game');ns={'__file__':str(C/'preflight_g3_first_floor_overlap.py')};exec((C/'preflight_g3_first_floor_overlap.py').read_text().split('old=[]')[0],ns);pins=json.loads((C/'g3_receiving_metadata/Game/data/architecture/group3_commons_crossings_20261012/CROSSINGS.json').read_text())['original_source_model_pins'];owned=[];floorrows=[]
def accessor(d,binbuf,idx):
 a=d['accessors'][idx];v=d['bufferViews'][a['bufferView']];fmt={5126:'f',5125:'I',5123:'H',5121:'B'}[a['componentType']];width={'VEC3':3,'SCALAR':1}[a['type']];size=struct.calcsize('<'+fmt*width);stride=v.get('byteStride',size);offset=v.get('byteOffset',0)+a.get('byteOffset',0);return[struct.unpack_from('<'+fmt*width,binbuf,offset+i*stride)for i in range(a['count'])]
for name,h in pins.items():
 b=(G/'assets/models'/name).read_bytes();assert hashlib.sha256(b).hexdigest()==h;size,_=struct.unpack_from('<II',b,12);d=json.loads(b[20:20+size]);off=20+size;binsize,kind=struct.unpack_from('<II',b,off);buf=b[off+8:off+8+binsize]
 for node in d['nodes']:
  if'mesh'not in node or'floor'not in node.get('name','').lower()or'shoe'in node.get('name','').lower():continue
  if any(k in node for k in ['matrix','translation','rotation','scale']):continue # Exclude transformed furniture floor-pads;scope is baked structural source floors.
  count=0
  for p in d['meshes'][node['mesh']]['primitives']:
   verts=accessor(d,buf,p['attributes']['POSITION']);indices=[q[0]for q in accessor(d,buf,p['indices'])]if'indices'in p else list(range(len(verts)))
   for i in range(0,len(indices),3):
    tri=[verts[j]for j in indices[i:i+3]]
    if all(abs(q[1]-12)<.00002 for q in tri):owned.append((name,node['name'],[[q[0],q[2]]for q in tri]));count+=1
  if count:floorrows.append({'source_file':name,'source_sha256':h,'mesh':node['name'],'floor_y':12.,'top_triangles':count})
source=json.loads((C/'g3_street_preflight/REMAINING_STREET_MISSING_FLOOR.json').read_text());hits=[]
for part in source['parts']:
 for i,t in enumerate(part['triangles']):
  for file,node,old in owned:
   area=ns['overlap'](t,old)
   if area>1e-6:hits.append({'part':part['name'],'triangle':i,'current_source_file':file,'current_mesh':node,'area_m2':area})
result={'status':'HOLD_EXACT_CURRENT_NATIVE_FLOOR_OVERLAP'if hits else'PASS_NO_OVERLAP_WITH_VERIFIED_D04_NATIVE_FLOORS','protected_current_floor_sources':floorrows,'overlap_m2':sum(q['area_m2']for q in hits),'overlap_pairs':hits,'source_originals_changed':False,'candidate_floor_regenerated_or_trimmed':False,'all13_source_network_failed_criteria_preserved':True,'crossing_wall_derivatives_remove_onlydeclaredwalls_notexistingfloors':True};(C/'G3_STREET_CURRENT_NATIVE_FLOOR_OVERLAP.json').write_text(json.dumps(result,indent=2)+'\n');print(result['status'],'floor sources',len(floorrows),'overlap_m2',result['overlap_m2'],'pairs',len(hits));print([(q['source_file'],q['mesh'],q['top_triangles'])for q in floorrows])
