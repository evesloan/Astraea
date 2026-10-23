from pathlib import Path
import json,math,hashlib
R=Path('/workspace/Astraea-recovered-e6274e77-20261021');G=R/'Game';P=R/'recovery/quiet_d14_composed_fix';P.mkdir(exist_ok=True);D=P/'payload/Game/scripts/delivery_quiet_d14_20261023';D.mkdir(parents=True,exist_ok=True)
rows=json.loads(Path('/tmp/quiet_preimages.json').read_text());receipt=json.loads((G/'data/quiet_d14_receiving_20261016/RECEIPT.json').read_text());out=[]
def clip(poly,axis,plane,less):
 result=[]
 for i,e in enumerate(poly):
  s=poly[i-1];ds=s['p'][axis]-plane;de=e['p'][axis]-plane;ins=ds<=0 if less else ds>=0;ine=de<=0 if less else de>=0
  if ins!=ine:
   t=ds/(ds-de);result.append({k:[a+(b-a)*t for a,b in zip(s[k],e[k])]for k in s})
  if ine:result.append(e)
 return result
def area(t):
 a=[t[1]['p'][i]-t[0]['p'][i]for i in range(3)];b=[t[2]['p'][i]-t[0]['p'][i]for i in range(3)];return .5*math.sqrt(sum(x*x for x in [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]))
for src in rows:
 r=next(r for r in receipt['walls']if r['name']==src['name']);cuts=[{'min':r['cut_min'],'max':r['cut_max']}]+r.get('additional_cuts',[]);old=[];new=[];unchanged=0;removed_area=0
 for i in range(0,len(src['indices']),3):
  tri=[]
  for j in src['indices'][i:i+3]:
   v={'p':src['vertices'][j],'n':src['normals'][j],'uv':src['uv'][j]}
   if src['tangents']:v['t']=src['tangents'][j*4:j*4+4]
   tri.append(v)
  old.append(tri);pieces=[tri]
  for cut in cuts:
   if any(max(v['p'][a]for v in tri)<cut['min'][a]or min(v['p'][a]for v in tri)>cut['max'][a]for a in range(3)):continue
   rest=[]
   for piece in pieces:
    inside=piece
    for axis in range(3):
     for plane,less in [(cut['min'][axis],False),(cut['max'][axis],True)]:
      outside=clip(inside,axis,plane,not less)
      if len(outside)>=3:rest.append(outside)
      inside=clip(inside,axis,plane,less)
    removed_area+=sum(area([inside[0],inside[k],inside[k+1]])for k in range(1,len(inside)-1))
   pieces=rest
  result=[]
  for poly in pieces:
   for k in range(1,len(poly)-1):
    t=[poly[0],poly[k],poly[k+1]]
    if area(t)>1e-10:result.append(t)
  if result==[tri]:unchanged+=1
  new.extend(result)
 before=sum(map(area,old));after=sum(map(area,new));assert abs(before-after-removed_area)<1e-5
 # No new volume/triangle is introduced: each result is a clipped subset of an original successor triangle.
 out.append({'name':src['name'],'preimage_faces_hex_sha256':src['faces_hex_sha256'],'preimage_triangles':src['triangles'],'preimage_min':src['min'],'preimage_max':src['max'],'cuts':cuts,'triangles':new,'result_triangles':len(new),'unchanged_triangles':unchanged,'before_area':before,'after_area':after,'removed_area':removed_area})
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();data={'source_scene':'res://quiet_grove_specialty_20261022/runtime/QuietGrove17Receiving_r001.scn','source_scene_sha256':sha(G/'quiet_grove_specialty_20261022/runtime/QuietGrove17Receiving_r001.scn'),'receipt_sha256':sha(G/'data/quiet_d14_receiving_20261016/RECEIPT.json'),'source_adapter_sha256':sha(G/'quiet_grove_specialty_20261022/adapter_r002.gd'),'rows':out}
(D/'COMPOSITION.json').write_text(json.dumps(data,separators=(',',':'))+'\n');(P/'COMPOSITION_CHECK.json').write_text(json.dumps([{k:v for k,v in r.items()if k!='triangles'}for r in out],indent=2)+'\n');print([(r['name'],r['preimage_triangles'],r['result_triangles'],r['unchanged_triangles'],r['removed_area'])for r in out])
