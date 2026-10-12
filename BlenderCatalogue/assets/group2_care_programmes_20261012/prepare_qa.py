import hashlib,json,pathlib,shutil,sys
ROOT=pathlib.Path(__file__).resolve().parents[3];dest=pathlib.Path(sys.argv[1]);assert not dest.exists();dest.mkdir()
(dest/'project.godot').write_text('config_version=5\n[application]\nconfig/name="Group2 care source QA"\nconfig/features=PackedStringArray("4.6", "GL Compatibility")\n[rendering]\nrenderer/rendering_method="gl_compatibility"\n')
files=['scripts/player.gd','scripts/static_contact_cache.gd','scripts/service_door.gd','scripts/guest_entry_door.gd','scripts/guest_privacy_door.gd','scripts/d04_court_service_visit.gd','scripts/group2_care_programmes/package.gd','tests/group2_care_programmes/validate_source.gd','data/group2_care_programmes/FITTINGS_r001.json','data/group2_completion/FLOOR_INTERFACE.json']
files+=[str(p.relative_to(ROOT/'Game'))for p in (ROOT/'Game/scripts/group2_completion').glob('*.gd')]
data=json.loads((ROOT/'Game/data/group2_care_programmes/FITTINGS_r001.json').read_text())
for row in data['rows']:
 k=row['key'];files += [f'assets/group2_completion/{k}.glb',f'data/group2_completion/contracts/{k}.json',f'assets/group2_care_programmes/CARE_{k}_r001.glb']
for rel in files:
 p=dest/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/'Game'/rel,p)
(dest/'artifacts').mkdir();print('Fresh six-adjunct fixture',len(files),'exact files')
