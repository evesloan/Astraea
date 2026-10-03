"""Clean source-only rebuild, new outputs absent before launch.
Copies original source inputs only. New enamel PNG/manifest are regenerated
from the original draw_textures.py before loading retail_materials.py.
"""
from pathlib import Path
import json,hashlib,shutil,subprocess
BASE=Path(__file__).resolve().parents[1];CAT=BASE.parents[1];STAGE=BASE/'qa/source_only_stage/catalogue'
assert not STAGE.exists(),'Never silently reuse or erase an earlier rebuild stage'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
common=json.loads((CAT/'materials/material_manifest.json').read_text())
inputs=['assets/retail_display/source/build_retail_display.py','standards/materials.py','standards/retail_materials.py','materials/material_manifest.json','materials/retail/draw_textures.py']+['materials/'+v['base_color_file']for v in common['materials'].values()]
for rel in inputs:
 dest=STAGE/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(CAT/rel,dest)
closure={'original_inputs':[{'path':p,'sha256':sha(CAT/p)}for p in inputs],'new_artwork_outputs_regenerated':['materials/retail/manifest.json','materials/retail/retail_terracotta_enamel.png'],'excluded':['pre-existing new .blend files','pre-existing new GLB files','new asset manifest/QA files','pre-existing generated retail PNG/manifest'],'commands':['python3 materials/retail/draw_textures.py','blender --background --threads 2 --python assets/retail_display/source/build_retail_display.py'],'all_common_loaded_roles_included':sorted(common['materials']),'no_font_dependency':True,'no_reference_pixels_copied':True}
(BASE/'source_input_manifest.json').write_text(json.dumps(closure,indent=2)+'\n')
assert not list((STAGE/'assets/retail_display').rglob('*.blend')) and not list((STAGE/'assets/retail_display').rglob('*.glb'))
subprocess.run(['python3',str(STAGE/'materials/retail/draw_textures.py')],check=True,cwd=STAGE)
with (BASE/'qa/source_only_build.log').open('w')as log:subprocess.run(['blender','--background','--threads','2','--python',str(STAGE/'assets/retail_display/source/build_retail_display.py')],check=True,cwd=STAGE,stdout=log,stderr=subprocess.STDOUT)
new=STAGE/'assets/retail_display';rows=[]
for ident in['AST-RTL-001','AST-RTL-002']:
 actual=json.loads((BASE/(ident+'.manifest.json')).read_text());regen=json.loads((new/(ident+'.manifest.json')).read_text());equal=[k for k in actual if k not in['source_sha256']and actual[k]==regen[k]];diff=[k for k in actual if k not in['source_sha256']and actual[k]!=regen[k]];rows.append({'catalogue_id':ident,'original_glb_sha256':sha(BASE/'exports'/f'{ident}.glb'),'rebuilt_glb_sha256':sha(new/'exports'/f'{ident}.glb'),'glb_bytes_identical':sha(BASE/'exports'/f'{ident}.glb')==sha(new/'exports'/f'{ident}.glb'),'manifest_fields_equal_except_packed_blend_path_hash':not diff,'differences':diff,'rebuilt_source_sha256':sha(new/'source'/f'{ident}.blend')})
art=[{'path':p,'original_sha256':sha(CAT/p),'regenerated_sha256':sha(STAGE/p),'bytes_identical':sha(CAT/p)==sha(STAGE/p)}for p in closure['new_artwork_outputs_regenerated']]
r={'scope':'Actual clean source-only regeneration, no generated assets or QA seeded','source_input_manifest_sha256':sha(BASE/'source_input_manifest.json'),'stage_path_relative_to_family':'qa/source_only_stage/catalogue','assets':rows,'original_artwork':art,'all_passed':all(x['glb_bytes_identical']and x['manifest_fields_equal_except_packed_blend_path_hash']for x in rows)and all(x['bytes_identical']for x in art)}
(BASE/'qa/source_only_rebuild.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2));assert r['all_passed']
