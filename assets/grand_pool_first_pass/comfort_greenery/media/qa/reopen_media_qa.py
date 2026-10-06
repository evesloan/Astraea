"""Independent fresh-process source reopen. Writes only this new derivative QA report; no export/render/Game or original-source/export writes.
blender --background --threads 2 --python-exit-code 1 --python qa/reopen_media_qa.py
Reopens original source for independent material ground truth, then candidate.
Does not load a .blend library into itself or accept counts as visual approval.
"""
from pathlib import Path
import sys,json,hashlib,math,importlib.util,collections
import bpy,bmesh
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'source'))
from blender_media_common import evaluated_geometry,material_state,source_to_world,sha
from prepare_contract import tri_hits,segment_box,inside_box,g
from media_paths import CAT,AUDIT,resolve_pin,new_catalogue_writes
C=json.loads((ROOT/'source_contract.json').read_text());PINS=json.loads((ROOT/'dependency_pins.json').read_text());A=json.loads((ROOT/'content_manifest.json').read_text());BUILD=json.loads((ROOT/'qa/SOURCE_BUILD_REPORT.json').read_text())
SRC=ROOT/BUILD['source_file'];ORIGINAL=CAT/BUILD['original_source_file'];assert SRC.resolve()!=ORIGINAL.resolve()
assert sha(SRC)==BUILD['source_sha256'];assert sha(ROOT/'source_contract.json')==BUILD['source_contract_sha256'];assert sha(ROOT/'content_manifest.json')==BUILD['content_manifest_sha256']
for p,h in PINS.items():assert sha(resolve_pin(p))==h,('retained input changed',p)
roles={'ivory_enamel','warm_walnut','dark_rubber','champagne_metal','display_glass'}
# Ground truth is independently reread from the frozen original, rather than trusting
# a report emitted by the builder or using Python identity on transient wrappers.
bpy.ops.wm.open_mainfile(filepath=str(ORIGINAL));bpy.context.view_layer.update()
baseline={m.get('astraea_material_role'):material_state(m)for m in bpy.data.materials if m.get('astraea_material_role')in roles};assert set(baseline)==roles
bpy.ops.wm.open_mainfile(filepath=str(SRC));bpy.context.view_layer.update();scene=bpy.context.scene
assert not any(o.type in ['LIGHT','CAMERA']for o in scene.objects)
sourceM={m.get('astraea_material_role'):m for m in bpy.data.materials if m.get('astraea_material_role')in roles}
assert {k:material_state(v)for k,v in sourceM.items()}==baseline,'Retained material nodes/inputs/images changed'
objects={c['name']:{o['part_spec_name']:o for o in scene.objects if o.type=='MESH'and o.get('candidate_name')==c['name']}for c in C['candidates']}
allgeo={c['name']:{k:evaluated_geometry(o)for k,o in objects[c['name']].items()}for c in C['candidates']}
assert sum(len(x)for x in objects.values())==sum(o.type=='MESH'for o in scene.objects),'Unexpected source-only prototype or unrelated mesh persisted'
# Read retained architecture and all 51 installed + 48 planned source instances.
cache={}
def retained(path):
 if str(path)not in cache:cache[str(path)]=g.read_glb(path)
 return cache[str(path)]
arch=retained(CAT/'assets/grand_pool_orchard_section/exports/AST-AQU-016.glb');T=list(arch['triangles']);context_names=['architecture/'+m['name']for m in arch['meshes']for t in m['triangles']]
for contract_path,prefix in [(CAT/'assets/grand_pool_first_pass/source/placement_contract.json','installed51'),(CAT/'assets/grand_pool_first_pass/finish_envelope/stock/stock_placement_contract.json','planned48')]:
 for p in json.loads(contract_path.read_text())['placements']:
  q=retained(CAT/p['retained_export'])
  for m in q['meshes']:
   ts=[[g.transform(v,p['position_xyz'],p['yaw_radians'])for v in t]for t in m['triangles']];T.extend(ts);context_names.extend([prefix+'/'+p['name']+'/'+m['name']]*len(ts))
