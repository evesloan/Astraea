"""Package and publish only explicitly already reviewed source sections, sequentially."""
import pathlib,json,subprocess,sys
R=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(R));from source_paths import section
for unit in map(int,sys.argv[1:]):
 row,o,native,export=section(unit)
 assert (o/'PIXEL_REVIEW.json').exists(),'Actual visual review required before delivery'
 archive=R/'deliveries'/f'Group2C_D17_{unit}_{row["reservation"]["tier"].title()}_source_r001.zip'
 if not archive.exists():subprocess.run([sys.executable,str(R/'package_luxury.py'),str(unit)],check=True)
 receipt=R/(archive.stem+'_REMOTE_RECEIPT.json')
 if receipt.exists():print('Existing independently retained delivery preserved',unit,flush=True);continue
 print('Publishing isolated verified source milestone',unit,flush=True)
 subprocess.run([sys.executable,str(R/'publish_luxury.py'),str(archive)],check=True)
