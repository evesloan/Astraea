"""Frame-explicit conservative compound proposals; no baked whole-case hull.
Run standalone after geometry build or through the generator. No Blender required.
"""
from pathlib import Path
import json,math
ROOT=Path(__file__).resolve().parents[1]
def C(p):return [p[0],p[2],-p[1]]
def box(name,lo,hi,attach=None):
 r={'name':name,'type':'box','pose_frame':'asset frame at authored rest pose','min_blender_source_m':lo,'max_blender_source_m':hi,'min_gltf_yup_m':[lo[0],lo[2],-hi[1]],'max_gltf_yup_m':[hi[0],hi[2],-lo[1]]}
 if attach:r['follows_named_node']=attach
 return r
def cylinder(name,c,r,d,axis,attach=None):
 row={'name':name,'type':'cylinder','pose_frame':'asset frame at authored rest pose','centre_blender_source_m':c,'centre_gltf_yup_m':C(c),'axis_blender_source':axis,'axis_gltf_yup':C(axis),'radius_m':r,'length_m':d}
 if attach:row['follows_named_node']=attach
 return row
def profile(w,h,c):return [(-w/2+c,-h/2),(w/2-c,-h/2),(w/2,-h/2+c),(w/2,h/2-c),(w/2-c,h/2),(-w/2+c,h/2),(-w/2,h/2-c),(-w/2,-h/2+c)]
outer=profile(.82,.68,.06);inner=profile(.768,.628,.052);parts=[]
for i in range(8):
 j=(i+1)%8;poly=[outer[i],outer[j],inner[j],inner[i]];vv=[[x,y,z] for y in [-.212,-.079] for x,z in poly]
 parts.append({'name':'formed_case_perimeter_%02d'%i,'type':'convex_prism','pose_frame':'asset frame at authored rest pose','vertices_blender_source_m':vv,'vertices_gltf_yup_m':[C(p) for p in vv],'faces':[[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]})
parts.extend([
 box('rear_closure',[-.41,-.098,-.34],[.41,-.079,.34]),
 box('upper_recessed_control_face',[-.3825,-.185,-.195],[.3825,-.165,.311]),
 box('lower_face_return',[-.332,-.185,-.312],[.332,-.165,-.294]),
 box('fixed_vent_rear_baffle',[.014,-.162,-.275],[.280,-.158,-.219]),
 box('fixed_vent_left_pocket_wall',[.010,-.190,-.279],[.015,-.158,-.215]),
 box('fixed_vent_right_pocket_wall',[.280,-.190,-.279],[.285,-.158,-.215]),
 box('fixed_vent_bottom_pocket_wall',[.014,-.190,-.279],[.281,-.158,-.275]),
 box('fixed_vent_top_pocket_wall',[.014,-.190,-.219],[.281,-.158,-.215]),
])
for name,lo,hi in [
 ('hatch_left_plate',[-.328,-.197,-.288],[.014,-.187,-.206]),
 ('hatch_right_rim',[.280,-.197,-.288],[.328,-.187,-.206]),
 ('hatch_vent_top',[.014,-.197,-.219],[.280,-.187,-.206]),
 ('hatch_vent_bottom',[.014,-.197,-.288],[.280,-.187,-.275])]:parts.append(box(name,lo,hi,'SERVICE_removable_hatch'))
for name,x in [('START',-.263),('HOLD',-.127),('ISOLATE',.009)]:parts.append(cylinder('button_cap_'+name,[x,-.219,-.133],.0195,.015,[0,1,0],'CTRL_button_'+name))
parts.append(cylinder('selector_knob',[.263,-.222,-.099],.027,.023,[0,-1,0],'CTRL_mode_selector'))
parts.append(box('selector_grip',[.253,-.248,-.126],[.273,-.226,-.072],'CTRL_mode_selector'))
parts.append(cylinder('static_gauge_rim',[.258,-.197,.137],.077,.026,[0,-1,0]))
for x in [-.305,.305]:
 parts.append(box('mount_cleat_'+str(x),[x-.028,-.094,-.266],[x+.028,-.060,.266]))
 for z in [-.221,.221]:
  name='MOUNT_%s_%s'%('L' if x<0 else 'R','LOW' if z<0 else 'HIGH')
  parts.append(cylinder(name+'_standoff',[x,-.045,z],.022,.080,[0,1,0]));parts.append(cylinder(name+'_wall_pad',[x,-.0025,z],.034,.005,[0,1,0]))
r={'asset_id':'AST-ENG-003','revision':'console-compound-open-service-02','status':'Compound collision proposals only; no engine acceptance','source_frame':'Blender asset-source metres Z-up, front -Y, rest pose','exchange_frame':'glTF asset-frame metres Y-up, front +Z, rest pose; explicit transformed positions and directions','parts':parts,'attachment_rule':'Rest-pose values are asset-frame numeric coordinates, not node-local. Convert through the inverse actual rest-pose node world matrix when attaching a shape to follows_named_node, then inherit its live node pose. Do not double-transform native GLB points.','open_space_preservation':'Eight separate perimeter prisms, thin rear closure, upper face and lower return preserve the open lower service bay. Removable hatch is four frame shapes with an open vent; remove/transform only its own shapes with the named hatch node. Moving caps/grip use small named shapes; no broad control_front box or whole-case hull exists. Rear mounting void remains mostly empty.','omitted_fine_parts':'Thin vent fins, fasteners, labels, annular control sockets, cable tails and clip straps are intentionally omitted from collision proposals to preserve their small visual openings and control clearance. Engine implementation may add verified fine shapes where interaction needs them.','collision_limits':'Rear closure/upper face boxes conservatively fill tiny chamfer corners. Sealed rear plate is intentional. No gameplay device logic, character reach, room fit, pressure/fluid behavior, electrical safety or target-PC performance certification.'}
(ROOT/'collision_proposals.json').write_text(json.dumps(r,indent=2))
print('CONSOLE_OPEN_SERVICE_COLLISION_PROPOSALS_WRITTEN',len(parts))
