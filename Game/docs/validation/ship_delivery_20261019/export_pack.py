from pathlib import Path
import subprocess,hashlib,json,shutil
R=Path('/workspace/Astraea');E=Path('/workspace/ship-delivery-20261019');D=E/'Astraea-Integrated-Construction';D.mkdir(exist_ok=True)
assert json.loads((E/'SCENE_INCLUSION.json').read_text())['status']=='PASS'
assert shutil.disk_usage(E).free>10*1024**3
p=R/'Game/project.godot';old=p.read_bytes();assert hashlib.sha256(old).hexdigest()=='42dfd175fd8135e51094d66347802a51f6622475a06b4b2c11227af29884bdc0'
try:
 p.write_bytes(old+b'\n[filesystem]\nimport/blender/enabled=false\n')
 with (E/'export.log').open('w')as log:
  result=subprocess.run(['godot','--headless','--path','Game','--export-pack','Integrated Construction Package',str(D/'Astraea.pck')],cwd=R,stdout=log,stderr=subprocess.STDOUT)
 assert result.returncode==0,result.returncode
finally:p.write_bytes(old)
print('Export complete', (D/'Astraea.pck').stat().st_size)
