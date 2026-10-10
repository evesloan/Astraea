"""Preserve completed isolated attempts, then repair proven cabin-header overlap.

Wait outside the heavy mutex for this worker's current review/build to finish.
Never interrupts another process or replaces an accepted source.
"""
import pathlib,json,sys,subprocess,time,os,shutil
R=pathlib.Path(__file__).resolve().parent
for unit,tier,recipe in [(792,'royalty','build_royalty.py'),(787,'supreme','build_supreme.py')]:
 O=R/'sections'/f'{unit}_{tier}';p=R/recipe
 while True:
  cp=O/'SECTION_CONTRACT.json'
  if cp.exists():
   c=json.loads(cp.read_text())
   if tier=='royalty':ready=c.get('review_view_rebuild',{}).get('script')=='review_multilevel_views.py'
   else:ready=(R/'supreme_787_build03.log').read_text(errors='replace').rstrip().endswith('Blender quit')
   if ready:break
  time.sleep(2)
 assert c['status']!='BOUNDED_FIT_VERIFIED_EDITABLE_SOURCE_CANDIDATE'
 B=R/'failed_source_attempts'/f'{unit}_actual_cabin_header_overlap_preserved';B.mkdir(exist_ok=False)
 # Verify both final absolute move targets stay in this worker's own lane.
 assert O.resolve().is_relative_to(R) and (B/'old_source').resolve().is_relative_to(R)
 shutil.copy2(p,B/p.name);os.rename(O,B/'old_source')
 s=p.read_text()
 if tier=='royalty':
  assert '-0.14000000000000057,0.019999999999999574' in s
  s=s.replace('-0.14000000000000057,0.019999999999999574','-.16,-.02')
  s=s.replace("('main_programme',(11.0,6.6,1.65),(15.0,10.2,3.2))","('main_programme',(11.4,8.1,1.65),(15.0,10.2,1.0))")
 else:
  assert ',15.86,16.02,' in s;s=s.replace(',15.86,16.02,',',15.84,15.98,')
 s=s.replace("('sleeping_second',(13.3,16.3,6.15),(15.6,19.2,5.6))","('sleeping_second',frame.inverse(frame.rigid(15.6,19.2,.45,-3.15,6.15)),frame.inverse(frame.rigid(15.6,19.2,0,.7,5.35)))")
 compile(s,str(p),'exec');p.write_text(s)
 print('Preserved and repaired actual header overlap',unit,flush=True)
 with (R/f'{tier}_{unit}_header_repair_build.log').open('w',encoding='utf8') as f:
  result=subprocess.run([sys.executable,str(R/'heavy.py'),str(p),str(unit)],stdout=f,stderr=subprocess.STDOUT)
 if result.returncode:raise RuntimeError('Source rebuild failed; evidence preserved '+str(unit))
 subprocess.run([sys.executable,str(R/'verify_private_levels.py'),str(unit)],check=True)
 print('Independent private-level source QA passed; actual pixels pending',unit,flush=True)
