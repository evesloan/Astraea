"""Summarize captured measurements; flag content confounds, never infer GPU cost."""
import argparse,json,statistics
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('directory',type=Path);a=p.parse_args()
records={}
for f in a.directory.glob('*.json'):
 d=json.loads(f.read_text())
 if d.get('status')=='CAPTURED'and 'samples'in d:records[d['mode']]=d
assert records,'No captured result files'
def content(d,s):
 state=d['residency_events'][s['state_index']]['state']
 return json.dumps({'d04':state['d04']['resident_ids'],'private':state['private']['resident_ids'],'lights':state['active_light_selection'],'all_lights':state['all_scene_light_state'],'actor':s['actor_position'],'max_fps':s['max_fps'],'vsync':s['vsync_mode'],'source':d['source_manifest_sha256'],'engine':d['engine_version'],'camera':s['camera_transform'],'fov':s['camera_fov'],'internal':s['internal_resolution'],'window':s['window_size'],'effects':s['effects']},sort_keys=True)
def quantile(values,q):
 v=sorted(values);return v[min(len(v)-1,int((len(v)-1)*q))]
required={'no_occlusion_no_batch','existing_occlusion_no_batch','batch_without_occlusion','batch_with_existing_occlusion'}
complete=set(records)==required
reference=records.get('existing_occlusion_no_batch');rows=[]
for mode,d in records.items():
 for heading in d['scenario']['headings_degrees']:
  samples=[s for s in d['samples']if s['heading']==heading and s['phase']=='warm_sample']
  if not samples:continue
  states={content(d,s)for s in samples};ref_states=set()
  if reference:ref_states={content(reference,s)for s in reference['samples']if s['heading']==heading and s['phase']=='warm_sample'}
  us=[s['frame_interval_us']/1000 for s in samples];controller=d['controller'];row={'mode':mode,'heading':heading,'frames':len(samples),'frame_interval_ms_median':statistics.median(us),'p95_ms':quantile(us,.95),'p99_ms':quantile(us,.99),'median_visible_draws':statistics.median(s['visible_draws']for s in samples),'median_shadow_draws':statistics.median(s['shadow_draws']for s in samples),'stable_content':len(states)==1,'same_stable_content_as_existing_reference':len(states)==1 and len(ref_states)==1 and states==ref_states,'fallback_events':controller.get('fallback_events',[]),'optimized_resident_count_final':controller.get('optimized_resident_count',0),'sampler_max_us':d['sampler_max_us'],'controller_max_us':controller.get('controller_max_us',0),'light_guard_highwater_us':controller.get('existing_light_guard_max_us',0)}
  sample_states=[d['residency_events'][s['state_index']]['state']for s in samples]
  row['batch_comparison_exercised_without_fallback']=d['batching']=='1'and not controller.get('fallback_events')and all(not state['batch_stopped']and len(state['d04']['optimized_ids'])>0 for state in sample_states)and any(r.get('saved_main_submissions',0)>0 for r in controller.get('activations',[]))
  frame_costs=[]
  frames=d.get('controller_frames',[])
  for before,after in zip(frames,frames[1:]):
   if samples[0]['ticks_us']<=after['ticks_us']<=samples[-1]['ticks_us']:
    frame_costs.append(max(0,after['total_us']-before['total_us']))
  row['controller_frame_us_p95']=quantile(frame_costs,.95)if frame_costs else None
  row['sampler_us_p95']=quantile([s.get('sampler_us',0)for s in samples],.95)
  row['mode_toggle_correct']=all(s['occlusion_enabled']==(d['occlusion']=='1')for s in samples)
  row['pure_render_comparison_eligible']=complete and row['same_stable_content_as_existing_reference']and row['mode_toggle_correct']and(d['batching']=='0'or row['batch_comparison_exercised_without_fallback'])
  rows.append(row)
print(json.dumps({'complete_four_mode_capture':complete,'rows':rows,'warning':'Frame intervals include instrumentation and frame cap. No GPU/CPU causal diagnosis or performance acceptance. Different/unstable residency or light selection prevents pure render attribution. Heading settling is not a cold process per heading.'},indent=2))
