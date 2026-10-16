from pathlib import Path
import shutil,hashlib,re,subprocess,json
R=Path('/workspace/Astraea');E=Path('/workspace/family-d14-integration');D=R/'BlenderCatalogue/assets/family_d14_staff_receiving_20261016'
assert json.loads((E/'CANDIDATE.json').read_text())['status']=='PASS'
f='FAMILY_D14_STAFF_RECEIVING_r001.glb';dest=R/'Game/assets/family_d14_receiving_20261016';dest.mkdir(exist_ok=True);assert not (dest/f).exists();shutil.copy2(D/f,dest/f)
s=(R/'Game/assets/quiet_d15_receiving_20261016/QUIET_D15_STAFF_RECEIVING_r004.glb.import').read_text();s=re.sub(r'^uid=.*\n','',s,flags=re.M);s=s.replace('quiet_d15_receiving','family_d14_receiving').replace('QUIET_D15_STAFF_RECEIVING_r004.glb',f);md5=hashlib.md5(('res://assets/family_d14_receiving_20261016/'+f).encode()).hexdigest();s=s.replace('3a29c57686218dc1fdd7ca47676294df',md5);(dest/(f+'.import')).write_text(s)
p=R/'Game/project.godot';original=p.read_bytes();assert hashlib.sha256(original).hexdigest()=='42dfd175fd8135e51094d66347802a51f6622475a06b4b2c11227af29884bdc0'
try:
 p.write_bytes(original+b'\n[filesystem]\nimport/blender/enabled=false\n')
 with (E/'import.log').open('w') as log:result=subprocess.run(['godot','--headless','--editor','--path','Game','--import'],cwd=R,stdout=log,stderr=subprocess.STDOUT)
 assert result.returncode==0,result.returncode
finally:p.write_bytes(original)
p=R/'Game/scripts/ship.gd';s=p.read_text();needle='\tload("res://scripts/family_d13_receiving_20261016/package.gd").build(self)';assert s.count(needle)==1;assert 'family_d14_receiving_20261016' not in s;p.write_text(s.replace(needle,needle+'\n\t# Family D14 joins the existing aft staff lobby opening.\n\tload("res://scripts/family_d14_receiving_20261016/package.gd").build(self)'))
print('Imported and hooked Family D14 after protected Quiet Grove D13–D16; original project settings restored.')
