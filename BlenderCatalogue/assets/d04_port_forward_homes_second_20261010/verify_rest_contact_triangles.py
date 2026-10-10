from pathlib import Path
import json,numpy as np,math
r=Path('/workspace/astraea-recovered-532087b9-20261010T083844Z');w=r/'BlenderCatalogue/assets/d04_port_forward_homes_second_20261010';p=json.load(open(w/'RUNTIME_PLAN.json'));f=r/'BlenderCatalogue/assets/forward_staff_shaft_interfaces_20261010/source_geometry.py';ns={'__file__':str(f)};exec(f.read_text(),ns);T=ns['triangles'];out=[]
for s in p['rest_reference_samples']:
 room=next(a for a in p['rooms']if a['source_index']==s['room']);v=np.array(s['local_reference']['position']);c=math.cos(s['yaw']);sn=math.sin(s['yaw']);at=np.array(s['position'])+np.array([c*v[0]+sn*v[2],v[1],-sn*v[0]+c*v[2]]);rows=[]
 for name,ts in T(room['model_file']):
  if s['binding']not in name:continue
  for tri in ts:
   q=tri[:,[0,2]];a=q[1]-q[0];b=q[2]-q[0];den=a[0]*b[1]-a[1]*b[0]
   if abs(den)<1e-9:continue
   d=at[[0,2]]-q[0];u=(d[0]*b[1]-d[1]*b[0])/den;v2=(a[0]*d[1]-a[1]*d[0])/den
   if u>=-1e-5 and v2>=-1e-5 and u+v2<=1+1e-5:
    y=tri[0,1]+u*(tri[1,1]-tri[0,1])+v2*(tri[2,1]-tri[0,1]);
    if abs(y-at[1])<.05:rows.append({'node':name,'height':float(y),'delta':float(y-at[1]),'normal_y':float(np.cross(tri[1]-tri[0],tri[2]-tri[0])[1])})
 out.append({'room':s['room'],'marker':s['local_reference']['name'],'at':at.tolist(),'near_surfaces':rows})
print(json.dumps(out,indent=2));(w/'REST_MARKER_SOURCE_TRIANGLES.json').write_text(json.dumps(out,indent=2)+'\n')
