"""Source-space OBB/AABB screening; never substitutes for the engine sweep."""
from pathlib import Path
import importlib.util,json,math,sys
import numpy as np
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[2];D=R/'Game/orchard_tram_interior_20261025/r002'
s=importlib.util.spec_from_file_location('source',R/'recovery/tram_section_successor_20261023/screen_section.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
p=json.loads((D/'PLAN.json').read_text());poses=json.loads((D/'POSE_KNOTS.json').read_text())
sources=[]
for name,file,offset,protected in [('Orchard','AST-RTL-009.glb',(4,52.5,-250),False),('Retail','AST-RTL-007.glb',(8,52.5,-216),False),('Switchback','AST-CIR-001.glb',(8,52.5,-237.5),True)]:
 for part,v in m.glb_vertices(file,offset):sources.append((name,part,np.min(v,axis=0),np.max(v,axis=0),protected or part.startswith('TAIL_Entry')))
for name,x,z in [('OrchardWestBearing',5.45,-248.4),('OrchardEastBearing',22.48,-248.4),('RetailBearing0',13,-226),('RetailBearing1',13,-206),('RetailBearing2',26,-230),('RetailBearing3',26,-216)]:
 for part,v in m.glb_vertices('AST-STR-001-H826.glb',(x,52.5,z)):sources.append((name,part,np.min(v,axis=0),np.max(v,axis=0),True))
def intersects(row,lo,hi,hx,hz,low,high):
 if hi[1]<=low or lo[1]>=high:return False
 center=np.array([row[1],row[2]]);q=(lo[[0,2]]+hi[[0,2]])/2;e=(hi[[0,2]]-lo[[0,2]])/2
 right=np.array([math.cos(row[3]),-math.sin(row[3])]);forward=np.array([math.sin(row[3]),math.cos(row[3])]);delta=q-center
 for axis in [np.array([1.,0]),np.array([0.,1]),right,forward]:
  ra=hx*abs(right@axis)+hz*abs(forward@axis);rb=e@np.abs(axis)
  if abs(delta@axis)>=ra+rb:return False
 return True
hits={};protected=[]
for row in poses[::5]:
 if not p['orchard_interval_m'][0]<=row[0]<=p['orchard_interval_m'][1]:continue
 for owner,name,lo,hi,protect in sources:
  if intersects(row,lo,hi,2,2.7,55.55,60.1):
   key=owner+'/'+name
   if key not in hits:hits[key]={'owner':owner,'name':name,'first_cursor':row[0],'first_pose':row[1:4],'lo':lo.tolist(),'hi':hi.tolist(),'protected':protect,'also_body_bbox':False}
   if intersects(row,lo,hi,1.162778,2.44,55.74,58.97):hits[key]['also_body_bbox']=True
protected=[v for v in hits.values() if v['protected']]
result={'mode':'conservative source OBB vs each source mesh AABB; not triangle or installed acceptance','reserved_envelope_m':{'width':4,'length':5.4,'y':[55.55,60.1]},'hits':list(hits.values()),'protected_hits':protected,'source_pins':m.PINS}
out=D/'SOURCE_SCREEN.json';assert not out.exists();out.write_bytes((json.dumps(result,indent=2)+'\n').encode())
print(json.dumps({'unique_hits':len(hits),'protected_hits':protected,'touched_owners':sorted({x['owner'] for x in hits.values()})},indent=2))
