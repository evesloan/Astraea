"""Read existing streamed route evidence; does not start or control an engine."""
import argparse,json,statistics,math
from collections import defaultdict
from pathlib import Path

def pct(a,q):
 a=sorted(a)
 if not a:return None
 return a[min(len(a)-1,max(0,math.ceil(len(a)*q)-1))]
def summary(path):
 rows=[json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]
 headers=[x for x in rows if x.get('kind')=='header'];results=[x for x in rows if x.get('kind')=='result']
 if len(headers)!=1:raise ValueError('exactly one source/renderer header required')
 h=headers[0];r=results[-1] if results else {'status':'INTERRUPTED_NO_RESULT'};groups=defaultdict(list)
 for row in rows:
  if row.get('kind')=='frame':groups[(row['cycle'],row['leg'],row['phase'])].append(row)
 measures=[]
 for key,frames in sorted(groups.items()):
  times=[x['interval_us']/1000 for x in frames];m={'cycle':key[0],'leg':key[1],'phase':key[2],'frames':len(frames),'frame_ms_median':statistics.median(times),'frame_ms_p95':pct(times,.95),'frame_ms_p99':pct(times,.99),'frame_ms_max':max(times),'draws_median':statistics.median(x['draws'] for x in frames),'peak_nodes':max(x['nodes'] for x in frames),'peak_resources':max(x['resources'] for x in frames),'peak_static_bytes':max(x['static_bytes'] for x in frames),'engine_process_ms_median':statistics.median(x['process_ms'] for x in frames),'physics_ms_median':statistics.median(x['physics_ms'] for x in frames)}
  for name in ['viewport_render_cpu_ms','viewport_render_gpu_ms']:
   values=[x[name] for x in frames if name in x and x[name]>0]
   m[name+'_median']=statistics.median(values) if values else None
  measures.append(m)
 settled=[x for x in rows if x.get('kind')=='settled' and x['station']=='CENTRAL']
 growth=[]
 if settled:
  start=settled[0]
  for row in settled[1:]:growth.append({'cycle':row['cycle'],'nodes_delta':row['nodes']-start['nodes'],'resources_delta':row['resources']-start['resources'],'static_bytes_delta':row['static_bytes']-start['static_bytes'],'same_cursor':abs(row['cursor_m']-start['cursor_m'])<.001,'camera_before':start['camera'],'camera_after':row['camera']})
 return {'source':h,'result':r,'measurements':measures,'central_settled_growth':growth,'acceptance':'No causal gain or hardware FPS acceptance inferred. Compare exact source flags, complete route, internal resolution and camera/content traces before A/B. Static bytes and Resource count are not total process RAM or live RID-owner counts. CPU render excludes scripts/physics; GPU zeros are unavailable, not zero cost.'}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('jsonl');p.add_argument('--output');a=p.parse_args();text=json.dumps(summary(a.jsonl),indent=2)+'\n'
 if a.output:
  out=Path(a.output)
  with out.open('x') as f:f.write(text)
 else:print(text,end='')