finish=json.loads((CAT/'assets/grand_pool_first_pass/finish_envelope/source/finish_contract.json').read_text());foliage=json.loads((AUDIT/'PLANTING_ENVELOPE_CANDIDATES.json').read_text())['candidates'];wet=json.loads((AUDIT/'WET_POT_FULLNESS_CANDIDATES.json').read_text())['candidates']
mediaT=[];mediaN=[]
for c,parts in allgeo.items():
 for name,z in parts.items():mediaT.extend(z['triangles_world']);mediaN.extend([c+'/'+name]*len(z['triangles_world']))

def bvhtree(ts):
 vs=[Vector(v)for t in ts for v in t];return BVHTree.FromPolygons(vs,[tuple(range(i,i+3))for i in range(0,len(vs),3)],all_triangles=True,epsilon=1e-6)
def mesh_contact(ga,gb):
 # BVH only proposes candidates; exact triangle SAT confirms intersection.
 ta,tb=ga['triangles_world'],gb['triangles_world'];a,b=bvhtree(ta),bvhtree(tb)
 pairs=a.overlap(b)
 for i,j in pairs:
  if g.triangle_intersects(ta[i],tb[j]):return {'confirmed_triangle_pair':[i,j]}
 return None

def uv_direction_report(ob,c):
 me=ob.data;uv=me.uv_layers.active;assert uv and len(me.polygons)==1
 xyz=[];uvs=[]
 for li in me.polygons[0].loop_indices:
  xyz.append(source_to_world(ob.matrix_world@me.vertices[me.loops[li].vertex_index].co));uvs.append(tuple(uv.data[li].uv))
 # Solve world point = origin + U * horizontal UV + V * vertical UV.
 D=np.array([[u,v,1]for u,v in uvs]);coeff=np.linalg.lstsq(D,np.asarray(xyz),rcond=None)[0];U,V=coeff[0],coeff[1]
 ur=U/np.linalg.norm(U);vr=V/np.linalg.norm(V);normal=np.cross(ur,vr)
 assert np.dot(ur,c['basis_world_columns'][0])>1-1e-7
 assert np.dot(vr,[0,1,0])>1-1e-7
 assert np.dot(normal,c['basis_world_columns'][2])>1-1e-7
 assert np.max(abs(D@coeff-np.asarray(xyz)))<5e-5
 assert sorted(uvs)==[(0.,0.),(0.,1.),(1.,0.),(1.,1.)]
 return {'actual_uv_corners':uvs,'actual_world_uv_right':ur.tolist(),'actual_world_uv_up':vr.tolist(),'front_normal':normal.tolist(),'mirror_or_upside_down':False}

def check_metric(ob,p):
 me=ob.data;uv=me.uv_layers.active;assert uv and uv.name=='UV_Metric_Metres';tile=ob.data.materials[0].get('meters_per_tile_uv',[1,1]);maxerror=0.
 for face in me.polygons:
  drop=max(range(3),key=lambda i:abs(face.normal[i]));axes=[i for i in range(3)if i!=drop];grain=p['grain_axis']
  if grain in axes:axes.remove(grain);axes.append(grain)
  for li in face.loop_indices:
   v=me.vertices[me.loops[li].vertex_index].co;expected=[v[axes[0]]/tile[0],v[axes[1]]/tile[1]];maxerror=max(maxerror,max(abs(uv.data[li].uv[i]-expected[i])for i in range(2)))
 assert maxerror<2e-6,(ob.name,'nonmetric UV',maxerror)
 return {'tile_metres':list(tile),'max_original_editable_face_uv_error':maxerror,'evaluated_bevel_uvs':'Inherited from metric parent faces; export remapping remains a separate future gate'}

