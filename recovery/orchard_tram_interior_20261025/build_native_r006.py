"""New editable Orchard interior route/receiving package. Originals immutable."""
import bpy,bmesh,json,hashlib,math,importlib.util,sys
from pathlib import Path
from mathutils import Vector
import numpy as np
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[2];D=R/'Game/orchard_tram_interior_20261025/r006';N=R/'BlenderCatalogue/assets/orchard_tram_interior_20261025/r006'
plan=json.loads((D/'PLAN.json').read_text());screen=json.loads((D/'SOURCE_SCREEN.json').read_text());assert not screen['protected_hits']
for p,h in plan['source_pins'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
assert not N.exists();N.mkdir(parents=True)
assert not (D/'OrchardInteriorReceiving.glb').exists()
spec=importlib.util.spec_from_file_location('retained_author',R/'recovery/tram_section_successor_20261023/author_section_r002.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
def god(v):return np.array([v.x,v.z,-v.y])
def xyz(v):return(v[0],-v[2],v[1])
def bounds(o):
 v=np.array([god(o.matrix_world@q.co) for q in o.data.vertices]);return v.min(axis=0),v.max(axis=0)
def digest(o):
 # Native pre/post identity of all untouched source geometry and UV layers.
 data={'v':[list(v.co) for v in o.data.vertices],'faces':[list(p.vertices) for p in o.data.polygons],'matrix':[list(x) for x in o.matrix_world],'uv':[[list(x.uv) for x in layer.data] for layer in o.data.uv_layers]}
 return hashlib.sha256(json.dumps(data,separators=(',',':')).encode()).hexdigest()
def overlap(lo,hi,b):return all(lo[i]<b['hi'][i]-1e-6 and hi[i]>b['lo'][i]+1e-6 for i in range(3))
groups={};pre={};changed=[];new=[]
for owner,file,offset in [('Orchard','AST-RTL-009.glb',[4,52.5,-250]),('Retail','AST-RTL-007.glb',[8,52.5,-216])]:
 before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(R/'Game/assets/models'/file));objs=set(bpy.data.objects)-before
 roots=[o for o in objs if o.parent not in objs]
 for o in roots:o.location+=Vector(xyz(offset))
 bpy.context.view_layer.update();groups[owner]={'objects':objs,'roots':roots,'offset':offset,'file':file}
 for o in objs:
  if o.type=='MESH':pre[owner+'/'+o.name]=digest(o)
def cut(o,box,label):
 lo,hi=bounds(o)
 if not overlap(lo,hi,box):return
 bpy.ops.mesh.primitive_cube_add(size=1,location=xyz((np.array(box['lo'])+box['hi'])/2));c=bpy.context.object
 size=np.array(box['hi'])-box['lo'];c.scale=(size[0],size[2],size[1]);bpy.context.view_layer.objects.active=c;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 mod=o.modifiers.new('Exact receiving cut','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=c
 bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
 bpy.data.objects.remove(c,do_unlink=True);changed.append({'owner':label,'member':o.name,'operation':'bounded exact Boolean opening','box':box})
changes=plan['architectural_changes']
for o in list(groups['Orchard']['objects']):
 if o.type=='MESH' and o.name.startswith(('EX_NorthWall_52','EX_NorthRecess_52')):cut(o,changes['orchard_north_transport_opening'],'Orchard')
for o in list(groups['Retail']['objects']):
 if o.type!='MESH':continue
 if o.name.startswith(('TAIL_PublicWall','TAIL_PublicCeiling')):cut(o,changes['retail_shared_arrival_opening'],'Retail')
 if o.name.startswith(('TAIL_FrontGlass','TAIL_TerracottaFascia','TAIL_FrontMullion','TAIL_PromenadeCanopy')):
  cut(o,changes['retail_front_transport_opening'],'Retail')
  cut(o,{'lo':[4,52.5,-234.2],'hi':[10.3,60.1,-223.8]},'Retail')
# Retain fixture lenses/housings and source identities; fit their stems to the
# higher supported ceiling. Runtime marker/spot-range changes remain explicit.
lighting=[]
for owner,token,target,ceiling in [('Orchard','_1',60.2,60.76),('Retail','public_0',60.2,60.55)]:
 objs=groups[owner]['objects']
 lens=[o for o in objs if o.type=='MESH' and ((owner=='Orchard' and o.name=='EX_LampLens_1') or (owner=='Retail' and o.name=='TAIL_FixtureLens_public_0'))]
 assert len(lens)==1;delta=target-bounds(lens[0])[0][1]
 for o in objs:
  chosen=(o.name in ['EX_LampHousing_1','EX_LampLens_1','EX_LampMount_1','DATUM_light_1']) if owner=='Orchard' else token in o.name and any(k in o.name for k in ['Fixture','Pendant','DATUM_light','DATUM_bounce','DATUM_receiver'])
  if not chosen:continue
  if o.type=='MESH' and ('Mount' in o.name or 'Stem' in o.name):
   lo,hi=bounds(o);low=lo[1]+delta;assert low<ceiling
   inverse=o.matrix_world.inverted()
   for v in o.data.vertices:
    w=god(o.matrix_world@v.co);w[1]=low+(w[1]-lo[1])/(hi[1]-lo[1])*(ceiling-low);v.co=inverse@Vector(xyz(w))
  else:o.location.z+=delta
  lighting.append({'owner':owner,'member':o.name,'delta_y':delta,'spot_range_m':9 if owner=='Orchard' else 10})
  if o.type=='MESH':changed.append({'owner':owner,'member':o.name,'operation':'fixture retained and refitted to raised ceiling'})
bpy.context.view_layer.update()
unchanged=[]
changed_keys={r['owner']+'/'+r['member'] for r in changed}
for owner,g in groups.items():
 for o in g['objects']:
  if o.type=='MESH' and owner+'/'+o.name not in changed_keys:
   assert digest(o)==pre[owner+'/'+o.name],o.name;unchanged.append(owner+'/'+o.name)
  if o.type=='MESH' and o.name.startswith('TAIL_Entry'):assert digest(o)==pre[owner+'/'+o.name]
# Reuse the established exact route-ribbon cross sections.
points=np.array(plan['route_points_xz'])
a.ribbon('Orchard_ContinuousWeb',points,0,.22,55.55,55.68)
for side in [-1,1]:a.ribbon('Orchard_Rail_'+str(side),points,side*.39,.10,55.68,55.74)
def slab(name,x0,x1,z0,z1,y):a.box(name,[(x0+x1)/2,y-.12,(z0+z1)/2],[x1-x0,.24,z1-z0],'warm_stone','Public supported receiving floor')
slab('ForemidBoardingStage',9.7,14.9,-237.3,-231.86,56.1)
slab('ForemidLiftWestReturn',9.7,10.8,-231.86,-228,56.1)
slab('ForemidStairUpperLanding',7.1,9.7,-234,-231.6,56.1)
slab('ForemidStairMidLanding',4.1,9.7,-228.6,-226.6,54.3)
for i in range(10):
 z=-231.6+i*.3;slab('ForemidStairDown_%02d'%i,7.1,9.7,z,z+.3,56.1-(i+1)*.18)
 slab('ForemidStairUp_%02d'%i,4.1,6.7,z,z+.3,52.5+(i+1)*.18)
def rail(name,aa,bb,y):
 a.beam(name+'_rail',[aa[0],y+1.14,aa[1]],[bb[0],y+1.14,bb[1]],.10,.08,'warm_walnut')
 a.beam(name+'_infill',[aa[0],y+.64,aa[1]],[bb[0],y+.64,bb[1]],.024,.94,'glass')
for name,aa,bb,y in [('StageNorth',[9.7,-237.3],[14.9,-237.3],56.1),('StageWestNorth',[9.7,-237.3],[9.7,-234],56.1),('StageWestSouth',[9.7,-231.6],[9.7,-228],56.1),('MidSouth',[4.1,-226.6],[9.7,-226.6],54.3)]:rail(name,aa,bb,y)
for name,x,z0,z1,y0,y1 in [('DownOuter',9.7,-231.6,-228.6,56.1,54.3),('DownInner',7.1,-231.6,-228.6,56.1,54.3),('UpOuter',4.1,-231.6,-228.6,52.5,54.3),('UpInner',6.7,-231.6,-228.6,52.5,54.3)]:
 a.beam(name+'_handrail',[x,y0+1.14,z0],[x,y1+1.14,z1],.10,.08,'warm_walnut')
 a.beam(name+'_infill',[x,y0+.64,z0],[x,y1+.64,z1],.024,.94,'glass')
 a.beam(name+'_stringer',[x,y0-.26,z0],[x,y1-.26,z1],.15,.32)
# Same two-stop shaft/cabin identities; new pit receiving remains explicit.
for x in [10.9,15.1]:a.box('LiftSide_'+str(x),[x,55.89,-229.94],[.12,7.22,3.72],'ivory_enamel')
a.box('LiftRear',[13,55.89,-228.1],[4.3,7.22,.12],'ivory_enamel')
a.box('LiftCap',[13,59.39,-229.84],[4.3,.18,3.92],'ivory_enamel')
a.box('LiftPit',[13,52.24,-229.84],[4.3,.08,3.92],'warm_stone')
for z in [-237.05,-234.5]:
 for x in [9.9,14.9]:a.box('StationPier_%s_%s'%(x,z),[x,54.145,z],[.16,3.29,.16])
 a.beam('StationCrossbeam_'+str(z),[9.8,55.86,z],[15,55.86,z],.2,.24)
# Supported north transport opening, clear running top60.1.
for x in [14.95,19.65]:a.box('NorthPortalPier_'+str(x),[x,56.35,-249.72],[.2,7.7,.2],'warm_stone')
a.box('NorthPortalHeader',[17.3,60.35,-249.72],[4.9,.3,.2],'warm_stone')
# Exact existing public-roof footprint, clipped to the coordinated arrival zone.
retail=json.loads((R/'Game/data/architecture/D09_thread_shell.json').read_text())
for i,tri in enumerate(retail['public_triangles']):
 poly=[list(p) for p in tri]
 for axis,val,above in [(0,7.8,True),(0,23,False),(1,-237.5,True),(1,-217.7,False)]:poly=a.screen.clip(poly,axis,val,above) if poly else []
 if len(poly)>=3:a.prism('RaisedArrivalCanopy_%03d'%i,poly,60.55,60.75,'ivory_enamel')
# Route supports attach to actual D10 floor polygons, retaining all stair/lift voids.
layout=json.loads((R/'Game/data/generated/structural_meshes.json').read_text());floors=[v for v in layout['regions'] if v['floor_y']==61]
fit=a.PathFit(points);receivers=[];unresolved=[]
pose_rows=np.array(json.loads((D/'POSE_KNOTS.json').read_text()))
pose_rows=pose_rows[(pose_rows[:,0]>=plan['orchard_interval_m'][0]-3)&(pose_rows[:,0]<=plan['orchard_interval_m'][1]+3)]
def leg_clear(leg):
 delta=leg-pose_rows[:,1:3];c=np.cos(pose_rows[:,3]);ss=np.sin(pose_rows[:,3])
 lateral=abs(delta[:,0]*c-delta[:,1]*ss);forward=abs(delta[:,0]*ss+delta[:,1]*c)
 if np.any((lateral<2.10)&(forward<2.80)):return False
 # Preserve the core and occupied existing/new landing/stair/lift footprints.
 protected=[(-7.8,7.8,-285,-252),(7.9,14.1,-248.1,-237.45),(19.62,23.62,-243.66,-239.34),(9.6,15.3,-237.4,-227.8),(4.,9.8,-234.1,-226.5)]
 return not any(x0-.1<leg[0]<x1+.1 and z0-.1<leg[1]<z1+.1 for x0,x1,z0,z1 in protected)
for i,at in enumerate(np.arange(plan['orchard_interval_m'][0]+2,plan['orchard_interval_m'][1]-2,7.5)):
 q,t=fit.sample(at);normal=np.array([t[1],-t[0]])
 for side in [-1,1]:
  leg_options=[]
  for distance in [2.4,2.8,3.2,3.6,4.]:
   for along in [0,-1.,1.,-2.,2.,-3.,3.]:
    candidate=q+normal*side*distance+t*along
    if leg_clear(candidate):leg_options.append(((distance-2.4)**2+along**2,candidate))
  if not leg_options:unresolved.append({'cursor':float(at),'side':side,'reason':'No leg outside swept and occupied circulation'});continue
  _,leg=min(leg_options,key=lambda row:row[0]);choices=[]
  for dx,dz in [(0,0)]+[(dx,dz) for dx in [-8,-4,0,4,8] for dz in [-8,-4,0,4,8]]:
   pad=leg+np.array([dx,dz]);owners=a.screen.footprint_owners(pad,floors)
   if len(owners)==1 and abs(owners[0]['overlap_m2']-.0864)<1e-6:choices.append((dx*dx+dz*dz,pad,owners[0]))
  if not choices:unresolved.append({'cursor':float(at),'leg':leg.tolist()});continue
  _,pad,owner=min(choices,key=lambda r:r[0]);label='%s_%s'%(i,side)
  a.box('RouteBearing_'+label,[pad[0],60.79,pad[1]],[.24,.08,.36])
  a.beam('RouteDrop_'+label,[leg[0],55.72,leg[1]],[leg[0],60.5,leg[1]],.08,.08)
  a.beam('RouteOverarm_'+label,[leg[0],60.34,leg[1]],[pad[0],60.34,pad[1]],.18,.32) if np.linalg.norm(leg-pad)>1e-6 else None
  a.beam('RoutePadStub_'+label,[pad[0],60.34,pad[1]],[pad[0],60.79,pad[1]],.08,.08)
  shoe=q+normal*side*1.48;a.beam('RouteShoe_'+label,[shoe[0],55.60,shoe[1]],[leg[0],55.60,leg[1]],.38,.19)
  receivers.append({'cursor':float(at),'leg':leg.tolist(),'pad':pad.tolist(),'owner':owner})
mats={}
for role in ['champagne_metal','warm_stone','warm_walnut','ivory_enamel','glass']:
 found=next((m for m in bpy.data.materials if role.lower() in m.name.lower()),None)
 if found is None:
  found=bpy.data.materials.new('New_'+role);found.diffuse_color=(.6,.57,.50,1) if role!='glass' else(.25,.43,.46,.25)
 mats[role]=found
for part in a.parts:
 mesh=bpy.data.meshes.new(part['name']);mesh.from_pydata([xyz(v) for v in part['vertices']],[],part['faces']);mesh.update()
 bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free()
 o=bpy.data.objects.new(part['name'],mesh);bpy.context.collection.objects.link(o);mesh.materials.append(mats[part['material']]);o['physical_contact_required']=True
 # Real metre-scaled face UVs for the retained embedded texture palette.
 # Largest face-normal axis selects an orthogonal projection; no world shader.
 uv=mesh.uv_layers.new(name='MaterialMetres')
 tile={'warm_stone':2.0,'warm_walnut':1.0,'ivory_enamel':2.0,'champagne_metal':.5,'glass':2.0}[part['material']]
 for face in mesh.polygons:
  axis=max(range(3),key=lambda j:abs(face.normal[j]));axes=[j for j in range(3) if j!=axis]
  for loop_index in face.loop_indices:
   v=mesh.vertices[mesh.loops[loop_index].vertex_index].co
   uv.data[loop_index].uv=(v[axes[0]]/tile,v[axes[1]]/tile)
 new.append(o)
def export(path,objs):
 bpy.ops.object.select_all(action='DESELECT')
 for o in objs:o.select_set(True)
 bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_yup=True,export_extras=True)
export(D/'OrchardInteriorReceiving.glb',new)
for owner,g in groups.items():
 for root in g['roots']:root.location-=Vector(xyz(g['offset']))
 bpy.context.view_layer.update();export(D/(owner+'_receiving_successor.glb'),g['objects'])
 for root in g['roots']:root.location+=Vector(xyz(g['offset']))
bpy.context.view_layer.update();bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(N/'OrchardInteriorRoute.blend'))
receipt={'selected':False,'new_parts':len(new),'unchanged_native_members':unchanged,'changed_members':changed,'lighting':lighting,'receiver_bindings':receivers,'unresolved_receivers':unresolved,'original_entry_members_unchanged':True,'pit_receiving_required':{'deck':'D09','lo_xz':[10.8,-231.96],'hi_xz':[15.2,-227.94],'pit_y':[52.2,52.28]},'remaining':plan['remaining'],'files':{str(p.relative_to(R)).replace('\\','/'):{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [D/'OrchardInteriorReceiving.glb',D/'Orchard_receiving_successor.glb',D/'Retail_receiving_successor.glb',N/'OrchardInteriorRoute.blend']}}
(D/'BUILD.json').write_bytes((json.dumps(receipt,indent=2)+'\n').encode());print(json.dumps({'new_parts':len(new),'unchanged':len(unchanged),'changed':len(changed),'receivers':len(receivers),'unresolved':unresolved,'selected':False}))
