import pathlib,sys,shutil
ROOT=pathlib.Path(__file__).resolve().parents[3];dest=pathlib.Path(sys.argv[1]);assert not dest.exists();dest.mkdir()
(dest/'project.godot').write_text('config_version=5\n[application]\nconfig/name="Group2 actual Family Terrace source QA"\nconfig/features=PackedStringArray("4.6", "GL Compatibility")\n[rendering]\nrenderer/rendering_method="gl_compatibility"\n')
files=['scripts/player.gd','scripts/static_contact_cache.gd','scripts/service_door.gd','scripts/guest_entry_door.gd','scripts/lighting_budget.gd','scripts/group2_family_childcare/entry.gd','scripts/group2_family_childcare/package.gd','tests/group2_family_childcare/validate_source.gd','assets/models/AST-DOR-002_wide.glb','assets/models/FAMILY_TERRACE_ARCHITECTURE_lift_r003.glb','assets/group2_family_childcare/FAMILY_CHILDCARE_r001.glb','data/group2_family_childcare/COMPONENT_r001.json']
for rel in files:
 p=dest/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/'Game'/rel,p)
(dest/'artifacts').mkdir();print('Fresh actual-receiver childcare fixture',len(files),'exact files')