def image_material_report(ob,c):
 m=ob.data.materials[0];expected=A['material_roles'][c['content_role']];assert m.get('astraea_material_role')==c['content_role'];bs=m.node_tree.nodes.get('Principled BSDF');tex=[n for n in m.node_tree.nodes if n.type=='TEX_IMAGE'];assert len(tex)==1;tex=tex[0];im=tex.image;assert im and im.packed_file
 packed=hashlib.sha256(bytes(im.packed_file.data)).hexdigest();assert packed==expected['sha256']==sha(ROOT/expected['file'])
 for socket in [bs.inputs['Base Color'],bs.inputs.get('Emission Color')or bs.inputs['Emission']]:
  assert len(socket.links)==1;link=socket.links[0]
  assert link.from_node.as_pointer()==tex.as_pointer()
  assert link.from_socket.as_pointer()==tex.outputs['Color'].as_pointer()
  assert link.to_node.as_pointer()==bs.as_pointer()
  assert link.to_socket.as_pointer()==socket.as_pointer()
 assert abs(bs.inputs['Emission Strength'].default_value-.18)<1e-7;assert abs(bs.inputs['Roughness'].default_value-.34)<1e-7
 assert bs.inputs['Metallic'].default_value==0 and bs.inputs['Alpha'].default_value==1
 assert list(im.size)==expected['size_px'];assert tex.extension=='EXTEND'
 return {'original_packed_image_sha256':packed,'image_dimensions':list(im.size),'verified_base_color_and_emission_sockets':True,'local_emission_strength':bs.inputs['Emission Strength'].default_value,'light_objects_added':0,'svg_sha256':sha(ROOT/expected['svg_source'])}

reports=[]
for c in C['candidates']:
 obs=objects[c['name']];geo=allgeo[c['name']];assert set(obs)=={p['name']for p in c['parts']}
 vs=[v for z in geo.values()for v in z['vertices_world']];assert all(inside_box(c['bounds'],v,C['metres_tolerance'])for v in vs),(c['name'],'outside envelope')
 assert all(z['matrix_positive']for z in geo.values())
 metrics={};joins=[];adj={p['name']:set()for p in c['parts']};ground=[]
 for p in c['parts']:
  name=p['name'];ob=obs[name];assert ob['parent_design_id']=='AST-LIB-010' and ob['family']=='library_use';assert ob['lineage_source_object']==p['lineage_object']
  if p['kind']!='art':assert geo[name]['closed_manifold'],(c['name'],name,'nonmanifold');metrics[name]=check_metric(ob,p)
  for j in p['joins']:
   if p['kind']=='art':
    tree=bvhtree(geo[j]['triangles_world']);distances=[tree.find_nearest(Vector(v))[3]for v in geo[name]['vertices_world']];assert max(distances)<.001
    contact={'laminated_layer_gap_m':max(distances),'explicit_allowed_optical_lamination_gap_m':.001}
   else:
    contact=mesh_contact(geo[name],geo[j]);assert contact,(c['name'],'disconnected bearing',name,j)
   joins.append({'part':name,'bearing_part':j,'actual_evaluated_geometry':contact});adj[name].add(j);adj[j].add(name)
  if p.get('contact',{}).get('kind')in ['wall_triangle_contact','floor_triangle_contact']:ground.append(name)
 # Actual bearing graph must connect every visible piece to a measured support.
 seen=set(ground);todo=list(ground)
 while todo:
  for q in adj[todo.pop()]-seen:seen.add(q);todo.append(q)
 assert seen==set(adj),(c['name'],'unsupported structural islands',set(adj)-seen)
 contact_reports=[]
 for contact in c['mount_contacts']:
  pname='wall_backplate_'+str(contact['backplate_index'])if'backplate_index'in contact else contact['part'];ts=geo[pname]['triangles_world'];witnesses=[]
  for w in contact['witnesses']:
   point=np.asarray(w['world_xyz'])
   if c['axis']=='z':
    normal=np.asarray(c['basis_world_columns'][2]);origin=point+normal*.004;direction=-normal
    retained_hits=tri_hits(origin,direction,arch['triangles'],0,.008);assert retained_hits
    support_point=retained_hits[0][2]
   else:
    origin=point-np.array([0,.004,0]);direction=np.array([0,1,0]);support_point=list(point)
    floor_ts=[[(v[0],c['floor_plane_y'],v[1])for v in t]for t in c['floor_contract_triangles_xz']]
    floor_hits=tri_hits(origin,direction,floor_ts,0,.008);assert floor_hits;support_point=floor_hits[0][2]
   actual=tri_hits(origin,direction,ts,0,.008);assert actual,(c['name'],pname,'no actual bearing at witness')
   gap=float(np.linalg.norm(np.asarray(actual[0][2])-support_point));assert gap<=C['metres_tolerance'],(c['name'],pname,'support gap',gap)
   witnesses.append({'actual_evaluated_bearing_point_xyz':actual[0][2],'actual_retained_support_point_xyz':support_point,'gap_m':gap,'source_triangle_index':actual[0][1]})
  contact_reports.append({'part':pname,'witnesses':witnesses})
 uv=uv_direction_report(obs['original_pool_leisure_image'],c);material=image_material_report(obs['original_pool_leisure_image'],c);views=[]
 for q in c['sampled_current_triangle_sightlines']:
  eye=np.asarray(q['eye_xyz']);target=np.asarray(q['target_xyz']);d=target-eye;distance=float(np.linalg.norm(d));d/=distance
  own=tri_hits(eye,d,mediaT,1e-4,distance+C['metres_tolerance']);assert own,(c['name'],'image not reached');t,ix,p=own[0]
  assert mediaN[ix]==c['name']+'/original_pool_leisure_image',(c['name'],'image obscured by derivative geometry',mediaN[ix],q)
  assert abs(t-distance)<=C['metres_tolerance'],(c['name'],'wrong plane')
  blockers=tri_hits(eye,d,T,.015,distance-C['metres_tolerance']);assert not blockers,(c['name'],'retained source occlusion',context_names[blockers[0][1]],q)
  finishhits=[p['name']for p in finish['parts']if segment_box(eye,target,[p['bounds_min_xyz'],p['bounds_max_xyz']])];assert not finishhits
  leafhits=[p['support']+'/'+l['name']for p in foliage for l in p['layers']if segment_box(eye,target,l['bounds'])];leafhits +=[p['name']for p in wet if segment_box(eye,target,p['bounds'])];assert not leafhits
  views.append({'eye_xyz':q['eye_xyz'],'target_xyz':q['target_xyz'],'first_evaluated_media_hit':mediaN[ix],'first_hit_distance_m':t,'expected_image_distance_m':distance,'retained_source_occlusions':[],'finish_envelope_occlusions':[],'full_reserved_foliage_occlusions':[]})
 reports.append({'candidate':c['name'],'actual_evaluated_bounds_world_xyz':g.bounds(vs),'mesh_objects':len(obs),'evaluated_triangles':sum(z['triangle_count']for z in geo.values()),'all_objects_grounded_by_evaluated_bearing_graph':True,'evaluated_bearing_joins':joins,'actual_mount_contacts':contact_reports,'artwork_uv_view_handedness':uv,'packed_image_material':material,'metric_uvs':metrics,'actual_image_plane_eye_probes':views,'visual_acceptance':False})
