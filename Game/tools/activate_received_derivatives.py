"""Activate explicitly requested, preservation-proved receiving derivatives."""
from pathlib import Path
import json,shutil,hashlib,sys
G=Path(__file__).resolve().parents[1];R=G.parent;A=R/'BlenderCatalogue/assets/received_sections_20261008'
mode=sys.argv[1]
if mode=='core':
 label,contract=sys.argv[2:];p=A/(label+'_core_aperture');c=json.loads((p/'APERTURE_INPUT.json').read_text());proof=json.loads((p/'RUNTIME_PROOF.json').read_text());assert proof['outside_aperture_volume_unchanged'] and proof['inverse_hash_verified']
 cp=G/'data/architecture'/contract;d=json.loads(cp.read_text());assert hashlib.sha256((G/'assets/models'/d['enclosure_file']).read_bytes()).hexdigest()==c['original_glb_sha256'];pre=p/(contract+'.preimage');assert not pre.exists();pre.write_bytes(cp.read_bytes());target=G/'assets/models'/c['output_glb'];assert not target.exists();shutil.copy2(p/c['output_glb'],target);d['enclosure_file']=c['output_glb'];cp.write_text(json.dumps(d,indent=2)+'\n');print(c['output_glb'])
elif mode=='section':
 p=G/'data/architecture/received_sections.json';d=json.loads(p.read_text())
 for key in sys.argv[2:]:
  folder=A/'D'/key/'root_entry_correction';proof=json.loads((folder/'RUNTIME_PROOF.json').read_text());row=next(x for x in d['sections'] if x['programme_key']==key);assert row['source_sha256']==proof['original_sha256'];assert proof['other_nodes_meshes_and_materials_exact'];name='SOL_'+key+'_entry001.glb';assert not (G/'assets/models'/name).exists();shutil.copy2(folder/(key+'_entry001.glb'),G/'assets/models'/name)
  row.update(model_file=name,source_sha256=proof['successor_sha256'],retained_original_native_path=row['editable_source'],editable_source=str(folder.relative_to(R)/'section_entry_corrected.blend'),root_entry_correction=str(folder.relative_to(R)/'RUNTIME_PROOF.json'));print(key)
 p.write_text(json.dumps(d,indent=2)+'\n')
else:raise ValueError(mode)
