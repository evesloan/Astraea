"""Precisely bounded portal and staff-cap derivatives. All earlier originals stay untouched."""
from pathlib import Path
import bpy,bmesh,math,json,hashlib
from mathutils import Vector
R=Path(__file__).resolve().parents[1];C=R.parents[1];D=json.loads((R/'source/connected_contract.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for p,h in D['preserved_catalogue_inputs'].items():assert sha(C/p)==h,p
F=[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
def box(name,x0,x1,z0,z1,y0,y1,material,owner):
 assert x1>x0 and z1>z0 and y1>y0,name
 me=bpy.data.meshes.new(name);me.from_pydata([(x,-z,y)for y in[y0,y1]for x,z in[(x0,z0),(x1,z0),(x1,z1),(x0,z1)]],[],F);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);me.materials.append(material);uv=me.uv_layers.new(name='MetreScaled');scale=material.get('meters_per_tile_uv',[1,1])
 for p in me.polygons:
  n=p.normal.normalized();u=(Vector((1,0,0))-n*n.x).normalized()if abs(n.z)>.7 else Vector((-n.y,n.x,0)).normalized();v=n.cross(u)
  for li in p.loop_indices:
   q=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(q.dot(u)/scale[0],q.dot(v)/scale[1])
 o['parent_design_id']=owner;o['derivative_scope']='Grand Pool / Orchard connected section';return o

def datum(name,p,extras=None):
 o=bpy.data.objects.new(name,None);bpy.context.collection.objects.link(o);o.location=(p[0],-p[2],p[1]);o.empty_display_size=.12
 for k,v in(extras or{}).items():o[k]=v

def save_export(stem,owner):
 bpy.context.preferences.filepaths.save_version=0;bpy.ops.file.pack_all();src=R/'source'/(stem+'.blend');out=R/'exports'/(stem+'.glb');bpy.ops.wm.save_as_mainfile(filepath=str(src));meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];tri=0;batches={}
 for o in meshes:
  o.data.calc_loop_triangles();tri+=len(o.data.loop_triangles)
  if owner=='AST-CIR-005':key=(0,0,0,o.data.materials[0].name)
  else:
   vv=[v.co for v in o.data.vertices];x=sum(v.x for v in vv)/len(vv);z=-sum(v.y for v in vv)/len(vv);y=sum(v.z for v in vv)/len(vv);key=(math.floor(x/20),math.floor(z/20),math.floor(y/8.5),o.data.materials[0].name)
  batches.setdefault(key,[]).append(o)
 for key,obs in sorted(batches.items()):
  bpy.ops.object.select_all(action='DESELECT')
  for o in obs:o.select_set(True)
  bpy.context.view_layer.objects.active=obs[0];bpy.ops.object.join();bpy.context.object.name='DERIVATIVE_%d_%d_%d_%s'%key
 bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',export_yup=True,export_extras=True)
 manifest={'catalogue_id':owner,'representation':stem,'new_unique_design_count':0,'source':'source/'+src.name,'export':'exports/'+out.name,'source_sha256':sha(src),'export_sha256':sha(out),'editable_parts':len(meshes),'export_batches':len(batches),'triangles':tri,'status':'Bounded source derivative; preservation and runtime checks pending'}
 (R/(stem+'.manifest.json')).write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(manifest))
# Forward core: remove exactly the four selected port wall/dado objects, preserving all841 others.
bpy.ops.wm.open_mainfile(filepath=str(C/'assets/primary_atrium_core/source/AST-CIR-005_forward_core.blend'))
ivory=bpy.data.materials['ivory_enamel'];wood=bpy.data.materials['warm_walnut']
for level,y,ceil in[(7,44,52.26),(8,52.5,60.76)]:
 for n in['CORE_OuterWall_%02d_-1'%level,'CORE_WallDado_%02d_-1'%level]:bpy.data.objects.remove(bpy.data.objects[n],do_unlink=True)
 for label,z0,z1 in[('Fore',-13,-3),('Aft',3,20)]:
  box('GPM_CORE_OuterWall_%02d_%s'%(level,label),-7.88,-7.72,z0,z1,y,ceil,ivory,'AST-CIR-005')
  box('GPM_CORE_Dado_%02d_%s'%(level,label),-7.685,-7.635,z0,z1,y+.12,y+.78,wood,'AST-CIR-005')
 box('GPM_CORE_PortalHeader_%02d'%level,-7.88,-7.72,-3,3,y+3.2,ceil,ivory,'AST-CIR-005')
 datum('DATUM_GPM_portal_D%02d'%(level+1),[-7.8,y,0],{'world_translation':[0,0,-432]})
