"""Editable original lower staff-network architecture, batched into 20 m runtime cells.
No general floors or dynamic parts. Coordinate/ownership source: section_contract.json.
"""
from pathlib import Path
import bpy,bmesh,json,hashlib,math,sys
from mathutils import Vector
R=Path(__file__).resolve().parents[1];C=R.parents[1];AID='AST-STF-009';FAMILY='lower_staff_network'
existing=json.loads((C/'catalogue_manifest.json').read_text())['assets']
assert all(a['catalogue_id']!=AID or a['family']==FAMILY for a in existing),'Catalogue ID already belongs to another family'
D=json.loads((R/'source/section_contract.json').read_text());D['light_markers']=[]
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
sys.path.insert(0,str(C/'standards'));import staff_materials
all_mats=staff_materials.materials();mats={k:all_mats[k]for k in ['staff_white_paint','staff_bluegrey_paint','staff_zinc','staff_rubber','staff_opal']}
for m in mats.values():
 for n in m.node_tree.nodes:
  if n.type=='TEX_IMAGE':n.interpolation='Closest'
bs=mats['staff_opal'].node_tree.nodes.get('Principled BSDF')
if bs is None:bs=next(n for n in mats['staff_opal'].node_tree.nodes if n.type=='BSDF_PRINCIPLED')
bs.inputs['Emission Color'].default_value=(.78,.88,.94,1);bs.inputs['Emission Strength'].default_value=.7
parts=[];boxes=[]
def split(a,b,cell=20):
 cuts=[a]+[v for v in range(math.floor(a/cell)*cell,math.ceil(b/cell)*cell+1,cell)if a+1e-7<v<b-1e-7]+[b]
 return list(zip(cuts,cuts[1:]))
