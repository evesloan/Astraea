"""Actual mesh contact graph including exact compiler-floor contract solids and retained keel mesh."""
from pathlib import Path
from collections import deque
import bpy,json,math,hashlib
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];C=R.parents[1];D=json.loads((R/'source/connected_contract.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(R/'source/AST-AQU-016.blend'))
obs={};eps=5e-5

def record(name,vv,ff):obs[name]={'v':vv,'tree':BVHTree.FromPolygons(vv,ff,all_triangles=False,epsilon=eps),'bounds':[(min(p[i]for p in vv),max(p[i]for p in vv))for i in range(3)]}
for o in bpy.context.scene.objects:
 if o.type!='MESH'or o.get('export_excluded',False):continue
 record(o.name,[o.matrix_world@v.co for v in o.data.vertices],[list(f.vertices)for f in o.data.polygons])
for f in D['floor_regions']:
 vv=[];ff=[]
 for t in f['triangles']:
  k=len(vv);vv += [Vector((x,-z,y))for y in[f['floor_y']-f['thickness'],f['floor_y']]for x,z in t];ff += [[k+i for i in face]for face in[(2,1,0),(3,4,5),(0,1,4,3),(1,2,5,4),(2,0,3,5)]]
 record('COMPILER_FLOOR_'+f['id'],vv,ff)
with bpy.data.libraries.load(str(C/'assets/lower_hull_body/source/AST-HUL-001.blend'),link=False)as(a,b):b.objects=['HUL_KeelPan']
o=b.objects[0];record('RETAINED_HUL_KeelPan',[o.matrix_world@v.co for v in o.data.vertices],[list(f.vertices)for f in o.data.polygons])
DIR=Vector((1,.371,.529)).normalized()
def inside(p,r):
 h=r['tree'].find_nearest(p)
 if h[0]is not None and h[3]<eps:return True
 q=p.copy();hits=0
 for _ in range(40):
  h,n,i,d=r['tree'].ray_cast(q,DIR)
  if h is None:break
  hits+=1;q=h+DIR*.0002
 return hits%2==1

def contact(a,b):
 if any(min(a['bounds'][i][1],b['bounds'][i][1])+eps<max(a['bounds'][i][0],b['bounds'][i][0])for i in range(3)):return None
 pairs=a['tree'].overlap(b['tree'])
 if pairs:return{'method':'actual BVH triangle intersections','triangle_pairs':len(pairs)}
 for p in a['v']:
  if inside(p,b):return{'method':'actual vertex at/on closed surface','witness_blender':list(p)}
 for p in b['v']:
  if inside(p,a):return{'method':'actual vertex at/on closed surface','witness_blender':list(p)}
 return None
names=sorted(obs);graph={n:set()for n in names};rows=[]
for i,a in enumerate(names):
 for b in names[i+1:]:
  hit=contact(obs[a],obs[b])
  if hit:graph[a].add(b);graph[b].add(a);rows.append({'a':a,'b':b,**hit})
seen={'RETAINED_HUL_KeelPan'};q=deque(seen)
while q:
 a=q.popleft()
 for b in graph[a]-seen:seen.add(b);q.append(b)
unrooted=sorted(set(names)-seen)
report={'input_sha256':{str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest()for p in[R/'source/connected_contract.json',R/'source/AST-AQU-016.blend',R/'exports/AST-AQU-016.glb']},'pass':not unrooted,'scope':'Actual source closed-mesh contacts, with intended compiler floor solids built exactly from contract; not civil-engineering certification or runtime adoption','root':'RETAINED_HUL_KeelPan','mesh_and_floor_nodes':len(names),'rooted_nodes':len(seen),'unrooted':unrooted,'contacts':rows,'tolerance_m':eps,'compiler_floors_exported':False}
(R/'qa/source_contact_graph.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items()if k!='contacts'},indent=2));assert not unrooted,unrooted
