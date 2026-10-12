"""Small exact-base source fixture, without importing the full production project."""
import hashlib,json,pathlib,shutil,sys
ROOT=pathlib.Path(__file__).resolve().parents[3]
P=pathlib.Path(__file__).resolve().parent
dest=pathlib.Path(sys.argv[1]);assert not dest.exists();dest.mkdir()
(dest/'project.godot').write_text('config_version=5\n[application]\nconfig/name="Group2 unplaced VIP source QA"\nconfig/features=PackedStringArray("4.6", "GL Compatibility")\n[rendering]\nrenderer/rendering_method="gl_compatibility"\n')
files=['scripts/player.gd','scripts/static_contact_cache.gd','scripts/service_door.gd',
 'scripts/guest_privacy_door.gd','scripts/lighting_budget.gd','assets/models/AST-DOR-001.glb',
 'scripts/group2_vip_pavilions/privacy_door.gd','scripts/group2_vip_pavilions/package.gd',
 'data/group2_vip_pavilions/KITS_r003.json','tests/group2_vip_pavilions/validate_source.gd',
 'assets/group2_vip_pavilions/VIP_TIDAL_r003.glb','assets/group2_vip_pavilions/VIP_QUIET_r003.glb']
rows=[]
for rel in files:
 target=dest/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/'Game'/rel,target)
 rows.append({'path':'Game/'+rel,'sha256':hashlib.sha256(target.read_bytes()).hexdigest()})
(dest/'artifacts').mkdir();(dest/'artifacts/FIXTURE_EXACT_INPUTS.json').write_text(json.dumps(rows,indent=2)+'\n')
print('Fresh isolated VIP fixture exact files',len(files))