save_export('AST-CIR-005_forward_pool_market','AST-CIR-005')
# Staff derivative: old cap alone removed. All original lower walls, fixtures, datum and stop evidence retained.
bpy.ops.wm.open_mainfile(filepath=str(C/'assets/lower_staff_network/source/AST-STF-009.blend'))
removed=[o for o in bpy.context.scene.objects if o.name.startswith('STF_ShaftTopCap')];assert len(removed)==1,[o.name for o in removed]
bpy.data.objects.remove(removed[0],do_unlink=True)
mats={r:next(m for m in bpy.data.materials if m.get('astraea_material_role')==r)for r in['staff_white_paint','staff_bluegrey_paint','staff_zinc','staff_rubber','staff_opal']}
def sb(n,x0,x1,z0,z1,y0,y1,role='staff_bluegrey_paint'):return box(n,x0,x1,z0,z1,y0,y1,mats[role],'AST-STF-009')
for z0,z1 in[(-492.2,-492.04),(-487.96,-487.8)]:sb('GPM_STF_UpperShaftSide',-27.12,-22.84,z0,z1,15.1,55.6)
sb('GPM_STF_UpperShaftRear',-27.12,-26.96,-492.04,-487.96,15.1,55.6)
for z0,z1 in[(-492.04,-491.9),(-488.1,-487.96)]:sb('GPM_STF_UpperFrontJamb',-23,-22.84,z0,z1,15.1,55.6)
for y0,y1 in[(15.1,46.2),(49.05,52.5),(55.35,55.6)]:sb('GPM_STF_UpperFrontSpandrel',-23,-22.84,-491.9,-488.1,y0,y1)
sb('GPM_STF_NewCap',-27.12,-22.84,-492.2,-487.8,55.6,55.74)
D['staff']['upper_light_markers']=[]
# Boundary thickness is placed inside exact compiler floor. Gate/open end cuts are explicit.
for y,deck in[(46.2,8),(52.5,9)]:
 floor=next(f for f in D['floor_regions']if f['id']==('D08_grand_pool_upper_staff'if deck==8 else'D09_orchard_market_upper_staff'));ring=floor['boundary']
 area=sum(a[0]*b[1]-b[0]*a[1]for a,b in zip(ring,ring[1:]+ring[:1]))
 if area<0:ring=list(reversed(ring))
 for a,b in zip(ring,ring[1:]+ring[:1]):
  axis='x'if a[0]==b[0]else'z';plane=a[0]if axis=='x'else a[1];lo,hi=sorted([a[1],b[1]]if axis=='x'else[a[0],b[0]])
  cuts=[lo,hi];holes=[]
  if axis=='x'and abs(plane+23.18)<1e-5:holes=[(-491.9,-488.1)]
  if axis=='x'and abs(plane+54)<1e-5:holes=[(-464.8,-461.2)]
  for aa,bb in holes:
   if lo<aa<hi:cuts.append(aa)
   if lo<bb<hi:cuts.append(bb)
  inward=(-1 if b[1]>a[1]else 1)if axis=='x'else(1 if b[0]>a[0]else-1);t0,t1=sorted([plane,plane+inward*.12])
  for aa,bb in zip(sorted(cuts),sorted(cuts)[1:]):
   if any(c<=(aa+bb)/2<=d for c,d in holes):continue
   for y0,y1,role in[(y,y+1.03,'staff_bluegrey_paint'),(y+1.03,y+3.2,'staff_white_paint')]:
    sb('GPM_STF_D%02d_Wall'%deck,t0,t1,aa,bb,y0,y1,role)if axis=='x'else sb('GPM_STF_D%02d_Wall'%deck,aa,bb,t0,t1,y0,y1,role)
 # Exact floor triangles make a fitted continuous overhead cover, no double rectangles.
 for i,t in enumerate(floor['triangles']):
  n=len(t);me=bpy.data.meshes.new('GPM_STF_Ceiling');me.from_pydata([(x,-z,h)for h in[y+3.2,y+3.34]for x,z in t],[],[(2,1,0),(3,4,5),(0,1,4,3),(1,2,5,4),(2,0,3,5)]);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();o=bpy.data.objects.new('GPM_STF_D%02d_Ceiling_%03d'%(deck,i),me);bpy.context.collection.objects.link(o);me.materials.append(mats['staff_bluegrey_paint']);uv=me.uv_layers.new(name='MetreScaled')
  for p in me.polygons:
   for li in p.loop_indices:q=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(q.x,q.y+q.z)
 for i,(x,z)in enumerate([(-21,-490),(-21,-497),(-29,-500),(-39,-500),(-49,-500),(-57,-500),(-57,-490),(-57,-480),(-57,-470),(-56,-463)]):
  sb('GPM_STF_FixtureHousing',x-.55,x+.55,z-.16,z+.16,y+3.03,y+3.2,'staff_zinc');sb('GPM_STF_FixtureLens',x-.48,x+.48,z-.11,z+.11,y+3.015,y+3.03,'staff_opal');name='DATUM_GPM_staff_light_D%02d_%02d'%(deck,i);p=[x,y+3.005,z];datum(name,p,{'profile':'staff_work'});D['staff']['upper_light_markers'].append({'name':name,'position_xyz':p,'direction':[0,-1,0],'suggested_range_m':7.5,'profile':'staff_work'})
 sb('GPM_STF_CallBacking',-22.995,-22.895,-491.83,-491.47,y+1.1,y+1.58,'staff_zinc');sb('GPM_STF_LandingHeader',-22.84,-22.7,-491.62,-488.38,y+2.93,y+3.06,'staff_zinc');datum('DATUM_GPM_staff_stop_D%02d'%deck,[-23.08,y,-490])
(R/'source/connected_contract.json').write_text(json.dumps(D,indent=2)+'\n')
save_export('AST-STF-009_pool_market','AST-STF-009')
