from pathlib import Path
import shutil,hashlib,re,subprocess,json
R=Path('/workspace/Astraea');E=Path('/workspace/quiet-d16-integration');D=R/'BlenderCatalogue/assets/quiet_d16_staff_receiving_20261016'
assert json.loads((E/'CANDIDATE.json').read_text())['status']=='PASS'
f='QUIET_D16_STAFF_RECEIVING_r001.glb';dest=R/'Game/assets/quiet_d16_receiving_20261016';dest.mkdir(exist_ok=True);assert not (dest/f).exists();shutil.copy2(D/f,dest/f)
s=(R/'Game/assets/quiet_d15_receiving_20261016/QUIET_D15_STAFF_RECEIVING_r004.glb.import').read_text();s=re.sub(r'^uid=.*\n','',s,flags=re.M);s=s.replace('quiet_d15_receiving','quiet_d16_receiving').replace('QUIET_D15_STAFF_RECEIVING_r004.glb',f);md5=hashlib.md5(('res://assets/quiet_d16_receiving_20261016/'+f).encode()).hexdigest();s=s.replace('3a29c57686218dc1fdd7ca47676294df',md5);(dest/(f+'.import')).write_text(s)
p=R/'Game/project.godot';original=p.read_bytes();assert hashlib.sha256(original).hexdigest()=='42dfd175fd8135e51094d66347802a51f6622475a06b4b2c11227af29884bdc0'
try:
 p.write_bytes(original+b'\n[filesystem]\nimport/blender/enabled=false\n')
 with (E/'import.log').open('w') as log:result=subprocess.run(['godot','--headless','--editor','--path','Game','--import'],cwd=R,stdout=log,stderr=subprocess.STDOUT)
 assert result.returncode==0,result.returncode
finally:p.write_bytes(original)
p=R/'Game/scripts/ship.gd';s=p.read_text();needle='\tload("res://scripts/quiet_d13_receiving_20261016/package.gd").build(self)';assert s.count(needle)==1;assert 'quiet_d16_receiving_20261016' not in s;p.write_text(s.replace(needle,needle+'\n\t# D16 adds its separate bounded native lobby opening.\n\tload("res://scripts/quiet_d16_receiving_20261016/package.gd").build(self)'))
print('Imported and hooked D16 after protected D14/D15; original project settings restored.')
