"""Complete this package's fresh native with final entry equipment; never opens retained natives."""
import bpy,json,importlib.util
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(P/'source/aquatic_district.blend'))
s=importlib.util.spec_from_file_location('builder',P/'source/build_aquatic.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
for role in ['warm_stone','champagne_metal','warm_walnut','ivory_enamel']:m.M[role]=bpy.data.materials['ASTRAEA_'+role]
names=json.loads((P/'qa/source_geometry.json').read_text())
for name in names:
 o=bpy.data.objects[name];(m.F if o.get('kind')=='compiler_floor_proposal' else m.A).append(o)
m.A.extend(o for o in bpy.context.scene.objects if o.type=='EMPTY' and o.name.startswith('DATUM_'))
for i in range(2):
 datum=bpy.data.objects['DATUM_boarding_ring_'+str(i)+'_MOUNT_RESERVED'];delta=Vector((75+i*6,-241.5,45.612))-datum.location
 for o in bpy.context.scene.objects:
  if o.name.startswith('AQD__boarding_ring_'+str(i)+'__') or o.name=='DATUM_boarding_ring_'+str(i)+'_MOUNT_RESERVED':
   o.location+=delta
   if o.type=='MESH':o['support_owner']='wet_promenade'
if 'AQD__river_south_hoist_anchor' not in bpy.data.objects:m.entry_equipment()
if 'AQD__fixed_seat_mount_south_-0.28' not in bpy.data.objects:
 m.finish_supports()
 for o in bpy.context.scene.objects:
  if o.name.startswith('AQD__river_lounge_pad_'):o.location.z-=.02
for prefix in ['clean_towels','dirty_return']:
 delta=62.8-bpy.data.objects['AQD__'+prefix+'_carcass'].location.x
 for o in bpy.context.scene.objects:
  if o.name.startswith('AQD__'+prefix+'_') or o.name=='DATUM_'+prefix+'_STOCK_RESERVED':o.location.x+=delta
bpy.data.objects['AQD__cascade_hood_post'].location.y=-214.4
# Fit repair: recovery station is between runouts; never inside a slide basin.
o=bpy.data.objects['AQD__bearing_foot_3'];m.A.remove(o);bpy.data.objects.remove(o,do_unlink=True);m.box('bearing_foot_3',(99.7,44.15,231),(.5,.3,.5),'warm_stone')
for o in bpy.context.scene.objects:
 if o.name=='AQD__north_recovery_transfer_seat':o.location.x=75;o.location.y=-193.5
 if o.name.startswith('AQD__north_recovery_entry_tread_'):o.location.x=75
 if o.name.startswith('AQD__fixed_seat_mount_north_'):
  o.location.x=75+float(o.name.rsplit('_',1)[1]);o.location.y=-193.5
 if o.name=='DATUM_north_recovery_RECOVERY_RESERVED':o.location=Vector((75,-193.5,45.45))
 if o.name=='DATUM_north_recovery_AFK_WATER_RESERVED':o.location=Vector((75,-195.3,45.25))
 for x in [77.0,79.0]:
  if o.name=='AQD__north_entry_grab_'+str(x) or o.name=='AQD__north_entry_grab_anchor_'+str(x):o.location.x=x-3;o.name=o.name.replace('_'+str(x),'_'+str(x-3))
# Idempotent hoist translation from its anchor to the corrected dry station.
delta=Vector((73.5,-193.5,45.5))-bpy.data.objects['AQD__river_north_hoist_anchor'].location
for o in bpy.context.scene.objects:
 if o.name.startswith('AQD__river_north_hoist_') or o.name=='DATUM_river_north_hoist_CONTROL_AND_LOAD_RESERVED':o.location+=delta
loop=m.D['river']['bed_polygons'][0]['boundary'];loop=loop[:-1] if loop[0]==loop[-1] else loop
for i,(a,b) in enumerate(zip(loop,loop[1:]+loop[:1])):
 skip=(abs((a[0]+b[0])/2-78)<1.05 and (a[1]+b[1])/2>237.8) or (abs((a[0]+b[0])/2-75)<1.05 and (a[1]+b[1])/2<194.8)
 for suffix,y,h,w,role in [('wall',44.3,1.15,.12,'warm_stone'),('coping',45.45,.1,.26,'ivory_enamel')]:
  name='river_outer_'+suffix+'_'+str(i);o=bpy.data.objects.get('AQD__'+name)
  if skip and o is not None:
   m.A.remove(o);bpy.data.objects.remove(o,do_unlink=True)
  elif not skip and o is None:m.wall(name,a,b,y,h,w,role)
bpy.context.scene['source_plan_sha256']=__import__('hashlib').sha256((P/'docs/AQUATIC_CONSTRUCTION_PLAN.json').read_bytes()).hexdigest()
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(P/'source/aquatic_district.blend'))
m.save_evidence();m.export_exchange()
