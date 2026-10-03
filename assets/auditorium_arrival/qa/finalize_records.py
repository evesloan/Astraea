from pathlib import Path
import json,hashlib
B=Path(__file__).resolve().parents[1];C=B.parents[1]
def rec(p,key='path'):
 return {key:str(p.relative_to(C)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
shared=[C/'standards/auditorium_materials.py',C/'standards/materials.py',C/'materials/material_manifest.json',C/'materials/auditorium/manifest.json']
for k,r in json.loads((C/'materials/material_manifest.json').read_text())['materials'].items():shared.append(C/'materials'/r['base_color_file'])
for k,r in json.loads((C/'materials/auditorium/manifest.json').read_text())['materials'].items():shared.append(C/'materials/auditorium'/r['file'])
local=[B/'source/build_auditorium_arrival.py',B/'source/draw_programme.py',B/'source/fonts/DejaVuSans.ttf',B/'source/fonts/DejaVu-LICENSE.txt',B/'textures/programme_original.png',B/'textures/usher_original.png']
inputs=local+shared
outputs=[p for pattern in('source/*.blend','exports/*.glb','*.manifest.json','manifest.json','marker_api.json','collision_proposals.json','README.md')for p in sorted(B.glob(pattern)) if p.is_file()]
d={'schema':'astraea_source_dependency_closure_v1','scope':'All direct production and reproducible artwork inputs; every helper-loaded common/auditorium role included even when unused. No QA file, old blend or generated GLB is a production input.','software':'Blender 4.3.2 bundled glTF; Python 3 and Pillow for original graphics','generator_command_from_catalogue_root':'blender --background --threads 2 --python-exit-code 1 --python assets/auditorium_arrival/source/build_auditorium_arrival.py','art_regeneration_command_from_catalogue_root':'python3 assets/auditorium_arrival/source/draw_programme.py','font_provenance':{'source':'Unmodified DejaVuSans.ttf from installed Debian fonts-dejavu-core','upstream':'https://dejavu-fonts.github.io/','bundled_font':'source/fonts/DejaVuSans.ttf','bundled_license':'source/fonts/DejaVu-LICENSE.txt','license':'Bitstream Vera font license; DejaVu changes public domain; redistributed unmodified with notice'},'source_only_inputs':[rec(p)for p in inputs],'local_input_files':[dict(path=str(p.relative_to(B)),sha256=rec(p)['sha256'],bytes=p.stat().st_size)for p in local],'external_input_files':[rec(p,'path_from_catalogue_root')for p in shared],'files':[rec(p)for p in outputs]}
(B/'dependency_manifest.json').write_text(json.dumps(d,indent=2)+'\n')
paths=sorted(set(inputs+outputs+[B/'dependency_manifest.json']))
(B/'SHA256SUMS.txt').write_text(''.join(rec(p)['sha256']+'  '+str(p.relative_to(C))+'\n'for p in paths))
print('DEPENDENCIES',len(inputs),'PRODUCTION_OUTPUTS',len(outputs))
