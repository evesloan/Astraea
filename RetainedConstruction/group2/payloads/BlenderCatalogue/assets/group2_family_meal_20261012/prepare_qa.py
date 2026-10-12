import pathlib,sys,shutil
ROOT=pathlib.Path(__file__).resolve().parents[3];dest=pathlib.Path(sys.argv[1]);assert not dest.exists();dest.mkdir()
(dest/'project.godot').write_text('config_version=5\n[application]\nconfig/name="Group2 actual Family meal source QA"\nconfig/features=PackedStringArray("4.6", "GL Compatibility")\n[rendering]\nrenderer/rendering_method="gl_compatibility"\n')
files=['scripts/static_contact_cache.gd','scripts/group2_family_meal/package.gd','tests/group2_family_meal/validate_source.gd','assets/models/FAMILY_TERRACE_ARCHITECTURE_lift_r003.glb','assets/group2_family_meal/FAMILY_MEAL_FITTINGS_r001.glb','data/group2_family_meal/COMPONENT_r001.json']
for rel in files:
 p=dest/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/'Game'/rel,p)
(dest/'artifacts').mkdir();print('Fresh exact meal fixture',len(files),'files')
