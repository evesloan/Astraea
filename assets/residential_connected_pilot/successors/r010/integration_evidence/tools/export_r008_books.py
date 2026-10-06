"""Authorized bounded two-thread source export. Fresh scratch only, source unchanged."""
import bpy,json,hashlib
from pathlib import Path
import os
S=Path(os.environ.get('ASTRAEA_RESIDENTIAL_STAGE_ROOT',str(Path(__file__).resolve().parents[1])));P=Path(os.environ.get('ASTRAEA_RESIDENTIAL_SOURCE_ROOT',str(S.parent)));rows=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for cfg in json.loads((P/'COURT_PILOT_PLAN.json').read_text())['rooms']:
 source=P/'outputs/court_domestic_r008'/cfg['address']/'assembly.blend';before=sha(source);dst=S/'assets/models/residential_pilot_205'/f'suite_{cfg["census_source_index"]}_books_r008.glb';assert not dst.exists()
 bpy.ops.wm.open_mainfile(filepath=str(source));bpy.context.view_layer.update();bpy.ops.object.select_all(action='DESELECT');selected=[]
 for obj in bpy.context.scene.objects:
  if obj.type=='MESH' and obj.name.startswith(('SUI_DeskBook_','SUI_TableBook_')):obj.select_set(True);selected.append(obj.name)
 assert len(selected)==5+cfg['occupant_props_variant']
 bpy.ops.export_scene.gltf(filepath=str(dst),export_format='GLB',use_selection=True,export_yup=True,export_extras=True)
 assert sha(source)==before
 rows.append({'room':cfg['address'],'source_census_index':cfg['census_source_index'],'source':str(source),'source_sha256_before':before,'source_sha256_after':sha(source),'parts':selected,'output':str(dst),'output_sha256':sha(dst)})
(S/'qa/BOOK_EXPORT_PROOF.json').write_text(json.dumps({'status':'exact r008 source book layer exported','blender_threads':2,'source_files_unchanged':True,'rooms':rows},indent=2)+'\n');print('R008_BOOK_EXPORT_PASS',sum(len(r['parts'])for r in rows))
