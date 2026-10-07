import json,pathlib,struct,hashlib,collections,math
import numpy as np
from PIL import Image,ImageDraw,ImageFont
import sys
sys.path.insert(0,'/workspace/scratch/375c2e438292/botanical_receiving_court_build_20261007/python_deps')
from shapely.geometry import box,shape
from shapely.ops import unary_union
D=pathlib.Path(__file__).resolve().parent
load=lambda n:json.loads((D/n).read_text())
blob=(D/'root_build/quiet_grove_upper_receiver.glb').read_bytes();n=struct.unpack_from('<I',blob,12)[0];j=json.loads(blob[20:20+n]);off=20+n;ln,typ=struct.unpack_from('<II',blob,off);buf=blob[off+8:off+8+ln]
def acc(i):
 a=j['accessors'][i];v=j['bufferViews'][a['bufferView']];fmt={5126:'f',5125:'I',5123:'H',5121:'B'}[a['componentType']];ct={'VEC3':3,'SCALAR':1}[a['type']];sz=struct.calcsize(fmt)*ct;start=v.get('byteOffset',0)+a.get('byteOffset',0);stride=v.get('byteStride',sz)
 return [struct.unpack_from('<'+fmt*ct,buf,start+k*stride) for k in range(a['count'])]
actual=[];triangles=0
for node in j['nodes']:
 if 'mesh' not in node:continue
 assert not any(k in node for k in ['matrix','rotation','scale','translation'])
 verts=[];outward=True;closed=True;volume=0
 for prim in j['meshes'][node['mesh']]['primitives']:
  v=np.array(acc(prim['attributes']['POSITION']),dtype=float);ix=[x[0] for x in acc(prim['indices'])];triangles+=len(ix)//3;cen=(v.min(axis=0)+v.max(axis=0))/2;edges=collections.Counter()
  for k in range(0,len(ix),3):
   t=v[ix[k:k+3]];normal=np.cross(t[1]-t[0],t[2]-t[0]);outward&=float(np.dot(normal,t.mean(axis=0)-cen))>0
   volume+=np.dot(t[0]-cen,np.cross(t[1]-cen,t[2]-cen))/6
   for a,b in [(t[0],t[1]),(t[1],t[2]),(t[2],t[0])]:edges[tuple(sorted((tuple(a),tuple(b))))]+=1
  closed &= all(x==2 for x in edges.values());verts.extend(v.tolist())
 actual.append({'id':node['name'],'bounds':[min(v[i] for v in verts) for i in range(3)]+[max(v[i] for v in verts) for i in range(3)],'closed_welded_edges':bool(closed),'outward_triangles':bool(outward),'volume_m3':volume})
expected={p['id']:p for p in load('GEOMETRY_PROPOSAL.json')['parts']};native={p['id']:p for p in load('NATIVE_REOPENED_GEOMETRY.json')};eps=1e-4
assert set(expected)==set(native)=={a['id'] for a in actual}
maxerr=max(abs(x-y) for a in actual for x,y in zip(a['bounds'],expected[a['id']]['bounds']));maxnative=max(abs(x-y) for a in actual for x,y in zip(a['bounds'],native[a['id']]['bounds']))
assert maxerr<eps and maxnative<eps and all(a['closed_welded_edges'] and a['outward_triangles'] and a['volume_m3']>0 for a in actual)
contacts=[];overlaps=[]
for i,a in enumerate(actual):
 for b in actual[i+1:]:
  x=a['bounds'];y=b['bounds'];ds=[min(x[k+3],y[k+3])-max(x[k],y[k]) for k in range(3)]
  if min(ds)>eps:overlaps.append([a['id'],b['id']])
  if sum(abs(d)<eps for d in ds)==1 and all(d>=-eps for d in ds):contacts.append([a['id'],b['id']])
assert len(contacts)==360 and not overlaps
adj={a['id']:set() for a in actual}
for a,b in contacts:adj[a].add(b);adj[b].add(a)
seen=set();todo=[actual[0]['id']]
while todo:
 a=todo.pop()
 if a in seen:continue
 seen.add(a);todo.extend(adj[a]-seen)