def box(name,x0,x1,y0,y1,z0,z1,role,deck,collidable=True):
 assert x1>x0 and y1>y0 and z1>z0,(name,x0,x1,y0,y1,z0,z1)
 # Every authorable object is a closed outward cuboid. Split long pieces before batching.
 for xa,xb in split(x0,x1):
  for za,zb in split(z0,z1):
   vertices=[(x,-z,y)for y in [y0,y1]for x,z in [(xa,za),(xb,za),(xb,zb),(xa,zb)]]
   faces=[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
   me=bpy.data.meshes.new(name);me.from_pydata(vertices,[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
   ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);me.materials.append(mats[role]);ob['catalogue_id']=AID;ob['deck']=deck;ob['collision_contract']='concave_static_surface'if collidable else 'none';ob['cell_x']=math.floor((xa+xb)/40);ob['cell_z']=math.floor((za+zb)/40)
   uv=me.uv_layers.new(name='MetreScaled');scale=mats[role]['meters_per_tile_uv']
   for f in me.polygons:
    n=f.normal.normalized();u=(Vector((1,0,0))-n*n.x).normalized()if abs(n.z)>.7 else Vector((-n.y,n.x,0)).normalized();v=n.cross(u)
    for li in f.loop_indices:
     q=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(q.dot(u)/scale[0],q.dot(v)/scale[1])
   parts.append(ob);boxes.append({'name':ob.name,'world_aabb':[xa,xb,y0,y1,za,zb],'role':role,'deck':deck})
def datum(name,p,extras=None):
 o=bpy.data.objects.new(name,None);bpy.context.collection.objects.link(o);o.location=(p[0],-p[2],p[1]);o.empty_display_size=.12
 if extras:
  for k,v in extras.items():o[k]=v
 return o
def rect_cells(rectangles):
 xs=sorted({r[k]for r in rectangles for k in [0,1]});zs=sorted({r[k]for r in rectangles for k in [2,3]})
 # Grid cells are disjoint, so opaque ceilings never z-fight.
 for a,b in zip(xs,xs[1:]):
  for c,d in zip(zs,zs[1:]):
   if any(r[0]<=(a+b)/2<=r[1]and r[2]<=(c+d)/2<=r[3]for r in rectangles):yield a,b,c,d
# Boundary segments stay inside the exact floor polygon. All rings here are CCW in XZ.
for deck in D['decks']:
 n=deck['deck'];y=deck['floor_y'];prefix='STF_D%02d_'%n
 for i,(x0,x1,z0,z1)in enumerate(rect_cells(deck['floor_union_rectangles_x0_x1_z0_z1'])):
  box(prefix+'Ceiling_%03d'%i,x0,x1,y+3.2,y+3.34,z0,z1,'staff_bluegrey_paint',n)
 for ri,ring in enumerate(deck['floor_union_polygons_xz']):
  for ei,(a,b)in enumerate(zip(ring,ring[1:]+ring[:1])):
   axis='x'if a[0]==b[0]else'z';plane=a[0]if axis=='x'else a[1];lo,hi=sorted([a[1],b[1]]if axis=='x'else[a[0],b[0]])
   cuts=[lo,hi]
   ap=[]
   for door in deck['boundary_apertures']:
    if door['plane_axis']==axis and abs(door['plane']-plane)<1e-6:
     aa,bb=door['range'];aa=max(lo,aa);bb=min(hi,bb)
     if bb>aa:cuts.extend([aa,bb]);ap.append((aa,bb))
   # The left-hand side of a CCW edge is interior.
   inward=(1 if b[0]>a[0]else-1)if axis=='z'else(-1 if b[1]>a[1]else 1)
   for j,(aa,bb)in enumerate(zip(sorted(set(cuts)),sorted(set(cuts))[1:])):
    if any(c<=(aa+bb)/2<=d for c,d in ap):continue
    t0,t1=sorted([plane,plane+inward*.12]);label=prefix+'Wall_%02d_%02d_%02d'%(ri,ei,j)
    def wall(loy,hiy,role,t0=t0,t1=t1,suffix=''):
     box(label+suffix,aa,bb,loy,hiy,t0,t1,role,n)if axis=='z'else box(label+suffix,t0,t1,loy,hiy,aa,bb,role,n)
    wall(y,y+1.03,'staff_bluegrey_paint',suffix='_Wainscot');wall(y+1.03,y+3.2,'staff_white_paint',suffix='_Enamel')
    inner=plane+inward*.12;b0,b1=sorted([inner,inner+inward*.025]);wall(y+.73,y+.86,'staff_rubber',b0,b1,'_CartBumper')
    # Restrained panel seam at four-metre interval. Raised only 6 mm above wall face.
    s0,s1=sorted([inner,inner+inward*.006])
    for q in range(math.ceil(aa/4)*4,math.floor(bb/4)*4+1,4):
     if q-.01<aa or q+.01>bb:continue
     box(label+'_PanelJoint',q-.008,q+.008,y+1.04,y+3.14,s0,s1,'staff_zinc',n)if axis=='z'else box(label+'_PanelJoint',s0,s1,y+1.04,y+3.14,q-.008,q+.008,'staff_zinc',n)
# Opaque shaft. The gate pocket apertures are cut, never covered by a cross-wall.
for z0,z1 in [(-492.2,-492.04),(-487.96,-487.8)]:box('STF_ShaftSide',-27.12,-22.84,-.24,15.1,z0,z1,'staff_bluegrey_paint',0)
box('STF_ShaftRear',-27.12,-26.96,-.24,15.1,-492.04,-487.96,'staff_bluegrey_paint',0)
for z0,z1 in [(-492.04,-491.9),(-488.1,-487.96)]:box('STF_ShaftFrontJamb',-23,-22.84,-.2,15.1,z0,z1,'staff_bluegrey_paint',0)
for lo,hi in [(-.2,0),(2.85,6),(8.85,12),(14.85,15.1)]:box('STF_ShaftFrontSpandrel',-23,-22.84,lo,hi,-491.9,-488.1,'staff_bluegrey_paint',0)
box('STF_ShaftPitPan',-26.96,-23,-.24,-.2,-492.04,-487.96,'staff_zinc',0)
box('STF_ShaftTopCap',-27.12,-22.84,15.1,15.24,-492.2,-487.8,'staff_bluegrey_paint',0)
# Reusable fixtures aligned with the route, plus one landing strip and one threshold task strip.
for deck in D['decks']:
 n=deck['deck'];y=deck['floor_y'];positions=[(-21,-490,'z'),(-21,-497,'z')]
 positions += [(x,-500,'x')for x in [-29,-39,-49,-57]]
 end={1:-60,2:-432,3:-216}[n]
 positions += [(-57,z,'z')for z in range(-490,end,10)]
 positions += [(x,z,'x')for x,z in ({1:[(-50,-60)],2:[(-56,-432)],3:[(-51,-432),(-51,-216)]}[n])]
 for i,(x,z,orient)in enumerate(positions):
  name='STF_D%02d_TaskFixture_%03d'%(n,i)
  w,d=(1.35,.24)if orient=='x'else(.24,1.35)
  box(name+'_Housing',x-w/2,x+w/2,y+3.03,y+3.2,z-d/2,z+d/2,'staff_zinc',n)
  box(name+'_Lens',x-w/2+.045,x+w/2-.045,y+3.015,y+3.03,z-d/2+.035,z+d/2-.035,'staff_opal',n)
  marker='DATUM_light_D%02d_%03d'%(n,i);p=[x,y+3.005,z]
  datum(marker,p,{'profile':'staff_work','direction':'down','role':'corridor_task'});D['light_markers'].append({'name':marker,'position':p,'direction':[0,-1,0],'profile':'staff_work','suggested_range':7.5,'suggested_spot_angle_degrees':70,'deck':n})
 # Backing sits outside the leaf channels, directly behind the existing call sphere.
 box('STF_CallBacking_%02d'%n,-22.995,-22.895,y+1.10,y+1.58,-491.83,-491.47,'staff_zinc',n)
 # Gate header fixture east of gate frame and above its2.85 m top.
 box('STF_LandingHeader_%02d'%n,-22.84,-22.70,y+2.93,y+3.06,-491.62,-488.38,'staff_zinc',n)
 box('STF_LandingHeaderLens_%02d'%n,-22.695,-22.69,y+2.95,y+3.02,-490.64,-489.36,'staff_opal',n)
 datum('DATUM_stop_D%02d'%n,[-23.08,y,-490])
datum('DATUM_lift_parent',[-25,0,-490]);datum('DATUM_origin',[0,0,0])
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
(R/'source/section_contract.json').write_text(json.dumps(D,indent=2)+'\n')
(R/'source/geometry_parts.json').write_text(json.dumps({'catalogue_id':AID,'boxes':boxes},indent=2)+'\n')
bpy.ops.file.pack_all();src=R/'source'/(AID+'.blend');out=R/'exports'/(AID+'.glb');bpy.ops.wm.save_as_mainfile(filepath=str(src))
triangles=sum(len(o.data.polygons)*2 for o in parts);batches={}
for o in parts:
 key=(o['deck'],o['cell_x'],o['cell_z'],o.data.materials[0].name);batches.setdefault(key,[]).append(o)
for key,objects in sorted(batches.items()):
 bpy.ops.object.select_all(action='DESELECT')
 for o in objects:o.select_set(True)
 bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();ob=bpy.context.object;ob.name='STF_CELL_D%02d_X%d_Z%d_%s'%key
bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',export_yup=True,export_extras=True)
manifest={'catalogue_id':AID,'family':FAMILY,'name':'Screened lower staff lift and connected three-deck service corridors','source':'source/'+AID+'.blend','export':'exports/'+AID+'.glb','source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'export_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'triangles':triangles,'editable_part_count':len(parts),'runtime_mesh_batches':len(batches),'light_marker_count':len(D['light_markers']),'max_runtime_batch_plan_extent_m':20,'coordinate_contract':'source/section_contract.json','status':'Editable construction kit; source checks pending; runtime and visual acceptance delegated to integration task.'}
(R/(AID+'.manifest.json')).write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(manifest))
