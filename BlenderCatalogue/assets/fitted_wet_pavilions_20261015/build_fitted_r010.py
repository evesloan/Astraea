from pathlib import Path
import bpy,json,hashlib,math
from mathutils import Vector,Matrix
D=Path(__file__).resolve().parent;P=D.parent;S=P/'immutable_inputs/Game/assets/group2_vip_pavilions';G=Path('/workspace/astraea-protected-integration-20261012/Game');plan=json.loads((D/'FITTED_SUCCESSOR_PLAN_r010.json').read_text());assert bpy.app.version[:3]==(4,3,2)
plan['TIDAL']['basin_translation_x']=-6.1
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.context.preferences.filepaths.save_version=0
B=lambda p:Vector((p[0],-p[2],p[1]));Gv=lambda p:Vector((p.x,p.z,-p.y));rosters=[];models=[];lights=[];doors=[];original_data=json.loads((P/'immutable_inputs/Game/data/group2_vip_pavilions/KITS_r003.json').read_text());meshes_by_kit={};fixture_mounts=[]
def bounds(o):
 ps=[Gv(o.matrix_world@Vector(v))for v in o.bound_box];return Vector(tuple(min(p[i]for p in ps)for i in range(3))),Vector(tuple(max(p[i]for p in ps)for i in range(3)))
def copy(source,col,name,world_origin,delta=(0,0,0)):
 o=source.copy();o.data=source.data;o.parent=None;o.matrix_world=Matrix.Translation(B(world_origin)+B(delta))@source.matrix_world;o.name='F010__'+name;col.objects.link(o);o['retained_source_mesh']=source.name;o['geometry_material_uv_unchanged']=True;rosters.append({'new':o.name,'source':source.name,'matrix_world_blender':[list(r)for r in o.matrix_world]});return o
def move_group(objects,anchor,target,angle=0):
 M=Matrix.Translation(B(target))@Matrix.Rotation(angle,4,'Z')@Matrix.Translation(-B(anchor))
 for o in objects:o.matrix_world=M@o.matrix_world

def mesh(col,name,vs,faces,mat):
 data=bpy.data.meshes.new(name);data.from_pydata([B(v)for v in vs],[],faces);data.update();centre=sum((v.co for v in data.vertices),Vector())/len(data.vertices)
 for face in data.polygons:
  if face.normal.dot(face.center-centre)<0:face.flip()
 data.update();assert all(face.normal.dot(face.center-centre)>0 for face in data.polygons),name
 o=bpy.data.objects.new(name,data);col.objects.link(o);data.materials.append(mat);o['versioned_fitted_adapter']=True;return o

def box(col,name,lo,hi,mat):
 vs=[(x,y,z)for y in[lo[1],hi[1]]for z in[lo[2],hi[2]]for x in[lo[0],hi[0]]];return mesh(col,name,vs,[(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)],mat)
def wedge_x(col,name,x0,x1,z0,z1,y0,y1,mat):
 t=.12;vs=[(x0,y0-t,z0),(x1,y1-t,z0),(x1,y1-t,z1),(x0,y0-t,z1),(x0,y0,z0),(x1,y1,z0),(x1,y1,z1),(x0,y0,z1)];return mesh(col,name,vs,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],mat)
def wedge_z(col,name,x0,x1,z0,z1,y0,y1,mat):
 t=.12;vs=[(x0,y0-t,z0),(x1,y0-t,z0),(x1,y1-t,z1),(x0,y1-t,z1),(x0,y0,z0),(x1,y0,z0),(x1,y1,z1),(x0,y1,z1)];return mesh(col,name,vs,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],mat)
def beam(col,name,a,b,width,depth,mat):
 a,b=Vector(a),Vector(b);d=(b-a).normalized();u=d.cross(Vector((0,1,0))).normalized()*width/2;v=u.normalized().cross(d).normalized()*depth/2;vs=[a-u-v,a+u-v,a+u+v,a-u+v,b-u-v,b+u-v,b+u+v,b-u+v];return mesh(col,name,vs,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],mat)
