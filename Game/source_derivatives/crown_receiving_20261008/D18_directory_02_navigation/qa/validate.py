"""Independent actual GLB, packed resources, source parity, contacts and body/cart source geometry."""
import bpy,json,math,struct,hashlib,sys,bmesh
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path(sys.argv[sys.argv.index('--')+1]);F=106.5;C=json.loads((P/'contract.json').read_text());SEC=C['programme_key'];POLY=[tuple(x) for x in C['boundary']]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def inside(x,z,poly):
 for a,b in zip(poly,poly[1:]+poly[:1]):
  if abs((b[0]-a[0])*(z-a[1])-(b[1]-a[1])*(x-a[0]))<1e-5 and min(a[0],b[0])-1e-5<=x<=max(a[0],b[0])+1e-5 and min(a[1],b[1])-1e-5<=z<=max(a[1],b[1])+1e-5:return True
 yes=False
 for (a,b),(c,d) in zip(poly,poly[1:]+poly[:1]):
  if (b>z)!=(d>z) and x<(c-a)*(z-b)/(d-b)+a:yes=not yes
 return yes
def data(o):
 dg=bpy.context.evaluated_depsgraph_get();eo=o.evaluated_get(dg);me=eo.to_mesh();me.calc_loop_triangles();v=[o.matrix_world@p.co for p in me.vertices];t=[tuple(f.vertices) for f in me.loop_triangles];eo.to_mesh_clear();return v,t
def gb(v):return [min(p.x for p in v),min(p.z for p in v),-max(p.y for p in v),max(p.x for p in v),max(p.z for p in v),-min(p.y for p in v)]
def clip(poly,h,above):
 out=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  ia=a[1]>=h if above else a[1]<=h;ib=b[1]>=h if above else b[1]<=h
  if ia:out.append(a)
  if ia!=ib:
   u=(h-a[1])/(b[1]-a[1]);out.append(tuple(a[j]+u*(b[j]-a[j]) for j in range(3)))
 return out
def segdist(p,a,b):
 dx,dy=b[0]-a[0],b[1]-a[1];den=dx*dx+dy*dy;u=0 if den<1e-12 else max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/den));return math.hypot(p[0]-a[0]-u*dx,p[1]-a[1]-u*dy)
bpy.ops.wm.open_mainfile(filepath=str(P/'source/native.blend'));native={};fonts=[];nuv=[];normalbad=[];nonmanifold=[]
for o in bpy.context.scene.objects:
 if o.get('section_key')!=SEC:continue
 v,t=data(o);native[o.name]={'bounds':gb(v),'support':o['support'],'zone':o['zone']}
 if o.type=='FONT':fonts.append(o.name)
 else:
  if not o.data.uv_layers:nuv.append(o.name)
  if any(not all(math.isfinite(q) for q in f.normal) or f.normal.length<.9 or f.area<1e-10 for f in o.data.polygons):normalbad.append(o.name)
  bm=bmesh.new();bm.from_mesh(o.data)
  if any(not e.is_manifold for e in bm.edges):nonmanifold.append(o.name)
  bm.free()
packed=[{'name':im.name,'packed':bool(im.packed_file)} for im in bpy.data.images if im.type=='IMAGE' and im.size[0]>0]
glb=P/'exports'/(SEC+'.glb');raw=glb.read_bytes();magic,version,total=struct.unpack_from('<4sII',raw);pos=12;doc={}
while pos<len(raw):
 size,kind=struct.unpack_from('<II',raw,pos);pos+=8
 if kind==0x4e4f534a:doc=json.loads(raw[pos:pos+size])
 pos+=size
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(glb))
rows={};geometry={};obstacle=[];buv=[];violations=[];triangles=0
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 v,t=data(o);b=gb(v);rows[o.name]=b;geometry[o.name]=(v,t,BVHTree.FromPolygons(v,t,all_triangles=True));triangles+=len(t)
 if not o.data.uv_layers:buv.append(o.name)
 if b[1]<F-.001 or b[4]>111+.001 or not all(inside(p.x,-p.y,POLY) for p in v):violations.append(o.name)
 for face in t:
  poly=clip([(v[j].x,v[j].z,-v[j].y) for j in face],F+.1,True)
  if poly:poly=clip(poly,F+1.8,False)
  if poly:
   proj=[(v[0],v[2]) for v in poly];obstacle.append((o.name,proj,(min(v[0] for v in proj),min(v[1] for v in proj),max(v[0] for v in proj),max(v[1] for v in proj))))
