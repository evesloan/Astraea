import pathlib,sys,shutil
ROOT=pathlib.Path(__file__).resolve().parents[3];dest=pathlib.Path(sys.argv[1]);assert not dest.exists();dest.mkdir()
(dest/'project.godot').write_text('config_version=5\n[application]\nconfig/name="Group2 actual garden quiet source QA"\nconfig/features=PackedStringArray("4.6", "GL Compatibility")\n[rendering]\nrenderer/rendering_method="gl_compatibility"\n')
files=['scripts/player.gd','scripts/static_contact_cache.gd','scripts/lighting_budget.gd','scripts/group2_garden_quiet/package.gd','tests/group2_garden_quiet/validate_source.gd','assets/models/FAMILY_TERRACE_ARCHITECTURE_lift_r003.glb','assets/models/QUIET_GROVE_ARCHITECTURE_lift_r003.glb','assets/group2_garden_quiet/family_hydroponics_r002.glb','assets/group2_garden_quiet/quiet_meditation_r002.glb','data/group2_garden_quiet/COMPONENTS_r002.json']
for rel in files:
 p=dest/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/'Game'/rel,p)
(dest/'artifacts').mkdir();print('Fresh exact garden/quiet fixture',len(files),'files')
