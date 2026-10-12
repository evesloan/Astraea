"""Fresh exact-source five-suite Godot fixture; no full-project import churn."""
import pathlib, shutil, sys
ROOT=pathlib.Path(__file__).resolve().parents[3]
dest=pathlib.Path(sys.argv[1]);assert not dest.exists();dest.mkdir()
(dest/'project.godot').write_text('config_version=5\n[application]\nconfig/name="Group2 private vertical source QA"\nconfig/features=PackedStringArray("4.6", "GL Compatibility")\n[rendering]\nrenderer/rendering_method="gl_compatibility"\n')
files=['scripts/commons_lift.gd','scripts/lift_gate.gd','scripts/lift_button.gd','scripts/player.gd',
       'scripts/static_contact_cache.gd','scripts/guest_entry_door.gd','scripts/guest_privacy_door.gd',
       'scripts/service_door.gd','scripts/d04_court_service_visit.gd','scripts/lighting_budget.gd',
       'shaders/hospitality_glass.gdshader','assets/models/AST-CIR-003.glb','assets/models/AST-DOR-003.glb',
       'data/group2_completion/FLOOR_INTERFACE.json','data/group2_private_vertical/INTERFACES.json',
       'data/group2_private_vertical/CONVERSATION_INTERFACE.json',
       'scripts/group2_private_vertical/package.gd','scripts/group2_private_vertical/moving_lift.gd',
       'tests/group2_private_vertical/validate_source.gd','tests/group2_private_vertical/validate_conversation.gd',
       'tests/group2_private_vertical/validate_lighting.gd']
files += [str(p.relative_to(ROOT/'Game'))for p in (ROOT/'Game/scripts/group2_completion').glob('*.gd')]
for key in ['787','792','794','795','797']:
    files += ['assets/group2_completion/'+key+'.glb','data/group2_completion/contracts/'+key+'.json',
              'assets/group2_private_vertical/PIT_'+key+'_r001.glb',
              'assets/group2_private_vertical/CONVERSATION_'+key+'_r001.glb']
for rel in files:
    target=dest/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/'Game'/rel,target)
(dest/'artifacts').mkdir()
print('Fresh private-vertical fixture exact files',len(files))
