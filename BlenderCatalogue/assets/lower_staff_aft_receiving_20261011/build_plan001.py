from pathlib import Path
import json,hashlib
from shapely.geometry import box,mapping
from shapely.ops import unary_union,triangulate
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.load(open(W/'PLAN.json'));sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
for f,h in P['source_pins'].items():assert sha(R/f)==h,f
S=json.load(open(W/'SITE_PREFLIGHT005.json'))
assert all(x['accepted']for x in S['support_feet'])
assert all(not x['blockers']for x in S['candidate_volumes']),S['candidate_volumes']
assert all(not x['meshes']for x in S['source_seams']),S['source_seams']
P['active']=False;P['parts']=[];P['lights']=[];P['runtime_preimages']=[];P['support_preimages']=S['support_feet'];P.pop('cut',None)
P['selection']='Enclosed shared D01 service circuit:original aft apron X-48/Z76 to original aft main spine X-4/Z300;no original source cuts'
P['service_doors']=[{'name':'CentralSharedStaffDoor','at':[-48,0,76],'yaw':1.5707963267948966,'id':'d01_central_shared_aft_staff_door_001'},{'name':'AftSpineSharedStaffDoor','at':[-4.1,0,300],'yaw':1.5707963267948966,'id':'d01_aft_spine_shared_staff_door_001'}]
P['limits']=[x for x in P['limits']if'concourse'not in x.lower()]+['Original aft apron and aft main spine are shared upstream/downstream;physical doors do not establish staff permissions or clean/used segregation','No original source cuts or programme floor/ceiling edits','Concourse recorded editable native path is unresolved;this package leaves its source unchanged']
P['unresolved_source_reference']={'path':'BlenderCatalogue/assets/received_sections_20261008/A/D01_directory_09/source/native.blend','expected_native_sha256':None,'source_archive_sha256':'91fa1ca67e8d74c6c1eabb0fc11f08acccbeb4fee62e38b4957d3bf815d97551','retained_runtime_sha256':P['source_pins']['Game/assets/models/SOL_D01_directory_09_source001.glb'],'scope':'Recorded local editable path absent;no claim of native byte loss/recovery or substitution;no derivative of this source made'}
P['source_pins']['BlenderCatalogue/assets/staff_threshold/source/AST-STF-008.blend']=sha(R/'BlenderCatalogue/assets/staff_threshold/source/AST-STF-008.blend')
poly=unary_union([box(-58.3,74.2,-54.7,301.8),box(-58.3,74.2,-48,77.8),box(-58.3,298.2,-4,301.8)])
faces=[[3,2,1,0],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]
def add(name,lo,hi,role='staff_bluegrey_paint',category='wall'):
 x,y,z=lo;X,Y,Z=hi;assert X>x and Y>y and Z>z
 q={'name':'LSA_'+name,'verts':[[a,b,c]for b in[y,Y]for a,c in[(x,z),(X,z),(X,Z),(x,Z)]],'faces':faces,'role':role,'category':category,'runtime_collision':True};P['parts'].append(q);return q
for label,lo,hi,role,cat in [('Floor',-.24,0,'staff_floor','floor'),('Roof',3.2,3.34,'staff_bluegrey_paint','roof')]:
 for i,t in enumerate(triangulate(poly)):
  if not poly.covers(t.representative_point()):continue
  q=list(t.exterior.coords)[:-1];P['parts'].append({'name':'LSA_'+label+str(i),'verts':[[x,y,z]for y in[lo,hi]for x,z in q],'faces':[[2,1,0],[3,4,5],[0,1,4,3],[1,2,5,4],[2,0,3,5]],'category':cat,'role':role,'runtime_collision':True})
