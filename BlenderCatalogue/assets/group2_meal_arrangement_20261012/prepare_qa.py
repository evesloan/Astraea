import pathlib,json,sys,shutil
ROOT=pathlib.Path(__file__).resolve().parents[3];dest=pathlib.Path(sys.argv[1]);assert not dest.exists();dest.mkdir()
(dest/'project.godot').write_text('config_version=5\n[application]\nconfig/name="Group2 corrected meal arrangement source QA"\nconfig/features=PackedStringArray("4.6", "GL Compatibility")\n[rendering]\nrenderer/rendering_method="gl_compatibility"\n')
receiving=json.loads((ROOT/'Game/data/architecture/FAMILY_TERRACE_RECEIVING.json').read_text())
files=['scripts/static_contact_cache.gd','scripts/family_terrace_receiving.gd','scripts/group2_family_meal/package.gd','scripts/group2_meal_arrangement/pose_successor.gd','tests/group2_meal_arrangement/validate_arrangement.gd','data/architecture/FAMILY_TERRACE_RECEIVING.json','data/group2_meal_arrangement/CHAIR_POSE_SUCCESSOR.json','assets/models/'+receiving['model_file'],'assets/group2_family_meal/FAMILY_MEAL_FITTINGS_r001.glb']
files+=['assets/models/'+d['model_file']for d in receiving['retained_asset_definitions'].values()]
for rel in files:
 p=dest/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/'Game'/rel,p)
(dest/'artifacts').mkdir();print('Fresh actual full157-prop Family receiver fixture',len(files),'files')
