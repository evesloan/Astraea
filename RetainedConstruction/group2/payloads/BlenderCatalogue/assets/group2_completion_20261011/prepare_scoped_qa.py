"""Fresh minimal Godot4.6.3 fixture using exact current production dependencies."""
import argparse, pathlib, shutil
ROOT = pathlib.Path(__file__).resolve().parents[3]
parser = argparse.ArgumentParser()
parser.add_argument('destination', type=pathlib.Path)
parser.add_argument('--smoke', action='store_true')
args = parser.parse_args()
dest = args.destination
assert not dest.exists(), 'Use a new QA revision directory; preserve failed attempts'
dest.mkdir()
(dest / 'project.godot').write_text('config_version=5\n[application]\nconfig/name="Astraea Group2 scoped construction QA"\nconfig/features=PackedStringArray("4.6", "GL Compatibility")\n[rendering]\nrenderer/rendering_method="gl_compatibility"\n')
files = ['scripts/guest_entry_door.gd', 'scripts/guest_privacy_door.gd', 'scripts/service_door.gd',
         'scripts/static_contact_cache.gd', 'scripts/lighting_budget.gd', 'scripts/d04_court_service_visit.gd',
         'scripts/player.gd', 'data/group2_completion/FLOOR_INTERFACE.json',
         'tests/group2_completion/validate_package.gd', 'tests/group2_completion/validate_interaction.gd',
         'tests/group2_completion/validate_lighting.gd']
files += [str(f.relative_to(ROOT / 'Game')) for f in (ROOT / 'Game/scripts/group2_completion').glob('*.gd')]
if (ROOT / 'Game/data/group2_completion/LIGHTING_ADDENDUM.json').exists():
    files.append('data/group2_completion/LIGHTING_ADDENDUM.json')
keys = ['780', '781', '787', '792'] if args.smoke else [f.stem for f in (ROOT / 'Game/data/group2_completion/contracts').glob('*.json')]
for key in keys:
    files.extend([f'assets/group2_completion/{key}.glb', f'data/group2_completion/contracts/{key}.json'])
for rel in files:
    path = dest / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / 'Game' / rel, path)
(dest / 'artifacts').mkdir()
print('Scoped QA exact files', len(files), 'sections', len(keys))
