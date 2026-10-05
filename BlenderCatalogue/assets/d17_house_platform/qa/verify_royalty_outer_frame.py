"""Exact prior-object preservation and geometric rooted contacts for held frame."""
import bpy, json, hashlib, subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1];C=R.parents[1]
BASE='37728e760344279c27d82baa76d0ac11409d7c1a'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=Path('/tmp/d17-outer-frame-baseline.blend')
old.write_bytes(subprocess.check_output(['git','-C',str(C),'show',BASE+':assets/d17_house_platform/source/AST-RES-005.blend']))
assert sha(old)=='f6ed3798fd88c43a82d9f87179f2d61188b658cd80fb5ca8ce4e7758898ebd2e'
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
assert all(B.get(n)==v for n,v in A.items()),'Prior source changed'
assert AM==BM
added=set(B)-set(A)
expected={'D17_SeatedHullFooting_5','D17_SeatedHullFooting_6','D17_RoyaltyPier_OuterFore','D17_RoyaltyPier_OuterAft','D17_RoyaltyOuterForeTransfer','D17_RoyaltyOuterAftTransfer','D17_RoyaltyOuterLongTransfer'}|{f'D17_RoyaltyOuter{plane}{kind}_{i:02d}' for plane in ['Fore','Aft','Long'] for kind in ['Rail','Brace'] for i in range(14)}
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
contacts=[]
for i,side in [(5,'Fore'),(6,'Aft')]:
 contacts.append(bearing(f'D17_SeatedHullFooting_{i}','D17_RoyaltyPier_Outer'+side))
 contacts.append(bearing('D17_RoyaltyPier_Outer'+side,'D17_RoyaltyOuter'+side+'Transfer'))
def side_contact(part,root,axis,part_edge,root_edge,min_area):
 a,b=bounds(part),bounds(root);assert abs(a[axis][part_edge]-b[axis][root_edge])<1e-5
 area=1
 for j in range(3):
  if j!=axis:area*=max(0,min(a[j][1],b[j][1])-max(a[j][0],b[j][0]))
 assert area>min_area,(part,root,area)
 contacts.append({'part':part,'root':root,'side_face_joint_m2':area,'type':'Geometric joint only; no connection-load acceptance'})
for side in ['Fore','Aft']:side_contact('D17_RoyaltyOuter'+side+'Transfer','D17_RoyaltyTransfer',0,0,1,1.4399)
side_contact('D17_RoyaltyOuterLongTransfer','D17_RoyaltyOuterForeTransfer',2,0,1,.9599)
side_contact('D17_RoyaltyOuterLongTransfer','D17_RoyaltyOuterAftTransfer',2,1,0,.9599)
def overlap(name,post,axes):
 o=bpy.data.objects[name];ps=points(name);bb=bounds(post);third=next(i for i in range(3) if i not in axes)
 face=next(f for f in o.data.polygons if max(ps[i][third] for i in f.vertices)-min(ps[i][third] for i in f.vertices)<1e-5)
 poly=[tuple(ps[i][j] for j in axes) for i in face.vertices]
 for axis,j in enumerate(axes):
  poly=clip(poly,axis,bb[j][0],True);poly=clip(poly,axis,bb[j][1],False)
 area=abs(sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(poly,poly[1:]+poly[:1])))/2
 aa=bounds(name);return area*max(0,min(aa[third][1],bb[third][1])-max(aa[third][0],bb[third][0]))
for name in sorted(added):
 if 'Footing' in name:continue
 for p in points(name):assert 107.59999<=p[0]<=116.40001 and 11.79999<=p[1]<=101.76001 and 28.99999<=p[2]<=46.60001,(name,p)
 if 'Rail' in name or 'Brace' in name:
  if 'OuterLong' in name:posts=['D17_RoyaltyPier_OuterFore','D17_RoyaltyPier_OuterAft'];axes=[1,2]
  elif 'OuterFore' in name:posts=['D17_RoyaltyPier_Fore','D17_RoyaltyPier_OuterFore'];axes=[0,1]
  else:posts=['D17_RoyaltyPier_InnerAft','D17_RoyaltyPier_OuterAft'];axes=[0,1]
  for post in posts:
   volume=overlap(name,post,axes);assert volume>.02,(name,post,volume)
   contacts.append({'part':name,'root':post,'actual_mesh_overlap_m3':volume})
census=json.loads((R/'qa/royalty_outer_frame_census.json').read_text());assert len(census['strips'])==3
assert all(len(r['slices'])==16 and all(not a['contacts'] for a in r['slices']) for r in census['strips'])
seats=json.loads((R/'qa/seated_contact_verification.json').read_text());assert seats['source_plane_seats_pass'] and len(seats['source_seats'])==7
report={'source_component_pass':True,'runtime_adoption_pass':False,'baseline_commit':BASE,'unchanged_objects':len(A),'new_meshes':len(added),'materials_and_packed_textures_exact':True,'contacts':contacts,'source_sha256':sha(R/'source/AST-RES-005.blend'),'export_sha256':sha(R/'exports/AST-RES-005.glb'),'hold':'Band03 strict source-to-retained-runtime1mm comparison fails; decoded imported hull shares the physics offset. New frame runtime fit untested. Floor/routes still unbuilt.'}
(R/'qa/royalty_outer_frame_verification.json').write_text(json.dumps(report,indent=2)+'\n')
p=R/'qa/source_join_ledger.json';ledger=json.loads(p.read_text());new_names=added-{'D17_SeatedHullFooting_5','D17_SeatedHullFooting_6'};ledger['contacts']=[a for a in ledger['contacts'] if a['part'] not in new_names]+contacts;ledger['scope']='All212 source meshes geometrically rooted; new runtime seat comparison remains failed/held';ledger['runtime_adoption_pass']=False
assert len({a['part'] for a in ledger['contacts']})==212
p.write_text(json.dumps(ledger,indent=2)+'\n')
print(json.dumps({'source_component_pass':True,'runtime_adoption_pass':False,'preserved_objects':len(A),'new_meshes':len(added),'contacts':len(contacts)}))
