from pathlib import Path
import bpy,json,hashlib
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.load(open(W/'PLAN.json'));sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
for f,h in P['source_pins'].items():assert sha(R/f)==h,f
bpy.ops.wm.open_mainfile(filepath=str(R/P['source_native']));parts=[]
for ob in bpy.context.scene.objects:
 if ob.type!='MESH' or not ob.data.vertices:continue
 vs=[ob.matrix_world@v.co for v in ob.data.vertices];vv=[[v.x,v.z,-v.y]for v in vs];lo=[min(v[i]for v in vv)for i in range(3)];hi=[max(v[i]for v in vv)for i in range(3)]
 parts.append({'name':ob.name,'bounds':[lo,hi],'world_vertices':vv,'role':ob.get('role'),'category':ob.get('category')})
for site in P['closure_sites']:
 q=next(x for x in parts if x['name']==site['source_name']);assert abs(q['bounds'][1][1]-site['bottom'])<.0001,site['source_name']
over=[]
for site in P['closure_sites']+P['ceiling_edge_sites']:
 name=site.get('source_name',site.get('name'));lo,hi=site['bounds']
 for q in parts:
  a,b=q['bounds'];dims=[min(hi[i],b[i])-max(lo[i],a[i])for i in range(3)]
  if min(dims)>.00001:over.append({'site':name,'source':q})
(W/'SOURCE_NATIVE_GEOMETRY.json').write_text(json.dumps(parts,indent=2)+'\n');(W/'SOURCE_CLOSURE_OVERLAPS.json').write_text(json.dumps(over,indent=2)+'\n');print(json.dumps({'source_meshes':len(parts),'overlaps':[{'site':q['site'],'source':q['source']['name']}for q in over]}))
