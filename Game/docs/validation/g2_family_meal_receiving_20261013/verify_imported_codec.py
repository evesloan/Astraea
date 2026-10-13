from pathlib import Path
import json,struct,hashlib,math,collections,zipfile
P=Path(__file__).parent;G=Path('/workspace/astraea-protected-integration-20261012/Game');b=(G/'assets/models/FAMILY_TERRACE_ARCHITECTURE_lift_r003.glb').read_bytes();assert hashlib.sha256(b).hexdigest()=='53220c30d8167a9f35e43ac4feb9e934f44f2c0aeecd97d1b6cc9cd3e00c312c';n,_=struct.unpack_from('<II',b,12);doc=json.loads(b[20:20+n]);buf=b[28+n:];probes=json.loads((P/'IMPORTED_TABLE_CODEC_VERIFICATION_INPUT.json').read_text());preflight=json.loads((P/'import/Game/data/group2_family_meal/CURRENT_TABLE_PREFLIGHT.json').read_text());records=[]
def accessor(i):
 a=doc['accessors'][i];v=doc['bufferViews'][a['bufferView']];fmt={5126:'f',5125:'I',5123:'H'}[a['componentType']];width={'VEC3':3,'SCALAR':1}[a['type']];size=struct.calcsize('<'+fmt*width);base=v.get('byteOffset',0)+a.get('byteOffset',0);stride=v.get('byteStride',size);return[struct.unpack_from('<'+fmt*width,buf,base+j*stride)for j in range(a['count'])]
for probe in probes:
 row=next(x for x in preflight['table_parts']if x['name']==probe['table']);node=next(x for x in doc['nodes']if x.get('name')==row['batch_node']);p=doc['meshes'][node['mesh']]['primitives'][0];allverts=accessor(p['attributes']['POSITION']);start=row['vertex_start'];end=start+row['vertex_count'];raw=allverts[start:end];unique=sorted(set(raw));ids={p:i for i,p in enumerate(unique)};mapping=[];maximum=0.;axismax=0.
 assert probe['surface_format']&probe['compress_attributes_flag']
 for at in probe['vertices']:
  delta,nearest=min((math.dist(at,q),q)for q in unique);maximum=max(maximum,delta);axismax=max(axismax,max(abs(at[i]-nearest[i])for i in range(3)));assert delta<.002,(probe['table'],delta);mapping.append(ids[nearest])
 sourceidx=[x[0]for x in accessor(p['indices'])];actualidx=[int(x)for x in probe['indices']];sourcefaces=collections.Counter();actualfaces=collections.Counter()
 for i in range(0,len(sourceidx),3):
  t=sourceidx[i:i+3]
  if all(start<=q<end for q in t):sourcefaces[tuple(sorted(ids[allverts[q]]for q in t))]+=1
 for i in range(0,len(actualidx),3):
  t=actualidx[i:i+3]
  if all(start<=q<end for q in t):actualfaces[tuple(sorted(mapping[q-start]for q in t))]+=1
 assert actualfaces==sourcefaces,(probe['table'],sum(sourcefaces.values()),sum(actualfaces.values()))
 row.update(imported_vertex_sha256=probe['actual_sha'],imported_surface_format=probe['surface_format']);records.append({'table':probe['table'],'raw_source_vertex_sha256':row['source_vertex_sha256'],'current_imported_vertex_sha256':probe['actual_sha'],'vertices':len(raw),'triangles':sum(sourcefaces.values()),'triangle_topology_and_geometry_equivalent_with_codec_precision':True,'maximum_vertex_distance_m':maximum,'maximum_axis_delta_m':axismax,'compressed_attributes':True})
with zipfile.ZipFile('/workspace/astraea-windows-build-evidence-20261012/Astraea_Windows_Preview_47eb835_20261012.zip')as z:
 raw=z.read('assets/models/FAMILY_TERRACE_ARCHITECTURE_lift_r003.glb');assert raw==b;cache='.godot/imported/FAMILY_TERRACE_ARCHITECTURE_lift_r003.glb-d4c213c480cb72545146bb5681964ccb.scn';cachehash=hashlib.sha256(z.read(cache)).hexdigest()
preflight['runtime_preimage_basis']='Exact retained current imported vertex hashes; raw source hashes retained separately. Every source triangle matches current cached geometry within measured compressed-attribute precision.';(P/'import/Game/data/group2_family_meal/CURRENT_TABLE_PREFLIGHT.json').write_text(json.dumps(preflight,indent=2)+'\n');receipt={'status':'PASS_EXPLAINED_EXISTING_IMPORT_CODEC_PREIMAGES','raw_receiver_source_sha256':hashlib.sha256(b).hexdigest(),'original_retained_preview_cached_scene_sha256':cachehash,'rows':records,'original_receiver_reimported_or_modified':False,'source_tabletop_support_tolerance_m':.002,'raw_to_import_comparison_not_used_as_fuzzy_runtime_preimage':True,'retained_import_setting_force_disable_compression':False,'source_shape_topology_or_table_dimensions_changed':False};(P/'IMPORTED_CODEC_VERIFICATION.json').write_text(json.dumps(receipt,indent=2)+'\n');print('PASS exact source triangle topology;compressed attribute deltas',[(r['table'],r['maximum_vertex_distance_m'])for r in records])