for p,h in PINS.items():assert sha(resolve_pin(p))==h,('retained input changed after QA',p)
assert sha(SRC)==BUILD['source_sha256'],'QA changed source file'
report={'status':'PASS_INDEPENDENT_REOPEN_GEOMETRY_MATERIAL_UV_CONTENT_SUPPORT','source_file':str(SRC.relative_to(ROOT)),'source_sha256':sha(SRC),'source_contract_sha256':sha(ROOT/'source_contract.json'),'content_manifest_sha256':sha(ROOT/'content_manifest.json'),'qa_script_sha256':sha(__file__),'candidates':reports,'actual_eye_to_image_probe_total':sum(len(x['actual_image_plane_eye_probes'])for x in reports),'all_pinned_inputs_unchanged':True,'scene_visual_acceptance':False,'combined_actual_leaf_geometry_visual_gate':'PENDING parent-coordinated paired scene review with fuller planting','independent_retention':'PENDING parent evidence; this script does not approve or perform exports','exports':[],'new_derivative_catalogue_writes':new_catalogue_writes([ROOT/'qa/INDEPENDENT_REOPEN_QA.json']),'retained_original_source_or_export_writes':[],'game_writes':[]}
(ROOT/'qa/INDEPENDENT_REOPEN_QA.json').write_text(json.dumps(report,indent=2)+'\n');print('INDEPENDENT_REOPEN_PASS_NO_EXPORT',report['source_sha256'],report['actual_eye_to_image_probe_total'])
