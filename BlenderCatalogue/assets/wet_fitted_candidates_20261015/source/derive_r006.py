from pathlib import Path
import json
D=Path(__file__).resolve().parent
s=(D/'build_fitted_r005.py').read_text().replace('r005','r006').replace('R005','R006').replace('F005','F006')
def sub(a,b):
 global s
 assert a in s,a
 s=s.replace(a,b)
sub("plan['TIDAL']['basin_translation_x']=-5.5","plan['TIDAL']['basin_translation_x']=-6.1")
sub("cp(name,(-5.5,0,dz))","cp(name,(-6.1,0,dz))")
sub("(-74.8,102,-360.8)","(-75.4,102,-360.8)")
sub("(-71.8,103.93,-362.6)","(-72.7,103.93,-362.6)")
sub("  x0,x1=-95.8,-71.1;z0,z1=-365.825,-356.275;px0,px1=-86.7,-74.3", "  full=[bounds(o)for o in transfer];delta=-72.19-max(b.x for a,b in full)\n  for o in transfer:o.matrix_world=Matrix.Translation(Vector((delta,0,0)))@o.matrix_world\n  x0,x1=-95.8,-72.0;z0,z1=-365.825,-356.275;px0,px1=-87.3,-74.9")
sub('Vector((-6.9,0,0))','Vector((-7.8,0,0))')
sub(";box(col,kit+'_F006_PlantEast',(-83.55,102,-380.25),(-83.4,105.4,-375.1),ivory);box(col,kit+'_F006_PlantRoof',(-86.6,105.4,-380.25),(-83.4,105.6,-375.1),ivory)", "\n  # Open utility bay uses the retained court cover;retain original stair guard without a new crossing wall.")
sub("[-94.3,-91.5,-89.2]","[-94.3,-92.0,-89.8]")
sub("(-74.65,103.405,-361.8),(-74.,103.505,-359.8)","(-75.25,103.405,-361.8),(-74.6,103.505,-359.8)")
sub("(94.1,(a.y+b.y)/2-1.5,-380.6)","(78.5,(a.y+b.y)/2-1.5,-364.8)")
sub("  for i,(x,z)in enumerate([(x,z)for z in[-362.5", "  a,b=bounds(made['DryLight-2_Mount']);box(col,kit+'_F006_UtilityLightMount',(-84.13,b.y-.02,-377.53),(-84.07,106.04,-377.47),metal)\n  for i,(x,z)in enumerate([(x,z)for z in[-362.5")
# Roof collar widened250mm within the original34m pavilion footprint.
sub('ox-15.8','ox-16.05');sub('ox+15.8','ox+16.05');sub('side*15.8','side*16.05')
anchor=' bpy.context.view_layer.update()\n for row in original_data'
insert=''' # Four thin pitched eave extensions overlap the original roof edge;no source panel changes.
 for side in[-1,1]:
  xa,xb=sorted([ox+side*15.75,ox+side*16.1])
  for token,za,zb,ya,yb in [('Fore',zfore,zridge,107.495,108.195),('Aft',zridge,zaft,108.195,107.495)]:
   vs=[(xa,ya,za),(xb,ya,za),(xb,yb,zb),(xa,yb,zb),(xa,ya+.18,za),(xb,ya+.18,za),(xb,yb+.18,zb),(xa,yb+.18,zb)]
   mesh(col,kit+'_F006_EaveCap'+str(side)+token,vs,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],ivory)
'''
sub(anchor,insert+anchor)
anchor="  for side,z in[('Fore',-383.625)"
insert='''  # Modelled underframes bear into the existing floor;structural capacity is still unadmitted.
  def support(name,x,z,top):
   box(col,kit+'_F006_'+name+'_Foot',(x-.09,101.98,z-.09),(x+.09,102.03,z+.09),metal)
   if top>102.015:box(col,kit+'_F006_'+name+'_Post',(x-.04,102.015,z-.04),(x+.04,top+.025,z+.04),metal)
  def girder(name,a,b):
   # Three explicit I-section members retain meaningful flange/web thickness.
   for token,dy,w,depth in [('Lower',-.085,.16,.03),('Web',0,.035,.14),('Upper',.085,.16,.03)]:
    beam(col,kit+'_F006_'+name+token,Vector(a)+Vector((0,dy,0)),Vector(b)+Vector((0,dy,0)),w,depth,metal)
  for i,z in enumerate([-383.55,-381.85]):girder('Ramp1Stringer'+str(i),(64.5,101.83,z),(77.5,h-.17,z))
  for i,x in enumerate([64.7,68.,71.3,74.6,77.3]):
   y=102+(x-64.5)/12-.17;beam(col,kit+'_F006_Ramp1Cross'+str(i),(x,y,-383.55),(x,y,-381.85),.12,.18,metal)
   if i:
    for j,z in enumerate([-383.45,-381.95]):support('Ramp1Support'+str(i)+'_'+str(j),x,z,y-.065)
  for i,(x,z)in enumerate([(x,z)for x in[77.65,79.15]for z in[-383.45,-381.75]]):support('TurnSupport'+str(i),x,z,h-.10)
  for i,x in enumerate([77.55,79.25]):girder('Ramp2Stringer'+str(i),(x,h-.17,-381.6),(x,103.33,-376.6))
  for i,z in enumerate([-380.8,-378.8,-376.8]):
   y=h+(z+381.6)/12-.17;beam(col,kit+'_F006_Ramp2Cross'+str(i),(77.55,y,z),(79.25,y,z),.12,.18,metal)
   for j,x in enumerate([77.65,79.15]):support('Ramp2Support'+str(i)+'_'+str(j),x,z,y-.065)
  for i,(x,z)in enumerate([(x,z)for x in[76.75,79.15]for z in[-376.45,-374.45]]):support('UpperLandingSupport'+str(i),x,z,103.28)
'''
sub(anchor,insert+anchor)
(D/'build_fitted_r006.py').write_text(s)
p=json.loads((D/'FITTED_SUCCESSOR_PLAN_r005.json').read_text());p['schema']='astraea.wet_fitted_successor.r006';p['status']='R006_BOUNDED_CONTACT_RELIEF_NATIVE_PENDING';p['TIDAL'].update(basin_translation_x=-6.1,deck_world_x=[-95.8,-72],roof_patch_world_x=[-96.05,-63.95],utility_bay='Open under retained106.02m cover;original stair guard remains',retained_cove_partition_max_x=-72.0);p['QUIET']['roof_patch_world_x']=[63.95,96.05];p['QUIET']['ramp_modelled_underframes']=True;p['both']['eave_extension_max_y']=108.375
(D/'FITTED_SUCCESSOR_PLAN_r006.json').write_text(json.dumps(p,indent=2)+'\n')
(D/'verify_rigid_r006.py').write_text((D/'verify_rigid_r005.py').read_text().replace('r005','r006'))
print('R006 authoring source prepared')