assert len(seen)==179
caps=load('SOURCE_INTERFACE_SCREEN.json')['cap_contacts'];capverify=[]
for c in caps:
 aa=[a for a in actual if a['id'].startswith('Bearing_'+c['counterpart']+'__')];assert len(aa)==1
 b=aa[0]['bounds'];assert abs(b[1]-83.08)<eps
 capverify.append({'counterpart':c['counterpart'],'actual_bottom':b[1],'actual_area':(b[3]-b[0])*(b[5]-b[2]),'expected_area':c['area_m2']})
shoes=collections.defaultdict(list)
for a in actual:
 if a['id'].startswith('RoomShoe_'):
  b=a['bounds'];assert abs(b[1]-83.76)<eps and abs(b[4]-83.78)<eps
  shoes[int(a['id'].split('_')[1])].append(a)
assert len(shoes)==9
actualtop=unary_union([box(a['bounds'][0],a['bounds'][2],a['bounds'][3],a['bounds'][5]) for a in actual if abs(a['bounds'][4]-83.76)<eps])
pierqa=[]
for p in load('TALL_PIER_CONTACTS.json'):
 b=p['bounds'];f=box(b[0],b[2],b[3],b[5]);missing=f.difference(actualtop).area;assert missing<eps;pierqa.append({'id':p['id'],'uncovered_area_m2':missing})
shoeqa=[]
for c in load('ROOM_CONTACTS.json'):
 group=shoes[c['source_index']];poly=unary_union([box(a['bounds'][0],a['bounds'][2],a['bounds'][3],a['bounds'][5]) for a in group]);delta=poly.symmetric_difference(shape(c['shoe_contact_polygon'])).area;assert delta<.001;shoeqa.append({'source_index':c['source_index'],'actual_contact_area':poly.area,'plan_difference_m2':delta})
