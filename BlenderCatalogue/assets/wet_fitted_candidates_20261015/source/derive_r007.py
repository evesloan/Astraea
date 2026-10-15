from pathlib import Path
import json
D=Path(__file__).resolve().parent;s=(D/'build_fitted_r006.py').read_text().replace('r006','r007').replace('R006','R007').replace('F006','F007')
def sub(a,b):
 global s
 assert a in s,a
 s=s.replace(a,b)
# Entrance header stays,but the added low glass sill is removed from the actual ramp opening.
sub("  box(col,kit+'_F007_InnerWallFore',(64.2,102,-383.55),(64.35,103.5,-381.6),glass);box", "  box")
sub("(64.5,101.83,z)","(64.7,101.8466666667,z)")
anchor="  # Existing original inner screen receives"
insert='''  # Suspension rods connect the raised retained arrival canopy to exact source roof triangles.
  from mathutils.bvhtree import BVHTree
  bpy.context.view_layer.update()
  for i,(x,z)in enumerate([(x,z)for x in[66.,78.]for z in[-380.2,-376.5]]):
   hits=[]
   for roof_name in['RoofPanel0','RoofPanel1']:
    roof=made[roof_name];verts=[Gv(roof.matrix_world@v.co)for v in roof.data.vertices];polys=[list(p.vertices)for p in roof.data.polygons];tree=BVHTree.FromPolygons(verts,polys);loc,normal,index,distance=tree.ray_cast(Vector((x,107.61,z)),Vector((0,1,0)),2)
    if loc is not None:hits.append(loc.y)
   assert hits,(x,z,'No retained gable suspension witness')
   top=min(hits)+.02;box(col,kit+'_F007_CanopySuspension'+str(i),(x-.035,107.58,z-.035),(x+.035,top,z+.035),metal)
'''
sub(anchor,insert+anchor)
(D/'build_fitted_r007.py').write_text(s)
p=json.loads((D/'FITTED_SUCCESSOR_PLAN_r006.json').read_text());p['schema']='astraea.wet_fitted_successor.r007';p['status']='R007_ORIGINAL_CONTROLLER_ACCESS_CORRECTIONS_NATIVE_PENDING';p['QUIET']['retained_arrival_canopy_rigid_raise_m']=2.2;p['QUIET']['retained_canopy_new_underside_y']=107.4;p['QUIET']['original_canopy_source_unchanged']=True;p['TIDAL']['retained_floor_approach_x']=-96.1
(D/'FITTED_SUCCESSOR_PLAN_r007.json').write_text(json.dumps(p,indent=2)+'\n');(D/'verify_rigid_r007.py').write_text((D/'verify_rigid_r006.py').read_text().replace('r006','r007'))
