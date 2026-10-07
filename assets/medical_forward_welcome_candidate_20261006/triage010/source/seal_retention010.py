"""Seal the completed source-only payload. Does not write Catalogue or Game."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert json.loads((R/'qa/RENDER_RECEIPT_010_clinical_cross.json').read_text())['unchanged']
receipt=json.loads((R/'qa/RENDER_RECEIPT_010_clinical_cross.json').read_text());assert len(receipt['views'])==4
assert 'Blender quit' in (R/'qa/render010.log').read_text()
assert 'Blender quit' in (R/'qa/render010_room_angles.log').read_text()
second=json.loads((R/'qa/RENDER_RECEIPT_010_whole_room.json').read_text());assert second['unchanged'] and len(second['views'])==2
files=[
'source/D05_medical_connected_triage_010.blend','exports/D05_medical_connected_architecture_010.glb',
'source/build_triage_wing010.py','source/build_triage_wing.py','source/source_helpers.py','source/check_loaded_wing.py','source/check_native_export.py','source/check_predecessor_preservation.py','source/render_triage.py','source/render_triage_room_angles.py','source/draw_plan.py','source/seal_retention010.py',
'qa/INPUT_PINS.json','qa/INDEPENDENT_BASE_SOURCE.json','qa/INDEPENDENT_INPUTS_010.json','qa/REFERENCE_APPLICATION.json','qa/UNBUILT_TRIAGE_ARRANGEMENT_PROPOSAL.json','qa/PLAN_SCREEN.json','qa/FLOOR_OWNER_PROPOSAL_010.json','qa/SOURCE_MANIFEST_010.json','qa/LOADED_SOURCE_FIT_010.json','qa/NATIVE_EXPORT_010.json','qa/PREDECESSOR_PRESERVATION_010.json','qa/RENDER_RECEIPT_010_clinical_cross.json','qa/PLAN_DRAWING_010.json','qa/SOURCE_HANDOFF_010.md','qa/build010.log','qa/render010.log','qa/render010_room_angles.log','qa/RENDER_RECEIPT_010_whole_room.json',
'qa/LOADED_SOURCE_FIT_009.json','qa/build009.log','qa/check_loaded_wing_009_used.py',
'renders/010_declared_plan_source_proposal.png','renders/010_clinical_cross_source_only.png','renders/010_triage_room_source_only.png','renders/010_work_edge_source_only.png','renders/010_arrival_link_source_only.png','renders/010_whole_room_source_only.png','renders/010_documentation_edge_source_only.png']
rows=[]
for rel in files:
 p=R/rel;assert p.is_file()and not p.is_symlink(),rel
 rows.append({'relative_path':rel,'source':str(p),'sha256':sha(p),'bytes':p.stat().st_size})
m={'schema':1,'scope':'New-only retention of uninstalled connected medical triage source010; no Game, plan, floor, core, registry or runtime adoption','destination':'assets/medical_forward_welcome_candidate_20261006/triage010','payload_files':len(rows),'payload_bytes':sum(x['bytes']for x in rows),'files':rows,'protected_inputs':json.loads((R/'qa/INDEPENDENT_INPUTS_010.json').read_text()),'predecessor_retained_path':'assets/medical_forward_welcome_candidate_20261006/finish008','retained_existing_work_unchanged':True,'capacity_accepted':False,'clinical_operation_accepted':False,'runtime_adopted':False}
p=R/'RETENTION_MANIFEST_010.json';assert not p.exists();p.write_text(json.dumps(m,indent=2)+'\n');print('SEALED_SOURCE010_RETENTION',len(rows),m['payload_bytes'],sha(p))
