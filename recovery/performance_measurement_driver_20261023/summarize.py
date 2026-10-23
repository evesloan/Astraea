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
 return json.dumps({'d04':state['d04']['resident_ids'],'private':state['private']['resident_ids'],'lights':state['active_light_selection'],'camera':s['camera_transform'],'fov':s['camera_fov'],'internal':s['internal_resolution'],'window':s['window_size'],'effects':s['effects']},sort_keys=True)
def quantile(values,q):
 v=sorted(values);return v[min(len(v)-1,int((len(v)-1)*q))]
reference=records.get('existing_occlusion_no_batch');rows=[]
for mode,d in records.items():
 for heading in d['scenario']['headings_degrees']:
  samples=[s for s in d['samples']if s['heading']==heading and s['phase']=='warm_sample']
  if not samples:continue
  states={content(d,s)for s in samples};ref_states=set()
  if reference:ref_states={content(reference,s)for s in reference['samples']if s['heading']==heading and s['phase']=='warm_sample'}
  us=[s['frame_interval_us']/1000 for s in samples];controller=d['controller'];row={'mode':mode,'heading':heading,'frames':len(samples),'frame_interval_ms_median':statistics.median(us),'p95_ms':quantile(us,.95),'p99_ms':quantile(us,.99),'median_visible_draws':statistics.median(s['visible_draws']for s in samples),'median_shadow_draws':statistics.median(s['shadow_draws']for s in samples),'stable_content':len(states)==1,'same_stable_content_as_existing_reference':len(states)==1 and len(ref_states)==1 and states==ref_states,'fallback_events':controller.get('fallback_events',[]),'optimized_resident_count_final':controller.get('optimized_resident_count',0),'sampler_max_us':d['sampler_max_us'],'controller_max_us':controller.get('controller_max_us',0),'light_guard_highwater_us':controller.get('existing_light_guard_max_us',0)}
  row['batch_comparison_exercised_without_fallback']=d['batching']=='1'and not controller.get('stopped',False)and controller.get('optimized_resident_count',0)>0
  rows.append(row)
print(json.dumps({'rows':rows,'warning':'Frame intervals include instrumentation and frame cap. No GPU/CPU causal diagnosis or performance acceptance. Different/unstable residency or light selection prevents pure render attribution. Heading settling is not a cold process per heading.'},indent=2))