def rail(col,prefix,a,b,mat):
 beam(col,prefix+'_Top',a,b,.05,.06,mat);length=(Vector(b)-Vector(a)).length
 for i in range(max(2,math.ceil(length/2)+1)):
  f=i/(max(2,math.ceil(length/2)+1)-1);p=Vector(a).lerp(Vector(b),f);box(col,prefix+'_Post'+str(i),(p.x-.025,p.y-1.05,p.z-.025),(p.x+.025,p.y,p.z+.025),mat)
def chair_move(objects,seat,back,target,forward):
 a,b=bounds(seat);c=(a+b)/2;ba,bb=bounds(back);f=c-(ba+bb)/2;f.y=0;f.normalize();t=Vector(forward);angle=math.atan2(f.x*t.z-f.z*t.x,f.dot(t))*-1;move_group(objects,c,Vector(target),angle)
# Source immutable bytes are the only inputs;new fitted objects are separate copies.
for kit,origin in [('TIDAL',(-80,102,-370)),('QUIET',(80,102,-370))]:
 src=S/f'VIP_{kit}_r003.glb';expected=next(x['sha256']for x in original_data['exports']if x['kit']==kit);assert hashlib.sha256(src.read_bytes()).hexdigest()==expected;before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(src));imported=list(set(bpy.data.objects)-before);source={o.name.replace('G2VIP_'+kit+'_',''):o for o in sorted(imported,key=lambda x:x.name)if o.type=='MESH'}
 reference=bpy.data.collections.new('UNEXPORTED_'+kit+'_R003_REFERENCE');bpy.context.scene.collection.children.link(reference);reference.hide_render=True;reference.hide_viewport=True
 for o in imported:
  for c in list(o.users_collection):c.objects.unlink(o)
  reference.objects.link(o)
 col=bpy.data.collections.new('FITTED_'+kit+'_R010');bpy.context.scene.collection.children.link(col);made={};new=[];ivory=source['AftBack'].data.materials[0];stone=source['BearingPadFore'].data.materials[0];deck=source['TerraceFore'].data.materials[0];tank=source['TankFore'].data.materials[0];glass=source['ForeClerestory'].data.materials[0];metal=source['Column0'].data.materials[0];water=source['Water_Illustrative'].data.materials[0]
 def cp(name,delta=(0,0,0)):
  o=copy(source[name],col,'G2VIP_'+kit+'_'+name,origin,delta);made[name]=o;return o
 if kit=='TIDAL':
  dz=17.875
  skipped=('BearingPad','Terrace','VesselFloor','Tank','Water_Illustrative','ForePlinth','ForeClerestory','ChangingFront','ChangingHeader','ChangingSide','AftBack','AftWest','AftEast','AftRoof','PlantPartition')
  for name,o in source.items():
   lo,hi=bounds(o)
   if hi.z<=-4 and not name.startswith(skipped):
    if name.startswith(('RampRail','RampPost'))and hi.z < -5.8:continue
    cp(name,(0,0,dz))
  # Complete original12x6 basin and18m ramp retained as rigid geometry;water entry reoriented to a supported side landing.
  for name in ['VesselFloor','TankFore','TankAft','TankWest','TankEast','Water_Illustrative']:cp(name,(-6.1,0,dz))
  for name in [n for n in made if n.startswith(('WaterEntry','TransferSeat'))]:
   bpy.data.objects.remove(made.pop(name),do_unlink=True)
  entry=[]
  for name in source:
   if name.startswith('WaterEntry'):entry.append(cp(name))
  move_group(entry,(-79.8,102,-376.64),(-75.4,102,-360.8),math.pi/2)
  transfer=[cp(n)for n in source if n.startswith('TransferSeat')];chair_move(transfer,made['TransferSeat_Seat'],made['TransferSeat_BackPad'],(-72.7,103.93,-362.6),(-1,0,0))
  full=[bounds(o)for o in transfer];delta=-72.19-max(b.x for a,b in full)
  for o in transfer:o.matrix_world=Matrix.Translation(Vector((delta,0,0)))@o.matrix_world
  x0,x1=-95.8,-72.0;z0,z1=-365.825,-356.275;px0,px1=-87.3,-74.9;pz0,pz1=-364.525,-358.125
  for name,lo,hi in [('BearingPadFore',(x0,102,z0),(x1,102.12,-358.075)),('BearingPadEast',(px1,102,-358.075),(x1,102.12,z1)),('TerraceFore',(x0,102.12,z0),(x1,103.5,pz0)),('TerraceWest',(x0,102.12,pz0),(px0,103.5,pz1)),('TerraceEast',(px1,102.12,pz0),(x1,103.5,z1)),('TerraceAftMiddle',(-95,102.12,pz1),(-77,103.5,-358.075)),('TerraceAftLanding',(-77,102.12,pz1),(x1,103.5,z1))]:box(col,kit+'_F010_'+name,lo,hi,stone if 'Bearing'in name else deck)
  box(col,kit+'_F010_UpperCornerReceiving',(-95.8,103.3,-358.175),(-95,103.5,-358.075),deck)
  rail(col,kit+'_F010_LevelUpperDeckGuard',(-95.8,104.55,-358.1),(-77,104.55,-358.1),metal)
  made['OuterWall'].matrix_world=Matrix.Translation(Vector((-7.8,0,0)))@made['OuterWall'].matrix_world
  box(col,kit+'_F010_ForePlinth',(x0,103.5,z0),(x1,104.4,z0+.15),ivory);box(col,kit+'_F010_ForeClerestoryWet',(x0,104.4,z0+.075),(x1,107.5,z0+.15),glass);box(col,kit+'_F010_ForeClerestoryCove',(x1,106,z0+.075),(-64.2,107.5,z0+.15),glass)
  # Two source-changing rooms retain all original benches/lockers and original1.2x2.3m door apertures.
  centres=[-91.7,-88.3]
  for i,cx in enumerate(centres):
   props=[cp(n)for n in source if n.startswith((f'ChangingBench{i}',f'PersonalLocker{i}'))];move_group(props,(-80+[-13.45,-8.95][i],102,-359.9),(cx,102,-377.65),math.pi)
   xa,xb=cx-1.7,cx+1.7;front=-375.1;back=-380.25
   box(col,kit+f'_F010_ChangingBack{i}',(xa,102,back),(xb,105.4,back+.15),ivory)
   box(col,kit+f'_F010_ChangingSide{i}',(xa,102,back),(xa+.15,105.4,front),ivory)
   box(col,kit+f'_F010_ChangingFront{i}L',(xa,102,front-.15),(cx-.6,105.4,front),ivory);box(col,kit+f'_F010_ChangingFront{i}R',(cx+.6,102,front-.15),(xb,105.4,front),ivory);box(col,kit+f'_F010_ChangingHeader{i}',(cx-.6,104.3,front-.15),(cx+.6,105.4,front),ivory)
   box(col,kit+f'_F010_ChangingRoof{i}',(xa,105.4,back),(xb,105.6,front),ivory)
   doors.append({'kit':kit,'source_index':i,'at':[cx,102,front-.01],'yaw':math.pi})
  box(col,kit+'_F010_PlantPartition',(-86.6,102,-380.25),(-86.45,105.4,-375.1),ivory)
  # Open utility bay uses the retained court cover;retain original stair guard without a new crossing wall.
  for i,z in enumerate([-379.15,-378.,-376.85]):
   for prefix in ['TreatmentCabinet','ServicePanel']:
    o=cp(prefix+str(i));a,b=bounds(o);target=Vector((-84.1,(a.y+b.y)/2,z));move_group([o],(a+b)/2,target)
  for i in range(6):
   o=cp('TreatmentPipe'+str(i));a,b=bounds(o);move_group([o],(a+b)/2,(-84.65,(a.y+b.y)/2,-379.6+i*.6))
  o=cp('ServiceCounter');a,b=bounds(o);move_group([o],(a+b)/2,(-89.5,(a.y+b.y)/2,-382.25),math.pi/2)
  for i,cx in enumerate([-91.7,-88.3,-84.1]):
   token=['-13','-8.5','-2'][i]
   items=[cp(n)for n in source if n.startswith('DryLight'+token+'_')];a,b=bounds(made['DryLight'+token+'_Lens']);move_group(items,(a+b)/2,(cx,(a.y+b.y)/2,-377.5))
  a,b=bounds(made['DryLight-2_Mount']);box(col,kit+'_F010_UtilityLightMount',(-84.13,b.y-.02,-377.53),(-84.07,106.04,-377.47),metal)
  for i,(x,z)in enumerate([(x,z)for z in[-362.5,-359.5]for x in[-94.3,-92.0,-89.8]]):
   items=[made[n]for n in made if n.startswith('Rest'+str(i)+'_')];a,b=bounds(made[f'Rest{i}_Seat']);chair_move(items,made[f'Rest{i}_Seat'],made[f'Rest{i}_BackPad'],(x,(a.y+b.y)/2,z),(1,0,0))
  items=[made[n]for n in made if n.startswith('Towel')];a,b=bounds(made['TowelStation']);move_group(items,(a+b)/2,(-93.8,(a.y+b.y)/2,-364.2))
  for i,name in enumerate([n for n in made if n.startswith('GardenTile')]):
   o=made[name];a,b=bounds(o);move_group([o],(a+b)/2,([-95.0,-92.6,-90.2,-87.8][i%4],(a.y+b.y)/2,[-363.,-360.][i//4]))
  box(col,kit+'_F010_WaterEntryDryToe',(-75.25,103.405,-361.8),(-74.6,103.505,-359.8),metal)
 else:
  skipped=('BearingPad','Terrace','VesselFloor','Tank','Water_Illustrative','ArrivalRamp','GroundRampToe','RampRail','RampPost','WaterEntry','TransferSeat','InnerWall')
  for name in source:
   if not name.startswith(skipped):cp(name)
  # Original aft changing/private rooms remain unchanged. New basin clears retained desk and3D stair/lift volumes.
  xa,xb=71.,76.6;za,zb=-381.6,-374.4
  box(col,kit+'_F010_BasinBase',(xa,102.12,za),(xb,102.2,zb),tank)
  for name,lo,hi in [('Fore',(xa,102.2,za),(xb,103.5,za+.2)),('Aft',(xa,102.2,zb-.2),(xb,103.5,zb)),('West',(xa,102.2,za+.2),(xa+.2,103.5,zb-.2)),('East',(xb-.2,102.2,za+.2),(xb,103.5,zb-.2))]:box(col,kit+'_F010_Tank'+name,lo,hi,tank)
  box(col,kit+'_F010_Water_Illustrative',(xa+.2,103.39,za+.2),(xb-.2,103.4,zb-.2),water)
  h=102+13/18*1.5;wedge_x(col,kit+'_F010_RampLeg1',64.5,77.5,-383.6,-381.8,102.,h,deck);box(col,kit+'_F010_RampTurn',(77.5,h-.12,-383.6),(79.3,h,-381.6),deck);wedge_z(col,kit+'_F010_RampLeg2',77.5,79.3,-381.6,-376.6,h,103.5,deck);box(col,kit+'_F010_UpperLanding',(76.6,103.26,-376.6),(79.3,103.5,-374.3),deck)
  # Modelled underframes bear into the existing floor;structural capacity is still unadmitted.
  def support(name,x,z,top):
   box(col,kit+'_F010_'+name+'_Foot',(x-.09,101.98,z-.09),(x+.09,102.03,z+.09),metal)
   if top>102.015:box(col,kit+'_F010_'+name+'_Post',(x-.04,102.015,z-.04),(x+.04,top+.025,z+.04),metal)
  def girder(name,a,b):
   # Three explicit I-section members retain meaningful flange/web thickness.
   for token,dy,w,depth in [('Lower',-.085,.16,.03),('Web',0,.035,.14),('Upper',.085,.16,.03)]:
    beam(col,kit+'_F010_'+name+token,Vector(a)+Vector((0,dy,0)),Vector(b)+Vector((0,dy,0)),w,depth,metal)
  for i,z in enumerate([-383.55,-381.85]):girder('Ramp1Stringer'+str(i),(64.7,101.8466666667,z),(77.5,h-.17,z))
  for i,x in enumerate([64.7,68.,71.3,74.6,77.3]):
   y=102+(x-64.5)/12-.17;beam(col,kit+'_F010_Ramp1Cross'+str(i),(x,y,-383.55),(x,y,-381.85),.12,.18,metal)
   if i:
    for j,z in enumerate([-383.45,-381.95]):support('Ramp1Support'+str(i)+'_'+str(j),x,z,y-.065)
  for i,(x,z)in enumerate([(x,z)for x in[77.65,79.15]for z in[-383.45,-381.75]]):support('TurnSupport'+str(i),x,z,h-.10)
  for i,x in enumerate([77.55,79.25]):girder('Ramp2Stringer'+str(i),(x,h-.17,-381.6),(x,103.33,-376.6))
  for i,z in enumerate([-380.8,-378.8,-376.8]):
   y=h+(z+381.6)/12-.17;beam(col,kit+'_F010_Ramp2Cross'+str(i),(77.55,y,z),(79.25,y,z),.12,.18,metal)
   for j,x in enumerate([77.65,79.15]):support('Ramp2Support'+str(i)+'_'+str(j),x,z,y-.065)
  for i,(x,z)in enumerate([(x,z)for x in[76.75,79.15]for z in[-376.45,-374.45]]):support('UpperLandingSupport'+str(i),x,z,103.28)
  for side,z in[('Fore',-383.625),('Aft',-381.775)]:rail(col,kit+'_F010_Ramp1'+side,(64.5,103.05,z),(77.5,h+1.05,z),metal)
  rail(col,kit+'_F010_Ramp2Outside',(79.325,h+1.05,-381.6),(79.325,104.55,-376.6),metal);rail(col,kit+'_F010_Ramp2Inside',(77.475,h+1.05,-381.6),(77.475,104.55,-376.6),metal)
  rail(col,kit+'_F010_TurnFore',(77.5,h+1.05,-383.625),(79.325,h+1.05,-383.625),metal);rail(col,kit+'_F010_TurnEast',(79.325,h+1.05,-383.625),(79.325,h+1.05,-381.6),metal)
  rail(col,kit+'_F010_LandingEast',(79.325,104.55,-376.6),(79.325,104.55,-374.3),metal);rail(col,kit+'_F010_LandingAft',(76.6,104.55,-374.275),(79.325,104.55,-374.275),metal)
  entry=[cp(n)for n in source if n.startswith('WaterEntry')];move_group(entry,(80.2,102,-376.64),(76.1,102,-375.6),math.pi/2)
  transfer=[cp(n)for n in source if n.startswith('TransferSeat')];a,b=bounds(made['TransferSeat_Seat']);chair_move(transfer,made['TransferSeat_Seat'],made['TransferSeat_BackPad'],(78.7,(a.y+b.y)/2,-375.1),(-1,0,0));full=[bounds(o)for o in transfer];right=max(b.x for a,b in full);delta=79.24-right
  for o in transfer:o.matrix_world=Matrix.Translation(Vector((delta,0,0)))@o.matrix_world
  box(col,kit+'_F010_WaterEntryDryToe',(76.25,103.405,-376.6),(76.9,103.505,-374.6),metal)
  made['OverheadPlantCasing'].matrix_world=Matrix.Translation(Vector((0,0,.08)))@made['OverheadPlantCasing'].matrix_world
  # Suspension rods connect the raised retained arrival canopy to exact source roof triangles.
  from mathutils.bvhtree import BVHTree
  bpy.context.view_layer.update()
  for i,(x,z)in enumerate([(x,z)for x in[66.,76.]for z in[-380.2,-376.5]]):
   hits=[]
   for roof_name in['RoofPanel0','RoofPanel1']:
    roof=made[roof_name];verts=[Gv(roof.matrix_world@v.co)for v in roof.data.vertices];polys=[list(p.vertices)for p in roof.data.polygons];tree=BVHTree.FromPolygons(verts,polys);loc,normal,index,distance=tree.ray_cast(Vector((x,107.61,z)),Vector((0,1,0)),2)
    if loc is not None:hits.append(loc.y)
   assert hits,(x,z,'No retained gable suspension witness')
   top=min(hits)+.02;box(col,kit+'_F010_CanopySuspension'+str(i),(x-.035,107.58,z-.035),(x+.035,top,z+.035),metal)
  # Existing original inner screen receives a source-owned ground-level ramp portal;the retained district wall is untouched.
  box(col,kit+'_F010_InnerWallHeader',(64.2,106,-383.55),(64.35,107.5,-381.6),glass);box(col,kit+'_F010_InnerWallBody',(64.2,102,-381.6),(64.35,107.5,-376.05),glass)
  box(col,kit+'_F010_OuterWallLower',(95.65,102,-383.55),(95.8,103.5,-374.15),glass)
  for i,(x,z)in enumerate([(x,z)for z in[-382.,-379.,-376.]for x in[91.,94.5]]):
   items=[made[n]for n in made if n.startswith('Rest'+str(i)+'_')];a,b=bounds(made[f'Rest{i}_Seat']);chair_move(items,made[f'Rest{i}_Seat'],made[f'Rest{i}_BackPad'],(x,(a.y+b.y)/2-1.5,z),(1 if x==91 else-1,0,0))
  for i,(x,z)in enumerate([(92.75,-383.2),(92.75,-378.),(95.1,-377.4)]):
   items=[made[n]for n in made if n=='Planter'+str(i)or n.startswith('Reed'+str(i)+'_')];a,b=bounds(made['Planter'+str(i)]);move_group(items,(a+b)/2,(x,(a.y+b.y)/2-1.5,z))
  items=[made[n]for n in made if n.startswith('Towel')];a,b=bounds(made['TowelStation']);move_group(items,(a+b)/2,(78.5,(a.y+b.y)/2-1.5,-364.8))
  for i in range(2):doors.append({'kit':kit,'source_index':i,'at':[80+[-13.45,-8.95][i],102,-362.45],'yaw':0})
 # Positive base adapters join the original columns to the actual retained D17 floor;capacity remains unadmitted.
 for name in [n for n in made if n.startswith('Column')]:
  a,b=bounds(made[name]);cx=(a.x+b.x)/2;cz=(a.z+b.z)/2;box(col,kit+'_F010_ColumnBase_'+name,(cx-.12,101.98,cz-.12),(cx+.12,103.52,cz+.12),metal)
 # Bounded roof risers close the raised source gable against the retained surrounding106.02..106.26m cover.
 ox=origin[0];zfore=-383.7+(17.875 if kit=='TIDAL'else 0);zridge=-379+(17.875 if kit=='TIDAL'else 0);zaft=-374.15+(17.875 if kit=='TIDAL'else 0)
 def riser(name,a,b,ta,tb):
  ax,az=a;bx,bz=b;d=Vector((bx-ax,bz-az)).normalized();u=Vector((-d.y,d.x))*.04;vs=[]
  for sign in[-1,1]:vs.extend([(ax+u.x*sign,106.12,az+u.y*sign),(bx+u.x*sign,106.12,bz+u.y*sign),(bx+u.x*sign,tb,bz+u.y*sign),(ax+u.x*sign,ta,az+u.y*sign)])
  return mesh(col,kit+'_F010_Weather_'+name,vs,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],ivory)
 riser('Fore',(ox-16.05,zfore),(ox+16.05,zfore),107.54,107.54);riser('Aft',(ox+16.05,zaft),(ox-16.05,zaft),107.54,107.54)
 for side in[-1,1]:
  x=ox+side*16.05;riser('Side'+str(side)+'Fore',(x,zfore),(x,zridge),107.54,108.24);riser('Side'+str(side)+'Aft',(x,zridge),(x,zaft),108.24,107.54)
 # Four thin pitched eave extensions overlap the original roof edge;no source panel changes.
 for side in[-1,1]:
  xa,xb=sorted([ox+side*15.75,ox+side*16.1])
  for token,za,zb,ya,yb in [('Fore',zfore,zridge,107.495,108.195),('Aft',zridge,zaft,108.195,107.495)]:
   vs=[(xa,ya,za),(xb,ya,za),(xb,yb,zb),(xa,yb,zb),(xa,ya+.18,za),(xb,ya+.18,za),(xb,yb+.18,zb),(xa,yb+.18,zb)]
   mesh(col,kit+'_F010_EaveCap'+str(side)+token,vs,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],ivory)
 # Positive fixture-to-ceiling adapters;original fixture parts and source exit markers are unchanged.
 from mathutils.bvhtree import BVHTree
 bpy.context.view_layer.update()
 for name in[n for n in made if n.endswith('_Mount')and n.startswith(('WetLight','DryLight'))]:
  a,b=bounds(made[name]);cx=(a.x+b.x)/2;cz=(a.z+b.z)/2;target='';top=None
  if name.startswith('DryLight'):
   top=106.02 if kit=='TIDAL'and name=='DryLight-2_Mount'else 105.4;target='Retained_TG_Batch_283'if top>106 else 'ChangingRoof'
  elif kit=='QUIET'and name=='WetLight-6_Mount':top=107.4;target='Retained_QG_Batch_172_Raised2.2m'
  else:
   hits=[]
   for roof_name in['RoofPanel0','RoofPanel1']:
    roof=made[roof_name];verts=[Gv(roof.matrix_world@v.co)for v in roof.data.vertices];polys=[list(p.vertices)for p in roof.data.polygons];tree=BVHTree.FromPolygons(verts,polys);loc,normal,index,distance=tree.ray_cast(Vector((cx,b.y+.001,cz)),Vector((0,1,0)),2)
    if loc is not None:hits.append((loc.y,roof_name))
   assert hits,(kit,name,'No actual overhead face');top,target=min(hits)
  assert top>=b.y-.101,(kit,name,top,b.y)
  adapter=kit+'_F010_FixtureAdapter_'+name
  if top<b.y-.001:
   assert name.startswith('DryLight');adapter=made[name].name # Original mount already penetrates the original changing roof by100mm.
  elif kit=='TIDAL'and name=='DryLight-2_Mount':adapter=kit+'_F010_UtilityLightMount'
  else:box(col,adapter,(cx-.045,b.y-.02,cz-.045),(cx+.045,top+.02,cz+.045),metal)
  fixture_mounts.append({'kit':kit,'source_mount':made[name].name,'adapter':adapter,'base_y':b.y-.02,'ceiling_pin_xyz':[cx,top,cz],'target':target,'positive_contact_m':.02})
 bpy.context.view_layer.update()
 for row in original_data['lights']:
  if row['kit']!=kit:continue
  short=row['source_mesh'].replace('G2VIP_'+kit+'_','');lens=made[short];a,b=bounds(lens);loc=(a+b)/2;oa,ob=bounds(source[short]);loc+=Vector(row['local_xyz'])-(oa+ob)/2;lights.append({'kit':kit,'source_mesh':lens.name,'at':list(loc),'energy':row['energy'],'range':row['range']})
 bpy.context.view_layer.update()
 lo,hi=bounds(made['Column0']);assert abs((lo.y+hi.y)/2-105.5)<.001,(kit,'Source origin/column elevation lost',list(lo),list(hi))
 meshes_by_kit[kit]=col;T=D/'fitted_r010_import/Game/assets/fitted_wet_pavilions_20261015';T.mkdir(parents=True,exist_ok=True);file=f'VIP_{kit}_FITTED_r010.glb';bpy.ops.object.select_all(action='DESELECT')
 for o in col.objects:o.select_set(True)
 bpy.ops.export_scene.gltf(filepath=str(T/file),export_format='GLB',use_selection=True,export_yup=True,export_extras=True,export_cameras=False,export_lights=False)
 models.append({'kit':kit,'file':file,'sha256':hashlib.sha256((T/file).read_bytes()).hexdigest(),'meshes':len([o for o in col.objects if o.type=='MESH']),'source_sha256':expected,'roof_patch_world_x':[ox-16.05,ox+16.05],'roof_patch_world_z':[zfore,zaft]})
# Native retains both original unexported references and all explicit fitted geometry/parameters.
for image in bpy.data.images:
 if image.source=='FILE'and not image.packed_file:image.pack()
bpy.data.texts.new('FITTED_SUCCESSOR_PLAN_r010.json').write(json.dumps(plan,indent=2));N=D/'native';N.mkdir(exist_ok=True);native=N/'VIP_FITTED_SUCCESSORS_r010.blend';bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True);bpy.ops.wm.open_mainfile(filepath=str(native));F=D/'fitted_r010_fresh';F.mkdir(exist_ok=True)
for row in models:
 bpy.ops.object.select_all(action='DESELECT')
 for o in bpy.data.collections['FITTED_'+row['kit']+'_R010'].objects:o.select_set(True)
 path=F/row['file'];bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_yup=True,export_extras=True,export_cameras=False,export_lights=False);assert hashlib.sha256(path.read_bytes()).hexdigest()==row['sha256']
