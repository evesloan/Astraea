from pathlib import Path
import json,hashlib,re
R=Path('/workspace/Astraea-recovered-e6274e77-20261021');G=R/'Game';P=G/'family_enclosure_finish_20261022';S=G/'scripts/family_enclosure_integration_20261022';checks=0
for name in ['bootstrap.gd','launcher.gd','presentation.gd']:
 original=(G/'scripts/family_specialty_integration_20261022'/name).read_text();new=(S/name).read_text();assert new==original.replace('family_specialty_20261022','family_enclosure_20261022');checks+=1
for name in ['bootstrap','launcher','main','ship']:
 original=(G/f'scenes/{name}_family_specialty_20261022.tscn').read_text();new=(G/f'scenes/{name}_family_enclosure_20261022.tscn').read_text();assert new==original.replace('family_specialty_integration_20261022','family_enclosure_integration_20261022');checks+=1
 for resource in re.findall(r'path="res://([^"]+)"',new):assert (G/resource).is_file();checks+=1
assert 'family_specialty_integration_20261022/ship.gd' in (S/'ship.gd').read_text();checks+=1
capture=json.loads((P/'evidence/CAPTURE.json').read_text());assert capture['status']=='PASS' and all(x['pass']for x in capture['focused_checks']);assert capture['active_lights']<=8;assert capture['power_off_pass'];checks+=3
assert 'run/main_scene="res://scenes/bootstrap_family_enclosure_20261022.tscn"'in(G/'project.godot').read_text();checks+=1
receipt={'status':'PASS','checks':checks,'menu_settings_bootstrap_behavior_preserved':True,'named_main_selected':True,'bounded_ship_hook_tested':True,'whole_ship_launch_tested':False,'fixed_laptop_package_changed':False};(P/'evidence/INTEGRATION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(receipt)
