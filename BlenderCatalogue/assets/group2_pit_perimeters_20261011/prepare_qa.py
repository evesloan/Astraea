"""Fresh scoped pit fixture; retained sources and previous rear ramps are exact."""
import pathlib,sys,subprocess,shutil
ROOT=pathlib.Path(__file__).resolve().parents[3];P=pathlib.Path(__file__).resolve().parent
dest=pathlib.Path(sys.argv[1]);assert not dest.exists()
subprocess.run([sys.executable,str(ROOT/'BlenderCatalogue/assets/group2_private_vertical_20261011/prepare_qa.py'),str(dest)],check=True)
files=['scripts/group2_pit_perimeters/package.gd','tests/group2_pit_perimeters/validate_changed_work.gd',
       'data/group2_pit_perimeters/PLAN_r003.json']
files += [f'assets/group2_pit_perimeters/PERIMETER_{key}_r003.glb'for key in ['787','792','794','795','797']]
for rel in files:
 target=dest/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/'Game'/rel,target)
print('Added focused pit fixture files',len(files))
