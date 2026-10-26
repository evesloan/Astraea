import json,statistics,math
from pathlib import Path
root=Path(__file__).resolve().parent
p=root/'tram-selected-operation-033'/'result.json'
r=json.loads(p.read_text(encoding='utf-8-sig'))
op=r['contact_sweep']['operation']
print('checks',r.get('checks'),'failures',r.get('failures'),'occluders',op.get('occluders'),'stable',op.get('stable_window_eligible'))
lights=op.get('lights',[])
print('visible lights',len(lights),'shadow',sum(x['shadow'] for x in lights))
stages=[{'stage':'settled_baseline','eligible':op.get('stable_window_eligible'),'samples':op.get('stable_samples',[])}]+op.get('attribution',[])
out=[]
for stage in stages:
    samples=stage['samples']
    if not samples:continue
    values={}
    for key in samples[0]:
        data=sorted(x[key] for x in samples)
        values[key]={'median':statistics.median(data),'p95':data[math.ceil(len(data)*.95)-1],'min':min(data),'max':max(data)}
    out.append({'stage':stage['stage'],'eligible':stage['eligible'],'count':len(samples),'metrics':values})
    print(stage['stage'],stage['eligible'],len(samples),{k:round(v['median'],3) for k,v in values.items()})
(p.parent/'ANALYSIS.json').write_text(json.dumps({'checks':r.get('checks'),'failures':r.get('failures'),'visible_lights':len(lights),'shadow_lights':sum(x['shadow'] for x in lights),'occluders':op.get('occluders'),'stages':out},indent=2)+'\n')

