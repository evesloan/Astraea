import bpy,json,math
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(BASE/'source/AST-AQU-006.blend'));seat=bpy.data.objects['recessed_tensioned_seat_membrane_with_drain_aperture'];contacts=[]
for x in(-.12,.12):
    hit,loc,normal,face=seat.ray_cast(Vector((x,-.06,1)),Vector((0,0,-1)));assert hit;contacts.append({'position_m':list(loc),'normal':list(normal),'status':'Measured surface location; actor contact remains a proposal'})
p=2.20;nominal=Vector((0,.605+.219*math.cos(p),.238+.306*math.sin(p)));normal=Vector((0,math.cos(p)/.219,math.sin(p)/.306)).normalized();hit,head,headnormal,face=bpy.data.objects['rear_pearl_headrest_crescent'].ray_cast(nominal+normal*.10,-normal);assert hit;head=list(head);drain=seat.ray_cast(Vector((0,-.06,1)),Vector((0,0,-1)))[0];assert not drain
out={'scope':'Saved source geometry measurements, not actor contact/rig or physics','seat_contacts':contacts,'headrest_contact_m':head,'headrest_contact_method':'Saved-source ray intersection on tessellated pearl skin, directed along analytic normal at t=pi/phi=2.20','center_vertical_ray_hits_membrane':drain,'drain_aperture_open':not drain};(BASE/'qa/measured_contacts.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))

# Reduced numerical collision proposals from the saved visual source.
indices=[row*64+j for row in(0,2,4,7)for j in range(0,64,4)];vertices=[list(seat.data.vertices[i].co)for i in indices];triangles=[]
for r in range(3):
    for j in range(16):
        a=r*16+j;b=r*16+(j+1)%16;c=(r+1)*16+(j+1)%16;d=(r+1)*16+j;triangles.extend([(a,c,b),(a,d,c)])
grips=[]
for side in('left','right'):
    ob=bpy.data.objects[side+'_arched_continuous_grip'];centers=[sum((ob.data.vertices[i*10+j].co for j in range(10)),Vector())/10 for i in range(21)];grips.append({'side':side,'capsules':[{'a_m':list(a),'b_m':list(b),'radius_m':.023}for a,b in zip(centers,centers[1:])]})
geom={'seat_surface':{'vertices_m':vertices,'top_triangles':triangles,'thickness_m':.012,'rows_from_source':[0,2,4,7],'angular_stride':4,'preserve_center_drain':True,'mesh_type':'Reduced open-centre top surface; build local patches or an engine-supported concave surface, never a global convex volume'},'grips':grips};(BASE/'qa/collision_geometry_samples.json').write_text(json.dumps(geom,indent=2)+'\n')
