from pathlib import Path
import json,hashlib,shutil
R=Path(__file__).resolve().parent;C=R/'compiler_candidate';G=Path('/workspace/shared/Astraea_recovery_20261007_AXWr5x/Game');ctx=json.loads((C/'data/architecture/packages/night_table/BUILD_CONTEXT.json').read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for p in (R/'runtime_candidate').rglob('*'):
 if p.is_file() and '.godot' not in p.parts:
  q=C/p.relative_to(R/'runtime_candidate');q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q)
gpath='tests/medical_triage_successor_guard.gd';spath='scripts/ship.gd'
s=(G/gpath).read_text();original=s;edits=[]
def edit(before,after,count=1):
 global s
 assert s.count(before)==count,(before,s.count(before));s=s.replace(before,after);edits.insert(0,dict(before=before,after=after,count=count))
# Route only the outer predecessor layer through the authenticated Night Table layer.
start=s.index('# UPPER_HULL_EXACT_SECTION_BEGIN');section=s[start:]
for before,after in [('FileAccess.get_sha256("res://"+str(path))','_night_current_sha256("res://"+str(path))'),('FileAccess.get_file_as_string("res://"+str(path))','_night_current_text("res://"+str(path))'),('else FileAccess.get_file_as_string(path)','else _night_current_text(path)'),('else FileAccess.get_sha256(path)','else _night_current_sha256(path)')]:
 old=section;assert before in section;section=section.replace(before,after)
# One whole section inverse protects unchanged nested text.
edit(s[start:],section)
for path in ['data/spatial_layout.json','data/generated/structural_meshes.json','docs/LAYOUT_COMPILE_CHECKS.json']:
 before='FileAccess.get_file_as_string("res://'+path+'")'
 # Only direct reads in sports and star sections; all other earlier functions have their own projections.
 for marker,endmarker in [('# SPORTS_CARE_EXACT_SECTION_BEGIN','# SPORTS_CARE_EXACT_SECTION_END'),('# STAR_FITTED_EXACT_SECTION_BEGIN','# STAR_FITTED_EXACT_SECTION_END')]:
  a=s.index(marker);b=s.index(endmarker,a);part=s[a:b]
  if before in part:edit(part,part.replace(before,'_night_current_text("res://'+path+'")'))
edit('assert(floors!=null and floors.get_child_count()==282,"Complete actual 282-owner roster required before predecessor projection")','assert(floors!=null and _night_floor_children(floors).size()==282,"Complete actual 284-owner roster authenticated before predecessor projection")')
a=s.index('static func _sports_care_floor_children');b=s.index('static func _sports_care_v',a);part=s[a:b];edit(part,part.replace('var children: Array=floors.get_children()','var children: Array=_night_floor_children(floors)'))
edit('value==sports_care_current_compiled)','value==sports_care_current_compiled or value==night_current_compiled)')
edit('\tif value==sports_care_current_compiled: value=moss_current_compiled','\tif value==night_current_compiled: value=sports_care_current_compiled\n\tif value==sports_care_current_compiled: value=moss_current_compiled')
edit('\t_upper_hull_validate_runtime(floors.get_parent().get_parent())','\t_night_validate_runtime(floors.get_parent().get_parent())\n\t_upper_hull_validate_runtime(floors.get_parent().get_parent())')
block=(R/'night_guard_block.gd').read_text().replace('static func _night_current_sha256(path:String)->String:\n','static func _night_current_sha256(path:String)->String:\n\t_night_ensure()\n')
s+=block
ship=(G/spath).read_text();before='\tlighting_budget.configure(self,player)';after='\tload("res://scripts/night_table_receiving.gd").build(self)\n'+before;assert ship.count(before)==1;ship=ship.replace(before,after)
for path,text in [(gpath,s),(spath,ship)]:p=C/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
layout=json.loads((C/'data/spatial_layout.json').read_text());compiled=json.loads((C/'data/generated/structural_meshes.json').read_text())
p=dict(schema=1,predecessors=ctx['predecessors'],added_layout=layout['regions'][-2:],added_compiled=compiled['regions'][-2:],inverse_edits={gpath:edits,spath:[dict(before=before,after=after,count=1)],'tools/compile_layout.py':ctx['compiler_inverse_edits']},block_normalized_sha256=hashlib.sha256(block.encode()).hexdigest(),current_sha256={})
paths=[spath,'data/spatial_layout.json','data/generated/structural_meshes.json','docs/LAYOUT_COMPILE_CHECKS.json','tools/compile_layout.py','tools/night_table_incremental_preservation.py','data/architecture/packages/night_table/NIGHT_TABLE_COMPILER_PROOF.json']
paths += [str(f.relative_to(C)) for f in (C/'data/architecture/night_table').rglob('*') if f.is_file()]
paths += [str(f.relative_to(C)) for f in (C/'assets/material_textures/night_table').rglob('*') if f.is_file()]
paths += ['scripts/night_table_receiving.gd','shaders/night_table_receiving_finish.gdshader','assets/models/WP12_night_table_runtime_names001.glb']
p['current_sha256']={f:sha(C/f)for f in paths};q=C/'data/architecture/packages/night_table/RUNTIME_PROOF.json';q.write_text(json.dumps(p,indent=2)+'\n');s=s.replace('const NIGHT_PROOF_SHA="<PROOF_SHA>"','const NIGHT_PROOF_SHA="'+sha(q)+'"');(C/gpath).write_text(s)
# Mechanically verify every whole-file inverse before any engine test.
for path,es in p['inverse_edits'].items():
 text=(C/path).read_text()
 if path==gpath:
  a=text.index('# NIGHT_TABLE_EXACT_SECTION_BEGIN');text=text[:a]
 for e in es:assert text.count(e['after'])==e['count'],(path,e['after'][:100],text.count(e['after']));text=text.replace(e['after'],e['before'])
 assert text==(C/p['predecessors'][path]['retained_path']).read_text(),path
print('Prepared staged guard and exact whole-file inverse proofs. No live files changed.')
