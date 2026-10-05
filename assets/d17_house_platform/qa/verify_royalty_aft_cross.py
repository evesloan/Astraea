"""Exact prior-object preservation and geometric rooted contacts for held frame."""
import bpy, json, hashlib, subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1];C=R.parents[1]
BASE='e8df16bf434c0b7251527f761d71c37b6f946837'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=Path('/tmp/d17-aft-cross-baseline.blend')
old.write_bytes(subprocess.check_output(['git','-C',str(C),'show',BASE+':assets/d17_house_platform/source/AST-RES-005.blend']))
assert sha(old)=='3bf92efacb8fe1c9dacc70435f84cb706ecdecafc1df273aca425fbb5d641687'
def snapshot(path):
 bpy.ops.wm.open_mainfile(filepath=str(path));objects={};mats={}
 for o in bpy.context.scene.objects:
  row={'type':o.type,'matrix':[list(a) for a in o.matrix_world],'props':{k:o[k] for k in o.keys()}}
  if o.type=='MESH':row.update(vertices=[list(v.co) for v in o.data.vertices],faces=[list(p.vertices) for p in o.data.polygons],uv=[list(v.uv) for v in o.data.uv_layers.active.data],materials=[m.name for m in o.data.materials])
  objects[o.name]=row
 for m in bpy.data.materials:
  if not m.use_nodes:continue
  nodes=[]
  for n in m.node_tree.nodes:
   inputs={}
   for s in n.inputs:
    if not hasattr(s,'default_value'):continue
    v=s.default_value
    if not isinstance(v,(str,int,float,bool)):
     try:v=list(v)
     except TypeError:continue
    inputs[s.name]=v
   row={'type':n.bl_idname,'inputs':inputs}
   if n.type=='TEX_IMAGE':row.update(image=hashlib.sha256(n.image.packed_file.data).hexdigest(),interpolation=n.interpolation)
   nodes.append(row)
  mats[m.name]=nodes
 return objects,mats
A,AM=snapshot(old);B,BM=snapshot(R/'source/AST-RES-005.blend')
assert all(B.get(n)==v for n,v in A.items()),'Prior source geometry changed'
assert AM==BM,'Prior material or packed texture changed'
added=set(B)-set(A)
expected={'D17_SeatedHullFooting_3','D17_SeatedHullFooting_4','D17_RoyaltyPier_InnerAft','D17_RoyaltyPier_WestAft','D17_RoyaltyAftCrossTransfer'}|{f'D17_RoyaltyAftCross{k}_{i:02d}' for k in ['Rail','Brace'] for i in range(16)}
assert added==expected
def points(name):
 o=bpy.data.objects[name]
 return [(p.x,p.z,-p.y) for v in o.data.vertices for p in [o.matrix_world@v.co]]
def bounds(name):
 p=points(name);return [(min(v[i] for v in p),max(v[i] for v in p)) for i in range(3)]
def bearing(a,b):
 aa,bb=bounds(a),bounds(b);assert abs(aa[1][1]-bb[1][0])<1e-5,(a,b)
 area=1
 for i in [0,2]:area*=max(0,min(aa[i][1],bb[i][1])-max(aa[i][0],bb[i][0]))
 assert area>.9599,(a,b,area)
 return {'part':b,'root':a,'horizontal_contact_m2':area}
def clip(poly,axis,value,greater):
 out=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  ina=a[axis]>=value if greater else a[axis]<=value
  inb=b[axis]>=value if greater else b[axis]<=value
  if ina:out.append(a)
  if ina!=inb:
   t=(value-a[axis])/(b[axis]-a[axis]);out.append(tuple(a[j]+t*(b[j]-a[j]) for j in range(2)))
 return out
contacts=[bearing('D17_SeatedHullFooting_3','D17_RoyaltyPier_WestAft'),bearing('D17_SeatedHullFooting_4','D17_RoyaltyPier_InnerAft'),bearing('D17_RoyaltyPier_WestAft','D17_RoyaltyAftCrossTransfer'),bearing('D17_RoyaltyPier_InnerAft','D17_RoyaltyTransfer')]
a,b=bounds('D17_RoyaltyAftCrossTransfer'),bounds('D17_RoyaltyTransfer')
assert abs(a[0][1]-b[0][0])<1e-5
area=(min(a[1][1],b[1][1])-max(a[1][0],b[1][0]))*(min(a[2][1],b[2][1])-max(a[2][0],b[2][0]))
assert area>1.4399
contacts.append({'part':'D17_RoyaltyAftCrossTransfer','root':'D17_RoyaltyTransfer','side_face_joint_m2':area,'type':'Flush side joint; geometric contact only, no connection-load acceptance'})
def cross_overlap(name,post):
 o=bpy.data.objects[name];ps=points(name);bb=bounds(post)
 face=next(f for f in o.data.polygons if max(ps[i][2] for i in f.vertices)-min(ps[i][2] for i in f.vertices)<1e-5)
 poly=[(ps[i][0],ps[i][1]) for i in face.vertices]
 for axis in [0,1]:
  poly=clip(poly,axis,bb[axis][0],True);poly=clip(poly,axis,bb[axis][1],False)
 area=abs(sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(poly,poly[1:]+poly[:1])))/2
 aa=bounds(name);return area*max(0,min(aa[2][1],bb[2][1])-max(aa[2][0],bb[2][0]))
for name in sorted(added):
 if 'Footing' in name:continue
 for p in points(name):assert 99.59999<=p[0]<=108.40001 and -.45001<=p[1]<=101.76001 and 45.39999<=p[2]<=46.60001,(name,p)
 if 'Rail' in name or 'Brace' in name:
  for post in ['D17_RoyaltyPier_WestAft','D17_RoyaltyPier_InnerAft']:
   volume=cross_overlap(name,post);assert volume>.02,(name,post,volume)
   contacts.append({'part':name,'root':post,'actual_mesh_overlap_m3':volume})
q=json.loads((R/'qa/d17_royalty_aft_cross_census.json').read_text());assert q['clear'] and len(q['full_height_strip_slices'])==16 and all(not r['contacts'] for r in q['full_height_strip_slices'])
report={'pass':True,'baseline_commit':BASE,'unchanged_objects':len(A),'new_meshes':len(added),'materials_and_packed_textures_exact':True,'contacts':contacts,'source_sha256':sha(R/'source/AST-RES-005.blend'),'export_sha256':sha(R/'exports/AST-RES-005.glb'),'limits':['Source-only orthogonal braced frame','No structural load capacity acceptance','Room floor extents, second cross-frame, routes and private upper remain unresolved']}
(R/'qa/royalty_aft_cross_verification.json').write_text(json.dumps(report,indent=2)+'\n')
ledger_path=R/'qa/source_join_ledger.json';ledger=json.loads(ledger_path.read_text());new_names=added-{'D17_SeatedHullFooting_3','D17_SeatedHullFooting_4'}
ledger['contacts']=[row for row in ledger['contacts'] if row['part'] not in new_names]+contacts
ledger['scope']='All121 source meshes geometrically rooted; no physical load or complete floor acceptance'
assert len({row['part'] for row in ledger['contacts']})==121
ledger_path.write_text(json.dumps(ledger,indent=2)+'\n')
print(json.dumps({'pass':True,'preserved_objects':len(A),'new_meshes':len(added),'verified_contacts':len(contacts)}))