contacts=[]
for n,r in native.items():
 if n not in rows:continue
 sup=r['support'];b=rows[n];metric=None;method=''
 if sup=='shared_floor':metric=abs(b[1]-F);method='actual imported min vs retained floor datum'
 elif sup=='shared_ceiling':metric=abs(b[4]-111);method='actual imported max vs retained Crown ceiling datum'
 elif sup in geometry:
  va,ta,tree=geometry[n];vb,tb,other=geometry[sup]
  if tree.overlap(other):metric=0;method='actual triangle intersection'
  else:
   ds=[other.find_nearest(v)[3] for v in va]+[tree.find_nearest(v)[3] for v in vb];metric=min(v for v in ds if v is not None);method='actual bidirectional vertex/surface contact'
 contacts.append({'part':n,'support':sup,'gap_m':metric,'method':method,'passed':metric is not None and metric<=.025})
routes=[]
for n,path in C['paths'].items():
 mind=999;hit=None;points=[]
 for a,b in zip(path,path[1:]):
  count=max(1,math.ceil(math.dist(a,b)/.15));points.extend([(a[0]+(b[0]-a[0])*j/count,a[1]+(b[1]-a[1])*j/count) for j in range(count+1)])
 for pt in points:
  # Explicit allocation margin; door's start is permitted on boundary.
  for on,poly,bb in obstacle:
   lower=math.hypot(max(bb[0]-pt[0],pt[0]-bb[2],0),max(bb[1]-pt[1],pt[1]-bb[3],0))
   if lower>mind:continue
   ds=min(segdist(pt,a,b) for a,b in zip(poly,poly[1:]+poly[:1]))
   if len(poly)>=3 and inside(pt[0],pt[1],poly):ds=0
   if ds<mind:mind=ds;hit=on
 for mode,radius in [('body',.3),('cart',.5)]:
  routes.append({'name':n+'_'+mode,'path_xz':path,'diameter_m':radius*2,'samples':len(points),'minimum_surface_clearance_m':round(mind-radius,4),'nearest':hit,'passed':mind>=radius+.005})
floors=json.loads((P/'dependencies/receiving_floors.json').read_text());regions=floors['regions'];floorbad=[]
for c in contacts:
 if c['support']!='shared_floor':continue
 b=rows[c['part']]
 for x,z in [(b[0],b[2]),(b[0],b[5]),(b[3],b[2]),(b[3],b[5])]:
  if not any(any(inside(x,z,[tuple(p) for p in t]) for t in r['triangles']) for r in regions):floorbad.append([c['part'],x,z])
ex,ez=C['entry_xz'];sign=1 if ex>0 else-1
sweepbad=[n for n,b in rows.items() if b[1]<109.2 and b[4]>F and b[0]<max(ex,ex+sign*2.5) and b[3]>min(ex,ex+sign*2.5) and b[2]<ez+2.5 and b[5]>ez-2.5]
errors=[max(abs(x-y) for x,y in zip(native[n]['bounds'],rows[n])) for n in native if n in rows]
external=[x['uri'] for x in doc.get('images',[])+doc.get('buffers',[]) if 'uri' in x]
checks={'native_parts':len(native),'actual_export_meshes':len(rows),'triangles':triangles,'names_equal':set(native)==set(rows),'font_names':fonts,'font_mesh_parity':all(n in rows for n in fonts),'max_bounds_error_m':max(errors,default=999),'bounds_godot':gb([v for vs,ts,tr in geometry.values() for v in vs]),'containment_failures':violations,'native_missing_uv':nuv,'export_missing_uv':buv,'invalid_normals_or_zero_area':normalbad,'nonmanifold_native_solids':nonmanifold,'packed_images':packed,'embedded_glb_images':len(doc.get('images',[])),'external_uris':external,'support_contacts':contacts,'support_failures':[c for c in contacts if not c['passed']],'floor_support_failures':floorbad,'door_sweep_intrusions':sweepbad,'routes':routes,'failed_routes':[r for r in routes if not r['passed']],'glb_declared_bytes':total,'glb_actual_bytes':len(raw),'glb_version':version}
passed=checks['names_equal'] and max(errors,default=999)<.001 and checks['font_mesh_parity'] and magic==b'glTF' and total==len(raw) and all(v['packed'] for v in packed) and not any([violations,nuv,buv,normalbad,nonmanifold,external,checks['support_failures'],floorbad,sweepbad,checks['failed_routes']])
report={'status':'PASS' if passed else 'FAIL','scope':'Independent actual GLB/source and conservative geometry checks. Not Godot capsule/cart/controller acceptance. Receiving windows/shell untouched.','blender':bpy.app.version_string,'checks':checks,'hashes':{'native':sha(P/'source/native.blend'),'glb':sha(glb)}}
(P/'qa/validation.json').write_text(json.dumps(report,indent=2));print('QA',report['status'],'parts',len(rows),'triangles',triangles)
for n in ['containment_failures','invalid_normals_or_zero_area','nonmanifold_native_solids','support_failures','door_sweep_intrusions','failed_routes']:print(n,checks[n])

