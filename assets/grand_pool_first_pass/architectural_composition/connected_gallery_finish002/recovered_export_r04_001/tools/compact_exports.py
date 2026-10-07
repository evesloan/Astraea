"""Lossless GLB provenance deduplication. Geometry binary and all original JSON recover exactly."""
from pathlib import Path
import json,struct,hashlib
B=Path(__file__).parent;R=B/'export_tools/runs/recovered001';O=B/'compact_exports001';O.mkdir(exist_ok=False)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
report={'status':'PASS_LOSSLESS_PROVENANCE_DEDUPLICATION','source_sha256':'fa6decb8198bec9aa13d92de35e030358913dc09f61710bb0225d3dd8560d50f','raw_equivalence_sha256':sha(R/'equivalence/GLB_EQUIVALENCE.json'),'scope':'Only repeated scene provenance moved to one asset extra; no geometry, material, UV, hierarchy or marker change','assets':[]}
for p in sorted((R/'exports').glob('*.glb')):
 raw=p.read_bytes();n=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+n]);original=json.loads(raw[20:20+n]);suffix=raw[20+n:];scene=None;count=0
 for node in doc['nodes']:
  e=node['extras'];value=e.pop('selected_source_scene_properties_json')
  if scene is None:scene=value
  assert scene==value
  e['selected_source_scene_properties_sha256']=hashlib.sha256(scene.encode()).hexdigest();count+=1
 assert 'extras' not in doc['asset'];doc['asset']['extras']={'selected_source_scene_properties_json':scene,'provenance_deduplication_schema':1}
 jb=json.dumps(doc,separators=(',',':'),ensure_ascii=True).encode();jb+=b' '*((-len(jb))%4)
 new=struct.pack('<III',0x46546c67,2,20+len(jb)+len(suffix))+struct.pack('<II',len(jb),0x4e4f534a)+jb+suffix;target=O/p.name;target.write_bytes(new)
 recovered=json.loads(new[20:20+len(jb)]);a=recovered['asset'].pop('extras');assert a['provenance_deduplication_schema']==1
 for node in recovered['nodes']:
  e=node['extras'];assert e.pop('selected_source_scene_properties_sha256')==hashlib.sha256(a['selected_source_scene_properties_json'].encode()).hexdigest();e['selected_source_scene_properties_json']=a['selected_source_scene_properties_json']
 assert recovered==original and new[20+len(jb):]==suffix
 report['assets'].append({'file':p.name,'raw_sha256':sha(p),'compact_sha256':sha(target),'raw_bytes':len(raw),'compact_bytes':len(new),'nodes_with_exact_provenance_reconstruction':count,'binary_chunk_unchanged_sha256':hashlib.sha256(suffix).hexdigest(),'inverse_json_exact':True,'binary_unchanged':True})
(O/'COMPACT_EQUIVALENCE.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