coords=list(poly.exterior.coords)
for i,(a,b)in enumerate(zip(coords,coords[1:])):
 x,z=a;X,Z=b
 #Source contacts keep a full 2.8m opening;the original door seals the new enclosure.
 if abs(x-X)<1e-6 and x in [-48,-4]:
  center=76 if x==-48 else 300
  for j,(start,end)in enumerate([(min(z,Z),center-1.4),(center+1.4,max(z,Z))]):
   if end>start:add('EntryJamb'+str(i)+'_'+str(j),(x-.06,0,start),(x+.06,3.2,end),'staff_zinc','wall')
  add('EntryHeader'+str(i),(x-.06,2.85,center-1.4),(x+.06,3.2,center+1.4),'staff_zinc','wall')
  continue
 lo=(x-.06,0,min(z,Z))if abs(x-X)<1e-6 else(min(x,X),0,z-.06)
 hi=(x+.06,3.2,max(z,Z))if abs(x-X)<1e-6 else(max(x,X),3.2,z+.06)
 #Institutional lower paint and pale upper panel meet without open-head gaps.
 add('WallLow'+str(i),lo,(hi[0],1.0,hi[2]));add('WallHigh'+str(i),(lo[0],1,lo[2]),hi,'staff_white_paint')
P['wall_ceiling_junctions']=[{'wall':q['name'],'top_y':max(v[1]for v in q['verts']),'actual_roof_bottom_y':3.2}for q in P['parts']if q['category']=='wall'and max(v[1]for v in q['verts'])==3.2]
for j,(x,X,z,Z)in enumerate([(-58.24,-58,74.2,301.8),(-55,-54.76,74.2,301.8),(-58.3,-48,74.26,74.5),(-58.3,-48,77.5,77.74),(-58.3,-4,298.26,298.5),(-58.3,-4,301.5,301.74)]):add('FloorStringer'+str(j),(x,-.45,z),(X,-.24,Z),'staff_zinc','frame')
for i,row in enumerate(S['support_feet']):
 x,_,z=row['top'];y=row['source_max_y'];assert y<-.53
 add('HullShoe'+str(i),(x-.12,y,z-.12),(x+.12,y+.08,z+.12),'staff_zinc','support')
 add('HullColumn'+str(i),(x-.12,y+.08,z-.12),(x+.12,-.45,z+.12),'staff_zinc','support')
 #Top fully meets the source shoe and the new longitudinal steel.
for i,z in enumerate(range(82,299,9)):
 add('TransverseTie'+str(i),(-58.3,-.45,z-.1),(-54.7,-.24,z+.1),'staff_zinc','frame')
centers=[(-56.5,z)for z in range(81,298,9)]+[(x,300)for x in[-49,-40,-31,-22,-13,-7]]+ [(-51,76)]
for i,(x,z)in enumerate(centers):
 add('FixtureHousing'+str(i),(x-.65,3.03,z-.16),(x+.65,3.2,z+.16),'staff_zinc','fixture')
 q=add('FixtureLens'+str(i),(x-.6,3.015,z-.105),(x+.6,3.035,z+.105),'staff_opal','fixture');P['lights'].append({'name':q['name'],'at':[x,3.0,z]})
P['floor_geometry']=mapping(poly);P['new_floor_m2']=poly.area;P['support_unique_columns']=len(S['support_feet']);P['structure_file']='LOWER_SHARED_AFT_STAFF_ROUTE_r001.glb'
P['route_samples']=[[-56.5,0,z]for z in range(79,299,6)]+[[x,0,300]for x in range(-56,-3,3)]+[[-46,0,76],[-50.2,0,76],[-56.5,0,76],[-6.2,0,300],[0,0,300]]
P['source_contact_faces']=[{'original_floor':'D01_aft_apron','plane':'x=-48','at':[-48,0,76],'width_m':3.6},{'original_floor':'D01_aft_route','plane':'x=-4','at':[-4,0,300],'width_m':3.6}]
P['phase_evidence']['authored']=[];P['phase_evidence']['connected']=[]
for f in ['PLAN.json','NATIVE_AUTHORING_INPUT_PLAN.json']:(W/f).write_text(json.dumps(P,indent=2)+'\n')
print(json.dumps({'parts':len(P['parts']),'floor_m2':poly.area,'support_columns':len(S['support_feet']),'wall_ceiling_joints':len(P['wall_ceiling_junctions'])}))