# All retained source pins, including actual room shells, are checked after build/reopen.
pins=load('SOURCE_PINS.json');same=all(hashlib.sha256(pathlib.Path(p['path']).read_bytes()).hexdigest()==p['current_sha256'] for p in pins)
assert same
for c in load('ROOM_CONTACTS.json'):assert hashlib.sha256(pathlib.Path(c['shell_path']).read_bytes()).hexdigest()==c['shell_sha256']
report={'status':'independent reopened native plus actual GLB byte-level QA passed','blender':'4.3.2','threads':2,'meshes':len(actual),'triangles':triangles,'native_closed_meshes':sum(n['closed_edges'] for n in native.values()),'GLB_closed_outward_positive_volume_meshes':len(actual),'max_expected_bounds_error_m':maxerr,'max_native_export_bounds_error_m':maxnative,'tolerance_m':eps,'internal_face_contacts':len(contacts),'connected_meshes':len(seen),'positive_volume_overlaps':overlaps,'cap_interfaces':capverify,'room_shoe_groups':{k:len(v) for k,v in shoes.items()},'four_tall_piers':pierqa,'actual_room_contact_polygons':shoeqa,'source_pins_unchanged_after_build':same,'pending_holds':['94m outboard gap','0.4m house longitudinal end gaps','Library/Cinema actual source counterpart revisions','source visual/art and runtime adoption acceptance'],'files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (D/'root_build').iterdir() if p.is_file()}}
(D/'ACTUAL_EXPORT_QA.json').write_text(json.dumps(report,indent=2));(D/'ACTUAL_EXPORT_BOUNDS.json').write_text(json.dumps(actual,indent=2))
# Legible technical source context derived from actual exported bounds; not a runtime capture.
im=Image.new('RGB',(1700,1740),'#f4f1e7');dr=ImageDraw.Draw(im)
fontpath='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
f=ImageFont.truetype(fontpath,21);small=ImageFont.truetype(fontpath,17);title=ImageFont.truetype(fontpath,30)
dr.text((45,25),'Quiet Grove | upper receiving candidate',fill='#203b42',font=title)
dr.text((45,72),'ACTUAL GLB SOURCE GEOMETRY • diagnostic material • not installed or final art',fill='#6a4f35',font=f)
# Plan map x horizontal,z vertical
sx=18;sy=12;ox=80;oy=145
pt=lambda x,z:(ox+(x-8.2)*sx,oy+(z+466)*sy)
for a in actual:
 b=a['bounds'];col='#58757c'
 if a['id'].startswith('Bearing_'):col='#b39050'
 if a['id'].startswith('RoomShoe_'):col='#e6914f'
 p=pt(b[0],b[2]);q=pt(b[3],b[5]);dr.rectangle((*p,*q),fill=col)
for p in load('TALL_PIER_CONTACTS.json'):
 b=p['bounds'];dr.rectangle((*pt(b[0],b[2]),*pt(b[3],b[5])),fill='#b52f40');x,z=pt((b[0]+b[3])/2,(b[2]+b[5])/2);dr.ellipse((x-7,z-7,x+7,z+7),outline='#b52f40',width=2)
for x in [9,12.1,25,40,42.2,45.8,53.7]:dr.text((pt(x,-466)[0]-15,115),str(x),fill='#203b42',font=small)
for z in [-462.6,-450.8,-447.4,-446,-435,-419,-418,-400.2]:dr.text((950,pt(54,z)[1]-8+(-5 if z==-419 else 5 if z==-418 else 0)),str(z),fill='#203b42',font=small)
for i,t in enumerate(['179 closed exported meshes','2,148 triangles','360 internal face contacts','20 stepped bearing nodes','9 room-floor shoe groups','4 tall pier feet on collectors','','PLAN: world X / Z','Gray: girder lattice','Gold: Y83.08 bearing nodes','Orange: 20 mm room shoes','Red: existing tall-pier feet','','All original house / venue','assets remain unchanged.']):dr.text((1110,155+i*32),t,fill='#203b42',font=f)
# section at collector446, exaggerate y clearly
base=1510;scale=225
spt=lambda x,y:(80+(x-8.2)*25,base-(y-82.7)*scale)
dr.text((45,1080),'SECTION Z -446 | vertical scale exaggerated 9x',fill='#203b42',font=f)
for a in actual:
 b=a['bounds']
 if b[2]-eps<=-446<=b[5]+eps:
  l,t=spt(b[0],b[4]);r,bot=spt(b[3],b[1]);dr.rectangle((l,t,r,bot),fill='#58757c',outline='#294b52')
# retained slab and tall pier footprints shown as thin context, not exported new geometry
l,t=spt(8.2,84);r,bot=spt(29.05,83.76);dr.rectangle((l,t,r,bot),fill='#d9d1b9',outline='#9e9076')
for x in [8.55,12.1]:
 l,t=spt(x-.18,84.13);r,bot=spt(x+.18,84);dr.rectangle((l,t,r,bot),fill='#b52f40')
for y,label in [(82.875,'Closure 82.85–82.90'),(83.08,'Cap interface 83.08'),(83.77,'Slab 83.76 / shoe 83.78'),(84,'Pier base 84.00')]:dr.text((1260,spt(0,y)[1]-8),label,fill='#203b42',font=small)
dr.text((45,1580),'Collector → retained garden slab → tall pier; west cantilever 0.8 m from X9.',fill='#203b42',font=f)
dr.text((45,1620),'Holds: 94 m outboard gap; 0.4 m house-rail end gaps; Library/Cinema counterparts.',fill='#8b4337',font=f)
dr.text((45,1660),'147 members preserved: 83 furnished source / 47 unfinished specialty / 17 unfinished VIP.',fill='#203b42',font=f)
im.save(D/'SOURCE_PLAN_SECTION.png');print(json.dumps({k:report[k] for k in ['meshes','triangles','max_expected_bounds_error_m','internal_face_contacts','source_pins_unchanged_after_build']}))