for row in models:assert hashlib.sha256((S/f"VIP_{row['kit']}_r003.glb").read_bytes()).hexdigest()==row['source_sha256']
rosters=[{'new':o.name,'source':str(o['retained_source_mesh']),'matrix_world_blender':[list(r)for r in o.matrix_world]}for kit in ['TIDAL','QUIET']for o in bpy.data.collections['FITTED_'+kit+'_R010'].objects if 'retained_source_mesh'in o]
receipt={'status':'PASS_NATIVE_FITTED_R010_FRESH_EXPORT_EXACT_RUNTIME_CHECKS_PENDING','native_sha256':hashlib.sha256(native.read_bytes()).hexdigest(),'models':models,'lights':lights,'doors':doors,'fixture_mounts':fixture_mounts,'rigid_source_roster':rosters,'original_source_bytes_unchanged':True,'Tidal_original12x6_basin_retained':True,'Quiet_fitted_basin_internal_m':[5.2,6.8,1.2],'new_capacity_room_registry_or_operating_admission':False,'water_load_body_weather_pressure_final_art_accepted':False};(D/'FITTED_NATIVE_VERIFICATION_r010.json').write_text(json.dumps(receipt,indent=2)+'\n');(D/'FITTED_SUCCESSOR_PLAN_r010.json').write_text(json.dumps(plan,indent=2)+'\n');print('PASS_FITTED_R010_NATIVE_EXPORT',[(r['kit'],r['meshes'])for r in models])
