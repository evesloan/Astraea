"""Independent saved native/imported GLB geometry audit. Run with shared mutex."""
import bpy,json,math,struct,hashlib,sys,pathlib
from mathutils import Vector
from mathutils.bvhtree import BVHTree
BASE=pathlib.Path(__file__).resolve().parent;section=sys.argv[sys.argv.index('--')+1];P=BASE/section
(P/'qa/verify_used.py').write_bytes(pathlib.Path(__file__).read_bytes())
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def data(o):
 eo=o.evaluated_get(bpy.context.evaluated_depsgraph_get());me=eo.to_mesh();me.calc_loop_triangles();v=[o.matrix_world@p.co for p in me.vertices];t=[tuple(f.vertices) for f in me.loop_triangles];eo.to_mesh_clear();return v,t

def bounds(v):return [min(p.x for p in v),min(p.z for p in v),-max(p.y for p in v),max(p.x for p in v),max(p.z for p in v),-min(p.y for p in v)]
def gap(a,b):return math.sqrt(sum(max(a[i]-b[i+3],b[i]-a[i+3],0)**2 for i in range(3)))
def clip(poly,h,above):
 out=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  ia=a[1]>=h if above else a[1]<=h;ib=b[1]>=h if above else b[1]<=h
  if ia:out.append(a)
  if ia!=ib:
   u=(h-a[1])/(b[1]-a[1]);out.append(tuple(a[k]+u*(b[k]-a[k]) for k in range(3)))
 return out

def inside(x,z,poly):
 yes=False
 for (a,b),(c,d) in zip(poly,poly[1:]+poly[:1]):
  if (b>z)!=(d>z) and x<(c-a)*(z-b)/(d-b)+a:yes=not yes
 return yes

def distance(p,a,b):
 dx,dy=b[0]-a[0],b[1]-a[1];den=dx*dx+dy*dy;u=0 if den<1e-12 else max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/den));return math.hypot(p[0]-a[0]-u*dx,p[1]-a[1]-u*dy)

meta=json.loads((P/'source/build_metadata.json').read_text());C=meta['section'];sign=C['sign'];poly=[(sign*u,v) for u,v in meta['polygon']]
bpy.ops.wm.open_mainfile(filepath=str(P/'source/native.blend'));native={};packed=[];native_errors=[]
for o in bpy.context.scene.objects:
 if o.type not in ['MESH','FONT']:continue
 v,t=data(o);native[o.name]={'bounds':bounds(v),'type':o.type,'role':o.get('role')}
 if o.name in ['Care_cabinet_0','Waiting_bench_0']:print('CATALOGUE FLAGS',o.name,o.hide_get(),o.hide_viewport,o.hide_render,o.hide_select,o.visible_get(),flush=True)
 if o.name.startswith('QA_'):native_errors.append('Preview context saved: '+o.name)
 if o.type=='MESH' and not o.data.uv_layers:native_errors.append('Native UV missing '+o.name)
packed=[{'name':im.name,'packed':bool(im.packed_file)} for im in bpy.data.images if im.source=='FILE'];native_errors += ['Unpacked '+i['name'] for i in packed if not i['packed']]
raw=(P/'exports/section.glb').read_bytes();magic,version,total=struct.unpack_from('<4sII',raw);pos=12;doc={};binbytes=0
while pos<len(raw):
 size,kind=struct.unpack_from('<II',raw,pos);pos+=8
 if kind==0x4e4f534a:doc=json.loads(raw[pos:pos+size])
 if kind==0x004e4942:binbytes=size
 pos+=size
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(P/'exports/section.glb'));geo={};errors=list(native_errors);obstacle=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 v,t=data(o);bb=bounds(v);geo[o.name]=(v,t,bb,BVHTree.FromPolygons(v,t,all_triangles=True))
 if not o.data.uv_layers:errors.append('Export UV missing '+o.name)
 if any(not math.isfinite(float(x)) for pt in v for x in pt):errors.append('Nonfinite export vertex '+o.name)
 if any(f.normal.length<.9 for f in o.data.polygons):errors.append('Degenerate export normal '+o.name)
 edgecounts={}
 for tri in t:
  for a,b in zip(tri,tri[1:]+tri[:1]):
   pair=tuple(sorted((a,b)));edgecounts[pair]=edgecounts.get(pair,0)+1
 volume=sum(v[a].dot(v[b].cross(v[c])) for a,b,c in t)/6
 if edgecounts and all(n==2 for n in edgecounts.values()) and volume<-.00001:errors.append('Inward closed-mesh winding '+o.name)
 if bb[1]<-.002 or bb[4]>C['roof']-C['floor']+.002 or bb[0]<(-46 if sign<0 else 0)-.002 or bb[3]>(0 if sign<0 else 46)+.002 or bb[2]<-.002 or bb[5]>68.002:errors.append('Export containment '+o.name)
 for face in t:
  pp=[(v[i].x,v[i].z,-v[i].y) for i in face];pp=clip(pp,.1,True)
  if pp:pp=clip(pp,1.8,False)
  if pp:
   proj=[(a[0],a[2]) for a in pp];obstacle.append((o.name,proj,(min(a[0] for a in proj),min(a[1] for a in proj),max(a[0] for a in proj),max(a[1] for a in proj))))
