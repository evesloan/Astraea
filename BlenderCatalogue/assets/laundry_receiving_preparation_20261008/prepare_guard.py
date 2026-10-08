from pathlib import Path
import json,hashlib,shutil
R=Path(__file__).resolve().parent;C=R/'compiler_candidate';ctx=json.loads((C/'data/architecture/packages/laundry/BUILD_CONTEXT.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for p in (R/'runtime_candidate').rglob('*'):
 if p.is_file()and '.godot'not in p.parts:
  q=C/p.relative_to(R/'runtime_candidate');q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q)
gpath='tests/medical_triage_successor_guard.gd';spath='scripts/ship.gd';s=(C/ctx['predecessors'][gpath]['retained_path']).read_text();edits=[]
def edit(before,after,count=1):
 global s
 assert s.count(before)==count,(before[:90],s.count(before));s=s.replace(before,after);edits.insert(0,dict(before=before,after=after,count=count))
# Only the immediate outer source layer and exact new-floor projection change.
a=s.index('# NIGHT_TABLE_EXACT_SECTION_BEGIN');part=s[a:];new=part
new=new.replace('FileAccess.get_sha256("res://"+str(path))','_laundry_current_sha256("res://"+str(path))').replace('FileAccess.get_file_as_string("res://"+str(path))','_laundry_current_text("res://"+str(path))')
for p in ['data/spatial_layout.json','data/generated/structural_meshes.json','docs/LAYOUT_COMPILE_CHECKS.json']:
 new=new.replace('FileAccess.get_file_as_string("res://'+p+'")','_laundry_current_text("res://'+p+'")')
new=new.replace('else FileAccess.get_file_as_string(path)','else _laundry_current_text(path)').replace('else FileAccess.get_sha256(path)','else _laundry_current_sha256(path)')
new=new.replace('assert(floors!=null and floors.get_child_count()==284)','assert(floors!=null and floors.get_child_count()==286)').replace('var children:=floors.get_children();var retained:Array=[]','var children:=_laundry_floor_children(floors);var retained:Array=[]')
edit(part,new)
edit('value==night_current_compiled)','value==night_current_compiled or value==laundry_current_compiled)')
edit('\tif value==night_current_compiled: value=sports_care_current_compiled','\tif value==laundry_current_compiled: value=night_current_compiled\n\tif value==night_current_compiled: value=sports_care_current_compiled')
edit('\t_night_validate_runtime(floors.get_parent().get_parent())','\t_laundry_validate_runtime(floors.get_parent().get_parent())\n\t_night_validate_runtime(floors.get_parent().get_parent())')
block=Path('/workspace/scratch/375c2e438292/night_table_receiving_20261008/night_guard_block.gd').read_text().replace('NIGHT_TABLE','LAUNDRY').replace('NIGHT_PROOF','LAUNDRY_PROOF').replace('night_table','laundry').replace('night_','laundry_').replace('_night','_laundry').replace('Night Table','Laundry').replace('NightTableSource','LaundrySource').replace('Vector3(-31,61,216)','Vector3.ZERO').replace('root.get_meta("source_dining_places")==240 and ','')
block=block.replace('==284','==286').replace('==282','==284').replace('i<282','i<284')
block=block.replace('static func _laundry_current_sha256(path:String)->String:\n','static func _laundry_current_sha256(path:String)->String:\n\t_laundry_ensure()\n')
s+=block
ship=(C/ctx['predecessors'][spath]['retained_path']).read_text();before='\tlighting_budget.configure(self,player)';after='\tload("res://scripts/laundry_receiving.gd").build(self)\n'+before;assert ship.count(before)==1;ship=ship.replace(before,after)
for path,text in [(gpath,s),(spath,ship)]:p=C/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
layout=json.loads((C/'data/spatial_layout.json').read_text());compiled=json.loads((C/'data/generated/structural_meshes.json').read_text());p=dict(schema=1,predecessors=ctx['predecessors'],added_layout=layout['regions'][-2:],added_compiled=compiled['regions'][-2:],inverse_edits={gpath:edits,spath:[dict(before=before,after=after,count=1)],'tools/compile_layout.py':ctx['compiler_inverse_edits']},block_normalized_sha256=hashlib.sha256(block.encode()).hexdigest(),current_sha256={})
paths=[spath,'data/spatial_layout.json','data/generated/structural_meshes.json','docs/LAYOUT_COMPILE_CHECKS.json','tools/compile_layout.py','tools/laundry_incremental_preservation.py','data/architecture/packages/laundry/LAUNDRY_COMPILER_PROOF.json']
for directory in ['data/architecture/laundry','assets/material_textures/laundry']:paths +=[str(f.relative_to(C))for f in (C/directory).rglob('*')if f.is_file()]
paths+=['scripts/laundry_receiving.gd','shaders/laundry_receiving_finish.gdshader','assets/models/WP08_laundry_runtime_names001.glb'];p['current_sha256']={f:sha(C/f)for f in paths};q=C/'data/architecture/packages/laundry/RUNTIME_PROOF.json';q.write_text(json.dumps(p,indent=2)+'\n');s=s.replace('const LAUNDRY_PROOF_SHA="<PROOF_SHA>"','const LAUNDRY_PROOF_SHA="'+sha(q)+'"');(C/gpath).write_text(s)
for path,es in p['inverse_edits'].items():
 text=(C/path).read_text()
 if path==gpath:text=text[:text.index('# LAUNDRY_EXACT_SECTION_BEGIN')]
 for e in es:assert text.count(e['after'])==e['count'],path;text=text.replace(e['after'],e['before'])
 assert text==(C/p['predecessors'][path]['retained_path']).read_text(),path
print('Laundry whole predecessor inverse source proofs pass in isolated staging')
