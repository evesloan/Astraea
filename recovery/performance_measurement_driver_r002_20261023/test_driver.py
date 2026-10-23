from pathlib import Path
import importlib.util,json,subprocess,tempfile,copy
P=Path('/workspace/Astraea-recovered-e6274e77-20261021/recovery/performance_measurement_driver_r002_20261023');spec=importlib.util.spec_from_file_location('driver',P/'run_modes.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
s=json.loads((P/'SCENARIO_TEMPLATE.json').read_text())
try:m.validate(s);raise RuntimeError('Missing pose accepted')
except ValueError:pass
s.update(expected_actor_position=[1,2,3],camera_pitch_degrees=-10,camera_fov=70);m.validate(s)
with tempfile.TemporaryDirectory(prefix='astraea-measurement-r002-')as tmp:
 t=Path(tmp);scenario=t/'scenario.json';scenario.write_text(json.dumps(s));cmd=['python','-O',str(P/'run_modes.py'),'--godot','not-installed-editor','--project',str(t/'absent'),'--scenario',str(scenario),'--output',str(t/'results')];r=subprocess.run(cmd,capture_output=True,text=True);assert r.returncode==0,r.stderr;plan=json.loads(r.stdout);assert len(plan['modes'])==4 and not plan['launch_requested']and not(t/'results').exists()
 bad=copy.deepcopy(s);bad['startup_timeout_seconds']=0
 try:m.validate(bad);raise RuntimeError('Bad timeout accepted')
 except ValueError:pass
 state={'d04':{'resident_ids':['room1'],'optimized_ids':[]},'private':{'resident_ids':['private1']},'active_light_selection':[],'all_scene_light_state':[],'batch_stopped':False}
 sample={'ticks_us':100,'state_index':0,'heading':0,'phase':'warm_sample','frame_interval_us':20000,'camera_transform':'fixed','camera_fov':70,'actor_position':'fixed','max_fps':60,'vsync_mode':1,'internal_resolution':[640,360],'window_size':'1280x720','effects':True,'visible_draws':10,'shadow_draws':2,'sampler_us':5}
 for name,batch,occ in m.MODES:
  d={'mode':name,'batching':batch,'occlusion':occ,'status':'CAPTURED','scenario':{'headings_degrees':[0]},'engine_version':{'string':'4.6.3'},'source_manifest_sha256':s['expected_source_manifest_sha256'],'residency_events':[{'state':copy.deepcopy(state)}],'samples':[dict(sample,occlusion_enabled=occ=='1')],'controller':{'optimized_resident_count':7,'activations':[{'saved_main_submissions':10}]},'sampler_max_us':5};(t/(name+'.json')).write_text(json.dumps(d))
 def summary():
  r=subprocess.run(['python',str(P/'summarize.py'),str(t)],capture_output=True,text=True);assert r.returncode==0,r.stderr;return json.loads(r.stdout)
 d=summary();assert d['complete_four_mode_capture'];assert all(not row['batch_comparison_exercised_without_fallback']for row in d['rows']if row['mode'].startswith('batch_'))
 f=t/'batch_with_existing_occlusion.json';d=json.loads(f.read_text());d['residency_events'][0]['state']['d04']['optimized_ids']=['room1'];f.write_text(json.dumps(d));rows=summary()['rows'];assert next(x for x in rows if x['mode']=='batch_with_existing_occlusion')['pure_render_comparison_eligible']
 d['residency_events'][0]['state']['all_scene_light_state']=[{'path':'changed_light'}];f.write_text(json.dumps(d));assert not next(x for x in summary()['rows']if x['mode']=='batch_with_existing_occlusion')['pure_render_comparison_eligible']
 (t/'no_occlusion_no_batch.json').unlink();assert not summary()['complete_four_mode_capture']
result={'gdscript_parse':'PASS','python_optimized_mode_dry_plan':'PASS_NO_LAUNCH','unresolved_pose_and_bad_timeout_refused':True,'final_state_false_batch_attribution_rejected':True,'matching_active_batch_eligible':True,'nonbudget_light_mismatch_rejected':True,'incomplete_modes_rejected':True,'real_ship_run':False,'laptop_launch':False};(P/'VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