parity=[]
for n,r in native.items():
 exportname=n+'_export' if r['type']=='FONT' else n
 if exportname not in geo:errors.append('Export object missing '+exportname);continue
 delta=max(abs(a-b) for a,b in zip(r['bounds'],geo[exportname][2]));parity.append({'native':n,'export':exportname,'max_bound_delta_m':delta,'text_geometry':r['type']=='FONT'})
 if delta>.003:errors.append('Bounds mismatch '+n)
# Actual surface contact network, anchored only by a receiving-floor contact.
# Broad boxes accelerate candidate lookup; contacts require actual triangles/vertex-to-triangle distances.
contacts=[];graph={n:set() for n in geo};names=list(geo)
for i,n in enumerate(names):
 v,t,bb,tr=geo[n]
 for other in names[i+1:]:
  vv,tt,bb2,tr2=geo[other]
  if gap(bb,bb2)>.026:continue
  if tr.overlap(tr2):metric=0;method='triangle intersection'
  else:
   metric=min([tr2.find_nearest(p)[3] for p in v]+[tr.find_nearest(p)[3] for p in vv]);method='bidirectional vertex-to-triangle surface distance'
  if metric<=.026:graph[n].add(other);graph[other].add(n);contacts.append({'a':n,'b':other,'surface_gap_m':round(metric,6),'method':method})
roots={n for n in geo if abs(geo[n][2][1])<=.026};seen=set(roots);todo=list(roots)
while todo:
 n=todo.pop()
 for m in graph[n]-seen:seen.add(m);todo.append(m)
unsupported=sorted(set(geo)-seen)
# Export text plaque is an editable native text mesh rendered from an attached plaque.
errors += ['No floor-connected surface support '+n for n in unsupported]
paths=json.loads((BASE/'route_witnesses.json').read_text())
routes=[]
for name,path in paths[C['kind']].items():
 for label,rad in [('player',.30),('broad_body',.65),('actual_cart_all_yaw_disc',0.8153)]:
  pp=[]
  for a,b in zip(path,path[1:]):
   count=max(1,math.ceil(math.dist(a,b)/.2));pp += [(sign*(a[0]+(b[0]-a[0])*i/count),a[1]+(b[1]-a[1])*i/count) for i in range(count+1)]
  mind=999;hit=None
  for pt in pp:
   for n,poly2,bb in obstacle:
    lower=math.hypot(max(bb[0]-pt[0],pt[0]-bb[2],0),max(bb[1]-pt[1],pt[1]-bb[3],0))
    if lower>mind:continue
    ds=min(distance(pt,a,b) for a,b in zip(poly2,poly2[1:]+poly2[:1]))
    if len(poly2)>=3 and inside(*pt,poly2):ds=0
    if ds<mind:mind=ds;hit=n
  routes.append({'route':name,'shape':label,'path_local_xz':[(sign*u,v) for u,v in path],'radius_m':rad,'samples':len(pp),'surface_clearance_after_radius_m':round(mind-rad,4),'nearest':hit,'passed':mind>=rad+.005})
for x in routes:
 if not x['passed']:errors.append('Approach fail '+x['route']+' '+x['shape'])
report={'scope':'Independent reopened saved-native and actual imported GLB source test; installed Godot physics/navigation acceptance remains root-owned and untested','programme_key':C['key'],'source_sha256':sha(P/'source/native.blend'),'export_sha256':sha(P/'exports/section.glb'),'glb_container':{'magic':magic.decode(),'version':version,'bytes':total,'actual_bytes':len(raw),'embedded_binary_bytes':binbytes,'external_images':[im for im in doc.get('images',[]) if 'uri' in im],'lights_extension':doc.get('extensions',{}).get('KHR_lights_punctual')},'native_objects':len(native),'export_objects':len(geo),'packed_images':packed,'parity':parity,'floor_contact_objects':sorted(roots),'actual_surface_contacts':contacts,'unsupported':unsupported,'routes':routes,'errors':errors}
(P/'qa/roundtrip.json').write_text(json.dumps(report,indent=2));print('ROUNDTRIP',len(errors),'errors',errors[:35],flush=True)
if errors:raise RuntimeError('Actual source roundtrip/support/approach checks failed; evidence retained')




