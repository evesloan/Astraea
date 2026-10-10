"""Preserve the dim pilot, add supported care lighting, build fixed six adjuncts."""
import pathlib,json,sys,subprocess,time,os,shutil
R=pathlib.Path(__file__).resolve().parent;p=R/'build_house_adjunct.py'
while not (R/'facility_PF_text.log').read_text(errors='replace').rstrip().endswith('Blender quit'):time.sleep(2)
B=R/'failed_source_attempts/port_forward_adjunct_service_light_attempt02';B.mkdir(exist_ok=False);O=R/'facilities/port_forward_upper_house'
assert O.resolve().is_relative_to(R) and (B/'old_source').resolve().is_relative_to(R)
shutil.copy2(p,B/p.name);os.rename(O,B/'old_source');s=p.read_text()
s=s.replace("box('CareCleanClosedInset',.44,.46,length-2.24,length-1.45,.15,1.65,'teal_weave','care_service')", "box('CareCleanClosedInset',.46,1.44,length-2.315,length-2.30,.97,1.65,'teal_weave','care_service')")
s=s.replace("box('CareUsedReturnInset',.44,.46,length-1.35,length-.50,.15,1.65,'dark_rubber','care_service')", "box('CareUsedReturnInset',.46,1.44,length-2.315,length-2.30,.15,.90,'dark_rubber','care_service')")
addition="""# A cool task fixture bears on the care backing; no unsupported light geometry.
box('CareTaskBacking',.45,2.45,length-.40,length-.25,0,2.60,'ivory_enamel','care_service')
box('CareTaskArm',1.80,2.20,length-1.40,length-.25,2.30,2.40,'champagne_metal','fixture')
box('CareTaskLens',1.65,2.35,length-1.50,length-.90,2.22,2.32,'lens','fixture')
data=bpy.data.lights.new('CareTaskLight','AREA');data.energy=210;data.color=(.70,.85,1.0);data.size=1.6;ob=bpy.data.objects.new('CareTaskLight',data);scene.collection.objects.link(ob);ob.location=xyz(2.0,length-1.20,2.20)
"""
s=s.replace('# Built-in reading provision',addition+'# Built-in reading provision')
s=s.replace("('care_threshold',(3.8,length-3.2,1.65),(1.0,length-1.1,1.1))", "('care_threshold',(3.8,length-3.2,1.65),(1.45,length-2.1,1.1))")
compile(s,str(p),'exec');p.write_text(s)
for row in json.loads((R/'EXCLUSIVE_FACILITIES_CROSSWALK.json').read_text())['source_proposals']:
 house=row['house'];O=R/'facilities'/house
 assert not (O/'house_adjunct.blend').exists(),'Existing adjunct source must be preserved explicitly'
 print('Sequential private adjunct',house,flush=True)
 for script,suffix in [('build_house_adjunct.py','build'),('verify_house_text.py','text')]:
  with (R/f'facility_{house}_{suffix}.log').open('w',encoding='utf8') as f:result=subprocess.run([sys.executable,str(R/'heavy.py'),str(R/script),house],stdout=f,stderr=subprocess.STDOUT)
  if result.returncode:raise RuntimeError('Preserved facility failure '+house+' '+script)
 print('Native/export/text source QA passed; actual pixels pending',house,flush=True)
